from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from database import User, db
from datetime import datetime

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/user/register', methods=['POST'])
def register_user():
    """Register a new user"""
    try:
        data = request.get_json()
        
        # Validation
        if not data.get('username') or not data.get('email') or not data.get('password'):
            return jsonify({'message': 'Username, email, and password are required'}), 400
        
        # Check if user exists
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'message': 'Username already exists'}), 400
        
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'message': 'Email already exists'}), 400
        
        # Create new user
        user = User(
            username=data['username'],
            email=data['email'],
            role='user'
        )
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({
            'message': 'User registered successfully',
            'user': user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Registration failed: {str(e)}'}), 500

@auth_bp.route('/user/login', methods=['POST'])
def login_user():
    """User login"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'message': 'Username and password are required'}), 400
        
        user = User.query.filter_by(username=username, role='user').first()
        
        if not user or not user.check_password(password):
            return jsonify({'message': 'Invalid username or password'}), 401
        
        # Create access token - ensure 'sub' (identity) is a string to satisfy JWT libraries
        access_token = create_access_token(identity=str(user.id), additional_claims={'role': user.role})
        
        return jsonify({
            'token': access_token,
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Login failed: {str(e)}'}), 500

@auth_bp.route('/admin/login', methods=['POST'])
def login_admin():
    """Admin login"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'message': 'Username and password are required'}), 400
        
        admin = User.query.filter_by(username=username, role='admin').first()
        
        if not admin or not admin.check_password(password):
            return jsonify({'message': 'Invalid admin credentials'}), 401
        
        # Create access token - ensure 'sub' (identity) is a string to satisfy JWT libraries
        access_token = create_access_token(identity=str(admin.id), additional_claims={'role': admin.role})
        
        return jsonify({
            'token': access_token,
            'user': admin.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Login failed: {str(e)}'}), 500


