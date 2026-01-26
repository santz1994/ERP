# 🚀 STAGING & CI/CD IMPLEMENTATION GUIDE

**Status**: Ready for Implementation  
**Effort**: 10-14 hours  
**Timeline**: 1-2 weeks  

---

## 📋 TABLE OF CONTENTS

1. Staging Environment Setup
2. CI/CD Pipeline Configuration
3. Monitoring & Alerting
4. Deployment Procedures
5. Rollback & Recovery
6. Team Runbooks

---

## 1️⃣ STAGING ENVIRONMENT SETUP

### 1.1 Prerequisites

```bash
# Install Docker & Docker Compose
sudo apt-get update
sudo apt-get install -y docker.io docker-compose

# Install additional tools
sudo apt-get install -y curl wget git postgresql-client redis-tools

# Create staging user
sudo useradd -m -s /bin/bash staging
sudo usermod -aG docker staging

# Create directories
mkdir -p /app/erp/{config,backups,logs,data}
cd /app/erp
```

### 1.2 Staging Infrastructure Setup

**Step 1: Clone production data structure**

```bash
#!/bin/bash
# File: scripts/setup-staging.sh

# Create .env file for staging
cat > /app/erp/.env.staging << EOF
# PostgreSQL
POSTGRES_DB=erp_staging
POSTGRES_USER=erp_staging_user
POSTGRES_PASSWORD=$(openssl rand -base64 32)

# Backend
DATABASE_URL=postgresql://erp_staging_user:${POSTGRES_PASSWORD}@postgres:5432/erp_staging
REDIS_URL=redis://redis:6379/0
JWT_SECRET=$(openssl rand -base64 64)
ENVIRONMENT=staging
LOG_LEVEL=INFO
CORS_ORIGINS=https://staging.erp.qutykarunia.com

# Frontend
REACT_APP_API_URL=https://api-staging.qutykarunia.com
REACT_APP_ENV=staging

# Monitoring
PROMETHEUS_ENABLED=true
GRAFANA_ADMIN_PASSWORD=$(openssl rand -base64 16)
EOF

# Create staging-specific docker-compose
cat > /app/erp/docker-compose.staging.yml << 'COMPOSEFILE'
version: '3.9'

services:
  # Nginx reverse proxy
  nginx:
    image: nginx:1.24-alpine
    container_name: nginx-staging
    volumes:
      - ./config/nginx-staging.conf:/etc/nginx/nginx.conf:ro
      - ./config/ssl:/etc/nginx/ssl:ro
    ports:
      - "80:80"
      - "443:443"
    depends_on:
      - frontend
      - backend
    networks:
      - erp-staging
    healthcheck:
      test: ["CMD", "wget", "-q", "--spider", "http://localhost"]
      interval: 30s
      timeout: 10s
      retries: 3
    restart: always

  # Frontend
  frontend:
    image: erp-ui:staging
    container_name: frontend-staging
    environment:
      - NODE_ENV=production
      - REACT_APP_API_URL=https://api-staging.qutykarunia.com
      - REACT_APP_ENV=staging
    ports:
      - "3001:3000"
    depends_on:
      - backend
    networks:
      - erp-staging
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000"]
      interval: 30s
      timeout: 10s
      retries: 3
    restart: always

  # Backend API
  backend:
    image: erp-backend:staging
    container_name: backend-staging
    environment:
      - DATABASE_URL=postgresql://erp_staging_user:${POSTGRES_PASSWORD}@postgres:5432/erp_staging
      - REDIS_URL=redis://redis:6379
      - JWT_SECRET=${JWT_SECRET}
      - ENVIRONMENT=staging
      - LOG_LEVEL=INFO
      - PROMETHEUS_ENABLED=true
    ports:
      - "8000:8000"
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    networks:
      - erp-staging
    volumes:
      - ./logs/backend:/app/logs
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    restart: always

  # PostgreSQL
  postgres:
    image: postgres:15-alpine
    container_name: postgres-staging
    environment:
      POSTGRES_DB: erp_staging
      POSTGRES_USER: erp_staging_user
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      PGLOG: /var/log/postgresql
    volumes:
      - postgres-staging-data:/var/lib/postgresql/data
      - ./logs/postgres:/var/log/postgresql
    ports:
      - "5433:5432"
    networks:
      - erp-staging
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U erp_staging_user -d erp_staging"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: always
    command:
      - "postgres"
      - "-c"
      - "log_statement=all"
      - "-c"
      - "log_duration=on"
      - "-c"
      - "log_min_duration_statement=1000"

  # Redis
  redis:
    image: redis:7-alpine
    container_name: redis-staging
    ports:
      - "6380:6379"
    networks:
      - erp-staging
    volumes:
      - redis-staging-data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: always
    command: redis-server --appendonly yes

  # Prometheus
  prometheus:
    image: prom/prometheus:latest
    container_name: prometheus-staging
    volumes:
      - ./config/prometheus-staging.yml:/etc/prometheus/prometheus.yml:ro
      - prometheus-staging-data:/prometheus
    ports:
      - "9091:9090"
    networks:
      - erp-staging
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--storage.tsdb.retention.time=7d'
    restart: always

  # Grafana
  grafana:
    image: grafana/grafana:latest
    container_name: grafana-staging
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_ADMIN_PASSWORD}
      - GF_INSTALL_PLUGINS=grafana-clock-panel,grafana-simple-json-datasource
    volumes:
      - ./config/grafana/provisioning:/etc/grafana/provisioning:ro
      - grafana-staging-data:/var/lib/grafana
    ports:
      - "3003:3000"
    networks:
      - erp-staging
    depends_on:
      - prometheus
    restart: always

  # AlertManager
  alertmanager:
    image: prom/alertmanager:latest
    container_name: alertmanager-staging
    volumes:
      - ./config/alertmanager.yml:/etc/alertmanager/alertmanager.yml:ro
    ports:
      - "9093:9093"
    networks:
      - erp-staging
    command:
      - '--config.file=/etc/alertmanager/alertmanager.yml'
      - '--storage.path=/alertmanager'
    restart: always

networks:
  erp-staging:
    driver: bridge

volumes:
  postgres-staging-data:
    driver: local
  redis-staging-data:
    driver: local
  prometheus-staging-data:
    driver: local
  grafana-staging-data:
    driver: local
COMPOSEFILE

echo "✅ Staging infrastructure files created"
```

