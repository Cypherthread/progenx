from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import jwt
import bcrypt

from config import settings
from database import get_db
from models import User

security = HTTPBearer()


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())


def create_token(user_id: str) -> str:
    payload = {
        "sub": user_id,
        "exp": datetime.utcnow() + timedelta(hours=settings.JWT_EXPIRY_HOURS),
        "iat": datetime.utcnow(),
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def get_current_user(
    creds: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    try:
        payload = jwt.decode(
            creds.credentials, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
        )
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user


def check_rate_limit(user: User, db: Session):
    """Check if free-tier user has exceeded monthly design limit."""
    current_month = datetime.utcnow().strftime("%Y-%m")
    if user.month_reset != current_month:
        user.designs_this_month = 0
        user.month_reset = current_month
        db.commit()

    if user.tier == "free" and user.designs_this_month >= settings.FREE_TIER_MONTHLY_DESIGNS:
        raise HTTPException(
            status_code=429,
            detail=f"Free tier limit: {settings.FREE_TIER_MONTHLY_DESIGNS} designs/month. Upgrade to Pro for unlimited.",
        )
