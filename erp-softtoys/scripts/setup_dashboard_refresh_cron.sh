#!/bin/bash

# ============================================================================
# Dashboard Materialized Views - Auto-Refresh Setup
# ============================================================================
# Purpose: Configure automated refresh of dashboard materialized views
# Author: Daniel - IT Developer Senior
# Date: 2026-01-21
# Schedule: Every 5 minutes
# ============================================================================

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "============================================================================"
echo "Dashboard Materialized Views - Cron Job Setup"
echo "============================================================================"
echo "Project Root: $PROJECT_ROOT"
echo ""

# ============================================================================
# Step 1: Verify PostgreSQL Connection
# ============================================================================
echo "[Step 1/5] Verifying PostgreSQL connection..."
if ! docker exec erp-postgres psql -U postgres -d quty_erp -c "\conninfo" >/dev/null 2>&1; then
    echo "❌ ERROR: Cannot connect to PostgreSQL database"
    echo "   Make sure Docker containers are running: docker-compose up -d"
    exit 1
fi
echo "✅ PostgreSQL connection verified"

# ============================================================================
# Step 2: Verify Materialized Views Exist
# ============================================================================
echo "[Step 2/5] Checking materialized views..."
VIEW_COUNT=$(docker exec erp-postgres psql -U postgres -d quty_erp -t -c "
    SELECT COUNT(*) FROM pg_matviews 
    WHERE matviewname IN (
        'mv_dashboard_stats', 
        'mv_production_dept_status',
        'mv_recent_alerts',
        'mv_mo_trends_7days'
    );
" | tr -d ' ')

if [ "$VIEW_COUNT" != "4" ]; then
    echo "⚠️  WARNING: Not all materialized views exist (found $VIEW_COUNT/4)"
    echo "   Run the SQL migration first:"
    echo "   docker exec -i erp-postgres psql -U postgres -d quty_erp < scripts/create_dashboard_materialized_views.sql"
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    echo "✅ All 4 materialized views found"
fi

# ============================================================================
# Step 3: Create Cron Job Entry
# ============================================================================
echo "[Step 3/5] Creating cron job entry..."

# Run every 5 minutes
CRON_SCHEDULE="*/5 * * * *"
CRON_COMMAND="docker exec erp-postgres psql -U postgres -d quty_erp -c 'SELECT refresh_dashboard_views();' >> $PROJECT_ROOT/logs/dashboard_refresh.log 2>&1"
CRON_ENTRY="$CRON_SCHEDULE $CRON_COMMAND"

echo "Cron Entry:"
echo "  $CRON_ENTRY"
echo ""

# ============================================================================
# Step 4: Backup Existing Crontab
# ============================================================================
echo "[Step 4/5] Backing up existing crontab..."
BACKUP_DIR="$PROJECT_ROOT/backups/crontab"
mkdir -p "$BACKUP_DIR"
BACKUP_FILE="$BACKUP_DIR/crontab_backup_$(date +%Y%m%d_%H%M%S).txt"
crontab -l > "$BACKUP_FILE" 2>/dev/null || echo "# No existing crontab" > "$BACKUP_FILE"
echo "✅ Crontab backed up to: $BACKUP_FILE"

# ============================================================================
# Step 5: Install Cron Job
# ============================================================================
echo "[Step 5/5] Installing cron job..."

# Check if entry already exists
if crontab -l 2>/dev/null | grep -q "refresh_dashboard_views"; then
    echo "⚠️  WARNING: Dashboard refresh cron job already exists!"
    echo "Existing entry:"
    crontab -l | grep "refresh_dashboard_views"
    echo ""
    read -p "Do you want to replace it? (y/N): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ Installation cancelled by user"
        exit 1
    fi
    
    # Remove old entry
    crontab -l | grep -v "refresh_dashboard_views" | crontab -
    echo "✅ Old cron job removed"
fi

# Create logs directory
mkdir -p "$PROJECT_ROOT/logs"

# Add new entry
(crontab -l 2>/dev/null; echo "$CRON_ENTRY") | crontab -
echo "✅ Cron job installed successfully"

# ============================================================================
# Step 6: Test Manual Refresh
# ============================================================================
echo ""
echo "Testing manual refresh..."
if docker exec erp-postgres psql -U postgres -d quty_erp -c "SELECT refresh_dashboard_views();" >/dev/null 2>&1; then
    echo "✅ Manual refresh test successful"
else
    echo "⚠️  WARNING: Manual refresh failed. Check logs for details."
fi

echo ""
echo "============================================================================"
echo "✅ Setup Complete!"
echo "============================================================================"
echo "Cron Job Details:"
echo "  Schedule: Every 5 minutes (*/5 * * * *)"
echo "  Command: Refresh all dashboard materialized views"
echo "  Log file: $PROJECT_ROOT/logs/dashboard_refresh.log"
echo ""
echo "Materialized Views:"
echo "  - mv_dashboard_stats (top-level stats)"
echo "  - mv_production_dept_status (department progress)"
echo "  - mv_recent_alerts (last 24h alerts)"
echo "  - mv_mo_trends_7days (MO trends chart)"
echo ""
echo "Manual Operations:"
echo "  Test refresh: docker exec erp-postgres psql -U postgres -d quty_erp -c 'SELECT refresh_dashboard_views();'"
echo "  Check logs: tail -f logs/dashboard_refresh.log"
echo "  View cron jobs: crontab -l | grep dashboard"
echo "  Remove cron job: crontab -e (then delete the line)"
echo ""
echo "Monitoring:"
echo "  - Cron logs: /var/log/syslog | grep CRON"
echo "  - View data: psql -U postgres -d quty_erp -c 'SELECT * FROM mv_dashboard_stats;'"
echo "  - Refresh time: psql -U postgres -d quty_erp -c 'SELECT refreshed_at FROM mv_dashboard_stats;'"
echo "============================================================================"
