from flask import Flask, jsonify, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from otp import generate_otp, get_expiry_time, verify_otp


app = Flask(__name__)

limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=[]
)

stored_otp = None
otp_expiry = None
failed_attempts = 0


@app.route("/")
def home():
    return "OTP Lab is running!"


@app.route("/otp/generate")
@limiter.limit("5 per minute")
def generate():
    global stored_otp, otp_expiry, failed_attempts

    stored_otp = generate_otp()
    otp_expiry = get_expiry_time()
    failed_attempts = 0

    return jsonify({
        "otp": stored_otp,
        "expires_at": otp_expiry.isoformat()
    })


@app.route("/otp/verify", methods=["POST"])
@limiter.limit("5 per minute")
def verify():
    global stored_otp, otp_expiry, failed_attempts

    data = request.get_json()

    if not data or "otp" not in data:
        return jsonify({
            "success": False,
            "message": "OTP is required"
        }), 400

    if stored_otp is None or otp_expiry is None:
        return jsonify({
            "success": False,
            "message": "No OTP has been generated"
        }), 400

    success, message, failed_attempts = verify_otp(
        data["otp"],
        stored_otp,
        otp_expiry,
        failed_attempts
    )

    if success:
        stored_otp = None
        otp_expiry = None
        failed_attempts = 0

        return jsonify({
            "success": True,
            "message": message
        })

    return jsonify({
        "success": False,
        "message": message,
        "failed_attempts": failed_attempts
    }), 401


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)