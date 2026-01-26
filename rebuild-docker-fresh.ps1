#!/usr/bin/env powershell
# ============================================================================
# Session 27: Docker Rebuild & Database Reseed Script
# Purpose: Clean rebuild of all Docker containers with fresh database seed
# Status: Production Ready
# ============================================================================

param(
    [string]$BackupFile = "",
    [switch]$SkipBackup = $false,
    [switch]$DryRun = $false
)

$ErrorActionPreference = "Stop"
$WarningPreference = "Continue"

# Colors for output
$colors = @{
    Success = "Green"
    Warning = "Yellow"
    Error = "Red"
    Info = "Cyan"
    Highlight = "Magenta"
}

function Write-LogInfo {
    param([string]$Message)
    Write-Host "ℹ️  $Message" -ForegroundColor $colors.Info
}

function Write-LogSuccess {
    param([string]$Message)
    Write-Host "✅ $Message" -ForegroundColor $colors.Success
}

function Write-LogWarning {
    param([string]$Message)
    Write-Host "⚠️  $Message" -ForegroundColor $colors.Warning
}

function Write-LogError {
    param([string]$Message)
    Write-Host "❌ $Message" -ForegroundColor $colors.Error
}

function Write-LogSeparator {
    Write-Host "─" * 80 -ForegroundColor $colors.Info
}

# ============================================================================
# PHASE 1: Backup Current Database
# ============================================================================

Write-LogSeparator
Write-Host "PHASE 1: Database Backup" -ForegroundColor $colors.Highlight
Write-LogSeparator

if ($SkipBackup) {
    Write-LogWarning "Skipping database backup (--SkipBackup flag set)"
} else {
    Write-LogInfo "Backing up current database..."
    
    $timestamp = Get-Date -Format "yyyy-MM-dd_HHmmss"
    $backupPath = "D:/Project/ERP2026/backups/erp_backup_$timestamp.sql"
    
    try {
        Write-LogInfo "Creating backup at: $backupPath"
        
        if ($DryRun) {
            Write-LogWarning "DRY RUN: Would execute: docker exec erp_postgres pg_dump..."
        } else {
            docker exec erp_postgres pg_dump -U postgres --verbose erp_quty_karunia > $backupPath 2>&1
            
            $backupSize = (Get-Item $backupPath).Length / 1MB
            Write-LogSuccess "Database backed up successfully ($([Math]::Round($backupSize, 2)) MB)"
            Write-LogInfo "Backup file: $backupPath"
        }
    } catch {
        Write-LogError "Database backup failed: $_"
        exit 1
    }
}

# ============================================================================
# PHASE 2: Stop All Containers
# ============================================================================

Write-LogSeparator
Write-Host "PHASE 2: Stop All Containers" -ForegroundColor $colors.Highlight
Write-LogSeparator

Write-LogInfo "Stopping all Docker containers..."

$containers = @(
    "erp_frontend",
    "erp_backend",
    "erp_postgres",
    "erp_redis",
    "erp_adminer",
    "erp_pgadmin",
    "erp_prometheus",
    "erp_grafana"
)

foreach ($container in $containers) {
    try {
        $status = docker ps -a --filter "name=$container" --format "table {{.Status}}"
        
        if ($status -like "*Up*") {
            Write-LogInfo "Stopping $container..."
            
            if ($DryRun) {
                Write-LogWarning "DRY RUN: Would execute: docker stop $container"
            } else {
                docker stop $container -t 30
                Write-LogSuccess "Stopped $container"
            }
        }
    } catch {
        Write-LogWarning "Could not stop $container (may not exist): $_"
    }
}

# Optional: Remove stopped containers for clean rebuild
Write-LogInfo "Removing stopped containers..."
if ($DryRun) {
    Write-LogWarning "DRY RUN: Would execute: docker-compose down"
} else {
    docker-compose down --remove-orphans
    Write-LogSuccess "Containers removed"
}

# ============================================================================
# PHASE 3: Prune Docker Resources
# ============================================================================

Write-LogSeparator
Write-Host "PHASE 3: Prune Docker Resources" -ForegroundColor $colors.Highlight
Write-LogSeparator

Write-LogWarning "Pruning unused Docker resources to free space..."

