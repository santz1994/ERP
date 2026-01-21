# 🎨 COMPREHENSIVE NAVBAR & MENU STRUCTURE GUIDE

**Date**: January 21, 2026  
**Version**: 1.0  
**Author**: Daniel (Senior Developer)  
**Status**: 📋 DESIGN SPECIFICATION READY

---

## 📋 TABLE OF CONTENTS

1. [Navbar Architecture](#navbar-architecture)
2. [Menu Structure Hierarchy](#menu-structure-hierarchy)
3. [Access Control System](#access-control-system)
4. [Implementation Guide](#implementation-guide)
5. [Admin Menu Manager](#admin-menu-manager)
6. [Database Schema](#database-schema)
7. [Frontend Components](#frontend-components)
8. [Backend Endpoints](#backend-endpoints)

---

## 🏗️ NAVBAR ARCHITECTURE

### **Desktop Navbar Layout**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                               │
│  🏢 QUTY         [Dashboard]  [Production]  [Warehouse]  [Quality]  [...]   │
│                                                                    │          │
│                                                                    ▼          │
│                                                        [🔍 Search]  [👤 Menu] │
│                                                                    ▲          │
│                                                                    │          │
└─────────────────────────────────────────────────────────────────────────────┘
     │
     ├─ Logo/Brand
     ├─ Main Navigation (Dynamic based on user role)
     ├─ Search/Quick Actions
     └─ User Menu (Profile, Settings, Logout)
```

### **Mobile Navbar Layout (Responsive)**

```
┌────────────────────────────┐
│ ☰ QUTY  [🔍]  [👤]         │  <- Hamburger, Search, User
├────────────────────────────┤
│                             │
│ [Drawer Menu Opens Here]   │
│ - Dashboard                 │
│ - Production                │
│ - Warehouse                 │
│ - Quality                   │
│ - Settings ⚙️              │
│ - Logout                    │
│                             │
└────────────────────────────┘
```

---

## 🗂️ MENU STRUCTURE HIERARCHY

### **Complete Menu Tree (Role-Based Visibility)**

```
MAIN NAVIGATION
│
├─ 📊 Dashboard
│  ├─ View: Production Status (View)
│  ├─ View: KPI Metrics (View)
│  ├─ View: Real-Time Stats (View)
│  └─ Edit: Configure Dashboard (Edit - Admin Only)
│
├─ 🏭 PRODUCTION (Production Managers + Supervisors + Operators)
│  ├─ 📋 Work Orders
│  │  ├─ View: List All WO (View)
│  │  ├─ View: WO Details (View)
│  │  ├─ Edit: Create WO (Edit - Manager Only)
│  │  └─ Edit: Modify WO (Edit - Supervisor+)
│  │
│  ├─ ✂️ Cutting
│  │  ├─ View: Cutting Queue (View)
│  │  ├─ Edit: Start Cutting (Edit - Operator)
│  │  ├─ Edit: Record Output (Edit - Operator)
│  │  └─ Edit: Transfer to Sewing (Edit - Operator)
│  │
│  ├─ 🧵 Embroidery
│  │  ├─ View: Embroidery Jobs (View)
│  │  ├─ Edit: Record Embroidery (Edit - Operator)
│  │  └─ Edit: Transfer Output (Edit - Operator)
│  │
│  ├─ 🪡 Sewing
│  │  ├─ View: Sewing Queue (View)
│  │  ├─ Edit: Process Assembly (Edit - Operator)
│  │  ├─ Edit: Process Labeling (Edit - Operator)
│  │  ├─ Edit: Process Stik (Edit - Operator)
│  │  └─ Edit: QC Inspection (Edit - QC)
│  │
│  ├─ 🎁 Finishing
│  │  ├─ View: Finishing Queue (View)
│  │  ├─ Edit: Record Stuffing (Edit - Operator)
│  │  ├─ Edit: Record Closing (Edit - Operator)
│  │  ├─ Edit: QC Pass (Edit - QC)
│  │  └─ Edit: Transfer to Packing (Edit - Supervisor)
│  │
│  ├─ 📦 Packing
│  │  ├─ View: Packing Jobs (View)
│  │  ├─ Edit: Create Carton (Edit - Operator)
│  │  ├─ Edit: Sort/Pack (Edit - Operator)
│  │  └─ Edit: Transfer to FG (Edit - Supervisor)
│  │
│  └─ 📊 Production Reports
│     ├─ View: Daily Production (View)
│     ├─ View: Line Efficiency (View)
│     └─ View: Downtime Log (View)
│
├─ 🏪 WAREHOUSE (Warehouse Managers + Stock Keepers)
│  ├─ 📍 Stock Management
│  │  ├─ View: Stock Levels (View)
│  │  ├─ View: Stock Movement (View)
│  │  ├─ Edit: Receive Material (Edit - Stock Keeper)
│  │  ├─ Edit: Issue Material (Edit - Stock Keeper)
│  │  ├─ Edit: Stock Adjustment (Edit - Manager)
│  │  └─ Edit: Transfer to Production (Edit - Operator)
│  │
│  ├─ 📦 Finished Goods
│  │  ├─ View: FG Stock (View)
│  │  ├─ View: FG Movement (View)
│  │  ├─ Edit: Receive from Production (Edit - Operator)
│  │  ├─ Edit: Quality Check (Edit - QC)
│  │  └─ Edit: Prepare Shipment (Edit - Supervisor)
│  │
│  └─ 📋 Warehouse Reports
│     ├─ View: Stock Report (View)
│     ├─ View: Movement Report (View)
│     └─ View: FIFO Aging Report (View)
│
├─ 🔬 QUALITY (QC Inspectors + Quality Managers)
│  ├─ 📊 Quality Tests
│  │  ├─ View: QC Lab Tests (View)
│  │  ├─ View: Test History (View)
│  │  ├─ Edit: Record Drop Test (Edit - Technician)
│  │  ├─ Edit: Record Stability Test (Edit - Technician)
│  │  ├─ Edit: Record Metal Detector (Edit - Technician)
│  │  └─ Edit: Record Seam Test (Edit - Technician)
│  │
│  ├─ 👁️ Inspections
│  │  ├─ View: Inspection Queue (View)
│  │  ├─ View: Defect Log (View)
│  │  ├─ Edit: Inline Inspection (Edit - Inspector)
│  │  ├─ Edit: Final Inspection (Edit - Inspector)
│  │  └─ Edit: Reject/Rework (Edit - Inspector)
│  │
│  └─ 📈 Quality Reports
│     ├─ View: Quality Metrics (View)
│     ├─ View: Defect Analysis (View)
│     └─ View: Trend Report (View)
│
├─ 💼 SALES & ORDERS (Sales Team + Order Managers)
│  ├─ 📋 Sales Orders
│  │  ├─ View: All Orders (View)
│  │  ├─ View: Order Details (View)
│  │  ├─ Edit: Create Order (Edit - Sales Manager)
│  │  ├─ Edit: Modify Order (Edit - Sales Manager)
│  │  └─ Edit: Close Order (Edit - Supervisor)
│  │
│  ├─ 📅 Forecasting
│  │  ├─ View: Demand Forecast (View)
│  │  ├─ Edit: Update Forecast (Edit - Manager)
│  │  └─ View: Historical Trends (View)
│  │
│  └─ 📊 Sales Reports
│     ├─ View: Sales Summary (View)
│     ├─ View: Order Performance (View)
│     └─ View: Customer Report (View)
│
├─ 🛒 PURCHASING (Purchasing Team + Procurement Managers)
│  ├─ 🛍️ Purchase Orders
│  │  ├─ View: All PO (View)
│  │  ├─ View: PO Details (View)
│  │  ├─ Edit: Create PO (Edit - Buyer)
│  │  ├─ Edit: Modify PO (Edit - Buyer)
│  │  ├─ Edit: Approve PO (Edit - Manager)
│  │  └─ Edit: Receive Goods (Edit - Stock Keeper)
│  │
│  ├─ 👥 Suppliers
│  │  ├─ View: Supplier List (View)
│  │  ├─ View: Supplier Performance (View)
│  │  ├─ Edit: Create Supplier (Edit - Manager)
│  │  ├─ Edit: Update Supplier (Edit - Manager)
│  │  └─ Edit: Change Status (Edit - Manager)
│  │
│  └─ 📊 Purchasing Reports
│     ├─ View: PO Status (View)
│     ├─ View: Delivery Performance (View)
│     └─ View: Spend Analysis (View)
│
├─ 📊 REPORTING (Report Viewers + Analysts + Managers)
│  ├─ 📈 Standard Reports
│  │  ├─ View: Production Report (View)
│  │  ├─ View: Quality Report (View)
│  │  ├─ View: Sales Report (View)
│  │  ├─ View: Financial Report (View)
│  │  └─ View: Compliance Report (View)
│  │
│  ├─ 🛠️ Custom Reports
│  │  ├─ View: My Reports (View)
│  │  ├─ Edit: Create Report (Edit - Analyst)
│  │  ├─ Edit: Modify Report (Edit - Owner)
│  │  └─ Edit: Delete Report (Edit - Owner)
│  │
│  ├─ 📥 Import/Export
│  │  ├─ View: Data Export (View)
│  │  ├─ Edit: Export Data (Edit - Admin)
│  │  ├─ Edit: Import Data (Edit - Admin)
│  │  └─ View: Import History (View)
│  │
│  └─ 📋 Data Dictionary
│     └─ View: Field Definitions (View)
│
├─ 👥 USER MANAGEMENT (SuperAdmin + HR Managers)
│  ├─ 🧑‍💼 Users
│  │  ├─ View: User List (View - Admin)
│  │  ├─ View: User Details (View - Admin)
│  │  ├─ Edit: Create User (Edit - HR Manager)
│  │  ├─ Edit: Modify User (Edit - HR Manager)
│  │  ├─ Edit: Assign Role (Edit - SuperAdmin)
│  │  └─ Edit: Deactivate User (Edit - SuperAdmin)
│  │
│  ├─ 👤 Roles & Permissions
│  │  ├─ View: Role List (View - Admin)
│  │  ├─ View: Permission Matrix (View - Admin)
│  │  ├─ Edit: Create Role (Edit - SuperAdmin)
│  │  ├─ Edit: Modify Role (Edit - SuperAdmin)
│  │  └─ Edit: Assign Permissions (Edit - SuperAdmin)
│  │
│  ├─ 🔓 Access Control
│  │  ├─ View: Module Access (View - Admin)
│  │  ├─ Edit: Grant Module Access (Edit - SuperAdmin)
│  │  ├─ Edit: Revoke Module Access (Edit - SuperAdmin)
│  │  └─ View: Access Audit Trail (View - Admin)
│  │
│  └─ 📋 HR Settings
│     ├─ View: Employee Directory (View)
│     ├─ Edit: Update Employee Info (Edit - HR)
│     └─ View: Department Structure (View)
│
├─ ⚙️ ADMINISTRATION (SuperAdmin Only)
│  ├─ 🔐 Settings & Configuration
│  │  ├─ 🔐 Security Settings
│  │  ├─ 📧 Email Configuration
│  │  ├─ 🌍 System Localization
│  │  ├─ 📄 Document Templates
│  │  ├─ 💾 Database Backup
│  │  ├─ 📊 System Monitoring
│  │  └─ 🔄 System Maintenance
│  │
│  ├─ 📋 Module Configuration
│  │  ├─ 🎛️ Feature Toggles (Enable/Disable Features)
│  │  ├─ 🔗 Module Dependencies
│  │  ├─ 📍 Route Configuration
│  │  └─ ⏱️ Processing Rules
│  │
│  ├─ 🔍 Audit & Compliance
│  │  ├─ View: Audit Trail (View)
│  │  ├─ View: System Logs (View)
│  │  ├─ View: User Activity (View)
│  │  └─ View: Compliance Report (View)
│  │
│  └─ 📜 System Information
│     ├─ View: System Status (View)
│     ├─ View: Version Info (View)
│     └─ View: API Documentation (View)
│
└─ ⚙️ SETTINGS (All Users)
   ├─ 👤 My Profile
   │  ├─ View: Profile Info (View)
   │  ├─ Edit: Update Profile (Edit - Self)
   │  ├─ Edit: Change Password (Edit - Self)
   │  └─ View: Login History (View - Self)
   │
   ├─ 🌍 Preferences
   │  ├─ Edit: Language & Timezone (Edit - Self)
   │  ├─ Edit: Display Preferences (Edit - Self)
   │  ├─ Edit: Notification Settings (Edit - Self)
   │  └─ Edit: Theme Selection (Edit - Self)
   │
   └─ 🚪 Logout
      └─ Action: Sign Out (All Users)
```

---

## 🔐 ACCESS CONTROL SYSTEM

### **Role-Based Access Control (RBAC) Matrix**

| Menu Item | SuperAdmin | Manager | Supervisor | Operator | Viewer | HR Manager |
|-----------|:----------:|:-------:|:----------:|:--------:|:------:|:----------:|
| Dashboard | ✅ Full | ✅ Full | ✅ View | ✅ View | ✅ View | ✅ View |
| Production | ✅ Full | ✅ Full | ✅ Full | ✅ Ops | ❌ - | ❌ - |
| Cutting | ✅ Full | ✅ Full | ✅ Full | ✅ Edit | ❌ - | ❌ - |
| Embroidery | ✅ Full | ✅ Full | ✅ Full | ✅ Edit | ❌ - | ❌ - |
| Sewing | ✅ Full | ✅ Full | ✅ Full | ✅ Edit | ❌ - | ❌ - |
| Finishing | ✅ Full | ✅ Full | ✅ Full | ✅ Edit | ❌ - | ❌ - |
| Packing | ✅ Full | ✅ Full | ✅ Full | ✅ Edit | ❌ - | ❌ - |
| Warehouse | ✅ Full | ✅ Full | ✅ View | ✅ Edit | ❌ - | ❌ - |
| Quality | ✅ Full | ✅ Full | ✅ Full | ✅ Edit | ❌ - | ❌ - |
| Sales | ✅ Full | ✅ Full | ✅ View | ❌ - | ❌ - | ❌ - |
| Purchasing | ✅ Full | ✅ Full | ✅ View | ❌ - | ❌ - | ❌ - |
| Reporting | ✅ Full | ✅ Full | ✅ Full | ✅ View | ✅ View | ✅ View |
| User Mgmt | ✅ Full | ❌ - | ❌ - | ❌ - | ❌ - | ✅ Full |
| Administration | ✅ Full | ❌ - | ❌ - | ❌ - | ❌ - | ❌ - |
| Settings | ✅ Full | ✅ Full | ✅ Full | ✅ Full | ✅ Full | ✅ Full |

**Legend**: ✅ Full = View + Edit, ✅ Full = All permissions, ✅ View = Read-only, ✅ Edit = Create/Modify/Delete, ✅ Ops = Operations only, ❌ - = No access

---

### **Permission Levels**

```
┌─────────────────────────────────────────┐
│         PERMISSION HIERARCHY             │
├─────────────────────────────────────────┤
│                                          │
│  ┌─ SUPER ADMIN (Level 0)              │
│  │  └─ Full access to all modules       │
│  │     └─ Can create/modify/delete      │
│  │        all menu items & roles        │
│  │                                       │
│  ├─ MANAGER (Level 1)                  │
│  │  └─ Full access to assigned modules │
│  │     └─ Can approve/reject operations│
│  │        └─ Cannot modify menu/roles   │
│  │                                       │
│  ├─ SUPERVISOR (Level 2)               │
│  │  └─ View + Limited Edit permissions │
│  │     └─ Can view all, edit operational│
│  │        └─ Cannot create new WO       │
│  │                                       │
│  ├─ OPERATOR (Level 3)                 │
│  │  └─ Operational only                │
│  │     └─ Can execute assigned tasks   │
│  │        └─ Cannot approve/modify      │
│  │                                       │
│  └─ VIEWER (Level 4)                   │
│     └─ Read-only access                │
│        └─ Can view reports/data        │
│           └─ Cannot edit anything      │
│                                          │
└─────────────────────────────────────────┘
```

---

## 🛠️ IMPLEMENTATION GUIDE

### **Frontend: React Component Structure**

```typescript
// src/components/Navbar/Navbar.tsx
import React from 'react';
import { usePermission } from '@/hooks/usePermission';
import { useMenuConfig } from '@/hooks/useMenuConfig';
import { Sidebar } from './Sidebar';
import { TopBar } from './TopBar';

export const Navbar: React.FC = () => {
  const { hasPermission } = usePermission();
  const { menuItems } = useMenuConfig();

  // Filter menu items based on user permissions
  const visibleMenus = menuItems.filter(item => 
    hasPermission(item.requiredModule, item.requiredPermission)
  );

  return (
    <nav className="navbar">
      <TopBar menuItems={visibleMenus} />
      <Sidebar menuItems={visibleMenus} />
    </nav>
  );
};

// src/components/Navbar/MenuItem.tsx
interface MenuItemProps {
  id: string;
  label: string;
  icon?: React.ReactNode;
  path?: string;
  submenu?: MenuItemProps[];
  requiredModule: string;
  requiredPermission: 'view' | 'edit' | 'delete' | 'approve';
  badge?: number;
  onClick?: () => void;
}

// src/hooks/useMenuConfig.ts
export const useMenuConfig = () => {
  const [menuItems, setMenuItems] = React.useState<MenuItemProps[]>([]);
  const [loading, setLoading] = React.useState(true);

  React.useEffect(() => {
    // Fetch menu configuration from API
    fetchMenuConfiguration();
  }, []);

  const fetchMenuConfiguration = async () => {
    try {
      const response = await api.get('/api/v1/admin/menu-config');
      setMenuItems(response.data.menu_items);
    } catch (error) {
      console.error('Failed to load menu configuration', error);
    } finally {
      setLoading(false);
    }
  };

  return { menuItems, loading, setMenuItems };
};
```

---

## ⚙️ ADMIN MENU MANAGER

### **SuperAdmin Interface for Managing Menu Access**

```
┌─────────────────────────────────────────────────────────────┐
│  ADMINISTRATION > MODULE & MENU MANAGEMENT                   │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  [ADD NEW MODULE]  [IMPORT CONFIG]  [EXPORT CONFIG]         │
│                                                               │
│  MODULE LIST                                                 │
│  ┌─────┬──────────────┬────────┬─────────┬─────────────┐   │
│  │ ID  │ Module Name  │ Status │ Roles   │ Actions     │   │
│  ├─────┼──────────────┼────────┼─────────┼─────────────┤   │
│  │ 1   │ Production   │ Active │ 4 roles │ Edit ✎      │   │
│  │ 2   │ Warehouse    │ Active │ 3 roles │ Edit ✎      │   │
│  │ 3   │ Quality      │ Active │ 2 roles │ Edit ✎      │   │
│  │ 4   │ Reporting    │ Active │ 5 roles │ Edit ✎      │   │
│  │ 5   │ Admin        │ Active │ 1 role  │ Edit ✎      │   │
│  └─────┴──────────────┴────────┴─────────┴─────────────┘   │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### **Edit Module Screen**

```
┌─────────────────────────────────────────────────────────────┐
│  EDIT MODULE: Production                                     │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  Module Name *:        [Production ________________]         │
│  Display Label *:      [🏭 PRODUCTION _________]            │
│  Description:          [Multi-stage manufacturing ...     ] │
│  Status:               [Active ▼]                           │
│  Menu Sort Order:      [2 ____]                             │
│                                                               │
│  MENU ITEMS (Submenus)                                       │
│  ┌──────────────────────────────────────────────────┐      │
│  │ Item         │ Permission │ Visible │ Actions    │      │
│  ├──────────────────────────────────────────────────┤      │
│  │ Work Orders  │ View/Edit  │ ✓       │ Edit / ✕   │      │
│  │ Cutting      │ View/Edit  │ ✓       │ Edit / ✕   │      │
│  │ Embroidery   │ View/Edit  │ ✓       │ Edit / ✕   │      │
│  │ Sewing       │ View/Edit  │ ✓       │ Edit / ✕   │      │
│  │ Finishing    │ View/Edit  │ ✓       │ Edit / ✕   │      │
│  │ Packing      │ View/Edit  │ ✓       │ Edit / ✕   │      │
│  └──────────────────────────────────────────────────┘      │
│                                                               │
│  [+ ADD MENU ITEM]                                          │
│                                                               │
│  ROLE ACCESS                                                │
│  ┌──────────────────────────────────────────────────┐      │
│  │ Role           │ Permission │ Visible │ Actions│      │
│  ├──────────────────────────────────────────────────┤      │
│  │ SuperAdmin     │ Full       │ ✓       │ Edit / ✕ │      │
│  │ Manager        │ Full       │ ✓       │ Edit / ✕ │      │
│  │ Supervisor     │ Full       │ ✓       │ Edit / ✕ │      │
│  │ Operator       │ Operational│ ✓       │ Edit / ✕ │      │
│  │ Viewer         │ None       │ ✗       │ Edit / ✕ │      │
│  └──────────────────────────────────────────────────┘      │
│                                                               │
│  [ Cancel ]                    [ Save Changes ]             │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### **Quick Access Control Grid**

```
┌──────────────────────────────────────────────────────────────┐
│  QUICK ACCESS CONTROL: Drag & Drop Permission Matrix        │
├──────────────────────────────────────────────────────────────┤
│                                                                │
│  MODULES vs ROLES (Drag to assign/remove)                    │
│                                                                │
│          │ SuperAdmin │ Manager │ Supervisor │ Operator     │
│  ────────┼────────────┼─────────┼────────────┼──────────    │
│  Prod.   │ ████████░░ │ ████████│ ████░░░░░░│ ███░░░░░░    │
│  ────────┼────────────┼─────────┼────────────┼──────────    │
│  Ware.   │ ████████░░ │ ████░░░░│ ██░░░░░░░░│ ███░░░░░░    │
│  ────────┼────────────┼─────────┼────────────┼──────────    │
│  Quality │ ████████░░ │ ████████│ ████░░░░░░│ ███░░░░░░    │
│  ────────┼────────────┼─────────┼────────────┼──────────    │
│  Sales   │ ████████░░ │ ████░░░░│ ░░░░░░░░░░│ ░░░░░░░░░░   │
│  ────────┼────────────┼─────────┼────────────┼──────────    │
│  Admin   │ ████████░░ │ ░░░░░░░░│ ░░░░░░░░░░│ ░░░░░░░░░░   │
│          │ FULL ACCESS│ LIMITED │ OPERATIONS│ NO ACCESS     │
│                                                                │
│  ████ = Permission Granted  ░░░░ = Permission Denied         │
│                                                                │
└──────────────────────────────────────────────────────────────┘
```

---

## 💾 DATABASE SCHEMA

### **Menu Configuration Tables**

```sql
-- Main modules table
CREATE TABLE modules (
  id BIGSERIAL PRIMARY KEY,
  name VARCHAR(100) UNIQUE NOT NULL,        -- "production", "warehouse"
  display_label VARCHAR(100) NOT NULL,      -- "🏭 Production"
  description TEXT,
  icon_class VARCHAR(50),                   -- "fa-factory", "fa-warehouse"
  sort_order INT DEFAULT 1,
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Menu items within modules
CREATE TABLE menu_items (
  id BIGSERIAL PRIMARY KEY,
  module_id BIGINT NOT NULL REFERENCES modules(id),
  parent_item_id BIGINT REFERENCES menu_items(id),  -- For submenus
  name VARCHAR(100) NOT NULL,               -- "work_orders", "cutting"
  display_label VARCHAR(100) NOT NULL,      -- "Work Orders", "✂️ Cutting"
  description TEXT,
  path VARCHAR(255),                        -- "/production/work-orders"
  icon_class VARCHAR(50),                   -- "fa-list"
  sort_order INT DEFAULT 1,
  permission_type ENUM('view', 'edit', 'delete', 'approve') DEFAULT 'view',
  is_active BOOLEAN DEFAULT TRUE,
  requires_module VARCHAR(100),             -- Referenced module
  requires_permission VARCHAR(50),
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  
  UNIQUE(module_id, name)
);

-- Role-specific menu access
CREATE TABLE role_menu_access (
  id BIGSERIAL PRIMARY KEY,
  role_id BIGINT NOT NULL REFERENCES roles(id),
  menu_item_id BIGINT NOT NULL REFERENCES menu_items(id),
  permission_level ENUM('none', 'view', 'edit', 'delete', 'approve', 'full') DEFAULT 'none',
  is_visible BOOLEAN DEFAULT TRUE,          -- Hide from UI but still accessible?
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  
  UNIQUE(role_id, menu_item_id)
);

-- Feature flags for modules
CREATE TABLE feature_toggles (
  id BIGSERIAL PRIMARY KEY,
  module_id BIGINT NOT NULL REFERENCES modules(id),
  feature_name VARCHAR(100) NOT NULL,       -- "big_button_mode", "real_time_updates"
  is_enabled BOOLEAN DEFAULT FALSE,
  effective_from TIMESTAMP,
  effective_to TIMESTAMP,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  
  UNIQUE(module_id, feature_name)
);

-- Menu configuration audit trail
CREATE TABLE menu_config_audit (
  id BIGSERIAL PRIMARY KEY,
  admin_user_id BIGINT NOT NULL REFERENCES users(id),
  action VARCHAR(50),                       -- "created", "modified", "deleted"
  entity_type VARCHAR(50),                  -- "module", "menu_item", "role_access"
  entity_id BIGINT,
  old_value JSONB,                          -- Before change
  new_value JSONB,                          -- After change
  change_reason TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);
```

---

## 🎯 BACKEND ENDPOINTS

### **Menu Configuration APIs**

```typescript
// GET /api/v1/admin/menu-config
// Get all menu items for current user based on permissions
Response: {
  menu_items: [
    {
      id: 1,
      module_id: 1,
      name: "dashboard",
      display_label: "📊 Dashboard",
      path: "/dashboard",
      permission_level: "view",
      submenu: [ ... ]
    },
    ...
  ]
}

// GET /api/v1/admin/modules
// List all modules (Admin only)
Response: {
  modules: [ ... ]
}

// POST /api/v1/admin/modules
// Create new module (SuperAdmin only)
Body: {
  name: "custom_module",
  display_label: "🔧 Custom",
  description: "Custom module for XYZ",
  sort_order: 10
}

// PUT /api/v1/admin/modules/{module_id}
// Update module configuration (SuperAdmin only)
Body: {
  display_label: "🔧 Custom Updated",
  sort_order: 11,
  is_active: true
}

// DELETE /api/v1/admin/modules/{module_id}
// Delete module (SuperAdmin only)
Response: { message: "Module deleted", affected_items: 5 }

// GET /api/v1/admin/modules/{module_id}/menu-items
// Get menu items within module

// POST /api/v1/admin/modules/{module_id}/menu-items
// Add menu item (SuperAdmin only)

// PUT /api/v1/admin/menu-items/{item_id}
// Update menu item configuration

// DELETE /api/v1/admin/menu-items/{item_id}
// Delete menu item

// PUT /api/v1/admin/roles/{role_id}/menu-access
// Configure which menus are visible for role
Body: {
  menu_item_id: 5,
  permission_level: "edit",
  is_visible: true
}

// GET /api/v1/admin/feature-toggles
// Get all feature toggles

// PUT /api/v1/admin/feature-toggles/{feature_id}
// Enable/disable feature

// GET /api/v1/admin/menu-config/audit
// Get audit trail of menu configuration changes
```

---

## ✅ SUCCESS CRITERIA

- [ ] Navbar responsive on desktop & mobile
- [ ] Menu items dynamically filtered by role
- [ ] SuperAdmin can add/remove/modify modules
- [ ] SuperAdmin can configure role-menu access
- [ ] Feature toggles working for modules
- [ ] All menu changes audited
- [ ] Performance: Menu load < 200ms
- [ ] Tests: 80%+ coverage
- [ ] Zero security bypasses
- [ ] User feedback: Intuitive navigation

---

**Document Status**: ✅ READY FOR IMPLEMENTATION  
**Last Updated**: January 21, 2026