### 1.3 Database Setup

**Step 2: Clone production database**

```bash
#!/bin/bash
# File: scripts/clone-prod-to-staging.sh

set -e

echo "🔄 Starting production database clone..."

PROD_HOST="prod-db.qutykarunia.com"
PROD_DB="erp_production"
PROD_USER="prod_user"
STAGING_HOST="localhost"
STAGING_DB="erp_staging"
STAGING_USER="erp_staging_user"

# Backup production
echo "📦 Creating production backup..."
pg_dump \
  -h $PROD_HOST \
  -U $PROD_USER \
  -d $PROD_DB \
  --no-password \
  --verbose \
  --format=custom \
  --file=./backups/prod_$(date +%Y%m%d_%H%M%S).dump

# Wait for dump completion
sleep 5

# Get latest dump
LATEST_DUMP=$(ls -t ./backups/prod_*.dump | head -1)
echo "📥 Using dump: $LATEST_DUMP"

# Restore to staging
echo "🔄 Restoring to staging..."
pg_restore \
  -h $STAGING_HOST \
  -U $STAGING_USER \
  -d $STAGING_DB \
  --if-exists \
  --clean \
  --verbose \
  $LATEST_DUMP

# Anonymize PII
echo "🔒 Anonymizing PII..."
PGPASSWORD=$(grep POSTGRES_PASSWORD .env.staging | cut -d= -f2) \
psql -h $STAGING_HOST -U $STAGING_USER -d $STAGING_DB \
  -f ./scripts/anonymize-staging.sql

echo "✅ Database clone complete"
```

**Step 3: Anonymize sensitive data**

```sql
-- File: scripts/anonymize-staging.sql

-- Anonymize user personal information
UPDATE public.users 
SET 
    email = 'test' || id || '@test.com',
    phone = '08' || LPAD((id % 1000000000)::text, 9, '0'),
    name = 'TestUser' || id
WHERE environment = 'staging';

-- Clear JWT tokens
TRUNCATE TABLE public.jwt_tokens;

-- Clear sensitive logs
DELETE FROM public.api_logs 
WHERE created_at < CURRENT_DATE - INTERVAL '7 days';

-- Clear PII from audit logs
UPDATE public.audit_logs 
SET 
    old_value = NULL,
    new_value = NULL
WHERE old_value LIKE '%email%' OR old_value LIKE '%phone%';

-- Verify anonymization
SELECT 'Users anonymized:', COUNT(*) FROM public.users;
SELECT 'Tokens cleared:', COUNT(*) FROM public.jwt_tokens;
```

