import secrets
from datetime import datetime, timedelta
from pathlib import Path


OTP_EXPIRY_SECONDS = 300
MAX_ATTEMPTS = 5
LOG_FILE = Path(__file__).parent.parent / "logs" / "auth.log"


def log_event(event):
    timestamp = datetime.now().isoformat()
    with LOG_FILE.open("a", encoding="utf-8") as log:
        log.write(f"{timestamp} - {event}\n")


def generate_otp():
    otp = f"{secrets.randbelow(1_000_000):06d}"
    log_event("OTP generated")
    return otp


def get_expiry_time():
    return datetime.now() + timedelta(seconds=OTP_EXPIRY_SECONDS)


def is_otp_expired(expiry_time):
    return datetime.now() > expiry_time


def verify_otp(submitted_otp, stored_otp, expiry_time, failed_attempts=0):
    if is_otp_expired(expiry_time):
        log_event("OTP verification failed: expired OTP")
        return False, "OTP has expired", failed_attempts

    if failed_attempts >= MAX_ATTEMPTS:
        log_event("OTP verification blocked: too many failed attempts")
        return False, "Too many failed attempts", failed_attempts

    if not secrets.compare_digest(submitted_otp, stored_otp):
        failed_attempts += 1
        log_event(f"OTP verification failed: invalid OTP, attempt {failed_attempts}")
        return False, "Invalid OTP", failed_attempts

    log_event("OTP verification successful")
    return True, "OTP verified successfully", failed_attempts
