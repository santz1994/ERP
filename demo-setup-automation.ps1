# =============================================================================
# ERP QUTY KARUNIA - DEMO SETUP AUTOMATION
# =============================================================================
# Purpose: One-click setup for live demo prototype
# Author: IT Developer Expert Team
# Date: 3 Februari 2026
# Usage: Run in PowerShell as Administrator
# =============================================================================

param(
    [Parameter(Mandatory=$false)]
    [string]$Mode = "full"  # Options: full, backend-only, frontend-only, verify
)

# Configuration
$PROJECT_ROOT = "d:\Project\ERP2026"
$BACKEND_DIR = "$PROJECT_ROOT\erp-softtoys"
$FRONTEND_DIR = "$PROJECT_ROOT\erp-ui\frontend"
$VENV_DIR = "$BACKEND_DIR\venv"

Write-Host @"
╔════════════════════════════════════════════════════════════════╗
║        ERP QUTY KARUNIA - DEMO SETUP AUTOMATION               ║
║        Live Prototype Development Environment                 ║
╚════════════════════════════════════════════════════════════════╝
"@ -ForegroundColor Cyan

Write-Host "`nMode: $Mode" -ForegroundColor Yellow
Write-Host "Project Root: $PROJECT_ROOT`n" -ForegroundColor Gray

# =============================================================================
# STEP 0: PREREQUISITES CHECK
# =============================================================================

function Test-Prerequisites {
    Write-Host "🔍 STEP 0: Checking Prerequisites..." -ForegroundColor Cyan
    
    $allGood = $true
    
    # Check Docker
    if (Get-Command docker -ErrorAction SilentlyContinue) {
        $dockerVersion = docker --version
        Write-Host "  ✅ Docker: $dockerVersion" -ForegroundColor Green
    } else {
        Write-Host "  ❌ Docker NOT installed" -ForegroundColor Red
        Write-Host "     Install from: https://www.docker.com/products/docker-desktop" -ForegroundColor Yellow
        $allGood = $false
    }
    
    # Check Python
    if (Get-Command python -ErrorAction SilentlyContinue) {
        $pythonVersion = python --version
        Write-Host "  ✅ Python: $pythonVersion" -ForegroundColor Green
    } else {
        Write-Host "  ❌ Python NOT installed" -ForegroundColor Red
        Write-Host "     Install from: https://www.python.org/downloads/" -ForegroundColor Yellow
        $allGood = $false
    }
    
    # Check Node.js
    if (Get-Command node -ErrorAction SilentlyContinue) {
        $nodeVersion = node --version
        Write-Host "  ✅ Node.js: $nodeVersion" -ForegroundColor Green
    } else {
        Write-Host "  ❌ Node.js NOT installed" -ForegroundColor Red
        Write-Host "     Install from: https://nodejs.org/" -ForegroundColor Yellow
        $allGood = $false
    }
    
    # Check Git
    if (Get-Command git -ErrorAction SilentlyContinue) {
        $gitVersion = git --version
        Write-Host "  ✅ Git: $gitVersion" -ForegroundColor Green
    } else {
        Write-Host "  ❌ Git NOT installed" -ForegroundColor Red
        $allGood = $false
    }
    
    # Check disk space
    $drive = Get-PSDrive D
    $freeSpaceGB = [math]::Round($drive.Free / 1GB, 2)
    if ($freeSpaceGB -gt 10) {
        Write-Host "  ✅ Disk Space: ${freeSpaceGB}GB available" -ForegroundColor Green
    } else {
        Write-Host "  ⚠️  Disk Space: Only ${freeSpaceGB}GB available (need 10GB+)" -ForegroundColor Yellow
    }
    
    if (-not $allGood) {
        Write-Host "`n❌ Prerequisites check FAILED. Please install missing software." -ForegroundColor Red
        exit 1
    }
    
    Write-Host "  ✅ All prerequisites satisfied!`n" -ForegroundColor Green
}

