# 🚀 QUICK START DEVELOPER GUIDE
**ERP Quty Karunia Live Demo - For Claude Sonnet 4.5**

**Target Audience**: AI Assistant (Claude), Developers  
**Purpose**: Step-by-step commands to setup & run demo  
**Time**: 30 minutes to first working prototype

---

## 📋 PREREQUISITES CHECK

```powershell
# Run this to verify your environment
Write-Host "🔍 Checking prerequisites..." -ForegroundColor Yellow

# Check Docker
if (Get-Command docker -ErrorAction SilentlyContinue) {
    Write-Host "✅ Docker installed: $(docker --version)" -ForegroundColor Green
} else {
    Write-Host "❌ Docker NOT installed" -ForegroundColor Red
}

# Check Python
if (Get-Command python -ErrorAction SilentlyContinue) {
    Write-Host "✅ Python installed: $(python --version)" -ForegroundColor Green
} else {
    Write-Host "❌ Python NOT installed" -ForegroundColor Red
}

# Check Node
if (Get-Command node -ErrorAction SilentlyContinue) {
    Write-Host "✅ Node.js installed: $(node --version)" -ForegroundColor Green
} else {
    Write-Host "❌ Node.js NOT installed" -ForegroundColor Red
}

Write-Host "`n📌 Requirements:" -ForegroundColor Cyan
Write-Host "- Docker Desktop 20+"
Write-Host "- Python 3.11+"
Write-Host "- Node.js 18+"
Write-Host "- 8GB RAM minimum"
Write-Host "- 10GB disk space"
```

**Required Software**:
- Docker Desktop 20+ (with Docker Compose)
- Python 3.11+
- Node.js 18+
- Git
- VS Code (recommended)

---

## ⚡ QUICK START (30 Minutes)

### Step 1: Clone & Setup (5 min)

```powershell
# Create demo directory
cd d:\Project
git clone https://github.com/santz1994/ERP.git ERP2026-Demo
cd ERP2026-Demo

# Copy environment file
Copy-Item .env.example .env

# Edit .env (basic configuration)
# DB_HOST=postgres
# DB_NAME=erp_demo
# DB_USER=erp_user
# DB_PASSWORD=demo123
# JWT_SECRET=your_secret_key_here_change_in_production
# ENVIRONMENT=development
```

### Step 2: Start Database (5 min)

```powershell
# Start PostgreSQL and Redis
docker-compose up -d postgres redis

# Wait for database ready
Write-Host "⏳ Waiting for PostgreSQL..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Verify services running
docker-compose ps

# Expected output:
# NAME                COMMAND                  STATUS              PORTS
# erp_postgres        "docker-entrypoint..."   Up 10 seconds       5432/tcp
# erp_redis           "docker-entrypoint..."   Up 10 seconds       6379/tcp
```

### Step 3: Setup Backend (10 min)

```powershell
cd erp-softtoys

# Create virtual environment
python -m venv venv

# Activate venv
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Seed demo data
python scripts/seed_demo_data.py

# Expected output:
# ✅ Created 4 demo users
# ✅ Created 3 categories
# ✅ Created 3 products
# ✅ Created 2 partners
# 🎉 Demo data seeded successfully!

# Start backend server
uvicorn app.main:app --reload --port 8000

# Server should start at: http://localhost:8000
# API Docs at: http://localhost:8000/docs
```

### Step 4: Setup Frontend (10 min)

**Open NEW PowerShell window**:

```powershell
cd d:\Project\ERP2026-Demo\erp-ui\frontend

# Install dependencies
npm install

# Start dev server
npm run dev

# Expected output:
# VITE v4.x.x  ready in xxx ms
# ➜  Local:   http://localhost:5173/
# ➜  Network: use --host to expose
```

### Step 5: First Test

```powershell
# Open browser
Start-Process "http://localhost:5173"

# Login with demo account:
# Username: admin
# Password: admin123

