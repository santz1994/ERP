# Full Comprehensive Test Script
# Tests: Pages, APIs, Navbar Structure, Session Persistence

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "  COMPREHENSIVE ERP FRONTEND & BACKEND TEST" -ForegroundColor Cyan
Write-Host "============================================================`n" -ForegroundColor Cyan

# Test configuration
$frontendUrl = "http://localhost:3001"
$backendUrl = "http://localhost:8000/api/v1"
$username = "admin"
$password = "Admin@123456"

# Step 1: Test Backend APIs
Write-Host "`n[1/5] TESTING BACKEND APIs..." -ForegroundColor Yellow
Write-Host "─────────────────────────────────────────────────────────────" -ForegroundColor Gray

$apiEndpoints = @(
    "/dashboard/metrics",
    "/ppic/schedules",
    "/production/cutting/pending",
    "/production/sewing/pending",
    "/production/finishing/pending",
    "/production/packing/pending",
    "/purchasing/purchase-orders",
    "/warehouse/materials",
    "/warehouse/stock",
    "/finishgoods/shipments",
    "/qc/inspections",
    "/kanban/boards",
    "/admin/users",
    "/admin/roles"
)

# Get auth token first
try {
    $loginBody = @{
        username = $username
        password = $password
    } | ConvertTo-Json

    $loginResponse = Invoke-RestMethod -Uri "$backendUrl/auth/login" -Method POST -Body $loginBody -ContentType "application/json"
    $token = $loginResponse.access_token
    Write-Host "✅ Authentication successful" -ForegroundColor Green
} catch {
    Write-Host "❌ Authentication failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

$headers = @{
    "Authorization" = "Bearer $token"
}

$apiResults = @()
foreach($endpoint in $apiEndpoints) {
    try {
        $response = Invoke-RestMethod -Uri "$backendUrl$endpoint" -Method GET -Headers $headers -TimeoutSec 5
        $status = "✅ 200 OK"
        $statusColor = "Green"
    } catch {
        $statusCode = $_.Exception.Response.StatusCode.value__
        if($statusCode) {
            $status = "❌ $statusCode"
        } else {
            $status = "❌ ERROR"
        }
        $statusColor = "Red"
    }
    
    $apiResults += [PSCustomObject]@{
        Endpoint = $endpoint
        Status = $status
    }
    
    Write-Host "  $status - $endpoint" -ForegroundColor $statusColor
}

$apiOK = ($apiResults | Where-Object {$_.Status -match "✅"} | Measure-Object).Count
$apiTotal = $apiEndpoints.Count
Write-Host "`n  API Summary: $apiOK/$apiTotal working" -ForegroundColor Cyan


# Step 2: Test Frontend Pages
Write-Host "`n[2/5] TESTING FRONTEND PAGES..." -ForegroundColor Yellow
Write-Host "─────────────────────────────────────────────────────────────" -ForegroundColor Gray

$pages = @(
    "/login",
    "/dashboard",
    "/ppic",
    "/cutting",
    "/sewing",
    "/finishing",
    "/packing",
    "/purchasing",
    "/warehouse/materials",
    "/warehouse/stock",
    "/finishgoods/shipments",
    "/qc/inspections",
    "/kanban",
    "/admin/users",
    "/admin/roles",
    "/admin/permissions",
    "/settings/password",
    "/settings/profile"
)

$pageResults = @()
foreach($page in $pages) {
    try {
        $response = Invoke-WebRequest -Uri "$frontendUrl$page" -Method GET -TimeoutSec 5 -UseBasicParsing
        $content = $response.Content
        
        # Check for React bundle
        $hasReact = $content -match 'index-[a-zA-Z0-9_-]+\.js'
        
        # Check for placeholder text
        $hasPlaceholder = $content -match 'under development|Under Development|placeholder|Placeholder'
        
        # Determine status
        if(-not $hasReact) {
            $status = "❌ NO REACT"
            $color = "Red"
        } elseif($hasPlaceholder) {
            $status = "⚠️  PLACEHOLDER"
            $color = "Yellow"
        } else {
            $status = "✅ OK"
            $color = "Green"
        }
        
        $pageResults += [PSCustomObject]@{
            Page = $page
            Status = $status
        }
        
        Write-Host "  $status - $page" -ForegroundColor $color
    } catch {
        $pageResults += [PSCustomObject]@{
            Page = $page
            Status = "❌ ERROR"
        }
        Write-Host "  ❌ ERROR - $page" -ForegroundColor Red
    }
}

$pagesOK = ($pageResults | Where-Object {$_.Status -match "✅"} | Measure-Object).Count
$pagesWarning = ($pageResults | Where-Object {$_.Status -match "⚠️"} | Measure-Object).Count
$pagesTotal = $pages.Count
Write-Host "`n  Pages Summary: $pagesOK OK, $pagesWarning Placeholder, $(($pagesTotal - $pagesOK - $pagesWarning)) Error" -ForegroundColor Cyan


# Step 3: Check Navbar Structure
Write-Host "`n[3/5] CHECKING NAVBAR STRUCTURE..." -ForegroundColor Yellow
Write-Host "─────────────────────────────────────────────────────────────" -ForegroundColor Gray

try {
    $dashboardPage = Invoke-WebRequest -Uri "$frontendUrl/dashboard" -UseBasicParsing
    
    # Check for menu items in the HTML
    $expectedMenus = @(
        "Dashboard",
        "PPIC",
        "Production",
        "Purchasing", 
        "Warehouse",
        "Finish Goods",
        "QC",
        "Kanban",
        "Admin",
        "Settings"
    )
    
    Write-Host "`n  Expected menu items:" -ForegroundColor Cyan
    foreach($menu in $expectedMenus) {
        $found = $dashboardPage.Content -match $menu
        if($found) {
            Write-Host "    ✅ $menu" -ForegroundColor Green
        } else {
            Write-Host "    ❌ $menu (not found)" -ForegroundColor Red
        }
    }
} catch {
    Write-Host "  ❌ Could not check navbar: $($_.Exception.Message)" -ForegroundColor Red
}


# Step 4: Check Session Persistence
Write-Host "`n[4/5] CHECKING SESSION PERSISTENCE..." -ForegroundColor Yellow
Write-Host "─────────────────────────────────────────────────────────────" -ForegroundColor Gray

Write-Host "  NOTE: Session persistence requires browser testing" -ForegroundColor Yellow
Write-Host "  Manual test required:" -ForegroundColor Cyan
Write-Host "    1. Login with admin/Admin@123456" -ForegroundColor Gray
Write-Host "    2. Refresh page (F5)" -ForegroundColor Gray
Write-Host "    3. Check if still logged in" -ForegroundColor Gray
Write-Host "    ✅ If stays logged in -> Session OK" -ForegroundColor Green
Write-Host "    ❌ If redirected to login -> Session issue" -ForegroundColor Red


# Step 5: Check Bundle Hash
Write-Host "`n[5/5] CHECKING BUILD VERSION..." -ForegroundColor Yellow
Write-Host "─────────────────────────────────────────────────────────────" -ForegroundColor Gray

try {
    $rootPage = Invoke-WebRequest -Uri "$frontendUrl/" -UseBasicParsing
    if($rootPage.Content -match 'index-([a-zA-Z0-9_-]+)\.js') {
        $bundleHash = $matches[1]
        Write-Host "  ✅ Bundle hash: $bundleHash" -ForegroundColor Green
        Write-Host "  Build time: $(Get-Date)" -ForegroundColor Cyan
    } else {
        Write-Host "  ❌ Could not find bundle hash" -ForegroundColor Red
    }
} catch {
    Write-Host "  ❌ Could not check bundle: $($_.Exception.Message)" -ForegroundColor Red
}


# Final Summary
Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "  FINAL SUMMARY" -ForegroundColor Cyan
Write-Host "============================================================`n" -ForegroundColor Cyan

Write-Host "  Backend APIs:   $apiOK/$apiTotal working" -ForegroundColor $(if($apiOK -eq $apiTotal){"Green"}else{"Yellow"})
Write-Host "  Frontend Pages: $pagesOK/$pagesTotal fully working" -ForegroundColor $(if($pagesOK -eq $pagesTotal){"Green"}else{"Yellow"})
Write-Host "  Placeholders:   $pagesWarning pages" -ForegroundColor $(if($pagesWarning -eq 0){"Green"}else{"Yellow"})

if($apiOK -eq $apiTotal -and $pagesOK -eq $pagesTotal) {
    Write-Host "`n  ALL TESTS PASSED!" -ForegroundColor Green
} else {
    Write-Host "`n  SOME TESTS FAILED - CHECK DETAILS ABOVE" -ForegroundColor Yellow
}

Write-Host "`n============================================================`n" -ForegroundColor Cyan