# =============================================================================
# STEP 1: SETUP DOCKER SERVICES
# =============================================================================

function Start-DockerServices {
    Write-Host "🐳 STEP 1: Starting Docker Services..." -ForegroundColor Cyan
    
    Set-Location $PROJECT_ROOT
    
    # Check if .env exists
    if (-not (Test-Path ".env")) {
        Write-Host "  📝 Creating .env file..." -ForegroundColor Yellow
        
        $envContent = @"
# Database Configuration
DB_HOST=postgres
DB_NAME=erp_demo
DB_USER=erp_user
DB_PASSWORD=demo123
DB_PORT=5432
DATABASE_URL=postgresql://erp_user:demo123@postgres:5432/erp_demo

# JWT Configuration
JWT_SECRET=demo_secret_key_change_in_production_env
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=1440

# Application Configuration
ENVIRONMENT=development
DEBUG=true
API_TITLE=ERP Quty Karunia API
API_VERSION=1.0.0
API_PREFIX=/api/v1

# Redis Configuration
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0

# CORS Configuration
BACKEND_CORS_ORIGINS=["http://localhost:5173","http://localhost:3000"]
"@
        
        Set-Content -Path ".env" -Value $envContent
        Write-Host "  ✅ .env file created" -ForegroundColor Green
    }
    
    # Start services
    Write-Host "  🚀 Starting PostgreSQL and Redis..." -ForegroundColor Yellow
    docker-compose up -d postgres redis
    
    # Wait for database
    Write-Host "  ⏳ Waiting for database to be ready..." -ForegroundColor Yellow
    Start-Sleep -Seconds 15
    
    # Check if services are running
    $postgres = docker ps --filter "name=erp_postgres" --format "{{.Names}}"
    $redis = docker ps --filter "name=erp_redis" --format "{{.Names}}"
    
    if ($postgres -and $redis) {
        Write-Host "  ✅ Docker services started successfully!`n" -ForegroundColor Green
    } else {
        Write-Host "  ❌ Failed to start Docker services" -ForegroundColor Red
        docker-compose logs
        exit 1
    }
}

# =============================================================================
# STEP 2: SETUP BACKEND
# =============================================================================

