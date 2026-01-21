# Frontend PBAC Integration Plan
**Phase 16 Week 4 - UI Integration**  
**Date:** January 21, 2026

---

## Current State Analysis

### ✅ Already Implemented (Role-Based)
- **Sidebar.tsx**: Role-based menu visibility
- **roleGuard.ts**: Role-based route protection (382 lines)
- **MODULE_ACCESS_MATRIX**: Comprehensive role-to-module mapping
- **Auth Store**: User role storage and management

### 🔄 Needs Migration (To Permission-Based)
- Menu item visibility (currently role-based)
- Button/action visibility within pages
- API error handling for 403 Forbidden
- Permission checking utilities

---

## Architecture Design

### 1. Permission Store
**File:** `src/store/permissionStore.ts`

```typescript
interface PermissionState {
  permissions: string[]
  loading: boolean
  
  // Actions
  loadPermissions: (userId: number) => Promise<void>
  hasPermission: (code: string) => boolean
  hasAnyPermission: (codes: string[]) => boolean
  clearPermissions: () => void
}
```

**Features:**
- Fetch user permissions from backend `/auth/permissions`
- Cache permissions in memory
- Provide utility functions for permission checks

---

### 2. Permission Hook
**File:** `src/hooks/usePermission.ts`

```typescript
export const usePermission = (permissionCode: string) => {
  const { permissions } = usePermissionStore()
  return permissions.includes(permissionCode)
}

export const useAnyPermission = (permissionCodes: string[]) => {
  const { permissions } = usePermissionStore()
  return permissionCodes.some(code => permissions.includes(code))
}
```

**Usage:**
```tsx
// In component
const canAllocateMaterial = usePermission('cutting.allocate_material')
const canPerformQC = usePermission('sewing.inline_qc')

{canAllocateMaterial && (
  <Button onClick={handleAllocate}>Allocate Material</Button>
)}
```

---

### 3. Backend API Enhancement
**File:** `app/api/v1/auth.py`

Add endpoint to return user's effective permissions:

```python
@router.get("/permissions")
async def get_user_permissions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's effective permissions (role + custom permissions)"""
    perm_service = get_permission_service()
    
    # Get all permission codes
    all_permissions = db.query(Permission).all()
    
    # Check which ones user has
    user_permissions = [
        perm.code 
        for perm in all_permissions 
        if perm_service.has_permission(db, current_user, perm.code)
    ]
    
    return {
        "user_id": current_user.id,
        "role": current_user.role.value,
        "permissions": user_permissions
    }
```

---

## Migration Strategy

### Phase 1: Infrastructure (Day 1)

#### Step 1: Create Permission Store
```typescript
// src/store/permissionStore.ts
import { create } from 'zustand'
import { apiClient } from '@/api/client'

interface PermissionState {
  permissions: string[]
  loading: boolean
  error: string | null
  
  loadPermissions: () => Promise<void>
  hasPermission: (code: string) => boolean
  hasAnyPermission: (codes: string[]) => boolean
  clearPermissions: () => void
}

export const usePermissionStore = create<PermissionState>((set, get) => ({
  permissions: [],
  loading: false,
  error: null,
  
  loadPermissions: async () => {
    try {
      set({ loading: true, error: null })
      const { data } = await apiClient.get('/auth/permissions')
      set({ permissions: data.permissions, loading: false })
    } catch (error: any) {
      set({ 
        error: error.message, 
        loading: false,
        permissions: [] 
      })
    }
  },
  
  hasPermission: (code: string) => {
    return get().permissions.includes(code)
  },
  
  hasAnyPermission: (codes: string[]) => {
    const perms = get().permissions
    return codes.some(code => perms.includes(code))
  },
  
  clearPermissions: () => set({ permissions: [] })
}))
```

#### Step 2: Create Permission Hooks
```typescript
// src/hooks/usePermission.ts
import { usePermissionStore } from '@/store/permissionStore'

export const usePermission = (permissionCode: string): boolean => {
  const hasPermission = usePermissionStore(state => state.hasPermission)
  return hasPermission(permissionCode)
}

export const useAnyPermission = (permissionCodes: string[]): boolean => {
  const hasAnyPermission = usePermissionStore(state => state.hasAnyPermission)
  return hasAnyPermission(permissionCodes)
}

export const usePermissions = () => {
  return usePermissionStore(state => state.permissions)
}
```

