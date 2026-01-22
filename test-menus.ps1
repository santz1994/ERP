# Comprehensive Page and Menu Test
$baseUrl = 'http://localhost:8000/api/v1'
$frontendUrl = 'http://localhost:3001'

Write-Host '======================================'
Write-Host 'COMPREHENSIVE PAGE & MENU TEST'
Write-Host '======================================'

# Login
Write-Host '[STEP 1] Logging in...'
$loginResponse = Invoke-WebRequest -Uri "$baseUrl/auth/login" -Method POST -ContentType 'application/json' -Body '{\"username\":\"admin\",\"password\":\"Admin@123456\"}' -UseBasicParsing
$token = ($loginResponse.Content | ConvertFrom-Json).access_token
Write-Host '  [OK] Logged in successfully' -ForegroundColor Green

# Test API Endpoints
Write-Host '[STEP 2] Testing API Endpoints...'
$endpoints = @('/dashboard/stats', '/ppic/manufacturing-orders', '/production/cutting/pending', '/production/sewing/pending', '/purchasing/purchase-orders', '/admin/users')
$passed = 0
foreach ($ep in $endpoints) {
    try {
        $r = Invoke-WebRequest -Uri "$baseUrl$ep" -Headers @{'Authorization'="Bearer $token"} -UseBasicParsing -TimeoutSec 5
        if ($r.StatusCode -eq 200) {
            Write-Host "  [OK] $ep" -ForegroundColor Green
            $passed++
        }
    } catch {
        Write-Host "  [FAIL] $ep" -ForegroundColor Red
    }
}

# Test Frontend Routes
Write-Host '[STEP 3] Testing Frontend Routes...'
$routes = @('/dashboard', '/ppic', '/cutting', '/sewing', '/admin', '/settings/password', '/settings/language')
$routesPassed = 0
foreach ($route in $routes) {
    try {
        $r = Invoke-WebRequest -Uri "$frontendUrl$route" -UseBasicParsing -TimeoutSec 5
        if ($r.StatusCode -eq 200) {
            Write-Host "  [OK] $route" -ForegroundColor Green
            $routesPassed++
        }
    } catch {
        Write-Host "  [FAIL] $route" -ForegroundColor Red
    }
}

Write-Host ''
Write-Host 'SUMMARY:'
Write-Host "API Endpoints: $passed/$($endpoints.Count) passed"
Write-Host "Frontend Routes: $routesPassed/$($routes.Count) passed"
