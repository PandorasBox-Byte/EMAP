# EMAP SERVER - Complete Deployment Plan

**Date**: March 1, 2026  
**Server**: 192.168.0.247  
**User**: panchein  
**Root Password**: Milo2022!  
**SSH Passphrase**: Makenzi2003!  
**GitHub Repo**: https://github.com/PandorasBox-Byte/EMAP.git

---

## Overview

This document provides a complete step-by-step deployment plan for the EMA (Encrypted Messaging Application) server on Ubuntu Linux. Follow each section sequentially.

---

## PHASE 1: Initial Access & System Setup

### Step 1.1: SSH Into Server

```bash
ssh panchein@192.168.0.247
```

**When prompted**: Enter SSH passphrase: `Makenzi2003!`

**Expected**: You see `panchein@...$ ` prompt

---

### Step 1.2: Switch to Root User

```bash
sudo -i
```

**When prompted**: Enter root password: `Milo2022!`

**Expected**: You see `root@...# ` prompt

---

### Step 1.3: Update System Packages

```bash
apt-get update
apt-get upgrade -y
```

**What it does**: Updates all system packages to latest versions  
**Duration**: 1-2 minutes  
**Expected**: Ends with success messages

---

## PHASE 2: Install Dependencies

### Step 2.1: Install All Required Packages

```bash
apt-get install -y python3 python3-pip python3-venv postgresql postgresql-contrib nginx certbot python3-certbot-nginx git curl wget
```

**Packages being installed**:
- `python3` - Python interpreter
- `python3-pip` - Python package manager
- `python3-venv` - Virtual environments
- `postgresql` - Database server
- `nginx` - Web server
- `certbot` - SSL certificate management
- `git` - Version control
- `curl wget` - Download tools

**Duration**: 2-3 minutes  
**Expected**: All packages installed successfully

---

## PHASE 3: Create Application User & Directory

### Step 3.1: Create EMA User

```bash
useradd -m -s /bin/bash ema
```

**What it does**: Creates a new user called `ema` for running the application  
**Why**: Better security than running as root

---

### Step 3.2: Create Application Directory

```bash
mkdir -p /opt/ema-server
chown -R ema:ema /opt/ema-server
```

**What it does**: Creates `/opt/ema-server` directory and gives `ema` user ownership

---

## PHASE 4: Clone Repository & Setup Python Environment

### Step 4.1: Switch to EMA User

```bash
su - ema
```

**Expected**: You see `ema@...$ ` prompt

---

### Step 4.2: Clone Repository (Server Directory Only)

```bash
cd ~
git init ema-server
cd ema-server
git remote add origin https://github.com/PandorasBox-Byte/EMAP.git
git config core.sparseCheckout true
echo "Server/" >> .git/info/sparse-checkout
git pull origin main
```

**What it does**: 
- Uses sparse-checkout to clone only the `Server/` directory
- Downloads from your GitHub repo
- Only pulls necessary files (faster, smaller)

**Expected**: Files downloaded to `/home/ema/ema-server`

---

### Step 4.3: Extract Server Directory Contents

```bash
mv Server/* .
rmdir Server 2>/dev/null || true
```

**What it does**: Moves all Server contents to root of ema-server directory

**Expected**: App files are now in current directory

---

### Step 4.4: Create Python Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

**Expected**: Your prompt shows `(venv) ema@...$ `

---

### Step 4.5: Install Python Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**What it does**: Installs all Python packages needed (Flask, SQLAlchemy, etc.)  
**Duration**: 1-2 minutes

---

## PHASE 5: Configuration

### Step 5.1: Create Environment File

```bash
cp .env.example .env
```

---

### Step 5.2: Edit Environment Configuration

```bash
nano .env
```

**Edit these values**:

```
FLASK_ENV=production
DEBUG=False
SECRET_KEY=YOUR_SECRET_KEY_HERE
DATABASE_URL=postgresql://ema_user:YOUR_DB_PASSWORD@localhost/ema_db
ADMIN_USERNAME=admin
ADMIN_PASSWORD_HASH=YOUR_PASSWORD_HASH_HERE
SESSION_COOKIE_SECURE=True
AUTO_UPDATE_ENABLED=True
GIT_REPOSITORY_URL=https://github.com/PandorasBox-Byte/EMAP.git
GIT_BRANCH=main
```

**To edit in nano**:
- Use arrow keys to navigate
- Delete text with backspace
- Save: `Ctrl+X` → `Y` → `Enter`

