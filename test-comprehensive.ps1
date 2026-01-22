# Full Comprehensive Test Script
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "COMPREHENSIVE ERP TEST" -ForegroundColor Yellow
Write-Host "========================================`n" -ForegroundColor Cyan

$frontendUrl = "http://localhost:3001"
$backendUrl = "http://localhost:8000/api/v1"
$username = "admin"
$password = "Admin@123456"

# Step 1: Test Backend APIs
Write-Host "[1/4] TESTING BACKEND APIs..." -ForegroundColor Yellow

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

try {
    $loginBody = @{
        username = $username
        password = $password
    } | ConvertTo-Json

    $loginResponse = Invoke-RestMethod -Uri "$backendUrl/auth/login" -Method POST -Body $loginBody -ContentType "application/json"
    $token = $loginResponse.access_token
    Write-Host "  Auth: OK" -ForegroundColor Green
} catch {
    Write-Host "  Auth: FAILED" -ForegroundColor Red
    exit 1
}

$headers = @{
    "Authorization" = "Bearer $token"
}

$apiOK = 0
foreach($endpoint in $apiEndpoints) {
    try {
        $response = Invoke-RestMethod -Uri "$backendUrl$endpoint" -Method GET -Headers $headers -TimeoutSec 5
        Write-Host "  OK - $endpoint" -ForegroundColor Green
        $apiOK++
    } catch {
        Write-Host "  FAIL - $endpoint" -ForegroundColor Red
    }
}

Write-Host "`nAPI Summary: $apiOK/$($apiEndpoints.Count) working`n" -ForegroundColor Cyan


# Step 2: Test Frontend Pages
Write-Host "[2/4] TESTING FRONTEND PAGES..." -ForegroundColor Yellow

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

$pagesOK = 0
$pagesWarning = 0

foreach($page in $pages) {
    try {
        $response = Invoke-WebRequest -Uri "$frontendUrl$page" -Method GET -TimeoutSec 5 -UseBasicParsing
        $content = $response.Content
        
        $hasReact = $content -match 'index-[a-zA-Z0-9_-]+\.js'
        $hasPlaceholder = $content -match 'under development|Under Development|placeholder'
        
        if(-not $hasReact) {
            Write-Host "  NO REACT - $page" -ForegroundColor Red
        } elseif($hasPlaceholder) {
            Write-Host "  PLACEHOLDER - $page" -ForegroundColor Yellow
            $pagesWarning++
        } else {
            Write-Host "  OK - $page" -ForegroundColor Green
            $pagesOK++
        }
    } catch {
        Write-Host "  ERROR - $page" -ForegroundColor Red
    }
}

Write-Host "`nPages Summary: $pagesOK OK, $pagesWarning Placeholder`n" -ForegroundColor Cyan


# Step 3: Check Navbar
Write-Host "[3/4] CHECKING NAVBAR STRUCTURE..." -ForegroundColor Yellow

try {
    $dashboardPage = Invoke-WebRequest -Uri "$frontendUrl/dashboard" -UseBasicParsing
    
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
    
    $menuOK = 0
    foreach($menu in $expectedMenus) {
        $found = $dashboardPage.Content -match $menu
        if($found) {
            Write-Host "  OK - $menu" -ForegroundColor Green
            $menuOK++
        } else {
            Write-Host "  MISSING - $menu" -ForegroundColor Red
        }
    }
    
    Write-Host "`nMenu Summary: $menuOK/$($expectedMenus.Count) found`n" -ForegroundColor Cyan
} catch {
    Write-Host "  ERROR checking navbar`n" -ForegroundColor Red
}


# Step 4: Check Build
Write-Host "[4/4] CHECKING BUILD VERSION..." -ForegroundColor Yellow

try {
    $rootPage = Invoke-WebRequest -Uri "$frontendUrl/" -UseBasicParsing
    if($rootPage.Content -match 'index-([a-zA-Z0-9_-]+)\.js') {
        $bundleHash = $matches[1]
        Write-Host "  Bundle hash: $bundleHash" -ForegroundColor Cyan
    }
} catch {
    Write-Host "  ERROR checking bundle`n" -ForegroundColor Red
}


# Final Summary
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "FINAL SUMMARY" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Backend APIs:   $apiOK/$($apiEndpoints.Count)" -ForegroundColor $(if($apiOK -eq $apiEndpoints.Count){"Green"}else{"Yellow"})
Write-Host "Frontend Pages: $pagesOK/$($pages.Count)" -ForegroundColor $(if($pagesOK -eq $pages.Count){"Green"}else{"Yellow"})
Write-Host "Placeholders:   $pagesWarning" -ForegroundColor $(if($pagesWarning -eq 0){"Green"}else{"Yellow"})

if($apiOK -eq $apiEndpoints.Count -and $pagesOK -eq $pages.Count) {
    Write-Host "`nALL TESTS PASSED!" -ForegroundColor Green
} else {
    Write-Host "`nSOME TESTS FAILED!" -ForegroundColor Yellow
}
Write-Host "========================================`n" -ForegroundColor Cyan
