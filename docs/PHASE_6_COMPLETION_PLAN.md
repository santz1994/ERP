# 🚀 PHASE 6 COMPLETION PLAN
**Quty Karunia ERP - Production Deployment (Remaining 25%)**

**Current Status**: 75% COMPLETE | **Target**: 100% by EOD  
**Last Updated**: January 19, 2026 - Session 2  
**Developer**: Daniel (Senior IT Developer)

---

## 📊 PHASE 6 PROGRESS BREAKDOWN

```
████████████████████░░░░░░░░░░░░ 75% Complete

✅ COMPLETED (75%)
  ✓ Docker infrastructure (8 services defined)
  ✓ Security environment setup (.env template)
  ✓ Nginx reverse proxy configuration
  ✓ Prometheus & Grafana setup
  ✓ Alert rules definition (15+ rules)
  ✓ Monitoring dashboards (5 pre-configured)
  ✓ Backup script templates
  ✓ CI/CD GitHub Actions template
  ✓ Deployment checklist & troubleshooting

🔴 REMAINING (25%)
  ⏳ SSL/TLS Certificate Setup (0%)
  ⏳ CI/CD Pipeline Activation (0%)
  ⏳ Production Database Optimization (50%)
  ⏳ Log Aggregation Setup (0%)
  ⏳ Load Testing & Capacity Planning (0%)
  ⏳ Production Secrets Management (50%)
```

---

## 🎯 REMAINING TASKS (Detailed)

### **TASK 1: SSL/TLS Certificate Setup** (Estimated: 30 min)

**Status**: 🔴 NOT STARTED

**Objective**: Enable HTTPS on production server with automatic certificate renewal

**Steps**:

1. **Install Certbot Container**
   ```bash
   # Add certbot service to docker-compose.yml
   certbot:
     image: certbot/certbot
     volumes:
       - ./certbot/conf:/etc/letsencrypt:rw
       - ./certbot/www:/var/www/certbot:rw
     entrypoint: /bin/sh -c 'trap exit TERM; while :; do certbot renew --webroot -w /var/www/certbot; sleep 12h & wait $${!}; done;'
   ```

2. **Generate Initial Certificate**
   ```bash
   docker-compose run --rm certbot certonly --standalone \
     -d erp.qutykarunia.com \
     --email admin@qutykarunia.com \
     --agree-tos \
     --non-interactive
   ```

3. **Update nginx.conf** with certificate paths
   ```nginx
   ssl_certificate /etc/letsencrypt/live/erp.qutykarunia.com/fullchain.pem;
   ssl_certificate_key /etc/letsencrypt/live/erp.qutykarunia.com/privkey.pem;
   ```

4. **Test HTTPS**
   ```bash
   curl -k https://localhost/api/v1/auth/me
   ```

**Deliverables**:
- [ ] SSL certificate installed
- [ ] HTTPS working on port 443
- [ ] HTTP redirects to HTTPS
- [ ] Certificate auto-renewal configured

---

### **TASK 2: CI/CD Pipeline Activation** (Estimated: 45 min)

**Status**: 🔴 NOT STARTED

**Objective**: Automated testing, building, and deployment on every push to main

**Prerequisites**:
- GitHub repository (assumes already created)
- Docker Hub account
- SSH access to production server

**Steps**:

1. **Create GitHub Secrets**
   ```
   Settings → Secrets and variables → Actions
   
   Add secrets:
   - DOCKER_USER: docker username
   - DOCKER_PASSWORD: docker access token
   - PROD_HOST: production server IP/domain
   - PROD_USER: SSH username
   - DEPLOY_KEY: SSH private key
   ```

2. **Create Workflow File**
   
   Location: `.github/workflows/deploy.yml`
   
   Already documented in PHASE_6_DEPLOYMENT.md - Copy and customize:
   ```yaml
   # Test → Build → Deploy pipeline
   # See PHASE_6_DEPLOYMENT.md lines 400-500
   ```

3. **Setup Docker Registry**
   ```bash
   # Create docker-compose.push configuration
   docker-compose -f docker-compose.production.yml push
   ```

