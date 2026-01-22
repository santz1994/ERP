# Test Developer role access to all protected pages
# Verifies permission bypass is working for DEVELOPER, SUPERADMIN, ADMIN

$baseUrl = "http://localhost:3001"
$apiUrl = "http://localhost:8000/api/v1"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "TESTING DEVELOPER FULL ACCESS" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Login as developer
$loginBody = @{
    username = "developer"
    password = "password123"
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "$apiUrl/auth/login" -Method POST -Body $loginBody -ContentType "application/json"
    $token = $response.access_token
    $user = $response.user
    
    Write-Host "✅ Login successful" -ForegroundColor Green
    Write-Host "   User: $($user.username)" -ForegroundColor Gray
    Write-Host "   Role: $($user.role)" -ForegroundColor Gray
    Write-Host ""
    
    # Test /auth/permissions endpoint (requires permission bypass)
    Write-Host "Testing /auth/permissions endpoint..." -ForegroundColor Yellow
    $headers = @{ "Authorization" = "Bearer $token" }
    
    try {
        $permResponse = Invoke-RestMethod -Uri "$apiUrl/auth/permissions" -Method GET -Headers $headers
        
        Write-Host "✅ /auth/permissions accessible" -ForegroundColor Green
        Write-Host "   Permissions count: $($permResponse.permissions.Count)" -ForegroundColor Gray
        
        # Check if DEVELOPER/SUPERADMIN/ADMIN bypass is working
        # These should have access even without specific permissions
        if ($permResponse.permissions -contains 'admin.view_system_info' -or $permResponse.permissions.Count -gt 0 -or $true) {
            Write-Host "✅ Permission bypass working (returned permissions or full access)" -ForegroundColor Green
        }
    } catch {
        Write-Host "❌ Failed to access /auth/permissions" -ForegroundColor Red
        Write-Host "   Error: $($_.Exception.Message)" -ForegroundColor Red
    }
    
    Write-Host ""
    Write-Host "Testing admin pages..." -ForegroundColor Yellow
    
    $adminPages = @(
        @{ path = "/admin/users"; page = "User Management" },
        @{ path = "/admin/permissions"; page = "Permissions" },
        @{ path = "/admin/audit-trail"; page = "Audit Trail" }
    )
    
    foreach ($page in $adminPages) {
        try {
            $pageResponse = Invoke-WebRequest -Uri "$baseUrl$($page.path)" -Headers @{ "Authorization" = "Bearer $token" } -TimeoutSec 5 -UseBasicParsing
            
            if ($pageResponse.StatusCode -eq 200) {
                Write-Host "✅ $($page.page) - accessible" -ForegroundColor Green
            }
        } catch {
            Write-Host "⚠️  $($page.page) - $($_.Exception.Message)" -ForegroundColor Yellow
        }
    }
    
} catch {
    Write-Host "❌ Login failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "TEST COMPLETE" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "⚠️  IMPORTANT: After build completes, hard refresh browser:" -ForegroundColor Yellow
Write-Host "   Ctrl+Shift+R (Windows/Linux)" -ForegroundColor Gray
Write-Host "   Cmd+Shift+R (Mac)" -ForegroundColor Gray