#### Step 3: Update Auth Flow
```typescript
// src/store/index.ts - Update login to load permissions
login: async (username: string, password: string) => {
  try {
    set({ loading: true, error: null })
    const response = await apiClient.login(username, password)
    
    localStorage.setItem('access_token', response.access_token)
    localStorage.setItem('user', JSON.stringify(response.user))
    
    set({
      user: response.user,
      token: response.access_token,
      loading: false,
      initialized: true,
    })
    
    // Load permissions after successful login
    const permStore = usePermissionStore.getState()
    await permStore.loadPermissions()
    
  } catch (error: any) {
    const message = error.response?.data?.detail || 'Login failed'
    set({ error: message, loading: false })
    throw error
  }
}
```

---

### Phase 2: Update Sidebar (Day 2)

#### Enhanced Sidebar with Permissions
```tsx
// src/components/Sidebar.tsx
import { usePermission, useAnyPermission } from '@/hooks/usePermission'

interface MenuItem {
  icon: React.ReactNode
  label: string
  path?: string
  roles?: UserRole[]  // Keep for backward compatibility
  permissions?: string[]  // NEW: Permission codes
  submenu?: SubMenuItem[]
}

const menuItems: MenuItem[] = [
  { 
    icon: <BarChart3 />, 
    label: 'Dashboard', 
    path: '/dashboard', 
    permissions: ['dashboard.view_stats', 'dashboard.view_production']
  },
  { 
    icon: <ClipboardList />, 
    label: 'PPIC', 
    path: '/ppic', 
    permissions: ['ppic.view_mo', 'ppic.create_mo', 'ppic.schedule_production']
  },
  { 
    icon: <Factory />, 
    label: 'Production', 
    permissions: ['cutting.view_status', 'sewing.view_status', 'finishing.view_status'],
    submenu: [
      { 
        icon: <Scissors />, 
        label: 'Cutting', 
        path: '/cutting', 
        permissions: ['cutting.view_status', 'cutting.allocate_material']
      },
      { 
        icon: <Zap />, 
        label: 'Sewing', 
        path: '/sewing', 
        permissions: ['sewing.view_status', 'sewing.accept_transfer']
      },
      { 
        icon: <Sparkles />, 
        label: 'Finishing', 
        path: '/finishing', 
        permissions: ['finishing.view_status', 'finishing.accept_transfer']
      },
      { 
        icon: <Package />, 
        label: 'Packing', 
        path: '/packing', 
        permissions: ['packing.view_status', 'packing.pack_product']
      },
    ]
  },
  { 
    icon: <Users />, 
    label: 'Admin', 
    permissions: ['admin.manage_users', 'admin.view_system_info'],
    submenu: [
      { 
        icon: <Users />, 
        label: 'User Management', 
        path: '/admin/users', 
        permissions: ['admin.manage_users']
      },
      { 
        icon: <Shield />, 
        label: 'Audit Trail', 
        path: '/admin/audit-trail', 
        permissions: ['admin.view_audit_logs']
      },
    ]
  },
]

export const Sidebar: React.FC = () => {
  const { user } = useAuthStore()
  const { sidebarOpen } = useUIStore()
  const { permissions } = usePermissionStore()
  
  const visibleItems = menuItems.filter((item) => {
    if (!user) return false
    
    // Check permissions (new system)
    if (item.permissions && item.permissions.length > 0) {
      return useAnyPermission(item.permissions)
    }
    
    // Fallback to roles (backward compatible)
    if (item.roles) {
      return item.roles.includes(user.role)
    }
    
    return true
  })
  
  // ... rest of component
}
```

---

### Phase 3: Update Pages with Permission Checks (Days 3-4)

#### Example: Cutting Page
```tsx
// src/pages/CuttingPage.tsx
import { usePermission } from '@/hooks/usePermission'

export const CuttingPage = () => {
  const canAllocateMaterial = usePermission('cutting.allocate_material')
  const canCompleteCutting = usePermission('cutting.complete_operation')
  const canHandleVariance = usePermission('cutting.handle_variance')
  const canLineClearance = usePermission('cutting.line_clearance')
  
  return (
    <div>
      <h1>Cutting Department</h1>
      
      {canAllocateMaterial && (
        <Button onClick={handleAllocateMaterial}>
          Receive SPK
        </Button>
      )}
      
      {canCompleteCutting && (
        <Button onClick={handleCompleteCutting}>
          Complete Cutting
        </Button>
      )}
      
      {canHandleVariance && (
        <Button onClick={handleVariance}>
          Handle Shortage
        </Button>
      )}
      
      {canLineClearance && (
        <Card>
          <h3>Line Clearance</h3>
          {/* Line clearance UI */}
        </Card>
      )}
    </div>
  )
}
```