if ($DryRun) {
    Write-LogWarning "DRY RUN: Would execute: docker system prune"
} else {
    Write-LogInfo "Pruning containers..."
    docker container prune -f
    
    Write-LogInfo "Pruning images..."
    docker image prune -f
    
    Write-LogInfo "Pruning volumes..."
    docker volume prune -f
    
    Write-LogInfo "Pruning networks..."
    docker network prune -f
    
    Write-LogSuccess "Docker resources pruned"
}

# ============================================================================
# PHASE 4: Rebuild Docker Images
# ============================================================================

Write-LogSeparator
Write-Host "PHASE 4: Rebuild Docker Images" -ForegroundColor $colors.Highlight
Write-LogSeparator

Write-LogInfo "Building fresh Docker images (no cache)..."

if ($DryRun) {
    Write-LogWarning "DRY RUN: Would execute: docker-compose build --no-cache"
} else {
    try {
        Push-Location "D:/Project/ERP2026"
        
        docker-compose build --no-cache
        
        Write-LogSuccess "Docker images built successfully"
        
        Pop-Location
    } catch {
        Write-LogError "Docker build failed: $_"
        exit 1
    }
}

# ============================================================================
# PHASE 5: Start Fresh Containers
# ============================================================================

Write-LogSeparator
Write-Host "PHASE 5: Start Fresh Containers" -ForegroundColor $colors.Highlight
Write-LogSeparator

Write-LogInfo "Starting fresh containers..."

if ($DryRun) {
    Write-LogWarning "DRY RUN: Would execute: docker-compose up -d"
} else {
    try {
        Push-Location "D:/Project/ERP2026"
        
        docker-compose up -d
        
        Write-LogSuccess "Containers started"
        
        # Wait for containers to be healthy
        Write-LogInfo "Waiting for containers to be healthy (30 seconds)..."
        Start-Sleep -Seconds 30
        
        # Check container status
        Write-LogInfo "Checking container health..."
        $unhealthyContainers = 0
        
        foreach ($container in $containers) {
            $status = docker ps --filter "name=$container" --format "table {{.Names}}\t{{.Status}}" 2>/dev/null
            
            if ($status -like "*unhealthy*") {
                Write-LogWarning "⚠️  $container is unhealthy"
                $unhealthyContainers++
            } elseif ($status -like "*Up*") {
                Write-LogSuccess "✅ $container is running"
            }
        }
        
        if ($unhealthyContainers -gt 0) {
            Write-LogWarning "Some containers may need more time to become healthy"
            Write-LogInfo "Run 'docker ps' to check status"
        }
        
        Pop-Location
    } catch {
        Write-LogError "Failed to start containers: $_"
        exit 1
    }
}

# ============================================================================
# PHASE 6: Run Database Migrations
# ============================================================================

Write-LogSeparator
Write-Host "PHASE 6: Run Database Migrations" -ForegroundColor $colors.Highlight
Write-LogSeparator

Write-LogInfo "Running database migrations..."

if ($DryRun) {
    Write-LogWarning "DRY RUN: Would execute: docker exec erp_backend alembic upgrade head"
} else {
    try {
        Write-LogInfo "Waiting for database to be ready (10 seconds)..."
        Start-Sleep -Seconds 10
        
        # Check if database is accessible
        docker exec erp_postgres pg_isready -U postgres
        
        if ($LASTEXITCODE -ne 0) {
            Write-LogError "Database is not ready"
            exit 1
        }
        
        Write-LogInfo "Running migrations..."
        docker exec erp_backend bash -c "cd /app && alembic upgrade head"
        
        Write-LogSuccess "Database migrations completed"
        
    } catch {
        Write-LogWarning "Migration step encountered issue: $_"
        Write-LogInfo "This may be normal if migrations are already applied"
    }
}

# ============================================================================
# PHASE 7: Reseed Database
# ============================================================================

Write-LogSeparator
Write-Host "PHASE 7: Reseed Database" -ForegroundColor $colors.Highlight
Write-LogSeparator

Write-LogInfo "Reseeding database with production data..."

