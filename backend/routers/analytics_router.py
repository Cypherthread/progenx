import html
import time
import threading
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel, Field
from sqlalchemy import func, distinct
from sqlalchemy.orm import Session

from database import get_db
from models import User, AnalyticsEvent
from auth import get_current_user

router = APIRouter()


# ── Input sanitization ──────────────────────────────────────────

def sanitize(s: str) -> str:
    return html.escape(s.strip()) if s else ""


# ── Per-IP rate limiting for POST /events ───────────────────────

_events_attempts: dict[str, list[float]] = {}  # IP -> list of timestamps
_events_lock = threading.Lock()
EVENTS_LIMIT = 10  # max requests per window
EVENTS_WINDOW = 60  # seconds


def _check_events_rate(ip: str) -> bool:
    """Returns True if the IP is allowed to post events."""
    now = time.time()
    with _events_lock:
        attempts = _events_attempts.get(ip, [])
        # Remove old attempts outside the window
        attempts = [t for t in attempts if now - t < EVENTS_WINDOW]
        _events_attempts[ip] = attempts
        if len(attempts) >= EVENTS_LIMIT:
            return False
        attempts.append(now)
        _events_attempts[ip] = attempts
        return True


# ── Pydantic schemas ─────────────────────────────────────────────

class EventIn(BaseModel):
    session_id: str = Field(max_length=64)
    user_id: str = Field(default="", max_length=64)
    event_type: str = Field(max_length=32)
    page: str = Field(default="", max_length=256)
    element: str = Field(default="", max_length=512)
    value: str = Field(default="", max_length=256)
    metadata: str = Field(default="{}", max_length=4096)


class BatchEventsRequest(BaseModel):
    events: list[EventIn]


# ── Valid event types ────────────────────────────────────────────

VALID_EVENT_TYPES = {
    "page_view", "click", "scroll_depth", "funnel_step",
    "time_on_page", "section_view", "feature_use", "rage_click",
    "error", "web_vital", "referral", "drop_off",
}


# ── POST /events — batch ingest (no auth) ────────────────────────

@router.post("/events")
def ingest_events(req: BatchEventsRequest, request: Request, db: Session = Depends(get_db)):
    """Batch receive analytics events. No auth required (anonymous tracking).
    Rate limit: 10 requests per minute per IP, 100 events per batch max."""

    # Per-IP rate limiting
    ip = request.client.host if request.client else "unknown"
    if not _check_events_rate(ip):
        raise HTTPException(
            status_code=429,
            detail="Too many requests. Try again in 60 seconds.",
        )

    if len(req.events) > 100:
        raise HTTPException(
            status_code=400,
            detail="Maximum 100 events per batch.",
        )

    created = 0
    for ev in req.events:
        if ev.event_type not in VALID_EVENT_TYPES:
            continue  # silently skip invalid event types

        event = AnalyticsEvent(
            session_id=ev.session_id,
            user_id=ev.user_id,
            event_type=ev.event_type,
            page=ev.page,
            element=sanitize(ev.element),
            value=sanitize(ev.value),
            metadata_=sanitize(ev.metadata),
        )
        db.add(event)
        created += 1

    db.commit()
    return {"accepted": created}


# ── Helpers ──────────────────────────────────────────────────────

def _require_admin(user: User):
    if user.tier != "admin":
        raise HTTPException(status_code=403, detail="Admin access required.")


def _parse_range(range_str: str) -> datetime:
    """Parse a range query parameter ('7d' or '30d') into a since-datetime."""
    now = datetime.utcnow()
    if range_str == "30d":
        return now - timedelta(days=30)
    return now - timedelta(days=7)


def _page_views(db: Session, since: datetime) -> list[dict]:
    """Page view counts grouped by page since the given date."""
    rows = (
        db.query(
            AnalyticsEvent.page,
            func.count().label("views"),
        )
        .filter(
            AnalyticsEvent.event_type == "page_view",
            AnalyticsEvent.created_at >= since,
        )
        .group_by(AnalyticsEvent.page)
        .order_by(func.count().desc())
        .all()
    )
    return [{"page": r.page, "views": r.views} for r in rows]


