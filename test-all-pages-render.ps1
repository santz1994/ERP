# Comprehensive Page Rendering Test
$frontendUrl = "http://localhost:3001"
$baseUrl = "http://localhost:8000/api/v1"

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "CHECKING ALL PAGE RENDERING ISSUES" -ForegroundColor Cyan
Write-Host "======================================`n" -ForegroundColor Cyan

# Login first
Write-Host "[STEP 1] Logging in..." -ForegroundColor Yellow
try {
    $loginResponse = Invoke-WebRequest -Uri "$baseUrl/auth/login" -Method POST -Body (@{username="admin"; password="Admin@123456"} | ConvertTo-Json) -ContentType "application/json" -UseBasicParsing
    $loginData = $loginResponse.Content | ConvertFrom-Json
    $token = $loginData.access_token
    Write-Host "[OK] Logged in successfully`n" -ForegroundColor Green
} catch {
    Write-Host "[FAIL] Cannot login: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Check backend logs for errors
Write-Host "[STEP 2] Checking Backend Logs..." -ForegroundColor Yellow
$logs = docker logs erp_backend --tail 50 2>&1
$errors = $logs | Select-String -Pattern "ERROR|Exception|Traceback|500|404" -Context 0,2
if ($errors) {
    Write-Host "[FOUND] Backend Errors:" -ForegroundColor Red
    $errors | Select-Object -First 10 | ForEach-Object { 
        Write-Host "  $($_.Line)" -ForegroundColor Gray 
    }
} else {
    Write-Host "[OK] No errors in backend logs" -ForegroundColor Green
}
Write-Host ""

# Test all API endpoints that pages depend on
Write-Host "[STEP 3] Testing All Page API Endpoints..." -ForegroundColor Yellow
$endpoints = @(
    @{path="/dashboard/stats"; name="Dashboard"; method="GET"}
    @{path="/ppic/manufacturing-orders"; name="PPIC"; method="GET"}
    @{path="/production/cutting/pending"; name="Cutting"; method="GET"}
    @{path="/production/sewing/pending"; name="Sewing"; method="GET"}
    @{path="/embroidery/work-orders"; name="Embroidery"; method="GET"}
    @{path="/production/finishing/pending"; name="Finishing"; method="GET"}
    @{path="/production/packing/pending"; name="Packing"; method="GET"}
    @{path="/warehouse/materials"; name="Warehouse Materials"; method="GET"}
    @{path="/warehouse/stock/1"; name="Warehouse Stock"; method="GET"}
    @{path="/purchasing/purchase-orders"; name="Purchasing"; method="GET"}
    @{path="/finishgoods/shipments"; name="Finish Goods"; method="GET"}
    @{path="/qc/inspections"; name="QC"; method="GET"}
    @{path="/kanban/cards"; name="Kanban"; method="GET"}
    @{path="/admin/users"; name="Admin Users"; method="GET"}
)

$failedEndpoints = @()
foreach ($endpoint in $endpoints) {
    try {
        $response = Invoke-WebRequest -Uri "$baseUrl$($endpoint.path)" -Method $endpoint.method -Headers @{"Authorization"="Bearer $token"} -UseBasicParsing -TimeoutSec 5
        if ($response.StatusCode -eq 200) {
            Write-Host "  [OK] $($endpoint.name) - $($endpoint.path)" -ForegroundColor Green
        } else {
            Write-Host "  [WARN] $($endpoint.name) - Status: $($response.StatusCode)" -ForegroundColor Yellow
        }
    } catch {
        $statusCode = $_.Exception.Response.StatusCode.value__
        Write-Host "  [FAIL] $($endpoint.name) - Status: $statusCode - $($endpoint.path)" -ForegroundColor Red
        $failedEndpoints += @{
            name = $endpoint.name
            path = $endpoint.path
            status = $statusCode
        }
    }
}

Write-Host ""

# Check frontend routes
Write-Host "[STEP 4] Testing Frontend Route Rendering..." -ForegroundColor Yellow
$routes = @("/dashboard", "/ppic", "/cutting", "/sewing", "/warehouse", "/admin")
foreach ($route in $routes) {
    try {
        $response = Invoke-WebRequest -Uri "$frontendUrl$route" -UseBasicParsing -TimeoutSec 3
        $hasRoot = $response.Content -match '<div id="root">'
        $hasBundle = $response.Content -match 'src="/assets/index-.+?\.js"'
        
        if ($hasRoot -and $hasBundle) {
            Write-Host "  [OK] $route - HTML structure valid" -ForegroundColor Green
        } else {
            Write-Host "  [WARN] $route - Missing structure" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "  [FAIL] $route - Cannot load" -ForegroundColor Red
    }
}

Write-Host ""

# Show detailed error info
if ($failedEndpoints.Count -gt 0) {
    Write-Host "[STEP 5] Failed Endpoints Analysis..." -ForegroundColor Yellow
    Write-Host ""
    foreach ($failed in $failedEndpoints) {
        Write-Host "  [$($failed.name)]" -ForegroundColor Red
        Write-Host "    Path: $($failed.path)" -ForegroundColor Gray
        Write-Host "    Status: $($failed.status)" -ForegroundColor Gray
        
        if ($failed.status -eq 404) {
            Write-Host "    Issue: API endpoint doesn't exist in backend" -ForegroundColor Yellow
            Write-Host "    Fix: Need to implement backend router" -ForegroundColor Yellow
        } elseif ($failed.status -eq 500) {
            Write-Host "    Issue: Backend crash/database error" -ForegroundColor Yellow
            Write-Host "    Fix: Check backend logs above for details" -ForegroundColor Yellow
        } elseif ($failed.status -eq 403) {
            Write-Host "    Issue: Permission denied (PBAC)" -ForegroundColor Yellow
            Write-Host "    Fix: Grant admin role the required permission" -ForegroundColor Yellow
        }
        Write-Host ""
    }
}

# Summary
Write-Host "======================================" -ForegroundColor Cyan
Write-Host "SUMMARY" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host "Tested Endpoints: $($endpoints.Count)" -ForegroundColor White
Write-Host "Failed Endpoints: $($failedEndpoints.Count)" -ForegroundColor $(if ($failedEndpoints.Count -gt 0) { "Red" } else { "Green" })
Write-Host ""

if ($failedEndpoints.Count -eq 0) {
    Write-Host "[SUCCESS] All endpoints working!" -ForegroundColor Green
} else {
    Write-Host "[ACTION REQUIRED] Fix the failed endpoints above" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Pages will show 'Page under development' or errors because:" -ForegroundColor Yellow
    Write-Host "  1. Frontend tries to fetch data from API" -ForegroundColor Gray
    Write-Host "  2. API returns 404/500 error" -ForegroundColor Gray
    Write-Host "  3. Frontend shows error message or placeholder" -ForegroundColor Gray
}

Write-Host ""
Write-Host "To see actual errors in browser:" -ForegroundColor Cyan
Write-Host "  1. Open http://localhost:3001/dashboard" -ForegroundColor Gray
Write-Host "  2. Press F12 (DevTools)" -ForegroundColor Gray
Write-Host "  3. Go to Console tab" -ForegroundColor Gray
Write-Host "  4. Look for red error messages" -ForegroundColor Gray
Write-Host "======================================`n" -ForegroundColor Cyan
