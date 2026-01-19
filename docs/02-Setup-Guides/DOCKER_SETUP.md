# 🐳 DOCKER SETUP & LOCAL DEVELOPMENT GUIDE
**Quty Karunia ERP System - Complete Docker Deployment**

---

## 📋 PREREQUISITES

### **System Requirements**
- **OS**: Windows 10/11, macOS, or Linux
- **Docker**: 20.10+ ([Install](https://docs.docker.com/get-docker/))
- **Docker Compose**: 1.29+ (included with Docker Desktop)
- **Git**: Latest version
- **RAM**: Minimum 8GB (recommended 16GB)
- **Disk Space**: 20GB free space

### **Installation Verification**
```bash
docker --version
docker-compose --version
git --version
```

---

## 🚀 QUICK START (5 MINUTES)

### **Step 1: Clone & Navigate**
```bash
cd D:\Project\ERP2026
```

### **Step 2: Set Up Environment Variables**
```bash
# Copy template
copy erp-softtoys\.env.example erp-softtoys\.env

# For Windows PowerShell users:
# Copy-Item erp-softtoys\.env.example erp-softtoys\.env
```

### **Step 3: Start All Services**
```bash
# Build and start all services
docker-compose up -d

# For first run (includes database initialization):
docker-compose up -d --build
```

### **Step 4: Wait for Services to Be Ready**
```bash
# Check service status
docker-compose ps

# Expected output (all RUNNING):
# NAME              STATUS
# erp_postgres      Up (healthy)
# erp_redis         Up (healthy)
# erp_backend       Up
# erp_pgadmin       Up
# erp_prometheus    Up
# erp_grafana       Up
# erp_adminer       Up
```

### **Step 5: Access Services**
- **API (Swagger UI)**: http://localhost:8000/docs
- **pgAdmin**: http://localhost:5050 (admin@erp.local / admin)
- **Adminer**: http://localhost:8080
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000 (admin / admin)

---

## 📊 SERVICE ARCHITECTURE

```
Internet (Port Exposure)
    ↓
nginx/Load Balancer (future)
    ↓
┌─────────────────────────────────────────────────────┐
│  Docker Compose Network (erp_network)               │
├─────────────────────────────────────────────────────┤
│                                                      │
│  ┌──────────────┐    ┌──────────────┐              │
│  │  FastAPI     │    │  PostgreSQL  │              │
│  │  Backend     │←──→│  Database    │              │
│  │  :8000       │    │  :5432       │              │
│  └──────────────┘    └──────────────┘              │
│         ↓                   ↓                       │
│    Metrics          Admin UI (pgAdmin)             │
│    Logging          :5050                          │
│         ↓                                          │
│  ┌──────────────┐    ┌──────────────┐              │
│  │  Prometheus  │    │   Grafana    │              │
│  │  :9090       │←──→│   :3000      │              │
│  └──────────────┘    └──────────────┘              │
│                                                     │
│  ┌──────────────┐    ┌──────────────┐              │
│  │   Redis      │    │   Adminer    │              │
│  │   :6379      │    │   :8080      │              │
│  └──────────────┘    └──────────────┘              │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

## 🔧 COMMON OPERATIONS

### **View Logs**
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f postgres
docker-compose logs -f redis

# Last N lines
docker-compose logs --tail=100 backend
```

### **Access Database**
```bash
# Option 1: Use Adminer (Web UI)
# Visit: http://localhost:8080
# System: PostgreSQL
# Server: postgres
# Username: postgres
# Password: password
# Database: erp_quty_karunia

# Option 2: Use pgAdmin (Web UI)
# Visit: http://localhost:5050
# Email: admin@erp.local
# Password: admin
# Add server: Host = postgres, Port = 5432

# Option 3: CLI (inside container)
docker exec -it erp_postgres psql -U postgres -d erp_quty_karunia

# Option 4: CLI from host (requires psql client)
psql -h localhost -U postgres -d erp_quty_karunia
```

### **Database Commands**
```bash
# List all tables
\dt

# Describe table structure
\d products

# View table data
SELECT * FROM products LIMIT 10;

# Exit
\q
```

### **Stop Services**
```bash
# Stop without removing
docker-compose stop

# Stop and remove containers (but keep volumes)
docker-compose down

# Remove everything including volumes
docker-compose down -v

# Clean up all Docker resources
docker system prune -a --volumes
```

### **Restart Services**
```bash
# Restart all
docker-compose restart

# Restart specific
docker-compose restart backend
docker-compose restart postgres
```

### **Run Commands in Containers**
```bash
# Execute command
docker exec -it erp_backend bash

# Run Python script
docker exec erp_backend python -c "import sys; print(sys.version)"

# Apply database migrations
docker exec erp_backend alembic upgrade head
```

---

## 🔍 TROUBLESHOOTING

### **Issue: "Cannot connect to Docker daemon"**
**Solution**: 
- Start Docker Desktop (Windows/macOS)
- On Linux: `sudo systemctl start docker`
- Check: `docker ps`

### **Issue: "Port 5432 already in use"**
**Solution**:
```bash
# Find what's using port 5432
# Windows:
netstat -ano | findstr :5432

# Kill the process (replace PID)
taskkill /PID <PID> /F

# Or change Docker Compose port:
# Edit docker-compose.yml, change "5432:5432" to "5433:5432"
```

### **Issue: "Backend container exits with error"**
**Solution**:
```bash
# View error logs
docker-compose logs backend

# Common issues:
# 1. Database not ready - wait 30s and restart
docker-compose restart backend

# 2. Missing environment variables - check .env file
cat .env

# 3. Alembic migration failed - rebuild
docker-compose down
docker-compose up -d --build
```

### **Issue: "PostgreSQL connection refused"**
**Solution**:
```bash
# Check if postgres is healthy
docker-compose ps postgres

# View postgres logs
docker-compose logs postgres

# If unhealthy, rebuild
docker-compose down -v
docker-compose up -d postgres

# Wait 30s for initialization, then start backend
docker-compose up -d backend
```

### **Issue: "Disk space full"**
**Solution**:
```bash
# Remove unused Docker resources
docker system prune -a

# Remove volumes (WARNING: deletes data)
docker volume prune

# Check Docker disk usage
docker system df
```

---

## 🛠️ DEVELOPMENT WORKFLOW

### **Making Code Changes**
```bash
# 1. Edit code locally (auto-reload enabled)
# File: d:\Project\ERP2026\erp-softtoys\app\main.py

# 2. FastAPI auto-detects changes (--reload flag active)
# Watch logs to see changes applied
docker-compose logs -f backend

# 3. Test via Swagger
# http://localhost:8000/docs
```

### **Installing New Python Packages**
```bash
# 1. Add to requirements.txt
echo "fastapi-utils==0.2.1" >> erp-softtoys/requirements.txt

# 2. Rebuild container
docker-compose build backend

# 3. Restart service
docker-compose up -d backend
```

### **Database Schema Changes**
```bash
# 1. Modify model files in:
# app/core/models/*.py

# 2. Create Alembic migration (inside container)
docker exec erp_backend alembic revision --autogenerate -m "Add new column"

# 3. Review migration file: erp-softtoys/migrations/versions/

# 4. Apply migration
docker exec erp_backend alembic upgrade head
```

### **Running Tests**
```bash
# Run all tests
docker exec erp_backend pytest

# Run specific test file
docker exec erp_backend pytest tests/test_api.py

# With coverage
docker exec erp_backend pytest --cov=app tests/

# Watch mode
docker exec erp_backend pytest-watch
```

---

## 📦 DATA MANAGEMENT

### **Backup Database**
```bash
# Export to SQL file
docker exec erp_postgres pg_dump -U postgres erp_quty_karunia > backup_$(date +%Y%m%d_%H%M%S).sql

# Or via docker
docker exec erp_postgres pg_dump -U postgres erp_quty_karunia | gzip > backup.sql.gz
```

### **Restore Database**
```bash
# From SQL file (into empty database)
docker exec -i erp_postgres psql -U postgres erp_quty_karunia < backup.sql

# Or
gunzip < backup.sql.gz | docker exec -i erp_postgres psql -U postgres erp_quty_karunia
```

### **Copy Data**
```bash
# Copy file from container
docker cp erp_backend:/app/exports/data.csv ./

# Copy file to container
docker cp ./data.csv erp_backend:/app/imports/
```

---

## 📈 MONITORING & METRICS

### **Access Grafana Dashboards**
1. Open: http://localhost:3000
2. Login: admin / admin
3. Go to: Dashboards → Browse
4. Select dashboard

### **View Prometheus Metrics**
1. Open: http://localhost:9090
2. Execute queries:
   ```
   up{job="erp_api"}
   rate(http_requests_total[5m])
   pg_stat_statements_calls
   ```

### **Set Up Grafana Datasource**
1. Configuration → Data Sources → Add
2. Name: Prometheus
3. URL: http://prometheus:9090
4. Save & Test

---

## 🔐 SECURITY BEST PRACTICES

### **Production Deployment Checklist**
```bash
# 1. Change default passwords
export DB_PASSWORD=your-secure-password
export PGADMIN_PASSWORD=your-secure-password
export GRAFANA_PASSWORD=your-secure-password

# 2. Change JWT secret
export JWT_SECRET_KEY=your-64-character-secure-key

# 3. Enable HTTPS
# Use reverse proxy (nginx) with Let's Encrypt

# 4. Restrict CORS
# Edit .env: CORS_ORIGINS=https://yourdomain.com

# 5. Enable log aggregation
# Integrate with ELK stack or CloudWatch

# 6. Regular backups
# Automate daily PostgreSQL backups to S3/NAS
```

---

## 📚 ADDITIONAL RESOURCES

### **Docker Documentation**
- [Docker Compose Reference](https://docs.docker.com/compose/compose-file/)
- [Docker Best Practices](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)
- [Multi-stage Builds](https://docs.docker.com/build/building/multi-stage/)

### **PostgreSQL**
- [PostgreSQL Docker Image](https://hub.docker.com/_/postgres)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

### **Development**
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy ORM](https://docs.sqlalchemy.org/)
- [Alembic Migrations](https://alembic.sqlalchemy.org/)

---

## ✅ VERIFICATION CHECKLIST

After starting Docker, verify:

- [ ] All services running: `docker-compose ps`
- [ ] Backend responding: `curl http://localhost:8000/docs`
- [ ] Database accessible: `http://localhost:5050` (pgAdmin)
- [ ] Redis connected: `docker exec erp_redis redis-cli ping` → PONG
- [ ] Prometheus scraping: `http://localhost:9090/targets`
- [ ] Grafana accessible: `http://localhost:3000`
- [ ] Example query works:
  ```bash
  curl http://localhost:8000/health
  ```

---

## 🎯 NEXT STEPS

1. **Review API Documentation**: http://localhost:8000/docs
2. **Create Test Data**: Use seed_data.py script
3. **Run Migrations**: `docker exec erp_backend alembic upgrade head`
4. **Configure Monitoring**: Set up Grafana dashboards
5. **Start Development**: Follow [IMPLEMENTATION_ROADMAP.md](/docs/IMPLEMENTATION_ROADMAP.md)

---

**Status**: ✅ Docker Setup Complete
**Last Updated**: January 19, 2026
**Docker Compose Version**: 3.8
**Python Version**: 3.11
