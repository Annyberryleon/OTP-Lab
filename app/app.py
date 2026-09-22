import os
import redis
from datetime import datetime

from flask import Flask, jsonify, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from prometheus_flask_exporter import PrometheusMetrics
from prometheus_client import Counter

from otp import generate_otp, get_expiry_time, verify_otp

app = Flask(__name__)


@app.after_request
def add_security_headers(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    return response


redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=6379,
    decode_responses=True
)

metrics = PrometheusMetrics(app, path="/metrics")

otp_generated_total = Counter(
    "otp_generated_total",
    "Total number of OTPs generated"
)

otp_verification_success_total = Counter(
    "otp_verification_success_total",
    "Total number of successful OTP verifications"
)

otp_verification_failed_total = Counter(
    "otp_verification_failed_total",
    "Total number of failed OTP verifications"
)

otp_expired_total = Counter(
    "otp_expired_total",
    "Total number of expired OTP verification attempts"
)

otp_blocked_total = Counter(
    "otp_blocked_total",
    "Total number of OTP verification attempts blocked due to too many failed attempts"
)

limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    storage_uri=f"redis://{os.getenv('REDIS_HOST', 'localhost')}:6379",
    default_limits=[]
)

OTP_KEY = "otp:current"


@app.route("/")
def home():
    return "OTP Lab is running!"


@app.route("/health")
def health():
    return jsonify({
        "status": "healthy"
    })


@app.route("/otp/generate")
@limiter.limit("5 per minute")
def generate():
    otp = generate_otp()
    otp_expiry = get_expiry_time()

    redis_client.hset(
        OTP_KEY,
        mapping={
            "otp": otp,
            "expires_at": otp_expiry.isoformat(),
            "failed_attempts": 0
        }
    )

    redis_client.expire(
        OTP_KEY,
        int(os.getenv("OTP_EXPIRY_SECONDS", "300"))
    )

    otp_generated_total.inc()

    return jsonify({
        "otp": otp,
        "expires_at": otp_expiry.isoformat()
    })


@app.route("/otp/verify", methods=["POST"])
@limiter.limit("5 per minute")
def verify():
    data = request.get_json()

    if not data or "otp" not in data:
        return jsonify({
            "success": False,
            "message": "OTP is required"
        }), 400

    submitted_otp = str(data["otp"])

    if not submitted_otp.isdigit() or len(submitted_otp) != 6:
        return jsonify({
            "success": False,
            "message": "OTP must be exactly 6 digits"
        }), 400

    otp_data = redis_client.hgetall(OTP_KEY)

    if not otp_data:
        return jsonify({
            "success": False,
            "message": "No OTP has been generated"
        }), 400

    stored_otp = otp_data["otp"]
    otp_expiry = datetime.fromisoformat(otp_data["expires_at"])
    failed_attempts = int(otp_data.get("failed_attempts", 0))

    success, message, failed_attempts = verify_otp(
        submitted_otp,
        stored_otp,
        otp_expiry,
        failed_attempts
    )

    if success:
        otp_verification_success_total.inc()

        redis_client.delete(OTP_KEY)

        return jsonify({
            "success": True,
            "message": message
        })

    otp_verification_failed_total.inc()

    if message == "OTP has expired":
        otp_expired_total.inc()

    if message == "Too many failed attempts":
        otp_blocked_total.inc()

    if message == "Invalid OTP":
        redis_client.hset(
            OTP_KEY,
            "failed_attempts",
            failed_attempts
        )

    return jsonify({
        "success": False,
        "message": message,
        "failed_attempts": failed_attempts
    }), 401


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )