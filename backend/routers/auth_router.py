from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from database import get_db
from models import User
from auth import hash_password, verify_password, create_token, get_current_user

router = APIRouter()


class SignupRequest(BaseModel):
    email: EmailStr
    password: str
    name: str = ""


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class AuthResponse(BaseModel):
    token: str
    user_id: str
    email: str
    name: str
    tier: str


class UserProfile(BaseModel):
    id: str
    email: str
    name: str
    tier: str
    designs_this_month: int
    monthly_limit: int


@router.post("/signup", response_model=AuthResponse)
def signup(req: SignupRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == req.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        email=req.email,
        hashed_password=hash_password(req.password),
        name=req.name,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return AuthResponse(
        token=create_token(user.id),
        user_id=user.id,
        email=user.email,
        name=user.name,
        tier=user.tier,
    )


@router.post("/login", response_model=AuthResponse)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == req.email).first()
    if not user or not verify_password(req.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return AuthResponse(
        token=create_token(user.id),
        user_id=user.id,
        email=user.email,
        name=user.name,
        tier=user.tier,
    )


@router.get("/me", response_model=UserProfile)
def me(user: User = Depends(get_current_user)):
    from config import settings
    return UserProfile(
        id=user.id,
        email=user.email,
        name=user.name,
        tier=user.tier,
        designs_this_month=user.designs_this_month,
        monthly_limit=settings.FREE_TIER_MONTHLY_DESIGNS if user.tier == "free" else -1,
    )


@router.post("/admin/promote")
def promote_to_admin(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Promote current user to admin tier. Requires ADMIN_SECRET in request body.
    This is a one-way operation — only the founder should know the secret."""
    from fastapi import Request
    from config import settings
    import json

    # This is intentionally NOT in the Pydantic model — read raw body
    # The secret must be passed as {"secret": "..."} in the request body
    return {"error": "Use the dedicated endpoint with secret"}


@router.post("/admin/activate")
async def activate_admin(
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Activate admin tier for current user. Requires ADMIN_SECRET."""
    from config import settings
    import json

    if not settings.ADMIN_SECRET:
        raise HTTPException(status_code=403, detail="Admin system not configured")

    try:
        body = await request.json()
        secret = body.get("secret", "")
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid request body")

    if not secret or secret != settings.ADMIN_SECRET:
        raise HTTPException(status_code=403, detail="Invalid admin secret")

    user.tier = "admin"
    db.commit()

    return {
        "message": "Account promoted to admin. Unlimited designs, all features enabled.",
        "tier": "admin",
    }


@router.post("/api-key")
def create_api_key(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Generate an API key for programmatic access (Pro tier only)."""
    if user.tier != "pro":
        raise HTTPException(status_code=403, detail="API keys are available for Pro tier. Upgrade to Pro for API access.")

    import secrets
    from models import ApiKey

    # Generate a random API key
    raw_key = f"pgx_{secrets.token_urlsafe(32)}"
    key_hash = hash_password(raw_key)

    api_key = ApiKey(
        user_id=user.id,
        key_hash=key_hash,
        name="Default",
    )
    db.add(api_key)
    db.commit()

    # Return the raw key ONCE — it's hashed in the DB and can't be retrieved
    return {
        "api_key": raw_key,
        "id": api_key.id,
        "message": "Save this key — it cannot be retrieved again.",
    }


@router.get("/api-keys")
def list_api_keys(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List active API keys (without revealing the key itself)."""
    from models import ApiKey
    keys = db.query(ApiKey).filter(ApiKey.user_id == user.id, ApiKey.is_active == True).all()
    return [
        {
            "id": k.id,
            "name": k.name,
            "created_at": k.created_at.isoformat() if k.created_at else None,
            "last_used": k.last_used.isoformat() if k.last_used else None,
        }
        for k in keys
    ]


@router.delete("/account")
def delete_account(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete user account and all associated data (GDPR right to erasure)."""
    from models import Design, ChatMessage, AuditLog

    # Delete all user data in order (foreign key constraints)
    designs = db.query(Design).filter(Design.user_id == user.id).all()
    for design in designs:
        db.query(ChatMessage).filter(ChatMessage.design_id == design.id).delete()
    db.query(Design).filter(Design.user_id == user.id).delete()
    db.query(AuditLog).filter(AuditLog.user_id == user.id).delete()
    db.query(User).filter(User.id == user.id).delete()
    db.commit()

    return {"deleted": True, "message": "Account and all associated data deleted."}
