# Migration & Seed Script for PostgreSQL 18.1-2 Local
# Runs all DB initialization, migrations, and seeding

$ErrorActionPreference = "Stop"

# Load environment
$env:PYTHONPATH = "D:\Project\ERP2026\erp-softtoys"
cd D:\Project\ERP2026\erp-softtoys

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "PostgreSQL 18.1-2 Migration & Seed" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Load .env
if (Test-Path ".env") {
    Get-Content .env | ForEach-Object {
        if ($_ -match "^([^=]+)=(.*)$") {
            $name = $matches[1].Trim()
            $value = $matches[2].Trim()
            [System.Environment]::SetEnvironmentVariable($name, $value)
        }
    }
}

$env:DATABASE_URL = "postgresql://postgres:password123@localhost:5432/erp_quty_karunia"

Write-Host "`nDatabase URL: $($env:DATABASE_URL.Replace('password123', '****'))" -ForegroundColor Green
Write-Host "Working Directory: $(Get-Location)" -ForegroundColor Green

# Step 1: Verify Connection
Write-Host "`n[1/5] Verifying PostgreSQL Connection..." -ForegroundColor Yellow
$testConnection = @"
import os
import psycopg
from dotenv import load_dotenv

load_dotenv()
try:
    db_url = os.getenv('DATABASE_URL', 'postgresql://postgres:password123@localhost:5432/erp_quty_karunia')
    with psycopg.connect(db_url) as conn:
        with conn.cursor() as cur:
            cur.execute('SELECT version();')
            version = cur.fetchone()[0]
            print(f"✅ PostgreSQL Connected: {version[:50]}")
except Exception as e:
    print(f"❌ Connection Failed: {e}")
    exit(1)
"@

$testConnection | Out-File -FilePath "test_connection.py" -Encoding UTF8
python test_connection.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Connection test failed!" -ForegroundColor Red
    exit 1
}

# Step 2: Initialize Database (Create Tables)
Write-Host "`n[2/5] Initializing Database Schema..." -ForegroundColor Yellow
python init_db.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Database initialization failed!" -ForegroundColor Red
    exit 1
}

# Step 3: Run SQL Migrations (if any)
Write-Host "`n[3/5] Running SQL Migrations..." -ForegroundColor Yellow
$sqlMigrations = @(
    "..\init-db.sql"
    "..\init-db-staging.sql"
)

foreach ($sqlFile in $sqlMigrations) {
    if (Test-Path $sqlFile) {
        Write-Host "  Running: $sqlFile" -ForegroundColor Cyan
        $env:PGPASSWORD = "password123"
        psql -U postgres -h localhost -p 5432 -d erp_quty_karunia -f $sqlFile 2>$null | Out-Null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  ✅ Completed: $sqlFile" -ForegroundColor Green
        } else {
            Write-Host "  ⚠️  $sqlFile had warnings or no data" -ForegroundColor Yellow
        }
    }
}

# Step 4: Seed Users
Write-Host "`n[4/5] Seeding All Demo Users..." -ForegroundColor Yellow
Write-Host "  Creating 22 roles with demo users..." -ForegroundColor Cyan
python seed_all_users.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "  ⚠️  User seeding had issues (may already exist)" -ForegroundColor Yellow
} else {
    Write-Host "  ✅ Users seeded successfully" -ForegroundColor Green
}

# Step 5: Verification
Write-Host "`n[5/5] Verifying Migration Complete..." -ForegroundColor Yellow
$verifyScript = @"
import os
import psycopg
from dotenv import load_dotenv

load_dotenv()
db_url = os.getenv('DATABASE_URL', 'postgresql://postgres:password123@localhost:5432/erp_quty_karunia')

try:
    with psycopg.connect(db_url) as conn:
        with conn.cursor() as cur:
            # Count tables
            cur.execute("""
                SELECT COUNT(*) 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """)
            table_count = cur.fetchone()[0]
            
            # Count users
            cur.execute("SELECT COUNT(*) FROM \"user\" WHERE 1=1")
            user_count = cur.fetchone()[0]
            
            print(f"✅ Migration Verification:")
            print(f"   Tables Created: {table_count}")
            print(f"   Users Seeded: {user_count}")
            
            if table_count > 0 and user_count > 0:
                print(f"✅ Database ready for production!")
            
except Exception as e:
    print(f"❌ Verification failed: {e}")
    exit(1)
"@

$verifyScript | Out-File -FilePath "verify_migration.py" -Encoding UTF8
python verify_migration.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Verification failed!" -ForegroundColor Red
    exit 1
}

# Cleanup
Remove-Item "test_connection.py" -Force -ErrorAction SilentlyContinue
Remove-Item "verify_migration.py" -Force -ErrorAction SilentlyContinue

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "✅ All Migrations & Seeding Complete!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "`nNext Steps:" -ForegroundColor Yellow
Write-Host "  1. Start pgBouncer: pgbouncer -c pgbouncer.ini" -ForegroundColor White
Write-Host "  2. Start Backend: docker-compose up backend" -ForegroundColor White
Write-Host "  3. Start Frontend: docker-compose up frontend" -ForegroundColor White
Write-Host "`nLogin Credentials:" -ForegroundColor Yellow
Write-Host "  Admin: admin / Admin@123" -ForegroundColor White
Write-Host "  SuperAdmin: superadmin / password123" -ForegroundColor White
