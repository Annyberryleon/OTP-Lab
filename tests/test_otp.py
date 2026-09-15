import sys
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent.parent / "app"))

from otp import generate_otp, get_expiry_time, is_otp_expired, verify_otp


def test_generate_otp():
    otp = generate_otp()

    assert len(otp) == 6
    assert otp.isdigit()


def test_otp_not_expired_immediately():
    expiry_time = get_expiry_time()

    assert is_otp_expired(expiry_time) is False


def test_correct_otp():
    otp = generate_otp()
    expiry_time = get_expiry_time()

    success, message, attempts = verify_otp(
        otp,
        otp,
        expiry_time
    )

    assert success is True
    assert message == "OTP verified successfully"
    assert attempts == 0


def test_wrong_otp():
    otp = generate_otp()
    expiry_time = get_expiry_time()

    success, message, attempts = verify_otp(
        "000000",
        otp,
        expiry_time
    )

    assert success is False
    assert message == "Invalid OTP"
    assert attempts == 1


def test_expired_otp():
    otp = generate_otp()
    expiry_time = datetime.now() - timedelta(seconds=1)

    success, message, attempts = verify_otp(
        otp,
        otp,
        expiry_time
    )

    assert success is False
    assert message == "OTP has expired"


def test_max_failed_attempts():
    otp = generate_otp()
    expiry_time = get_expiry_time()

    failed_attempts = 0

    for _ in range(5):
        success, message, failed_attempts = verify_otp(
            "000000",
            otp,
            expiry_time,
            failed_attempts
        )

        assert success is False
        assert message == "Invalid OTP"

    success, message, failed_attempts = verify_otp(
        "000000",
        otp,
        expiry_time,
        failed_attempts
    )

    assert success is False
    assert message == "Too many failed attempts"
    assert failed_attempts == 5
def test_successful_verification_is_logged():
    otp = generate_otp()
    expiry_time = get_expiry_time()

    verify_otp(
        otp,
        otp,
        expiry_time
    )

    log_file = Path(__file__).parent.parent / "logs" / "auth.log"
    log_content = log_file.read_text(encoding="utf-8")

    assert "OTP verification successful" in log_content


def test_failed_verification_is_logged():
    otp = generate_otp()
    expiry_time = get_expiry_time()

    verify_otp(
        "000000",
        otp,
        expiry_time
    )

    log_file = Path(__file__).parent.parent / "logs" / "auth.log"
    log_content = log_file.read_text(encoding="utf-8")

    assert "OTP verification failed: invalid OTP" in log_content