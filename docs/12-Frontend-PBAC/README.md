# 🎨 FRONTEND PBAC DOCUMENTATION

**Category**: Frontend PBAC Integration, Permission Management  
**Last Updated**: January 21, 2026

---

## 📋 FOLDER CONTENTS (3 Documents)

### 📖 Implementation Guide

1. **[FRONTEND_PBAC_INTEGRATION.md](FRONTEND_PBAC_INTEGRATION.md)** (14KB) ⭐⭐
   - **Purpose**: Complete frontend PBAC implementation guide
   - **Audience**: Frontend developers
   - **Contains**:
     - Permission store architecture (Zustand)
     - 5 permission hooks usage
     - Component-level permission checks
     - Page migration guide
     - Best practices and patterns
   - **Time to Read**: 20-30 minutes
   - **Coverage**: Days 1-3 implementation

### 🚀 Quick Reference

2. **[FRONTEND_PBAC_QUICK_REF.md](FRONTEND_PBAC_QUICK_REF.md)** (5KB) ⭐
   - **Purpose**: Quick reference for developers
   - **Audience**: Frontend developers (daily use)
   - **Contains**:
     - Permission hooks cheat sheet
     - Common patterns
     - Code snippets
     - Troubleshooting tips
   - **Time to Read**: 5 minutes
   - **Usage**: Keep open while coding

### 🎛️ Permission Management UI

3. **[PERMISSION_MANAGEMENT_QUICK_REF.md](PERMISSION_MANAGEMENT_QUICK_REF.md)** (12KB)
   - **Purpose**: Permission Management UI usage guide
   - **Audience**: Admins, Managers, End users
   - **Contains**:
     - Grant/revoke custom permissions workflow
     - Expiration date setting
     - Permission badge component
     - Admin user page features
   - **Time to Read**: 15 minutes
   - **Coverage**: Day 3 Permission Management Page

---

## 🎯 FRONTEND PBAC ARCHITECTURE

### Component Hierarchy

```
Frontend PBAC System
├── State Management (Zustand)
│   └── permissionStore.ts (150 lines)
│       - Load permissions on login
│       - Cache in memory
│       - Sync with backend
│
├── Permission Hooks (5 hooks)
│   ├── usePermission(code) - Single permission check
│   ├── useAnyPermission([codes]) - OR logic
│   ├── useAllPermissions([codes]) - AND logic
│   ├── usePermissions() - Get all permissions
│   └── useHasAnyPermission() - Check if has any
│
├── Components
│   ├── PermissionBadge.tsx (200 lines)
│   │   - "No Permission" badge
│   │   - Lock icon
│   │   - Disabled state styling
│   │
│   └── PermissionManagementPage.tsx (600 lines)
│       - Grant/revoke UI
│       - Expiration date picker
│       - Permission list
│       - Audit log
│
└── Pages (7 migrated pages)
    ├── CuttingPage.tsx (29 checks)
    ├── SewingPage.tsx (34 checks)
    ├── FinishingPage.tsx (28 checks)
    ├── PackingPage.tsx (31 checks)
    ├── PPICPage.tsx (27 checks)
    ├── AdminUserPage.tsx (5 checks)
    └── PermissionManagementPage.tsx (new)
```

---

## 🚀 QUICK START GUIDE

### For New Frontend Developers

**Day 1: Understanding (30 minutes)**
1. Read **[FRONTEND_PBAC_QUICK_REF.md](FRONTEND_PBAC_QUICK_REF.md)** (5 min)
2. Review permission hooks examples (10 min)
3. Understand store architecture (10 min)
4. Try examples in DevTools (5 min)

**Day 2: Implementation (2 hours)**
1. Read **[FRONTEND_PBAC_INTEGRATION.md](FRONTEND_PBAC_INTEGRATION.md)** (30 min)
2. Migrate your first component (1 hour)
3. Test with different roles (30 min)

**Daily Reference**
- Keep **FRONTEND_PBAC_QUICK_REF.md** open
- Use code snippets for common patterns
- Follow best practices

### For Admins/End Users

**Managing Permissions (15 minutes)**
1. Read **[PERMISSION_MANAGEMENT_QUICK_REF.md](PERMISSION_MANAGEMENT_QUICK_REF.md)**
2. Navigate to Settings → Permission Management
3. Grant custom permissions to users
4. Set expiration dates (optional)
5. Verify changes (refresh user page)

---

## 🛠️ PERMISSION HOOKS

### Basic Usage

```tsx
import { usePermission, useAnyPermission } from '@/hooks/usePermission';

function MyComponent() {
  // Single permission check
  const canCreate = usePermission('cutting.work_order.create');
  
  // Multiple permissions (OR logic)
  const canManage = useAnyPermission([
    'cutting.work_order.edit',
    'cutting.work_order.delete'
  ]);
  
  return (
    <>
      {canCreate && (
        <button onClick={handleCreate}>
          Create Work Order
        </button>
      )}
      
      {canManage && (
        <button onClick={handleManage}>
          Manage Work Orders
        </button>
      )}
    </>
  );
}
```

### Button-Level Permission Check

```tsx
<button
  onClick={handleApprove}
  disabled={!usePermission('purchasing.po.approve')}
  className={!usePermission('purchasing.po.approve') ? 'opacity-50 cursor-not-allowed' : ''}
>
  {!usePermission('purchasing.po.approve') && <LockIcon />}
  Approve PO
</button>
```