4. **Verify Workflow**
   ```bash
   # Push to main branch and monitor GitHub Actions tab
   git push origin main
   
   # Check Actions tab: https://github.com/qutykarunia/erp/actions
   ```

**Deliverables**:
- [ ] GitHub Actions workflow created
- [ ] Docker images auto-building
- [ ] Tests running on every push
- [ ] Auto-deployment to production on success

---

### **TASK 3: Production Database Optimization** (Estimated: 60 min)

**Status**: 🟡 PARTIAL (50%)

**Objective**: Ensure database performs optimally under production load

**Steps**:

1. **Add Database Indexes** (Currently 70% - need to complete)
   ```sql
   -- High-priority indexes for QT-09 protocol
   CREATE INDEX idx_transfer_logs_status ON transfer_logs(status, created_at DESC);
   CREATE INDEX idx_line_occupancy_dept ON line_occupancy(to_dept, article_id);
   CREATE INDEX idx_stock_quants_product_location ON stock_quants(product_id, location_id);
   
   -- Quality control indexes
   CREATE INDEX idx_qc_inspections_batch ON qc_inspections(batch_number, created_at DESC);
   CREATE INDEX idx_metal_detector_results ON qc_lab_tests(test_type, test_result) WHERE test_type = 'Metal Detector';
   
   -- Manufacturing order performance
   CREATE INDEX idx_manufacturing_orders_state ON manufacturing_orders(state, created_at DESC);
   CREATE INDEX idx_work_orders_department_status ON work_orders(department, status);
   ```

2. **Setup Connection Pooling**
   ```python
   # In app/core/database.py
   engine = create_engine(
       DATABASE_URL,
       poolclass=QueuePool,
       pool_size=20,
       max_overflow=40,
       pool_pre_ping=True,
       pool_recycle=3600,
   )
   ```

3. **Enable Query Logging** for monitoring
   ```python
   # In config.py
   SQLALCHEMY_ECHO = False  # Production
   SQLALCHEMY_ECHO_POOL = True  # Connection pool logging
   ```

4. **Performance Testing**
   ```bash
   # Run PostgreSQL ANALYZE
   docker-compose exec postgres psql -U postgres -d erp_quty_karunia_production -c "ANALYZE;"
   
   # Check query plans
   EXPLAIN ANALYZE SELECT * FROM transfer_logs WHERE status = 'LOCKED' LIMIT 10;
   ```

**Deliverables**:
- [ ] All indexes created (8-10 indexes)
- [ ] Connection pooling configured
- [ ] Query performance optimized
- [ ] Performance baseline documented

---

### **TASK 4: Log Aggregation Setup** (Estimated: 40 min)

**Status**: 🔴 NOT STARTED

**Objective**: Centralized logging for all services (FastAPI, PostgreSQL, nginx)

**Steps**:

1. **Add ELK Stack Services**
   
   Update `docker-compose.yml`:
   ```yaml
   elasticsearch:
     image: docker.elastic.co/elasticsearch/elasticsearch:8.0.0
     environment:
       - discovery.type=single-node
       - "ES_JAVA_OPTS=-Xms512m -Xmx512m"
     ports:
       - "9200:9200"
     volumes:
       - elasticsearch_data:/usr/share/elasticsearch/data

   logstash:
     image: docker.elastic.co/logstash/logstash:8.0.0
     ports:
       - "5000:5000"
     volumes:
       - ./logstash.conf:/usr/share/logstash/pipeline/logstash.conf

   kibana:
     image: docker.elastic.co/kibana/kibana:8.0.0
     ports:
       - "5601:5601"
   ```

2. **Configure Application Logging**
   ```python
   # In app/core/config.py
   import logging
   
   # Send FastAPI logs to Logstash
   handler = logging.StreamHandler()
   handler.setFormatter(logging.JSONFormatter())
   logging.getLogger("uvicorn").addHandler(handler)
   ```

