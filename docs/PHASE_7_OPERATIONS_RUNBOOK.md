# 📖 OPERATIONS RUNBOOK - DAILY PROCEDURES
**Quty Karunia ERP - Production Operations Guide**

---

## 📋 TABLE OF CONTENTS
1. Daily Operations
2. Service Health Checks
3. Backup Procedures
4. Performance Monitoring
5. Common Issues & Resolution
6. Emergency Procedures

---

## 🌅 DAILY STARTUP PROCEDURE

**Time**: 06:00 AM daily (Before business hours)  
**Duration**: 15 minutes  
**Owner**: Operations Team

### **Step 1: SSH Access to Production Server**

```bash
# Connect to production server
ssh -i ~/.ssh/erp_prod.key admin@erp-prod.yourdomain.com

# Verify you're on production (should show production hostname)
hostname

# Go to project directory
cd /opt/erp
```

### **Step 2: Verify All Services Are Running**

```bash
# Check all services
docker-compose -f docker-compose.production.yml ps

# Expected output:
# NAME                  STATUS              PORTS
# erp-postgres          Up (healthy)        5432/tcp
# erp-redis             Up (healthy)        6379/tcp
# erp-backend           Up (healthy)        8000/tcp
# erp-nginx             Up (healthy)        80/tcp, 443/tcp
# erp-prometheus        Up (healthy)        9090/tcp
# erp-grafana           Up (healthy)        3000/tcp
# erp-alertmanager      Up (healthy)        9093/tcp
# erp-elasticsearch     Up (healthy)        9200/tcp
# erp-logstash          Up (healthy)        5000/tcp
# erp-kibana            Up (healthy)        5601/tcp
```

### **Step 3: Check Service Logs for Errors**

```bash
# Check last 50 lines of each service for errors
docker-compose -f docker-compose.production.yml logs --tail=50 | grep -i error

# If errors found, investigate with:
docker-compose -f docker-compose.production.yml logs postgres
docker-compose -f docker-compose.production.yml logs backend
docker-compose -f docker-compose.production.yml logs nginx
```

### **Step 4: Verify Database Connectivity**

```bash
# Connect to PostgreSQL
psql -U postgres -h localhost -d erp_quty_karunia_prod

# Check status:
\dt  # List all tables
SELECT count(*) FROM products;  # Should return row count
\q   # Quit

# Expected: All tables present, data visible
```

### **Step 5: Test Critical API Endpoints**

```bash
# Health check endpoint
curl -k https://localhost/health

# Expected: {"status": "ok", "timestamp": "..."}

# Alternative if SSL cert issues:
curl -k https://erp-prod.yourdomain.com/health
```

### **Step 6: Verify Monitoring Stack**

```bash
# Prometheus metrics
curl -k https://localhost:9090/api/v1/query?query=up

# Grafana status (visual check)
# Open: https://erp-prod.yourdomain.com/grafana
# Dashboard should show all services UP

# Kibana logs check (visual check)
# Open: https://erp-prod.yourdomain.com/kibana
# Recent logs should be flowing in
```

### **Daily Startup Checklist**

- [ ] All 11 services running (`docker-compose ps` shows all "Up")
- [ ] No error logs in services
- [ ] Database connectivity verified
- [ ] API health endpoint responding
- [ ] Prometheus metrics flowing
- [ ] Grafana dashboards updating
- [ ] Kibana receiving logs

**If any item fails**: See "Common Issues & Resolution" section

---

## 🔍 SERVICE HEALTH MONITORING

### **Hourly Health Check (Automated)**

**These run automatically via Prometheus**. Monitor on Grafana:

```
Dashboard: System Overview
└─ Check every hour: 09:00, 10:00, 11:00, ... 17:00

Key Metrics:
  ✓ Database connections < 150 (max 200)
  ✓ API response time p95 < 1 second
  ✓ CPU usage < 70%
  ✓ Memory usage < 80%
  ✓ Disk usage < 85%
  ✓ Redis memory < 512MB
  ✓ Error rate < 1%
```

### **Manual Health Check (If Alerts Trigger)**

