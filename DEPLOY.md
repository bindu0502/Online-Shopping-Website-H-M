# Project149 Deployment Guide

## Overview

This guide covers deploying Project149 (e-commerce + ML recommendation system) to production using Docker.

## Prerequisites

- Docker 20.10+
- Docker Compose 2.0+
- 4GB RAM minimum
- 10GB disk space

## Quick Start

### 1. Clone and Configure

```bash
git clone <repository-url>
cd Project149_Main

# Copy environment template
cp .env.example .env

# Edit .env with your values
nano .env
```

### 2. Required Environment Variables

Edit `.env` file:

```bash
# CRITICAL: Change these for production!
API_SECRET=your-super-secret-key-min-32-chars
DATABASE_URL=sqlite:///project149.db

# CORS - add your production domain
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# API URL for frontend
VITE_API_URL=https://api.yourdomain.com

# Ports
BACKEND_PORT=8000
FRONTEND_PORT=80
```

### 3. Build and Run

```bash
# Build and start all services
docker-compose up -d --build

# Check logs
docker-compose logs -f

# Check health
curl http://localhost:8000/health
curl http://localhost/
```

### 4. Post-Deployment Verification

```bash
# Run deployment checks
bash scripts/deploy_check.sh

# Run smoke tests
export API_URL=http://localhost:8000
node frontend/tests/smoke_auth.js
node frontend/tests/smoke_recommend.js
```

## Production Deployment

### Option 1: Docker Compose (Simple)

1. **Prepare server:**
   ```bash
   # Install Docker
   curl -fsSL https://get.docker.com -o get-docker.sh
   sh get-docker.sh
   
   # Install Docker Compose
   sudo apt-get install docker-compose-plugin
   ```

2. **Deploy:**
   ```bash
   # Copy files to server
   scp -r . user@server:/opt/project149/
   
   # SSH to server
   ssh user@server
   cd /opt/project149
   
   # Configure environment
   cp .env.example .env
   nano .env  # Edit with production values
   
   # Start services
   docker-compose up -d --build
   ```

3. **Setup reverse proxy (Nginx/Traefik):**
   ```nginx
   # /etc/nginx/sites-available/project149
   server {
       listen 80;
       server_name yourdomain.com;
       
       location / {
           proxy_pass http://localhost:80;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
       
       location /api {
           proxy_pass http://localhost:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

4. **Enable HTTPS with Let's Encrypt:**
   ```bash
   sudo apt-get install certbot python3-certbot-nginx
   sudo certbot --nginx -d yourdomain.com
   ```

### Option 2: Kubernetes (Scalable)

See `k8s/` directory for manifests:

```bash
# Apply configurations
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secrets.yaml
kubectl apply -f k8s/backend-deployment.yaml
kubectl apply -f k8s/frontend-deployment.yaml
kubectl apply -f k8s/ingress.yaml

# Check status
kubectl get pods -n project149
kubectl get svc -n project149
```

## Data Migration

### Import Products

```bash
# Enter backend container
docker-compose exec backend bash

# Run import scripts
python src/import_products.py
python src/update_image_paths.py
python src/update_prices.py

# Verify
python -c "from src.db import *; db=SessionLocal(); print(f'Products: {db.query(Product).count()}'); db.close()"
```

### Backup Database

```bash
# Backup
docker-compose exec backend sqlite3 project149.db .dump > backup_$(date +%Y%m%d).sql

# Restore
cat backup_20240101.sql | docker-compose exec -T backend sqlite3 project149.db
```

## Monitoring

### Health Checks

```bash
# API health
curl http://localhost:8000/health

# Response:
# {
#   "status": "healthy",
#   "service": "project149-api",
#   "database": "connected",
#   "images": "available"
# }

# Recommendation health
curl http://localhost:8000/recommend/health
```

### Logs

```bash
# View all logs
docker-compose logs -f

# View specific service
docker-compose logs -f backend
docker-compose logs -f frontend

# Last 100 lines
docker-compose logs --tail=100 backend
```

### Metrics

Add Prometheus/Grafana for production monitoring:

```yaml
# docker-compose.yml (add to services)
prometheus:
  image: prom/prometheus
  volumes:
    - ./prometheus.yml:/etc/prometheus/prometheus.yml
  ports:
    - "9090:9090"

grafana:
  image: grafana/grafana
  ports:
    - "3000:3000"
```

## Scaling

### Horizontal Scaling

```bash
# Scale backend
docker-compose up -d --scale backend=3

