# Frontend PBAC - Quick Reference
**Phase 16 Week 4 - Permission-Based Access Control**

---

## ✅ Completed Infrastructure

### Backend
- `/auth/permissions` endpoint (returns user's effective permissions)
- Redis caching (<1ms hot cache, <10ms cold cache)

### Frontend
- Permission store (`src/store/permissionStore.ts`)
- Permission hooks (`src/hooks/usePermission.ts`)
- Auth integration (load permissions on login/logout)
- Sidebar updated (permission-based menu filtering)

---

## 🎯 How to Use Permissions in Components

### 1. Import Hook
```tsx
import { usePermission, useAnyPermission } from '@/hooks/usePermission'
```

### 2. Check Permission
```tsx
const canAllocateMaterial = usePermission('cutting.allocate_material')
const canPerformQC = usePermission('sewing.inline_qc')
```

### 3. Conditional Rendering
```tsx
{canAllocateMaterial && (
  <Button onClick={handleAllocate}>Allocate Material</Button>
)}

{canPerformQC && (
  <Section title="Quality Control">
    {/* QC UI */}
  </Section>
)}
```

### 4. Multiple Permissions (OR logic)
```tsx
const canViewCutting = useAnyPermission([
  'cutting.view_status',
  'cutting.allocate_material'
])
```

---

## 📋 Permission Codes

### Cutting
- `cutting.allocate_material` - Receive SPK
- `cutting.complete_operation` - Complete cutting
- `cutting.handle_variance` - Handle shortage
- `cutting.line_clearance` - Line clearance check
- `cutting.create_transfer` - Transfer to next stage
- `cutting.view_status` - View status

### Sewing
- `sewing.accept_transfer` - Accept transfer from cutting
- `sewing.validate_input` - Validate input materials
- `sewing.inline_qc` - **QC Inspector only**
- `sewing.create_transfer` - Transfer to finishing
- `sewing.view_status` - View status
- `sewing.return_to_stage` - Internal loop

### Finishing
- `finishing.accept_transfer` - Accept transfer
- `finishing.line_clearance` - Line clearance
- `finishing.perform_stuffing` - Stuffing operation
- `finishing.perform_closing` - Closing & grooming
- `finishing.metal_detector_qc` - **Metal detector test (QC)**
- `finishing.final_qc` - Final QC check
- `finishing.convert_to_fg` - Convert to finished goods
- `finishing.view_status` - View status

### Packing
- `packing.sort_by_destination` - Sort by destination
- `packing.pack_product` - Pack into cartons
- `packing.label_carton` - Apply shipping mark
- `packing.complete_operation` - Complete packing
- `packing.view_status` - View status

### PPIC
- `ppic.create_mo` - Create manufacturing order
- `ppic.view_mo` - View manufacturing order
- `ppic.schedule_production` - View MO list
- `ppic.approve_mo` - Approve MO

### Dashboard
- `dashboard.view_stats` - View statistics
- `dashboard.view_production` - View production status
- `dashboard.view_alerts` - View alerts
- `dashboard.view_trends` - View trends
- `dashboard.refresh_views` - Refresh materialized views

### Admin
- `admin.manage_users` - User management
- `admin.view_system_info` - System info

### Import/Export
- `import_export.import_data` - Import data
- `import_export.export_data` - Export data

---

## 📝 Component Update Pattern

### Before (Role-based)
```tsx
import { useAuthStore } from '@/store'
import { UserRole } from '@/types'

export const CuttingPage = () => {
  const { user } = useAuthStore()
  
  const canAllocate = user?.role === UserRole.SPV_CUTTING || 
                      user?.role === UserRole.ADMIN
  
  return (
    <>
      {canAllocate && <Button>Allocate</Button>}
    </>
  )
}
```

### After (Permission-based)
```tsx
import { usePermission } from '@/hooks/usePermission'

export const CuttingPage = () => {
  const canAllocate = usePermission('cutting.allocate_material')
  
  return (
    <>
      {canAllocate && <Button>Allocate</Button>}
    </>
  )
}
```

---

## 🔄 Backward Compatibility

The Sidebar supports **both** permission-based and role-based menu items:

### Permission-based (NEW)
```tsx
{ 
  label: 'Cutting', 
  permissions: ['cutting.view_status'] 
}
```

### Role-based (OLD - still works)
```tsx
{ 
  label: 'Warehouse', 
  roles: [UserRole.WAREHOUSE_ADMIN] 
}
```

**Priority:** If `permissions` array exists, it overrides `roles`.

---

## 🧪 Testing

### Check Permissions in Console
```javascript
// Open browser console
const permStore = window.Zustand.usePermissionStore.getState()
console.log(permStore.permissions)

// Check specific permission
console.log(permStore.hasPermission('cutting.allocate_material'))
```

### Reload Permissions
```javascript
const permStore = window.Zustand.usePermissionStore.getState()
await permStore.loadPermissions()
```

---

## ⏭️ Next Pages to Migrate

### High Priority (Days 2-3)
1. **CuttingPage.tsx** - 6 permission checks
2. **SewingPage.tsx** - 6 permission checks
3. **FinishingPage.tsx** - 8 permission checks
4. **PackingPage.tsx** - 5 permission checks

### Medium Priority (Day 4)
5. **PPICPage.tsx** - 4 permission checks
6. **AdminUserPage.tsx** - 2 permission checks

---

## 🐛 Common Issues

### Issue: Permissions not loading
**Solution:** Check browser console for errors. Verify `/auth/permissions` endpoint is accessible.

### Issue: Menu items not showing
**Solution:** Ensure permissions array is correct. Check user's permissions in console.

### Issue: Permissions stale after role change
**Solution:** User must log out and log back in to refresh permissions.

---

## 📚 Documentation

- **Full Guide:** `docs/FRONTEND_PBAC_INTEGRATION.md` (600 lines)
- **Session Report:** `docs/SESSION_13.3_FRONTEND_PBAC_COMPLETE.md` (500 lines)
- **Task List:** `docs/WEEK4_COMPLETE_TASK_LIST.md` (300 lines)
- **Backend PBAC:** `docs/SESSION_13.2_PBAC_COMPLETE.md` (5,000 lines)

---

**Status:** ✅ **INFRASTRUCTURE READY - START PAGE MIGRATION**
