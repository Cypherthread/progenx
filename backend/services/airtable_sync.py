"""
Airtable CRM sync for Progenx.

Automatically syncs user signups and design activity to Airtable
so the founder can send custom emails, track engagement, and manage
the user base without logging into the app database directly.

Setup:
1. Create a base called "Progenx CRM" at airtable.com
2. Create table "Users" with fields:
   - Email (email)
   - Name (single line text)
   - Tier (single line text)
   - Signup Date (single line text)
   - Designs Count (number)
   - Last Active (single line text)
   - Source (single line text)
   - Notes (long text)
   - Progenx User ID (single line text)
3. Create table "Designs" with fields:
   - Design Name (single line text)
   - User Email (email)
   - Prompt (long text)
   - Chassis (single line text)
   - Genes (single line text)
   - Safety Score (number)
   - Created (single line text)
   - Model Used (single line text)
   - Progenx Design ID (single line text)
4. Set env vars:
   AIRTABLE_API_TOKEN=pat...
   AIRTABLE_BASE_ID=app...
   AIRTABLE_USERS_TABLE=tbl... (or "Users")
   AIRTABLE_DESIGNS_TABLE=tbl... (or "Designs")
"""

import httpx
from datetime import datetime
from config import settings

AIRTABLE_API = "https://api.airtable.com/v0"

_token = getattr(settings, "AIRTABLE_API_TOKEN", "") or ""
_base_id = getattr(settings, "AIRTABLE_BASE_ID", "") or ""
_users_table = getattr(settings, "AIRTABLE_USERS_TABLE", "Users")
_designs_table = getattr(settings, "AIRTABLE_DESIGNS_TABLE", "Designs")


def _headers() -> dict:
    return {
        "Authorization": f"Bearer {_token}",
        "Content-Type": "application/json",
    }


def _enabled() -> bool:
    return bool(_token and _base_id)


def sync_user_signup(user_id: str, email: str, name: str, tier: str = "free"):
    """Sync a new user signup to Airtable. Called after successful signup."""
    if not _enabled():
        return

    try:
        httpx.post(
            f"{AIRTABLE_API}/{_base_id}/{_users_table}",
            headers=_headers(),
            json={
                "fields": {
                    "Email": email,
                    "Name": name,
                    "Tier": tier,
                    "Signup Date": datetime.utcnow().isoformat() + "Z",
                    "Designs Count": 0,
                    "Last Active": datetime.utcnow().isoformat() + "Z",
                    "Progenx User ID": user_id,
                }
            },
            timeout=10,
        )
    except Exception as e:
        print(f"[Airtable] User sync failed (non-blocking): {e}")


def sync_design_created(
    design_id: str,
    user_email: str,
    design_name: str,
    prompt: str,
    chassis: str,
    genes: list[str],
    safety_score: float,
    model_used: str,
):
    """Sync a new design to Airtable. Called after successful design generation."""
    if not _enabled():
        return

    try:
        httpx.post(
            f"{AIRTABLE_API}/{_base_id}/{_designs_table}",
            headers=_headers(),
            json={
                "fields": {
                    "Design Name": design_name,
                    "User Email": user_email,
                    "Prompt": prompt[:1000],
                    "Chassis": chassis,
                    "Genes": ", ".join(genes[:10]),
                    "Safety Score": round(safety_score * 100),
                    "Created": datetime.utcnow().isoformat() + "Z",
                    "Model Used": model_used,
                    "Progenx Design ID": design_id,
                }
            },
            timeout=10,
        )
    except Exception as e:
        print(f"[Airtable] Design sync failed (non-blocking): {e}")


def update_user_activity(user_email: str, designs_count: int):
    """Update user's last active timestamp and design count in Airtable."""
    if not _enabled():
        return

    try:
        # Find the user record by email
        resp = httpx.get(
            f"{AIRTABLE_API}/{_base_id}/{_users_table}",
            headers=_headers(),
            params={
                "filterByFormula": f"{{Email}}='{user_email}'",
                "maxRecords": 1,
            },
            timeout=10,
        )
        records = resp.json().get("records", [])
        if records:
            record_id = records[0]["id"]
            httpx.patch(
                f"{AIRTABLE_API}/{_base_id}/{_users_table}/{record_id}",
                headers=_headers(),
                json={
                    "fields": {
                        "Designs Count": designs_count,
                        "Last Active": datetime.utcnow().isoformat() + "Z",
                    }
                },
                timeout=10,
            )
    except Exception as e:
        print(f"[Airtable] Activity update failed (non-blocking): {e}")


def update_user_tier(user_email: str, new_tier: str):
    """Update user's tier in Airtable when they upgrade/downgrade."""
    if not _enabled():
        return

    try:
        resp = httpx.get(
            f"{AIRTABLE_API}/{_base_id}/{_users_table}",
            headers=_headers(),
            params={
                "filterByFormula": f"{{Email}}='{user_email}'",
                "maxRecords": 1,
            },
            timeout=10,
        )
        records = resp.json().get("records", [])
        if records:
            record_id = records[0]["id"]
            httpx.patch(
                f"{AIRTABLE_API}/{_base_id}/{_users_table}/{record_id}",
                headers=_headers(),
                json={"fields": {"Tier": new_tier}},
                timeout=10,
            )
    except Exception as e:
        print(f"[Airtable] Tier update failed (non-blocking): {e}")
