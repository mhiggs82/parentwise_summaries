#!/bin/bash

# ParentWise Book Summaries - Deployment Script for Hostinger VPS
# Run this script on your Hostinger VPS after uploading the files

set -e

echo "========================================"
echo "ParentWise Deployment Script"
echo "========================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}Please run as root (sudo ./deploy.sh)${NC}"
    exit 1
fi

# Get domain from user
read -p "Enter your domain (e.g., summaries.getparentwise.com): " DOMAIN
export DOMAIN_URL="https://${DOMAIN}"

echo -e "${YELLOW}Step 1: Installing Docker...${NC}"
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com | sh
    systemctl enable docker
    systemctl start docker
    echo -e "${GREEN}Docker installed successfully${NC}"
else
    echo -e "${GREEN}Docker already installed${NC}"
fi

echo -e "${YELLOW}Step 2: Installing Docker Compose...${NC}"
if ! command -v docker-compose &> /dev/null; then
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
    echo -e "${GREEN}Docker Compose installed successfully${NC}"
else
    echo -e "${GREEN}Docker Compose already installed${NC}"
fi

echo -e "${YELLOW}Step 3: Creating SSL directory...${NC}"
mkdir -p nginx/ssl
echo -e "${GREEN}SSL directory created${NC}"

echo -e "${YELLOW}Step 4: Building and starting containers...${NC}"
docker-compose down 2>/dev/null || true
docker-compose build --no-cache
docker-compose up -d

echo -e "${YELLOW}Step 5: Waiting for services to start...${NC}"
sleep 10

echo -e "${YELLOW}Step 6: Checking service status...${NC}"
docker-compose ps

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Deployment Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Your app is now running at: http://${DOMAIN}"
echo ""
echo "Next steps:"
echo "1. Point your domain DNS to this server's IP address"
echo "2. For SSL, run: ./setup-ssl.sh ${DOMAIN}"
echo "3. Check logs: docker-compose logs -f"
echo ""
