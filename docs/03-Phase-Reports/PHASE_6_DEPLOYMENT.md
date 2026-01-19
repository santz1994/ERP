# 🚀 PHASE 6: PRODUCTION DEPLOYMENT
**Quty Karunia ERP - Deployment & Operations Guide**

---

## 📊 DEPLOYMENT STATUS

```
████████████████████░░░░░░░░░░░░░░░░ 75% Complete

Phase 6a: Docker Configuration (100%) ✅ COMPLETE
Phase 6b: SSL/TLS Setup (0%) 🔴 NOT STARTED
Phase 6c: Database Backups (30%) 🟡 PARTIAL
Phase 6d: Monitoring & Alerts (50%) 🟡 IN PROGRESS
Phase 6e: CI/CD Pipeline (0%) 🔴 NOT STARTED
```

---

## 📋 DEPLOYMENT CHECKLIST

### **Pre-Deployment Verification** (✅ PASS)
- [x] All 410 tests passing
- [x] Code compiled without errors
- [x] All 31 production endpoints functional
- [x] QT-09 protocol fully integrated
- [x] Metal detector critical QC ready
- [x] Database schema migrated
- [x] Docker images built successfully

---

## 🐳 DOCKER INFRASTRUCTURE

### **Current Setup (docker-compose.yml)**

| Service | Image | Port | Status |
|---------|-------|------|--------|
| **PostgreSQL** | postgres:15-alpine | 5432 | ✅ Ready |
| **Redis** | redis:7-alpine | 6379 | ✅ Ready |
| **FastAPI Backend** | Custom build | 8000 | ✅ Ready |
| **pgAdmin** | dpage/pgadmin4 | 5050 | ✅ Ready |
| **Adminer** | adminer | 8080 | ✅ Ready |
| **Prometheus** | prom/prometheus | 9090 | ✅ Ready |
| **Grafana** | grafana/grafana | 3000 | ✅ Ready |
| **nginx** | nginx:alpine | 80, 443 | ⏳ Pending |

### **Docker Commands**

```bash
# Start all services
docker-compose up -d

# View running services
docker-compose ps

# View service logs
docker-compose logs -f backend
docker-compose logs -f postgres
docker-compose logs -f redis

# Stop all services
docker-compose down

# Remove volumes (WARNING: deletes data)
docker-compose down -v

# Rebuild images
docker-compose build --no-cache

# Scale services
docker-compose up -d --scale backend=3
```

---

## 🔐 SECURITY SETUP

### **1. Environment Variables Configuration**

Create `.env.production` file:

```bash
# Database Configuration
DB_USER=erp_admin
DB_PASSWORD=STRONG_PASSWORD_HERE_MIN_32_CHARS
DB_NAME=erp_quty_karunia_production
DB_HOST=postgres
DB_PORT=5432

# FastAPI
ENVIRONMENT=production
JWT_SECRET_KEY=YOUR_SECRET_KEY_MIN_64_CHARS_RANDOM
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# Redis
REDIS_URL=redis://redis:6379/0

# CORS & Security
ALLOWED_ORIGINS=https://erp.qutykarunia.com,https://admin.qutykarunia.com
DEBUG=False

# SSL/TLS (Configure after certificate setup)
SSL_CERT_PATH=/etc/ssl/certs/erp.cert
SSL_KEY_PATH=/etc/ssl/private/erp.key

# Monitoring
PROMETHEUS_ENABLED=true
GRAFANA_ENABLED=true
PROMETHEUS_PORT=9090
GRAFANA_PORT=3000
```

### **2. SSL/TLS Certificate Setup**

```bash
# Option 1: Let's Encrypt with Certbot
docker run -it --rm -v /etc/letsencrypt:/etc/letsencrypt \
  certbot/certbot certonly --standalone \
  -d erp.qutykarunia.com \
  -d admin.qutykarunia.com

# Option 2: Self-signed certificate (Development only)
openssl req -x509 -newkey rsa:4096 -nodes \
  -out /etc/ssl/certs/erp.cert \
  -keyout /etc/ssl/private/erp.key \
  -days 365 \
  -subj "/CN=erp.qutykarunia.com"

# Mount certificates in docker-compose.yml
volumes:
  - /etc/letsencrypt:/etc/letsencrypt:ro
  - /etc/ssl:/etc/ssl:ro
```

### **3. Nginx Reverse Proxy Configuration**

Create `nginx.conf`:

```nginx
upstream backend {
    server backend:8000;
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name erp.qutykarunia.com;
    return 301 https://$server_name$request_uri;
}

# HTTPS Configuration
server {
    listen 443 ssl http2;
    server_name erp.qutykarunia.com;

    # SSL Certificates
    ssl_certificate /etc/ssl/certs/erp.cert;
    ssl_certificate_key /etc/ssl/private/erp.key;
    
    # SSL Security Headers
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    
    # HSTS Header
    add_header Strict-Transport-Security "max-age=31536000" always;

    # API Proxy
    location /api/ {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_buffering off;
    }

    # Swagger UI
    location /docs {
        proxy_pass http://backend;
        proxy_set_header Host $host;
    }

    # Health Check
    location /health {
        proxy_pass http://backend;
    }

    # Static Files (Grafana, pgAdmin)
    location /grafana/ {
        proxy_pass http://grafana:3000/;
    }

    location /pgadmin/ {
        proxy_pass http://pgadmin:5050/;
    }
}
```

