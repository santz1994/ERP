#!/usr/bin/env powershell
<#
.SYNOPSIS
    Verify all ERP2026 Docker services and ports are accessible
.DESCRIPTION
    Tests connectivity to all services and reports status
#>

$ErrorActionPreference = "SilentlyContinue"
$ProgressPreference = "SilentlyContinue"

# Service configuration
$Services = @(
    @{ Name = "Frontend"; Port = 3000; Protocol = "HTTP"; URL = "http://localhost:3000" }
    @{ Name = "Backend API"; Port = 8000; Protocol = "HTTP"; URL = "http://localhost:8000/health" }
    @{ Name = "API Docs"; Port = 8000; Protocol = "HTTP"; URL = "http://localhost:8000/docs" }
    @{ Name = "PostgreSQL"; Port = 5432; Protocol = "TCP"; URL = "localhost:5432" }
    @{ Name = "Redis"; Port = 6379; Protocol = "TCP"; URL = "localhost:6379" }
    @{ Name = "Prometheus"; Port = 9090; Protocol = "HTTP"; URL = "http://localhost:9090" }
    @{ Name = "Grafana"; Port = 3001; Protocol = "HTTP"; URL = "http://localhost:3001" }
    @{ Name = "AlertManager"; Port = 9093; Protocol = "HTTP"; URL = "http://localhost:9093" }
    @{ Name = "pgAdmin"; Port = 5051; Protocol = "HTTP"; URL = "http://localhost:5051" }
)

function Test-Port {
    param(
        [string]$Server,
        [int]$Port,
        [int]$Timeout = 1000
    )
    
    $TCPClient = New-Object System.Net.Sockets.TcpClient
    $AsyncResult = $TCPClient.BeginConnect($Server, $Port, $null, $null)
    $WaitHandle = $AsyncResult.AsyncWaitHandle
    
    try {
        if (-not $WaitHandle.WaitOne($Timeout, $false)) {
            $TCPClient.Close()
            return $false
        }
        
        $TCPClient.EndConnect($AsyncResult)
        $TCPClient.Close()
        return $true
    }
    catch {
        return $false
    }
}

function Test-HTTP {
    param(
        [string]$URL,
        [int]$Timeout = 5000
    )
    
    try {
        $Response = Invoke-WebRequest -Uri $URL -TimeoutSec ($Timeout / 1000) -ErrorAction Stop
        return $Response.StatusCode -eq 200
    }
    catch {
        return $false
    }
}

Write-Host ""
Write-Host "╔═══════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║    ERP2026 - Service Port Verification                   ║" -ForegroundColor Cyan
Write-Host "╚═══════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

$HealthyServices = 0
$UnhealthyServices = 0

foreach ($Service in $Services) {
    Write-Host "Checking $($Service.Name)... " -NoNewline
    
    try {
        if ($Service.Protocol -eq "HTTP") {
            if (Test-HTTP $Service.URL) {
                Write-Host "✅ ONLINE (Port $($Service.Port))" -ForegroundColor Green
                $HealthyServices++
            } else {
                Write-Host "❌ OFFLINE (Port $($Service.Port))" -ForegroundColor Red
                $UnhealthyServices++
            }
        } else {
            $HostPort = $Service.URL.Split(":")[0]
            $PortNum = $Service.URL.Split(":")[1]
            
            if (Test-Port $HostPort $PortNum) {
                Write-Host "✅ ONLINE (Port $($Service.Port))" -ForegroundColor Green
                $HealthyServices++
            } else {
                Write-Host "❌ OFFLINE (Port $($Service.Port))" -ForegroundColor Red
                $UnhealthyServices++
            }
        }
    }
    catch {
        Write-Host "❌ ERROR (Port $($Service.Port))" -ForegroundColor Red
        $UnhealthyServices++
    }
}

Write-Host ""
Write-Host "╔═══════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║    Summary                                                ║" -ForegroundColor Cyan
Write-Host "╚═══════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Healthy Services:   $HealthyServices/$($Services.Count)" -ForegroundColor Green
Write-Host "  Unhealthy Services: $UnhealthyServices/$($Services.Count)" -ForegroundColor $(if ($UnhealthyServices -gt 0) { "Red" } else { "Green" })
Write-Host ""

if ($UnhealthyServices -eq 0) {
    Write-Host "✅ ALL SERVICES ARE RUNNING AND HEALTHY!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Quick Links:" -ForegroundColor Cyan
    Write-Host "  Frontend:   http://localhost:3000" -ForegroundColor White
    Write-Host "  API Docs:   http://localhost:8000/docs" -ForegroundColor White
    Write-Host "  Grafana:    http://localhost:3001 (admin/admin)" -ForegroundColor White
    Write-Host "  pgAdmin:    http://localhost:5051 (admin@example.com/admin)" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host "⚠️  SOME SERVICES ARE NOT RESPONDING" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Troubleshooting:" -ForegroundColor Cyan
    Write-Host "  1. Check Docker is running: docker ps" -ForegroundColor White
    Write-Host "  2. Check service logs: docker-compose logs [service]" -ForegroundColor White
    Write-Host "  3. Verify ports are available" -ForegroundColor White
    Write-Host ""
}
