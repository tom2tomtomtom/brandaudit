"""
AI Brand Audit Tool - Main Application
Secure Flask application with proper configuration management
"""

import os
import sys
import logging
from datetime import datetime, timedelta

from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv

from src.celery_app import make_celery
from src.extensions import cache
from src.config import get_config
from src.extensions import db
from src.routes.user import user_bp
from src.routes.brand_audit import brand_audit_bp
from src.routes.auth import auth_bp
from src.routes.status import status_bp

# Add src directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Load environment variables
if os.environ.get('RAILWAY_ENVIRONMENT'):
    # Load production environment file in Railway
    load_dotenv('.env.production')
else:
    load_dotenv()


def create_app(config_name=None):
    """Application factory pattern"""
    app = Flask(__name__)

    # Load configuration
    config_class = get_config(config_name)
    app.config.from_object(config_class)

    # Initialize configuration
    config_class.init_app(app)

    # Configure logging
    configure_logging(app)

    # Initialize extensions
    initialize_extensions(app)

    # Register blueprints
    register_blueprints(app)

    # Register error handlers
    register_error_handlers(app)

    return app


def configure_logging(app):
    """Configure application logging"""
    if not app.debug and not app.testing:
        # Production logging
        if not os.path.exists("logs"):
            os.mkdir("logs")

        file_handler = logging.FileHandler("logs/brand_audit.log")
        file_handler.setFormatter(logging.Formatter(app.config["LOG_FORMAT"]))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info("Brand Audit Tool startup")


def initialize_extensions(app):
    """Initialize Flask extensions"""
    # Database
    db.init_app(app)

    # Initialize Cache
    cache.init_app(app)

    # CORS with secure configuration
    CORS(
        app,
        origins=app.config["ALLOWED_ORIGINS"],
        supports_credentials=True,
        allow_headers=["Content-Type", "Authorization"],
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    )

    # JWT Authentication
    jwt = JWTManager(app)

    # Configure JWT
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)
    app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=30)

    # Celery Configuration
    app.config["CELERY_BROKER_URL"] = os.environ.get(
        "CELERY_BROKER_URL", "redis://localhost:6379/0"
    )
    app.config["CELERY_RESULT_BACKEND"] = os.environ.get(
        "CELERY_RESULT_BACKEND", "redis://localhost:6379/0"
    )

    # Initialize Celery
    celery = make_celery(app)
    app.celery = celery

    # Rate Limiting
    Limiter(
        app=app,
        key_func=get_remote_address,
        storage_uri=app.config["RATELIMIT_STORAGE_URL"],
        default_limits=[app.config["RATELIMIT_DEFAULT"]],
    )

    # JWT error handlers
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({"error": "Token has expired"}), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({"error": "Invalid token"}), 401

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({"error": "Authorization token is required"}), 401


def register_blueprints(app):
    """Register application blueprints"""
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(user_bp, url_prefix="/api")
    app.register_blueprint(brand_audit_bp, url_prefix="/api")
    app.register_blueprint(status_bp, url_prefix="/api")


def register_error_handlers(app):
    """Register global error handlers"""

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify(
            {
                "error": "Bad request",
                "message": "The request could not be understood by the server",
            }
        ), 400

    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify(
            {"error": "Unauthorized", "message": "Authentication is required"}
        ), 401

    @app.errorhandler(403)
    def forbidden(error):
        return jsonify(
            {
                "error": "Forbidden",
                "message": "You do not have permission to access this resource",
            }
        ), 403

    @app.errorhandler(404)
    def not_found(error):
        return jsonify(
            {"error": "Not found", "message": "The requested resource was not found"}
        ), 404

    @app.errorhandler(429)
    def ratelimit_handler(error):
        return jsonify(
            {
                "error": "Rate limit exceeded",
                "message": "Too many requests. Please try again later.",
            }
        ), 429

    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f"Server Error: {error}")
        return jsonify(
            {
                "error": "Internal server error",
                "message": "An unexpected error occurred",
            }
        ), 500


# Create application instance
app = create_app()

# Initialize database tables
with app.app_context():
    try:
        db.create_all()
        app.logger.info("Database tables created successfully")
    except Exception as e:
        app.logger.error(f"Database initialization failed: {e}")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=False)


# Health check endpoint
@app.route("/api/health")
def health_check():
    """Application health check"""
    return jsonify(
        {
            "status": "healthy",
            "version": app.config["APP_VERSION"],
            "timestamp": datetime.utcnow().isoformat(),
        }
    )


@app.route('/')
def root():
    """Root endpoint - API status"""
    return jsonify({
        "message": "AI Brand Audit Tool API",
        "version": app.config["APP_VERSION"],
        "status": "running"
    })