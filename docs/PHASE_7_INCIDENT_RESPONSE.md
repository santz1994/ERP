# 🚨 INCIDENT RESPONSE RUNBOOK
**Quty Karunia ERP - Production Incident Management**

---

## 📋 INCIDENT SEVERITY LEVELS

### **Severity Classification**

| Level | Name | Impact | Response | Escalation |
|-------|------|--------|----------|------------|
| **P1** | CRITICAL | System down, data loss risk | 5 minutes | Immediate |
| **P2** | HIGH | Major feature broken, 50+ users affected | 15 minutes | Within 15 min |
| **P3** | MEDIUM | Feature degraded, single dept affected | 30 minutes | Within 1 hour |
| **P4** | LOW | Minor issue, workaround available | 1 hour | Within 8 hours |

---

## 🎯 INCIDENT RESPONSE FLOW

```
Incident Detected
        ↓
        ├─→ Identify Severity (P1-P4)
        ├─→ Open Incident Ticket
        ├─→ Notify Stakeholders
        ├─→ Acknowledge Receipt
        ├─→ Investigate Root Cause
        ├─→ Implement Fix
        ├─→ Verify Resolution
        ├─→ Communicate Status
        ├─→ Post-Incident Review
        └─→ Update Documentation
```

---

## 🔴 P1: CRITICAL INCIDENTS (System Down)

**Response Time**: 5 minutes  
**Goal**: Restore service ASAP

### **Step 1: Immediate Assessment (2 min)**

```bash
# Quick status check
docker-compose ps

# Identify which service(s) are down
docker-compose logs --tail 50 backend | tail -20
docker-compose logs --tail 50 postgres | tail -20
docker-compose logs --tail 50 nginx | tail -20
```

**Possible Scenarios**:

#### **Scenario A: API Backend Down**
```bash
# Check backend container
docker-compose ps backend
# Status: "Exited" or "Restarting"

# View error logs
docker-compose logs backend --tail 200

# Action: Restart backend
docker-compose restart backend

# Verify: (wait 10 seconds)
docker-compose ps backend
# Expected: "Up (healthy)"

# Test endpoint
curl https://erp.yourdomain.com/health
```

#### **Scenario B: Database Down**
```bash
# Check PostgreSQL
docker-compose ps postgres
# Status: Should be "Up (healthy)"

# Try to connect
psql -U postgres -h localhost -d erp_quty_karunia_prod

# If connection refused:
docker-compose logs postgres --tail 50
# Check for: "FATAL", "OOM", "disk full"

# Restart database
docker-compose restart postgres
# WARNING: May take 30-60 seconds for recovery

# Verify
docker-compose ps postgres
# Expected: "Up (healthy)"

# If not recovering, check disk space
df -h /
# If < 10GB free, clean up or expand disk
```

#### **Scenario C: Nginx Reverse Proxy Down**
```bash
# Check nginx
docker-compose ps nginx
# Status: "Exited" or "Restarting"

# View error
docker-compose logs nginx --tail 50

# Check SSL certificate
ls -la /opt/erp/certs/
# Verify: live/yourdomain/fullchain.pem exists

# Restart nginx
docker-compose restart nginx

# Verify
docker-compose ps nginx
curl -kv https://erp.yourdomain.com/ | head -20
```

#### **Scenario D: Disk Full**
```bash
# Check space
df -h /

# If < 5% free:
# 1. Stop non-critical services
docker-compose stop alertmanager elasticsearch kibana

# 2. Clean Docker artifacts
docker container prune -f
docker image prune -f

# 3. Archive old logs
mkdir -p /archives/$(date +%Y%m%d)
find /var/lib/docker/containers -name "*.log" -mtime +7 -delete

# 4. Restart services
docker-compose restart alertmanager elasticsearch kibana

# 5. Verify space
df -h /
# Should show > 20% free
```

### **Step 2: Escalation (P1 Only - 3 min)**

```bash
# Immediately notify all stakeholders
# Slack: @channel in #erp-emergency
# Message:
# "🚨 CRITICAL P1: ERP System Down
#  - Detected: [TIME]
#  - Impact: Users cannot access system
#  - Status: Investigating [ISSUE]
#  - ETA to resolution: [TIME]"

# Email (if critical)
# To: management@qutykarunia.com
# Subject: URGENT: ERP System Outage

# Call on-call team (if not responding to Slack)
# Phone: [Emergency number]
```

