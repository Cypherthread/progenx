import secrets
import hashlib
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session

from database import get_db
from models import User
from auth import hash_password, verify_password, create_token, get_current_user
from config import settings

router = APIRouter()

# Password reset tokens: {token_hash: {email, expires_at}}
_reset_tokens: dict[str, dict] = {}


class SignupRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
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

    # Sync to Airtable CRM (non-blocking)
    from services.airtable_sync import sync_user_signup
    sync_user_signup(user.id, user.email, user.name, user.tier)

    # Send welcome email (non-blocking — don't break signup if email fails)
    try:
        from services.email_service import send_welcome
        send_welcome(user.email, user.name)
    except Exception as e:
        print(f"[EMAIL] Welcome email failed for {user.email}: {e}")

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


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    password: str


@router.post("/forgot-password")
def forgot_password(req: ForgotPasswordRequest, db: Session = Depends(get_db)):
    """Request a password reset link. Always returns 200 to prevent email enumeration."""
    user = db.query(User).filter(User.email == req.email).first()

    if user:
        # Generate a secure token
        token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(token.encode()).hexdigest()

        # Store with 30-minute expiry
        _reset_tokens[token_hash] = {
            "email": user.email,
            "expires_at": datetime.utcnow() + timedelta(minutes=30),
        }

        # Build reset URL and send email
        reset_url = f"{settings.FRONTEND_URL}/reset-password?token={token}"
        try:
            from services.email_service import send_password_reset
            send_password_reset(user.email, reset_url)
        except Exception as e:
            print(f"[EMAIL] Password reset email failed for {user.email}: {e}")

    # Always return the same response (prevent email enumeration)
    return {"message": "If that email exists, we sent a reset link."}


@router.post("/reset-password")
def reset_password(req: ResetPasswordRequest, db: Session = Depends(get_db)):
    """Reset password using a valid token."""
    if len(req.password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters.")

    # Look up token
    token_hash = hashlib.sha256(req.token.encode()).hexdigest()
    token_data = _reset_tokens.get(token_hash)

    if not token_data:
        raise HTTPException(status_code=400, detail="Invalid or expired reset link.")

    if datetime.utcnow() > token_data["expires_at"]:
        # Clean up expired token
        del _reset_tokens[token_hash]
        raise HTTPException(status_code=400, detail="Reset link has expired. Please request a new one.")

    # Find user and update password
    user = db.query(User).filter(User.email == token_data["email"]).first()
    if not user:
        raise HTTPException(status_code=400, detail="Invalid or expired reset link.")

    user.hashed_password = hash_password(req.password)
    db.commit()

    # Delete used token
    del _reset_tokens[token_hash]

    # Send confirmation email
    try:
        from services.email_service import send_password_changed
        send_password_changed(user.email, user.name)
    except Exception:
        pass

    return {"message": "Password reset successfully."}


@router.delete("/account")
def delete_account(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete user account and all associated data (GDPR right to erasure)."""
    email, name = user.email, user.name
    from models import (
        Design, ChatMessage, AuditLog, AnalyticsEvent,
        Bump, DesignComment, DesignVersion, ApiKey,
    )

    # Delete all user data in order (foreign key constraints)
    designs = db.query(Design).filter(Design.user_id == user.id).all()
    design_ids = [d.id for d in designs]

    # Delete child records of designs first
    if design_ids:
        db.query(ChatMessage).filter(ChatMessage.design_id.in_(design_ids)).delete(synchronize_session=False)
        db.query(DesignComment).filter(DesignComment.design_id.in_(design_ids)).delete(synchronize_session=False)
        db.query(DesignVersion).filter(DesignVersion.design_id.in_(design_ids)).delete(synchronize_session=False)
        db.query(Bump).filter(Bump.design_id.in_(design_ids)).delete(synchronize_session=False)

    # Delete user-level records
    db.query(Bump).filter(Bump.user_id == user.id).delete(synchronize_session=False)
    db.query(DesignComment).filter(DesignComment.user_id == user.id).delete(synchronize_session=False)
    db.query(ApiKey).filter(ApiKey.user_id == user.id).delete(synchronize_session=False)
    db.query(AnalyticsEvent).filter(AnalyticsEvent.user_id == user.id).delete(synchronize_session=False)
    db.query(AuditLog).filter(AuditLog.user_id == user.id).delete(synchronize_session=False)
    db.query(Design).filter(Design.user_id == user.id).delete(synchronize_session=False)
    db.query(User).filter(User.id == user.id).delete(synchronize_session=False)
    db.commit()

    # Send deletion confirmation (to their email, even though account is gone)
    try:
        from services.email_service import send_account_deleted
        send_account_deleted(email, name)
    except Exception:
        pass

    return {"deleted": True, "message": "Account and all associated data deleted."}