```bash
# Check PostgreSQL
docker-compose exec postgres pg_isready

# Check Redis
docker-compose exec redis redis-cli ping
# Expected: PONG

# Check FastAPI
curl https://erp.yourdomain.com/health

# Check Nginx
docker-compose logs nginx | tail -20

# Check specific endpoint latency
time curl https://erp.yourdomain.com/api/v1/auth/me \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 💾 BACKUP PROCEDURES

### **Automatic Daily Backup** (No action needed)

**Time**: 02:00 AM daily  
**Duration**: 15-30 minutes  
**Retention**: 7-day rolling backup

```
Backup Location: /backups/erp-postgres/
Naming: erp_backup_YYYY-MM-DD_HH00.sql.gz

Example: erp_backup_2026-01-19_0200.sql.gz
```

### **Verify Backup Completion**

```bash
# Check backup directory
ls -lh /backups/erp-postgres/ | tail -5

# Expected output:
# -rw-r--r-- 1 backup backup 125M Jan 19 02:15 erp_backup_2026-01-19_0200.sql.gz

# Check backup age
find /backups/erp-postgres -name "*.sql.gz" -mtime +1 | wc -l

# Should be 0 (no backups older than 24h that we haven't cleaned up)
```

### **Manual Backup (If Needed)**

```bash
# Create manual backup
bash /opt/erp/deploy.sh backup

# Verify
ls -lh /backups/erp-postgres/ | tail -1

# Output should show fresh backup
```

### **Restore from Backup** (Emergency Procedure)

```bash
# Stop the backend to release DB connections
docker-compose -f docker-compose.production.yml stop backend

# List available backups
ls -lh /backups/erp-postgres/

# Restore from specific backup (example with date)
BACKUP_FILE="/backups/erp-postgres/erp_backup_2026-01-19_0200.sql.gz"

# Restore
zcat "$BACKUP_FILE" | \
  docker-compose exec -T postgres psql -U postgres

# Restart backend
docker-compose -f docker-compose.production.yml start backend

# Verify restoration
docker-compose -f docker-compose.production.yml ps backend
# Should show: Up (healthy)
```

---

## 📊 PERFORMANCE MONITORING

### **Daily Performance Review** (08:00 AM)

Open Grafana dashboard: `https://erp.yourdomain.com/grafana`

**Monitor these dashboards** (in order):

#### 1. System Overview Dashboard
```
Key Metrics to Check:
┌─ CPU Usage: Should be < 50% during normal hours
├─ Memory Usage: Should be < 70%
├─ Disk Usage: Should be < 80%
├─ Network I/O: Normal throughput visible
└─ Load Average: Should correlate with user count
```

#### 2. API Performance Dashboard
```
Key Metrics to Check:
┌─ Request Rate: Check for traffic patterns
├─ Response Time (p95): Should be < 1 second
├─ Error Rate: Should be near 0%
├─ Successful Requests: Monitor for spikes/drops
└─ Top Endpoints: Identify heavy users
```

#### 3. Database Health Dashboard
```
Key Metrics to Check:
┌─ Connection Count: Should be < 150 (max 200)
├─ Slow Query Count: Should be near 0
├─ Cache Hit Rate: Should be > 95%
├─ Transaction Rate: Monitor for patterns
└─ Disk Space: Should have > 100 GB free
```

#### 4. QT-09 Protocol Dashboard
```
Key Metrics to Check:
┌─ Line Clearance Checks: All passing
├─ Transfer Handshakes: 100% success rate
├─ Segregation Violations: 0 recorded
└─ Protocol Errors: 0 recorded
```

#### 5. Quality Control Dashboard
```
Key Metrics to Check:
┌─ Metal Detector Status: Operational
├─ QC Pass Rate: Target 98%+
├─ Defect Rate: Track trends
└─ QC Response Time: < 30 seconds
```

### **Weekly Performance Report** (Friday 17:00)

```bash
# Generate performance report from logs
curl -X POST https://erp.yourdomain.com/admin/reports/performance \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "start_date": "2026-01-13",
    "end_date": "2026-01-19",
    "include": ["response_times", "error_rates", "usage_patterns"]
  }'

# Save report for stakeholder review
# Email to: management@qutykarunia.com
# Subject: ERP Weekly Performance Report - Week of Jan 13-19
```

---

## 🔧 COMMON ISSUES & RESOLUTION

### **Issue 1: Database Connection Pool Exhausted**