### **Step 3: Recovery (P1 Only - < 15 min target)**

```bash
# If basic restart doesn't work, try full restart
docker-compose down
sleep 10
docker-compose up -d

# Monitor startup
watch docker-compose ps

# Wait for all services to be "Up (healthy)" (2-3 min)

# Run smoke tests
bash /opt/erp/deploy.sh health_check

# Expected output:
# ✓ PostgreSQL: OK
# ✓ Redis: OK  
# ✓ Backend: OK (Response time: XX ms)
# ✓ Prometheus: OK
```

### **Step 4: Status Updates (Every 5 min)**

```
Timeline Example:
14:32 - P1 Incident Detected: ERP Down
14:33 - Slack alert sent
14:34 - Diagnosis: Backend container not responding
14:35 - Action: Restarting backend service
14:37 - Verification: Services recovering
14:40 - RESOLVED: System back online
        → Update Slack: "✅ System restored. Investigation in progress"
```

### **Step 5: Post-Resolution (Within 1 hour)**

1. **Verify All Systems**
   ```bash
   # Full health check
   docker-compose ps
   curl https://erp.yourdomain.com/health
   ```

2. **Communicate Update**
   ```
   Slack Message:
   "✅ RESOLVED: ERP System Restored
    Duration: 8 minutes
    Root Cause: [Brief description]
    Preventive Measures: [What we're doing to prevent recurrence]
    Post-Incident Review: [Scheduled for tomorrow 10:00]"
   ```

3. **Collect Evidence**
   ```bash
   # Save all logs for analysis
   docker-compose logs > /archives/incident_$(date +%Y%m%d_%H%M%S).log
   
   # Document what happened
   # File: /archives/P1_incident_analysis_YYYYMMDD.txt
   ```

---

## 🟠 P2: HIGH PRIORITY INCIDENTS (Major Feature Broken)

**Response Time**: 15 minutes  
**Goal**: Restore feature or find workaround

### **Examples of P2 Incidents**
- All users in Cutting department cannot submit work orders
- Payment processing API returning errors (if applicable)
- Transfer protocol not accepting new transfers
- QC system cannot record test results

### **Diagnosis Steps**

```bash
# 1. Identify affected endpoint
# From user report: "Cannot create manufacturing order"

# 2. Test endpoint manually
curl -X GET https://erp.yourdomain.com/api/v1/ppic/manufacturing-orders \
  -H "Authorization: Bearer $TOKEN"

# Expected: 200 OK with data
# If error: Note the status code and message

# 3. Check backend logs for that specific endpoint
docker-compose logs backend | grep "manufacturing-order" | tail -20

# 4. Check database for issues
docker-compose exec postgres psql -U postgres -d erp_quty_karunia_prod
psql> SELECT COUNT(*) FROM manufacturing_orders;
psql> SELECT * FROM manufacturing_orders LIMIT 5;

# 5. If database query slow:
psql> EXPLAIN ANALYZE SELECT * FROM manufacturing_orders LIMIT 5;

# 6. Check if recent deployment caused it
cat /opt/erp/.git/logs/HEAD | tail -20
# Should show last deployment timestamp
```

### **Common P2 Issues & Fixes**

#### **Issue: API Returning 500 Error**
```bash
# Check for exceptions
docker-compose logs backend | grep -i "exception" | tail -10

# Common causes:
# - Database connection pool exhausted
# - Missing environment variable
# - SQL error in query

# Fix: Restart backend
docker-compose restart backend
```

#### **Issue: API Returning 403 Forbidden**
```bash
# User doesn't have permission

# Check:
# 1. Is user logged in?
curl https://erp.yourdomain.com/api/v1/auth/me \
  -H "Authorization: Bearer $TOKEN"

# 2. Does user have correct role?
psql -c "SELECT role FROM users WHERE username='username';"

# 3. Verify role has endpoint permission
# Contact Senior Developer to check RBAC rules

# Fix: Assign correct role to user
psql -c "UPDATE users SET role='PPIC_Manager' WHERE username='username';"
```

