import React, { useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import {
  BarChart3, Scissors, Palette, Zap, Sparkles, Package, Beaker,
  Warehouse, ShoppingCart, TruckIcon, Users, Factory, ChevronDown,
  ChevronRight, FileText, ClipboardList, Shield, AlertCircle,
  Settings, Lock, Globe, Bell, Palette as PaletteIcon, Mail,
  FileEdit, Building, Database, Calendar, LayoutDashboard
} from 'lucide-react'
import { useAuthStore, useUIStore, usePermissionStore } from '@/store'
import { UserRole } from '@/types'

// Tipe data diperbarui dengan 'section'
interface SubMenuItem {
  icon: React.ReactNode
  label: string
  path: string
  roles?: UserRole[]
  permissions?: string[]
}

interface MenuItem {
  icon: React.ReactNode
  label: string
  path?: string
  roles?: UserRole[]
  permissions?: string[]
  submenu?: SubMenuItem[]
  section?: string // New: Untuk grouping menu
}

// Menu Items dengan Grouping Section
const menuItems: MenuItem[] = [
  // --- SECTION: MAIN ---
  { 
    section: 'MAIN',
    icon: <LayoutDashboard />, 
    label: 'Dashboard', 
    path: '/dashboard', 
    permissions: ['dashboard.view_stats']
  },
  
  // --- SECTION: OPERATIONS ---
  { 
    section: 'OPERATIONS',
    icon: <ClipboardList />, 
    label: 'PPIC & Planning', 
    path: '/ppic', 
    permissions: ['ppic.view_mo']
  },
  { 
    icon: <Factory />, 
    label: 'Production Floor', 
    permissions: ['production.view_status'],
    submenu: [
      { icon: <Calendar />, label: 'Daily Input', path: '/daily-production', permissions: ['production.input_daily'] },
      { icon: <Scissors />, label: 'Cutting', path: '/cutting', permissions: ['cutting.view_status'] },
      { icon: <Palette />, label: 'Embroidery', path: '/embroidery', roles: [UserRole.OPERATOR_EMBRO, UserRole.SPV_CUTTING, UserRole.ADMIN] },
      { icon: <Zap />, label: 'Sewing', path: '/sewing', permissions: ['sewing.view_status'] },
      { icon: <Sparkles />, label: 'Finishing', path: '/finishing', permissions: ['finishing.view_status'] },
      { icon: <Package />, label: 'Packing', path: '/packing', permissions: ['packing.view_status'] },
    ]
  },
  { 
    icon: <Beaker />, 
    label: 'Quality Control', 
    path: '/quality', 
    roles: [UserRole.QC_INSPECTOR, UserRole.ADMIN] 
  },
  { 
    icon: <FileEdit />, 
    label: 'Rework Station', 
    path: '/rework-management',
    roles: [UserRole.QC_INSPECTOR, UserRole.SPV_CUTTING, UserRole.SPV_SEWING, UserRole.SPV_FINISHING]
  },

  // --- SECTION: INVENTORY & LOGISTICS ---
  { 
    section: 'INVENTORY',
    icon: <ShoppingCart />, 
    label: 'Purchasing', 
    path: '/purchasing', 
    roles: [UserRole.PURCHASING, UserRole.ADMIN] 
  },
  { 
    icon: <Warehouse />, 
    label: 'Warehouse', 
    path: '/warehouse', 
    roles: [UserRole.WAREHOUSE_ADMIN, UserRole.ADMIN] 
  },
  { 
    icon: <AlertCircle />, 
    label: 'Material Debt', 
    path: '/material-debt', 
    roles: [UserRole.WAREHOUSE_ADMIN, UserRole.SPV_CUTTING, UserRole.SPV_SEWING, UserRole.SPV_FINISHING, UserRole.PPIC_MANAGER] 
  },
  { 
    icon: <TruckIcon />, 
    label: 'Finish Goods', 
    path: '/finishgoods', 
    roles: [UserRole.WAREHOUSE_ADMIN, UserRole.ADMIN] 
  },

  // --- SECTION: SYSTEM ---
  { 
    section: 'SYSTEM',
    icon: <FileText />, 
    label: 'Reports', 
    path: '/reports', 
    roles: [UserRole.PPIC_MANAGER, UserRole.ADMIN] 
  },
  { 
    icon: <Users />, 
    label: 'Administration', 
    permissions: ['admin.manage_users'],
    submenu: [
      { icon: <Users />, label: 'User Management', path: '/admin/users', permissions: ['admin.manage_users'] },
      { icon: <Shield />, label: 'Permissions', path: '/admin/permissions', permissions: ['admin.view_system_info'] },
      { icon: <Shield />, label: 'Audit Trail', path: '/admin/audit-trail', roles: [UserRole.DEVELOPER, UserRole.SUPERADMIN] },
      { icon: <FileText />, label: 'Import/Export', path: '/admin/import-export', permissions: ['import_export.import_data'] },
    ]
  },
  { 
    icon: <Settings />, 
    label: 'Settings', 
    submenu: [
      { icon: <Lock />, label: 'Security', path: '/settings/security' },
      { icon: <Globe />, label: 'General', path: '/settings/company' },
    ]
  },
]

export const Sidebar: React.FC = () => {
  const { user } = useAuthStore()
  const { sidebarOpen } = useUIStore()
  const { hasPermission } = usePermissionStore()
  const location = useLocation()
  const [openDropdowns, setOpenDropdowns] = useState<string[]>([])

  // Helper: Check Access (Logic tetap sama, hanya disederhanakan)
  const hasAccess = (item: MenuItem | SubMenuItem): boolean => {
    if (!user) return false
    const role = user.role.toUpperCase()
    if (['DEVELOPER', 'SUPERADMIN', 'ADMIN'].includes(role)) return true
    if (!item.roles && !item.permissions) return true
    if (item.permissions?.some(p => hasPermission(p))) return true
    if (item.roles?.includes(user.role as UserRole)) return true
    return false
  }

  const toggleDropdown = (label: string) => {
    setOpenDropdowns(prev => prev.includes(label) ? prev.filter(i => i !== label) : [...prev, label])
  }

  // Helper: Styles
  const getLinkClasses = (isActive: boolean, isSubmenu = false) => {
    const base = "flex items-center gap-3 transition-all duration-200 group relative "
    const padding = isSubmenu ? "px-3 py-2 text-sm ml-8" : "px-4 py-3"
    const activeState = isActive 
      ? "text-brand-500 bg-brand-50/10 border-r-[3px] border-brand-500 font-medium" 
      : "text-slate-400 hover:text-slate-100 hover:bg-slate-800/50 border-r-[3px] border-transparent"
    
    return `${base} ${padding} ${activeState}`
  }

  const renderMenuItem = (item: MenuItem, index: number) => {
    if (!hasAccess(item)) return null

    const isActive = item.path === location.pathname || (item.submenu?.some(sub => sub.path === location.pathname) ?? false)
    const isDropdownOpen = openDropdowns.includes(item.label) || isActive // Auto open if active
    const showSectionLabel = item.section && sidebarOpen && (index === 0 || menuItems[index - 1].section !== item.section)

    return (
      <div key={item.label}>
        {/* Section Label */}
        {showSectionLabel && (
          <div className="px-4 mt-6 mb-2">
            <p className="text-[10px] font-bold tracking-wider text-slate-500 uppercase">{item.section}</p>
          </div>
        )}

        {item.submenu ? (
          // --- Dropdown Menu ---
          <div>
            <button
              onClick={() => toggleDropdown(item.label)}
              className={`w-full flex items-center justify-between ${getLinkClasses(false)}`}
              title={!sidebarOpen ? item.label : undefined}
            >
              <div className="flex items-center gap-3">
                <div className={`transition-colors ${isActive ? 'text-brand-400' : 'text-slate-400 group-hover:text-slate-100'}`}>
                  {item.icon}
                </div>
                {sidebarOpen && <span>{item.label}</span>}
              </div>
              {sidebarOpen && (
                <ChevronRight size={14} className={`transition-transform duration-200 ${isDropdownOpen ? 'rotate-90' : ''}`} />
              )}
            </button>
            
            {/* Submenu Items */}
            {sidebarOpen && isDropdownOpen && (
              <div className="mt-1 mb-2 space-y-0.5">
                {item.submenu.filter(hasAccess).map(sub => (
                  <Link
                    key={sub.path}
                    to={sub.path}
                    className={getLinkClasses(location.pathname === sub.path, true)}
                  >
                    <span className="truncate">{sub.label}</span>
                  </Link>
                ))}
              </div>
            )}
          </div>
        ) : (
          // --- Single Menu ---
          <Link
            to={item.path!}
            className={getLinkClasses(isActive)}
            title={!sidebarOpen ? item.label : undefined}
          >
            <div className={`transition-colors ${isActive ? 'text-brand-400' : 'text-slate-400 group-hover:text-slate-100'}`}>
              {item.icon}
            </div>
            {sidebarOpen && <span>{item.label}</span>}
          </Link>
        )}
      </div>
    )
  }

  return (
    <div className={`bg-slate-900 text-slate-300 h-screen shadow-xl transition-all duration-300 flex flex-col relative z-20 ${sidebarOpen ? 'w-64' : 'w-20'}`}>
      {/* Brand Header */}
      <div className="h-16 flex items-center justify-center border-b border-slate-800 bg-slate-950">
        {sidebarOpen ? (
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-brand-600 rounded-lg flex items-center justify-center text-white font-bold">Q</div>
            <div>
              <h1 className="font-bold text-white leading-none">Quty Karunia</h1>
              <span className="text-[10px] text-brand-400 font-medium">ERP SYSTEM v1.2</span>
            </div>
          </div>
        ) : (
          <div className="w-8 h-8 bg-brand-600 rounded-lg flex items-center justify-center text-white font-bold">Q</div>
        )}
      </div>

      {/* Menu List */}
      <nav className="flex-1 overflow-y-auto py-4 custom-scrollbar">
        {menuItems.map((item, idx) => renderMenuItem(item, idx))}
      </nav>

      {/* Footer Profile (Optional) */}
      {sidebarOpen && user && (
        <div className="p-4 border-t border-slate-800 bg-slate-950/50">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-full bg-slate-700 flex items-center justify-center border border-slate-600">
              <span className="font-bold text-xs">{user.username.substring(0, 2).toUpperCase()}</span>
            </div>
            <div className="overflow-hidden">
              <p className="text-sm font-medium text-white truncate">{user.username}</p>
              <p className="text-xs text-slate-500 truncate capitalize">{user.role.replace('_', ' ')}</p>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
