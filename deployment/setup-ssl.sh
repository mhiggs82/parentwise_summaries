#!/bin/bash

# SSL Setup Script using Let's Encrypt
# Usage: ./setup-ssl.sh your-domain.com

set -e

DOMAIN=$1

if [ -z "$DOMAIN" ]; then
    echo "Usage: ./setup-ssl.sh your-domain.com"
    exit 1
fi

echo "Setting up SSL for $DOMAIN..."

# Install certbot if not present
if ! command -v certbot &> /dev/null; then
    apt-get update
    apt-get install -y certbot
fi

# Stop nginx temporarily
docker-compose stop nginx

# Get certificate
certbot certonly --standalone -d $DOMAIN --non-interactive --agree-tos --email admin@$DOMAIN

# Copy certificates to nginx ssl directory
cp /etc/letsencrypt/live/$DOMAIN/fullchain.pem nginx/ssl/
cp /etc/letsencrypt/live/$DOMAIN/privkey.pem nginx/ssl/

# Update nginx.conf to enable HTTPS
echo "Enabling HTTPS in nginx configuration..."
echo "Please uncomment the HTTPS server block in nginx/nginx.conf"
echo "and comment out the HTTP redirect line"

# Restart nginx
docker-compose start nginx

echo ""
echo "SSL certificate installed successfully!"
echo "Don't forget to:"
echo "1. Edit nginx/nginx.conf to enable the HTTPS server block"
echo "2. Run: docker-compose restart nginx"
echo ""
echo "Certificate will auto-renew. To manually renew:"
echo "certbot renew && docker-compose restart nginx"
