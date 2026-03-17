from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from database import init_db
from routers import auth_router, designs_router, challenges_router, billing_router

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description=settings.TAGLINE,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router.router, prefix="/api/auth", tags=["auth"])
app.include_router(designs_router.router, prefix="/api/designs", tags=["designs"])
app.include_router(challenges_router.router, prefix="/api/challenges", tags=["challenges"])
app.include_router(billing_router.router, prefix="/api/billing", tags=["billing"])


@app.on_event("startup")
def startup():
    init_db()


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
