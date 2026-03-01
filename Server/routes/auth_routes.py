from flask import Blueprint, request, jsonify
from app import db
from models import User, FriendRequest
import uuid
import random
import string
import jwt
from datetime import datetime, timedelta
import os

bp = Blueprint('auth', __name__, url_prefix='/api/auth')

def generate_friend_code():
    """Generate a unique 12-character friend code"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))

@bp.route('/register', methods=['POST'])
def register():
    """Register a new user with username and device ID"""
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('device_id') or not data.get('public_key'):
        return jsonify({'error': 'Missing required fields: username, device_id, public_key'}), 400
    
    username = data.get('username').strip()
    device_id = data.get('device_id').strip()
    public_key = data.get('public_key').strip()
    
    # Validate username
    if len(username) < 3 or len(username) > 50:
        return jsonify({'error': 'Username must be between 3 and 50 characters'}), 400
    
    # Check if username already exists
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return jsonify({'error': 'Username already taken'}), 409
    
    # Check if device ID already registered
    existing_device = User.query.filter_by(device_id=device_id).first()
    if existing_device:
        return jsonify({'error': 'Device already registered. Username is immutable.'}), 409
    
    try:
        # Generate friend code
        friend_code = generate_friend_code()
        while User.query.filter_by(friend_code=friend_code).first():
            friend_code = generate_friend_code()
        
        # Create new user
        new_user = User(
            username=username,
            device_id=device_id,
            public_key=public_key,
            friend_code=friend_code
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        # Generate JWT token
        token = jwt.encode({
            'user_id': new_user.id,
            'exp': datetime.utcnow() + timedelta(days=30)
        }, os.getenv('SECRET_KEY', 'dev-secret-key'), algorithm='HS256')
        
        return jsonify({
            'message': 'User registered successfully',
            'user': new_user.to_dict(),
            'token': token,
            'friend_code': new_user.friend_code
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/login', methods=['POST'])
def login():
    """Login user by device ID"""
    data = request.get_json()
    
    if not data or not data.get('device_id'):
        return jsonify({'error': 'Missing device_id'}), 400
    
    user = User.query.filter_by(device_id=data.get('device_id')).first()
    
    if not user:
        return jsonify({'error': 'Device not registered'}), 404
    
    # Update last seen and online status
    user.last_seen = datetime.utcnow()
    user.is_online = True
    db.session.commit()
    
    # Generate JWT token
    token = jwt.encode({
        'user_id': user.id,
        'exp': datetime.utcnow() + timedelta(days=30)
    }, os.getenv('SECRET_KEY', 'dev-secret-key'), algorithm='HS256')
    
    return jsonify({
        'message': 'Login successful',
        'user': user.to_dict(),
        'token': token
    }), 200

@bp.route('/logout', methods=['POST'])
def logout():
    """Logout user"""
    data = request.get_json()
    
    if not data or not data.get('user_id'):
        return jsonify({'error': 'Missing user_id'}), 400
    
    user = User.query.filter_by(id=data.get('user_id')).first()
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    user.is_online = False
    user.last_seen = datetime.utcnow()
    db.session.commit()
    
    return jsonify({'message': 'Logged out successfully'}), 200

@bp.route('/user/<user_id>', methods=['GET'])
def get_user(user_id):
    """Get user information by ID"""
    user = User.query.filter_by(id=user_id).first()
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify(user.to_dict()), 200
