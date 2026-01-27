import React, { useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import {
  BarChart3,
  Scissors,
  Palette,
  Zap,
  Sparkles,
  Package,
  Beaker,
  Warehouse,
  ShoppingCart,
  TruckIcon,
  Users,
  Factory,
  ChevronDown,
  ChevronRight,
  FileText,
  ClipboardList,
  Shield,
  Settings,
  Lock,
  Globe,
  Bell,
  Palette as PaletteIcon,
  Mail,
  FileEdit,
  Building,
  Database,
  Calendar,
} from 'lucide-react'
import { useAuthStore, useUIStore, usePermissionStore } from '@/store'
import { UserRole } from '@/types'

interface SubMenuItem {
  icon: React.ReactNode
  label: string
  path: string
  roles?: UserRole[]  // Optional: backward compatible
  permissions?: string[]  // NEW: permission-based access
}

interface MenuItem {
  icon: React.ReactNode
  label: string
  path?: string
  roles?: UserRole[]  // Optional: backward compatible
  permissions?: string[]  // NEW: permission-based access
  submenu?: SubMenuItem[]
}

/**
 * Menu items with PBAC (Permission-Based Access Control)
 * Phase 16 Week 4
 * 
 * Backward compatible:
 * - If `permissions` is defined, use permission-based check
 * - If only `roles` is defined, use role-based check (old behavior)
 */
const menuItems: MenuItem[] = [
  { 
    icon: <BarChart3 />, 
    label: 'Dashboard', 
    path: '/dashboard', 
    permissions: ['dashboard.view_stats', 'dashboard.view_production', 'dashboard.view_alerts']
  },
  { 
    icon: <ShoppingCart />, 
    label: 'Purchasing', 
    path: '/purchasing', 
    roles: [UserRole.PPIC_MANAGER, UserRole.PPIC_ADMIN, UserRole.PURCHASING, UserRole.ADMIN] 
  },
  { 
    icon: <ClipboardList />, 
    label: 'PPIC', 
    path: '/ppic', 
    permissions: ['ppic.view_mo', 'ppic.create_mo', 'ppic.schedule_production', 'ppic.approve_mo']
  },
  { 
    icon: <Factory />, 
    label: 'Production', 
    permissions: ['cutting.view_status', 'sewing.view_status', 'finishing.view_status', 'packing.view_status'],
    submenu: [
      {
        icon: <Calendar />,
        label: 'Daily Input',
        path: '/daily-production',
        permissions: ['production.input_daily', 'production.view_spk']
      },
      { 
        icon: <Scissors />, 
        label: 'Cutting', 
        path: '/cutting', 
        permissions: ['cutting.view_status', 'cutting.allocate_material', 'cutting.complete_operation']
      },
      { 
        icon: <Palette />, 
        label: 'Embroidery', 
        path: '/embroidery', 
        roles: [UserRole.OPERATOR_EMBRO, UserRole.SPV_CUTTING, UserRole.ADMIN] 
      },
      { 
        icon: <Zap />, 
        label: 'Sewing', 
        path: '/sewing', 
        permissions: ['sewing.view_status', 'sewing.accept_transfer', 'sewing.inline_qc', 'sewing.create_transfer']
      },
      { 
        icon: <Sparkles />, 
        label: 'Finishing', 
        path: '/finishing', 
        permissions: ['finishing.view_status', 'finishing.accept_transfer', 'finishing.final_qc', 'finishing.convert_to_fg']
      },
      { 
        icon: <Package />, 
        label: 'Packing', 
        path: '/packing', 
        permissions: ['packing.view_status', 'packing.pack_product', 'packing.label_carton', 'packing.complete_operation']
      },
    ]
  },
  { 
    icon: <Warehouse />, 
    label: 'Warehouse', 
    path: '/warehouse', 
    roles: [UserRole.WAREHOUSE_ADMIN, UserRole.WAREHOUSE_OP, UserRole.ADMIN] 
  },
  { 
    icon: <TruckIcon />, 
    label: 'Finish Goods', 
    path: '/finishgoods', 
    roles: [UserRole.WAREHOUSE_ADMIN, UserRole.WAREHOUSE_OP, UserRole.ADMIN] 
  },
  { 
    icon: <Beaker />, 
    label: 'QC', 
    path: '/quality', 
    roles: [UserRole.QC_INSPECTOR, UserRole.QC_LAB, UserRole.ADMIN] 
  },
  { 
    icon: <FileText />, 
    label: 'Reports', 
    path: '/reports', 
    roles: [UserRole.PPIC_MANAGER, UserRole.PPIC_ADMIN, UserRole.ADMIN] 
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
        label: 'Permissions', 
        path: '/admin/permissions', 
        permissions: ['admin.view_system_info']
      },
      { 
        icon: <Shield />, 
        label: 'Audit Trail', 
        path: '/admin/audit-trail', 
        roles: [UserRole.DEVELOPER, UserRole.SUPERADMIN, UserRole.MANAGER] 
      },
      { 
        icon: <FileText />, 
        label: 'Import/Export', 
        path: '/admin/import-export', 
        permissions: ['import_export.import_data', 'import_export.export_data']
      },
    ]
  },
  { 
    icon: <Settings />, 
    label: 'Settings', 
    submenu: [
      { 
        icon: <Lock />, 
        label: 'Change Password', 
        path: '/settings/password',
        // All users can change their password
      },
      { 
        icon: <Globe />, 
        label: 'Language & Timezone', 
        path: '/settings/language',
        // All users can set preferences
      },
      { 
        icon: <Bell />, 
        label: 'Notifications', 
        path: '/settings/notifications',
        // All users can manage notifications
      },
      { 
        icon: <PaletteIcon />, 
        label: 'Display Preferences', 
        path: '/settings/display',
        // All users can customize display
      },
      { 
        icon: <Users />, 
        label: 'User Access Control', 
        path: '/settings/access-control',
        roles: [UserRole.SUPERADMIN, UserRole.ADMIN]
      },
      { 
        icon: <Mail />, 
        label: 'Email Configuration', 
        path: '/settings/email',
        roles: [UserRole.SUPERADMIN, UserRole.ADMIN]
      },
      { 
        icon: <FileEdit />, 
        label: 'Document Templates', 
        path: '/settings/templates',
        roles: [UserRole.SUPERADMIN, UserRole.ADMIN]
      },
      { 
        icon: <Building />, 
        label: 'Company Settings', 
        path: '/settings/company',
        roles: [UserRole.SUPERADMIN]
      },
      { 
        icon: <Lock />, 
        label: 'Security Settings', 
        path: '/settings/security',
        roles: [UserRole.SUPERADMIN, UserRole.DEVELOPER]
      },
      { 
        icon: <Database />, 
        label: 'Database Management', 
        path: '/settings/database',
        roles: [UserRole.SUPERADMIN, UserRole.DEVELOPER]
      },
    ]
  },
]

