# Start Frontend Development Server
Write-Host "Starting ERP Frontend (React + Vite)..." -ForegroundColor Green

# Navigate to frontend directory
Set-Location "d:\Project\ERP2026\erp-ui\frontend"

# Check if node_modules exists
if (-not (Test-Path "node_modules")) {
    Write-Host "Installing dependencies..." -ForegroundColor Yellow
    npm install
}

# Start Vite dev server
Write-Host "Starting Vite on http://localhost:3001..." -ForegroundColor Yellow
Write-Host "Press CTRL+C to stop" -ForegroundColor Red
Write-Host ""

npm run dev