### 1.4 Testing Database Integrity

```bash
#!/bin/bash
# File: scripts/test-staging-integrity.sh

echo "🧪 Testing staging database integrity..."

PGPASSWORD=$POSTGRES_PASSWORD psql -h localhost -p 5433 -U erp_staging_user -d erp_staging << EOF

-- Test: Table count
SELECT 'Tables' as test, COUNT(*) as count FROM information_schema.tables 
WHERE table_schema = 'public';

-- Test: Foreign key constraints
SELECT COUNT(*) FROM information_schema.table_constraints 
WHERE constraint_type = 'FOREIGN KEY' AND table_schema = 'public';

-- Test: Data integrity
SELECT 'Users', COUNT(*) FROM public.users
UNION ALL
SELECT 'SPK', COUNT(*) FROM public.spk
UNION ALL
SELECT 'Daily Production', COUNT(*) FROM public.daily_production_input;

-- Test: No sensitive data
SELECT COUNT(*) as found_sensitive_emails
FROM public.users 
WHERE email NOT LIKE 'test%@test.com';

EOF

echo "✅ Integrity check complete"
```

---

## 2️⃣ CI/CD PIPELINE CONFIGURATION

### 2.1 GitHub Actions Setup

**Step 1: Create secrets in GitHub**

```bash
# Navigate to: Settings > Secrets and variables > Actions

# Add these secrets:
- STAGING_SSH_KEY: Private SSH key for staging server
- STAGING_HOST: staging.erp.qutykarunia.com
- PROD_SSH_KEY: Private SSH key for production server
- PROD_HOST: api.erp.qutykarunia.com
- SONAR_HOST_URL: SonarQube instance URL
- SONAR_TOKEN: SonarQube authentication token
- SLACK_WEBHOOK_STAGING: Slack webhook for staging notifications
- SLACK_WEBHOOK_PROD: Slack webhook for production notifications
- DOCKER_REGISTRY_URL: Docker registry URL
- DOCKER_REGISTRY_USERNAME: Registry username
- DOCKER_REGISTRY_PASSWORD: Registry password
```

**Step 2: Create workflow file**

