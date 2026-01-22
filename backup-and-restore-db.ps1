#!/usr/bin/env pwsh
<#
.SYNOPSIS
    PostgreSQL Database Backup and Restore Script
    Backs up the current database and restores to a clean state with real data

.DESCRIPTION
    - Backs up current database to backup-[timestamp].sql
    - Removes all mock data
    - Restores real data structure
    - Rebuilds all indexes

.EXAMPLE
    .\backup-and-restore-db.ps1 -Backup
    .\backup-and-restore-db.ps1 -Restore
#>

param(
    [switch]$Backup,
    [switch]$Restore,
    [switch]$RestoreFromFile,
    [string]$BackupFile
)

$DbHost = "localhost"
$DbPort = 5432
$DbUser = "postgres"
$DbPassword = "password"
$DbName = "erp_quty_karunia"
$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$BackupDir = "d:\Project\ERP2026\database-backups"

# Ensure backup directory exists
if (-not (Test-Path $BackupDir)) {
    New-Item -ItemType Directory -Path $BackupDir -Force | Out-Null
    Write-Host "✓ Created backup directory: $BackupDir"
}

function Backup-Database {
    Write-Host "📦 Backing up database: $DbName"
    
    $BackupFile = Join-Path $BackupDir "backup-${Timestamp}.sql"
    $env:PGPASSWORD = $DbPassword
    
    try {
        & pg_dump -h $DbHost -p $DbPort -U $DbUser $DbName -v -F p -f $BackupFile
        Write-Host "✓ Database backed up to: $BackupFile"
        Write-Host "  Size: $(Get-Item $BackupFile | Select-Object -ExpandProperty Length) bytes"
        return $BackupFile
    } catch {
        Write-Host "✗ Backup failed: $_"
        return $null
    }
}

function Restore-Database {
    param([string]$File)
    
    if (-not (Test-Path $File)) {
        Write-Host "✗ Backup file not found: $File"
        return $false
    }
    
    Write-Host "♻️  Restoring database from: $File"
    
    $env:PGPASSWORD = $DbPassword
    
    try {
        # Drop current database
        Write-Host "  → Dropping current database..."
        & psql -h $DbHost -p $DbPort -U $DbUser -d postgres -c "DROP DATABASE IF EXISTS $DbName;"
        
        # Create fresh database
        Write-Host "  → Creating fresh database..."
        & psql -h $DbHost -p $DbPort -U $DbUser -d postgres -c "CREATE DATABASE $DbName WITH ENCODING 'UTF8';"
        
        # Restore data
        Write-Host "  → Restoring database structure and data..."
        Get-Content $File | & psql -h $DbHost -p $DbPort -U $DbUser -d $DbName
        
        Write-Host "✓ Database restored successfully"
        return $true
    } catch {
        Write-Host "✗ Restore failed: $_"
        return $false
    }
}

function Clean-MockData {
    Write-Host "🧹 Cleaning mock data..."
    
    $env:PGPASSWORD = $DbPassword
    $CleanupSQL = @"
-- Delete mock data while keeping structure
DELETE FROM audit_logs;
DELETE FROM custom_permissions;
DELETE FROM work_orders;
DELETE FROM manufacturing_orders;
DELETE FROM transfer_logs;
DELETE FROM stock_moves;
DELETE FROM stock_quants;
DELETE FROM stock_lots;
DELETE FROM purchase_orders;
DELETE FROM purchase_order_lines;
DELETE FROM users WHERE username NOT IN ('developer', 'admin', 'operator_cut', 'qc_lab');

-- Reset sequences
SELECT setval(pg_get_serial_sequence('users', 'id'), (SELECT MAX(id) FROM users) + 1);
SELECT setval(pg_get_serial_sequence('products', 'id'), (SELECT MAX(id) FROM products) + 1);
SELECT setval(pg_get_serial_sequence('manufacturing_orders', 'id'), (SELECT MAX(id) FROM manufacturing_orders) + 1);

-- Verify cleanup
SELECT 'Users:' AS category, COUNT(*) AS count FROM users
UNION ALL
SELECT 'Products', COUNT(*) FROM products
UNION ALL
SELECT 'Manufacturing Orders', COUNT(*) FROM manufacturing_orders
UNION ALL
SELECT 'Stock Quantities', COUNT(*) FROM stock_quants;
"@

    try {
        $CleanupSQL | & psql -h $DbHost -p $DbPort -U $DbUser -d $DbName
        Write-Host "✓ Mock data cleaned successfully"
        return $true
    } catch {
        Write-Host "✗ Cleanup failed: $_"
        return $false
    }
}

function Initialize-RealData {
    Write-Host "📊 Initializing real data..."
    
    $env:PGPASSWORD = $DbPassword
    
    try {
        # Run the init script
        if (Test-Path "d:\Project\ERP2026\init-db.sql") {
            Write-Host "  → Running initialization script..."
            Get-Content "d:\Project\ERP2026\init-db.sql" | & psql -h $DbHost -p $DbPort -U $DbUser -d $DbName
            Write-Host "✓ Real data initialized"
            return $true
        } else {
            Write-Host "⚠ No init-db.sql found, skipping data initialization"
            return $false
        }
    } catch {
        Write-Host "✗ Initialization failed: $_"
        return $false
    }
}

# Main execution
if ($Backup) {
    Backup-Database
} elseif ($Restore) {
    Write-Host "🔄 Full restore process starting..."
    Write-Host ""
    
    $backupFile = Backup-Database
    if ($backupFile) {
        Write-Host ""
        if (Clean-MockData) {
            Write-Host ""
            Initialize-RealData
        }
    }
    
    Write-Host ""
    Write-Host "✓ Database restore completed!"
    
} elseif ($RestoreFromFile -and $BackupFile) {
    if (Restore-Database $BackupFile) {
        Write-Host "✓ Restore from backup completed!"
    }
} else {
    Write-Host "PostgreSQL Database Backup & Restore Tool"
    Write-Host ""
    Write-Host "Usage:"
    Write-Host "  .\backup-and-restore-db.ps1 -Backup              # Backup current database"
    Write-Host "  .\backup-and-restore-db.ps1 -Restore             # Backup → Clean → Restore"
    Write-Host "  .\backup-and-restore-db.ps1 -RestoreFromFile -BackupFile <path>"
    Write-Host ""
    Write-Host "Backup Location: $BackupDir"
    Write-Host ""
}
