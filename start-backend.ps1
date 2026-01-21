# Start Backend Server
Write-Host "Starting ERP Backend Server..." -ForegroundColor Green

# Navigate to backend directory
Set-Location "d:\Project\ERP2026\erp-softtoys"

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1

# Start uvicorn
Write-Host "Starting Uvicorn on http://localhost:8000..." -ForegroundColor Yellow
Write-Host "API Docs: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "Press CTRL+C to stop" -ForegroundColor Red
Write-Host ""

uvicorn app.main:app --reload --port 8000 --host 0.0.0.0
