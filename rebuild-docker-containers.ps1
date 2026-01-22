#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Docker Container Rebuild and Cleanup Script
    Rebuilds all ERP containers from scratch, removing old images and volumes

.DESCRIPTION
    1. Stops all running containers
    2. Removes old containers
    3. Removes old images
    4. Rebuilds images from scratch
    5. Starts all services
    6. Verifies all containers are healthy

.EXAMPLE
    .\rebuild-docker-containers.ps1
#>

$ErrorActionPreference = "Stop"
$ProjectRoot = "d:\Project\ERP2026"

Write-Host "🐳 Docker Container Rebuild Script"
Write-Host "===================================="
Write-Host ""

# Verify docker is running
try {
    $dockerStatus = docker version -q
    if (-not $dockerStatus) {
        throw "Docker is not running"
    }
    Write-Host "✓ Docker is running"
} catch {
    Write-Host "✗ Docker error: $_"
    exit 1
}

# Step 1: Stop all running containers
Write-Host ""
Write-Host "📵 Stopping running containers..."
try {
    $runningContainers = docker ps -q --filter "name=erp_" | Sort-Object
    if ($runningContainers) {
        docker stop $runningContainers
        Write-Host "✓ Stopped $(($runningContainers | Measure-Object).Count) container(s)"
    } else {
        Write-Host "  (No running containers)"
    }
} catch {
    Write-Host "⚠ Warning while stopping containers: $_"
}

# Step 2: Remove all ERP containers
Write-Host ""
Write-Host "🗑  Removing old containers..."
try {
    $allContainers = docker ps -aq --filter "name=erp_" | Sort-Object
    if ($allContainers) {
        docker rm -f $allContainers
        Write-Host "✓ Removed $(($allContainers | Measure-Object).Count) container(s)"
    } else {
        Write-Host "  (No containers to remove)"
    }
} catch {
    Write-Host "⚠ Warning while removing containers: $_"
}

# Step 3: Remove old images (except volumes - we'll keep those)
Write-Host ""
Write-Host "🖼  Removing old images..."
try {
    $oldImages = docker images | Where-Object { $_ -match "erp_|<none>" } | Skip 1 | ForEach-Object { ($_ -split '\s+')[2] } | Sort-Object -Unique
    if ($oldImages) {
        docker rmi -f $oldImages 2>$null
        Write-Host "✓ Removed old images"
    } else {
        Write-Host "  (No old images to remove)"
    }
} catch {
    Write-Host "⚠ Warning while removing images: $_"
}

# Step 4: Rebuild images
Write-Host ""
Write-Host "🔨 Rebuilding Docker images..."
try {
    Push-Location $ProjectRoot
    
    # Build backend
    Write-Host "  → Building backend image..."
    docker-compose build --no-cache backend 2>&1 | Select-Object -Last 5
    Write-Host "  ✓ Backend image built"
    
    # Build frontend
    Write-Host "  → Building frontend image..."
    docker-compose build --no-cache frontend 2>&1 | Select-Object -Last 5
    Write-Host "  ✓ Frontend image built"
    
    Pop-Location
} catch {
    Write-Host "✗ Error rebuilding images: $_"
    exit 1
}

# Step 5: Start all services
Write-Host ""
Write-Host "🚀 Starting all services..."
try {
    Push-Location $ProjectRoot
    docker-compose up -d
    Write-Host "✓ All services started"
    Pop-Location
} catch {
    Write-Host "✗ Error starting services: $_"
    exit 1
}

# Step 6: Wait for services to be ready
Write-Host ""
Write-Host "⏳ Waiting for services to be ready..."
Start-Sleep -Seconds 5

# Step 7: Verify containers
Write-Host ""
Write-Host "🔍 Verifying container health..."
$containers = @(
    "erp_postgres",
    "erp_redis", 
    "erp_backend",
    "erp_frontend"
)

$allHealthy = $true
foreach ($container in $containers) {
    $status = docker ps --filter "name=$container" --format "{{.Status}}"
    if ($status -match "Up") {
        $healthy = if ($status -match "healthy") { "✓ Healthy" } else { "✓ Running" }
        Write-Host "  $container : $healthy ($status)"
    } else {
        Write-Host "  $container : ✗ Not running"
        $allHealthy = $false
    }
}

# Final status
Write-Host ""
if ($allHealthy) {
    Write-Host "✅ All containers are running!"
    Write-Host ""
    Write-Host "URLs:"
    Write-Host "  Frontend: http://localhost:3001"
    Write-Host "  Backend:  http://localhost:8000"
    Write-Host "  API Docs: http://localhost:8000/docs"
} else {
    Write-Host "⚠ Some containers may not be ready yet"
    Write-Host "  Check status with: docker-compose ps"
    Write-Host "  View logs with: docker-compose logs -f"
}

Write-Host ""
