#!/usr/bin/env pwsh
# Test all API endpoints with developer token

$ErrorActionPreference = "Stop"

Write-Host "Step 1: Login as developer" -ForegroundColor Yellow
$response = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/login" -Method Post `
    -Body '{"username":"developer","password":"password123"}' `
    -ContentType "application/json"

$Token = $response.access_token
Write-Host "✅ Logged in - Token: $($Token.Substring(0,30))..." -ForegroundColor Green

Write-Host "`nStep 2: Test all endpoints" -ForegroundColor Yellow

$endpoints = @(
    @{path="/quality/stats"; desc="Quality Stats"},
    @{path="/quality/inspections"; desc="Quality Inspections"},
    @{path="/reports/production-stats"; desc="Production Stats"},
    @{path="/reports/qc-stats"; desc="QC Stats"},
    @{path="/reports/inventory-summary"; desc="Inventory Summary"}
)

$failed = 0
foreach ($ep in $endpoints) {
    try {
        $result = Invoke-RestMethod -Uri "http://localhost:8000/api/v1$($ep.path)" `
            -Headers @{Authorization="Bearer $Token"} -TimeoutSec 5
        Write-Host "✅ $($ep.desc)" -ForegroundColor Green
    } catch {
        Write-Host "❌ $($ep.desc) - $($_.Exception.Message)" -ForegroundColor Red
        $failed++
    }
}

if ($failed -eq 0) {
    Write-Host "`n✅ All endpoints working!" -ForegroundColor Green
    exit 0
} else {
    Write-Host "`n❌ $failed endpoint(s) failed" -ForegroundColor Red
    exit 1
}