# You should see dashboard!
```

---

## 🛠️ DEVELOPMENT WORKFLOW

### Running Services

**Terminal 1 - Backend**:
```powershell
cd d:\Project\ERP2026-Demo\erp-softtoys
.\venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --port 8000
```

**Terminal 2 - Frontend**:
```powershell
cd d:\Project\ERP2026-Demo\erp-ui\frontend
npm run dev
```

**Terminal 3 - Database (Docker)**:
```powershell
cd d:\Project\ERP2026-Demo
docker-compose up postgres redis
```

### Verify Everything Works

```powershell
# File: verify-setup.ps1

Write-Host "🧪 Verifying Setup..." -ForegroundColor Cyan

# Test 1: Backend health
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ Backend: HEALTHY" -ForegroundColor Green
    }
} catch {
    Write-Host "❌ Backend: NOT RUNNING" -ForegroundColor Red
}

# Test 2: Frontend
try {
    $response = Invoke-WebRequest -Uri "http://localhost:5173" -UseBasicParsing
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ Frontend: HEALTHY" -ForegroundColor Green
    }
} catch {
    Write-Host "❌ Frontend: NOT RUNNING" -ForegroundColor Red
}

# Test 3: Database connection
try {
    docker exec erp_postgres pg_isready -U erp_user
    Write-Host "✅ Database: CONNECTED" -ForegroundColor Green
} catch {
    Write-Host "❌ Database: NOT CONNECTED" -ForegroundColor Red
}

# Test 4: Login API
try {
    $body = @{
        username = "admin"
        password = "admin123"
    } | ConvertTo-Json

    $response = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/login" `
        -Method POST `
        -Body $body `
        -ContentType "application/json"
    
    if ($response.access_token) {
        Write-Host "✅ Authentication: WORKING" -ForegroundColor Green
    }
} catch {
    Write-Host "❌ Authentication: FAILED" -ForegroundColor Red
}

Write-Host "`n🎉 Setup verification complete!" -ForegroundColor Cyan
```

---

## 🔧 COMMON TASKS

### Adding New API Endpoint

```python
# File: erp-softtoys/app/api/v1/demo.py

from fastapi import APIRouter, Depends
from app.core.dependencies import get_current_user
from app.core.models.users import User

router = APIRouter(prefix="/demo", tags=["Demo"])

@router.get("/hello")
async def hello_world(
    current_user: User = Depends(get_current_user)
):
    """Simple demo endpoint"""
    return {
        "message": f"Hello {current_user.username}!",
        "timestamp": datetime.utcnow()
    }

# Register router in app/main.py:
# from app.api.v1 import demo
# app.include_router(demo.router, prefix="/api/v1")
```

### Adding New Frontend Page

```typescript
// File: erp-ui/frontend/src/pages/DemoPage.tsx

import React from 'react'
import { useAuthStore } from '@/store/authStore'

export const DemoPage: React.FC = () => {
  const { user } = useAuthStore()

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4">Demo Page</h1>
      <p>Welcome, {user?.username}!</p>
    </div>
  )
}

// Register route in App.tsx:
// import { DemoPage } from './pages/DemoPage'
// <Route path="demo" element={<DemoPage />} />
```

### Database Migration

```powershell
# Create new migration
cd erp-softtoys
alembic revision -m "add_new_table"

# Edit generated file in alembic/versions/xxx_add_new_table.py

# Apply migration
alembic upgrade head

# Rollback if needed
alembic downgrade -1
```

### Seed Additional Data

```python
# File: erp-softtoys/scripts/seed_more_data.py

from app.core.database import SessionLocal
from app.core.models.products import Product, Category
from sqlalchemy.orm import Session

