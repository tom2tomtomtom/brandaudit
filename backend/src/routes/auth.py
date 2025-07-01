"""
Authentication routes for the Brand Audit Tool
"""

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
    get_jwt,
)
from marshmallow import Schema, fields, ValidationError
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
import uuid

from src.models.user_model import User, db

auth_bp = Blueprint("auth", __name__)


# Validation schemas
class RegisterSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=lambda x: len(x) >= 8)
    name = fields.Str(required=True, validate=lambda x: len(x.strip()) > 0)
    company = fields.Str(load_default="")


class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True)


# Token blacklist (in production, use Redis or database)
blacklisted_tokens = set()


@auth_bp.route("/register", methods=["POST"])
def register():
    """User registration endpoint"""
    try:
        # Validate input
        schema = RegisterSchema()
        data = schema.load(request.get_json() or {})

        # Check if user already exists
        if User.query.filter_by(email=data["email"]).first():
            return jsonify(
                {"success": False, "error": "User with this email already exists"}
            ), 400

        # Create new user
        user = User(
            id=str(uuid.uuid4()),
            email=data["email"],
            name=data["name"],
            company=data.get("company", ""),
            password_hash=generate_password_hash(data["password"]),
            created_at=datetime.utcnow(),
            is_active=True,
        )

        db.session.add(user)
        db.session.commit()

        # Create tokens
        access_token = create_access_token(
            identity=user.id, additional_claims={"email": user.email, "name": user.name}
        )
        refresh_token = create_refresh_token(identity=user.id)

        return jsonify(
            {
                "success": True,
                "message": "User registered successfully",
                "data": {
                    "user": {
                        "id": user.id,
                        "email": user.email,
                        "name": user.name,
                        "company": user.company,
                    },
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                },
            }
        ), 201

    except ValidationError as e:
        return jsonify(
            {"success": False, "error": "Validation error", "details": e.messages}
        ), 400
    except Exception as e:
        current_app.logger.error(f"Registration error: {str(e)}")
        return jsonify({"success": False, "error": "Registration failed"}), 500


@auth_bp.route("/login", methods=["POST"])
def login():
    """User login endpoint"""
    try:
        # Validate input
        schema = LoginSchema()
        data = schema.load(request.get_json() or {})

        # Find user
        user = User.query.filter_by(email=data["email"]).first()

        if not user or not check_password_hash(user.password_hash, data["password"]):
            return jsonify(
                {"success": False, "error": "Invalid email or password"}
            ), 401

        if not user.is_active:
            return jsonify({"success": False, "error": "Account is deactivated"}), 401

        # Update last login
        user.last_login = datetime.utcnow()
        db.session.commit()

        # Create tokens
        access_token = create_access_token(
            identity=user.id, additional_claims={"email": user.email, "name": user.name}
        )
        refresh_token = create_refresh_token(identity=user.id)

        return jsonify(
            {
                "success": True,
                "message": "Login successful",
                "data": {
                    "user": {
                        "id": user.id,
                        "email": user.email,
                        "name": user.name,
                        "company": user.company,
                    },
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                },
            }
        ), 200

    except ValidationError as e:
        return jsonify(
            {"success": False, "error": "Validation error", "details": e.messages}
        ), 400
    except Exception as e:
        current_app.logger.error(f"Login error: {str(e)}")
        return jsonify({"success": False, "error": "Login failed"}), 500


@auth_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    """Refresh access token"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        if not user or not user.is_active:
            return jsonify(
                {"success": False, "error": "User not found or inactive"}
            ), 404

        # Create new access token
        access_token = create_access_token(
            identity=user.id, additional_claims={"email": user.email, "name": user.name}
        )

        return jsonify({"success": True, "data": {"access_token": access_token}}), 200

    except Exception as e:
        current_app.logger.error(f"Token refresh error: {str(e)}")
        return jsonify({"success": False, "error": "Token refresh failed"}), 500


@auth_bp.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    """User logout endpoint"""
    try:
        # Get the JWT token
        jti = get_jwt()["jti"]

        # Add token to blacklist
        blacklisted_tokens.add(jti)

        return jsonify({"success": True, "message": "Successfully logged out"}), 200

    except Exception as e:
        current_app.logger.error(f"Logout error: {str(e)}")
        return jsonify({"success": False, "error": "Logout failed"}), 500


@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def get_current_user():
    """Get current user information"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        if not user:
            return jsonify({"success": False, "error": "User not found"}), 404

        return jsonify(
            {
                "success": True,
                "data": {
                    "user": {
                        "id": user.id,
                        "email": user.email,
                        "name": user.name,
                        "company": user.company,
                        "created_at": user.created_at.isoformat()
                        if user.created_at
                        else None,
                        "last_login": user.last_login.isoformat()
                        if user.last_login
                        else None,
                    }
                },
            }
        ), 200

    except Exception as e:
        current_app.logger.error(f"Get user error: {str(e)}")
        return jsonify(
            {"success": False, "error": "Failed to get user information"}
        ), 500


# JWT token blacklist checker
def check_if_token_revoked(jwt_header, jwt_payload):
    """Check if JWT token is blacklisted"""
    jti = jwt_payload["jti"]
    return jti in blacklisted_tokens
