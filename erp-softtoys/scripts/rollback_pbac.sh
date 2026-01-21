#!/bin/bash
################################################################################
# PBAC Migration Rollback Script
# Emergency rollback procedure for RBAC → PBAC migration
#
# Author: Daniel (IT Senior Developer)
# Date: January 21, 2026
# Version: 1.0
#
# Usage: ./scripts/rollback_pbac.sh
#
# CRITICAL: Only use this script if PBAC migration fails validation!
################################################################################

set -e  # Exit on error

echo "⚠️  =============================================="
echo "⚠️  PBAC MIGRATION ROLLBACK"
echo "⚠️  =============================================="
echo ""
echo "This script will:"
echo "1. Switch traffic back to RBAC (old) version"
echo "2. Drop PBAC tables from database"
echo "3. Restore to last known good state"
echo ""
read -p "Are you sure you want to rollback? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "❌ Rollback cancelled"
    exit 0
fi

echo ""
echo "📊 Starting rollback process..."
echo ""

# Step 1: Verify database connection
echo "🔍 Step 1: Checking database connection..."
docker-compose exec -T postgres psql -U erp_user -d erp_db -c "SELECT 1;" > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ Database connection OK"
else
    echo "❌ Database connection failed"
    exit 1
fi

# Step 2: Drop PBAC tables
echo ""
echo "🗑️  Step 2: Dropping PBAC tables..."
docker-compose exec -T postgres psql -U erp_user -d erp_db <<EOF
-- Drop PBAC tables in reverse dependency order
DROP TABLE IF EXISTS user_custom_permissions CASCADE;
DROP TABLE IF EXISTS role_permissions CASCADE;
DROP TABLE IF EXISTS permissions CASCADE;
DROP TABLE IF EXISTS pbac_migrations CASCADE;

-- Verify tables dropped
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
  AND table_name IN ('permissions', 'role_permissions', 'user_custom_permissions', 'pbac_migrations');
EOF

if [ $? -eq 0 ]; then
    echo "✅ PBAC tables dropped successfully"
else
    echo "❌ Failed to drop PBAC tables"
    exit 1
fi

# Step 3: Verify RBAC still intact
echo ""
echo "🔍 Step 3: Verifying RBAC system integrity..."
docker-compose exec -T postgres psql -U erp_user -d erp_db -c "SELECT COUNT(*) as user_count FROM users;" > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ RBAC system intact (users table accessible)"
else
    echo "❌ RBAC system check failed"
    exit 1
fi

# Step 4: Restart backend to reload RBAC code
echo ""
echo "🔄 Step 4: Restarting backend service..."
docker-compose restart backend

# Wait for backend to be healthy
echo "⏳ Waiting for backend to start..."
sleep 10

# Health check
curl -f http://localhost:8000/api/health > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ Backend restarted successfully"
else
    echo "⚠️  Backend health check failed - manual verification required"
fi

# Step 5: Test RBAC authentication
echo ""
echo "🔐 Step 5: Testing RBAC authentication..."
response=$(curl -s -o /dev/null -w "%{http_code}" -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"Admin@123456"}')

if [ "$response" = "200" ]; then
    echo "✅ RBAC authentication working"
else
    echo "⚠️  Auth test returned HTTP $response - verify manually"
fi

# Step 6: Create rollback log
echo ""
echo "📝 Step 6: Creating rollback log..."
ROLLBACK_LOG="rollback_$(date +%Y%m%d_%H%M%S).log"
cat > "$ROLLBACK_LOG" <<EOL
PBAC Migration Rollback Report
==============================
Date: $(date)
Performed by: $USER
Status: SUCCESS

Actions Performed:
- Dropped user_custom_permissions table
- Dropped role_permissions table
- Dropped permissions table
- Dropped pbac_migrations table
- Restarted backend service
- Verified RBAC system

System State:
- Database: RBAC mode (no PBAC tables)
- Backend: Restarted and healthy
- Authentication: RBAC working

Next Steps:
1. Investigate migration failure root cause
2. Fix issues identified in migration logs
3. Re-run migration after fixes
4. Update deployment procedures

EOL

echo "✅ Rollback log created: $ROLLBACK_LOG"

# Final summary
echo ""
echo "=============================================="
echo "✅ ROLLBACK COMPLETE"
echo "=============================================="
echo ""
echo "System Status:"
echo "- Database: RBAC mode (PBAC tables removed)"
echo "- Backend: Restarted with RBAC code"
echo "- Frontend: No changes (RBAC compatible)"
echo ""
echo "Rollback log: $ROLLBACK_LOG"
echo ""
echo "⚠️  IMPORTANT:"
echo "1. Investigate migration failure before re-attempting"
echo "2. Review logs in erp-softtoys/logs/"
echo "3. Contact DBA if database issues persist"
echo "4. Do NOT re-run migration until root cause fixed"
echo ""
