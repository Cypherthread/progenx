from fastapi import APIRouter, Depends, HTTPException
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