**Symptoms**:
- API returns "Connection pool exhausted" errors
- Response times slow dramatically
- Logs show: `sqlalchemy.pool.QueuePool`

**Resolution** (5 minutes):

```bash
# Step 1: Check current connections
psql -U postgres -h localhost -d erp_quty_karunia_prod -c \
  "SELECT datname, count(*) FROM pg_stat_activity GROUP BY datname;"

# Step 2: Kill idle connections if > 150
psql -U postgres -h localhost -d erp_quty_karunia_prod -c \
  "SELECT pg_terminate_backend(pid) FROM pg_stat_activity
   WHERE datname = 'erp_quty_karunia_prod'
   AND query_start < now() - interval '30 minutes'
   AND query NOT LIKE 'autovacuum%';"

# Step 3: Restart backend container to reset pool
docker-compose restart backend

# Step 4: Monitor
curl https://erp.yourdomain.com/health

# If issue persists, escalate to Senior Developer
```

### **Issue 2: High API Response Time (> 1 second)**

**Symptoms**:
- Users report slowness
- Grafana shows p95 latency spike
- Logs show slow queries

**Resolution** (10 minutes):

```bash
# Step 1: Identify slow queries
psql -U postgres -h localhost -d erp_quty_karunia_prod -c \
  "SELECT * FROM v_slow_queries LIMIT 10;"

# Step 2: Check top endpoints by latency
curl -s 'http://prometheus:9090/api/v1/query' \
  --data-urlencode 'query=topk(5, rate(http_request_duration_seconds_sum[5m]))' \
  | jq '.data.result'

# Step 3: If database query is slow:
# - Run EXPLAIN ANALYZE on that query
# - Check if missing index
# - Contact Senior Developer

# Step 4: If Redis is slow:
docker-compose exec redis redis-cli info memory
# Should show < 500MB used

# Step 5: Restart if necessary
docker-compose restart backend
# Wait 30 seconds then verify
curl https://erp.yourdomain.com/health
```

### **Issue 3: PostgreSQL Out of Disk Space**

**Symptoms**:
- Database inserts fail
- Logs show: "no space left on device"
- Grafana disk usage at 100%

**Resolution** (15 minutes):

```bash
# Step 1: Check disk usage
df -h /

# Step 2: Clean up backups (keep last 3 only)
ls -1t /backups/erp-postgres/*.sql.gz | tail -n +4 | xargs rm

# Step 3: Clean up logs (if taking space)
docker-compose exec postgres psql -U postgres -d erp_quty_karunia_prod -c \
  "VACUUM ANALYZE;"

# Step 4: Archive old logs
docker-compose logs --tail 10000 > /archives/logs_backup_$(date +%Y%m%d).txt
docker container prune -f
docker image prune -f

# Step 5: Verify
df -h /
# Should show > 100GB free

# If still issues:
# - Contact DevOps to expand disk (LVM)
# - Or move backups to external storage
```

### **Issue 4: Elasticsearch Cannot Ingest Logs**

**Symptoms**:
- Kibana shows no recent logs
- Logstash errors in docker logs
- Elasticsearch down or full

**Resolution** (10 minutes):

```bash
# Step 1: Check Elasticsearch status
curl -X GET "localhost:9200/_cluster/health"

# Expected: "status":"green" or "yellow"

# Step 2: If red, check indices
curl -X GET "localhost:9200/_cat/indices"

# Step 3: Delete old indices (keep last 30 days)
curl -X DELETE "localhost:9200/erp-*" \
  -d '{"query": {"range": {"@timestamp": {"lt": "now-30d"}}}}'

# Step 4: Restart Logstash
docker-compose restart logstash

# Step 5: Verify logs flowing
curl -X GET "localhost:9200/erp-*/_count"
# Should show count > 0

# Step 6: Monitor Kibana
# Open: https://erp.yourdomain.com/kibana
# Should show recent logs flowing in
```

### **Issue 5: Alert Storm (Too Many Alerts)**

**Symptoms**:
- Slack flooded with alerts
- Alertmanager showing 50+ grouped alerts
- Cannot identify real issues

**Resolution** (10 minutes):