```yaml
# File: .github/workflows/ci-cd-pipeline.yml

name: CI/CD Pipeline

on:
  push:
    branches: [main, develop, staging]
  pull_request:
    branches: [main, develop]
  schedule:
    # Daily security scan at 2 AM
    - cron: '0 2 * * *'

env:
  REGISTRY: ${{ secrets.DOCKER_REGISTRY_URL }}
  IMAGE_TAG: ${{ github.sha }}

jobs:
  # ===== LINT & FORMAT =====
  lint:
    runs-on: ubuntu-latest
    name: Code Quality Checks
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      # Kotlin Lint
      - name: Set up JDK 17
        uses: actions/setup-java@v4
        with:
          java-version: '17'
          distribution: 'temurin'

      - name: Run Kotlin linter
        working-directory: erp-ui/mobile
        run: ./gradlew ktlint

      # TypeScript Lint
      - name: Set up Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '18'
          cache: 'npm'
          cache-dependency-path: erp-ui/frontend/package-lock.json

      - name: Install dependencies (Frontend)
        working-directory: erp-ui/frontend
        run: npm ci

      - name: Run TypeScript checks
        working-directory: erp-ui/frontend
        run: npm run lint

      - name: Run Prettier format check
        working-directory: erp-ui/frontend
        run: npm run format:check

      # Python Lint
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
          cache: 'pip'

      - name: Install Python dependencies
        run: |
          pip install -r erp-softtoys/requirements-dev.txt

      - name: Run Pylint
        working-directory: erp-softtoys
        run: pylint --recursive=y app/

      - name: Run Black formatter check
        working-directory: erp-softtoys
        run: black --check app/

  # ===== SECURITY SCAN =====
  security:
    runs-on: ubuntu-latest
    name: Security Scanning
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      # Dependency check
      - name: Run OWASP dependency-check
        uses: dependency-check/Dependency-Check_Action@main
        with:
          path: '.'
          format: 'JSON'
          args: >
            --enableExperimental
            --exclude node_modules
            --exclude .git

      # SonarQube scan
      - name: SonarQube Scan
        uses: sonarsource/sonarqube-scan-action@master
        env:
          SONAR_HOST_URL: ${{ secrets.SONAR_HOST_URL }}
          SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}

      # SAST scan
      - name: Run Snyk Security Scan
        uses: snyk/actions/setup@master
        with:
          snyk-version: latest
        env:
          SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
        run: snyk test --severity-threshold=high

  # ===== BUILD =====
  build:
    needs: lint
    runs-on: ubuntu-latest
    name: Build Artifacts
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      # Android Build
      - name: Set up JDK 17
        uses: actions/setup-java@v4
        with:
          java-version: '17'
          distribution: 'temurin'

      - name: Build Android APK
        working-directory: erp-ui/mobile
        run: ./gradlew clean assemble

      - name: Build Android App Bundle
        working-directory: erp-ui/mobile
        run: ./gradlew bundle

      - name: Upload Android APK
        uses: actions/upload-artifact@v3
        with:
          name: android-apk
          path: erp-ui/mobile/app/build/outputs/apk/**/*.apk
          retention-days: 30

      # Backend Build
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install Python dependencies
        run: |
          pip install -r erp-softtoys/requirements.txt

      - name: Build Python wheel
        working-directory: erp-softtoys
        run: |
          pip install build
          python -m build

      - name: Upload Backend wheel
        uses: actions/upload-artifact@v3
        with:
          name: backend-wheel
          path: erp-softtoys/dist/**/*.whl
          retention-days: 30

      # Frontend Build
      - name: Set up Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '18'
          cache: 'npm'
          cache-dependency-path: erp-ui/frontend/package-lock.json

      - name: Build Frontend
        working-directory: erp-ui/frontend
        run: npm run build

      - name: Upload Frontend build
        uses: actions/upload-artifact@v3
        with:
          name: frontend-build
          path: erp-ui/frontend/dist/
          retention-days: 30

      # Docker Build
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2

      - name: Login to Docker Registry
        uses: docker/login-action@v2
        with:
          registry: ${{ secrets.DOCKER_REGISTRY_URL }}
          username: ${{ secrets.DOCKER_REGISTRY_USERNAME }}
          password: ${{ secrets.DOCKER_REGISTRY_PASSWORD }}

      - name: Build and push Backend Docker image
        uses: docker/build-push-action@v4
        with:
          context: erp-softtoys
          file: erp-softtoys/Dockerfile
          push: true
          tags: |
            ${{ env.REGISTRY }}/erp-backend:${{ env.IMAGE_TAG }}
            ${{ env.REGISTRY }}/erp-backend:latest

      - name: Build and push Frontend Docker image
        uses: docker/build-push-action@v4
        with:
          context: erp-ui/frontend
          file: erp-ui/frontend/Dockerfile
          push: true
          tags: |
            ${{ env.REGISTRY }}/erp-ui:${{ env.IMAGE_TAG }}
            ${{ env.REGISTRY }}/erp-ui:latest

  # ===== TEST =====
  test:
    needs: build
    runs-on: ubuntu-latest
    name: Test Suite

    services:
      postgres:
        image: postgres:15-alpine
        env:
          POSTGRES_DB: erp_test
          POSTGRES_USER: test_user
          POSTGRES_PASSWORD: test_pass
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432

      redis:
        image: redis:7-alpine
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 6379:6379

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      # Kotlin Tests
      - name: Set up JDK 17
        uses: actions/setup-java@v4
        with:
          java-version: '17'
          distribution: 'temurin'

      - name: Run Android unit tests
        working-directory: erp-ui/mobile
        run: ./gradlew test --info

      - name: Generate test coverage report
        working-directory: erp-ui/mobile
        run: ./gradlew jacocoTestReport

      - name: Upload Kotlin coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./erp-ui/mobile/app/build/reports/jacoco/test/jacocoTestReport.xml
          flags: kotlin

      # Python Tests
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install Python dependencies
        run: |
          pip install -r erp-softtoys/requirements-dev.txt

      - name: Run backend unit tests
        working-directory: erp-softtoys
        env:
          DATABASE_URL: postgresql://test_user:test_pass@localhost/erp_test
          REDIS_URL: redis://localhost:6379
        run: pytest tests/ -v --cov=app --cov-report=xml --cov-report=term

      - name: Upload Python coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./erp-softtoys/coverage.xml
          flags: python

      # JavaScript Tests
      - name: Set up Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '18'
          cache: 'npm'
          cache-dependency-path: erp-ui/frontend/package-lock.json

      - name: Run frontend unit tests
        working-directory: erp-ui/frontend
        run: npm run test -- --coverage --watchAll=false

      - name: Upload JavaScript coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./erp-ui/frontend/coverage/coverage-final.json
          flags: javascript

  # ===== DEPLOY TO STAGING =====
  deploy-staging:
    needs: [test, security]
    runs-on: ubuntu-latest
    name: Deploy to Staging
    if: github.ref == 'refs/heads/develop' || github.ref == 'refs/heads/staging'
    environment: staging

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Deploy to staging server
        env:
          SSH_PRIVATE_KEY: ${{ secrets.STAGING_SSH_KEY }}
          SSH_HOST: ${{ secrets.STAGING_HOST }}
        run: |
          mkdir -p ~/.ssh
          echo "$SSH_PRIVATE_KEY" > ~/.ssh/id_rsa
          chmod 600 ~/.ssh/id_rsa
          ssh-keyscan -H $SSH_HOST >> ~/.ssh/known_hosts
          
          ssh -i ~/.ssh/id_rsa deploy@$SSH_HOST << 'DEPLOY_SCRIPT'
          cd /app/erp
          git pull origin staging
          
          # Build and start services
          docker-compose -f docker-compose.staging.yml pull
          docker-compose -f docker-compose.staging.yml down
          docker-compose -f docker-compose.staging.yml up -d
          
          # Wait for services to be healthy
          echo "Waiting for services to be healthy..."
          sleep 30
          
          # Run smoke tests
          bash scripts/smoke-tests.sh
          
          # Run integration tests
          docker-compose -f docker-compose.staging.yml exec -T backend \
            pytest tests/integration/ -v
          
          echo "✅ Staging deployment complete"
          DEPLOY_SCRIPT

      - name: Notify Slack - Success
        if: success()
        uses: slackapi/slack-github-action@v1
        with:
          webhook-url: ${{ secrets.SLACK_WEBHOOK_STAGING }}
          payload: |
            {
              "text": "✅ Staging Deployment Successful",
              "blocks": [
                {
                  "type": "section",
                  "text": {
                    "type": "mrkdwn",
                    "text": "*Staging Deployment*\n*Branch:* ${{ github.ref_name }}\n*Commit:* ${{ github.sha }}\n*Status:* ✅ Success"
                  }
                }
              ]
            }

      - name: Notify Slack - Failure
        if: failure()
        uses: slackapi/slack-github-action@v1
        with:
          webhook-url: ${{ secrets.SLACK_WEBHOOK_STAGING }}
          payload: |
            {
              "text": "❌ Staging Deployment Failed",
              "blocks": [
                {
                  "type": "section",
                  "text": {
                    "type": "mrkdwn",
                    "text": "*Staging Deployment Failed*\n*Branch:* ${{ github.ref_name }}\n*Status:* ❌ Failed\n*Link:* ${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}"
                  }
                }
              ]
            }

  # ===== DEPLOY TO PRODUCTION =====
  deploy-production:
    needs: [test, security]
    runs-on: ubuntu-latest
    name: Deploy to Production
    if: github.ref == 'refs/heads/main'
    environment: production

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Create GitHub Release
        uses: actions/create-release@v1
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        with:
          tag_name: v${{ github.run_number }}
          release_name: Release v${{ github.run_number }}
          body: |
            Release v${{ github.run_number }}
            Commit: ${{ github.sha }}
            Branch: ${{ github.ref_name }}

      - name: Deploy to production server
        env:
          SSH_PRIVATE_KEY: ${{ secrets.PROD_SSH_KEY }}
          SSH_HOST: ${{ secrets.PROD_HOST }}
        run: |
          mkdir -p ~/.ssh
          echo "$SSH_PRIVATE_KEY" > ~/.ssh/id_rsa
          chmod 600 ~/.ssh/id_rsa
          ssh-keyscan -H $SSH_HOST >> ~/.ssh/known_hosts
          
          ssh -i ~/.ssh/id_rsa deploy@$SSH_HOST << 'DEPLOY_SCRIPT'
          cd /app/erp
          
          # Blue-Green deployment
          echo "Starting blue-green deployment..."
          
          # Pull latest
          git pull origin main
          
          # Create backup of current state
          docker-compose -f docker-compose.prod.yml exec -T postgres \
            pg_dump -U erp_user erp_production > /backups/pre-deploy-$(date +%Y%m%d_%H%M%S).dump
          
          # Deploy green (new version)
          export DOCKER_TAG=${{ github.sha }}
          docker-compose -f docker-compose.prod.yml pull
          docker-compose -f docker-compose.prod.yml up -d --scale backend=2
          
          # Wait for new services
          sleep 60
          
          # Health check
          echo "Running health checks..."
          curl -f http://localhost:8000/health || exit 1
          curl -f http://localhost:3000 || exit 1
          
          # Run smoke tests
          bash scripts/smoke-tests.sh || exit 1
          
          # Switch traffic to green (done by load balancer)
          echo "✅ Production deployment complete"
          DEPLOY_SCRIPT

      - name: Notify Slack - Success
        if: success()
        uses: slackapi/slack-github-action@v1
        with:
          webhook-url: ${{ secrets.SLACK_WEBHOOK_PROD }}
          payload: |
            {
              "text": "🚀 Production Deployment Successful",
              "blocks": [
                {
                  "type": "section",
                  "text": {
                    "type": "mrkdwn",
                    "text": "*Production Deployment*\n*Version:* v${{ github.run_number }}\n*Commit:* ${{ github.sha }}\n*Status:* 🚀 Live"
                  }
                }
              ]
            }

      - name: Notify Slack - Failure
        if: failure()
        uses: slackapi/slack-github-action@v1
        with:
          webhook-url: ${{ secrets.SLACK_WEBHOOK_PROD }}
          payload: |
            {
              "text": "🔴 Production Deployment Failed - ROLLBACK REQUIRED",
              "blocks": [
                {
                  "type": "section",
                  "text": {
                    "type": "mrkdwn",
                    "text": "*Production Deployment Failed*\n*Version:* v${{ github.run_number }}\n*Status:* 🔴 FAILED - Manual intervention required"
                  }
                }
              ]
            }
```

