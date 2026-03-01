from flask import Blueprint, request, jsonify
from app import db
from models import Message, User
import jwt
import os
from datetime import datetime

bp = Blueprint('messages', __name__, url_prefix='/api/messages')

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

@bp.route('/send', methods=['POST'])
def send_message():
    """Send an encrypted message"""
    token = get_token_from_request()
    user_id = verify_token(token)
    
    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    
    if not data or not data.get('receiver_id') or not data.get('encrypted_content'):
        return jsonify({'error': 'Missing required fields: receiver_id, encrypted_content'}), 400
    
    receiver = User.query.filter_by(id=data.get('receiver_id')).first()
    
    if not receiver:
        return jsonify({'error': 'Receiver not found'}), 404
    
    try:
        # Create message
        message = Message(
            sender_id=user_id,
            receiver_id=data.get('receiver_id'),
            encrypted_content=data.get('encrypted_content')
        )
        
        # If receiver is online, mark as delivered immediately
        if receiver.is_online:
            message.is_delivered = True
            message.delivered_at = datetime.utcnow()
        
        db.session.add(message)
        db.session.commit()
        
        return jsonify({
            'message': 'Message sent successfully',
            'message_id': message.id,
            'is_delivered': message.is_delivered
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/get/<receiver_id>', methods=['GET'])
def get_messages(receiver_id):
    """Get undelivered messages for a user"""
    token = get_token_from_request()
    user_id = verify_token(token)
    
    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401
    
    # receiver_id in URL is actually the message recipient (the one requesting messages)
    messages = Message.query.filter_by(
        receiver_id=user_id,
        is_delivered=False
    ).all()
    
    return jsonify({
        'messages': [msg.to_dict() for msg in messages]
    }), 200

@bp.route('/mark-delivered/<message_id>', methods=['POST'])
def mark_delivered(message_id):
    """Mark a message as delivered"""
    token = get_token_from_request()
    user_id = verify_token(token)
    
    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401
    
    message = Message.query.filter_by(id=message_id).first()
    
    if not message:
        return jsonify({'error': 'Message not found'}), 404
    
    if message.receiver_id != user_id:
        return jsonify({'error': 'Unauthorized'}), 401
    
    message.is_delivered = True
    message.delivered_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({'message': 'Message marked as delivered'}), 200

@bp.route('/history/<other_user_id>', methods=['GET'])
def get_message_history(other_user_id):
    """Get message history with another user"""
    token = get_token_from_request()
    user_id = verify_token(token)
    
    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401
    
    limit = request.args.get('limit', 50, type=int)
    
    messages = Message.query.filter(
        ((Message.sender_id == user_id) & (Message.receiver_id == other_user_id)) |
        ((Message.sender_id == other_user_id) & (Message.receiver_id == user_id))
    ).order_by(Message.created_at.desc()).limit(limit).all()
    
    return jsonify({
        'messages': [msg.to_dict() for msg in reversed(messages)]
    }), 200
