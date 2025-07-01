from flask import Blueprint, jsonify, current_app
from datetime import datetime

status_bp = Blueprint("status", __name__)


@status_bp.route("/health")
def health_check():
    """Application health check"""
    return jsonify(
        {
            "status": "healthy",
            "version": current_app.config["APP_VERSION"],
            "timestamp": datetime.utcnow().isoformat(),
        }
    )
