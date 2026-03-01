# EMA Admin Panel - Deployment & Usage Guide

## Overview
The EMA Admin Panel is a secure HTTPS-based management interface for your encrypted messaging server. It provides real-time monitoring of users, messages, and friend requests with a professional dashboard.

## 🔒 Security Features

- **Password-Protected Login**: Secure authentication with bcrypt hashing
- **Session Management**: Secure HTTP-only cookies with automatic expiration
- **HTTPS/TLS**: All connections encrypted with Let's Encrypt SSL
- **CSRF Protection**: Built-in Flask session security
- **Rate Limiting**: API rate limits to prevent brute force attacks
- **Admin Isolation**: Admin panel runs on separate authentication system
- **Security Headers**: HSTS, X-Frame-Options, CSP, and more

## 🚀 Quick Start (Development)

### 1. Setup Development Environment

```bash
cd Server
./setup_dev.sh
source venv/bin/activate
python app.py
```

### 2. Access Admin Panel

- **URL**: http://localhost:5000/admin/
- **Username**: admin
- **Password**: admin123

⚠️ **Change the default password immediately in production!**

## 📡 Production Deployment on Linux

### Prerequisites
- Ubuntu 20.04 or later
- Root or sudo access
- Domain name (for HTTPS with Let's Encrypt)
- Email address (for SSL certificates)

### Deployment Steps

1. **Prepare your server**:
   ```bash
   sudo apt-get update
   sudo apt-get upgrade -y
   ```

2. **Make deployment script executable**:
   ```bash
   chmod +x deploy_to_linux.sh
   ```

3. **Run deployment script**:
   ```bash
   sudo ./deploy_to_linux.sh your-domain.com admin@example.com
   ```

   The script will:
   - Install required packages (Python, PostgreSQL, Nginx, Certbot)
   - Create application user and directory
   - Setup PostgreSQL database with secure credentials
   - Configure Python virtual environment
   - Setup Gunicorn WSGI server
   - Configure Nginx as reverse proxy
   - Obtain SSL certificate from Let's Encrypt
   - Create systemd service for automatic startup
   - Start all services

4. **Copy application files** (when prompted):
   ```bash
   cp app.py /opt/ema/
   cp models.py /opt/ema/
   cp requirements.txt /opt/ema/
   cp -r routes /opt/ema/
   cp -r admin /opt/ema/
   cp -r templates /opt/ema/
   cp update_manager.py /opt/ema/
   cp git_config.json /opt/ema/
   ```

5. **Configure environment**:
   ```bash
   sudo nano /opt/ema/.env
   ```
   Update the `.env` file with:
   - Strong `SECRET_KEY`
   - New admin credentials (generate password hash)
   - Database configuration (auto-filled)
   - Git repository settings

## 🔑 Admin Credentials

### Generating Secure Password Hash

```bash
python3 -c "from werkzeug.security import generate_password_hash; print(generate_password_hash('your-secure-password'))"
```

Copy the hash to your `.env` file as `ADMIN_PASSWORD_HASH`.

### Changing Admin Password

The only way to change the admin password on deployed servers is to:

1. Generate new password hash:
   ```bash
   python3 -c "from werkzeug.security import generate_password_hash; print(generate_password_hash('new-password'))"
   ```

2. Update `.env`:
   ```bash
   sudo nano /opt/ema/.env
   ADMIN_PASSWORD_HASH=<paste-new-hash>
   ```

3. Restart service:
   ```bash
   sudo systemctl restart ema
   ```

## 📊 Admin Panel Features

### Dashboard
- **Total Users**: Count of registered users
- **Online Users**: Currently active users
- **Total Messages**: All messages in system
- **Undelivered Messages**: Messages waiting for offline users
- **Recent Messages**: Latest 10 messages with sender/receiver info
- **Live Stats**: Auto-refreshing every 5 seconds

### Users Management
- View all registered users with pagination
- Search users by username
- View user details (ID, friend code, online status)
- View registration date and last seen
- Delete users (cascades to delete messages, requests, friendships)
- Search functionality

### Messages Monitoring
- View all messages with pagination
- Filter by delivery status (delivered/pending)
- Show message preview (first 50 characters)
- Monitor message flow in real-time
- Track offline message caching

### Friend Requests
- View all friend requests
- Filter by status (pending/accepted/rejected)
- View request timestamps
- Delete requests as needed
- Manage friendship network

## 🛠️ Useful Server Commands

```bash
# View service status
sudo systemctl status ema

# View real-time logs
sudo journalctl -u ema -f

# Restart service
sudo systemctl restart ema

# Stop service
sudo systemctl stop ema

# Start service
sudo systemctl start ema

# View configuration
grep -v '#' /opt/ema/.env

# Database access
sudo -u postgres psql -d ema_db

# Check Nginx status
sudo systemctl status nginx

# View Nginx logs
tail -f /var/log/nginx/ema_access.log
tail -f /var/log/nginx/ema_error.log

# SSL certificate renewal (automatic, but can force)
sudo certbot renew --force-renewal
```

## 🔐 SSL/HTTPS Setup

### Automatic (via Let's Encrypt)
The deployment script handles this automatically. Certificates are renewed automatically every 60+ days.

### Manual Setup
```bash
sudo certbot --nginx -d your-domain.com
```

### Check Certificate Status
```bash
sudo certbot certificates
```

### Manual Renewal
```bash
sudo certbot renew --force-renewal
```

## 📋 Backup & Maintenance

### Database Backup
```bash
# Backup PostgreSQL
sudo -u postgres pg_dump ema_db > ema_backup_$(date +%Y%m%d).sql

# Restore from backup
sudo -u postgres psql ema_db < ema_backup_20240101.sql
```

### Application Backup
```bash
sudo tar -czf ema_backup_$(date +%Y%m%d).tar.gz /opt/ema/
```

## 🚨 Security Checklist for Production

- [ ] Change admin password from default (admin123)
- [ ] Use strong SECRET_KEY (generated automatically but verify)
- [ ] Enable SESSION_COOKIE_SECURE=True in .env
- [ ] Configure proper database backups
- [ ] Review firewall rules (only allow 80, 443, 22)
- [ ] Configure log rotation
- [ ] Set up email alerts for certificate renewal
- [ ] Monitor disk space for logs
- [ ] Keep system packages updated
- [ ] Review Nginx logs regularly
- [ ] Test database recovery procedures

## 🐛 Troubleshooting

### Service won't start
```bash
sudo journalctl -u ema -n 50  # View last 50 lines of logs
```

### Admin panel not loading
1. Check service status: `sudo systemctl status ema`
2. Check Nginx: `sudo systemctl status nginx`
3. View logs: `sudo journalctl -u ema -f`

### Database connection errors
1. Check PostgreSQL: `sudo systemctl status postgresql`
2. Verify .env DATABASE_URL
3. Test connection: `sudo -u postgres psql -d ema_db`

### SSL certificate issues
1. Check renewal: `sudo certbot certificates`
2. View logs: `sudo certbot logs`
3. Force renewal: `sudo certbot renew --force-renewal`

### Port already in use
- Check what's using port 5000: `lsof -i :5000`
- The Gunicorn service should be the only one using it

## 📞 Support

For issues and questions:
1. Check service logs: `sudo journalctl -u ema -f`
2. Review configuration: `grep -v '#' /opt/ema/.env`
3. Test database connection
4. Verify Nginx configuration: `sudo nginx -t`

## 🔄 Updating Admin Panel Code

1. Pull latest changes to your local repo
2. Copy updated files to server:
   ```bash
   scp admin_routes.py user@server:/opt/ema/admin/
   scp templates/*.html user@server:/opt/ema/templates/
   ```
3. Restart service: `sudo systemctl restart ema`

## Statistics & Monitoring

Access real-time server statistics via:
- Admin Dashboard: `/admin/`
- API Endpoint: `/admin/api/stats` (requires admin login)
- Health Check: `/health` (public)

The dashboard automatically refreshes statistics every 5 seconds for real-time monitoring.
