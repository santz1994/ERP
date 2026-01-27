# Setup PostgreSQL 18.1-2 Local Database for ERP
# Author: ERP Setup
# Date: 2026-01-27

$env:PGPASSWORD = "password123"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "PostgreSQL 18.1-2 Local Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# 1. Verify PostgreSQL Connection
Write-Host "`n[1/5] Verifying PostgreSQL Connection..." -ForegroundColor Yellow
$version = psql -U postgres -h localhost -t -c "SELECT version();"
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Connected Successfully!" -ForegroundColor Green
    Write-Host "Version: $version" -ForegroundColor Green
} else {
    Write-Host "❌ Connection Failed!" -ForegroundColor Red
    exit 1
}

# 2. Create Database
Write-Host "`n[2/5] Creating Database 'erp_quty_karunia'..." -ForegroundColor Yellow
psql -U postgres -h localhost -c "SELECT 1 FROM pg_database WHERE datname = 'erp_quty_karunia';" | Out-Null
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Database already exists" -ForegroundColor Green
} else {
    psql -U postgres -h localhost -c "CREATE DATABASE erp_quty_karunia;"
    Write-Host "✅ Database created" -ForegroundColor Green
}

# 3. Create Extensions
Write-Host "`n[3/5] Installing Extensions..." -ForegroundColor Yellow
psql -U postgres -h localhost -d erp_quty_karunia -c "
CREATE EXTENSION IF NOT EXISTS uuid-ossp;
CREATE EXTENSION IF NOT EXISTS pgcrypto;
SELECT 'Extensions created' as status;
"
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Extensions installed" -ForegroundColor Green
}

# 4. Verify Extensions
Write-Host "`n[4/5] Verifying Extensions..." -ForegroundColor Yellow
$extensions = psql -U postgres -h localhost -d erp_quty_karunia -t -c "SELECT extname FROM pg_extension ORDER BY extname;"
Write-Host "Available Extensions:" -ForegroundColor Green
Write-Host $extensions -ForegroundColor Green

# 5. Test Connection with Python
Write-Host "`n[5/5] Testing Python Connection..." -ForegroundColor Yellow
$testScript = @"
import os
import psycopg
from dotenv import load_dotenv

load_dotenv()

try:
    db_url = os.getenv('DATABASE_URL')
    print(f"Connecting to: {db_url.split('@')[1]}")
    
    with psycopg.connect(os.getenv('DATABASE_URL')) as conn:
        with conn.cursor() as cur:
            cur.execute('SELECT version();')
            version = cur.fetchone()[0]
            print(f"✅ Python Connection Successful!")
            print(f"PostgreSQL: {version[:50]}...")
except Exception as e:
    print(f"❌ Connection Failed: {e}")
    exit(1)
"@

# Save and run test
$testScript | Out-File -FilePath "test_db_connection.py" -Encoding UTF8
python test_db_connection.py

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ All checks passed!" -ForegroundColor Green
} else {
    Write-Host "⚠️  Python connection test failed - check dependencies" -ForegroundColor Yellow
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "PostgreSQL Setup Complete!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Cleanup
Remove-Item "test_db_connection.py" -Force -ErrorAction SilentlyContinue