def _clicks(db: Session, since: datetime) -> list[dict]:
    """Which elements get clicked most, grouped by element + page."""
    rows = (
        db.query(
            AnalyticsEvent.element,
            AnalyticsEvent.page,
            func.count().label("count"),
        )
        .filter(
            AnalyticsEvent.event_type == "click",
            AnalyticsEvent.element != "",
            AnalyticsEvent.created_at >= since,
        )
        .group_by(AnalyticsEvent.element, AnalyticsEvent.page)
        .order_by(func.count().desc())
        .limit(100)
        .all()
    )
    return [{"element": r.element, "page": r.page, "count": r.count} for r in rows]


def _scroll_depth(db: Session, since: datetime) -> list[dict]:
    """Scroll depth distribution per page: how many users reached 25/50/75/100%."""
    rows = (
        db.query(
            AnalyticsEvent.page,
            AnalyticsEvent.value,
            func.count().label("count"),
        )
        .filter(
            AnalyticsEvent.event_type == "scroll_depth",
            AnalyticsEvent.created_at >= since,
        )
        .group_by(AnalyticsEvent.page, AnalyticsEvent.value)
        .all()
    )

    # Group by page, then compute bucket counts
    page_data: dict[str, dict] = {}
    for r in rows:
        page = r.page
        if page not in page_data:
            page_data[page] = {"25": 0, "50": 0, "75": 0, "100": 0}

        try:
            depth = int(float(r.value))
        except (ValueError, TypeError):
            continue

        if depth >= 25:
            page_data[page]["25"] += r.count
        if depth >= 50:
            page_data[page]["50"] += r.count
        if depth >= 75:
            page_data[page]["75"] += r.count
        if depth >= 100:
            page_data[page]["100"] += r.count

    return [
        {
            "page": page,
            "reached_25": buckets["25"],
            "reached_50": buckets["50"],
            "reached_75": buckets["75"],
            "reached_100": buckets["100"],
        }
        for page, buckets in page_data.items()
    ]


def _funnel(db: Session, since: datetime) -> list[dict]:
    """Funnel conversion: landing -> signup -> studio -> generate -> share -> explore."""
    FUNNEL_STEPS = ["landing", "signup", "studio", "generate", "share", "explore"]

    counts = {}
    for step in FUNNEL_STEPS:
        count = (
            db.query(func.count(distinct(AnalyticsEvent.session_id)))
            .filter(
                AnalyticsEvent.event_type == "funnel_step",
                AnalyticsEvent.value == step,
                AnalyticsEvent.created_at >= since,
            )
            .scalar()
        ) or 0
        counts[step] = count

    first_step_count = counts.get(FUNNEL_STEPS[0], 0) or 1

    result = []
    for i, step in enumerate(FUNNEL_STEPS):
        prev_count = counts[FUNNEL_STEPS[i - 1]] if i > 0 else counts[step]
        prev_count = prev_count or 1  # avoid division by zero

        result.append({
            "step": step,
            "count": counts[step],
            "conversion_from_previous": round(counts[step] / prev_count * 100, 1) if i > 0 else 100.0,
            "conversion_from_start": round(counts[step] / first_step_count * 100, 1),
        })

    return result


def _feature_usage(db: Session, since: datetime) -> list[dict]:
    """Feature usage from feature_use events."""
    rows = (
        db.query(
            AnalyticsEvent.element,
            func.count().label("uses"),
        )
        .filter(
            AnalyticsEvent.event_type == "feature_use",
            AnalyticsEvent.element != "",
            AnalyticsEvent.created_at >= since,
        )
        .group_by(AnalyticsEvent.element)
        .order_by(func.count().desc())
        .limit(20)
        .all()
    )
    return [{"feature": r.element, "uses": r.uses} for r in rows]