---

## 3️⃣ MONITORING & ALERTING

### 3.1 Prometheus Configuration

```yaml
# File: config/prometheus-staging.yml

global:
  scrape_interval: 15s
  evaluation_interval: 15s
  external_labels:
    environment: 'staging'
    team: 'erp-team'

alerting:
  alertmanagers:
    - static_configs:
        - targets: ['alertmanager:9093']
      scheme: http
      timeout: 10s

rule_files:
  - 'alert-rules.yml'

scrape_configs:
  # Backend metrics
  - job_name: 'backend'
    static_configs:
      - targets: ['backend:8000']
    metrics_path: '/metrics'
    scrape_interval: 30s
    scrape_timeout: 10s

  # PostgreSQL metrics
  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres-exporter:9187']
    scrape_interval: 30s

  # Redis metrics
  - job_name: 'redis'
    static_configs:
      - targets: ['redis-exporter:9121']
    scrape_interval: 30s

  # Node metrics
  - job_name: 'node'
    static_configs:
      - targets: ['node-exporter:9100']
    scrape_interval: 30s
```

### 3.2 Alert Rules

```yaml
# File: config/alert-rules.yml

groups:
  - name: api_alerts
    interval: 1m
    rules:
      - alert: HighAPIResponseTime
        expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High API response time"
          description: "API p95 response time > 1s for more than 5 minutes"

      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.01
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "High 5xx error rate"
          description: "Error rate > 1% for more than 2 minutes"

  - name: database_alerts
    interval: 1m
    rules:
      - alert: DatabaseConnectionPoolExhausted
        expr: pg_stat_activity_count / pg_settings_max_connections > 0.8
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Database connection pool high"
          description: "Connection pool usage > 80%"

      - alert: SlowQueries
        expr: rate(pg_stat_statements_mean_exec_time[5m]) > 1000
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Slow database queries detected"
          description: "Average query time > 1 second"

  - name: system_alerts
    interval: 1m
    rules:
      - alert: HighMemoryUsage
        expr: (1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) > 0.85
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High memory usage"
          description: "Memory usage > 85%"

      - alert: DiskSpaceLow
        expr: (node_filesystem_avail_bytes / node_filesystem_size_bytes) < 0.1
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Low disk space"
          description: "Disk space < 10%"

  - name: application_alerts
    interval: 1m
    rules:
      - alert: HighMobileAppCrashRate
        expr: rate(mobile_app_crashes_total[1h]) > 0.001
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High mobile app crash rate"
          description: "Crash rate > 0.1%"

      - alert: SyncQueueBacklog
        expr: offline_sync_queue_size > 1000
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "Large offline sync queue"
          description: "Offline sync queue > 1000 items"
```

