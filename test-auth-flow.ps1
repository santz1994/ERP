# Automated Auth Flow Test Script
# Tests: Backend API, Token Storage, Frontend Auth

Write-Host "=== AUTOMATED AUTH FLOW TEST ===" -ForegroundColor Cyan
Write-Host "Test Date: $(Get-Date)" -ForegroundColor Gray

# Configuration
$API_URL = "http://localhost:8000/api/v1"
$FRONTEND_URL = "http://localhost:5173"
$TEST_USER = "developer"
$TEST_PASSWORD = "Developer@123456"

# Test 1: Check backend is running
Write-Host "`n[TEST 1] Checking Backend API..." -ForegroundColor Yellow
try {
    $healthCheck = Invoke-WebRequest -Uri "$API_URL/health" -Method GET -ErrorAction Stop
    Write-Host "✅ Backend API is running" -ForegroundColor Green
} catch {
    Write-Host "❌ Backend API not running at $API_URL" -ForegroundColor Red
    Write-Host "Error: $($_)" -ForegroundColor Red
    exit 1
}

# Test 2: Check frontend is running
Write-Host "`n[TEST 2] Checking Frontend..." -ForegroundColor Yellow
try {
    $frontendCheck = Invoke-WebRequest -Uri $FRONTEND_URL -Method GET -ErrorAction Stop
    Write-Host "✅ Frontend is running at $FRONTEND_URL" -ForegroundColor Green
} catch {
    Write-Host "❌ Frontend not running at $FRONTEND_URL" -ForegroundColor Red
}

# Test 3: Test Login Endpoint
Write-Host "`n[TEST 3] Testing Login Endpoint..." -ForegroundColor Yellow
$loginPayload = @{
    username = $TEST_USER
    password = $TEST_PASSWORD
} | ConvertTo-Json

Write-Host "Payload: $loginPayload" -ForegroundColor Gray

