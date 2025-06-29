from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from src.models.user import User

def role_required(required_roles):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            current_user_id = get_jwt_identity()
            user = User.query.get(current_user_id)

            if not user:
                return jsonify({'msg': 'User not found'}), 404

            if user.role not in required_roles:
                return jsonify({'msg': 'Access forbidden: insufficient role'}), 403

            return fn(*args, **kwargs)
        return wrapper
    return decorator