---

## 4️⃣ DEPLOYMENT PROCEDURES

### 4.1 Pre-Deployment Checklist

```bash
#!/bin/bash
# File: scripts/pre-deployment-checklist.sh

echo "📋 Pre-Deployment Checklist"
echo "============================"

# 1. Code quality
echo "1️⃣  Code Quality Checks..."
git diff --quiet || echo "❌ Uncommitted changes. Commit first." && exit 1
npm run lint || echo "❌ Linting failed" && exit 1
npm run build || echo "❌ Build failed" && exit 1

# 2. Test coverage
echo "2️⃣  Test Coverage..."
npm run test -- --coverage --watchAll=false
COVERAGE=$(cat coverage/coverage-summary.json | jq '.total.lines.pct')
if (( $(echo "$COVERAGE < 80" | bc -l) )); then
  echo "❌ Coverage below 80%: $COVERAGE%"
  exit 1
fi

# 3. Security scan
echo "3️⃣  Security Scan..."
npm audit --audit-level=moderate || echo "⚠️  Security vulnerabilities found"

# 4. Database migration test
echo "4️⃣  Database Migration Test..."
npm run migrate:test || echo "❌ Migration test failed" && exit 1

# 5. Backup verification
echo "5️⃣  Backup Verification..."
ls -lh backups/prod_*.dump | tail -1 || echo "❌ No recent backup found" && exit 1

# 6. Service health
echo "6️⃣  Current Service Health..."
curl -s http://localhost:8000/health | jq .
curl -s http://localhost:3000/health | jq .

echo "✅ All pre-deployment checks passed!"
```

