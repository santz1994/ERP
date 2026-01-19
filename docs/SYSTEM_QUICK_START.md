# 🚀 QUTY KARUNIA ERP - QUICK START GUIDE
**System Version**: 2.0.0 | **Date**: January 19, 2026 | **Status**: Ready for Go-Live

---

## 📍 ACCESS POINTS

### API Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

### Database Management
- **pgAdmin**: http://localhost:5050
  - Email: admin@erp.local
  - Password: password123 (set in docker-compose.yml)

### System Monitoring (when enabled)
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000

---

## 🐳 DOCKER COMMANDS

### Start System
```bash
cd d:\Project\ERP2026
docker-compose up -d postgres redis backend
```

### Stop System
```bash
docker-compose down
```

### View Logs
```bash
# Backend logs
docker-compose logs backend -f

# PostgreSQL logs
docker-compose logs postgres -f

# Redis logs
docker-compose logs redis -f
```

### Check Status
```bash
docker ps
docker-compose ps
```

### Clean Restart
```bash
docker-compose down -v
docker-compose up -d
```

---

## 🔌 API USAGE EXAMPLES

### Authentication
```bash
# Register
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"username":"john","email":"john@example.com","password":"SecurePass123"}'

# Login
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"john","password":"SecurePass123"}'
```

### Create Manufacturing Order (PPIC)
```bash
curl -X POST "http://localhost:8000/api/v1/ppic/manufacturing-order" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "so_line_id": 1,
    "product_id": 5,
    "qty_planned": 100,
    "routing_type": "Route1",
    "batch_number": "BATCH-2024-001"
  }'
```

### Quality Lab Test
```bash
curl -X POST "http://localhost:8000/api/v1/quality/lab-test/perform" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "batch_number": "BATCH-2024-001",
    "test_type": "Drop Test",
    "test_result": "Pass",
    "measured_value": 150,
    "measured_unit": "cm"
  }'
```

---

## 📊 DATABASE SCHEMA

### Production Modules
- **Cutting**: Material allocation, shortage handling, QT-09 handshake
- **Sewing**: WIP acceptance, inline QC, segregation checks
- **Finishing**: Stuffing, metal detector, FG conversion
- **Packing**: Sorting, carton packing, shipping marks
- **Quality**: Lab tests, inspections, compliance reports

### Core Tables (21 total)
```
Master Data: Products, Categories, Partners, BOM
Orders: SalesOrders, PurchaseOrders
Manufacturing: ManufacturingOrders, WorkOrders, MaterialConsumption
Warehouse: Locations, StockMoves, StockQuants, StockLots
Quality: QCLabTests, QCInspections
Transfer: TransferLogs, LineOccupancy
Exceptions: AlertLogs, SegregasiAcknowledgement
Users: Users (with role-based access)
```

---

## 🔐 USER ROLES

- **Admin**: Full system access
- **PPIC**: Manufacturing order management (admin-only, no planning)
- **Department Manager**: Plan production per department capacity
- **Operator**: Execute production tasks
- **QC Inspector**: Quality testing and inspections
- **Warehouse Admin**: Inventory management
- **Security**: Gate/access control

---

## ⚠️ CRITICAL ALERTS

### P1 Severity (Immediate Action Required)
- **Metal Detection**: Product quarantined immediately
- **Critical QC Failure**: Batch hold for investigation
- **Shortage Escalation**: Requires supervisor approval
- **Line Blockage**: Prevents product transfer

### Health Checks
```bash
# API Health
curl http://localhost:8000/health

# Database Connection
docker-compose exec postgres pg_isready

# Redis Connection
docker-compose exec redis redis-cli ping
```

---

## 📚 DOCUMENTATION

| Document | Location | Purpose |
|----------|----------|---------|
| Session 4 Summary | `/docs/SESSION_4_COMPLETION.md` | Latest changes & status |
| Implementation Status | `/docs/IMPLEMENTATION_STATUS.md` | Overall progress |
| API Reference | `/docs/QUICK_API_REFERENCE.md` | Endpoint documentation |
| Operations Runbook | `/docs/PHASE_7_OPERATIONS_RUNBOOK.md` | Go-live procedures |
| Incident Response | `/docs/PHASE_7_INCIDENT_RESPONSE.md` | Troubleshooting guide |
| Database Schema | `/Project Docs/Database Scheme.csv` | Full schema reference |
| Production Flow | `/Project Docs/Flow Production.md` | Business process |

---

## 🛠️ TROUBLESHOOTING

### Backend won't start
```bash
# Check if port 8000 is in use
netstat -ano | findstr :8000

# Force clean restart
docker-compose down -v
docker-compose build --no-cache backend
docker-compose up -d
```

### Database connection failed
```bash
# Verify PostgreSQL is running
docker-compose ps postgres

# Check PostgreSQL logs
docker-compose logs postgres

# Verify connection string in .env
cat .env | grep DATABASE_URL
```

### Tests failing
```bash
# Run single test
docker-compose exec backend pytest tests/test_auth.py::TestUserRegistration::test_register_success -v

# View full output
docker-compose exec backend pytest tests/ -v --tb=short
```

---

## 📞 SUPPORT

**For Production Issues:**
1. Check `/docs/PHASE_7_INCIDENT_RESPONSE.md`
2. Review container logs: `docker-compose logs -f`
3. Check database connectivity
4. Verify network configuration

**System Owner**: Daniel Rizaldy (Senior Developer)  
**Last Updated**: 2026-01-19

---

### Next Steps
✅ All production modules implemented  
✅ Docker infrastructure running  
✅ API endpoints tested  
⏳ Phase 7 Go-Live Ready - Awaiting data migration & UAT
