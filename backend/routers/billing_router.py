"""
Stripe billing: checkout, webhooks, customer portal.
Handles Pro tier upgrades ($29/mo) and downgrades.
"""

import stripe
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from config import settings
from database import get_db
from models import User
from auth import get_current_user

router = APIRouter()

if settings.STRIPE_SECRET_KEY:
    stripe.api_key = settings.STRIPE_SECRET_KEY


@router.post("/checkout")
def create_checkout_session(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a Stripe Checkout session for Pro tier upgrade."""
    if not settings.STRIPE_SECRET_KEY:
        raise HTTPException(status_code=503, detail="Stripe not configured")

    if user.tier == "pro":
        raise HTTPException(status_code=400, detail="Already on Pro tier")

    # Find or create Stripe customer
    customer_id = user.stripe_customer_id
    if not customer_id:
        customer = stripe.Customer.create(
            email=user.email,
            metadata={"user_id": user.id},
        )
        customer_id = customer.id
        user.stripe_customer_id = customer_id
        db.commit()

    session = stripe.checkout.Session.create(
        customer=customer_id,
        mode="subscription",
        line_items=[{
            "price": settings.STRIPE_PRO_PRICE_ID,
            "quantity": 1,
        }],
        success_url=f"{settings.FRONTEND_URL}/studio?upgraded=true",
        cancel_url=f"{settings.FRONTEND_URL}/pricing",
        metadata={"user_id": user.id},
    )

    return {"checkout_url": session.url}


@router.post("/portal")
def create_portal_session(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a Stripe Customer Portal session for managing subscription."""
    if not settings.STRIPE_SECRET_KEY:
        raise HTTPException(status_code=503, detail="Stripe not configured")

    if not user.stripe_customer_id:
        raise HTTPException(status_code=400, detail="No billing account found")

    session = stripe.billing_portal.Session.create(
        customer=user.stripe_customer_id,
        return_url=f"{settings.FRONTEND_URL}/studio",
    )

    return {"portal_url": session.url}


@router.post("/webhook")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    """Handle Stripe webhook events for subscription changes."""
    if not settings.STRIPE_SECRET_KEY or not settings.STRIPE_WEBHOOK_SECRET:
        raise HTTPException(status_code=503, detail="Stripe webhooks not configured")

    payload = await request.body()
    sig_header = request.headers.get("stripe-signature", "")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    # Handle subscription events
    from services.email_service import send_upgrade_confirmation, send_subscription_canceled, send_payment_failed

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        user_id = session.get("metadata", {}).get("user_id")
        if user_id:
            user = db.query(User).filter(User.id == user_id).first()
            if user:
                user.tier = "pro"
                user.stripe_subscription_id = session.get("subscription")
                db.commit()
                try:
                    send_upgrade_confirmation(user.email, user.name)
                except Exception:
                    pass

    elif event["type"] in (
        "customer.subscription.deleted",
        "customer.subscription.paused",
    ):
        subscription = event["data"]["object"]
        customer_id = subscription.get("customer")
        user = db.query(User).filter(
            User.stripe_customer_id == customer_id
        ).first()
        if user:
            user.tier = "free"
            user.stripe_subscription_id = None
            db.commit()
            try:
                end_date = subscription.get("current_period_end", "")
                if end_date:
                    from datetime import datetime
                    end_date = datetime.fromtimestamp(end_date).strftime("%B %d, %Y")
                send_subscription_canceled(user.email, user.name, end_date or "end of billing period")
            except Exception:
                pass

    elif event["type"] == "customer.subscription.updated":
        subscription = event["data"]["object"]
        customer_id = subscription.get("customer")
        status = subscription.get("status")
        user = db.query(User).filter(
            User.stripe_customer_id == customer_id
        ).first()
        if user:
            if status in ("active", "trialing"):
                user.tier = "pro"
            elif status in ("canceled", "unpaid", "past_due"):
                user.tier = "free"
            db.commit()

    elif event["type"] == "invoice.payment_failed":
        invoice = event["data"]["object"]
        customer_id = invoice.get("customer")
        user = db.query(User).filter(
            User.stripe_customer_id == customer_id
        ).first()
        if user:
            try:
                send_payment_failed(user.email, user.name)
            except Exception:
                pass

    return {"received": True}
