# Install All Dependencies Script
Write-Host "Installing ERP Backend Dependencies..." -ForegroundColor Green

# Stop any running uvicorn processes
Write-Host "Stopping running Python processes..." -ForegroundColor Yellow
Get-Process | Where-Object {$_.Path -like "*erp-softtoys\venv*"} | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2

# Navigate to backend directory
Set-Location "d:\Project\ERP2026\erp-softtoys"

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1

# Install requirements
Write-Host "Installing requirements.txt..." -ForegroundColor Cyan
pip install -r requirements.txt

Write-Host "`nInstallation complete!" -ForegroundColor Green
Write-Host "You can now run: uvicorn app.main:app --reload --port 8000" -ForegroundColor Cyan
