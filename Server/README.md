# EMA Server - Encrypted Messaging Application

A secure, end-to-end encrypted messaging server built with Flask and PostgreSQL. Includes a professional HTTPS admin dashboard for server management.

## 🎯 Features

### Core Messaging
- ✅ End-to-end encryption using Signal Protocol (libsignal)
- ✅ Offline message caching with delivery tracking
- ✅ Device identification and binding
- ✅ Real-time user online/offline status
- ✅ Message history with encryption metadata

### Friend Management
- ✅ Unique friend codes for user discovery
- ✅ QR code generation for easy friend code sharing
- ✅ Friend request system with accept/reject
- ✅ Bidirectional friendship tracking
- ✅ Friend list management

### Admin Dashboard (NEW!)
- ✅ Secure HTTPS admin panel at `/admin/`
- ✅ Real-time server statistics and monitoring
- ✅ User management (view, search, delete)
- ✅ Message monitoring and delivery tracking
- ✅ Friend request management
- ✅ Professional responsive UI with dark theme
- ✅ Session-based authentication with secure cookies
- ✅ API rate limiting and security headers

### Deployment
- ✅ Automatic Git-based updates
- ✅ PostgreSQL database with SQLAlchemy ORM
- ✅ Gunicorn WSGI application server
- ✅ Nginx reverse proxy with HTTPS
- ✅ Let's Encrypt SSL certificate automation
- ✅ Systemd service for process management
- ✅ Comprehensive deployment automation

## 📋 Quick Start

### Development Setup

```bash
# Clone and setup
cd Server
./setup_dev.sh
source venv/bin/activate

# Run server
python app.py
```

**Access:**
- API: http://localhost:5000
- Admin Panel: http://localhost:5000/admin/
- Default credentials: `admin` / `admin123`

### Production Deployment

```bash
sudo chmod +x deploy_to_linux.sh
sudo ./deploy_to_linux.sh your-domain.com admin@example.com
```

This automated script:
- Sets up Ubuntu with all dependencies
- Configures PostgreSQL database
- Creates Python virtual environment
- Installs Python packages
- Configures Gunicorn + Nginx
- Obtains SSL certificate from Let's Encrypt
- Starts all services automatically

## 📁 Project Structure

```
Server/
├── app.py                      # Flask application entry point
├── models.py                   # SQLAlchemy database models
├── requirements.txt            # Python dependencies
├── update_manager.py          # Auto-update system with GitPython
├── git_config.json            # Git tracking configuration
│
├── admin/                     # Admin panel package
│   ├── __init__.py
│   └── admin_routes.py        # Admin endpoints and logic
│
├── routes/                    # API routes
│   ├── __init__.py
│   ├── auth_routes.py         # User registration/login
│   ├── message_routes.py      # Message sending/receiving
│   └── friend_routes.py       # Friend management
│
├── templates/                 # HTML templates
│   ├── admin_login.html       # Secure login page
│   ├── admin_dashboard.html   # Main dashboard
│   ├── admin_users.html       # User management
│   ├── admin_messages.html    # Message monitoring
│   └── admin_requests.html    # Friend request management
│
├── deploy_to_linux.sh        # Complete Ubuntu setup automation
├── setup_dev.sh              # Development environment setup
├── ema.service               # Systemd service file
├── nginx_config.conf         # Nginx reverse proxy config
├── .env.example              # Environment variables template
└── ADMIN_PANEL_GUIDE.md      # Comprehensive admin documentation
```

## 🔑 API Endpoints

### Authentication
- `POST /register` - Create new user account
- `POST /login` - User login with device ID
- `POST /logout` - Logout user
- `GET /user/<user_id>` - Get user profile

### Messages
- `POST /send` - Send encrypted message
- `GET /get` - Get messages for user
- `POST /mark-delivered` - Mark message as delivered
- `GET /history/<user_id>` - Get conversation history

### Friends
- `POST /add-by-code` - Add friend by code
- `GET /qr-code` - Get QR code for friend code
- `POST /request/<user_id>/accept` - Accept friend request
- `GET /requests` - Get pending friend requests
- `GET /list` - Get friend list

### Admin Panel
- `POST /admin/login` - Admin authentication
- `GET /admin/` - Dashboard
- `GET /admin/users` - User management page
- `GET /admin/messages` - Message monitoring
- `GET /admin/requests` - Friend requests
- `GET /admin/api/stats` - Real-time statistics
- `GET /admin/api/health` - Server health check

