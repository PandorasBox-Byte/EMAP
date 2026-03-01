from flask import Blueprint, request, jsonify
from app import db
from models import User, FriendRequest, Friend
import jwt
import os
import qrcode
from io import BytesIO
import base64

bp = Blueprint('friends', __name__, url_prefix='/api/friends')

def verify_token(token):
    """Verify JWT token and return user_id"""
    try:
        payload = jwt.decode(token, os.getenv('SECRET_KEY', 'dev-secret-key'), algorithms=['HS256'])
        return payload.get('user_id')
    except:
        return None

def get_token_from_request():
    """Extract token from Authorization header"""
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return None
    parts = auth_header.split()
    if len(parts) != 2 or parts[0].lower() != 'bearer':
        return None
    return parts[1]

@bp.route('/add-by-code', methods=['POST'])
def add_by_friend_code():
    """Add friend using friend code"""
    token = get_token_from_request()
    user_id = verify_token(token)
    
    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    
    if not data or not data.get('friend_code'):
        return jsonify({'error': 'Missing friend_code'}), 400
    
    friend = User.query.filter_by(friend_code=data.get('friend_code')).first()
    
    if not friend:
        return jsonify({'error': 'Friend code not found'}), 404
    
    if friend.id == user_id:
        return jsonify({'error': 'Cannot add yourself as a friend'}), 400
    
    # Check if already friends
    existing_friend = Friend.query.filter_by(user_id=user_id, friend_id=friend.id).first()
    if existing_friend:
        return jsonify({'error': 'Already friends'}), 409
    
    try:
        # Check if friend request already exists
        existing_request = FriendRequest.query.filter(
            ((FriendRequest.sender_id == user_id) & (FriendRequest.receiver_id == friend.id)) |
            ((FriendRequest.sender_id == friend.id) & (FriendRequest.receiver_id == user_id))
        ).first()
        
        if existing_request:
            return jsonify({'error': 'Friend request already exists'}), 409
        
        # Create friend request
        friend_request = FriendRequest(
            sender_id=user_id,
            receiver_id=friend.id
        )
        
        db.session.add(friend_request)
        db.session.commit()
        
        return jsonify({
            'message': 'Friend request sent',
            'request_id': friend_request.id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/qr-code', methods=['GET'])
def get_qr_code():
    """Generate QR code for friend code"""
    token = get_token_from_request()
    user_id = verify_token(token)
    
    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401
    
    user = User.query.filter_by(id=user_id).first()
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(user.friend_code)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    img_io = BytesIO()
    img.save(img_io, 'PNG')
    img_io.seek(0)
    img_base64 = base64.b64encode(img_io.getvalue()).decode()
    
    return jsonify({
        'qr_code': f'data:image/png;base64,{img_base64}',
        'friend_code': user.friend_code
    }), 200

@bp.route('/requests', methods=['GET'])
def get_friend_requests():
    """Get pending friend requests"""
    token = get_token_from_request()
    user_id = verify_token(token)
    
    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401
    
    requests = FriendRequest.query.filter_by(receiver_id=user_id, status='pending').all()
    
    return jsonify({
        'requests': [
            {
                'id': req.id,
                'sender': User.query.get(req.sender_id).to_dict(),
                'created_at': req.created_at.isoformat()
            } for req in requests
        ]
    }), 200

@bp.route('/request/<request_id>/accept', methods=['POST'])
def accept_friend_request(request_id):
    """Accept a friend request"""
    token = get_token_from_request()
    user_id = verify_token(token)
    
    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401
    
    friend_req = FriendRequest.query.filter_by(id=request_id).first()
    
    if not friend_req:
        return jsonify({'error': 'Friend request not found'}), 404
    
    if friend_req.receiver_id != user_id:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        friend_req.status = 'accepted'
        
        # Add both directions to friend list
        friend1 = Friend(user_id=friend_req.sender_id, friend_id=friend_req.receiver_id)
        friend2 = Friend(user_id=friend_req.receiver_id, friend_id=friend_req.sender_id)
        
        db.session.add(friend1)
        db.session.add(friend2)
        db.session.commit()
        
        return jsonify({'message': 'Friend request accepted'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/list', methods=['GET'])
def get_friends():
    """Get list of friends"""
    token = get_token_from_request()
    user_id = verify_token(token)
    
    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401
    
    friends = Friend.query.filter_by(user_id=user_id).all()
    
    return jsonify({
        'friends': [
            User.query.get(friend.friend_id).to_dict() for friend in friends
        ]
    }), 200
