from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt

def admin_required(f):
    """Decorator to require admin role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        claims = get_jwt()
        if claims.get('role') != 'admin':
            return jsonify({'message': 'Admin access required'}), 403
        return f(*args, **kwargs)
    return decorated_function

def user_required(f):
    """Decorator to require user role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        claims = get_jwt()
        role = claims.get('role')
        if role not in ['user', 'admin']:  # Admin can also access user endpoints
            return jsonify({'message': 'Authentication required'}), 403
        return f(*args, **kwargs)
    return decorated_function