#### **Issue: Transfer Protocol Handshake Failing**
```bash
# Check QT-09 protocol logs
docker-compose logs backend | grep -i "qt-09" | tail -20

# Verify transfer_logs table
psql -c "SELECT * FROM transfer_logs ORDER BY created_at DESC LIMIT 5;"

# Check line occupancy
psql -c "SELECT * FROM line_occupancy WHERE status='LOCKED';"

# Possible fixes:
# 1. Clear stuck lock (if line clearance issue)
psql -c "UPDATE line_occupancy SET status='AVAILABLE' WHERE department='sewing' AND locked_at < now() - interval '1 hour';"

# 2. Restart affected service
docker-compose restart backend
```

### **Communication for P2**

```
Slack: #erp-support
"⚠️ P2: Cutting Department cannot submit work orders
 - Affected Users: All in Cutting dept (~20 users)
 - Impact: Cannot start production
 - Status: Investigating
 - ETA: 30 min"

(Update every 10 minutes)

"✅ RESOLVED: Work order submission restored
 Root Cause: Database connection pool exhausted
 Action: Restarted backend service
 Duration: 22 minutes"
```

---

## 🟡 P3: MEDIUM PRIORITY (Degraded Performance)

**Response Time**: 30 minutes  
**Goal**: Improve performance or provide workaround

### **Examples of P3 Incidents**
- API response time consistently > 5 seconds
- Specific endpoint slow (e.g., stock search)
- Memory usage climbing (possible memory leak)
- Query timeout errors occasionally

### **Performance Troubleshooting**

```bash
# 1. Identify slow endpoint
curl -w "@/tmp/curl-format.txt" \
  https://erp.yourdomain.com/api/v1/warehouse/stock/123 \
  -H "Authorization: Bearer $TOKEN"

# 2. Check Grafana for trends
# Open: https://erp.yourdomain.com/grafana
# Dashboard: API Performance
# Look for: Spike in response time

# 3. Check database query time
docker-compose exec postgres psql -U postgres -d erp_quty_karunia_prod

psql> SELECT query, calls, mean_time 
      FROM pg_stat_statements 
      WHERE mean_time > 1000 
      ORDER BY mean_time DESC 
      LIMIT 10;

# 4. If slow query identified, check query plan
psql> EXPLAIN ANALYZE [THE SLOW QUERY];

# 5. Check if missing index
# Run: database-optimization.sql
# File: /opt/erp/database-optimization.sql
psql -f /opt/erp/database-optimization.sql
```

### **Common P3 Fixes**

#### **High Memory Usage**
```bash
# Check container memory
docker stats erp-backend --no-stream

# If > 1GB:
# 1. Check for memory leak
docker-compose logs backend | grep -i "memory" | tail -20

# 2. Restart service
docker-compose restart backend

# 3. Monitor
watch docker stats erp-backend

# 4. If persists, escalate with memory dump
```

#### **High CPU Usage**
```bash
# Check CPU
top -p $(docker inspect -f '{{.State.Pid}}' erp-backend)

# If consistently > 80%:
# 1. Check for infinite loops
docker-compose logs backend | tail -100 | grep -v "INFO"

# 2. Check database locks
psql -c "SELECT * FROM pg_locks WHERE NOT granted;"

# 3. If found, kill blocking query
psql -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity 
         WHERE pid != pg_backend_pid() AND state = 'active';"

# 4. Restart backend
docker-compose restart backend
```

---

## 🟢 P4: LOW PRIORITY (Minor Issues)

**Response Time**: 1 hour  
**Goal**: Schedule fix, provide workaround

### **Examples of P4 Incidents**
- Typo in error message
- UI display issue
- Optional feature not working
- Documentation needs update

### **P4 Resolution**

```bash
# 1. Document the issue
cat > /opt/erp/issues/$(date +%Y%m%d)_issue.txt << EOF
Title: [Brief description]
Severity: P4
Reporter: [Name]
Date: [Date]
Description: [Details]
Workaround: [If available]
EOF

# 2. Create ticket in issue tracking system
# Assign to developer

# 3. Schedule for next maintenance window
# (Not urgent - can wait until next deployment)

# 4. No urgent communication needed
# (Can mention in weekly status if relevant)
```

