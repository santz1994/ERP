#!/usr/bin/env pwsh
# Quick test - Ensure developer user exists and test endpoints

$BaseURL = "http://localhost:8000/api/v1"

Write-Host "Testing API Endpoints with Developer User" -ForegroundColor Cyan

# Create developer user if not exists
Write-Host "`nStep 1: Ensure developer user exists" -ForegroundColor Yellow
docker exec erp_backend python seed_all_users.py 2>&1 | Select-String "developer|already exists"

# Get token
Write-Host "`nStep 2: Login as developer" -ForegroundColor Yellow
$loginResponse = Invoke-RestMethod -Uri "$BaseURL/auth/login" -Method Post `
    -Body (@{username="developer"; password="password123"} | ConvertTo-Json) `
    -ContentType "application/json"

if ($loginResponse.status -eq "success") {
    $Token = $loginResponse.data.access_token
    Write-Host "✅ Logged in successfully" -ForegroundColor Green
    Write-Host "   Token: $($Token.Substring(0,20))..." -ForegroundColor Gray
} else {
    Write-Host "❌ Login failed" -ForegroundColor Red
    exit 1
}

# Test endpoints
Write-Host "`nStep 3: Test API Endpoints" -ForegroundColor Yellow

$endpoints = @(
    @{name="/quality/stats"; method="GET"},
    @{name="/quality/inspections"; method="GET"},
    @{name="/reports/production-stats"; method="GET"},
    @{name="/reports/qc-stats"; method="GET"},
    @{name="/reports/inventory-summary"; method="GET"}
)

foreach ($endpoint in $endpoints) {
    try {
        $response = Invoke-RestMethod -Uri "$BaseURL$($endpoint.name)" -Method $endpoint.method `
            -Headers @{Authorization="Bearer $Token"} -TimeoutSec 5
        Write-Host "✅ $($endpoint.name)" -ForegroundColor Green
    } catch {
        $statusCode = $_.Exception.Response.StatusCode.Value
        if ($statusCode -eq 403) {
            Write-Host "⚠️  $($endpoint.name) - 403 Permission Check (might need PBAC setup)" -ForegroundColor Yellow
        } else {
            Write-Host "❌ $($endpoint.name) - $statusCode" -ForegroundColor Red
        }
    }
}

Write-Host "`n✅ Test complete!" -ForegroundColor Green
