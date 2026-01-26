# 📊 MONITORING & OBSERVABILITY STRATEGY

**Status**: Complete Strategy Document  
**Purpose**: Production-ready monitoring, logging, and alerting  
**Timeline**: Implementation in parallel with CI/CD  

---

## 1. OBSERVABILITY STACK ARCHITECTURE

```
┌─────────────────────────────────────────────────────────────┐
│                  OBSERVABILITY STACK (ELK+M)               │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  DATA COLLECTION LAYER                                      │
│  ├─ Application Metrics (Micrometer)                        │
│  ├─ System Metrics (Node Exporter)                          │
│  ├─ Database Metrics (Postgres Exporter)                    │
│  ├─ Logs (Logback → Logstash)                               │
│  └─ Traces (OpenTelemetry)                                  │
│                                                             │
│  TIME-SERIES DATABASE                                       │
│  ├─ Prometheus (metrics)                                    │
│  └─ InfluxDB (optional: high-cardinality metrics)           │
│                                                             │
│  LOG AGGREGATION                                            │
│  ├─ Elasticsearch (storage)                                 │
│  ├─ Logstash (processing)                                   │
│  └─ Filebeat (shipping)                                     │
│                                                             │
│  VISUALIZATION                                              │
│  ├─ Grafana (metrics dashboards)                            │
│  ├─ Kibana (log analysis)                                   │
│  └─ Jaeger (distributed tracing)                            │
│                                                             │
│  ALERTING & RESPONSE                                        │
│  ├─ AlertManager (alert routing)                            │
│  ├─ Slack (notifications)                                   │
│  ├─ PagerDuty (escalation)                                  │
│  └─ Incident.io (incident tracking)                         │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. METRICS INSTRUMENTATION

### 2.1 Backend Metrics (FastAPI)

```python
# File: erp-softtoys/app/monitoring/metrics.py

from prometheus_client import Counter, Histogram, Gauge
from functools import wraps
import time
from typing import Callable, Any

# Request metrics
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

REQUEST_DURATION = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency',
    ['method', 'endpoint'],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0)
)

# Business metrics
PRODUCTION_SPKS = Gauge(
    'production_spks_count',
    'Total number of SPK',
    ['status']  # PENDING, IN_PROGRESS, COMPLETED
)

DAILY_OUTPUT = Counter(
    'daily_output_total',
    'Total daily output',
    ['spk_id', 'date']
)

BARCODE_SCANS = Counter(
    'barcode_scans_total',
    'Total barcode scans',
    ['status']  # SUCCESS, FAILED, DUPLICATE
)

SYNC_OPERATIONS = Counter(
    'sync_operations_total',
    'Total sync operations',
    ['type', 'status']  # type: DAILY_INPUT, BARCODE, APPROVAL | status: SUCCESS, FAILED
)

# Database metrics
DB_QUERY_DURATION = Histogram(
    'database_query_duration_seconds',
    'Database query latency',
    ['operation', 'table'],
    buckets=(0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0)
)

DB_CONNECTION_POOL_SIZE = Gauge(
    'database_connection_pool_size',
    'Current connection pool size'
)

DB_CONNECTION_POOL_USED = Gauge(
    'database_connection_pool_used',
    'Used database connections'
)

# Cache metrics
CACHE_HITS = Counter(
    'cache_hits_total',
    'Cache hits',
    ['cache_name']
)

CACHE_MISSES = Counter(
    'cache_misses_total',
    'Cache misses',
    ['cache_name']
)

# Error metrics
ERRORS_TOTAL = Counter(
    'errors_total',
    'Total errors',
    ['error_type', 'endpoint']
)

# Helper decorator for automatic instrumentation
def track_metrics(endpoint: str):
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                REQUEST_COUNT.labels(
                    method='GET' if 'get' in func.__name__.lower() else 'POST',
                    endpoint=endpoint,
                    status=200
                ).inc()
                REQUEST_DURATION.labels(
                    method='GET' if 'get' in func.__name__.lower() else 'POST',
                    endpoint=endpoint
                ).observe(time.time() - start_time)
                return result
            except Exception as e:
                REQUEST_COUNT.labels(
                    method='GET' if 'get' in func.__name__.lower() else 'POST',
                    endpoint=endpoint,
                    status=500
                ).inc()
                ERRORS_TOTAL.labels(
                    error_type=type(e).__name__,
                    endpoint=endpoint
                ).inc()
                raise
        return wrapper
    return decorator