def _drop_offs(db: Session, since: datetime) -> list[dict]:
    """Pages where sessions end (drop_off events)."""
    rows = (
        db.query(
            AnalyticsEvent.page,
            func.count().label("count"),
        )
        .filter(
            AnalyticsEvent.event_type == "drop_off",
            AnalyticsEvent.created_at >= since,
        )
        .group_by(AnalyticsEvent.page)
        .order_by(func.count().desc())
        .all()
    )
    return [{"page": r.page, "count": r.count} for r in rows]


def _overview(db: Session, since: datetime) -> dict:
    """Overview stats: sessions, unique users, pages viewed, avg session duration."""
    total_sessions = (
        db.query(func.count(distinct(AnalyticsEvent.session_id)))
        .filter(AnalyticsEvent.created_at >= since)
        .scalar()
    ) or 0

    unique_users = (
        db.query(func.count(distinct(AnalyticsEvent.user_id)))
        .filter(
            AnalyticsEvent.created_at >= since,
            AnalyticsEvent.user_id != "",
        )
        .scalar()
    ) or 0

    pages_viewed = (
        db.query(func.count())
        .filter(
            AnalyticsEvent.event_type == "page_view",
            AnalyticsEvent.created_at >= since,
        )
        .scalar()
    ) or 0

    # Average session duration from time_on_page events
    all_times = (
        db.query(AnalyticsEvent.session_id, AnalyticsEvent.value)
        .filter(
            AnalyticsEvent.event_type == "time_on_page",
            AnalyticsEvent.created_at >= since,
        )
        .all()
    )

    # Sum time_on_page per session, then average across sessions
    session_totals: dict[str, float] = {}
    for r in all_times:
        try:
            t = float(r.value)
        except (ValueError, TypeError):
            continue
        session_totals[r.session_id] = session_totals.get(r.session_id, 0) + t

    avg_session_duration = 0.0
    if session_totals:
        avg_session_duration = round(
            sum(session_totals.values()) / len(session_totals), 1
        )

    return {
        "total_sessions": total_sessions,
        "unique_users": unique_users,
        "pages_viewed": pages_viewed,
        "avg_session_duration_seconds": avg_session_duration,
    }


# ── GET /dashboard — admin aggregated analytics ──────────────────