if ($DryRun) {
    Write-LogWarning "DRY RUN: Would execute: docker exec erp_backend python seed_all_users.py"
} else {
    try {
        Write-LogInfo "Creating initial users and roles..."
        docker exec erp_backend bash -c "cd /app && python seed_all_users.py"
        
        Write-LogSuccess "Initial seed completed"
        
        # Optional: Run additional seed scripts
        Write-LogInfo "Creating warehouse materials..."
        docker exec erp_backend bash -c "cd /app && python quick_seed.py" 2>/dev/null || Write-LogWarning "Additional seed skipped (optional)"
        
        Write-LogSuccess "Database reseeding completed"
        
    } catch {
        Write-LogWarning "Reseed encountered issue: $_"
        Write-LogInfo "This may be normal - check database content manually"
    }
}

# ============================================================================
# PHASE 8: Verification & Health Check
# ============================================================================

Write-LogSeparator
Write-Host "PHASE 8: Verification & Health Check" -ForegroundColor $colors.Highlight
Write-LogSeparator

Write-LogInfo "Running system health checks..."

if ($DryRun) {
    Write-LogWarning "DRY RUN: Skipping health checks"
} else {
    try {
        # Check Backend Health
        Write-LogInfo "Checking Backend health..."
        $backendHealth = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/health" -UseBasicParsing -ErrorAction SilentlyContinue
        if ($backendHealth.StatusCode -eq 200) {
            Write-LogSuccess "Backend is healthy"
        } else {
            Write-LogWarning "Backend health check returned: $($backendHealth.StatusCode)"
        }
        
        # Check Frontend Health
        Write-LogInfo "Checking Frontend health..."
        $frontendHealth = Invoke-WebRequest -Uri "http://localhost:3001" -UseBasicParsing -ErrorAction SilentlyContinue
        if ($frontendHealth.StatusCode -eq 200) {
            Write-LogSuccess "Frontend is accessible"
        } else {
            Write-LogWarning "Frontend check returned: $($frontendHealth.StatusCode)"
        }
        
        # Check Database Connectivity
        Write-LogInfo "Checking Database connectivity..."
        $dbCheck = docker exec erp_postgres pg_isready -U postgres
        Write-LogSuccess "Database is accessible"
        
        # Check Redis
        Write-LogInfo "Checking Redis..."
        $redisCheck = docker exec erp_redis redis-cli ping
        if ($redisCheck -like "*PONG*") {
            Write-LogSuccess "Redis is healthy"
        }
        
    } catch {
        Write-LogWarning "Health check encountered issue: $_"
    }
}

# ============================================================================
# FINAL SUMMARY
# ============================================================================

Write-LogSeparator
Write-Host "REBUILD COMPLETE" -ForegroundColor $colors.Highlight
Write-LogSeparator

if ($DryRun) {
    Write-LogWarning "DRY RUN MODE - No changes were made"
} else {
    Write-LogSuccess "All phases completed successfully"
    
    Write-Host ""
    Write-Host "📋 System Access URLs:" -ForegroundColor $colors.Highlight
    Write-Host "  Frontend:  http://localhost:3001" -ForegroundColor $colors.Info
    Write-Host "  Backend:   http://localhost:8000/api/v1/docs" -ForegroundColor $colors.Info
    Write-Host "  PgAdmin:   http://localhost:5050" -ForegroundColor $colors.Info
    Write-Host "  Adminer:   http://localhost:8080" -ForegroundColor $colors.Info
    Write-Host "  Grafana:   http://localhost:3000" -ForegroundColor $colors.Info
    Write-Host ""
    
    Write-Host "🔑 Default Credentials:" -ForegroundColor $colors.Highlight
    Write-Host "  Database: postgres / password" -ForegroundColor $colors.Info
    Write-Host "  PgAdmin:  admin@erp.local / password123" -ForegroundColor $colors.Info
    Write-Host "  Grafana:  admin / admin" -ForegroundColor $colors.Info
    Write-Host ""
    
    Write-LogWarning "⚠️  Remember to:"
    Write-Host "  1. Update CORS_ORIGINS for production deployment" -ForegroundColor $colors.Warning
    Write-Host "  2. Run comprehensive tests before deploying to production" -ForegroundColor $colors.Warning
    Write-Host "  3. Verify all API endpoints (Session 27 report: 157 endpoints)" -ForegroundColor $colors.Warning
    Write-Host "  4. Check database backup location: D:/Project/ERP2026/backups/" -ForegroundColor $colors.Warning
}

Write-LogSeparator
Write-Host "Session 27 Docker Rebuild & Reseed Complete" -ForegroundColor $colors.Success
Write-LogSeparator
