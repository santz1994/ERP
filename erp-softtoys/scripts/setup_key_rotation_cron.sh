#!/bin/bash

# ============================================================================
# SECRET_KEY Rotation Cron Job Setup
# ============================================================================
# Purpose: Configure automated SECRET_KEY rotation every 90 days
# Author: Daniel - IT Developer Senior
# Date: 2026-01-20
# ============================================================================

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "============================================================================"
echo "SECRET_KEY Rotation - Cron Job Setup"
echo "============================================================================"
echo "Project Root: $PROJECT_ROOT"
echo "Python Script: $PROJECT_ROOT/scripts/rotate_secret_key.py"
echo ""

# ============================================================================
# Step 1: Verify Python Script Exists
# ============================================================================
echo "[Step 1/5] Verifying rotation script..."
if [ ! -f "$PROJECT_ROOT/scripts/rotate_secret_key.py" ]; then
    echo "❌ ERROR: Rotation script not found at $PROJECT_ROOT/scripts/rotate_secret_key.py"
    exit 1
fi
echo "✅ Rotation script found"

# ============================================================================
# Step 2: Verify Docker Compose Configuration
# ============================================================================
echo "[Step 2/5] Verifying Docker Compose..."
if [ ! -f "$PROJECT_ROOT/docker-compose.yml" ]; then
    echo "❌ ERROR: docker-compose.yml not found at $PROJECT_ROOT"
    exit 1
fi
echo "✅ Docker Compose configuration found"

# ============================================================================
# Step 3: Create Cron Job Entry
# ============================================================================
echo "[Step 3/5] Creating cron job entry..."

# Run at 2:00 AM server time, every 90 days
# Minute Hour Day Month DayOfWeek Command
CRON_SCHEDULE="0 2 */90 * *"
CRON_COMMAND="cd $PROJECT_ROOT && python scripts/rotate_secret_key.py && docker-compose restart backend"
CRON_ENTRY="$CRON_SCHEDULE $CRON_COMMAND"

echo "Cron Entry:"
echo "  $CRON_ENTRY"
echo ""

# ============================================================================
# Step 4: Add Cron Job (with backup)
# ============================================================================
echo "[Step 4/5] Installing cron job..."

# Backup existing crontab
echo "Backing up existing crontab..."
BACKUP_DIR="$PROJECT_ROOT/backups/crontab"
mkdir -p "$BACKUP_DIR"
BACKUP_FILE="$BACKUP_DIR/crontab_backup_$(date +%Y%m%d_%H%M%S).txt"
crontab -l > "$BACKUP_FILE" 2>/dev/null || echo "# No existing crontab" > "$BACKUP_FILE"
echo "✅ Crontab backed up to: $BACKUP_FILE"

# Check if entry already exists
if crontab -l 2>/dev/null | grep -q "rotate_secret_key.py"; then
    echo "⚠️  WARNING: SECRET_KEY rotation cron job already exists!"
    echo "Existing entry:"
    crontab -l | grep "rotate_secret_key.py"
    echo ""
    read -p "Do you want to replace it? (y/N): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ Installation cancelled by user"
        exit 1
    fi
    
    # Remove old entry
    crontab -l | grep -v "rotate_secret_key.py" | crontab -
    echo "✅ Old cron job removed"
fi

# Add new entry
(crontab -l 2>/dev/null; echo "$CRON_ENTRY") | crontab -
echo "✅ Cron job installed successfully"

# ============================================================================
# Step 5: Verify Installation
# ============================================================================
echo "[Step 5/5] Verifying installation..."
echo "Current crontab entries:"
crontab -l | grep -i "secret\|rotate" || echo "  (no matching entries - this shouldn't happen!)"

echo ""
echo "============================================================================"
echo "✅ Setup Complete!"
echo "============================================================================"
echo "Cron Job Details:"
echo "  Schedule: Every 90 days at 2:00 AM server time"
echo "  Action 1: Rotate SECRET_KEY (python scripts/rotate_secret_key.py)"
echo "  Action 2: Restart backend service (docker-compose restart backend)"
echo ""
echo "Next Rotation: (Run 'python scripts/rotate_secret_key.py --dry-run' to check)"
echo ""
echo "Manual Rotation:"
echo "  1. Test: python scripts/rotate_secret_key.py --dry-run"
echo "  2. Execute: python scripts/rotate_secret_key.py"
echo "  3. Restart: docker-compose restart backend"
echo ""
echo "Monitoring:"
echo "  - Rotation logs: logs/secret_key_rotation/"
echo "  - Cron logs: /var/log/syslog | grep CRON"
echo "  - Manual test: python scripts/rotate_secret_key.py --test"
echo ""
echo "Rollback:"
echo "  - Restore crontab: crontab $BACKUP_FILE"
echo "  - Remove cron job: crontab -e (then delete the rotation line)"
echo "============================================================================"