3. **Setup Log Pipeline** (logstash.conf)
   ```
   input {
     tcp {
       port => 5000
       codec => json
     }
   }
   
   filter {
     mutate {
       add_field => { "[@metadata][index_name]" => "erp-%{+YYYY.MM.dd}" }
     }
   }
   
   output {
     elasticsearch {
       hosts => ["elasticsearch:9200"]
       index => "%{[@metadata][index_name]}"
     }
   }
   ```

4. **Create Kibana Dashboards**
   ```bash
   # Access Kibana
   # http://localhost:5601
   
   # Create index pattern: erp-*
   # Create visualizations for:
   # - API requests per second
   # - Error rates by endpoint
   # - Database query times
   # - Authentication failures
   ```

**Deliverables**:
- [ ] Elasticsearch running
- [ ] Logstash pipeline configured
- [ ] FastAPI logs flowing to ELK
- [ ] Kibana dashboards created

---

### **TASK 5: Load Testing & Capacity Planning** (Estimated: 90 min)

**Status**: 🔴 NOT STARTED

**Objective**: Identify performance bottlenecks and capacity limits

**Steps**:

1. **Install Load Testing Tool**
   ```bash
   pip install locust pytest-benchmark
   ```

2. **Create Load Test Script** (locustfile.py)
   ```python
   from locust import HttpUser, task, between
   
   class ProductionUser(HttpUser):
       wait_time = between(1, 3)
       token = None
       
       def on_start(self):
           # Login
           response = self.client.post("/api/v1/auth/login", json={
               "email": "operator@qutykarunia.com",
               "password": "test_password"
           })
           self.token = response.json()["access_token"]
       
       @task(3)
       def get_stock(self):
           self.client.get("/api/v1/warehouse/stock/1", 
               headers={"Authorization": f"Bearer {self.token}"})
       
       @task(2)
       def create_transfer(self):
           self.client.post("/api/v1/warehouse/transfer",
               json={"from_dept": "CUTTING", "to_dept": "SEWING"},
               headers={"Authorization": f"Bearer {self.token}"})
       
       @task(1)
       def check_mo_status(self):
           self.client.get("/api/v1/ppic/manufacturing-orders",
               headers={"Authorization": f"Bearer {self.token}"})
   ```

3. **Run Load Test**
   ```bash
   # Test with 100 concurrent users
   locust -f locustfile.py --host=http://localhost:8000 \
     --users 100 --spawn-rate 10 --run-time 5m
   ```

4. **Analyze Results**
   ```
   Expected Metrics:
   - Response time p95: < 500ms
   - Error rate: < 1%
   - Throughput: > 500 req/s
   ```

5. **Database Capacity Test**
   ```bash
   # Simulate 1000 concurrent database connections
   pgbench -c 100 -j 10 -T 60 erp_quty_karunia_production
   ```

**Deliverables**:
- [ ] Load test script created
- [ ] 100-user concurrent test passing
- [ ] Performance bottlenecks identified
- [ ] Capacity plan documented

---

### **TASK 6: Production Secrets Management** (Estimated: 30 min)

**Status**: 🟡 PARTIAL (50%)

**Objective**: Secure credential storage without exposing secrets

**Steps**:

1. **Setup HashiCorp Vault** (Alternative: AWS Secrets Manager)
   ```bash
   # Docker service
   vault:
     image: vault:latest
     ports:
       - "8200:8200"
     environment:
       - VAULT_DEV_ROOT_TOKEN_ID=myroot
       - VAULT_DEV_LISTEN_ADDRESS=0.0.0.0:8200
     volumes:
       - vault_data:/vault/data
   ```

2. **Store Production Secrets**
   ```bash
   # Initialize Vault
   vault kv put secret/erp/production \
     DB_PASSWORD="$(openssl rand -base64 32)" \
     JWT_SECRET_KEY="$(openssl rand -base64 64)" \
     API_KEY="$(openssl rand -hex 32)"
   
   # Retrieve in application
   client = hvac.Client(url='http://vault:8200', token='myroot')
   secrets = client.secrets.kv.read_secret_version(path='erp/production')
   ```

3. **Environment-Specific Configs**
   ```
   .env.production       (Production secrets - NEVER COMMIT)
   .env.staging         (Staging secrets - NEVER COMMIT)
   .env.development     (Dev defaults - OK to commit)
   .env.example         (Template - OK to commit)
   ```

