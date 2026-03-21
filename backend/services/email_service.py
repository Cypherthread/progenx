try:
    import resend
    RESEND_AVAILABLE = True
except ImportError:
    RESEND_AVAILABLE = False
from config import settings


def send_email(to: str, subject: str, html: str):
    """Send a transactional email via Resend."""
    if not RESEND_AVAILABLE or not settings.RESEND_API_KEY:
        print(f"[EMAIL] Resend not configured. Would send to {to}: {subject}")
        return None

    resend.api_key = settings.RESEND_API_KEY
    try:
        result = resend.Emails.send({
            "from": settings.FROM_EMAIL,
            "to": [to],
            "subject": subject,
            "html": html,
        })
        return result
    except Exception as e:
        print(f"[EMAIL] Failed to send to {to}: {e}")
        return None


def send_password_reset(to: str, reset_url: str):
    """Send password reset email."""
    html = f"""
    <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 480px; margin: 0 auto; padding: 40px 20px;">
        <div style="text-align: center; margin-bottom: 32px;">
            <h1 style="font-size: 24px; font-weight: 700; color: #ffffff; margin: 0;">Progenx</h1>
        </div>
        <div style="background: #0F1629; border: 1px solid #1e293b; border-radius: 12px; padding: 32px; color: #e2e8f0;">
            <h2 style="font-size: 18px; font-weight: 600; color: #ffffff; margin: 0 0 16px;">Reset your password</h2>
            <p style="font-size: 14px; line-height: 1.6; color: #94a3b8; margin: 0 0 24px;">
                We received a request to reset your password. Click the button below to choose a new one. This link expires in 30 minutes.
            </p>
            <div style="text-align: center; margin: 24px 0;">
                <a href="{reset_url}" style="display: inline-block; background: #0891b2; color: #ffffff; text-decoration: none; padding: 12px 32px; border-radius: 8px; font-size: 14px; font-weight: 600;">
                    Reset Password
                </a>
            </div>
            <p style="font-size: 12px; color: #64748b; margin: 24px 0 0; line-height: 1.5;">
                If you didn't request this, you can safely ignore this email. Your password won't change.
            </p>
            <hr style="border: none; border-top: 1px solid #1e293b; margin: 24px 0;" />
            <p style="font-size: 11px; color: #475569; margin: 0;">
                Can't click the button? Copy this link:<br/>
                <span style="color: #06b6d4; word-break: break-all;">{reset_url}</span>
            </p>
        </div>
        <p style="font-size: 11px; color: #475569; text-align: center; margin-top: 24px;">
            Progenx — AI-powered bioengineering design
        </p>
    </div>
    """
    return send_email(to, "Reset your Progenx password", html)


def send_welcome(to: str, name: str):
    """Send welcome email after signup."""
    html = f"""
    <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 480px; margin: 0 auto; padding: 40px 20px;">
        <div style="text-align: center; margin-bottom: 32px;">
            <h1 style="font-size: 24px; font-weight: 700; color: #ffffff; margin: 0;">Progenx</h1>
        </div>
        <div style="background: #0F1629; border: 1px solid #1e293b; border-radius: 12px; padding: 32px; color: #e2e8f0;">
            <h2 style="font-size: 18px; font-weight: 600; color: #ffffff; margin: 0 0 16px;">Welcome, {name or 'there'}!</h2>
            <p style="font-size: 14px; line-height: 1.6; color: #94a3b8; margin: 0 0 16px;">
                You now have 5 free designs per month. Describe any microbe, enzyme, or genetic circuit in plain English and get back real gene sequences, metabolic simulations, and downloadable files.
            </p>
            <p style="font-size: 14px; line-height: 1.6; color: #94a3b8; margin: 0 0 24px;">
                Try something like: "Design a microbe that eats ocean microplastics and converts them to biodegradable plastic."
            </p>
            <div style="text-align: center; margin: 24px 0;">
                <a href="{settings.FRONTEND_URL}/studio" style="display: inline-block; background: #0891b2; color: #ffffff; text-decoration: none; padding: 12px 32px; border-radius: 8px; font-size: 14px; font-weight: 600;">
                    Open Design Studio
                </a>
            </div>
        </div>
        <p style="font-size: 11px; color: #475569; text-align: center; margin-top: 24px;">
            Progenx — AI-powered bioengineering design
        </p>
    </div>
    """
    return send_email(to, "Welcome to Progenx", html)


