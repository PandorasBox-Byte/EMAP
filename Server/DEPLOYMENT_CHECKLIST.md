# EMA Admin Panel Deployment Checklist

Complete this checklist when deploying the admin panel to production.

## Pre-Deployment (Local Development)

- [ ] Test admin panel locally: `python app.py`
- [ ] Verify login works with credentials
- [ ] Test all dashboard features (users, messages, requests)
- [ ] Confirm navigation between pages
- [ ] Test search and filter functionality
- [ ] Verify statistics auto-refresh
- [ ] Test user deletion (confirm cascade delete)

## Server Preparation

- [ ] Ubuntu 20.04 or later installed
- [ ] Root or sudo access available
- [ ] Domain name registered and DNS configured
- [ ] Email address ready for SSL certificate
- [ ] SSH key setup for remote access
- [ ] Firewall rules prepared (80, 443, 22)

## Deployment Execution

- [ ] Make deployment script executable: `chmod +x deploy_to_linux.sh`
- [ ] Run deployment: `sudo ./deploy_to_linux.sh domain.com email@example.com`
- [ ] Copy application files when prompted:
  - [ ] app.py
  - [ ] models.py
  - [ ] requirements.txt
  - [ ] routes/ directory
  - [ ] admin/ directory
  - [ ] templates/ directory
  - [ ] update_manager.py
  - [ ] git_config.json

## Post-Deployment Configuration

- [ ] Update .env file: `sudo nano /opt/ema/.env`
  - [ ] Change SECRET_KEY
  - [ ] Generate new admin password hash
  - [ ] Update ADMIN_PASSWORD_HASH in .env
  - [ ] Configure DATABASE_URL if using PostgreSQL
  - [ ] Set SESSION_COOKIE_SECURE=True
  - [ ] Configure GIT_REPOSITORY_URL
- [ ] Restart service: `sudo systemctl restart ema`
- [ ] Verify service is running: `sudo systemctl status ema`

## SSL/HTTPS Verification

- [ ] SSL certificate obtained from Let's Encrypt
- [ ] Access admin panel via HTTPS: https://domain.com/admin/
- [ ] Verify certificate is valid (no browser warnings)
- [ ] Check certificate expiration: `sudo certbot certificates`
- [ ] Confirm automatic renewal is enabled
- [ ] Test HTTP → HTTPS redirect

## Security Hardening

- [ ] Change admin password from default (admin123)
  ```bash
  python3 -c "from werkzeug.security import generate_password_hash; print(generate_password_hash('your-strong-password'))"
  # Copy hash to .env ADMIN_PASSWORD_HASH
  ```
- [ ] Verify SESSION_COOKIE_SECURE=True
- [ ] Review security headers in Nginx config
- [ ] Disable admin panel HTTP (80) access
- [ ] Test rate limiting on admin panel
- [ ] Configure firewall to restrict admin access if needed
- [ ] Review /var/log/ema/ permissions
- [ ] Ensure database password is strong and rotated

## Nginx Configuration

- [ ] Nginx configuration applied: `/etc/nginx/sites-available/ema`
- [ ] Site symbolic link created: `/etc/nginx/sites-enabled/ema`
- [ ] Default site disabled: `rm /etc/nginx/sites-enabled/default`
- [ ] Nginx configuration tested: `sudo nginx -t`
- [ ] Nginx restarted: `sudo systemctl restart nginx`
- [ ] Access logs configured: `/var/log/nginx/ema_access.log`
- [ ] Error logs configured: `/var/log/nginx/ema_error.log`

## Database Setup

- [ ] PostgreSQL database created: `ema_db`
- [ ] Database user created with strong password
- [ ] Database permissions verified
- [ ] Database connection tested from app

## Systemd Service

- [ ] Service file created: `/etc/systemd/system/ema.service`
- [ ] Service enabled: `sudo systemctl enable ema`
- [ ] Service started: `sudo systemctl start ema`
- [ ] Service status verified: `sudo systemctl status ema`
- [ ] Auto-restart on reboot enabled
- [ ] Log directory created: `/var/log/ema/`
- [ ] Log directory permissions set correctly

## Testing

