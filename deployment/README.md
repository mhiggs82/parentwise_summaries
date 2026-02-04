# ParentWise Deployment Guide for Hostinger VPS

## Prerequisites

- Hostinger VPS with Ubuntu 22.04 or Debian 12
- SSH access to your VPS
- Domain pointed to your VPS IP address

## Quick Start

### 1. Upload Files to VPS

```bash
# On your local machine, zip the deployment folder
cd /path/to/parentwise
zip -r parentwise-deploy.zip deployment/ Docs/ output_pdfs/ backend/server.py frontend/

# Upload to VPS using scp
scp parentwise-deploy.zip root@your-vps-ip:/root/
```

### 2. SSH into VPS and Extract

```bash
ssh root@your-vps-ip
cd /root
unzip parentwise-deploy.zip
cd deployment
```

### 3. Run Deployment Script

```bash
chmod +x deploy.sh setup-ssl.sh
./deploy.sh
```

### 4. Set Up SSL (Optional but Recommended)

```bash
./setup-ssl.sh summaries.getparentwise.com
```

Then edit `nginx/nginx.conf` to enable the HTTPS server block.

## Manual Deployment

If you prefer manual control:

```bash
# Install Docker
curl -fsSL https://get.docker.com | sh

# Start services
export DOMAIN_URL=https://your-domain.com
docker-compose up -d

# Check status
docker-compose ps
docker-compose logs -f
```

## File Structure

```
deployment/
├── docker-compose.yml      # Main orchestration file
├── backend/
│   ├── Dockerfile          # Backend container
│   ├── requirements.txt    # Python dependencies
│   └── .env.production     # Backend environment
├── frontend/
│   ├── Dockerfile          # Frontend container
│   └── nginx.conf          # Frontend nginx config
├── nginx/
│   ├── nginx.conf          # Main reverse proxy config
│   └── ssl/                # SSL certificates (created during setup)
├── deploy.sh               # Automated deployment script
├── setup-ssl.sh            # SSL certificate setup
└── README.md               # This file
```

## Common Commands

```bash
# View logs
docker-compose logs -f
docker-compose logs -f backend
docker-compose logs -f frontend

# Restart services
docker-compose restart

# Stop all services
docker-compose down

# Rebuild after code changes
docker-compose build --no-cache
docker-compose up -d

# Check container status
docker-compose ps

# Access MongoDB shell
docker exec -it parentwise-mongodb mongosh
```

## Troubleshooting

### 502 Bad Gateway
- Check if backend is running: `docker-compose logs backend`
- Verify MongoDB connection: `docker-compose logs mongodb`

### Frontend not loading
- Check frontend logs: `docker-compose logs frontend`
- Verify REACT_APP_BACKEND_URL in docker-compose.yml

### SSL Issues
- Ensure domain DNS is pointing to VPS IP
- Check certbot logs: `/var/log/letsencrypt/`
- Verify certificates exist: `ls nginx/ssl/`

## Updating the Application

```bash
# Pull latest code (if using git)
git pull

# Rebuild containers
docker-compose build --no-cache
docker-compose up -d
```

## Backup

```bash
# Backup MongoDB data
docker exec parentwise-mongodb mongodump --out /data/backup
docker cp parentwise-mongodb:/data/backup ./mongodb-backup

# Backup PDFs
cp -r output_pdfs/ ./pdfs-backup/
```

## Support

For issues, check:
1. Docker logs: `docker-compose logs`
2. Nginx logs: `docker exec parentwise-nginx cat /var/log/nginx/error.log`
3. System resources: `htop` or `free -m`