def send_design_limit_warning(to: str, name: str, used: int, limit: int):
    """Send when user hits 4/5 designs (one remaining)."""
    html = _wrap(f"""
        <h2 style="font-size: 18px; font-weight: 600; color: #ffffff; margin: 0 0 16px;">You're almost at your limit, {name or 'there'}</h2>
        <p style="font-size: 14px; line-height: 1.6; color: #94a3b8; margin: 0 0 16px;">
            You've used {used} of your {limit} free designs this month. You have {limit - used} design remaining.
        </p>
        <p style="font-size: 14px; line-height: 1.6; color: #94a3b8; margin: 0 0 24px;">
            Upgrade to Pro for unlimited designs with Claude AI, priority generation, and version history.
        </p>
        <div style="text-align: center; margin: 24px 0;">
            <a href="{settings.FRONTEND_URL}/pricing" style="display: inline-block; background: #0891b2; color: #ffffff; text-decoration: none; padding: 12px 32px; border-radius: 8px; font-size: 14px; font-weight: 600;">
                View Pro Plans
            </a>
        </div>
        <p style="font-size: 12px; color: #64748b; margin: 16px 0 0;">
            Your limit resets at the start of each month.
        </p>
    """)
    return send_email(to, f"You have {limit - used} free design left this month", html)


def send_design_limit_reached(to: str, name: str):
    """Send when user hits 5/5 designs."""
    html = _wrap(f"""
        <h2 style="font-size: 18px; font-weight: 600; color: #ffffff; margin: 0 0 16px;">You've used all your free designs</h2>
        <p style="font-size: 14px; line-height: 1.6; color: #94a3b8; margin: 0 0 24px;">
            {name or 'Hey'}, you've reached your 5 free designs for this month. Your limit resets at the start of next month.
        </p>
        <p style="font-size: 14px; line-height: 1.6; color: #94a3b8; margin: 0 0 24px;">
            Need more now? Pro gives you unlimited designs, Claude AI for higher quality, and priority generation.
        </p>
        <div style="text-align: center; margin: 24px 0;">
            <a href="{settings.FRONTEND_URL}/pricing" style="display: inline-block; background: #0891b2; color: #ffffff; text-decoration: none; padding: 12px 32px; border-radius: 8px; font-size: 14px; font-weight: 600;">
                Upgrade to Pro — $29/mo
            </a>
        </div>
    """)
    return send_email(to, "You've used all 5 free designs this month", html)


def send_upgrade_confirmation(to: str, name: str):
    """Send when user upgrades to Pro."""
    html = _wrap(f"""
        <h2 style="font-size: 18px; font-weight: 600; color: #ffffff; margin: 0 0 16px;">You're on Pro now</h2>
        <p style="font-size: 14px; line-height: 1.6; color: #94a3b8; margin: 0 0 16px;">
            {name or 'Hey'}, your Pro subscription is active. Here's what you unlocked:
        </p>
        <ul style="font-size: 14px; line-height: 1.8; color: #94a3b8; margin: 0 0 24px; padding-left: 20px;">
            <li>Unlimited designs</li>
            <li>Claude Sonnet AI (best quality)</li>
            <li>LLM function validation on NCBI results</li>
            <li>Priority generation queue</li>
            <li>Design version history</li>
            <li>API access</li>
        </ul>
        <div style="text-align: center; margin: 24px 0;">
            <a href="{settings.FRONTEND_URL}/studio" style="display: inline-block; background: #0891b2; color: #ffffff; text-decoration: none; padding: 12px 32px; border-radius: 8px; font-size: 14px; font-weight: 600;">
                Start Designing
            </a>
        </div>
    """)
    return send_email(to, "Welcome to Progenx Pro", html)


def send_subscription_canceled(to: str, name: str, end_date: str):
    """Send when user cancels Pro subscription."""
    html = _wrap(f"""
        <h2 style="font-size: 18px; font-weight: 600; color: #ffffff; margin: 0 0 16px;">Your Pro plan is canceled</h2>
        <p style="font-size: 14px; line-height: 1.6; color: #94a3b8; margin: 0 0 16px;">
            {name or 'Hey'}, we've canceled your Pro subscription. You'll keep Pro access until <strong style="color: #e2e8f0;">{end_date}</strong>, then your account reverts to the free tier.
        </p>
        <p style="font-size: 14px; line-height: 1.6; color: #94a3b8; margin: 0 0 24px;">
            Your designs and history will always be available. If you change your mind, you can resubscribe anytime.
        </p>
        <div style="text-align: center; margin: 24px 0;">
            <a href="{settings.FRONTEND_URL}/pricing" style="display: inline-block; border: 1px solid #334155; color: #94a3b8; text-decoration: none; padding: 12px 32px; border-radius: 8px; font-size: 14px; font-weight: 600;">
                Resubscribe
            </a>
        </div>
    """)
    return send_email(to, "Your Progenx Pro plan has been canceled", html)