```bash
# Step 1: Check current alerts
curl -s http://localhost:9093/api/v1/alerts | jq '.data | length'

# Step 2: Silence noisy alert group (30 min)
curl -X POST http://localhost:9093/api/v1/alerts/groups/silence \
  -d '{
    "matchers": [
      {"name": "alertname", "value": "HighCPU", "isRegex": false}
    ],
    "duration": "30m",
    "createdBy": "ops"
  }'

# Step 3: Investigate root cause
# - Check what's causing alert
# - Optimize if possible
# - Remove Silence after fix

# Step 4: Adjust threshold if needed
# Edit: alert_rules.yml
# Restart: docker-compose restart prometheus
```

### **Issue 6: API Container Crashes**

**Symptoms**:
- Backend container keeps restarting
- Users cannot access system
- Logs show: "CrashLoopBackOff"

**Resolution** (Emergency - 5 minutes):

```bash
# Step 1: Check logs
docker-compose logs backend --tail 100

# Step 2: If database connection issue:
# - Verify database is running
docker-compose ps postgres

# Step 3: If environment variable issue:
# - Check .env.production file
cat .env.production | grep -i database_url

# Step 4: Manual restart
docker-compose down backend
sleep 5
docker-compose up -d backend

# Step 5: Monitor startup
watch docker-compose ps backend

# Expected: Status changes from "Restarting" to "Up (healthy)"

# Step 6: If still crashing:
# ESCALATE TO SENIOR DEVELOPER IMMEDIATELY
# Provide: docker-compose logs backend (last 200 lines)
```

---

## 🚨 EMERGENCY PROCEDURES

### **System Complete Outage**

**Response Time**: Immediate  
**Communication**: Slack #erp-emergency

```
Step 1: Notify all stakeholders (2 min)
├─ Slack: #erp-emergency
├─ Email: management@qutykarunia.com
└─ Message: "System outage detected at HH:MM. Investigating..."

Step 2: Attempt diagnosis (5 min)
├─ docker-compose ps
├─ docker-compose logs (all services)
└─ Check server resources (CPU, memory, disk)

Step 3: Attempt recovery (10 min)
├─ docker-compose restart
├─ If persists: docker-compose down && docker-compose up
└─ Monitor: docker-compose ps (all should be Up)

Step 4: If recovery fails (> 10 min)
├─ Escalate to Senior Developer
├─ Prepare to execute rollback
└─ Notify users of ETA

Step 5: Root cause analysis (After recovery)
├─ Check logs for errors
├─ Identify what caused outage
└─ Implement fix + testing
```

### **Data Corruption Detected**

**Response Time**: Immediate  
**Data Loss Risk**: Must prevent

```
Step 1: STOP all writes (2 min)
├─ docker-compose pause backend
└─ Message users: "System in maintenance"

Step 2: Backup current state (5 min)
├─ bash deploy.sh backup
└─ Verify: ls -lh /backups/erp-postgres/

Step 3: Identify extent of corruption (10 min)
├─ Connect to DB
├─ Run integrity checks
└─ Check: SELECT * FROM products WHERE id IS NULL

Step 4: Restore from clean backup (30 min)
├─ Identify last good backup
├─ Restore: See "Restore from Backup" section above
└─ Verify: SELECT count(*) FROM products

Step 5: Resume operations (5 min)
├─ docker-compose unpause backend
├─ Run smoke tests
└─ Notify users: "System restored"

Step 6: Investigation (Next day)
├─ Find root cause of corruption
├─ Implement preventive measures
└─ Update runbook
```

---

## 📞 ESCALATION CONTACTS

**For 24/7 Support**:

| Severity | Situation | Contact | Response |
|----------|-----------|---------|----------|
| **P1** | System down | On-Call Senior Dev | 5 min |
| **P1** | Data at risk | Senior Dev + DBA | 5 min |
| **P2** | API slow (>5s) | Support + Senior Dev | 15 min |
| **P2** | High error rate | Senior Dev | 15 min |
| **P3** | Performance issue | Support | 30 min |
| **P3** | Single user issue | Support | 1 hour |

**Slack Channel**: #erp-support  
**Email**: erp-support@qutykarunia.com  
**On-Call**: [Insert phone number]

---

**Version**: 1.0 | **Last Updated**: January 19, 2026 | **Next Review**: Weekly