---

## 📊 IMPLEMENTATION STATUS

### Pages Migrated (7/12 = 58%)

| Page | Permission Checks | Status | Day |
|------|-------------------|--------|-----|
| CuttingPage | 29 checks | ✅ Complete | Day 2 |
| SewingPage | 34 checks | ✅ Complete | Day 2 |
| FinishingPage | 28 checks | ✅ Complete | Day 2 |
| PackingPage | 31 checks | ✅ Complete | Day 2 |
| PPICPage | 27 checks | ✅ Complete | Day 2 |
| AdminUserPage | 5 checks | ✅ Complete | Day 3 |
| PermissionManagementPage | New page | ✅ Complete | Day 3 |

### Sidebar Menu (7/12 = 58%)

| Menu Item | Permission-Based | Status |
|-----------|------------------|--------|
| Dashboard | Role-based | 🟡 Pending |
| Cutting | ✅ cutting.* | ✅ Complete |
| Sewing | ✅ sewing.* | ✅ Complete |
| Finishing | ✅ finishing.* | ✅ Complete |
| Packing | ✅ packing.* | ✅ Complete |
| PPIC | ✅ ppic.* | ✅ Complete |
| Admin Users | ✅ admin.user.* | ✅ Complete |
| Permission Mgmt | ✅ admin.permission.* | ✅ Complete |
| Embroidery | Role-based | 🟡 Pending |
| Warehouse | Role-based | 🟡 Pending |
| QC | Role-based | 🟡 Pending |
| Reports | Role-based | 🟡 Pending |

**Total Permission Checks**: 154 button-level checks across 7 pages

---

## 🎯 PERMISSION CODES

### Production Modules (32 permissions)

**Cutting Module (8)**
- `cutting.work_order.view`
- `cutting.work_order.create`
- `cutting.work_order.edit`
- `cutting.work_order.delete`
- `cutting.transfer.create`
- `cutting.shortage.report`
- `cutting.output.record`
- `cutting.material.allocate`

**Sewing Module (8)**
- `sewing.work_order.view`
- `sewing.work_order.create`
- `sewing.transfer.accept`
- `sewing.transfer.create`
- `sewing.qc.inline`
- `sewing.rework.create`
- `sewing.label.attach`
- `sewing.output.record`

**Finishing Module (8)**
- `finishing.work_order.view`
- `finishing.stuffing.create`
- `finishing.closing.create`
- `finishing.qc.final`
- `finishing.transfer.create`
- `finishing.defect.report`
- `finishing.metal_detect`
- `finishing.output.record`

**Packing Module (8)**
- `packing.work_order.view`
- `packing.carton.scan`
- `packing.label.print`
- `packing.sortir.create`
- `packing.transfer.create`
- `packing.master_carton.create`
- `packing.shipping_mark.create`
- `packing.output.record`

### Admin Modules (4 permissions)

**Admin Module**
- `admin.user.view`
- `admin.user.create`
- `admin.user.edit`
- `admin.user.delete`

**Permission Management**
- `admin.permission.view`
- `admin.permission.grant`
- `admin.permission.revoke`

---

## 🐛 TROUBLESHOOTING

### Permission Not Loading
```tsx
// Check permission store
import { usePermissionStore } from '@/store/permissionStore';

const permissions = usePermissionStore((state) => state.permissions);
console.log('Loaded permissions:', permissions);
// Should show array of 36+ permission codes
```

### Button Still Disabled
```tsx
// Check specific permission
const hasPermission = usePermission('cutting.work_order.create');
console.log('Has permission:', hasPermission);

// Check user role
const user = useAuthStore((state) => state.user);
console.log('User role:', user?.role);
```

### Permission Store Not Updating
```tsx
// Force refresh permissions
const { fetchPermissions } = usePermissionStore();
await fetchPermissions();
```

---

## 📁 RELATED FOLDERS

- **[09-Security/](../09-Security/)**: RBAC/PBAC backend documentation
- **[10-Testing/](../10-Testing/)**: PBAC test plan (30+ test cases)
- **[13-Phase16/](../13-Phase16/)**: Phase 16 status reports
- **[04-Session-Reports/](../04-Session-Reports/)**: Session 13.3-13.5 completion reports

---

## 🔗 QUICK LINKS

**Frontend Files**:
- `erp-ui/frontend/src/store/permissionStore.ts` (150 lines)
- `erp-ui/frontend/src/hooks/usePermission.ts` (5 hooks)
- `erp-ui/frontend/src/components/PermissionBadge.tsx` (200 lines)
- `erp-ui/frontend/src/pages/PermissionManagementPage.tsx` (600 lines)

**Backend Files**:
- `erp-softtoys/app/core/permissions.py` (36 permission codes)
- `erp-softtoys/app/services/permission_service.py` (540+ lines)

---

## 📞 FRONTEND TEAM

**Frontend Lead**: [Contact Info]  
**PBAC Implementation**: Days 1-3 (Session 13.3-13.5)  
**Testing**: Week 4 (11 hours planned)

---

**Last Reorganization**: January 21, 2026  
**Total Documents**: 3 files, ~31KB  
**Status**: ✅ All frontend PBAC docs organized  
**Next**: Week 4 comprehensive testing (30+ test cases)