4. **Rotate Secrets Quarterly**
   ```bash
   # Schedule in cron
   0 0 1 1,4,7,10 * /scripts/rotate-secrets.sh
   ```

**Deliverables**:
- [ ] Vault/Secrets Manager setup
- [ ] Production secrets stored securely
- [ ] No secrets in git history
- [ ] Secret rotation policy documented

---

## 📋 CONSOLIDATED COMPLETION CHECKLIST

### **Pre-Deployment Verification** (ALL PASSING ✅)
- [x] All 410 tests passing (5 test suites)
- [x] Code compiled without errors
- [x] All 31 production endpoints functional
- [x] QT-09 protocol fully integrated
- [x] Metal detector critical QC ready
- [x] Database schema migrated
- [x] Docker images built successfully

### **Phase 6 - Remaining Deployment Tasks**
- [ ] SSL/TLS certificates installed
- [ ] HTTPS working on port 443
- [ ] GitHub Actions CI/CD pipeline active
- [ ] Auto-deployment to production working
- [ ] Database indexes optimized (8+ indexes)
- [ ] Connection pooling configured
- [ ] ELK log aggregation running
- [ ] Kibana dashboards created
- [ ] Load tests passing (100+ concurrent users)
- [ ] Secrets management system configured
- [ ] Backup jobs running daily
- [ ] Prometheus metrics scraping
- [ ] Grafana dashboards populated
- [ ] Alert rules active

### **Production Readiness Sign-Off**
- [ ] All services health check passing
- [ ] Performance baseline established
- [ ] Incident response plan ready
- [ ] On-call rotation configured
- [ ] Documentation complete
- [ ] Team trained on production operations

---

## 🔄 EXECUTION PLAN - THIS SESSION

### **Timeline: 4-5 Hours**

**Hour 1**: SSL/TLS Setup + CI/CD Activation (75 min)
- [ ] Certbot container configured
- [ ] SSL certificates generated
- [ ] HTTPS working
- [ ] GitHub Actions workflow created
- [ ] Docker registry connected

**Hour 2**: Database Optimization + Log Aggregation (100 min)
- [ ] All database indexes created
- [ ] Connection pooling configured
- [ ] ELK stack services added
- [ ] Log pipeline configured
- [ ] Kibana dashboards created

**Hour 3**: Load Testing + Secrets Management (70 min)
- [ ] Load test script created
- [ ] 100-user test executed
- [ ] Performance baseline documented
- [ ] Vault/Secrets Manager configured
- [ ] Secrets rotated and secured

**Hour 4**: Final Verification & Documentation (30 min)
- [ ] All 6 remaining tasks verified
- [ ] Documentation updated
- [ ] Production deployment checklist signed off
- [ ] Team readiness confirmed

---

## 🎉 POST-COMPLETION STATE

**Target Status**: ✅ Phase 6 100% COMPLETE

```
████████████████████████████████ 100% Complete

Phase 6 Deployment (100%) ✅ COMPLETE
  ✅ Docker infrastructure
  ✅ SSL/TLS certificates
  ✅ CI/CD pipeline
  ✅ Database optimization
  ✅ Log aggregation
  ✅ Load testing
  ✅ Secrets management
  ✅ Monitoring & alerting
  ✅ Backup strategy

Overall Project Status: 95% COMPLETE
Remaining: Phase 7 (Go-Live & Operations) - 5%
```

---

## 🚀 PHASE 7 PREVIEW (Next)

**Phase 7: Production Go-Live & Operations** (Week 11-12)

- Production environment cutover
- Data migration from legacy system
- User acceptance testing (UAT)
- Runbook documentation
- 24/7 production support setup
- Performance monitoring & optimization
- Incident response procedures

---

**Document Status**: In Progress → Ready for Execution  
**Next Action**: Begin Task 1 - SSL/TLS Certificate Setup  
**Estimated Completion**: 4-5 hours  

Daniel Rizaldy  
Senior IT Developer  
January 19, 2026