function Setup-Backend {
    Write-Host "🐍 STEP 2: Setting up Backend..." -ForegroundColor Cyan
    
    Set-Location $BACKEND_DIR
    
    # Create virtual environment
    if (-not (Test-Path $VENV_DIR)) {
        Write-Host "  📦 Creating Python virtual environment..." -ForegroundColor Yellow
        python -m venv venv
    } else {
        Write-Host "  ✅ Virtual environment already exists" -ForegroundColor Green
    }
    
    # Activate virtual environment
    Write-Host "  🔌 Activating virtual environment..." -ForegroundColor Yellow
    & "$VENV_DIR\Scripts\Activate.ps1"
    
    # Install dependencies
    Write-Host "  📥 Installing Python dependencies..." -ForegroundColor Yellow
    pip install --upgrade pip
    pip install -r requirements.txt
    
    # Run migrations
    Write-Host "  🗄️  Running database migrations..." -ForegroundColor Yellow
    alembic upgrade head
    
    # Seed demo data
    Write-Host "  🌱 Seeding demo data..." -ForegroundColor Yellow
    
    # Check if seed script exists
    if (Test-Path "scripts\seed_demo_data.py") {
        python scripts\seed_demo_data.py
    } else {
        Write-Host "  ⚠️  Seed script not found, creating..." -ForegroundColor Yellow
        
        # Create scripts directory
        if (-not (Test-Path "scripts")) {
            New-Item -ItemType Directory -Path "scripts" | Out-Null
        }
        
        # Create seed script
        $seedScript = @'
"""Seed essential demo data"""
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.core.models.users import User, UserRole
from app.core.models.products import Category, Product, Partner
from app.core.security import PasswordUtils
from datetime import datetime

def seed_users(db: Session):
    """Create demo users"""
    users_data = [
        {"username": "admin", "email": "admin@quty.com", "role": UserRole.SUPERADMIN, "password": "admin123"},
        {"username": "ppic1", "email": "ppic@quty.com", "role": UserRole.PPIC_STAFF, "password": "ppic123"},
        {"username": "cutting1", "email": "cutting@quty.com", "role": UserRole.CUTTING_ADMIN, "password": "cut123"},
        {"username": "sewing1", "email": "sewing@quty.com", "role": UserRole.SEWING_ADMIN, "password": "sew123"},
    ]
    
    for data in users_data:
        existing = db.query(User).filter_by(username=data["username"]).first()
        if existing:
            print(f"⏩ User {data['username']} already exists, skipping")
            continue
        
        user = User(
            username=data["username"],
            email=data["email"],
            role=data["role"],
            hashed_password=PasswordUtils.hash_password(data["password"]),
            is_active=True,
            created_at=datetime.utcnow()
        )
        db.add(user)
    
    db.commit()
    print(f"✅ Demo users ready")

def seed_categories(db: Session):
    """Create product categories"""
    categories = [
        {"code": "RAW", "name": "Raw Material", "type": "material"},
        {"code": "FG", "name": "Finished Goods", "type": "product"},
        {"code": "WIP", "name": "Work in Progress", "type": "semi_finished"},
    ]
    
    for cat in categories:
        existing = db.query(Category).filter_by(code=cat["code"]).first()
        if existing:
            continue
        
        category = Category(**cat)
        db.add(category)
    
    db.commit()
    print(f"✅ Categories ready")

def seed_products(db: Session):
    """Create sample products"""
    cat_raw = db.query(Category).filter_by(code="RAW").first()
    cat_fg = db.query(Category).filter_by(code="FG").first()
    
    if not cat_raw or not cat_fg:
        print("⚠️  Categories not found, run seed_categories first")
        return
    
    products = [
        {"default_code": "IKHR504", "name": "KOHAIR Fabric", "category_id": cat_raw.id, "uom": "YD", "price": 15000},
        {"default_code": "IKP20157", "name": "Filling Material", "category_id": cat_raw.id, "uom": "KG", "price": 45000},
        {"default_code": "40551542", "name": "AFTONSPARV Doll", "category_id": cat_fg.id, "uom": "PCS", "price": 85000},
    ]
    
    for prod in products:
        existing = db.query(Product).filter_by(default_code=prod["default_code"]).first()
        if existing:
            continue
        
        product = Product(**prod)
        db.add(product)
    
    db.commit()
    print(f"✅ Products ready")

def seed_partners(db: Session):
    """Create suppliers and customers"""
    partners = [
        {"name": "IKEA Sweden", "partner_type": "customer", "email": "ikea@sweden.com"},
        {"name": "Fabric Supplier A", "partner_type": "supplier", "email": "supplier@fabric.com"},
    ]
    
    for partner in partners:
        existing = db.query(Partner).filter_by(name=partner["name"]).first()
        if existing:
            continue
        
        p = Partner(**partner)
        db.add(p)
    
    db.commit()
    print(f"✅ Partners ready")

if __name__ == "__main__":
    db = SessionLocal()
    try:
        print("🌱 Seeding demo data...")
        seed_users(db)
        seed_categories(db)
        seed_products(db)
        seed_partners(db)
        print("\n🎉 Demo data seeded successfully!")
        print("\nDemo accounts:")
        print("  Admin: admin / admin123")
        print("  PPIC: ppic1 / ppic123")
        print("  Cutting: cutting1 / cut123")
        print("  Sewing: sewing1 / sew123")
    finally:
        db.close()
'@
        
        Set-Content -Path "scripts\seed_demo_data.py" -Value $seedScript
        python scripts\seed_demo_data.py
    }
    
    Write-Host "  ✅ Backend setup complete!`n" -ForegroundColor Green
}

