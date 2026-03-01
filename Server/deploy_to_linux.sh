#!/bin/bash
set -e

# EMA Server Deployment Script for Ubuntu 20.04+
# This script sets up the server with HTTPS (Let's Encrypt), PostgreSQL, and Gunicorn

echo "🚀 EMA Server Installation Script"
echo "=================================="

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "❌ This script must be run as root (use: sudo ./deploy_to_linux.sh)"
    exit 1
fi

# Configuration
DOMAIN="${1:-localhost}"
EMAIL="${2:-admin@example.com}"
APP_USER="ema"
APP_DIR="/opt/ema"
DB_NAME="ema_db"
DB_USER="ema_user"
DB_PASSWORD=$(openssl rand -base64 32)

echo "📋 Configuration:"
echo "  Domain: $DOMAIN"
echo "  Admin Email: $EMAIL"
echo "  App Directory: $APP_DIR"
echo "  Database: $DB_NAME"
echo ""

# 1. Update system
echo "📦 Updating system packages..."
apt-get update
apt-get upgrade -y

# 2. Install dependencies
echo "📦 Installing dependencies..."
apt-get install -y \
    python3-pip \
    python3-venv \
    postgresql \
    postgresql-contrib \
    nginx \
    certbot \
    python3-certbot-nginx \
    git \
    curl \
    wget

# 3. Create application user
echo "👤 Creating application user..."
useradd -m -s /bin/bash $APP_USER || true

# 4. Create application directory
echo "📁 Setting up application directory..."
mkdir -p $APP_DIR
chown -R $APP_USER:$APP_USER $APP_DIR

# 5. Setup PostgreSQL database
echo "🗄️  Setting up PostgreSQL database..."
sudo -u postgres psql << EOF
CREATE DATABASE $DB_NAME;
CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';
ALTER ROLE $DB_USER SET client_encoding TO 'utf8';
ALTER ROLE $DB_USER SET default_transaction_isolation TO 'read committed';
ALTER ROLE $DB_USER SET default_transaction_deferrable TO on;
ALTER ROLE $DB_USER SET default_transaction_deferrable TO on;
ALTER ROLE $DB_USER SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;
EOF

# 6. Create Python virtual environment
echo "🐍 Setting up Python virtual environment..."
sudo -u $APP_USER python3 -m venv $APP_DIR/venv

# 7. Copy application code (you'll do this manually)
echo "⚠️  Manual step: Copy your application code to $APP_DIR"
echo "   Files to copy:"
echo "   - app.py"
echo "   - models.py"
echo "   - requirements.txt"
echo "   - routes/ (directory)"
echo "   - admin/ (directory)"
echo "   - templates/ (directory)"
echo "   - update_manager.py"
echo "   - git_config.json"
echo ""
echo "Place files in: $APP_DIR"

# Wait for user to confirm
echo "Press Enter after copying the application files..."
read

# 8. Install Python dependencies
echo "📚 Installing Python dependencies..."
sudo -u $APP_USER $APP_DIR/venv/bin/pip install --upgrade pip
sudo -u $APP_USER $APP_DIR/venv/bin/pip install -r $APP_DIR/requirements.txt

# 9. Create .env file
echo "⚙️  Creating .env configuration file..."
cat > $APP_DIR/.env << EOF
FLASK_ENV=production
DEBUG=False
SECRET_KEY=$(openssl rand -base64 32)
DATABASE_URL=postgresql://$DB_USER:$DB_PASSWORD@localhost/$DB_NAME
SESSION_COOKIE_SECURE=True
ADMIN_USERNAME=admin
ADMIN_PASSWORD_HASH=\$(python3 -c "from werkzeug.security import generate_password_hash; print(generate_password_hash('admin123'))")
EOF

chmod 600 $APP_DIR/.env
chown $APP_USER:$APP_USER $APP_DIR/.env

# 10. Create systemd service file
echo "⚙️  Creating systemd service..."
cat > /etc/systemd/system/ema.service << EOF
[Unit]
Description=EMA Messaging Server
After=network.target postgresql.service

[Service]
Type=notify
User=$APP_USER
WorkingDirectory=$APP_DIR
Environment="PATH=$APP_DIR/venv/bin"
ExecStart=$APP_DIR/venv/bin/gunicorn --workers 4 --worker-class sync --bind 127.0.0.1:5000 --access-logfile - --error-logfile - app:app

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload

# 11. Create Nginx configuration
echo "🌐 Configuring Nginx..."
cat > /etc/nginx/sites-available/ema << 'NGINX_EOF'
upstream gunicorn_app {
    server 127.0.0.1:5000;
}

server {
    listen 80;
    server_name DOMAIN_PLACEHOLDER;
    client_max_body_size 10M;

    location / {
        proxy_pass http://gunicorn_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
    }

    location /static/ {
        alias $APP_DIR/static/;
    }
}
NGINX_EOF

# Replace domain placeholder
sed -i "s|DOMAIN_PLACEHOLDER|$DOMAIN|g" /etc/nginx/sites-available/ema
sed -i "s|\$APP_DIR|$APP_DIR|g" /etc/nginx/sites-available/ema

# Enable Nginx site
ln -sf /etc/nginx/sites-available/ema /etc/nginx/sites-enabled/ema
rm -f /etc/nginx/sites-enabled/default

# Test Nginx configuration
nginx -t

# 12. Setup SSL with Let's Encrypt
echo "🔒 Setting up SSL with Let's Encrypt..."
if [ "$DOMAIN" != "localhost" ]; then
    certbot --nginx -d $DOMAIN --email $EMAIL --agree-tos --non-interactive --redirect || true
else
    echo "⚠️  Skipping SSL setup for localhost. Use certbot manually for real domains:"
    echo "   sudo certbot --nginx -d your-domain.com"
fi

# 13. Start services
echo "🚀 Starting services..."
systemctl enable postgresql
systemctl restart postgresql
systemctl enable nginx
systemctl restart nginx
systemctl enable ema
systemctl start ema

# 14. Create firewall rules (if ufw is enabled)
if command -v ufw &> /dev/null; then
    echo "🔥 Configuring firewall..."
    ufw allow 22/tcp
    ufw allow 80/tcp
    ufw allow 443/tcp
fi

# 15. Print success message
echo ""
echo "✅ Installation Complete!"
echo "=================================="
echo "🎉 Your EMA Server is now running!"
echo ""
echo "📊 Admin Panel Information:"
echo "   Default Username: admin"
echo "   Default Password: admin123"
echo "   ⚠️  CHANGE THIS IMMEDIATELY!"
echo ""
if [ "$DOMAIN" != "localhost" ]; then
    echo "🌐 Access admin panel: https://$DOMAIN/admin/"
else
    echo "🌐 Access admin panel: http://localhost:5000/admin/"
fi
echo ""
echo "📋 Useful commands:"
echo "   View logs:        sudo journalctl -u ema -f"
echo "   Restart service:  sudo systemctl restart ema"
echo "   Check status:     sudo systemctl status ema"
echo "   View env:         grep -v '#' $APP_DIR/.env"
echo ""
echo "📚 Configuration file: $APP_DIR/.env"
echo "📚 Database info: $DB_NAME / $DB_USER"
echo ""
echo "📝 Security Checklist:"
echo "   ☐ Change admin password in admin panel"
echo "   ☐ Configure proper database backup strategy"
echo "   ☐ Review Nginx logs: /var/log/nginx/"
echo "   ☐ Setup email notifications for certificate renewal"
echo "   ☐ Configure firewall rules for your environment"