### 4.2 Staging Deployment

```bash
#!/bin/bash
# File: scripts/deploy-staging.sh

set -e

echo "🚀 Deploying to Staging..."

# 1. Code checkout
echo "📥 Pulling latest code..."
git pull origin staging

# 2. Run pre-deployment checks
echo "📋 Running pre-deployment checks..."
bash scripts/pre-deployment-checklist.sh || exit 1

# 3. Database backup
echo "💾 Creating database backup..."
docker-compose -f docker-compose.staging.yml exec -T postgres \
  pg_dump -U erp_staging_user erp_staging > \
  backups/staging_pre_deploy_$(date +%Y%m%d_%H%M%S).dump

# 4. Build and deploy
echo "🔨 Building and deploying..."
docker-compose -f docker-compose.staging.yml pull
docker-compose -f docker-compose.staging.yml down
docker-compose -f docker-compose.staging.yml up -d

# 5. Wait for services
echo "⏳ Waiting for services to be healthy..."
MAX_ATTEMPTS=30
ATTEMPT=1
while [ $ATTEMPT -le $MAX_ATTEMPTS ]; do
  if curl -f http://localhost:8000/health && curl -f http://localhost:3000; then
    echo "✅ Services are healthy"
    break
  fi
  echo "Attempt $ATTEMPT/$MAX_ATTEMPTS..."
  sleep 10
  ATTEMPT=$((ATTEMPT + 1))
done

# 6. Run tests
echo "🧪 Running tests..."
bash scripts/smoke-tests.sh

# 7. Notify
echo "✅ Staging deployment complete!"
```

### 4.3 Production Rollback

```bash
#!/bin/bash
# File: scripts/rollback-prod.sh

set -e

echo "🔄 Production Rollback Initiated"

# 1. Get last backup
LAST_BACKUP=$(ls -t backups/prod_*.dump | head -1)
echo "Using backup: $LAST_BACKUP"

# 2. Stop current services
echo "🛑 Stopping current services..."
docker-compose -f docker-compose.prod.yml down

# 3. Restore database
echo "📥 Restoring database..."
docker-compose -f docker-compose.prod.yml up -d postgres
sleep 30
pg_restore -d erp_production < $LAST_BACKUP

# 4. Restart services
echo "🚀 Restarting services..."
docker-compose -f docker-compose.prod.yml up -d

# 5. Verify
echo "✅ Verifying..."
curl -f http://localhost:8000/health
curl -f http://localhost:3000

echo "✅ Rollback complete"
```

