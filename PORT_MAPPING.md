# ERP2026 - Port Mapping Reference

## 🔌 Service Ports

| Service | Host Port | Container Port | URL | Credentials |
|---------|-----------|-----------------|-----|-------------|
| **Frontend** | 3000 | 3000 | http://localhost:3000 | N/A |
| **Backend API** | 8000 | 8000 | http://localhost:8000 | N/A |
| **API Swagger Docs** | 8000 | 8000 | http://localhost:8000/docs | N/A |
| **PostgreSQL** | 5432 | 5432 | localhost:5432 | user: erp_staging_user |
| **Redis** | 6379 | 6379 | localhost:6379 | N/A |
| **Prometheus** | 9090 | 9090 | http://localhost:9090 | N/A |
| **Grafana** | 3001 | 3000 | http://localhost:3001 | admin / admin |
| **AlertManager** | 9093 | 9093 | http://localhost:9093 | N/A |
| **pgAdmin** | 5051 | 80 | http://localhost:5051 | admin@example.com / admin |

---

## 📋 Quick Access

### Web Applications
```
Frontend:      http://localhost:3000
API Docs:      http://localhost:8000/docs
Grafana:       http://localhost:3001
pgAdmin:       http://localhost:5051
Prometheus:    http://localhost:9090
AlertManager:  http://localhost:9093
```

### Databases
```
PostgreSQL:  localhost:5432
Redis:       localhost:6379
```

### Credentials
```
PostgreSQL:
  User:     erp_staging_user
  Password: erp_staging_pass
  Database: erp_staging

Grafana:
  User:     admin
  Password: admin

pgAdmin:
  Email:    admin@example.com
  Password: admin
```

---

## 🚀 Service Status Check

```bash
# Check if port is in use
netstat -ano | findstr :3000   # Windows
lsof -i :3000                   # macOS/Linux

# Check Docker service status
docker-compose ps
docker-compose logs -f [service-name]
```

---

## ⚡ Common Issues & Solutions

### Port Already in Use
```bash
# Find process using port
netstat -ano | findstr :PORT_NUMBER

# Kill process (Windows)
taskkill /PID <PID> /F

# Kill process (macOS/Linux)
kill -9 <PID>
```

### Service Won't Connect
1. Verify service is running: `docker-compose ps`
2. Check logs: `docker-compose logs [service-name]`
3. Verify network connectivity: `docker network inspect erp_network`

### Port Conflict
Ensure no other application is using:
- 3000 (Frontend)
- 3001 (Grafana)
- 5432 (PostgreSQL)
- 6379 (Redis)
- 8000 (Backend API)
- 9090 (Prometheus)
- 9093 (AlertManager)
- 5051 (pgAdmin)

---

## 📝 Notes

- All services are on the `erp_network` bridge network
- Services can communicate using service names (e.g., `postgres:5432`)
- External connections use `localhost:PORT`
- All ports are configurable via environment variables or docker-compose.yml

---

**Updated: 2026-01-26**