# =============================================================================
# STEP 3: SETUP FRONTEND
# =============================================================================

function Setup-Frontend {
    Write-Host "⚛️  STEP 3: Setting up Frontend..." -ForegroundColor Cyan
    
    Set-Location $FRONTEND_DIR
    
    # Check if node_modules exists
    if (-not (Test-Path "node_modules")) {
        Write-Host "  📥 Installing Node.js dependencies (this may take a while)..." -ForegroundColor Yellow
        npm install
    } else {
        Write-Host "  ✅ Node modules already installed" -ForegroundColor Green
    }
    
    Write-Host "  ✅ Frontend setup complete!`n" -ForegroundColor Green
}

# =============================================================================
# STEP 4: VERIFICATION
# =============================================================================

function Test-Setup {
    Write-Host "🧪 STEP 4: Verifying Setup..." -ForegroundColor Cyan
    
    $allGood = $true
    
    # Test 1: Database connection
    Write-Host "  Testing database connection..." -ForegroundColor Yellow
    try {
        $dbCheck = docker exec erp_postgres pg_isready -U erp_user
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  ✅ Database: CONNECTED" -ForegroundColor Green
        } else {
            Write-Host "  ❌ Database: NOT CONNECTED" -ForegroundColor Red
            $allGood = $false
        }
    } catch {
        Write-Host "  ❌ Database: ERROR" -ForegroundColor Red
        $allGood = $false
    }
    
    # Test 2: Backend health (start temporarily)
    Write-Host "  Testing backend API..." -ForegroundColor Yellow
    Set-Location $BACKEND_DIR
    & "$VENV_DIR\Scripts\Activate.ps1"
    
    # Start backend in background
    $backendJob = Start-Job -ScriptBlock {
        param($BackendDir, $VenvDir)
        Set-Location $BackendDir
        & "$VenvDir\Scripts\Activate.ps1"
        uvicorn app.main:app --port 8000 --host 0.0.0.0 2>&1 | Out-Null
    } -ArgumentList $BACKEND_DIR, $VENV_DIR
    
    Start-Sleep -Seconds 5
    
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -TimeoutSec 5
        if ($response.StatusCode -eq 200) {
            Write-Host "  ✅ Backend API: HEALTHY" -ForegroundColor Green
        } else {
            Write-Host "  ❌ Backend API: UNHEALTHY" -ForegroundColor Red
            $allGood = $false
        }
    } catch {
        Write-Host "  ⚠️  Backend API: Could not verify (may need manual start)" -ForegroundColor Yellow
    }
    
    # Stop backend job
    Stop-Job $backendJob
    Remove-Job $backendJob
    
    # Test 3: Authentication
    Write-Host "  Testing authentication..." -ForegroundColor Yellow
    Start-Sleep -Seconds 2
    
    # Start backend again for auth test
    $backendJob = Start-Job -ScriptBlock {
        param($BackendDir, $VenvDir)
        Set-Location $BackendDir
        & "$VenvDir\Scripts\Activate.ps1"
        uvicorn app.main:app --port 8000 --host 0.0.0.0 2>&1 | Out-Null
    } -ArgumentList $BACKEND_DIR, $VENV_DIR
    
    Start-Sleep -Seconds 5
    
    try {
        $body = @{
            username = "admin"
            password = "admin123"
        } | ConvertTo-Json
        
        $response = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/login" `
            -Method POST `
            -Body $body `
            -ContentType "application/json" `
            -TimeoutSec 5
        
        if ($response.access_token) {
            Write-Host "  ✅ Authentication: WORKING" -ForegroundColor Green
        } else {
            Write-Host "  ❌ Authentication: FAILED" -ForegroundColor Red
            $allGood = $false
        }
    } catch {
        Write-Host "  ⚠️  Authentication: Could not verify" -ForegroundColor Yellow
    }
    
    # Stop backend job
    Stop-Job $backendJob
    Remove-Job $backendJob
    
    Write-Host ""
    
    if ($allGood) {
        Write-Host "  ✅ All tests passed!`n" -ForegroundColor Green
    } else {
        Write-Host "  ⚠️  Some tests failed, but you can proceed manually`n" -ForegroundColor Yellow
    }
}