try {
    $loginResponse = Invoke-WebRequest -Uri "$API_URL/auth/login" -Method POST `
        -Headers @{"Content-Type"="application/json"} `
        -Body $loginPayload `
        -ErrorAction Stop

    $loginData = $loginResponse.Content | ConvertFrom-Json
    
    if ($loginData.access_token) {
        Write-Host "✅ Login successful!" -ForegroundColor Green
        Write-Host "   Token: $($loginData.access_token.Substring(0,20))..." -ForegroundColor Gray
        Write-Host "   User: $($loginData.user.username) (Role: $($loginData.user.role))" -ForegroundColor Gray
        $ACCESS_TOKEN = $loginData.access_token
    } else {
        Write-Host "❌ Login response missing token" -ForegroundColor Red
        Write-Host $loginResponse.Content -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "❌ Login endpoint failed" -ForegroundColor Red
    Write-Host "Error: $($_)" -ForegroundColor Red
    exit 1
}

# Test 4: Test /auth/me endpoint with token
Write-Host "`n[TEST 4] Testing /auth/me with Token..." -ForegroundColor Yellow
try {
    $meResponse = Invoke-WebRequest -Uri "$API_URL/auth/me" -Method GET `
        -Headers @{"Authorization"="Bearer $ACCESS_TOKEN"} `
        -ErrorAction Stop

    $meData = $meResponse.Content | ConvertFrom-Json
    Write-Host "✅ /auth/me successful!" -ForegroundColor Green
    Write-Host "   User: $($meData.username)" -ForegroundColor Gray
    Write-Host "   Role: $($meData.role)" -ForegroundColor Gray
} catch {
    Write-Host "❌ /auth/me failed with token" -ForegroundColor Red
    Write-Host "Error: $($_)" -ForegroundColor Red
    Write-Host "Status: $($_.Exception.Response.StatusCode)" -ForegroundColor Red
}

# Test 5: Test /auth/me without token (should fail with 401)
Write-Host "`n[TEST 5] Testing /auth/me without Token (should fail)..." -ForegroundColor Yellow
try {
    $meNoTokenResponse = Invoke-WebRequest -Uri "$API_URL/auth/me" -Method GET -ErrorAction Stop
    Write-Host "❌ /auth/me should require token but didn't" -ForegroundColor Red
} catch {
    if ($_.Exception.Response.StatusCode -eq 401) {
        Write-Host "✅ Correctly returned 401 for missing token" -ForegroundColor Green
    } else {
        Write-Host "❌ Expected 401, got: $($_.Exception.Response.StatusCode)" -ForegroundColor Red
    }
}

# Test 6: Test Dashboard page
Write-Host "`n[TEST 6] Testing Dashboard Page Access..." -ForegroundColor Yellow
try {
    $dashResponse = Invoke-WebRequest -Uri "$FRONTEND_URL/dashboard" -Method GET -ErrorAction Stop
    Write-Host "✅ Dashboard page loads" -ForegroundColor Green
} catch {
    Write-Host "⚠️ Could not fetch dashboard (expected if behind router)" -ForegroundColor Yellow
}

# Test 7: Create test HTML to verify localStorage
Write-Host "`n[TEST 7] Creating Browser Test File..." -ForegroundColor Yellow
$testHtml = @"
<!DOCTYPE html>
<html>
<head>
    <title>Auth Storage Test</title>
    <style>
        body { font-family: monospace; margin: 20px; }
        .pass { color: green; }
        .fail { color: red; }
        .warn { color: orange; }
        pre { background: #f5f5f5; padding: 10px; overflow-x: auto; }
    </style>
</head>
<body>
    <h1>ERP Auth Flow Test</h1>
    <div id="results"></div>
    
    <script>
        const results = [];
        
        // Test 1: Check localStorage
        const token = localStorage.getItem('access_token');
        const userStr = localStorage.getItem('user');
        
        if (token) {
            results.push('<div class="pass">✅ access_token found in localStorage</div>');
            results.push('<pre>Token: ' + token.substring(0,50) + '...</pre>');
        } else {
            results.push('<div class="fail">❌ NO access_token in localStorage</div>');
        }
        
        if (userStr) {
            try {
                const user = JSON.parse(userStr);
                results.push('<div class="pass">✅ user found in localStorage</div>');
                results.push('<pre>' + JSON.stringify(user, null, 2) + '</pre>');
            } catch (e) {
                results.push('<div class="fail">❌ user data is invalid JSON: ' + e.message + '</div>');
            }
        } else {
            results.push('<div class="fail">❌ NO user in localStorage</div>');
        }
        
        // Test 2: Check Zustand auth store
        if (window.__ZUSTAND_STORE__) {
            results.push('<div class="pass">✅ Zustand store found</div>');
            results.push('<pre>' + JSON.stringify(window.__ZUSTAND_STORE__, null, 2) + '</pre>');
        } else {
            results.push('<div class="warn">⚠️ Zustand store not exposed (normal)</div>');
        }
        
        // Test 3: Check API connectivity
        results.push('<div><b>Testing API connectivity...</b></div>');
        fetch('http://localhost:8000/api/v1/auth/me', {
            headers: { 'Authorization': 'Bearer ' + token }
        })
        .then(r => {
            if (r.ok) results.push('<div class="pass">✅ API /auth/me - OK</div>');
            else results.push('<div class="fail">❌ API /auth/me - ' + r.status + ' ' + r.statusText + '</div>');
        })
        .catch(e => results.push('<div class="fail">❌ API /auth/me - Error: ' + e.message + '</div>'))
        .finally(() => {
            document.getElementById('results').innerHTML = results.join('');
        });
    </script>
</body>
</html>
"@

$testHtmlPath = "d:\Project\ERP2026\test-auth.html"
Set-Content -Path $testHtmlPath -Value $testHtml
Write-Host "✅ Test file created at: file:///$testHtmlPath" -ForegroundColor Green
Write-Host "   Open in browser to check localStorage and API" -ForegroundColor Gray

# Summary
Write-Host "`n=== TEST SUMMARY ===" -ForegroundColor Cyan
Write-Host "Backend API: RUNNING ✅" -ForegroundColor Green
Write-Host "Login: WORKING ✅" -ForegroundColor Green
Write-Host "Token: $($ACCESS_TOKEN.Substring(0,30))..." -ForegroundColor Green
Write-Host "`nNext Steps:" -ForegroundColor Yellow
Write-Host "1. Login to frontend at $FRONTEND_URL" -ForegroundColor White
Write-Host "2. Open browser DevTools (F12)" -ForegroundColor White
Write-Host "3. Check Console for [AuthStore] and [PrivateRoute] logs" -ForegroundColor White
Write-Host "4. Check Application > LocalStorage for tokens" -ForegroundColor White
Write-Host "5. Refresh page (F5) and check if you stay logged in" -ForegroundColor White
Write-Host "6. Open $testHtmlPath in browser to verify storage" -ForegroundColor White