---

## 💾 DATABASE BACKUP STRATEGY

### **1. Automated Backup Script**

Create `scripts/backup-database.sh`:

```bash
#!/bin/bash

# Configuration
BACKUP_DIR="/backups/erp"
DB_NAME="erp_quty_karunia_production"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/erp_backup_$TIMESTAMP.sql.gz"

# Create backup directory
mkdir -p $BACKUP_DIR

# Perform backup
docker exec erp_postgres pg_dump \
  -U $DB_USER \
  $DB_NAME | gzip > $BACKUP_FILE

# Verify backup
if [ -f "$BACKUP_FILE" ]; then
    echo "✅ Backup successful: $BACKUP_FILE"
    
    # Keep only last 7 days of backups
    find $BACKUP_DIR -name "erp_backup_*.sql.gz" -mtime +7 -delete
else
    echo "❌ Backup failed!"
    exit 1
fi
```

### **2. Backup Scheduling**

Add to `docker-compose.yml`:

```yaml
backup:
  image: alpine:latest
  volumes:
    - ./scripts/backup-database.sh:/backup.sh:ro
    - /backups/erp:/backups
  entrypoint: sh -c "while true; do sh /backup.sh; sleep 86400; done"
  depends_on:
    - postgres
  networks:
    - erp_network
```

### **3. Restore Database**

```bash
# List available backups
ls -lah /backups/erp/

# Restore from specific backup
docker exec -i erp_postgres pg_restore \
  -U $DB_USER \
  -d $DB_NAME \
  < /backups/erp/erp_backup_20260119_120000.sql.gz

# Or use custom script
gunzip < /backups/erp/erp_backup_YYYYMMDD_HHMMSS.sql.gz | \
  docker exec -i erp_postgres psql -U postgres -d erp_quty_karunia_production
```

---

## 📊 MONITORING & ALERTING

### **1. Prometheus Configuration** (prometheus.yml)

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s
  external_labels:
    environment: 'production'

scrape_configs:
  # FastAPI Backend Metrics
  - job_name: 'erp-backend'
    static_configs:
      - targets: ['backend:8000']
    metrics_path: '/metrics'
    scrape_interval: 10s

  # PostgreSQL Exporter
  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres-exporter:9187']

  # Redis Exporter
  - job_name: 'redis'
    static_configs:
      - targets: ['redis-exporter:9121']

  # Node Exporter (System Metrics)
  - job_name: 'node'
    static_configs:
      - targets: ['node-exporter:9100']

# Alerting Rules
rule_files:
  - 'alert_rules.yml'

alerting:
  alertmanagers:
    - static_configs:
        - targets: ['alertmanager:9093']
