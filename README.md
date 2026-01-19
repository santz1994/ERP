# 🏭 QUTY KARUNIA ERP SYSTEM
**AI-Powered Manufacturing Execution System for Soft Toys Production**

![Status](https://img.shields.io/badge/Status-Week%201%20Complete-brightgreen)
![Architecture](https://img.shields.io/badge/Architecture-Modular%20Monolith-blue)
![Database](https://img.shields.io/badge/Database-PostgreSQL-336791)
![API](https://img.shields.io/badge/API-FastAPI-009688)

---

## 📋 OVERVIEW

Quty Karunia ERP is a comprehensive manufacturing execution system designed for stuffed toy production with IKEA standards. The system manages complex multi-stage production workflows with real-time quality control, inventory tracking, and inter-departmental handshake protocols.

### **Key Features**
- 🔄 **3 Production Routes** - Flexible routing (Full Process, Direct Sewing, Subcon)
- 📦 **Real-Time Inventory** - FIFO stock management with lot traceability
- 🚚 **QT-09 Transfer Protocol** - Gold standard handshake for inter-departmental transfers
- 📊 **Quality Control** - ISO 8124 lab testing with digital records
- 🎯 **Line Clearance** - Prevent product segregation & article mixing
- 📱 **Mobile-First** - Operator touchscreen interfaces
- 📈 **Real-Time Monitoring** - Prometheus metrics + Grafana dashboards

---

## 🚀 QUICK START

### **Prerequisites**
- Python 3.10+
- PostgreSQL 13+
- Git

### **Setup (5 minutes)**
```bash
# 1. Clone & navigate
cd D:\Project\ERP2026\erp-softtoys

# 2. Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create .env file
cat > .env << EOF
DATABASE_URL=postgresql://postgres:password@localhost:5432/erp_quty_karunia
JWT_SECRET_KEY=your-secret-key
ENVIRONMENT=development
EOF

# 5. Create database & run migrations
createdb -U postgres erp_quty_karunia
alembic upgrade head

# 6. Start server
python -m uvicorn app.main:app --reload

# 7. Open browser
# Swagger UI: http://localhost:8000/docs
```

---

## 📁 PROJECT STRUCTURE

```
erp-softtoys/
├── app/
│   ├── core/
│   │   ├── database.py           # SQLAlchemy setup
│   │   ├── models/
│   │   │   ├── products.py       # Articles + Categories (parent-child)
│   │   │   ├── bom.py            # Bill of Materials
│   │   │   ├── manufacturing.py  # MO + Work Orders
│   │   │   ├── transfer.py       # Transfer logs + Line occupancy
│   │   │   ├── warehouse.py      # Stock management + FIFO
│   │   │   ├── quality.py        # QC tests + Inspections
│   │   │   ├── exceptions.py     # Alerts + Acknowledgements
│   │   │   └── users.py          # Users + Roles
│   │   ├── config.py             # Configuration (coming Week 2)
│   │   ├── security.py           # Auth & encryption (coming Week 2)
│   │   └── constants.py          # System constants
│   ├── api/
│   │   └── v1/                   # API routes (coming Week 2)
│   ├── modules/                  # Business logic (coming Week 3)
│   ├── shared/                   # Common utilities (coming Week 2)
│   └── main.py                   # FastAPI app
├── migrations/                   # Alembic DB migrations
├── tests/                        # Test suite (coming Week 9)
├── requirements.txt              # Python dependencies
├── .env.example                  # Environment template
└── README.md                     # This file

docs/
├── IMPLEMENTATION_ROADMAP.md     # 11-week development plan
├── WEEK1_SETUP_GUIDE.md          # Week 1 setup instructions
├── WEEK1_SUMMARY.md              # Phase 0 completion report
└── Project Docs/
    ├── Project.md                # Project overview & recommendations
    ├── Flow Production.md         # Production SOP
    ├── Database Scheme.csv        # Schema reference
    └── Flowchart ERP.csv         # Process flowchart
```

---

## 📊 DATABASE SCHEMA

### **21 Tables Implemented**
- **Master Data**: Products, Categories, BOM, Partners
- **Production**: Manufacturing Orders, Work Orders, Material Consumption
- **Transfer**: Transfer Logs, Line Occupancy (Real-time status)
- **Warehouse**: Locations, Stock Moves, Stock Quants, Stock Lots (FIFO)
- **Quality**: QC Lab Tests, QC Inspections
- **Exception**: Alert Logs, Segregasi Acknowledgement
- **Security**: Users (with role-based access)

### **Key Features**
✅ Parent-child article hierarchy (Gap Fix #1)
✅ Real-time line occupancy tracking (Gap Fix #2)
✅ Transfer enum expansion including Embroidery (Gap Fix #3)
✅ BOM revision audit trail (Gap Fix #4)
✅ QC test numeric precision (Gap Fix #5)

---

## 🎯 PRODUCTION WORKFLOWS

### **Route 1: Full Process (With Embroidery)**
```
PO → PPIC → Cutting → Embroidery → Sewing → Finishing → Packing → FG
         (WIP CUT)   (WIP EMBO)   (WIP SEW)  (FG Code)
```

### **Route 2: Direct Sewing (Skip Embroidery)**
```
PO → PPIC → Cutting → Sewing → Finishing → Packing → FG
         (WIP CUT)  (WIP SEW)  (FG Code)
```

### **Route 3: Subcon (External Vendor)**
```
PO → PPIC → Cutting → [Vendor] → Finishing → Packing → FG
         (WIP CUT)   (External)  (FG Code)
```

---

## 🔐 SECURITY & ROLES

### **Role-Based Access Control (16 Roles)**
- **Admin** - System administrator
- **PPIC Manager** - Production planning
- **SPV Cutting** - Cutting supervisor (Escalation point)
- **SPV Sewing** - Sewing supervisor
- **SPV Finishing** - Finishing supervisor
- **Operator_*** - Machine operators
- **QC Inspector** - Quality control
- **Warehouse Admin** - Inventory management
- **Purchasing** - Procurement
- **Security** - Gate security

---

## 📈 MONITORING & METRICS

### **5 Key Performance Indicators**
1. **Line Utilization Rate** - Target > 85%
2. **Transfer Cycle Time** - Target Cutting→Sewing < 15 min
3. **QC Reject Rate** - Target < 2%
4. **Line Clearance Compliance** - Target 100%
5. **Handshake Acknowledgement Rate** - Target 100%

### **Monitoring Infrastructure**
- Prometheus metrics collection
- Grafana real-time dashboards
- ELK stack for centralized logging
- Alert rules for critical events

---

## 📚 DOCUMENTATION

| Document | Purpose | Status |
|----------|---------|--------|
| [IMPLEMENTATION_ROADMAP.md](./docs/IMPLEMENTATION_ROADMAP.md) | 11-week development plan | ✅ Complete |
| [WEEK1_SETUP_GUIDE.md](./docs/WEEK1_SETUP_GUIDE.md) | Setup & troubleshooting | ✅ Complete |
| [WEEK1_SUMMARY.md](./docs/WEEK1_SUMMARY.md) | Phase 0 completion report | ✅ Complete |
| [Project.md](./docs/Project%20Docs/Project.md) | Architecture & recommendations | ✅ Complete |
| [Flow Production.md](./docs/Project%20Docs/Flow%20Production.md) | Production SOP | ✅ Complete |
| [Database Scheme.csv](./docs/Project%20Docs/Database%20Scheme.csv) | Schema reference | ✅ Complete |
| [Flowchart ERP.csv](./docs/Project%20Docs/Flowchart%20ERP.csv) | Process flowchart | ✅ Complete |

---

## 🗓️ DEVELOPMENT TIMELINE

| Phase | Week | Component | Status |
|-------|------|-----------|--------|
| **0** | 1 | Database Models & Schema | ✅ **COMPLETE** |
| **1** | 2 | Authentication & API Skeleton | 🟡 Next |
| **1** | 3-4 | Core Modules (PPIC, Cutting) | 🔴 Upcoming |
| **2** | 5-6 | Production Modules (Sewing, Finishing) | 🔴 Upcoming |
| **3** | 7 | QC & Exception Handling | 🔴 Upcoming |
| **4** | 8 | Monitoring & Alerting | 🔴 Upcoming |
| **5** | 9-10 | Testing (Unit & Integration) | 🔴 Upcoming |
| **6** | 11 | Deployment (Docker + K8s) | 🔴 Upcoming |

---

## 🛠️ TECHNOLOGY STACK

### **Backend**
- **Framework**: FastAPI (async Python web framework)
- **Database**: PostgreSQL (with SQLAlchemy ORM)
- **Validation**: Pydantic
- **Authentication**: JWT + bcrypt
- **Message Queue**: Redis (for real-time alerts)
- **Monitoring**: Prometheus + Grafana

### **Frontend** (Coming Week 4+)
- **Mobile**: React Native
- **Dashboard**: React + TypeScript
- **Charts**: Recharts/Apache ECharts

### **DevOps** (Coming Week 11)
- **Containerization**: Docker
- **Orchestration**: Kubernetes
- **CI/CD**: GitHub Actions
- **Registry**: Docker Hub

---

## 🧪 TESTING

### **Coverage Target**: > 85%
- **Unit Tests** (Week 9): 100+ tests
- **Integration Tests** (Week 10): 15+ full workflows
- **Load Tests** (Week 10): 1000 concurrent users
- **Performance Tests**: API response time < 500ms

### **Test Data Scenarios**
- ✅ Route 1: Full process with embroidery
- ✅ Route 2: Direct sewing
- ✅ Route 3: Subcon external vendor
- ✅ Error scenarios (line blocked, segregasi mismatch)
- ✅ Exception flows (QC fail, shortage, duplicate scan)

---

## 🚀 DEPLOYMENT

### **Development** (Local)
```bash
python -m uvicorn app.main:app --reload
```

### **Production** (Docker + Kubernetes)
```bash
docker build -t quty-erp:latest .
docker push quty-erp:latest
kubectl apply -f k8s-manifests/
```

---

## 🤝 CONTRIBUTING

### **Branch Strategy**
- `main` - Production (stable releases)
- `develop` - Development (integration)
- `feature/*` - Feature branches
- `bugfix/*` - Bug fix branches

### **Code Standards**
- Black for code formatting
- Flake8 for linting
- MyPy for type checking
- 80-character line limit

---

## 📞 SUPPORT

### **Issues & Questions**
- Check [WEEK1_SETUP_GUIDE.md](./docs/WEEK1_SETUP_GUIDE.md) troubleshooting section
- Review [Project.md](./docs/Project%20Docs/Project.md) for architecture questions
- See [Flowchart ERP.csv](./docs/Project%20Docs/Flowchart%20ERP.csv) for workflow details

### **Team Contacts**
- **Senior Developer**: Daniel Rizaldy
- **Architecture**: Modular Monolith pattern
- **Lead**: AI-Assisted Development

---

## 📄 LICENSE

**CONFIDENTIAL - QUTY KARUNIA PROPRIETARY**

This project is for Quty Karunia internal use only. Do not share any part of this project without permission.

---

## ✨ ACKNOWLEDGMENTS

- **Database Design**: Based on comprehensive manufacturing SOP
- **Flowchart Design**: Industry best practices (QT-09 Gold Standard)
- **Architecture**: Modular Monolith for manufacturing systems
- **Standards**: IKEA compliance requirements

---

## 🎯 SUCCESS CRITERIA

✅ Week 1: Database models complete (ALL GAP FIXES APPLIED)
🟡 Week 2: API skeleton with authentication (IN PROGRESS)
🔴 Week 3: Core production modules
🔴 Week 4: Transfer handshake protocol
🔴 Week 5-6: Full production workflow
🔴 Week 7-10: QC, testing, monitoring
🔴 Week 11: Production deployment

---

**Status**: Phase 0 Foundation COMPLETE ✅
**Next**: Week 2 API Development
**Last Updated**: January 19, 2026

---

*Developed by: Daniel Rizaldy (Senior IT Developer)*
*Architecture: Modular Monolith + FastAPI + PostgreSQL*
*For: Quty Karunia Manufacturing*
#   E R P  
 