# Database tracking
class DatabaseMetricsMiddleware:
    def __init__(self, db):
        self.db = db
    
    async def __call__(self, scope, receive, send):
        if scope['type'] == 'http':
            with DB_QUERY_DURATION.labels(operation='query', table='all').time():
                # Query execution happens here
                pass
```

### 2.2 Android Metrics

```kotlin
// File: erp-ui/mobile/app/src/main/java/com/qutykarunia/erp/monitoring/CrashlyticsLogger.kt

import com.google.firebase.crashlytics.FirebaseCrashlytics
import com.google.firebase.analytics.FirebaseAnalytics
import androidx.annotation.StringRes

class CrashlyticsLogger(private val analytics: FirebaseAnalytics) {
    
    private val crashlytics = FirebaseCrashlytics.getInstance()
    
    // Track custom events
    fun logBarcodeScanned(
        barcodeId: String,
        articleCount: Int,
        timeMs: Long,
        success: Boolean
    ) {
        val bundle = Bundle().apply {
            putString("barcode_id", barcodeId)
            putInt("article_count", articleCount)
            putLong("scan_duration_ms", timeMs)
            putBoolean("success", success)
        }
        analytics.logEvent("barcode_scanned", bundle)
    }
    
    fun logDailyInputSaved(
        spkId: String,
        quantity: Int,
        offline: Boolean
    ) {
        val bundle = Bundle().apply {
            putString("spk_id", spkId)
            putInt("quantity", quantity)
            putBoolean("offline_mode", offline)
        }
        analytics.logEvent("daily_input_saved", bundle)
    }
    
    fun logSyncAttempt(
        itemType: String,
        itemCount: Int,
        success: Boolean,
        errorMessage: String? = null
    ) {
        val bundle = Bundle().apply {
            putString("item_type", itemType)
            putInt("item_count", itemCount)
            putBoolean("success", success)
            errorMessage?.let { putString("error", it) }
        }
        analytics.logEvent("sync_attempt", bundle)
    }
    
    fun logNetworkChange(newNetworkType: String) {
        analytics.logEvent("network_changed", Bundle().apply {
            putString("network_type", newNetworkType)
        })
    }
    
    fun logException(
        exception: Exception,
        context: String,
        isFatal: Boolean = false
    ) {
        crashlytics.setCustomKey("context", context)
        crashlytics.setCustomKey("timestamp", System.currentTimeMillis())
        
        if (isFatal) {
            crashlytics.recordException(exception)
        } else {
            crashlytics.log("Non-fatal: ${exception.message}")
        }
    }
    
    fun logPerformanceMetric(
        metric: String,
        durationMs: Long,
        metadata: Map<String, String> = emptyMap()
    ) {
        val bundle = Bundle().apply {
            putLong("duration_ms", durationMs)
            metadata.forEach { (k, v) -> putString(k, v) }
        }
        analytics.logEvent(metric, bundle)
    }
}
```

---

## 3. LOGGING STRATEGY

### 3.1 Log Levels & Format

```python
# File: erp-softtoys/app/logging_config.py

import logging
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
        }
        
        # Add exception info
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        # Add request context if available
        if hasattr(record, 'request_id'):
            log_data['request_id'] = record.request_id
        
        if hasattr(record, 'user_id'):
            log_data['user_id'] = record.user_id
        
        return json.dumps(log_data)

# Configure logging
logging.basicConfig(
    format='%(message)s',
    handlers=[
        # Console handler
        logging.StreamHandler(),
        # File handler (for Filebeat to pick up)
        logging.FileHandler('/var/log/erp/application.log')
    ]
)

# Set log levels per module
logging.getLogger('app.api').setLevel(logging.INFO)
logging.getLogger('app.database').setLevel(logging.DEBUG)
logging.getLogger('app.business_logic').setLevel(logging.INFO)
logging.getLogger('sqlalchemy').setLevel(logging.WARN)
```

### 3.2 Structured Logging Example

```python
# File: erp-softtoys/app/api/routers/daily_production.py