## 🔒 Security

### Encryption
- **Signal Protocol**: Industry-standard E2E encryption
- **AES-256**: Message encryption in transit
- **Device Binding**: Unique device identification
- **Perfect Forward Secrecy**: Keys rotated with Signal protocol

### Authentication
- **JWT Tokens**: 30-day expiration (API)
- **Secure Sessions**: HTTP-only cookies (Admin)
- **Bcrypt Hashing**: Password hashing with Werkzeug
- **HTTPS/TLS**: All connections encrypted
- **CSRF Protection**: Flask session security

### Network Security
- **Nginx Reverse Proxy**: Hides internal service
- **Rate Limiting**: API and admin panel protected
- **Security Headers**: HSTS, X-Frame-Options, CSP
- **Firewall Ready**: Easily restricted to specific ports
- **Let's Encrypt**: Automatic SSL certificate management

## 📊 Admin Dashboard Features

### Real-time Monitoring
```
📊 Statistics
  • Total Users
  • Online Users
  • Total Messages
  • Undelivered Messages
  • Recent Messages (last 10)

🔄 Auto-refresh every 5 seconds
```

### User Management
```
Column      Function
────────────────────────────────────
Username    Display name
Friend Code Unique ID for sharing
Status      Online/Offline indicator
Created     Account creation date
Last Seen   Last activity timestamp
Actions     Delete user
```

### Message Monitoring
```
Filter by:
  • All messages
  • Delivered messages
  • Undelivered/Pending
  
View:
  • Sender/Receiver
  • Timestamp
  • Delivery status
  • Message preview
```

### Friend Request Management
```
Filter by:
  • Pending requests
  • Accepted requests
  • Rejected requests
  
Actions:
  • View sender/receiver
  • Delete requests
```

## 🚀 Environment Configuration

**Development (.env.example):**
```bash
FLASK_ENV=development
DEBUG=True
DATABASE_URL=sqlite:///ema.db
ADMIN_USERNAME=admin
ADMIN_PASSWORD_HASH=<your-hash>
SESSION_COOKIE_SECURE=False
```

**Production (.env after deployment):**
```bash
FLASK_ENV=production
DEBUG=False
DATABASE_URL=postgresql://user:pass@localhost/ema_db
ADMIN_USERNAME=admin
ADMIN_PASSWORD_HASH=<your-hash>
SESSION_COOKIE_SECURE=True
```

## 📞 Support Commands

```bash
# View service status
sudo systemctl status ema

# View logs (live)
sudo journalctl -u ema -f

# Restart service
sudo systemctl restart ema

# View configuration
cat /opt/ema/.env

# Check SSL certificate
sudo certbot certificates

# Database backup
sudo -u postgres pg_dump ema_db > backup.sql
```

## 🔄 Auto-Updates

The server automatically checks for Git updates every hour:
- Configured in `git_config.json`
- Uses GitPython for safe pulls
- Logs updates in service logs
- No downtime for checks

## 📚 Documentation

- [ADMIN_PANEL_GUIDE.md](ADMIN_PANEL_GUIDE.md) - Complete admin setup and usage guide
- [requirements.txt](requirements.txt) - All Python dependencies
- [.env.example](.env.example) - Configuration template

## ⚙️ Technology Stack

| Layer | Technology |
|-------|-----------|
| Framework | Flask 2.3.0 |
| ORM | SQLAlchemy 3.0.5 |
| Database | PostgreSQL + SQLite (dev) |
| Encryption | Signal Protocol + AES-256 |
| Auth | JWT + Bcrypt + Sessions |
| Server | Gunicorn + Nginx |
| SSL | Let's Encrypt + Certbot |
| VCS | Git + GitPython |
| Security | Werkzeug + Flask-CORS |

## 🎓 Getting Started

1. **Understand the code**: Review `app.py` and `models.py`
2. **Local development**: Run `./setup_dev.sh` and `python app.py`
3. **Admin panel**: Access at http://localhost:5000/admin/
4. **Deploy**: Use `./deploy_to_linux.sh` on Ubuntu server
5. **Monitor**: Use admin dashboard for real-time stats

## 📝 License

[Your License Here]

## 🔗 Related

- Client App: See `/Client` folder
- Git Repository: Auto-update configured in `git_config.json`
