#!/bin/bash

# Conservation Solutions Dashboard - Production Deployment Script
# Run with: chmod +x deploy.sh && ./deploy.sh

set -e

echo "🌿 Conservation Solutions Dashboard - Deployment Script"
echo "======================================================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create necessary directories
echo "📁 Creating deployment directories..."
mkdir -p deploy/ssl
mkdir -p backup

# Set up environment files if they don't exist
if [ ! -f backend/.env ]; then
    echo "⚙️ Setting up backend environment..."
    cat > backend/.env << EOL
MONGO_URL=mongodb://admin:conservation123@mongodb:27017/conservation_dashboard?authSource=admin
SECRET_KEY=$(openssl rand -hex 32)
CORS_ORIGINS=http://localhost:3000,http://localhost:80
EOL
fi

if [ ! -f frontend/.env ]; then
    echo "⚙️ Setting up frontend environment..."
    cat > frontend/.env << EOL
REACT_APP_BACKEND_URL=http://localhost:8001
REACT_APP_APP_NAME=Conservation Solutions Dashboard
EOL
fi

# Create Dockerfiles if they don't exist
if [ ! -f backend/Dockerfile ]; then
    echo "🐳 Creating backend Dockerfile..."
    cat > backend/Dockerfile << EOL
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8001

CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8001"]
EOL
fi

if [ ! -f frontend/Dockerfile ]; then
    echo "🐳 Creating frontend Dockerfile..."
    cat > frontend/Dockerfile << EOL
FROM node:18-alpine

WORKDIR /app

COPY package*.json yarn.lock ./
RUN yarn install

COPY . .

EXPOSE 3000

CMD ["yarn", "start"]
EOL
fi

# Create nginx configuration
echo "🌐 Setting up Nginx configuration..."
cat > deploy/nginx.conf << EOL
events {
    worker_connections 1024;
}

http {
    upstream backend {
        server backend:8001;
    }

    upstream frontend {
        server frontend:3000;
    }

    server {
        listen 80;
        server_name localhost;

        # Frontend routes
        location / {
            proxy_pass http://frontend;
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
            proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto \$scheme;
        }

        # Backend API routes
        location /api/ {
            proxy_pass http://backend/api/;
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
            proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto \$scheme;
        }

        # Health check
        location /health {
            access_log off;
            return 200 "healthy\n";
            add_header Content-Type text/plain;
        }
    }
}
EOL

# Build and start services
echo "🚀 Building and starting services..."
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d

# Wait for services to start
echo "⏳ Waiting for services to initialize..."
sleep 30

# Health check
echo "🏥 Performing health checks..."
if curl -f http://localhost:80/health > /dev/null 2>&1; then
    echo "✅ Nginx is healthy"
else
    echo "❌ Nginx health check failed"
fi

if curl -f http://localhost:8001/api/ > /dev/null 2>&1; then
    echo "✅ Backend is healthy"
else
    echo "❌ Backend health check failed"
fi

if curl -f http://localhost:3000 > /dev/null 2>&1; then
    echo "✅ Frontend is healthy"
else
    echo "❌ Frontend health check failed"
fi

echo ""
echo "🎉 Deployment Complete!"
echo "========================================"
echo "📱 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:8001/api"
echo "🌐 Nginx Proxy: http://localhost:80"
echo ""
echo "📋 Next Steps:"
echo "1. Upload your Excel data via the web interface"
echo "2. Configure SSL certificates for HTTPS"
echo "3. Set up domain name and DNS"
echo "4. Configure backups and monitoring"
echo ""
echo "🔧 Management Commands:"
echo "  View logs: docker-compose logs -f [service]"
echo "  Stop: docker-compose down"
echo "  Restart: docker-compose restart"
echo "  Backup: docker exec conservation-mongodb mongodump"
echo ""
echo "🛡️ Security Reminders:"
echo "⚠️  Change default passwords in production"
echo "⚠️  Enable firewall (ufw enable)"
echo "⚠️  Set up SSL certificates"
echo "⚠️  Regular security updates"