import logging
from app.monitoring.metrics import track_metrics

logger = logging.getLogger(__name__)

@router.post("/daily-input")
@track_metrics("/api/production/daily-input")
async def record_daily_input(request: DailyInputRequest, current_user: User):
    request_id = request.headers.get('X-Request-ID', 'unknown')
    
    logger.info(
        "Daily input received",
        extra={
            'request_id': request_id,
            'user_id': current_user.id,
            'spk_id': request.spk_id,
            'quantity': request.quantity,
            'timestamp': datetime.now().isoformat()
        }
    )
    
    try:
        # Process input
        result = await ProductionService.record_input(request)
        
        logger.info(
            "Daily input recorded successfully",
            extra={
                'request_id': request_id,
                'user_id': current_user.id,
                'spk_id': request.spk_id,
                'result_id': result.id,
                'duration_ms': int((datetime.now() - request.timestamp).total_seconds() * 1000)
            }
        )
        
        return result
        
    except ValidationError as e:
        logger.warning(
            "Daily input validation failed",
            extra={
                'request_id': request_id,
                'user_id': current_user.id,
                'spk_id': request.spk_id,
                'error': str(e)
            }
        )
        raise
    
    except DatabaseError as e:
        logger.error(
            "Database error recording daily input",
            extra={
                'request_id': request_id,
                'user_id': current_user.id,
                'spk_id': request.spk_id,
                'error': str(e),
                'error_type': type(e).__name__
            },
            exc_info=True
        )
        raise
```

---

## 4. GRAFANA DASHBOARDS

### 4.1 System Health Dashboard

```json
{
  "dashboard": {
    "title": "System Health Overview",
    "tags": ["production", "overview"],
    "timezone": "browser",
    "panels": [
      {
        "title": "API Response Time (p95)",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))"
          }
        ],
        "thresholds": "1,2"
      },
      {
        "title": "Error Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total{status=~\"5..\"}[5m])"
          }
        ],
        "thresholds": "0.005,0.01"
      },
      {
        "title": "Active Database Connections",
        "type": "gauge",
        "targets": [
          {
            "expr": "pg_stat_activity_count"
          }
        ],
        "thresholds": "50,80"
      },
      {
        "title": "Memory Usage",
        "type": "gauge",
        "targets": [
          {
            "expr": "1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)"
          }
        ],
        "thresholds": "0.7,0.85"
      },
      {
        "title": "Disk Usage",
        "type": "gauge",
        "targets": [
          {
            "expr": "1 - (node_filesystem_avail_bytes{mountpoint=\"/\"} / node_filesystem_size_bytes{mountpoint=\"/\"})"
          }
        ],
        "thresholds": "0.8,0.95"
      }
    ]
  }
}
```

### 4.2 Production Workflow Dashboard

```json
{
  "dashboard": {
    "title": "Production Workflow Metrics",
    "tags": ["business", "production-workflow"],
    "panels": [
      {
        "title": "Active SPKs by Status",
        "type": "pie",
        "targets": [
          {
            "expr": "production_spks_count"
          }
        ]
      },
      {
        "title": "Daily Output Trend",
        "type": "graph",
        "targets": [
          {
            "expr": "increase(daily_output_total[1d])"
          }
        ]
      },
      {
        "title": "Barcode Scan Success Rate",
        "type": "gauge",
        "targets": [
          {
            "expr": "rate(barcode_scans_total{status=\"SUCCESS\"}[1h]) / rate(barcode_scans_total[1h])"
          }
        ],
        "thresholds": "0.95,0.99"
      },
      {
        "title": "Sync Queue Size",
        "type": "graph",
        "targets": [
          {
            "expr": "sync_queue_size"
          }
        ],
        "alertThreshold": 1000
      },
      {
        "title": "Material Debt Status",
        "type": "table",
        "targets": [
          {
            "expr": "material_debt_status"
          }
        ]
      }
    ]
  }
}
```

### 4.3 Mobile Performance Dashboard

```json
{
  "dashboard": {
    "title": "Mobile App Performance",
    "tags": ["mobile", "performance"],
    "panels": [
      {
        "title": "App Crash Rate (24h)",
        "type": "stat",
        "targets": [
          {
            "expr": "rate(mobile_app_crashes_total[24h])"
          }
        ],
        "thresholds": "0.0001,0.001",
        "colors": ["green", "yellow", "red"]
      },
      {
        "title": "Active Sessions",
        "type": "stat",
        "targets": [
          {
            "expr": "mobile_app_active_sessions"
          }
        ]
      },
      {
        "title": "Barcode Scan Latency",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, barcode_scan_duration_ms_bucket)"
          }
        ],
        "yaxisLabel": "ms"
      },
      {
        "title": "Battery Usage per Hour",
        "type": "graph",
        "targets": [
          {
            "expr": "increase(battery_usage_percent[1h])"
          }
        ]
      },
      {
        "title": "Network Type Distribution",
        "type": "pie",
        "targets": [
          {
            "expr": "mobile_network_type_count"
          }
        ]
      }
    ]
  }
}
```

---

## 5. ALERT RULES

### 5.1 Critical Alerts

```yaml
# File: config/alert-rules-critical.yml