- [ ] Login with default credentials works
- [ ] Dashboard loads and shows statistics
- [ ] Statistics auto-refresh every 5 seconds
- [ ] User list loads with pagination
- [ ] User search functionality works
- [ ] Message list loads and filters work
- [ ] Friend request list works
- [ ] Delete user function works (with confirm)
- [ ] Logout function works
- [ ] Admin panel is HTTPS only

## Monitoring & Logging

- [ ] Service logs accessible: `sudo journalctl -u ema -f`
- [ ] Log rotation configured (optional)
- [ ] Access logs being recorded
- [ ] Error logs being recorded
- [ ] Health check endpoint working: `/health`
- [ ] Stats API accessible: `/admin/api/stats`

## Backup & Disaster Recovery

- [ ] Database backup created: 
  ```bash
  sudo -u postgres pg_dump ema_db > ema_backup_$(date +%Y%m%d).sql
  ```
- [ ] Full app backup created:
  ```bash
  sudo tar -czf ema_backup_$(date +%Y%m%d).tar.gz /opt/ema/
  ```
- [ ] Backup location documented
- [ ] Database recovery procedure tested
- [ ] Backup automation scheduled (cron job)

## Performance Tuning (Optional)

- [ ] Gunicorn workers set to 4 (or per CPU cores)
- [ ] Memory limits configured in systemd
- [ ] Database connection pooling configured
- [ ] Nginx worker processes tuned
- [ ] SSL session caching enabled

## Firewall Configuration

- [ ] Allow SSH (22) for remote access
  ```bash
  sudo ufw allow 22/tcp
  ```
- [ ] Allow HTTP (80) for Let's Encrypt renewal
  ```bash
  sudo ufw allow 80/tcp
  ```
- [ ] Allow HTTPS (443) for admin panel
  ```bash
  sudo ufw allow 443/tcp
  ```
- [ ] Deny all other ports
  ```bash
  sudo ufw default deny incoming
  ```
- [ ] Enable UFW
  ```bash
  sudo ufw enable
  ```

## Documentation & Handover

- [ ] Document admin login credentials (secure location)
- [ ] Document server IP and domain
- [ ] Document database credentials (secure location)
- [ ] Create runbook for common operations
- [ ] List emergency contacts
- [ ] Document rollback procedure
- [ ] Test disaster recovery procedure

## First 24 Hours Monitoring

- [ ] Monitor service logs for errors
- [ ] Check admin panel responsiveness
- [ ] Monitor database performance
- [ ] Watch for unusual traffic
- [ ] Check disk space usage
- [ ] Verify SSL certificate is working
- [ ] Confirm auto-update mechanism

## Post-Deployment Optimization

- [ ] Enable caching headers for static files
- [ ] Configure connection pooling
- [ ] Set up alert monitoring (optional)
- [ ] Create performance baseline
- [ ] Schedule regular security audits
- [ ] Plan for certificate renewal (auto handles)

## Security Audit

- [ ] No default passwords in use
- [ ] SSH key-based authentication only
- [ ] Database passwords strong and unique
- [ ] All logs properly permission-restricted
- [ ] No secrets in .env visible to users
- [ ] HTTPS enforced everywhere
- [ ] Admin panel not accessible via HTTP
- [ ] Rate limiting working on APIs
- [ ] CSRF tokens validated

## Notification Setup (Optional)

- [ ] SSL certificate renewal notifications
- [ ] Error log alerts
- [ ] Service restart alerts
- [ ] Disk space alerts
- [ ] Database backup completion alerts

## Final Verification

- [ ] Admin can login successfully
- [ ] All dashboard features functional
- [ ] Real-time stats updating
- [ ] User management working
- [ ] Message monitoring active
- [ ] Friend request management functional
- [ ] Server is responding to API requests
- [ ] HTTPS is enforced and working
- [ ] No console errors in browser
- [ ] Response times acceptable

---

## Sign-Off

- **Deployed By**: ________________________
- **Date**: ________________________
- **Server**: ________________________
- **Domain**: ________________________
- **Verified By**: ________________________
- **Date Verified**: ________________________

## Notes

```
[Add any deployment notes, issues encountered, and resolutions here]
```
