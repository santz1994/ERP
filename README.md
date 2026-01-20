# 🏭 QUTY KARUNIA ERP SYSTEM
**AI-Powered Manufacturing Execution System for Soft Toys Production**

![Status](https://img.shields.io/badge/Status-100%25%20Complete-success)
![Production](https://img.shields.io/badge/Ready-Production%20Deployment-brightgreen)
![Architecture](https://img.shields.io/badge/Architecture-Modular%20Monolith-blue)
![Database](https://img.shields.io/badge/Database-PostgreSQL%2015-336791)
![API](https://img.shields.io/badge/API-FastAPI%200.95-009688)
![Frontend](https://img.shields.io/badge/Frontend-React%2018.2-61DAFB)
![TypeScript](https://img.shields.io/badge/TypeScript-5.3-3178C6)

---

## 📋 OVERVIEW

Quty Karunia ERP is a **production-ready** manufacturing execution system designed for stuffed toy production with IKEA standards. The system manages complex multi-stage production workflows with real-time quality control, inventory tracking, and inter-departmental handshake protocols.

### **✨ Implemented Features**
- ✅ **104 REST API Endpoints** - Complete backend implementation (11 departments)
- ✅ **15 Frontend Pages** - React 18 + TypeScript production UI
- ✅ **11-Department Production Flow** - Purchasing → Warehouse → Cutting → Embroidery → Sewing → Finishing → Packing → Finishgoods
- ✅ **UAC/RBAC System** - Fine-grained module-level permissions for 17 roles ⭐ NEW!
- ✅ **QC Module** - Complete quality control interface with inspections & lab tests ⭐ NEW!
- ✅ **Admin Tools** - User, Masterdata, and Import/Export management ⭐ NEW!
- ✅ **Dynamic Report Builder** - Custom report creation with 5+ data sources ⭐ NEW!
- ✅ **Barcode Scanner** - Camera + manual barcode scanning for warehouse & finishgoods ⭐ NEW!
- ✅ **Purchasing Module** - PO management, approval workflow, supplier performance tracking
- ✅ **Finishgoods Module** - Final warehouse with shipment preparation & stock aging analysis
- ✅ **Sewing Internal Loop** - Handle products returning to same department (Note 1 from Flow Production)
- ✅ **E-Kanban Board** - Digital accessory request system with approval workflow
- ✅ **Reports Dashboard** - Production/QC/Inventory reports with PDF/Excel export
- ✅ **Real-Time Updates** - React Query with 3-5 second polling
- ✅ **Multilingual Support** - Indonesia & English (i18n)
- ✅ **CSV/Excel Import/Export** - Data migration and backup tools
- ✅ **WIB Timezone** - GMT+7 with 3-shift system support
- ✅ **Line Clearance Protocol** - Prevent product segregation
- ✅ **QT-09 Transfer Protocol** - Gold standard inter-department handshake
- ✅ **Shortage Logic** - Automatic shortage detection with approval workflow
- ✅ **FIFO Inventory** - First-In-First-Out stock allocation with lot traceability
- Docker Desktop (recommended) OR Python 3.10+ & Node.js 18+
- PostgreSQL 15+ & Redis 7+ (if not using Docker)
- Git

### **Option 1: Docker (Recommended - 2 minutes)**
```bash
# 1. Clone repository
git clone <repo-url>
cd ERP2026

# 2. Start all services
docker-compose up -d

# 3. Access applications
# Backend API: http://localhost:8000
# Frontend UI: http://localhost:3000
# Swagger Docs: http://localhost:8000/docs
# pgAdmin: http://localhost:5050
```

### **Option 2: Local Development**

#### **Backend Setup**
```bash
# 1. Navigate to backend
cd erp-softtoys

# 2. Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env with your database credentials

# 5. Initialize database
alembic upgrade head

# 6. Start backend
uvicorn app.main:app --reload --port 8000
```

#### **Frontend Setup**
ERP2026/
├── erp-softtoys/                 # Backend (FastAPI)
│   ├── app/
│   │   ├── core/
│   │   │   ├── database.py       # SQLAlchemy + async support
│   │   │   ├── security.py       # JWT auth + bcrypt
│   │   │   ├── config.py         # Environment configuration
│   │   │   ├── permissions.py    # UAC/RBAC system (17 roles × 16 modules) ⭐ NEW!
│   │   │   └── models/           # SQLAlchemy ORM models (27 tables)
│   │   ├── api/
│   │   │   └── v1/               # 104 REST API endpoints ⭐ UPDATED!
│   │   │       ├── auth.py       # Authentication (7 endpoints + permissions)
│   │   │       ├── admin.py      # Admin management (7 endpoints)
│   │   │       ├── ppic.py       # PPIC management (5 endpoints)
│   │   │       ├── purchasing.py # Purchasing module (6 endpoints)
│   │   │       ├── warehouse.py  # Warehouse operations (8 endpoints)
│   │   │       ├── cutting.py    # Cutting module (5 endpoints)
│   │   │       ├── embroidery.py # Embroidery module (6 endpoints)
│   │   │       ├── sewing.py     # Sewing module (7 endpoints)
│   │   │       ├── finishing.py  # Finishing module (5 endpoints)
│   │   │       ├── packing.py    # Packing module (6 endpoints)
│   │   │       ├── finishgoods.py # Finishgoods module (6 endpoints)
│   │   │       ├── quality.py    # Quality control (4 endpoints)
│   │   │       ├── kanban.py     # E-Kanban (5 endpoints)
│   │   │       ├── reports.py    # Reports (8 endpoints)
│   │   │       ├── report_builder.py # Dynamic report builder (6 endpoints) ⭐ NEW!
│   │   │       ├── import_export.py  # CSV/Excel (8 endpoints)
│   │   │       └── websocket.py  # Real-time notifications (3 endpoints)
│   │   ├── modules/              # Production logic (11 departments)
│   │   │   ├── ppic/             # PPIC planning
│   │   │   ├── purchasing/       # Purchasing business logic ⭐ NEW!
│   │   │   ├── cutting/          # Cutting business logic
│   │   │   ├── embroidery/       # Embroidery business logic
│   │   │   ├── sewing/           # Sewing + Internal Loop ⭐ Enhanced!
│   │   │   ├── finishing/        # Finishing business logic
│   │   │   ├── packing/          # Packing business logic
│   │   │   ├── finishgoods/      # Finishgoods business logic ⭐ NEW!
│   │   │   ├── quality/          # Quality control
│   │   │   └── warehouse/        # Warehouse management
│   │   ├── shared/               # Common utilities
│   │   │   ├── i18n.py           # Multilingual support (ID/EN)
│   │   │   ├── timezone.py       # WIB timezone utilities
│   │   │   └── audit.py          # Audit trail logging
│   │   └── main.py               # FastAPI application
│   ├── tests/                    # Test suite (6 test files)
│   ├── requirements.txt          # Python dependencies
│   └── Dockerfile                # Backend container
│
├── erp-ui/                       # User Interfaces (Multi-Platform)
│   ├── frontend/                 # Web Application (React + TypeScript) ✅ COMPLETE
│   │   ├── src/
│   │   │   ├── pages/            # 15 major pages
│   │   │   │   ├── LoginPage.tsx, DashboardPage.tsx, PPICPage.tsx
│   │   │   │   ├── PurchasingPage.tsx, WarehousePage.tsx
│   │   │   │   ├── CuttingPage.tsx, EmbroideryPage.tsx, SewingPage.tsx
│   │   │   │   ├── FinishingPage.tsx, PackingPage.tsx, FinishgoodsPage.tsx
│   │   │   │   ├── QCPage.tsx, KanbanPage.tsx, ReportsPage.tsx
│   │   │   │   └── AdminUserPage.tsx, AdminMasterdataPage.tsx, AdminImportExportPage.tsx
│   │   │   ├── components/       # Reusable components
│   │   │   ├── api/              # Axios API clients
│   │   │   ├── store/            # Zustand state management
│   │   │   └── App.tsx           # Router configuration
│   │   ├── package.json          # Dependencies
│   │   └── Dockerfile            # Container build
│   ├── mobile/                   # Mobile App (React Native) 🚧 PLANNED
│   │   ├── src/                  # Mobile screens & components
│   │   │   ├── screens/          # Native screens (Login, QC Scanner, etc.)
│   │   │   ├── components/       # Mobile components
│   │   │   └── navigation/       # React Navigation
│   │   └── package.json          # React Native dependencies
│   └── desktop/                  # Desktop App (Electron) 🚧 READY
│       ├── main.js               # Electron main process
│       ├── preload.js            # Security preload
│       └── package.json          # Electron dependencies
├── prometheus.yml                # Metrics collection
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
- **Audit Trail**: Change logs for critical tables

### **Key Features**
✅ Parent-child article hierarchy (Gap Fix #1)
✅ Real-time line occupancy tracking (Gap Fix #2)
✅ Transfer enum expansion including Embroidery (Gap Fix #3)
✅ **Raw Materials (RM)** → Issued from Warehouse using FIFO allocation
- **WIP CUT** → Semi-finished after cutting
- **WIP EMBO** → Semi-finished after embroidery (Route 1 only)
- **WIP SEW** → Semi-finished after sewing
- **FG Code** → Finished goods after packing
- **FG Warehouse** → Final storage location

### **Key Implemented Processes**
- 📦 **Material Issuance** - FIFO stock allocation with lot tracking
- 🔄 **QT-09 Transfer** - Line clearance + inter-department handshake protocol
- 🛠️ **Work Order Execution** - Real-time work order management across 4 departments
- ✅ **Quality Control** - 8 defect types, inspection tracking, pass/fail statistics
- 📊 **E-Kanban System** - Digital accessory request workflow (Requested → Approved → In Transit → Received)
- ⚠️ **Exception Handling** - Automatic alerts for shortages, segregation mismatches, QC failures
- 📈 **Real-Time Monitoring** - Live production status, line occupancy, variance tracking
- 📑 **Reporting** - Production/QC/Inventory reports with PDF/Excel export
      Implemented Authentication & Authorization**
- ✅ **JWT Token-based Authentication** - Secure stateless auth with 24h token expiration
- ✅ **Password Hashing** - bcrypt with salt for secure password storage
- ✅ **Account Lockout** - Automatic lockout after 5 failed login attempts
- ✅ **Role-Based Access Control (RBAC)** - Granular permissions per role
- ✅ **Password Policies** - Minimum 8 characters, uppercase, lowercase, digit, special char
- ✅ **Audit Trail** - All critical actions logged with user, timestamp, and changes

### **User Roles (5 Primary Roles)**
1. **Admin** - Full system access, user management, system configuration
2. **PPIC** - Manufacturing order creation, production planning, BOM management
3. **Production** - Work order execution (Cutting, Embroidery, Sewing, Finishing, Packing)
4. **QC** - Quality inspections, defect tracking, lab test management
5. **Warehouse** - Inventory management, stock moves, FIFO allocation, E-Kanban approval

### **Key Technical Features**
✅ Parent-child article hierarchy for product variants
✅ Real-time line occupancy tracking (prevents segregation)
✅ FIFO stock allocation with lot traceability
✅ BOM revision audit trail for change tracking
✅ Numeric precision for QC test results (DECIMAL(10,4))
✅ Comprehensive foreign key relationships (45+ constraints)
✅ Optimized indexes on frequently queried columns
✅ PostgreSQL 15 with advanced featuresrse proxy configuration for CORS and security headers
✅ Dockerized multi-service architecture (API, DB, Redis, pgAdmin)

---

## 🏭 PRODUCTION WORKFLOWS

### **3 Production Routes**
1. **Route 1 (Full Process with Embroidery)**: PO → PPIC → Warehouse → Cutting → **Embroidery** → Sewing → Finishing → Packing → FG
2. **Route 2 (Standard Process)**: PO → PPIC → Warehouse → Cutting → Sewing → Finishing → Packing → FG
3. **Route 3 (Express/Simple)**: PO → PPIC → Warehouse → Cutting → Finishing → Packing → FG

### **Stock Types**
- **RM (Raw Materials)** → Issued from Warehouse using FIFO allocation
- **WIP CUT** → Semi-finished after cutting
- **WIP EMBO** → Semi-finished after embroidery (Route 1 only) ⭐ NEW!
- **WIP SEW** → Semi-finished after sewing
- **WIP FIN** → Semi-finished after finishing
- **FG** → Finished goods after packing

### **Key Implemented Processes**
- 📦 **Material Issuance** - FIFO stock allocation with lot tracking
- 🔄 **QT-09 Transfer** - Line clearance + inter-department handshake protocol
- 🎨 **Embroidery Operations** - Design type tracking, thread color recording, line status monitoring ⭐ NEW!
- 🛠️ **Work Order Execution** - Real-time work order management across 5 departments
- ✅ **Quality Control** - 8 defect types, inspection tracking, pass/fail statistics
- 📊 **E-Kanban System** - Digital accessory request workflow (4-stage board)
- ⚠️ **Exception Handling** - Automatic alerts for shortages, segregation mismatches, QC failures
- 📈 **Real-Time Monitoring** - Live production status, line occupancy, variance tracking
- 📑 **Reporting** - Production/QC/Inventory reports with PDF/Excel export

---

## 📊 MONITORING & REPORTING

### **Implemented Reports Dashboard**
1. **Production Report**
   - Total output quantity by department
   - Work orders completed count
   - Overall efficiency percentage (color-coded: Green ≥95%, Yellow ≥85%, Red <85%)
   - Department-wise breakdown with input/output/reject quantities
   - Date range filtering
   - PDF/Excel export

2. **QC Report**
   - Total inspections performed
   - Pass rate percentage
   - Defect breakdown by type (8 categories)
   - Pass/fail statistics
   - Inspector performance tracking

3. **Inventory Report**
   - Total unique items
   - Low stock items count
   - Out of stock items
   - Category-wise breakdown
   - Stock health indicators

### **Real-Time Monitoring**
- ✅ **Work Order Status** - Live tracking across all departments
- ✅ **Line Occupancy** - Real-time line clearance status
- ✅ **QC Pass/Fail Rates** - Instant quality metrics
- ✅ **E-Kanban Cards** - Accessory request status tracking
- ✅ **Variance Tracking** - Surplus/shortage detection
- ✅ **React Query Polling** - Auto-refresh every 3-5 seconds

### **Future Enhancements (Optional)**
- Prometheus metrics collection
- Grafana real-time dashboards
- ELK stack for centralized logging
- WebSocket real-time push notificationsts + Inspection checkpoints
- ⚠️ **Exception Handling** - Alerts for shortages, segregasi mismatches

---

## 🔐 SECURITY & ROLES

### **Role-Based Access Control (16 Roles)**
### **Session Reports**
| Document | Purpose | Status |
|----------|---------|--------|
| [SESSION_6_COMPLETION.md](./docs/04-Session-Reports/SESSION_6_COMPLETION.md) | Enterprise features implementation | ✅ Complete |
| [SESSION_7_COMPLETION.md](./docs/04-Session-Reports/SESSION_7_COMPLETION.md) | UI/UX implementation (600+ lines) | ✅ Complete |

### **Planning & Status**
| Document | Purpose | Status |
|----------|---------|--------|
| [IMPLEMENTATION_STATUS.md](./docs/06-Planning-Roadmap/IMPLEMENTATION_STATUS.md) | Real-time project status (100%) | ✅ Complete |
| [IMPLEMENTATION_ROADMAP.md](./docs/IMPLEMENTATION_ROADMAP.md) | Original development plan | ✅ Complete |

### **Technical Documentation**
| Document | Purpose | Status |
|----------|---------|--------|
| [DOCKER_SETUP.md](./docs/DOCKER_SETUP.md) | Docker configuration guide | ✅ Complete |
| [Project.md](./docs/Project%20Docs/Project.md) | Architecture & recommendations | ✅ Complete |
| [Flow Production.md](./docs/Project%20Docs/Flow%20Production.md) | Production SOP | ✅ Complete |
| [Database Scheme.csv](./docs/Project%20Docs/Database%20Scheme.csv) | 27-table schema reference | ✅ Complete |

### **API Documentation**
- **Swagger UI**: http://localhost:8000/docs (Interactive API testing)
- **ReDoc**: http://localhost:8000/redoc (Alternative API docs)
- **OpenAPI JSON**: http://localhost:8000/openapi.json (Machine-readable spec)
- **Security** - Gate security

---
Session | Component | Status | Deliverables |
|-------|---------|-----------|--------|--------------|
| **0** | 1 | Database Foundation | ✅ **COMPLETE** | 27 tables, 45+ relationships, 5 gap fixes |
| **1** | 2 | Authentication & Core API | ✅ **COMPLETE** | JWT auth, 13 endpoints (Auth + Admin + PPIC) |
| **2** | 3 | Production Modules | ✅ **COMPLETE** | Cutting, Sewing, Finishing, Packing (24 endpoints) |
| **3** | 4 | QC & Transfer Protocol | ✅ **COMPLETE** | QT-09 handshake, QC module, line clearance |
| **4** | 4 | Additional Modules | ✅ **COMPLETE** | Warehouse, inventory, stock management |
| **5** | 5 | Testing & Bug Fixes | ✅ **COMPLETE** | Test suite, password validation, error handling |
| **6** | 5 | Docker Deployment | ✅ **COMPLETE** | docker-compose.yml, 4-container architecture |
| **7** | 5 | WebSocket & Notifications | ✅ **COMPLETE** | Real-time alerts, department notifications |
| **8** | 5 | E-Kanban & Reporting | ✅ **COMPLETE** | Kanban workflow, report generation |
| **9** | 6 | Enterprise Features | ✅ **COMPLETE** | CSV/Excel import/export, i18n, timezone, license |
| **10** | 7 | UI/UX Implementation | ✅ **COMPLETE** | 8 React pages, E-Kanban board, Reports dashboard |

**Total Duration**: 7 sessions (January 12-19, 2026)  
**Project Sta (Complete)**
- **Framework**: FastAPI 0.95.1 - Async Python web framework with automatic OpenAPI docs
- **Database**: PostgreSQL 15-alpine - Advanced relational database
- **ORM**: SQLAlchemy 2.0 - Modern async ORM with type hints
- **Validation**: Pydantic V2 - Data validation using Python type annotations
- **Authentication**: JWT + bcrypt - Secure token-based auth
- **Cache**: Redis 7-alpine - In-memory data store for sessions
- **Excel Processing**: openpyxl 3.1.2 - Excel file import/export
- **Timezone**: zoneinfo - WIB (GMT+7) timezone support
- **Testing**: pytest + pytest-asyncio - Unit and integration tests

### **Frontend (Complete)**
- **Framework**: React 18.2.0 + TypeScript 5.3.3
- **Build Tool**: Vite 5.0.8 - Lightning-fast HMR and builds
- **Routing**: React Router v6.20.0 - Client-side routing
- **State Management**: 
  - Zustand 4.4.0 - Client state (auth, UI)
  - React Query 5.28.0 - Server state (API data)
- **HTTP Client**: Axios 1.6.2 - Promise-based HTTP client
- **UI Framework**: TailwindCSS 3.4.1 + @tailwindcss/forms
- **Icons**: Lucide React 0.294.0 - Beautiful icon library
- **Date Handling**: date-fns 2.30.0 - Modern date utility

### **DevOps (Complete)**
- **Containerization**: Docker - Multi-stage builds for backend & frontend
- **OrImplemented Test Suite**
- **Test Files**: 6 test modules (auth, cutting, sewing, finishing, packing, QT-09)
- **Test Framework**: pytest + pytest-asyncio
- **Coverage Areas**:
  - ✅ Authentication flows (register, login, token refresh)
  - ✅ Manufacturing order creation and approval
  - ✅ Work order execution (all 4 departments)
  - ✅ QT-09 transfer protocol validation
  - ✅ QC inspection with defect tracking
  - ✅ Line clearance and segregation prevention
  - ✅ Shortage logic with approval workflow
  - ✅ E-Kanban card lifecycle
  - ✅ Password validation and security

### **Running Tests**
```bash
# Run all tests
cd erp-softtoys (Local)**
```bash
# Backend
cd erp-softtoys
uvicorn app.main:app --reload --port 8000

# Frontend
cd erp-ui
npm run dev
```

### **Production (Docker)**
```bash
# Start all services
docker-compose -f docker-compose.production.yml up -d

# Services started:
# - PostgreSQL (port 5432)
# - Redis (port 6379)
# - Backend API (port 8000)
# - Frontend UI (port 3000)
# - Nginx reverse proxy (port 80)

# Check status
docker-compose ps

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Stop services
docker-compose down
```

### **Docker Architecture**
```
┌─────────────────────────────────────┐
│         Nginx (Port 80)             │
│    Reverse Proxy + SSL              │
└──────────┬────────────┬─────────────┘
           │            │
    ┌──────▼──────┐  ┌──▼──────────┐
    │  Frontend   │  │  Backend    │
    │  React:3000 │  │  FastAPI    │
    │             │  │  :8000      │
    └─────────────┘  └──┬──────────┘
                        │
           ┌────────────┼────────────┐
           │            │            │
    ┌──────▼──────┐ ┌──▼──────┐     │
    │ PostgreSQL  │ │  Redis  │     │
    │   :5432     │ │  :6379  │     │
    └─────────────┘ └─────────┘     │
```

### **Environment Variables (Production)**
```bash
# Database
DATABASE_URL=postgresql://postgres:secure_password@postgres:5432/erp_production
REDIS_URL=redis://redis:6379/0

# Security
JWT_SECRET_KEY=<generate-secure-key>
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Environment
ENVIRONMENT=production
DEBUG=false
CORS_ORIGINS=https://yourdomain.com

# Email (optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
### **Test Data Scenarios**
- ✅ Route 1: Full process (Cutting → Embroidery → Sewing → Finishing → Packing)
- ✅ Route 2: Direct sewing (Cutting → Sewing → Finishing → Packing)
- ✅ Route 3: Subcon external vendor
- ✅ Error scenarios (line blocked, segregation mismatch, duplicate scan)
- ✅ Exception flows (QC fail, shortage, rework request)
- ✅ Edge cases (missing data, invalid inputs, unauthorized access
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
#   E R P 
 
 