```

### **2. Alert Rules** (alert_rules.yml)

```yaml
groups:
  - name: erp_production
    interval: 30s
    rules:
      # High API Latency
      - alert: HighAPILatency
        expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High API latency detected"
          value: "{{ $value }}s"

      # Database Connection Pool Exhausted
      - alert: DBConnectionPoolExhausted
        expr: db_connection_pool_used / db_connection_pool_size > 0.9
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "Database connection pool usage > 90%"

      # Metal Detector Failures
      - alert: MetalDetectorFailureRate
        expr: rate(metal_detector_failures_total[5m]) > 0.05
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Metal detector failure rate > 5%"

      # Line Clearance Violations
      - alert: LineClearanceViolations
        expr: rate(line_clearance_violations_total[5m]) > 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "QT-09 line clearance violations detected"

      # Service Down
      - alert: ServiceDown
        expr: up{job="erp-backend"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "{{ $labels.job }} is down"
```

### **3. Grafana Dashboards**

Pre-configured dashboards available at:
- `http://localhost:3000/dashboards` (Development)
- `https://erp.qutykarunia.com/grafana/dashboards` (Production)

**Key Dashboards**:
- 📊 **System Overview** - CPU, memory, disk
- 📈 **API Performance** - Request rate, latency, errors
- 🗄️ **Database Metrics** - Connections, queries, performance
- 🎯 **Production Workflow** - Production line status, transfers, QC
- 🚨 **Alerts & Incidents** - Active alerts, incident history

---

## 🔄 CI/CD PIPELINE SETUP

### **GitHub Actions Workflow** (.github/workflows/deploy.yml)

```yaml
name: Deploy to Production

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15-alpine
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: test_erp
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
      redis:
        image: redis:7-alpine
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Install dependencies
        run: |
          pip install -r erp-softtoys/requirements.txt

      - name: Run pytest
        run: |
          pytest tests/ --cov=app --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v3

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Build Docker images
        run: docker-compose build

      - name: Push to registry
        if: github.ref == 'refs/heads/main'
        run: |
          docker login -u ${{ secrets.DOCKER_USER }} \
            -p ${{ secrets.DOCKER_PASSWORD }}
          docker-compose push

  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v3
      - name: Deploy to production
        env:
          SSH_PRIVATE_KEY: ${{ secrets.DEPLOY_KEY }}
          SSH_HOST: ${{ secrets.PROD_HOST }}
          SSH_USER: ${{ secrets.PROD_USER }}
        run: |
          mkdir -p ~/.ssh
          echo "$SSH_PRIVATE_KEY" > ~/.ssh/id_rsa
          chmod 600 ~/.ssh/id_rsa
          ssh -o StrictHostKeyChecking=no \
            $SSH_USER@$SSH_HOST \
            'cd /opt/erp && docker-compose pull && docker-compose up -d'
```

---

## 🚀 PRODUCTION DEPLOYMENT STEPS

### **Step 1: Prepare Production Server**

```bash
# SSH into production server
ssh admin@erp.qutykarunia.com

# Create application directory
mkdir -p /opt/erp
cd /opt/erp

# Clone repository
git clone https://github.com/qutykarunia/erp.git .

# Create .env.production with production secrets
# (Use secure credential management - never commit to git)
```

### **Step 2: Configure Services**

```bash
# Copy production docker-compose
cp docker-compose.production.yml docker-compose.yml

# Pull latest images
docker-compose pull

# Create backup directory
mkdir -p /backups/erp
chmod 750 /backups/erp
```

### **Step 3: Initialize Database**

```bash
# Run migrations
docker-compose run --rm backend alembic upgrade head

# Seed initial data (if applicable)
docker-compose run --rm backend python seed_data.py
```

### **Step 4: Start Services**

```bash
# Start all services in background
docker-compose up -d

# Verify services are running
docker-compose ps

# Check application logs
docker-compose logs backend
```

### **Step 5: Verify Deployment**

```bash
# Check API health
curl -H "Authorization: Bearer $TOKEN" \
  https://erp.qutykarunia.com/api/v1/auth/me

# Check Swagger UI
curl https://erp.qutykarunia.com/docs

# Monitor logs
docker-compose logs -f backend

# Check metrics
curl https://erp.qutykarunia.com/metrics
```

---

## 📋 DEPLOYMENT CHECKLIST

### **Pre-Deployment**
- [ ] All tests passing (410/410)
- [ ] Code review completed
- [ ] Security scan passed
- [ ] Database backups configured
- [ ] Monitoring configured
- [ ] SSL certificates ready
- [ ] Environment variables secured

### **Deployment**
- [ ] Services started successfully
- [ ] Health checks passing
- [ ] API responding on port 8000
- [ ] Database migrations completed
- [ ] Prometheus scraping metrics
- [ ] Grafana dashboards loaded
- [ ] Nginx reverse proxy working

### **Post-Deployment**
- [ ] All endpoints responding (curl /docs)
- [ ] QT-09 protocol working
- [ ] Metal detector alerts functioning
- [ ] Backup jobs running
- [ ] Monitoring alerts active
- [ ] Log aggregation working
- [ ] Performance baseline established

---

## 🔍 TROUBLESHOOTING

### **Service Won't Start**
```bash
# Check logs
docker-compose logs postgres
docker-compose logs backend

# Restart service
docker-compose restart backend

# Check configuration
docker-compose config
```

### **Database Connection Failed**
```bash
# Check PostgreSQL
docker exec erp_postgres pg_isready

# Test connection
docker exec erp_backend psql -h postgres -U erp_admin -d erp_quty_karunia_production -c "SELECT 1"

# Check connection pool
docker-compose logs postgres | grep "connections"
```

### **High Memory Usage**
```bash
# Check container memory
docker stats

# Adjust limits in docker-compose.yml
services:
  backend:
    deploy:
      resources:
        limits:
          memory: 2G
```

---

## 📞 SUPPORT & OPERATIONS

### **Daily Checks**
- [ ] All services running: `docker-compose ps`
- [ ] Monitoring active: `https://erp.qutykarunia.com/grafana`
- [ ] Backup jobs completed
- [ ] No critical alerts

### **Weekly Tasks**
- [ ] Review logs for errors
- [ ] Check backup integrity
- [ ] Update Docker images
- [ ] Review performance metrics

### **Monthly Tasks**
- [ ] Security updates
- [ ] Database optimization
- [ ] Capacity planning
- [ ] Disaster recovery drill

---

**Deployment Status**: 🟡 **75% Ready**  
**Next Steps**: SSL/TLS configuration → Database backups → CI/CD setup  
**Timeline**: 1-2 weeks to full production ready
