from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from config import settings
from database import engine, init_db
from routers import auth_router, designs_router, challenges_router, billing_router, analytics_router

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description=settings.TAGLINE,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)


# ── Security headers middleware ──────────────────────────────────
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: blob:; connect-src 'self' https://api.progenx.ai https://progenx-api.onrender.com; font-src 'self'"
        if request.url.scheme == "https":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response

app.add_middleware(SecurityHeadersMiddleware)


# ── Per-IP rate limiting for auth endpoints ──────────────────────
import time
import threading

_login_attempts: dict[str, list[float]] = {}  # IP -> list of timestamps
_login_lock = threading.Lock()
LOGIN_LIMIT = 10  # max attempts per window
LOGIN_WINDOW = 60  # seconds


def _check_login_rate(ip: str) -> bool:
    """Returns True if the IP is allowed to attempt login."""
    now = time.time()
    with _login_lock:
        # Cleanup old entries to prevent unbounded memory growth
        stale_ips = [k for k, attempts in _login_attempts.items() if all(t < now - 60 for t in attempts)]
        for k in stale_ips:
            del _login_attempts[k]

        attempts = _login_attempts.get(ip, [])
        # Remove old attempts outside the window
        attempts = [t for t in attempts if now - t < LOGIN_WINDOW]
        _login_attempts[ip] = attempts
        if len(attempts) >= LOGIN_LIMIT:
            return False
        attempts.append(now)
        _login_attempts[ip] = attempts
        return True


# Monkey-patch rate limiting into auth endpoints
from fastapi import HTTPException

_original_login = auth_router.router.routes
# We'll use a middleware approach instead — intercept /api/auth/login

@app.middleware("http")
async def rate_limit_auth(request: Request, call_next):
    if request.url.path in ("/api/auth/login", "/api/auth/signup"):
        ip = request.client.host if request.client else "unknown"
        if not _check_login_rate(ip):
            return Response(
                content='{"detail":"Too many attempts. Try again in 60 seconds."}',
                status_code=429,
                media_type="application/json",
            )
    return await call_next(request)


app.include_router(auth_router.router, prefix="/api/auth", tags=["auth"])
app.include_router(designs_router.router, prefix="/api/designs", tags=["designs"])
app.include_router(challenges_router.router, prefix="/api/challenges", tags=["challenges"])
app.include_router(billing_router.router, prefix="/api/billing", tags=["billing"])
app.include_router(analytics_router.router, prefix="/api/analytics", tags=["analytics"])


@app.on_event("startup")
def startup():
    # Safety: crash if JWT secret is the default value
    if settings.JWT_SECRET == "change-me-in-production":
        raise RuntimeError(
            "FATAL: JWT_SECRET is set to the default value. "
            "Set a strong random secret in your .env file before running in production. "
            "Generate one with: python -c \"import secrets; print(secrets.token_urlsafe(64))\""
        )

    try:
        init_db()
        print(f"[DB] Connected to {settings.DATABASE_URL.split('@')[1].split('/')[0] if '@' in settings.DATABASE_URL else 'local'}")
    except Exception as e:
        print(f"[DB] WARNING: Database init failed: {e}")
        print(f"[DB] App will start but database operations may fail")

    # Enable WAL mode for SQLite (better concurrent read performance)
    if "sqlite" in settings.DATABASE_URL:
        try:
            from sqlalchemy import text
            with engine.connect() as conn:
                conn.execute(text("PRAGMA journal_mode=WAL"))
                conn.commit()
        except Exception:
            pass


@app.get("/api/health")
def health():
    return {"status": "ok", "app": settings.APP_NAME, "version": settings.VERSION}


@app.get("/api/info")
def info():
    return {
        "name": settings.APP_NAME,
        "tagline": settings.TAGLINE,
        "free_tier_limit": settings.FREE_TIER_MONTHLY_DESIGNS,
    }


@app.get("/api/stats")
def public_stats():
    """Real-time platform stats — no auth required, shown on landing page."""
    from database import SessionLocal
    from models import User, Design
    db = SessionLocal()
    try:
        total_users = db.query(User).count()
        total_designs = db.query(Design).filter(Design.status == "complete").count()
        return {
            "users": total_users,
            "designs": total_designs,
        }
    finally:
        db.close()