def send_payment_failed(to: str, name: str):
    """Send when a payment fails (card declined, expired, etc.)."""
    html = _wrap(f"""
        <h2 style="font-size: 18px; font-weight: 600; color: #ffffff; margin: 0 0 16px;">Payment failed</h2>
        <p style="font-size: 14px; line-height: 1.6; color: #94a3b8; margin: 0 0 24px;">
            {name or 'Hey'}, we couldn't process your Pro subscription payment. Please update your payment method to keep Pro access.
        </p>
        <div style="text-align: center; margin: 24px 0;">
            <a href="{settings.FRONTEND_URL}/account" style="display: inline-block; background: #0891b2; color: #ffffff; text-decoration: none; padding: 12px 32px; border-radius: 8px; font-size: 14px; font-weight: 600;">
                Update Payment Method
            </a>
        </div>
        <p style="font-size: 12px; color: #64748b; margin: 16px 0 0;">
            We'll retry the payment automatically. If it continues to fail, your account will revert to the free tier.
        </p>
    """)
    return send_email(to, "Action needed: payment failed for Progenx Pro", html)


def send_account_deleted(to: str, name: str):
    """Send confirmation after account deletion."""
    html = _wrap(f"""
        <h2 style="font-size: 18px; font-weight: 600; color: #ffffff; margin: 0 0 16px;">Account deleted</h2>
        <p style="font-size: 14px; line-height: 1.6; color: #94a3b8; margin: 0 0 24px;">
            {name or 'Hey'}, your Progenx account has been permanently deleted. All your designs, data, and API keys have been removed from our systems.
        </p>
        <p style="font-size: 14px; line-height: 1.6; color: #94a3b8; margin: 0 0 24px;">
            If you ever want to come back, you can create a new account at any time.
        </p>
        <p style="font-size: 12px; color: #64748b; margin: 16px 0 0;">
            If you didn't request this, contact support@progenx.ai immediately.
        </p>
    """)
    return send_email(to, "Your Progenx account has been deleted", html)


def send_password_changed(to: str, name: str):
    """Send confirmation after password is changed/reset."""
    html = _wrap(f"""
        <h2 style="font-size: 18px; font-weight: 600; color: #ffffff; margin: 0 0 16px;">Password changed</h2>
        <p style="font-size: 14px; line-height: 1.6; color: #94a3b8; margin: 0 0 24px;">
            {name or 'Hey'}, your Progenx password was just changed. If this was you, no action is needed.
        </p>
        <p style="font-size: 14px; line-height: 1.6; color: #f87171; margin: 0 0 24px;">
            If you did NOT change your password, reset it immediately and contact support@progenx.ai.
        </p>
        <div style="text-align: center; margin: 24px 0;">
            <a href="{settings.FRONTEND_URL}" style="display: inline-block; border: 1px solid #334155; color: #94a3b8; text-decoration: none; padding: 12px 32px; border-radius: 8px; font-size: 14px; font-weight: 600;">
                Go to Progenx
            </a>
        </div>
    """)
    return send_email(to, "Your Progenx password was changed", html)


def _wrap(body_content: str) -> str:
    """Wrap email body in standard Progenx template."""
    return f"""
    <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 480px; margin: 0 auto; padding: 40px 20px; background: #080C14;">
        <div style="text-align: center; margin-bottom: 32px;">
            <h1 style="font-size: 24px; font-weight: 700; color: #ffffff; margin: 0;">Progenx</h1>
        </div>
        <div style="background: #0F1629; border: 1px solid #1e293b; border-radius: 12px; padding: 32px; color: #e2e8f0;">
            {body_content}
        </div>
        <p style="font-size: 11px; color: #475569; text-align: center; margin-top: 24px;">
            Progenx — AI-powered bioengineering design<br/>
            <a href="{settings.FRONTEND_URL}/privacy" style="color: #475569; text-decoration: underline;">Privacy Policy</a>
        </p>
    </div>
    """