def seed_products(db: Session):
    """Add more products for testing"""
    cat_fg = db.query(Category).filter_by(code="FG").first()
    
    products = [
        {
            "default_code": "40551543",
            "name": "KRAMIG Bear",
            "category_id": cat_fg.id,
            "uom": "PCS",
            "price": 95000
        },
        {
            "default_code": "40551544",
            "name": "BLAHAJ Shark",
            "category_id": cat_fg.id,
            "uom": "PCS",
            "price": 120000
        }
    ]
    
    for prod_data in products:
        product = Product(**prod_data)
        db.add(product)
    
    db.commit()
    print(f"✅ Added {len(products)} products")

if __name__ == "__main__":
    db = SessionLocal()
    try:
        seed_products(db)
    finally:
        db.close()
```

---

## 🐛 TROUBLESHOOTING

### Backend Won't Start

```powershell
# Check Python version
python --version  # Should be 3.11+

# Check if port 8000 is in use
Get-NetTCPConnection -LocalPort 8000

# Kill process on port 8000
Stop-Process -Id (Get-NetTCPConnection -LocalPort 8000).OwningProcess -Force

# Check database connection
docker exec erp_postgres psql -U erp_user -d erp_demo -c "SELECT 1"

# View backend logs
Get-Content -Path "erp-softtoys\logs\app.log" -Tail 50

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Frontend Won't Start

```powershell
# Check Node version
node --version  # Should be 18+

# Clear npm cache
npm cache clean --force

# Delete and reinstall
Remove-Item -Path node_modules -Recurse -Force
Remove-Item -Path package-lock.json -Force
npm install

# Check if port 5173 is in use
Get-NetTCPConnection -LocalPort 5173

# Try different port
npm run dev -- --port 5174
```

### Database Issues

```powershell
# Reset database
docker-compose down -v  # WARNING: Deletes all data!
docker-compose up -d postgres

# Wait and re-migrate
Start-Sleep -Seconds 10
cd erp-softtoys
alembic upgrade head
python scripts/seed_demo_data.py

# Check database logs
docker-compose logs postgres

# Connect to database directly
docker exec -it erp_postgres psql -U erp_user -d erp_demo
# Then run SQL: \dt (list tables)
```

### Cannot Login

```powershell
# Verify user exists
docker exec -it erp_postgres psql -U erp_user -d erp_demo -c "SELECT username, email, role FROM users;"

# Reset admin password
cd erp-softtoys
python -c "
from app.core.database import SessionLocal
from app.core.models.users import User
from app.core.security import PasswordUtils

db = SessionLocal()
admin = db.query(User).filter_by(username='admin').first()
if admin:
    admin.hashed_password = PasswordUtils.hash_password('admin123')
    db.commit()
    print('✅ Admin password reset to: admin123')
else:
    print('❌ Admin user not found')
db.close()
"
```

### CORS Error

```python
# File: erp-softtoys/app/main.py
# Add CORS middleware (should already exist)

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 📊 TESTING

### Backend API Testing

```powershell
# Manual test with curl
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/login" `
    -Method POST `
    -Body '{"username":"admin","password":"admin123"}' `
    -ContentType "application/json"

# Automated tests
cd erp-softtoys
pytest tests/ -v

# Test specific module
pytest tests/test_auth.py -v

# Coverage report
pytest tests/ --cov=app --cov-report=html
```

### Frontend Testing

```powershell
# Manual test: Open browser
Start-Process "http://localhost:5173"

# Check console for errors (F12 in browser)

# Network tab: Verify API calls succeed (200 status)
```

### Load Testing

```python
# File: tests/load_test_login.py
import requests
import time
from concurrent.futures import ThreadPoolExecutor

BASE_URL = "http://localhost:8000"

def test_login(user_id):
    """Test login endpoint"""
    start = time.time()
    response = requests.post(
        f"{BASE_URL}/api/v1/auth/login",
        json={"username": "admin", "password": "admin123"}
    )
    duration = time.time() - start
    
    return {
        "user_id": user_id,
        "status": response.status_code,
        "duration": duration
    }