# With load balancer
# Add nginx/traefik to distribute traffic
```

### Caching with Redis

```bash
# Start with Redis
docker-compose --profile with-redis up -d

# Backend will use Redis for:
# - Session storage
# - Popular products cache
# - Recommendation cache
```

## Model Updates

### Reload Model Without Downtime

```bash
# Set auth token
export AUTH_TOKEN=your-admin-token

# Reload model
bash scripts/reload_model.sh

# Or manually:
curl -X POST http://localhost:8000/recommend/reload \
  -H "Authorization: Bearer $AUTH_TOKEN"
```

### Train New Model

```bash
# Enter container
docker-compose exec backend bash

# Train model
python src/model_train.py

# Reload via API
curl -X POST http://localhost:8000/recommend/reload
```

## Rollback Plan

### Quick Rollback

```bash
# Stop current deployment
docker-compose down

# Restore previous version
git checkout <previous-commit>

# Rebuild and start
docker-compose up -d --build

# Restore database if needed
cat backup_previous.sql | docker-compose exec -T backend sqlite3 project149.db
```

### Blue-Green Deployment

```bash
# Start new version on different ports
BACKEND_PORT=8001 FRONTEND_PORT=81 docker-compose up -d

# Test new version
bash scripts/deploy_check.sh

# Switch traffic (update nginx/load balancer)
# If issues, switch back to old version
```

## Security Checklist

- [ ] Change `API_SECRET` to strong random value
- [ ] Use HTTPS in production (Let's Encrypt)
- [ ] Set proper `CORS_ORIGINS` (no wildcards)
- [ ] Enable firewall (ufw/iptables)
- [ ] Regular security updates: `docker-compose pull && docker-compose up -d`
- [ ] Backup database regularly
- [ ] Monitor logs for suspicious activity
- [ ] Use secrets management (Vault/AWS Secrets Manager)
- [ ] Enable rate limiting on API
- [ ] Set up fail2ban for SSH

## Performance Optimization

### Database

```bash
# For production, consider PostgreSQL
DATABASE_URL=postgresql://user:pass@localhost/project149

# Add indexes
# See src/db.py for index definitions
```

### Caching

```python
# Add Redis caching for popular endpoints
# - GET /products/ (popular items)
# - GET /recommend/me (user recommendations)
# - Product details
```

### CDN

- Serve static images via CDN (CloudFlare/AWS CloudFront)
- Cache frontend assets
- Enable compression

## Troubleshooting

### Services Won't Start

```bash
# Check logs
docker-compose logs

# Check ports
netstat -tulpn | grep -E '8000|80'

# Rebuild from scratch
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
```

### Database Locked

```bash
# SQLite doesn't handle concurrent writes well
# For production, use PostgreSQL:
DATABASE_URL=postgresql://user:pass@db:5432/project149
```

### Out of Memory

```bash
# Increase Docker memory limit
# Or add swap space
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

### Images Not Loading

```bash
# Check images directory
docker-compose exec backend ls -la Project149/datasets/images_128_128/

# Re-run image path update
docker-compose exec backend python src/update_image_paths.py

# Check nginx config
docker-compose exec frontend cat /etc/nginx/conf.d/default.conf
```

## Support

- Documentation: See README.md files in each directory
- API Docs: http://localhost:8000/docs
- Issues: Create GitHub issue
- Logs: `docker-compose logs -f`

## Maintenance

### Regular Tasks

```bash
# Weekly: Update dependencies
docker-compose pull
docker-compose up -d

# Daily: Backup database
bash scripts/backup_db.sh

# Monthly: Clean old images
docker system prune -a

# As needed: Reload model
bash scripts/reload_model.sh
```

### Monitoring Checklist

- [ ] API response times < 200ms
- [ ] Error rate < 1%
- [ ] Database size growth
- [ ] Disk space > 20% free
- [ ] Memory usage < 80%
- [ ] CPU usage < 70%

## Production Checklist

Before going live:

- [ ] Environment variables configured
- [ ] HTTPS enabled
- [ ] Database backed up
- [ ] Products imported
- [ ] Image paths updated
- [ ] Prices set
- [ ] Health checks passing
- [ ] Smoke tests passing
- [ ] Monitoring configured
- [ ] Backup strategy in place
- [ ] Rollback plan tested
- [ ] Security hardening complete
- [ ] Performance tested
- [ ] Documentation updated

---

**Last Updated:** 2024
**Version:** 1.0.0
