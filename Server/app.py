from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os
from dotenv import load_dotenv
from update_manager import check_updates_on_startup
from datetime import timedelta

load_dotenv()

app = Flask(__name__)
CORS(app)

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///ema.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')

# Session configuration for admin panel
app.config['SESSION_COOKIE_SECURE'] = os.getenv('SESSION_COOKIE_SECURE', 'False').lower() == 'true'
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)

db = SQLAlchemy(app)

# Import models and routes
from models import User, Message, FriendRequest
from routes import auth_routes, message_routes, friend_routes
from admin import bp as admin_bp

# Register blueprints
app.register_blueprint(auth_routes.bp)
app.register_blueprint(message_routes.bp)
app.register_blueprint(friend_routes.bp)
app.register_blueprint(admin_bp)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy'}), 200

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Resource not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Check for updates on startup
    check_updates_on_startup()
    
    with app.app_context():
        db.create_all()
    app.run(debug=os.getenv('DEBUG', False), port=int(os.getenv('PORT', 5000)))
