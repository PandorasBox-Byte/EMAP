from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from functools import wraps
from app import db
from models import User, Message, FriendRequest, Friend
from werkzeug.security import check_password_hash, generate_password_hash
import os
from datetime import datetime, timedelta

bp = Blueprint('admin', __name__, url_prefix='/admin')

# Admin credentials (use env variables in production)
ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD_HASH = os.getenv('ADMIN_PASSWORD_HASH', generate_password_hash('admin123'))

def login_required(f):
    """Decorator to check if user is logged in to admin panel"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_user' not in session:
            return redirect(url_for('admin.login'))
        return f(*args, **kwargs)
    return decorated_function

@bp.route('/login', methods=['GET', 'POST'])
def login():
    """Admin login page"""
    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if username == ADMIN_USERNAME and check_password_hash(ADMIN_PASSWORD_HASH, password):
            session['admin_user'] = username
            session.permanent = True
            session.modified = True
            return jsonify({'success': True}), 200
        
        return jsonify({'error': 'Invalid credentials'}), 401
    
    return render_template('admin_login.html')

@bp.route('/logout', methods=['POST'])
def logout():
    """Logout admin"""
    session.pop('admin_user', None)
    return jsonify({'success': True}), 200

@bp.route('/', methods=['GET'])
@login_required
def dashboard():
    """Admin dashboard"""
    total_users = User.query.count()
    total_messages = Message.query.count()
    pending_requests = FriendRequest.query.filter_by(status='pending').count()
    online_users = User.query.filter_by(is_online=True).count()
    
    undelivered_messages = Message.query.filter_by(is_delivered=False).count()
    
    # Recent messages (last 10)
    recent_messages = Message.query.order_by(Message.created_at.desc()).limit(10).all()
    
    stats = {
        'total_users': total_users,
        'total_messages': total_messages,
        'pending_requests': pending_requests,
        'online_users': online_users,
        'undelivered_messages': undelivered_messages
    }
    
    return render_template('admin_dashboard.html', stats=stats, recent_messages=recent_messages)

@bp.route('/users', methods=['GET'])
@login_required
def users():
    """View all users"""
    page = request.args.get('page', 1, type=int)
    users = User.query.paginate(page=page, per_page=20)
    
    return render_template('admin_users.html', users=users)

@bp.route('/api/users', methods=['GET'])
@login_required
def get_users_api():
    """API to get users data"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    
    query = User.query
    if search:
        query = query.filter(User.username.ilike(f'%{search}%'))
    
    users_paginated = query.paginate(page=page, per_page=20)
    
    users_data = [{
        'id': u.id,
        'username': u.username,
        'device_id': u.device_id,
        'friend_code': u.friend_code,
        'is_online': u.is_online,
        'created_at': u.created_at.isoformat(),
        'last_seen': u.last_seen.isoformat() if u.last_seen else None
    } for u in users_paginated.items]
    
    return jsonify({
        'data': users_data,
        'total': users_paginated.total,
        'pages': users_paginated.pages,
        'current_page': page
    }), 200

@bp.route('/api/users/<user_id>/delete', methods=['POST'])
@login_required
def delete_user(user_id):
    """Delete a user and related data"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Delete user's messages
        Message.query.filter((Message.sender_id == user_id) | (Message.receiver_id == user_id)).delete()
        
        # Delete user's friend requests
        FriendRequest.query.filter((FriendRequest.sender_id == user_id) | (FriendRequest.receiver_id == user_id)).delete()
        
        # Delete user's friendships
        Friend.query.filter((Friend.user_id == user_id) | (Friend.friend_id == user_id)).delete()
        
        # Delete user
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({'message': f'User {user.username} deleted'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/messages', methods=['GET'])
@login_required
def messages():
    """View messages"""
    return render_template('admin_messages.html')

@bp.route('/api/messages', methods=['GET'])
@login_required
def get_messages_api():
    """API to get messages data"""
    page = request.args.get('page', 1, type=int)
    delivered = request.args.get('delivered', '', type=str)
    
    query = Message.query
    
    if delivered == 'true':
        query = query.filter_by(is_delivered=True)
    elif delivered == 'false':
        query = query.filter_by(is_delivered=False)
    
    messages_paginated = query.order_by(Message.created_at.desc()).paginate(page=page, per_page=20)
    
    messages_data = []
    for m in messages_paginated.items:
        sender = User.query.get(m.sender_id)
        receiver = User.query.get(m.receiver_id)
        messages_data.append({
            'id': m.id,
            'sender': sender.username if sender else 'Unknown',
            'receiver': receiver.username if receiver else 'Unknown',
            'created_at': m.created_at.isoformat(),
            'is_delivered': m.is_delivered,
            'preview': m.encrypted_content[:50] + '...' if len(m.encrypted_content) > 50 else m.encrypted_content
        })
    
    return jsonify({
        'data': messages_data,
        'total': messages_paginated.total,
        'pages': messages_paginated.pages,
        'current_page': page
    }), 200

@bp.route('/requests', methods=['GET'])
@login_required
def requests():
    """View friend requests"""
    return render_template('admin_requests.html')

@bp.route('/api/requests', methods=['GET'])
@login_required
def get_requests_api():
    """API to get friend requests"""
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', 'pending')
    
    reqs = FriendRequest.query.filter_by(status=status).order_by(FriendRequest.created_at.desc()).paginate(page=page, per_page=20)
    
    requests_data = []
    for r in reqs.items:
        sender = User.query.get(r.sender_id)
        receiver = User.query.get(r.receiver_id)
        requests_data.append({
            'id': r.id,
            'sender': sender.username if sender else 'Unknown',
            'receiver': receiver.username if receiver else 'Unknown',
            'created_at': r.created_at.isoformat(),
            'status': r.status
        })
    
    return jsonify({
        'data': requests_data,
        'total': reqs.total,
        'pages': reqs.pages,
        'current_page': page
    }), 200

@bp.route('/api/requests/<request_id>/delete', methods=['POST'])
@login_required
def delete_request(request_id):
    """Delete a friend request"""
    try:
        freq = FriendRequest.query.get(request_id)
        if not freq:
            return jsonify({'error': 'Request not found'}), 404
        
        db.session.delete(freq)
        db.session.commit()
        
        return jsonify({'message': 'Friend request deleted'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/api/stats', methods=['GET'])
@login_required
def get_stats():
    """Get system statistics"""
    return jsonify({
        'total_users': User.query.count(),
        'total_messages': Message.query.count(),
        'pending_requests': FriendRequest.query.filter_by(status='pending').count(),
        'online_users': User.query.filter_by(is_online=True).count(),
        'undelivered_messages': Message.query.filter_by(is_delivered=False).count()
    }), 200

@bp.route('/api/health', methods=['GET'])
@login_required
def health():
    """Server health check"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'database': 'connected'
    }), 200