def run_load_test(num_users=10):
    """Simulate multiple concurrent users"""
    with ThreadPoolExecutor(max_workers=num_users) as executor:
        results = list(executor.map(test_login, range(num_users)))
    
    # Calculate stats
    success_count = sum(1 for r in results if r["status"] == 200)
    avg_duration = sum(r["duration"] for r in results) / len(results)
    
    print(f"✅ Success: {success_count}/{num_users}")
    print(f"⏱️  Avg Duration: {avg_duration:.2f}s")

if __name__ == "__main__":
    run_load_test(10)  # Test with 10 concurrent users
```

---

## 🚀 DEPLOYMENT

### Build Production Images

```powershell
# Backend
cd erp-softtoys
docker build -t erp-backend:latest .

# Frontend
cd ..\erp-ui\frontend
docker build -t erp-frontend:latest .

# Verify images
docker images | Select-String "erp-"
```

### Deploy to Staging

```powershell
# File: deploy-staging.ps1
$SERVER_IP = "192.168.1.100"
$SERVER_USER = "ubuntu"

Write-Host "🚀 Deploying to staging..." -ForegroundColor Green

# Build images
docker-compose -f docker-compose.staging.yml build

# Push to registry (if using registry)
# docker-compose -f docker-compose.staging.yml push

# Copy to server (alternative to registry)
docker save erp-backend:latest | ssh $SERVER_USER@$SERVER_IP "docker load"
docker save erp-frontend:latest | ssh $SERVER_USER@$SERVER_IP "docker load"

# Deploy on server
ssh $SERVER_USER@$SERVER_IP @"
cd /var/www/erp-demo
docker-compose down
docker-compose up -d
docker-compose exec backend alembic upgrade head
docker-compose exec backend python scripts/seed_demo_data.py
"@

Write-Host "✅ Deployed to http://$SERVER_IP" -ForegroundColor Green
```

---

## 📚 HELPFUL COMMANDS

### Docker Commands

```powershell
# View running containers
docker-compose ps

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Restart service
docker-compose restart backend

# Rebuild and restart
docker-compose up -d --build backend

# Stop all services
docker-compose down

# Clean up (DELETE ALL DATA)
docker-compose down -v
```

### Database Commands

```powershell
# Connect to database
docker exec -it erp_postgres psql -U erp_user -d erp_demo

# Inside psql:
# \dt              # List tables
# \d users         # Describe users table
# SELECT * FROM users LIMIT 5;
# \q               # Quit
```

### Git Commands

```powershell
# Check status
git status

# Commit changes
git add .
git commit -m "Add new feature"

# Push to remote
git push origin main

# Pull latest changes
git pull origin main

# Create new branch
git checkout -b feature/new-feature
```

---

## 🎯 NEXT STEPS

After setup works:

1. **Read the full plan**: [LIVE_DEMO_PROTOTYPE_PLAN.md](LIVE_DEMO_PROTOTYPE_PLAN.md)
2. **Follow Phase 1**: Days 1-10 (Foundation)
3. **Implement Phase 2**: Days 11-24 (Core Features)
4. **Testing Phase 3**: Days 25-36 (Testing & Deployment)

---

## 📞 SUPPORT

### Documentation
- Main Plan: `LIVE_DEMO_PROTOTYPE_PLAN.md`
- Architecture: `images/02-ARCHITECTURE-DIAGRAM.md`
- Workflow: `images/03-PRODUCTION-WORKFLOW.md`
- API Docs: `http://localhost:8000/docs`

### Debugging
- Backend logs: `erp-softtoys/logs/`
- Frontend console: Browser DevTools (F12)
- Database logs: `docker-compose logs postgres`

### Getting Help
1. Check this Quick Start guide
2. Review error messages carefully
3. Search in documentation
4. Check GitHub issues
5. Ask Claude Sonnet 4.5 with context

---

**Last Updated**: 3 Februari 2026  
**Version**: 1.0  
**For**: Claude Sonnet 4.5 & Human Developers

🚀 **HAPPY CODING!**