---

### Step 5.3: Generate SECRET_KEY

In a new terminal window (keep nano open):

```bash
openssl rand -base64 32
```

**Copy the output** and put it in `.env` next to `SECRET_KEY=`

---

### Step 5.4: Generate ADMIN_PASSWORD_HASH

With Python activated:

```bash
python3 << 'EOF'
from werkzeug.security import generate_password_hash
print(generate_password_hash("your-secure-admin-password"))
EOF
```

**Copy the hash output** and put it in `.env` next to `ADMIN_PASSWORD_HASH=`

---

### Step 5.5: Generate Strong Database Password

```bash
openssl rand -base64 32
```

**Copy the output** and use it as `YOUR_DB_PASSWORD` in `.env`

---

### Step 5.6: Save .env File

In nano, after editing all values:

```
Ctrl+X → Y → Enter
```

---

## PHASE 6: PostgreSQL Database Setup

### Step 6.1: Exit EMA User & Switch to Root

```bash
exit
exit
sudo -i
```

---

### Step 6.2: Create Database & User

Replace `your-strong-db-password` with the password you generated:

```bash
sudo -u postgres psql << 'EOF'
CREATE DATABASE ema_db;
CREATE USER ema_user WITH PASSWORD 'your-strong-db-password';
ALTER ROLE ema_user SET client_encoding TO 'utf8';
ALTER ROLE ema_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE ema_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE ema_db TO ema_user;
\q
EOF
```

**Expected**: Database created successfully

---

### Step 6.3: Initialize Database Tables

```bash
su - ema
cd ~/ema-server
source venv/bin/activate
python3 << 'EOF'
from app import db, app
with app.app_context():
    db.create_all()
    print('✅ Database initialized')
EOF
```

**Expected**: `✅ Database initialized` message

---

## PHASE 7: Systemd Service Setup

### Step 7.1: Exit EMA User

```bash
exit
exit
sudo -i
```

---

### Step 7.2: Create Systemd Service File

```bash
cat > /etc/systemd/system/ema.service << 'EOF'
[Unit]
Description=EMA Encrypted Messaging Server
After=network.target postgresql.service
Wants=postgresql.service

[Service]
Type=simple
User=ema
WorkingDirectory=/home/ema/ema-server
Environment="PATH=/home/ema/ema-server/venv/bin"
Environment="PYTHONUNBUFFERED=1"
ExecStart=/home/ema/ema-server/venv/bin/python3 /home/ema/ema-server/app.py

Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF
```

---

### Step 7.3: Enable & Start Service

```bash
systemctl daemon-reload
systemctl enable ema
systemctl start ema
systemctl status ema
```

**Expected**: Status shows `active (running)`

---

## PHASE 8: Nginx Configuration

### Step 8.1: Create Nginx Configuration

Replace `192.168.0.247` with your server's IP or domain:

```bash
cat > /etc/nginx/sites-available/ema << 'EOF'
upstream gunicorn_app {
    server 127.0.0.1:5000;
}

server {
    listen 80;
    server_name 192.168.0.247;
    client_max_body_size 10M;

    location / {
        proxy_pass http://gunicorn_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF
```

---

### Step 8.2: Enable Nginx Site

```bash
ln -sf /etc/nginx/sites-available/ema /etc/nginx/sites-enabled/ema
rm -f /etc/nginx/sites-enabled/default
```

---

### Step 8.3: Test & Restart Nginx

```bash
nginx -t
systemctl restart nginx
systemctl status nginx
```

**Expected**: Nginx shows `active (running)`

---

## PHASE 9: Verification & Testing

### Step 9.1: Check Application is Running

```bash
curl http://localhost:5000/health
```

**Expected**: `{"status":"healthy"}`

---

### Step 9.2: Check All Services

```bash
systemctl status ema postgresql nginx
```

**Expected**: All three show `active (running)`

---

### Step 9.3: View Application Logs

```bash
journalctl -u ema -n 20
```

**Expected**: Recent log entries, no critical errors

---

## PHASE 10: Access Admin Panel

### Step 10.1: Open Browser

Go to: `http://192.168.0.247/admin/`

---

### Step 10.2: Login

- **Username**: `admin`
- **Password**: (whatever you set in ADMIN_PASSWORD_HASH - the plain password used to generate it)

---

### Step 10.3: Verify Dashboard