groups:
  - name: critical_alerts
    interval: 30s
    rules:
      # API is down
      - alert: APIServiceDown
        expr: up{job="backend"} == 0
        for: 2m
        labels:
          severity: critical
          team: backend
        annotations:
          summary: "API service is down"
          description: "Backend API has not been responding for 2+ minutes"
          dashboard: "https://grafana.internal/d/api-health"
          runbook: "https://wiki.internal/runbooks/api-down"

      # Database is down
      - alert: DatabaseDown
        expr: up{job="postgres"} == 0
        for: 2m
        labels:
          severity: critical
          team: database
        annotations:
          summary: "Database is down"
          description: "PostgreSQL is not responding"

      # High error rate (>5%)
      - alert: HighErrorRate
        expr: (rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m])) > 0.05
        for: 3m
        labels:
          severity: critical
          team: backend
        annotations:
          summary: "High error rate on {{ $labels.job }}"
          description: "Error rate is {{ $value | humanizePercentage }}"

      # Disk space critical
      - alert: DiskSpaceCritical
        expr: (1 - (node_filesystem_avail_bytes / node_filesystem_size_bytes)) > 0.9
        for: 5m
        labels:
          severity: critical
          team: infrastructure
        annotations:
          summary: "Disk space is critical (>90%)"
          description: "{{ $labels.device }} is {{ $value | humanizePercentage }} full"

      # Database connection pool exhausted
      - alert: DatabaseConnectionPoolExhausted
        expr: pg_stat_activity_count / 100 > 0.95  # Assuming max 100 connections
        for: 3m
        labels:
          severity: critical
          team: database
        annotations:
          summary: "Database connection pool nearly exhausted"
          description: "{{ $value | humanizePercentage }} of connections in use"
```

### 5.2 Warning Alerts

```yaml
# File: config/alert-rules-warning.yml

groups:
  - name: warning_alerts
    interval: 1m
    rules:
      # Slow queries
      - alert: SlowQueries
        expr: rate(pg_stat_statements_mean_exec_time[5m]) > 1000
        for: 5m
        labels:
          severity: warning
          team: database
        annotations:
          summary: "Slow database queries detected"
          description: "Average query time is {{ $value | humanize }}ms"

      # High memory usage
      - alert: HighMemoryUsage
        expr: (1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) > 0.80
        for: 5m
        labels:
          severity: warning
          team: infrastructure
        annotations:
          summary: "High memory usage (>80%)"
          description: "Memory usage is {{ $value | humanizePercentage }}"

      # API response time degradation
      - alert: HighAPIResponseTime
        expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 1.0
        for: 5m
        labels:
          severity: warning
          team: backend
        annotations:
          summary: "API response time is slow"
          description: "p95 response time is {{ $value | humanize }}s"

      # High sync queue
      - alert: HighSyncQueueBacklog
        expr: sync_queue_size > 1000
        for: 10m
        labels:
          severity: warning
          team: mobile
        annotations:
          summary: "High sync queue backlog"
          description: "Offline sync queue has {{ $value }} items"

      # Mobile app crash rate elevated
      - alert: MobileAppCrashRateElevated
        expr: rate(mobile_app_crashes_total[1h]) > 0.0005
        for: 5m
        labels:
          severity: warning
          team: mobile
        annotations:
          summary: "Mobile app crash rate elevated"
          description: "Crash rate is {{ $value | humanizePercentage }}"