---

## 📝 INCIDENT DOCUMENTATION TEMPLATE

**Create for every P1 or P2 incident within 24 hours**

```
FILE: /archives/INCIDENT_REPORT_[DATE]_[ID].md

# Incident Report

## Summary
- **Incident ID**: INC-20260119-001
- **Date/Time**: 2026-01-19 14:32 UTC
- **Duration**: 8 minutes (14:32 - 14:40)
- **Severity**: P1 (Critical)
- **Status**: RESOLVED

## Impact
- **Affected Users**: All (~500 users)
- **Affected System**: Entire ERP (Cutting, Sewing, Finishing modules)
- **Business Impact**: Production stopped for 8 minutes
- **Data Loss**: None
- **Customer Impact**: None (internal system)

## Root Cause
PostgreSQL connection pool exhausted due to long-running query in backup process.
Backup job didn't release connections properly.

## Timeline
- 14:32 - First error reports in Slack (#erp-support)
- 14:33 - On-call engineer paged
- 14:34 - Diagnosed: Backend unable to connect to database
- 14:35 - Restarted backend service
- 14:37 - Services recovering
- 14:40 - All services healthy, tests passing
- 14:50 - Root cause identified in logs

## Resolution
Restarted backend service to clear connection pool.

## Preventive Measures Implemented
1. Modified backup script to close connections after backup
2. Reduced connection timeout from 5min to 2min
3. Added alert for connection pool usage > 150

## Post-Incident Actions
- [x] Updated monitoring alert threshold
- [x] Modified backup script
- [x] Documented in runbook
- [ ] Team training on this scenario (scheduled for Friday)

## Lessons Learned
- Backup process needs better connection management
- Should add monitoring alert for connection pool exhaustion
- Team should have tested database recovery more thoroughly

## Sign-off
- Incident Commander: [Name]
- Senior Developer: [Name]
- Date Reviewed: [Date]
```

---

## 🎓 INCIDENT RESPONSE TRAINING

### **Monthly Drill Checklist**

```
□ First Tuesday of each month: 15:00 UTC

Scenario 1 (Every month):
  - API service crashes
  - Team must restart and verify
  - Target: 5 min resolution

Scenario 2 (Rotating):
  - Month 1: Database connection pool exhausted
  - Month 2: Disk full
  - Month 3: High memory usage
  - Month 4: SSL certificate expired
  - Month 5: Network connectivity issue

Scoring:
  - Time to detect: < 2 min = +2 points
  - Time to resolve: < 10 min = +2 points
  - Correct communication: +2 points
  - Proper documentation: +2 points
  - Total: 8 points per drill

Target: 6+ points (75%)
```

### **Team Responsibilities**

**Every team member should know**:
- [ ] How to SSH to production server
- [ ] How to check service status
- [ ] How to read Docker logs
- [ ] How to restart a service
- [ ] Who to call for help
- [ ] How to use Slack escalation

**Senior Developer should know**:
- [ ] How to debug application errors
- [ ] How to analyze slow queries
- [ ] How to perform database recovery
- [ ] How to execute rollback procedure
- [ ] Root cause analysis technique

**DevOps should know**:
- [ ] Full docker-compose restart
- [ ] SSH key rotation
- [ ] Certificate renewal
- [ ] Firewall rule changes
- [ ] Infrastructure scaling

---

## 📞 EMERGENCY CONTACTS

| Role | Name | Phone | Slack | Email |
|------|------|-------|-------|-------|
| **On-Call Eng** | [Name] | +62-XXX-XXXX | @daniel | daniel@quty.com |
| **Senior Dev** | Daniel | +62-XXX-XXXX | @daniel-dev | dev@quty.com |
| **DevOps Lead** | [Name] | +62-XXX-XXXX | @devops | ops@quty.com |
| **Manager** | [Name] | +62-XXX-XXXX | @manager | mgr@quty.com |

**Emergency Channel**: #erp-emergency (Slack)  
**24/7 Hotline**: [Insert number]

---

**Version**: 1.0 | **Last Updated**: January 19, 2026 | **Review Frequency**: Monthly