export const Sidebar: React.FC = () => {
  const { user } = useAuthStore()
  const { sidebarOpen } = useUIStore()
  const { hasPermission } = usePermissionStore()
  const location = useLocation()
  const [openDropdowns, setOpenDropdowns] = useState<string[]>([])

  /**
   * Check if user has access to a menu item
   * Supports both permission-based (new) and role-based (old) checks
   * 
   * DEVELOPER and SUPERADMIN roles bypass all checks (full access)
   */
  const hasAccess = (item: MenuItem | SubMenuItem): boolean => {
    if (!user) return false
    
    // BYPASS: Developer, Superadmin, and ADMIN have full access (matches backend)
    // Handle both database format (ADMIN, DEVELOPER, SUPERADMIN) and TypeScript enum format
    const userRoleUpper = user.role.toUpperCase()
    if (userRoleUpper === 'DEVELOPER' || userRoleUpper === 'SUPERADMIN' || userRoleUpper === 'ADMIN') {
      return true
    }
    
    // Settings submenu items without roles/permissions are accessible to all logged-in users
    if (!item.roles && !item.permissions) {
      return true
    }
    
    // Priority 1: PBAC - Permission-based check (primary system)
    if (item.permissions && item.permissions.length > 0) {
      // Check if user has ANY of the required permissions (OR logic)
      return item.permissions.some(perm => hasPermission(perm))
    }
    
    // Priority 2: RBAC - Role-based check (fallback for backward compatibility)
    if (item.roles && item.roles.length > 0) {
      return item.roles.includes(user.role as UserRole)
    }
    
    // Default: deny access if no permissions or roles defined
    return false
  }

  const visibleItems = menuItems.filter((item) => {
    // Check main item access
    if (hasAccess(item)) {
      return true
    }
    
    // Check if user has access to any submenu item
    if (item.submenu) {
      return item.submenu.some(sub => hasAccess(sub))
    }
    
    return false
  })

  const toggleDropdown = (label: string) => {
    setOpenDropdowns(prev => 
      prev.includes(label) 
        ? prev.filter(item => item !== label)
        : [...prev, label]
    )
  }

  const isActive = (path?: string, submenu?: SubMenuItem[]) => {
    if (path && location.pathname === path) return true
    if (submenu) {
      return submenu.some(sub => location.pathname === sub.path)
    }
    return false
  }

  const renderMenuItem = (item: MenuItem) => {
    const hasSubmenu = item.submenu && item.submenu.length > 0
    const isDropdownOpen = openDropdowns.includes(item.label)
    const active = isActive(item.path, item.submenu)

    // Filter visible submenu items using hasAccess (supports both permissions and roles)
    const visibleSubmenu = item.submenu?.filter(sub => hasAccess(sub))

    if (hasSubmenu && visibleSubmenu && visibleSubmenu.length > 0) {
      return (
        <div key={item.label}>
          <button
            onClick={() => toggleDropdown(item.label)}
            className={`flex items-center justify-between w-full gap-3 px-4 py-3 rounded-lg transition-colors ${
              active
                ? 'bg-brand-600 text-white'
                : 'text-gray-300 hover:bg-gray-800'
            }`}
            title={!sidebarOpen ? item.label : undefined}
          >
            <div className="flex items-center gap-3">
              <div className="w-6 h-6 flex-shrink-0">{item.icon}</div>
              {sidebarOpen && <span className="text-sm">{item.label}</span>}
            </div>
            {sidebarOpen && (
              <div className="w-4 h-4 flex-shrink-0">
                {isDropdownOpen ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
              </div>
            )}
          </button>

          {/* Submenu */}
          {sidebarOpen && isDropdownOpen && (
            <div className="ml-4 mt-1 space-y-1 border-l-2 border-gray-700 pl-4">
              {visibleSubmenu.map((subItem) => (
                <Link
                  key={subItem.path}
                  to={subItem.path}
                  className={`flex items-center gap-3 px-3 py-2 rounded-lg transition-colors text-sm ${
                    location.pathname === subItem.path
                      ? 'bg-brand-500 text-white'
                      : 'text-gray-400 hover:bg-gray-800 hover:text-white'
                  }`}
                >
                  <div className="w-5 h-5 flex-shrink-0">{subItem.icon}</div>
                  <span>{subItem.label}</span>
                </Link>
              ))}
            </div>
          )}
        </div>
      )
    }

    // Regular menu item without submenu
    if (item.path) {
      return (
        <Link
          key={item.path}
          to={item.path}
          className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
            location.pathname === item.path
              ? 'bg-brand-600 text-white'
              : 'text-gray-300 hover:bg-gray-800'
          }`}
          title={!sidebarOpen ? item.label : undefined}
        >
          <div className="w-6 h-6 flex-shrink-0">{item.icon}</div>
          {sidebarOpen && <span className="text-sm">{item.label}</span>}
        </Link>
      )
    }

    return null
  }

  return (
    <div
      className={`bg-gray-900 text-white h-screen shadow-lg transition-all duration-300 overflow-y-auto relative z-20 ${
        sidebarOpen ? 'w-64' : 'w-20'
      }`}
    >
      <div className="p-4 pb-20">
        {sidebarOpen && (
          <div className="text-center mb-8">
            <h2 className="text-xl font-bold text-brand-400">DR ERP</h2>
            <p className="text-xs text-gray-400">Manufacturing System</p>
          </div>
        )}

        <nav className="space-y-2 mb-8">
          {visibleItems.map(renderMenuItem)}
        </nav>
        
        {sidebarOpen && (
          <div className="mt-8 p-4 bg-gray-800 rounded-lg">
            <p className="text-xs text-gray-400 mb-2">Version</p>
            <p className="text-sm font-semibold">1.26.0</p>
          </div>
        )}
      </div>
    </div>
  )
}