---

## 5️⃣ TEAM RUNBOOKS

### 5.1 Daily Operations Runbook

```markdown
# Daily Operations Runbook

## Morning Checks (8 AM)

### 1. System Health
- [ ] Check Grafana dashboards
- [ ] Review error logs (Kibana)
- [ ] Check alert status (AlertManager)

### 2. Database Integrity
- [ ] Run integrity checks
- [ ] Verify backup completion
- [ ] Check disk space

### 3. API Endpoint Health
- [ ] GET /health on all services
- [ ] Check response times (p95, p99)
- [ ] Verify error rate < 0.5%

### 4. Mobile Metrics
- [ ] Check crash rate
- [ ] Review sync queue size
- [ ] Check connectivity issues

## During Business Hours

### 1. Issue Response
- If error rate > 1%:
  - [ ] Check error logs
  - [ ] Identify affected endpoints
  - [ ] Scale up if CPU > 80%
  
- If sync queue > 1000:
  - [ ] Check network connectivity
  - [ ] Restart sync workers
  - [ ] Escalate if persists

### 2. User Reports
- [ ] Log issue in ticketing system
- [ ] Check logs for user session
- [ ] Reproduce in staging first

## End of Day

- [ ] Review error logs
- [ ] Check backup completion
- [ ] Document any incidents
- [ ] Prepare handoff notes
```

### 5.2 Incident Response Runbook

```markdown
# Incident Response Runbook

## Critical Alert: High Error Rate (>5%)

### Immediate Actions (0-5 min)
1. [ ] Acknowledge alert in Slack/PagerDuty
2. [ ] Check Grafana dashboards
3. [ ] Identify affected service (API/DB/Frontend)
4. [ ] Get on incident call

### Investigation (5-15 min)
1. [ ] Check error logs in Kibana
2. [ ] Identify error pattern
3. [ ] Check recent deployments
4. [ ] Check resource utilization (CPU, memory, connections)

### Remediation
- If recent deployment → Rollback
- If resource limit → Scale up
- If database → Restart DB
- If API → Restart API service

### Communication
- [ ] Update status in Slack
- [ ] Notify stakeholders
- [ ] Document incident

## Critical Alert: Database Connection Pool Exhausted

### Immediate Actions
1. [ ] Check active connections: `psql -d erp_production -c "SELECT count(*) FROM pg_stat_activity;"`
2. [ ] Kill idle connections if necessary
3. [ ] Scale up connection pool

### Restart Procedure
```bash
docker-compose down postgres
docker-compose up -d postgres
# Verify backend reconnects automatically
```

## Critical Alert: Low Disk Space (<10%)

### Immediate Actions
1. [ ] Identify large files/logs
2. [ ] Archive logs to object storage
3. [ ] Delete old backups if necessary
4. [ ] Monitor closely

### Cleanup
```bash
# Clean old backups (keep last 7 days)
find /backups -name "*.dump" -mtime +7 -delete

# Clean old logs (keep last 30 days)
find /logs -name "*.log" -mtime +30 -delete
```
```

---

## 📊 IMPLEMENTATION CHECKLIST

### Week 1: Infrastructure Setup
- [ ] Create staging .env file
- [ ] Create staging docker-compose
- [ ] Clone production database
- [ ] Anonymize PII
- [ ] Test database integrity
- [ ] Create Nginx configuration

### Week 2: CI/CD Setup
- [ ] Create GitHub Actions workflow
- [ ] Add GitHub secrets
- [ ] Test build pipeline
- [ ] Test staging deployment
- [ ] Setup Docker registry
- [ ] Configure notifications (Slack)

### Week 3: Monitoring Setup
- [ ] Deploy Prometheus
- [ ] Deploy Grafana
- [ ] Create dashboards
- [ ] Setup AlertManager
- [ ] Configure alert rules
- [ ] Test alerts

### Week 4: Production Ready
- [ ] Create runbooks
- [ ] Train team
- [ ] Test rollback procedure
- [ ] Verify backups
- [ ] Load testing
- [ ] Final sign-off

---

**Status**: Ready for implementation  
**Est. Total Effort**: 10-14 hours  
**Estimated Cost**: Minimal (uses existing infrastructure)

