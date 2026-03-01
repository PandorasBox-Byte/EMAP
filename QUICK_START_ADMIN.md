# Quick Start Guide - EMA Admin Panel

## 🚀 Start in 3 Minutes (Development)

```bash
cd "/Users/adammurdoch/Desktop/Encrypte Messaging App (EMA)/Server"

# Setup
./setup_dev.sh
source venv/bin/activate

# Run
python app.py

# Access
Open browser: http://localhost:5000/admin/
Login: admin / admin123
```

---

## 🌐 Deploy to Linux in 10 Minutes

### Prerequisites
- Ubuntu 20.04+ server
- Domain name (for HTTPS)
- Root/sudo access
- SSH connection to server

### Deployment
```bash
# On your local machine
cd Server

# Transfer files to server
scp deploy_to_linux.sh admin_routes.py admin/__init__.py app.py requirements.txt user@server:/tmp/

# On the server
cd /tmp
sudo chmod +x deploy_to_linux.sh
sudo ./deploy_to_linux.sh your-domain.com admin@example.com

# When prompted, copy these files to /opt/ema/:
# - app.py
# - models.py
# - requirements.txt
# - routes/
# - admin/
# - templates/
# - update_manager.py
# - git_config.json

# After deployment, secure your admin password:
sudo nano /opt/ema/.env
# Edit ADMIN_PASSWORD_HASH (generate new hash first)
sudo systemctl restart ema

# Access
https://your-domain.com/admin/
```

---

## 📁 File Structure

```
Server/
├── app.py                    ← Main Flask app (UPDATED with admin)
├── models.py                 ← Database models
├── requirements.txt          ← Dependencies (UPDATED)
├── routes/                   ← API routes
│   ├── auth_routes.py
│   ├── message_routes.py
│   └── friend_routes.py
├── admin/                    ← NEW: Admin panel
│   ├── __init__.py
│   └── admin_routes.py
├── templates/                ← NEW: HTML templates
│   ├── admin_login.html
│   ├── admin_dashboard.html
│   ├── admin_users.html
│   ├── admin_messages.html
│   └── admin_requests.html
├── static/                   ← NEW: Static files (CSS, JS)
│   ├── css/
│   └── js/
├── deploy_to_linux.sh       ← NEW: Auto-deployment script
├── setup_dev.sh             ← NEW: Dev setup script
├── ema.service              ← NEW: Systemd service
├── nginx_config.conf        ← NEW: Nginx HTTPS config
├── .env.example             ← UPDATED with admin config
├── README.md                ← UPDATED project docs
├── ADMIN_PANEL_GUIDE.md     ← NEW: Complete guide
└── DEPLOYMENT_CHECKLIST.md  ← NEW: Deploy checklist
```

---

## 🔑 Default Credentials

**Username**: `admin`  
**Password**: `admin123`

⚠️ **CHANGE IMMEDIATELY IN PRODUCTION**

---

## 🎯 Admin Panel URLs

| Page | URL | Purpose |
|------|-----|---------|
| Login | `/admin/login` | Admin authentication |
| Dashboard | `/admin/` | Real-time statistics |
| Users | `/admin/users` | User management |
| Messages | `/admin/messages` | Message monitoring |
| Requests | `/admin/requests` | Friend request management |

---

## 🛠️ Common Tasks

### View Logs
```bash
sudo journalctl -u ema -f
```

### Restart Service
```bash
sudo systemctl restart ema
```

### Change Admin Password
```bash
# Generate hash
python3 -c "from werkzeug.security import generate_password_hash; print(generate_password_hash('new-password'))"

# Update
sudo nano /opt/ema/.env
# Paste hash in ADMIN_PASSWORD_HASH

# Restart
sudo systemctl restart ema
```

### Backup Database
```bash
sudo -u postgres pg_dump ema_db > backup_$(date +%Y%m%d).sql
```

### Check SSL Certificate
```bash
sudo certbot certificates
```

---

## 🔒 Security Features

✅ **Password Hashing** - Bcrypt encryption  
✅ **HTTPS/TLS** - All connections encrypted  
✅ **Session Security** - HTTP-only cookies, CSRF protection  
✅ **Rate Limiting** - Brute force protection  
✅ **Security Headers** - HSTS, CSP, X-Frame-Options  
✅ **Admin Isolation** - Separate auth from API  
✅ **Auto-Renewal** - Let's Encrypt certificates auto-renew  

---

## 📊 Features

### Dashboard
- Total users
- Online users
- Total messages
- Undelivered messages
- Recent messages list
- Auto-refresh (5 sec)

### User Management
- View all users
- Search by username
- Pagination (20/page)
- Delete users
- View status & dates

### Message Monitoring
- View all messages
- Filter by delivery status
- See message preview
- Pagination
- Real-time updates

### Friend Requests
- View all requests
- Filter by status
- Delete requests
- Manage friendships

---

## 🐛 Troubleshooting

### Service Not Running?
```bash
sudo systemctl status ema
sudo journalctl -u ema -n 50
```

### Can't Access Admin Panel?
```bash
# Check Nginx
sudo systemctl status nginx
sudo nginx -t

# Check app
netstat -tuln | grep 5000
```

### SSL Certificate Error?
```bash
sudo certbot certificates
sudo certbot renew --force-renewal
```

### Database Error?
```bash
sudo systemctl status postgresql
sudo -u postgres psql -d ema_db -c "SELECT 1"
```

---

## 📞 Documentation

1. **README.md** - Project overview
2. **ADMIN_PANEL_GUIDE.md** - Complete setup & usage
3. **DEPLOYMENT_CHECKLIST.md** - Deployment steps
4. **ADMIN_PANEL_SETUP_SUMMARY.md** - What was created

---

## ✨ You're All Set!

**Local Testing**: `python app.py` → http://localhost:5000/admin/  
**Production Deploy**: `sudo ./deploy_to_linux.sh domain.com email@example.com`

For detailed instructions, see `ADMIN_PANEL_GUIDE.md` 📚