@router.get("/dashboard")
def analytics_dashboard(
    range: str = Query(default="7d", pattern="^(7d|30d)$"),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Admin only. Returns aggregated analytics data matching frontend DashboardData schema."""
    _require_admin(user)

    since = _parse_range(range)

    return {
        "overview": _overview(db, since),
        "page_views": _page_views(db, since),
        "clicks": _clicks(db, since),
        "scroll_depth": _scroll_depth(db, since),
        "funnel": _funnel(db, since),
        "feature_usage": _feature_usage(db, since),
        "drop_offs": _drop_offs(db, since),
    }


# ── GET /suggestions — admin actionable suggestions ──────────────

@router.get("/suggestions")
def analytics_suggestions(
    range: str = Query(default="7d", pattern="^(7d|30d)$"),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Admin only. Analyzes data and returns actionable suggestions."""
    _require_admin(user)

    since = _parse_range(range)
    suggestions: list[dict] = []

    # ── 1. Scroll depth on landing page ──────────────────────────
    scroll_data = _scroll_depth(db, since)
    for entry in scroll_data:
        if entry["page"] in ("landing", "/", "/landing", "home"):
            total = entry["reached_25"] or 1
            reach_75_pct = entry["reached_75"] / total * 100
            if reach_75_pct < 30:
                suggestions.append({
                    "type": "warning",
                    "text": (
                        "Most visitors don't scroll past the fold on the landing page. "
                        "Consider moving key content higher."
                    ),
                })
            break

    # ── 2. Low click-rate elements ───────────────────────────────
    click_data = _clicks(db, since)

    total_page_views = (
        db.query(func.count())
        .filter(
            AnalyticsEvent.event_type == "page_view",
            AnalyticsEvent.created_at >= since,
        )
        .scalar()
    ) or 1

    for item in click_data:
        click_rate = item["count"] / total_page_views * 100
        if click_rate < 5 and item["count"] >= 2:
            suggestions.append({
                "type": "idea",
                "text": (
                    f"The '{item['element']}' button on {item['page']} is rarely used "
                    f"({click_rate:.1f}% click rate). Consider removing or repositioning."
                ),
            })

    # ── 3. Signup-to-generate conversion ─────────────────────────
    funnel = _funnel(db, since)
    funnel_map = {s["step"]: s for s in funnel}
    signup_count = funnel_map.get("signup", {}).get("count", 0)
    generate_count = funnel_map.get("generate", {}).get("count", 0)
    if signup_count > 0:
        signup_to_generate = generate_count / signup_count * 100
        if signup_to_generate < 40:
            suggestions.append({
                "type": "warning",
                "text": (
                    "Users sign up but don't generate designs "
                    f"({signup_to_generate:.0f}% conversion). "
                    "The studio onboarding may need improvement."
                ),
            })

    # ── 4. Rarely viewed tabs ────────────────────────────────────
    tab_clicks = [
        c for c in click_data
        if "tab" in c["element"].lower() or "panel" in c["element"].lower()
    ]
    if tab_clicks:
        max_tab_clicks = max(t["count"] for t in tab_clicks)
        for tab in tab_clicks:
            if max_tab_clicks > 0 and (tab["count"] / max_tab_clicks * 100) < 10:
                suggestions.append({
                    "type": "idea",
                    "text": (
                        f"The '{tab['element']}' tab is rarely viewed "
                        f"({tab['count']} clicks vs {max_tab_clicks} for the top tab). "
                        "Consider merging its content into Overview."
                    ),
                })

    # ── 5. Very low time on page ─────────────────────────────────
    all_times = (
        db.query(AnalyticsEvent.page, AnalyticsEvent.value)
        .filter(
            AnalyticsEvent.event_type == "time_on_page",
            AnalyticsEvent.created_at >= since,
        )
        .all()
    )
    page_times: dict[str, list[float]] = {}
    for r in all_times:
        try:
            t = float(r.value)
        except (ValueError, TypeError):
            continue
        page_times.setdefault(r.page, []).append(t)

    for page, times in page_times.items():
        avg = sum(times) / len(times)
        if avg < 5 and len(times) >= 3:
            suggestions.append({
                "type": "warning",
                "text": (
                    f"Users spend very little time on '{page}' "
                    f"(avg {avg:.1f}s). It may not be providing value."
                ),
            })

    # ── 6. Explore page low engagement ───────────────────────────
    explore_views = (
        db.query(func.count())
        .filter(
            AnalyticsEvent.event_type == "page_view",
            AnalyticsEvent.page.in_(["explore", "/explore"]),
            AnalyticsEvent.created_at >= since,
        )
        .scalar()
    ) or 0

    total_sessions = (
        db.query(func.count(distinct(AnalyticsEvent.session_id)))
        .filter(AnalyticsEvent.created_at >= since)
        .scalar()
    ) or 1

    if total_sessions > 5 and (explore_views / total_sessions * 100) < 10:
        suggestions.append({
            "type": "idea",
            "text": (
                "The Explore page gets few visits "
                f"({explore_views} views across {total_sessions} sessions). "
                "Consider promoting community designs on the landing page."
            ),
        })

    # ── 7. High drop-off pages ───────────────────────────────────
    drop_off_data = _drop_offs(db, since)
    if drop_off_data:
        worst = drop_off_data[0]
        if worst["count"] >= 5:
            suggestions.append({
                "type": "warning",
                "text": (
                    f"'{worst['page']}' has the highest drop-off rate "
                    f"({worst['count']} sessions ended there). "
                    "Investigate what's causing users to leave."
                ),
            })

    if not suggestions:
        suggestions.append({
            "type": "idea",
            "text": (
                "Not enough data to generate suggestions yet. "
                "Keep collecting events and check back later."
            ),
        })

    return suggestions