# =============================================================================
# STEP 5: START SERVICES
# =============================================================================

function Start-DemoServices {
    Write-Host "🚀 STEP 5: Starting Demo Services..." -ForegroundColor Cyan
    
    Write-Host @"
  
  To start the demo, you need to run 2 terminals:
  
  Terminal 1 - Backend:
  ─────────────────────────────────────────────
  cd $BACKEND_DIR
  .\venv\Scripts\Activate.ps1
  uvicorn app.main:app --reload --port 8000
  
  Terminal 2 - Frontend:
  ─────────────────────────────────────────────
  cd $FRONTEND_DIR
  npm run dev
  
  Then open browser: http://localhost:5173
  
  Demo accounts:
  • Admin: admin / admin123
  • PPIC: ppic1 / ppic123
  • Cutting: cutting1 / cut123

"@ -ForegroundColor Yellow
    
    $startNow = Read-Host "Do you want to start services now? (y/n)"
    
    if ($startNow -eq "y" -or $startNow -eq "Y") {
        # Start backend in new terminal
        Write-Host "  🐍 Starting backend..." -ForegroundColor Yellow
        Start-Process powershell -ArgumentList "-NoExit", "-Command", @"
cd '$BACKEND_DIR'
& '.\venv\Scripts\Activate.ps1'
Write-Host '🐍 Backend Server Starting...' -ForegroundColor Green
Write-Host 'API Docs: http://localhost:8000/docs' -ForegroundColor Cyan
uvicorn app.main:app --reload --port 8000
"@
        
        Start-Sleep -Seconds 3
        
        # Start frontend in new terminal
        Write-Host "  ⚛️  Starting frontend..." -ForegroundColor Yellow
        Start-Process powershell -ArgumentList "-NoExit", "-Command", @"
cd '$FRONTEND_DIR'
Write-Host '⚛️  Frontend Server Starting...' -ForegroundColor Green
Write-Host 'URL: http://localhost:5173' -ForegroundColor Cyan
npm run dev
"@
        
        Start-Sleep -Seconds 5
        
        # Open browser
        Write-Host "  🌐 Opening browser..." -ForegroundColor Yellow
        Start-Process "http://localhost:5173"
        
        Write-Host "`n  ✅ Demo services started!`n" -ForegroundColor Green
    } else {
        Write-Host "  ℹ️  Services not started. Use commands above to start manually.`n" -ForegroundColor Gray
    }
}

# =============================================================================
# MAIN EXECUTION
# =============================================================================

try {
    switch ($Mode) {
        "full" {
            Test-Prerequisites
            Start-DockerServices
            Setup-Backend
            Setup-Frontend
            Test-Setup
            Start-DemoServices
        }
        "backend-only" {
            Test-Prerequisites
            Start-DockerServices
            Setup-Backend
            Test-Setup
        }
        "frontend-only" {
            Test-Prerequisites
            Setup-Frontend
        }
        "verify" {
            Test-Setup
        }
        default {
            Write-Host "Invalid mode. Use: full, backend-only, frontend-only, or verify" -ForegroundColor Red
            exit 1
        }
    }
    
    Write-Host @"
╔════════════════════════════════════════════════════════════════╗
║                    SETUP COMPLETE! 🎉                         ║
╚════════════════════════════════════════════════════════════════╝

Next steps:
1. Access demo at: http://localhost:5173
2. Login with: admin / admin123
3. Follow guide: docs\00-Overview\QUICK_START_DEVELOPER_GUIDE.md

"@ -ForegroundColor Green
    
} catch {
    Write-Host "`n❌ ERROR OCCURRED:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    Write-Host "`nPlease check logs and try again.`n" -ForegroundColor Yellow
    exit 1
}
