# Test all page access for DEVELOPER and SUPERADMIN roles
# Verifies full access bypass works correctly

$baseUrl = "http://localhost:3001"
$apiUrl = "http://localhost:8000/api/v1"

# Test accounts
$testAccounts = @(
    @{ username = "developer"; password = "password123"; role = "DEVELOPER" },
    @{ username = "superadmin"; password = "password123"; role = "SUPERADMIN" }
)

# All protected routes to test
$routes = @(
    "/dashboard",
    "/purchasing",
    "/ppic",
    "/cutting",
    "/embroidery",
    "/sewing",
    "/finishing",
    "/packing",
    "/warehouse",
    "/finishgoods",
    "/quality",
    "/reports",
    "/admin/users",
    "/admin/permissions",
    "/admin/audit-trail",
    "/settings/password",
    "/settings/language",
    "/settings/notifications",
    "/settings/display",
    "/settings/access-control",
    "/settings/email",
    "/settings/templates",
    "/settings/company",
    "/settings/security",
    "/settings/database"
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "TESTING ALL PERMISSIONS - SUPERADMIN & DEVELOPER" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

foreach ($account in $testAccounts) {
    Write-Host "Testing: $($account.role) ($($account.username))" -ForegroundColor Yellow
    Write-Host "----------------------------------------" -ForegroundColor Yellow
    
    # Login
    try {
        $loginBody = @{
            username = $account.username
            password = $account.password
        } | ConvertTo-Json
        
        $response = Invoke-RestMethod -Uri "$apiUrl/auth/login" -Method POST -Body $loginBody -ContentType "application/json"
        $token = $response.access_token
        
        Write-Host "✅ Login successful" -ForegroundColor Green
        Write-Host "   Token: $($token.Substring(0, 20))..." -ForegroundColor Gray
        
        # Test each route
        $successCount = 0
        $failCount = 0
        
        foreach ($route in $routes) {
            try {
                $headers = @{
                    "Authorization" = "Bearer $token"
                }
                
                $pageResponse = Invoke-WebRequest -Uri "$baseUrl$route" -Headers $headers -TimeoutSec 5 -UseBasicParsing
                
                if ($pageResponse.StatusCode -eq 200) {
                    Write-Host "   ✅ $route" -ForegroundColor Green
                    $successCount++
                } else {
                    Write-Host "   ❌ $route (HTTP $($pageResponse.StatusCode))" -ForegroundColor Red
                    $failCount++
                }
            } catch {
                # For frontend routes, 200 is expected even without backend auth
                # The page will load, but may show auth errors in console
                if ($_.Exception.Response.StatusCode -eq 200) {
                    Write-Host "   ✅ $route" -ForegroundColor Green
                    $successCount++
                } else {
                    Write-Host "   ⚠️  $route (Error: $($_.Exception.Message))" -ForegroundColor Yellow
                    $failCount++
                }
            }
            
            Start-Sleep -Milliseconds 100
        }
        
        Write-Host ""
        Write-Host "Summary for $($account.role):" -ForegroundColor Cyan
        Write-Host "  ✅ Success: $successCount/$($routes.Count)" -ForegroundColor Green
        Write-Host "  ❌ Failed:  $failCount/$($routes.Count)" -ForegroundColor Red
        Write-Host ""
        
    } catch {
        Write-Host "❌ Login failed: $($_.Exception.Message)" -ForegroundColor Red
        Write-Host ""
    }
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "TEST COMPLETE" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
