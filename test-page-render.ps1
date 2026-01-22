# Test Page Rendering in Browser
$frontendUrl = "http://localhost:3001"
$baseUrl = "http://localhost:8000/api/v1"

# Login first
$loginResponse = Invoke-WebRequest -Uri "$baseUrl/auth/login" -Method POST -Body (@{username="admin"; password="Admin@123456"} | ConvertTo-Json) -ContentType "application/json" -UseBasicParsing
$loginData = $loginResponse.Content | ConvertFrom-Json
$token = $loginData.access_token

Write-Host "Testing Page Data Endpoints:" -ForegroundColor Cyan
Write-Host ""

# Test Dashboard data
Write-Host "[1] Dashboard Page - Testing /dashboard/stats" -ForegroundColor Yellow
try {
    $dashStats = Invoke-WebRequest -Uri "$baseUrl/dashboard/stats" -Headers @{"Authorization"="Bearer $token"} -UseBasicParsing
    Write-Host "  [OK] Dashboard stats: $($dashStats.StatusCode)" -ForegroundColor Green
    $dashData = $dashStats.Content | ConvertFrom-Json
    Write-Host "  - Total MOs: $($dashData.total_mos)" -ForegroundColor Gray
} catch {
    Write-Host "  [FAIL] Dashboard stats: $($_.Exception.Message)" -ForegroundColor Red
}

# Test PPIC data
Write-Host "`n[2] PPIC Page - Testing /ppic/manufacturing-orders" -ForegroundColor Yellow
try {
    $ppicData = Invoke-WebRequest -Uri "$baseUrl/ppic/manufacturing-orders" -Headers @{"Authorization"="Bearer $token"} -UseBasicParsing
    Write-Host "  [OK] PPIC data: $($ppicData.StatusCode)" -ForegroundColor Green
    $mos = $ppicData.Content | ConvertFrom-Json
    Write-Host "  - Manufacturing Orders: $($mos.Count)" -ForegroundColor Gray
} catch {
    Write-Host "  [FAIL] PPIC data: $($_.Exception.Message)" -ForegroundColor Red
}

# Test Sewing data
Write-Host "`n[3] Sewing Page - Testing /sewing/work-orders" -ForegroundColor Yellow
try {
    $sewingData = Invoke-WebRequest -Uri "$baseUrl/sewing/work-orders" -Headers @{"Authorization"="Bearer $token"} -UseBasicParsing
    Write-Host "  [OK] Sewing data: $($sewingData.StatusCode)" -ForegroundColor Green
    $wos = $sewingData.Content | ConvertFrom-Json
    Write-Host "  - Work Orders: $($wos.Count)" -ForegroundColor Gray
} catch {
    Write-Host "  [FAIL] Sewing data: $($_.Exception.Response.StatusCode) - $($_.Exception.Message)" -ForegroundColor Red
}

# Test Cutting data
Write-Host "`n[4] Cutting Page - Testing /cutting/work-orders" -ForegroundColor Yellow
try {
    $cuttingData = Invoke-WebRequest -Uri "$baseUrl/cutting/work-orders" -Headers @{"Authorization"="Bearer $token"} -UseBasicParsing
    Write-Host "  [OK] Cutting data: $($cuttingData.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "  [FAIL] Cutting data: $($_.Exception.Response.StatusCode)" -ForegroundColor Red
}

# Test Warehouse data
Write-Host "`n[5] Warehouse Page - Testing /warehouse/materials" -ForegroundColor Yellow
try {
    $warehouseData = Invoke-WebRequest -Uri "$baseUrl/warehouse/materials" -Headers @{"Authorization"="Bearer $token"} -UseBasicParsing
    Write-Host "  [OK] Warehouse data: $($warehouseData.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "  [FAIL] Warehouse data: $($_.Exception.Response.StatusCode)" -ForegroundColor Red
}

Write-Host "`n======================================" -ForegroundColor Cyan
Write-Host "BROWSER CONSOLE CHECK:" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host "1. Open browser DevTools (F12)" -ForegroundColor Yellow
Write-Host "2. Go to Console tab" -ForegroundColor Yellow
Write-Host "3. Look for errors (red messages)" -ForegroundColor Yellow
Write-Host "4. Check Network tab for failed API calls" -ForegroundColor Yellow
Write-Host ""
Write-Host "Common Issues:" -ForegroundColor Cyan
Write-Host "  - 403 Forbidden: Permission/PBAC issue" -ForegroundColor Gray
Write-Host "  - 404 Not Found: API endpoint doesn't exist" -ForegroundColor Gray
Write-Host "  - 500 Server Error: Backend crash/bug" -ForegroundColor Gray
Write-Host "  - CORS Error: Frontend can't reach backend" -ForegroundColor Gray
Write-Host "======================================`n" -ForegroundColor Cyan