```

---

## 6. ALERTMANAGER CONFIGURATION

```yaml
# File: config/alertmanager.yml

global:
  resolve_timeout: 5m
  slack_api_url: 'https://hooks.slack.com/services/YOUR/WEBHOOK/URL'
  pagerduty_url: 'https://events.pagerduty.com/v2/enqueue'

templates:
  - '/etc/alertmanager/templates/*.tmpl'

route:
  receiver: 'default-receiver'
  group_by: ['alertname', 'cluster', 'service']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 4h
  routes:
    # Critical alerts
    - match:
        severity: critical
      receiver: 'critical-team'
      group_wait: 1s
      repeat_interval: 5m
      continue: true

    # Database alerts
    - match:
        team: database
      receiver: 'database-team'
      group_by: ['alertname', 'instance']
      repeat_interval: 30m

    # Mobile alerts
    - match:
        team: mobile
      receiver: 'mobile-team'
      repeat_interval: 1h

receivers:
  # Default receiver (Slack)
  - name: 'default-receiver'
    slack_configs:
      - channel: '#erp-alerts'
        title: 'Alert: {{ .GroupLabels.alertname }}'
        text: '{{ range .Alerts }}{{ .Annotations.description }}{{ end }}'
        color: '{{ if eq .Status "firing" }}danger{{ else }}good{{ end }}'

  # Critical receiver (Slack + PagerDuty)
  - name: 'critical-team'
    slack_configs:
      - channel: '#erp-critical'
        title: '🚨 CRITICAL: {{ .GroupLabels.alertname }}'
        text: '{{ range .Alerts }}{{ .Annotations.description }}{{ end }}'
        color: 'danger'
        actions:
          - type: button
            text: 'View in Grafana'
            url: 'https://grafana.internal/d/{{ .GroupLabels.dashboard }}'
    pagerduty_configs:
      - description: '{{ .GroupLabels.alertname }}: {{ (index .Alerts 0).Annotations.summary }}'
        severity: 'critical'

  # Database team
  - name: 'database-team'
    slack_configs:
      - channel: '#erp-database'
        title: '⚠️ Database Alert: {{ .GroupLabels.alertname }}'

  # Mobile team
  - name: 'mobile-team'
    slack_configs:
      - channel: '#erp-mobile'
        title: '📱 Mobile Alert: {{ .GroupLabels.alertname }}'

inhibit_rules:
  # Suppress warning if critical alert exists
  - source_match:
      severity: 'critical'
    target_match:
      severity: 'warning'
    equal: ['alertname', 'instance']

  # Suppress if service is already down
  - source_match:
      alertname: 'APIServiceDown'
    target_match_re:
      alertname: 'High.*'
    equal: ['instance']
```

---

## 7. LOGGING INFRASTRUCTURE

### 7.1 Filebeat Configuration

```yaml
# File: config/filebeat.yml

filebeat.inputs:
  - type: log
    enabled: true
    paths:
      - /var/log/erp/application.log
      - /var/log/erp/access.log
    json.message_key: message
    json.keys_under_root: false
    processors:
      - add_kubernetes_metadata:
          host: ${NODE_NAME}
      - add_docker_metadata: ~
      - add_process_metadata: ~

output.elasticsearch:
  hosts: ["elasticsearch:9200"]
  index: "erp-logs-%{+yyyy.MM.dd}"
  
logging.level: info
logging.to_files: true
logging.files:
  path: /var/log/filebeat
  name: filebeat
  keepfiles: 7
  permissions: 0644
```

### 7.2 Logstash Pipeline

```conf
# File: config/logstash.conf

