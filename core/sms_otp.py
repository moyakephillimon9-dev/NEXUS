"""
NEXUS — SMS OTP Manager
Generates, stores, and verifies one-time phone verification codes.
Sends via Twilio when credentials are configured.
"""

import os
import random
import time
import threading

# OTP store: phone → {code, expires_at, attempts}
_otp_store: dict = {}
_lock = threading.Lock()

OTP_TTL     = 300   # 5 minutes
MAX_TRIES   = 5


def _clean_phone(phone: str) -> str:
    """Strip spaces/dashes; ensure E.164-ish format."""
    cleaned = phone.strip().replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
    if not cleaned.startswith("+"):
        cleaned = "+" + cleaned
    return cleaned


def send_otp(phone: str) -> dict:
    """
    Generate a 6-digit OTP and send it via Twilio SMS.
    Returns {'success': True, 'message': '...'} or {'success': False, 'error': '...'}.
    """
    phone = _clean_phone(phone)
    if len(phone) < 8:
        return {"success": False, "error": "Invalid phone number."}

    code = f"{random.randint(100000, 999999)}"

    with _lock:
        _otp_store[phone] = {
            "code"      : code,
            "expires_at": time.time() + OTP_TTL,
            "attempts"  : 0,
        }

    # ── Try Twilio ─────────────────────────────────────────────────────────
    sid   = os.environ.get("TWILIO_ACCOUNT_SID", "")
    token = os.environ.get("TWILIO_AUTH_TOKEN", "")
    from_ = os.environ.get("TWILIO_PHONE_NUMBER", "")

    if sid and token and from_:
        try:
            from twilio.rest import Client
            client = Client(sid, token)
            client.messages.create(
                body=f"Your NEXUS verification code is: {code}. Valid for 5 minutes.",
                from_=from_,
                to=phone,
            )
            return {"success": True, "message": f"Code sent to {phone}"}
        except Exception as exc:
            # Clear the stored code if send failed
            with _lock:
                _otp_store.pop(phone, None)
            return {"success": False, "error": f"SMS failed: {str(exc)}"}
    else:
        # Twilio not yet configured — return error with helpful message
        return {
            "success": False,
            "error"  : "Twilio is not configured. Add TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, and TWILIO_PHONE_NUMBER in Settings → Secrets.",
        }


def verify_otp(phone: str, code: str) -> dict:
    """
    Verify a submitted OTP code.
    Returns {'success': True} or {'success': False, 'error': '...'}.
    """
    phone = _clean_phone(phone)

    with _lock:
        record = _otp_store.get(phone)

        if not record:
            return {"success": False, "error": "No code was sent to this number. Request a new one."}

        if time.time() > record["expires_at"]:
            _otp_store.pop(phone, None)
            return {"success": False, "error": "Code expired. Please request a new one."}

        record["attempts"] += 1
        if record["attempts"] > MAX_TRIES:
            _otp_store.pop(phone, None)
            return {"success": False, "error": "Too many attempts. Please request a new code."}

        if record["code"] != code.strip():
            return {"success": False, "error": f"Incorrect code. {MAX_TRIES - record['attempts']} attempts left."}

        # ✓ Correct
        _otp_store.pop(phone, None)
        return {"success": True}


def is_configured() -> bool:
    """Return True if Twilio credentials are present."""
    return bool(
        os.environ.get("TWILIO_ACCOUNT_SID")
        and os.environ.get("TWILIO_AUTH_TOKEN")
        and os.environ.get("TWILIO_PHONE_NUMBER")
    )