You should see:
- ✅ Total Users counter
- ✅ Online Users counter
- ✅ Total Messages counter
- ✅ Undelivered Messages counter
- ✅ User Management page
- ✅ Message Monitoring page
- ✅ Friend Requests page

---

## PHASE 11: Post-Deployment Setup

### Step 11.1: Create Logs Directory

```bash
su - ema
mkdir -p ~/ema-server/logs
exit
```

---

### Step 11.2: Configure Log Rotation (Optional)

```bash
cat > /etc/logrotate.d/ema << 'EOF'
/home/ema/ema-server/logs/*.log {
    daily
    rotate 7
    compress
    delaycompress
    notifempty
    create 0640 ema ema
}
EOF
```

---

### Step 11.3: Create Backup Script (Optional)

```bash
cat > /home/ema/ema-server/backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/home/ema/ema-server/backups"
mkdir -p "$BACKUP_DIR"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
sudo -u postgres pg_dump ema_db > "$BACKUP_DIR/ema_db_$TIMESTAMP.sql"
tar -czf "$BACKUP_DIR/ema_server_$TIMESTAMP.tar.gz" /home/ema/ema-server --exclude='venv' --exclude='.git'
echo "Backup completed: $TIMESTAMP"
EOF
chmod +x /home/ema/ema-server/backup.sh
```

---

## PHASE 12: SSL/HTTPS Setup (Optional but Recommended)

### Step 12.1: Obtain SSL Certificate

```bash
certbot --nginx -d your-domain.com
```

If using IP address instead of domain, skip this step.

---

### Step 12.2: Automatic Renewal

```bash
systemctl enable certbot.timer
```

---

## Troubleshooting Guide

### Issue: Service won't start

**Check logs**:
```bash
journalctl -u ema -n 50
```

**Common fixes**:
- Check `.env` file has correct values
- Verify DATABASE_URL is correct
- Confirm database user has permissions

---

### Issue: Can't access admin panel

**Check Nginx**:
```bash
systemctl status nginx
nginx -t
```

**Check app is listening**:
```bash
netstat -tuln | grep 5000
```

---

### Issue: Database connection error

**Check PostgreSQL**:
```bash
systemctl status postgresql
sudo -u postgres psql -d ema_db -c "SELECT 1"
```

---

### Issue: Admin panel shows 500 error

**Check application logs**:
```bash
journalctl -u ema -f
```

Look for the actual error message.

---

## Useful Commands

### View Service Status
```bash
systemctl status ema
```

### View Real-time Logs
```bash
journalctl -u ema -f
```

### Restart Service
```bash
systemctl restart ema
```

### View Environment Configuration
```bash
grep -v '#' /home/ema/ema-server/.env
```

### Check Database Connection
```bash
sudo -u postgres psql -d ema_db -c "\dt"
```

### Stop Service
```bash
systemctl stop ema
```

### Start Service
```bash
systemctl start ema
```

### View Nginx Access Logs
```bash
tail -f /var/log/nginx/access.log
```

### View Nginx Error Logs
```bash
tail -f /var/log/nginx/error.log
```

---

## Access Points After Deployment

| Service | URL | Credentials |
|---------|-----|-------------|
| **Admin Panel** | http://192.168.0.247/admin/ | admin / (your password) |
| **API Health** | http://192.168.0.247/health | Public (no auth needed) |
| **API Base** | http://192.168.0.247/ | Device authentication required |

---

## Security Checklist

After deployment, verify:

- [ ] Admin password is securely stored in .env
- [ ] Database password is strong (auto-generated)
- [ ] SECRET_KEY is random (auto-generated)
- [ ] PostgreSQL is only accessible locally
- [ ] Nginx is properly proxying requests
- [ ] Service auto-restarts on failure
- [ ] Logs are being recorded
- [ ] Database backups are working

---

## Next Steps

1. ✅ Follow all phases sequentially
2. ✅ Test admin panel access
3. ✅ Verify all services are running
4. ✅ Review logs for any errors
5. ✅ Set up automated backups (optional)
6. ✅ Configure HTTPS with SSL (optional)
7. ✅ Monitor server performance

---

## Support Information

**If you encounter issues**:

1. Check the Troubleshooting Guide above
2. View application logs: `journalctl -u ema -f`
3. Verify all services are running: `systemctl status ema postgresql nginx`
4. Review .env configuration: `grep -v '#' /home/ema/ema-server/.env`

---

**Good luck with your deployment! 🚀**