input {
  beats {
    port => 5000
    ssl => true
    ssl_certificate => "/etc/logstash/certs/cert.pem"
    ssl_key => "/etc/logstash/certs/key.pem"
  }
}

filter {
  # Parse JSON logs
  json {
    source => "message"
    target => "parsed"
  }
  
  # Extract fields
  mutate {
    add_field => {
      "environment" => "production"
      "region" => "asia-southeast"
    }
  }
  
  # Grok parsing for non-JSON logs
  if [type] == "nginx" {
    grok {
      match => { "message" => "%{COMBINEDAPACHELOG}" }
    }
  }
}

output {
  # Send to Elasticsearch
  elasticsearch {
    hosts => ["elasticsearch:9200"]
    index => "erp-logs-%{+YYYY.MM.dd}"
  }
  
  # Alert on critical errors
  if [parsed][level] == "ERROR" or [parsed][level] == "CRITICAL" {
    email {
      to => "ops-team@qutykarunia.com"
      subject => "Critical Error: %{parsed.message}"
      body => "%{message}"
    }
  }
}
```

---

## 8. HEALTH CHECK ENDPOINTS

### 8.1 Backend Health Checks

```python
# File: erp-softtoys/app/api/routers/health.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from redis import Redis
import time

router = APIRouter(prefix="/health", tags=["health"])

@router.get("/")
async def health_check(db: AsyncSession = Depends(get_db)):
    """Basic health check - returns 200 if service is up"""
    return {"status": "ok", "timestamp": time.time()}

@router.get("/live")
async def liveness_check():
    """Kubernetes liveness probe - just check if app is running"""
    return {"status": "alive"}

@router.get("/ready")
async def readiness_check(
    db: AsyncSession = Depends(get_db),
    redis_client: Redis = Depends(get_redis)
):
    """Kubernetes readiness probe - check dependencies"""
    try:
        # Check database
        await db.execute(text("SELECT 1"))
        
        # Check Redis
        redis_client.ping()
        
        # Check disk space
        import shutil
        disk = shutil.disk_usage("/")
        if (disk.free / disk.total) < 0.1:  # Less than 10%
            raise HTTPException(status_code=503, detail="Low disk space")
        
        return {
            "status": "ready",
            "checks": {
                "database": "ok",
                "redis": "ok",
                "disk": "ok"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))

@router.get("/detailed")
async def detailed_health(
    db: AsyncSession = Depends(get_db),
    redis_client: Redis = Depends(get_redis)
):
    """Detailed health information"""
    import psutil
    
    try:
        return {
            "status": "ok",
            "timestamp": time.time(),
            "version": APP_VERSION,
            "environment": os.getenv("ENVIRONMENT"),
            "checks": {
                "database": await check_database_health(db),
                "redis": check_redis_health(redis_client),
                "system": {
                    "cpu_percent": psutil.cpu_percent(),
                    "memory_percent": psutil.virtual_memory().percent,
                    "disk_percent": psutil.disk_usage("/").percent
                }
            }
        }
    except Exception as e:
        return {"status": "degraded", "error": str(e)}, 503
```

---

## 9. PRODUCTION RUNBOOKS

### 9.1 Critical Alert Response

```markdown
# CRITICAL ALERT RESPONSE GUIDE

## Alert: API Service Down

### Detection
- **Alert**: APIServiceDown
- **Threshold**: No response for 2+ minutes
- **Severity**: CRITICAL

### Immediate Actions (0-2 minutes)

1. **Acknowledge Alert**
   ```bash
   # In AlertManager UI, mark as acknowledged
   # Notify team in #erp-critical Slack channel
   ```

2. **Verify the Issue**
   ```bash
   # Check if service is actually down
   curl -v http://api.qutykarunia.com/health
   curl -v http://localhost:8000/health  # On server
   
   # Check container status
   docker ps | grep backend
   docker logs backend-staging --tail 50
   ```

3. **Quick Diagnostics**
   - Check CPU usage: `top`
   - Check memory: `free -h`
   - Check disk: `df -h`
   - Check network: `ss -tuln | grep 8000`

### Remediation Actions

**Option A: Restart Service**
```bash
docker-compose restart backend
# Wait 30 seconds
curl -f http://localhost:8000/health
```

