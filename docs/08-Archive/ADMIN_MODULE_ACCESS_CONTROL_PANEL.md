# 🔐 ADMIN MODULE ACCESS CONTROL PANEL

**Date**: January 21, 2026  
**Version**: 1.0  
**Author**: Daniel (Senior Developer)  
**Purpose**: SuperAdmin & Developer tool untuk mengelola akses module, pages, dan features

---

## 📋 TABLE OF CONTENTS

1. [Overview](#overview)
2. [Access Control Interface](#access-control-interface)
3. [Implementation Strategy](#implementation-strategy)
4. [Database Schema](#database-schema)
5. [Backend APIs](#backend-apis)
6. [Frontend Components](#frontend-components)
7. [Use Cases](#use-cases)

---

## 🎯 OVERVIEW

Sistem yang memungkinkan **SuperAdmin & Developers** untuk:

✅ **Menambah** modul/page baru dan mengontrol akses  
✅ **Mengubah** permission level per role tanpa code deployment  
✅ **Membatasi** akses ke modul specific tanpa perlu modify database  
✅ **Mengaktifkan/Menonaktifkan** fitur untuk testing atau gradual rollout  
✅ **Audit trail** semua perubahan akses untuk compliance  

---

## 🎨 ACCESS CONTROL INTERFACE

### **Main Dashboard: Module & Access Management**

```
┌─────────────────────────────────────────────────────────────────┐
│  ADMINISTRATION > ACCESS CONTROL & MODULE MANAGEMENT             │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  [+ ADD MODULE]  [IMPORT]  [EXPORT]  [SETTINGS]                 │
│                                                                   │
│  🔍 Search modules...  [Advanced Filters ▼]                      │
│                                                                   │
│  ACTIVE MODULES & THEIR ACCESS MATRIX                            │
│  ┌──────┬─────────────┬────────┬─────┬──────┬──────────┐        │
│  │ ID   │ Module Name │ Status │ Dev │ Test │ Actions  │        │
│  ├──────┼─────────────┼────────┼─────┼──────┼──────────┤        │
│  │ 1    │ Production  │ Active │ ✓   │ ✓    │ Edit ✎   │        │
│  │ 2    │ Warehouse   │ Active │ ✓   │ ✓    │ Edit ✎   │        │
│  │ 3    │ Quality     │ Active │ ✓   │ ✓    │ Edit ✎   │        │
│  │ 4    │ BigBtnMode  │ Active │ ✓   │ ✓    │ Edit ✎   │        │
│  │ 5    │ Reporting   │ Active │ ✓   │ ✓    │ Edit ✎   │        │
│  │ 6    │ Settings    │ Active │ ✓   │ ✓    │ Edit ✎   │        │
│  └──────┴─────────────┴────────┴─────┴──────┴──────────┘        │
│                                                                   │
│  Dev = Development environment, Test = Test environment          │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

### **Screen 1: Add New Module**

```
┌─────────────────────────────────────────────────────────────────┐
│  ADD NEW MODULE                                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  Module Information                                              │
│  ─────────────────────                                           │
│                                                                   │
│  Module Name * (Code)                                            │
│  [custom_module_________________]                                │
│  ℹ️  Use snake_case, no spaces                                  │
│                                                                   │
│  Display Label *                                                 │
│  [🔧 Custom Module ____________]                                │
│  ℹ️  Include emoji for visual identification                    │
│                                                                   │
│  Description                                                     │
│  [Multi-line field for module purpose/description]              │
│  [...]                                                           │
│                                                                   │
│  Sort Order (Menu Position)                                      │
│  [10__]  (1-100, lower = higher in menu)                         │
│                                                                   │
│  ─────────────────────────────────────────────────────────────  │
│  INITIAL ACCESS CONFIGURATION                                    │
│  ─────────────────────────────────────────────────────────────  │
│                                                                   │
│  Pages/Features in this Module                                   │
│  [+ Add Page]                                                    │
│  ┌─────────────────────────────────────────────────────┐        │
│  │ Page Name          │ Permission │ Required │ Actions│        │
│  ├─────────────────────────────────────────────────────┤        │
│  │ Page List          │ View       │ None     │ ✎ / ✕  │        │
│  │ Page Details       │ View       │ None     │ ✎ / ✕  │        │
│  │ Page Create        │ Edit       │ Manager  │ ✎ / ✕  │        │
│  │ Page Modify        │ Edit       │ Manager  │ ✎ / ✕  │        │
│  └─────────────────────────────────────────────────────┘        │
│                                                                   │
│  Which roles can access this module?                             │
│  ☑️ SuperAdmin (Full Access)                                    │
│  ☑️ Manager (Limited)                                           │
│  ☑️ Supervisor (Limited)                                        │
│  ☐ Operator                                                     │
│  ☐ Viewer                                                       │
│                                                                   │
│  Feature Flags (Optional - for gradual rollout)                  │
│  [+ Add Feature Flag]                                            │
│                                                                   │
│  ─────────────────────────────────────────────────────────────  │
│                                                                   │
│  [ Cancel ]                                 [ Create Module ]   │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

### **Screen 2: Edit Module & Configure Access**

```
┌──────────────────────────────────────────────────────────────────┐
│  EDIT MODULE: Production                                          │
├──────────────────────────────────────────────────────────────────┤
│                                                                    │
│  Module Details                                                   │
│  ────────────────────                                             │
│                                                                    │
│  Module Name (Fixed):  [production]                              │
│  Display Label:        [🏭 PRODUCTION ______________]            │
│  Description:          [Multi-stage manufacturing ...]           │
│  Status:               [Active ▼]                                │
│  Sort Order:           [2]                                       │
│  Last Modified:        2026-01-21 14:30 by Admin                │
│                                                                    │
│  ────────────────────────────────────────────────────────────── │
│  PAGES/FEATURES                                                   │
│  ────────────────────────────────────────────────────────────── │
│                                                                    │
│  [+ Add Page]  [Import Pages]  [Export Pages]                   │
│                                                                    │
│  Pages in this module:                                            │
│  ┌──────┬──────────────────┬────────────┬──────────┬────────┐   │
│  │ ID   │ Page Name        │ Path       │ Perms    │ Status │   │
│  ├──────┼──────────────────┼────────────┼──────────┼────────┤   │
│  │ 1    │ Work Orders      │ /prod/wo   │ V, E     │ Active │   │
│  │ 2    │ Cutting          │ /prod/cut  │ V, E     │ Active │   │
│  │ 3    │ Embroidery       │ /prod/emb  │ V, E     │ Active │   │
│  │ 4    │ Sewing           │ /prod/sew  │ V, E     │ Active │   │
│  │ 5    │ Finishing        │ /prod/fin  │ V, E     │ Active │   │
│  │ 6    │ Packing          │ /prod/pack │ V, E     │ Active │   │
│  │ 7    │ BigButton Mode   │ /prod/bb   │ E        │ Active │   │
│  │ 8    │ Reports          │ /prod/rep  │ V        │ Active │   │
│  └──────┴──────────────────┴────────────┴──────────┴────────┘   │
│                                                                    │
│  V = View, E = Edit, D = Delete, A = Approve                     │
│                                                                    │
│  ────────────────────────────────────────────────────────────── │
│  ROLE ACCESS CONTROL                                              │
│  ────────────────────────────────────────────────────────────── │
│                                                                    │
│  Configure which roles can access this module:                    │
│                                                                    │
│  ┌─────────────┬──────────────┬──────────┬─────────────┐        │
│  │ Role        │ Access Level │ Visible? │ Actions     │        │
│  ├─────────────┼──────────────┼──────────┼─────────────┤        │
│  │ SuperAdmin  │ Full         │ ✓        │ Edit / ✕    │        │
│  │ Manager     │ Full         │ ✓        │ Edit / ✕    │        │
│  │ Supervisor  │ Edit         │ ✓        │ Edit / ✕    │        │
│  │ Operator    │ Operational  │ ✓        │ Edit / ✕    │        │
│  │ Viewer      │ None         │ ✗        │ Edit / ✕    │        │
│  └─────────────┴──────────────┴──────────┴─────────────┘        │
│                                                                    │
│  [+ Add Custom Role]                                              │
│                                                                    │
│  ────────────────────────────────────────────────────────────── │
│  FEATURE TOGGLES                                                  │
│  ────────────────────────────────────────────────────────────── │
│                                                                    │
│  Enable/disable features for controlled rollout:                  │
│                                                                    │
│  ☑️ Real-Time Dashboard    (Enabled since Jan 20)               │
│     Effective: 2026-01-20 to ∞                                   │
│                                                                    │
│  ☑️ BigButton Mode         (Enabled since Jan 21)               │
│     Effective: 2026-01-21 to ∞                                   │
│                                                                    │
│  ☐ Advanced Analytics      (Disabled)                            │
│                                                                    │
│  ☐ Mobile App Support      (Scheduled: 2026-02-01 to 2026-02-28)│
│     Effective: 2026-02-01 to 2026-02-28                         │
│                                                                    │
│  [+ Add Feature Flag]                                             │
│                                                                    │
│  ────────────────────────────────────────────────────────────── │
│                                                                    │
│  [ Cancel ]                              [ Save Changes ]        │
│  [ Duplicate Module ]  [ Archive Module ]                        │
│                                                                    │
└──────────────────────────────────────────────────────────────────┘
```

---

### **Screen 3: Role-Based Permission Matrix**

```
┌──────────────────────────────────────────────────────────────────┐
│  ROLE ACCESS MATRIX - DRAG & DROP PERMISSION CONTROL             │
├──────────────────────────────────────────────────────────────────┤
│                                                                    │
│  Use mouse to drag permission level to assign or remove          │
│  Green = Full Access | Yellow = Limited | Red = No Access        │
│                                                                    │
│              │ SuperAdmin │ Manager │ Supervisor │ Operator      │
│  ────────────┼────────────┼─────────┼────────────┼──────────     │
│  Production  │ [🟢] Full  │ [🟢] FU │ [🟡] Edt │ [🟡] Ops        │
│              │ (Drag)     │ (Drag)  │ (Drag)    │ (Drag)        │
│              │            │         │           │               │
│  Warehouse   │ [🟢] Full  │ [🟡] Li │ [🟡] Li  │ [🔴] NO        │
│              │ (Drag)     │ (Drag)  │ (Drag)    │ (Drag)        │
│              │            │         │           │               │
│  Quality     │ [🟢] Full  │ [🟢] FU │ [🟢] FU  │ [🟡] Ops        │
│              │ (Drag)     │ (Drag)  │ (Drag)    │ (Drag)        │
│              │            │         │           │               │
│  Sales       │ [🟢] Full  │ [🟡] Li │ [🔴] NO  │ [🔴] NO        │
│              │ (Drag)     │ (Drag)  │ (Drag)    │ (Drag)        │
│              │            │         │           │               │
│  Admin       │ [🟢] Full  │ [🔴] NO │ [🔴] NO  │ [🔴] NO        │
│              │ (Drag)     │ (Drag)  │ (Drag)    │ (Drag)        │
│              │            │         │           │               │
│  Reporting   │ [🟢] Full  │ [🟢] FU │ [🟢] FU  │ [🟡] View      │
│              │ (Drag)     │ (Drag)  │ (Drag)    │ (Drag)        │
│              │            │         │           │               │
│  Settings    │ [🟢] Full  │ [🟢] FU │ [🟢] FU  │ [🟢] Personal  │
│              │ (Drag)     │ (Drag)  │ (Drag)    │ (Drag)        │
│              │            │         │           │               │
│  ────────────┴────────────┴─────────┴────────────┴──────────     │
│                                                                    │
│  LEGEND:                                                           │
│  🟢 Full = View + Edit + Delete + Approve                         │
│  🟡 Limited = View + Edit (no delete)                             │
│  🟡 Edit = View + Create/Modify (no delete/approve)              │
│  🟡 Ops = Operations only (pre-defined actions)                  │
│  🟡 View = Read-only access                                      │
│  🔴 NO = No access to module                                     │
│                                                                    │
│  QUICK ACTIONS:                                                   │
│  [Reset to Default]  [Copy from Role...]  [Apply Template]      │
│                                                                    │
│  [ Cancel ]                              [ Save Matrix ]        │
│                                                                    │
└──────────────────────────────────────────────────────────────────┘
```

---

### **Screen 4: Bulk Edit & Template Application**

```
┌──────────────────────────────────────────────────────────────────┐
│  BULK OPERATIONS: Apply Template or Batch Changes                │
├──────────────────────────────────────────────────────────────────┤
│                                                                    │
│  SCENARIO 1: Apply Access Template                               │
│  ─────────────────────────────────────────────────────────────   │
│                                                                    │
│  Template:  [Select Template ▼]                                  │
│    • Production Supervisor Template                              │
│    • Warehouse Manager Template                                  │
│    • New Hire Onboarding Template                                │
│    • Operator Basic Access Template                              │
│    • Finance Manager Template                                    │
│                                                                    │
│  Apply to roles:                                                  │
│  ☑️ Supervisor (6 users)                                        │
│  ☐ Manager (3 users)                                            │
│  ☐ Operator (24 users)                                          │
│                                                                    │
│  Review changes:                                                  │
│  Before: Supervisor had [Production, Warehouse, Quality]         │
│  After:  Supervisor will have [Production, Warehouse, Quality]   │
│          + Reporting + Settings                                  │
│                                                                    │
│  ─────────────────────────────────────────────────────────────   │
│  SCENARIO 2: Enable Feature for Specific Roles                   │
│  ─────────────────────────────────────────────────────────────   │
│                                                                    │
│  Feature: [BigButton Mode ▼]                                     │
│  Enable for:                                                      │
│  ☑️ Operator    (24 users) - From: 2026-01-21                   │
│  ☑️ Supervisor  (6 users)  - From: 2026-01-20                   │
│  ☑️ Manager     (3 users)  - From: 2026-01-15                   │
│  ☐ Viewer                                                        │
│                                                                    │
│  Rollback plan if issues:                                         │
│  [Disable for all at: 2026-01-21 16:00]                         │
│                                                                    │
│  ─────────────────────────────────────────────────────────────   │
│  SCENARIO 3: Create New Role & Clone Access                      │
│  ─────────────────────────────────────────────────────────────   │
│                                                                    │
│  New Role Name:  [Quality Supervisor __________________]         │
│  Clone Access from:  [Quality Manager ▼]                         │
│                                                                    │
│  Adjustments:                                                     │
│  ☑️ Remove Admin module access                                   │
│  ☑️ Remove Purchasing module access                              │
│  ☐ Keep all other permissions                                    │
│                                                                    │
│  ─────────────────────────────────────────────────────────────   │
│                                                                    │
│  [ Cancel ]                              [ Execute Changes ]     │
│                                                                    │
│  Change Summary:                                                  │
│  • Roles affected: 1-5                                            │
│  • Users impacted: 0-30                                           │
│  • Features toggled: 0-3                                          │
│  • Estimated time: < 5 minutes                                    │
│                                                                    │
└──────────────────────────────────────────────────────────────────┘
```

---

## 🔧 IMPLEMENTATION STRATEGY

### **Phase 1: Database & API** (2 hours)
- Create menu/module configuration tables
- Build REST APIs for CRUD operations
- Implement permission checking middleware

### **Phase 2: Frontend Components** (3 hours)
- Build module management interface
- Create role-access matrix UI
- Implement drag-drop permission editor

### **Phase 3: Audit & Security** (2 hours)
- Add audit logging for all changes
- Implement approval workflow
- Add rollback capability

### **Phase 4: Integration & Testing** (3 hours)
- Test end-to-end workflows
- Performance testing
- User acceptance testing

---

## 💾 DATABASE SCHEMA (New Tables)

```sql
-- Module management
CREATE TABLE modules (
  id BIGSERIAL PRIMARY KEY,
  code VARCHAR(100) UNIQUE NOT NULL,        -- 'production', 'warehouse'
  display_label VARCHAR(100) NOT NULL,      -- '🏭 Production'
  description TEXT,
  sort_order INT DEFAULT 1,
  is_active BOOLEAN DEFAULT TRUE,
  created_by BIGINT NOT NULL REFERENCES users(id),
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Pages within modules
CREATE TABLE module_pages (
  id BIGSERIAL PRIMARY KEY,
  module_id BIGINT NOT NULL REFERENCES modules(id),
  page_name VARCHAR(100) NOT NULL,
  page_path VARCHAR(255) NOT NULL,
  permission_level ENUM('view', 'edit', 'delete', 'approve') DEFAULT 'view',
  is_active BOOLEAN DEFAULT TRUE,
  sort_order INT DEFAULT 1,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  
  UNIQUE(module_id, page_name)
);

-- Role-module access mapping
CREATE TABLE role_module_access (
  id BIGSERIAL PRIMARY KEY,
  role_id BIGINT NOT NULL REFERENCES roles(id),
  module_id BIGINT NOT NULL REFERENCES modules(id),
  access_level ENUM('none', 'view', 'edit', 'delete', 'approve', 'full') DEFAULT 'none',
  is_visible BOOLEAN DEFAULT TRUE,
  effective_from TIMESTAMP,
  effective_to TIMESTAMP,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  
  UNIQUE(role_id, module_id)
);

-- Feature toggles
CREATE TABLE feature_toggles (
  id BIGSERIAL PRIMARY KEY,
  module_id BIGINT REFERENCES modules(id),
  feature_code VARCHAR(100) NOT NULL,
  feature_name VARCHAR(100) NOT NULL,
  is_enabled BOOLEAN DEFAULT FALSE,
  enabled_for_roles TEXT[],             -- array of role IDs
  effective_from TIMESTAMP,
  effective_to TIMESTAMP,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  
  UNIQUE(module_id, feature_code)
);

-- Audit trail for access control changes
CREATE TABLE access_control_audit (
  id BIGSERIAL PRIMARY KEY,
  admin_id BIGINT NOT NULL REFERENCES users(id),
  action_type VARCHAR(50),               -- 'added', 'modified', 'removed'
  entity_type VARCHAR(50),               -- 'module', 'role_access', 'feature'
  entity_id BIGINT,
  old_value JSONB,
  new_value JSONB,
  change_reason TEXT,
  status VARCHAR(20) DEFAULT 'completed', -- 'pending', 'completed', 'rolled_back'
  created_at TIMESTAMP DEFAULT NOW()
);

-- Access control templates
CREATE TABLE access_templates (
  id BIGSERIAL PRIMARY KEY,
  template_name VARCHAR(100) UNIQUE NOT NULL,
  template_description TEXT,
  module_access JSONB,                  -- { "module_id": "access_level" }
  created_by BIGINT NOT NULL REFERENCES users(id),
  is_default BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);
```

---

## 🔌 BACKEND APIs

```typescript
// GET /api/v1/admin/modules
// List all modules
Response: {
  modules: [
    {
      id: 1,
      code: "production",
      display_label: "🏭 Production",
      is_active: true,
      pages: 8,
      roles_with_access: 4
    }
  ]
}

// POST /api/v1/admin/modules
// Create new module (SuperAdmin only)
Body: {
  code: "custom_module",
  display_label: "🔧 Custom",
  description: "...",
  pages: [
    { name: "page1", path: "/custom/page1", permission_level: "view" }
  ]
}

// PUT /api/v1/admin/modules/{module_id}/role-access
// Configure role access for module
Body: {
  role_id: 2,
  access_level: "full",
  effective_from: "2026-01-21T00:00:00Z"
}

// GET /api/v1/admin/access-matrix
// Get full access matrix (all roles x modules)
Response: {
  matrix: {
    "role_1": { "module_1": "full", "module_2": "edit", ... },
    "role_2": { "module_1": "view", "module_2": "none", ... }
  }
}

// POST /api/v1/admin/feature-toggles
// Enable/disable feature
Body: {
  feature_code: "bigbutton_mode",
  is_enabled: true,
  enabled_for_roles: [3, 4, 5],
  effective_from: "2026-01-21T00:00:00Z"
}

// GET /api/v1/admin/access-audit
// Get audit trail
Query: ?limit=50&offset=0&entity_type=module
Response: {
  audit_logs: [ ... ]
}
```

---

## ✅ SUCCESS CRITERIA

- [ ] SuperAdmin can create/modify/delete modules without coding
- [ ] Permissions update immediately without app restart
- [ ] Role-access matrix updates in real-time
- [ ] Feature toggles work for gradual rollout
- [ ] All changes audited and reversible
- [ ] UI intuitive and performant
- [ ] API response time < 200ms
- [ ] 95%+ test coverage

---

**Status**: ✅ SPECIFICATION READY FOR IMPLEMENTATION  
**Estimated Development Time**: 8-10 hours  
**Deployment Impact**: Requires database migration + API deployment