#### Example: Sewing Page
```tsx
// src/pages/SewingPage.tsx
export const SewingPage = () => {
  const canAcceptTransfer = usePermission('sewing.accept_transfer')
  const canPerformQC = usePermission('sewing.inline_qc')
  const canCreateTransfer = usePermission('sewing.create_transfer')
  
  return (
    <div>
      <h1>Sewing Department</h1>
      
      {canAcceptTransfer && (
        <Section title="Accept Transfer">
          {/* Transfer acceptance UI */}
        </Section>
      )}
      
      {canPerformQC && (
        <Section title="Quality Control">
          <Alert>⚠️ QC Inspector Only</Alert>
          {/* QC inspection UI */}
        </Section>
      )}
      
      {canCreateTransfer && (
        <Button onClick={handleTransferToFinishing}>
          Transfer to Finishing
        </Button>
      )}
    </div>
  )
}
```

---

### Phase 4: Error Handling Enhancement (Day 5)

#### API Client Update
```typescript
// src/api/client.ts
this.client.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Unauthorized - token expired or invalid
      localStorage.removeItem('access_token')
      localStorage.removeItem('user')
      window.location.href = '/login'
    } else if (error.response?.status === 403) {
      // Forbidden - insufficient permissions
      const message = error.response?.data?.detail || 'Insufficient permissions'
      
      // Show notification
      const { addNotification } = useUIStore.getState()
      addNotification({
        type: 'error',
        message: `Access Denied: ${message}`
      })
      
      // Optionally redirect to unauthorized page
      // window.location.href = '/unauthorized'
    }
    return Promise.reject(error)
  }
)
```

---

## Permission Code Reference

### Dashboard
- `dashboard.view_stats`
- `dashboard.view_production`
- `dashboard.view_alerts`
- `dashboard.view_trends`
- `dashboard.refresh_views`

### Cutting
- `cutting.allocate_material`
- `cutting.complete_operation`
- `cutting.handle_variance`
- `cutting.line_clearance`
- `cutting.create_transfer`
- `cutting.view_status`

### Sewing
- `sewing.accept_transfer`
- `sewing.validate_input`
- `sewing.inline_qc`
- `sewing.create_transfer`
- `sewing.view_status`
- `sewing.return_to_stage`

### Finishing
- `finishing.accept_transfer`
- `finishing.line_clearance`
- `finishing.perform_stuffing`
- `finishing.perform_closing`
- `finishing.metal_detector_qc`
- `finishing.final_qc`
- `finishing.convert_to_fg`
- `finishing.view_status`

### Packing
- `packing.sort_by_destination`
- `packing.pack_product`
- `packing.label_carton`
- `packing.complete_operation`
- `packing.view_status`

### PPIC
- `ppic.create_mo`
- `ppic.view_mo`
- `ppic.schedule_production`
- `ppic.approve_mo`

### Admin
- `admin.manage_users`
- `admin.view_system_info`

### Import/Export
- `import_export.import_data`
- `import_export.export_data`

---

## Testing Checklist

### Unit Tests
- [ ] Permission store loads correctly
- [ ] hasPermission returns correct boolean
- [ ] hasAnyPermission works with multiple codes
- [ ] Permissions cleared on logout

### Integration Tests
- [ ] Menu items show/hide based on permissions
- [ ] Buttons show/hide based on permissions
- [ ] 403 errors display notifications
- [ ] Unauthorized page loads for no access

### User Acceptance Tests
- [ ] Operator sees only their permissions
- [ ] SPV sees operator + SPV permissions
- [ ] Admin sees all menu items
- [ ] Permission changes reflect immediately

---

## Migration Timeline

| Day | Task | Status |
|-----|------|--------|
| 1 | Create permission store + hooks | Pending |
| 1 | Add `/auth/permissions` backend endpoint | Pending |
| 2 | Update Sidebar with permission checks | Pending |
| 2 | Update Navbar (if needed) | Pending |
| 3 | Migrate Cutting page | Pending |
| 3 | Migrate Sewing page | Pending |
| 4 | Migrate Finishing page | Pending |
| 4 | Migrate Packing page | Pending |
| 5 | Migrate PPIC page | Pending |
| 5 | Migrate Admin page | Pending |
| 5 | Update error handling | Pending |

---

## Backward Compatibility

The migration maintains backward compatibility:

1. **Role-based checks still work** - Existing `roles` property in menu items supported
2. **Permission checks are additive** - If `permissions` property exists, it overrides `roles`
3. **Gradual migration** - Can migrate page-by-page without breaking existing pages

---

## Success Criteria

- ✅ All menu items render based on permissions
- ✅ All action buttons controlled by permissions
- ✅ 403 errors handled gracefully
- ✅ No performance degradation
- ✅ Zero breaking changes to existing functionality
- ✅ Permission changes reflect in <100ms

---

**Status:** 📋 **PLAN READY - AWAITING IMPLEMENTATION**