**Option B: Scale Up**
```bash
docker-compose up -d --scale backend=3
```

**Option C: Rollback**
```bash
# If recent deployment
git revert HEAD --no-edit
docker-compose down
docker-compose up -d
```

### Verification
- [ ] API responds to health check
- [ ] No new errors in logs
- [ ] Response times normal
- [ ] Acknowledge resolved alert

### Post-Incident
1. Review logs for root cause
2. Document incident in wiki
3. Plan fix if needed
4. Schedule post-mortem if critical
```

### 9.2 Database Performance Degradation

```markdown
# DATABASE PERFORMANCE DEGRADATION

### Detection
- Alert: SlowQueries
- Metric: Average query time > 1000ms for 5+ minutes

### Immediate Actions

1. **Check Current Load**
   ```sql
   -- Find slow queries
   SELECT query, calls, mean_exec_time 
   FROM pg_stat_statements 
   ORDER BY mean_exec_time DESC 
   LIMIT 10;
   
   -- Find active connections
   SELECT pid, usename, query 
   FROM pg_stat_activity 
   WHERE state = 'active';
   ```

2. **Check Resource Usage**
   ```bash
   docker stats postgres
   ```

3. **Identify Problem Query**
   ```sql
   EXPLAIN ANALYZE <slow_query>;
   ```

### Remediation

**Option A: Add Index**
```sql
-- If query is missing index
CREATE INDEX ON table_name(column_name);
ANALYZE table_name;
```

**Option B: Kill Long-Running Query**
```sql
-- Identify pid
SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE query_start < NOW() - INTERVAL '10 min';
```

**Option C: Increase Connection Pool**
```yaml
# In docker-compose
postgres:
  environment:
    POSTGRES_MAX_CONNECTIONS: 200
```

### Verification
- [ ] Query times < 1s (p95)
- [ ] Connection pool utilization < 70%
- [ ] No new slow queries
```

---

## 10. IMPLEMENTATION CHECKLIST

### Phase 1: Data Collection (Week 1)
- [ ] Deploy Prometheus
- [ ] Add metrics instrumentation to FastAPI
- [ ] Add Firebase Analytics to mobile app
- [ ] Deploy ELK stack
- [ ] Configure log shipping (Filebeat)

### Phase 2: Visualization (Week 2)
- [ ] Deploy Grafana
- [ ] Create system health dashboard
- [ ] Create production workflow dashboard
- [ ] Create mobile performance dashboard
- [ ] Create custom dashboards per team

### Phase 3: Alerting (Week 2)
- [ ] Deploy AlertManager
- [ ] Configure alert rules (critical + warning)
- [ ] Setup Slack integration
- [ ] Setup PagerDuty integration
- [ ] Test alert routing

### Phase 4: Runbooks & Training (Week 3)
- [ ] Write incident response runbooks
- [ ] Create troubleshooting guides
- [ ] Train ops team on dashboards
- [ ] Train team on alert response
- [ ] Practice incident response drills

### Phase 5: Refinement (Ongoing)
- [ ] Add more granular metrics
- [ ] Tune alert thresholds
- [ ] Add custom dashboards
- [ ] Improve runbook documentation
- [ ] Analyze alert effectiveness

---

## 📊 KEY METRICS SUMMARY

| Metric | Target | Alert Level |
|--------|--------|------------|
| API Response Time (p95) | < 500ms | Warning: 1s, Critical: 2s |
| Error Rate (5xx) | < 0.5% | Warning: 1%, Critical: 5% |
| Database Query Time (avg) | < 100ms | Warning: 500ms, Critical: 1s |
| Memory Usage | < 70% | Warning: 80%, Critical: 90% |
| Disk Usage | < 70% | Warning: 80%, Critical: 90% |
| Mobile App Crash Rate | < 0.01% | Warning: 0.05%, Critical: 0.1% |
| Sync Success Rate | > 99% | Warning: 98%, Critical: 95% |
| Barcode Scan Success Rate | > 99% | Warning: 95%, Critical: 90% |

---

**Status**: Ready for Production  
**Implementation Effort**: 6-8 hours  
**Maintenance Effort**: 2 hours/week

