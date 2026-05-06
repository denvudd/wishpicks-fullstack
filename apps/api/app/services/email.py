import logging

import httpx

from app.core.settings import settings

logger = logging.getLogger(__name__)

_RESEND_API_URL = "https://api.resend.com/emails"


async def send_verification_email(to_email: str, code: str) -> None:
    if not settings.RESEND_API_KEY:
        logger.warning("RESEND_API_KEY not configured — skipping verification email")
        return

    html = (
        "<div style='font-family:sans-serif;max-width:420px;margin:0 auto'>"
        "<h2>Verify your Wishpicks account</h2>"
        "<p>Enter this code to confirm your email address:</p>"
        f"<p style='font-size:40px;font-weight:bold;letter-spacing:10px;"
        f"text-align:center;margin:24px 0'>{code}</p>"
        "<p style='color:#666;font-size:14px'>This code expires in 10 minutes.</p>"
        "</div>"
    )

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(
                _RESEND_API_URL,
                headers={
                    "Authorization": f"Bearer {settings.RESEND_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "from": settings.EMAIL_FROM,
                    "to": [to_email],
                    "subject": "Your Wishpicks verification code",
                    "html": html,
                },
            )
            resp.raise_for_status()
    except Exception as exc:
        logger.error("Failed to send verification email to %s: %s", to_email, exc)
