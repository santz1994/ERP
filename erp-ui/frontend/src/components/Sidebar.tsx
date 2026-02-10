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

  // Helper: Enhanced Styles with Modern UI/UX
  const getLinkClasses = (isActive: boolean, isSubmenu = false) => {
    const base = "flex items-center gap-3 transition-all duration-300 group relative overflow-hidden "
    const padding = isSubmenu ? "px-4 py-2.5 text-sm ml-6" : "px-4 py-3.5"
    
    if (isActive) {
      return `${base} ${padding} text-white bg-gradient-to-r from-blue-600/90 to-blue-500/80 
              border-r-4 border-blue-400 font-medium shadow-lg shadow-blue-500/20 
              backdrop-blur-sm before:absolute before:inset-0 before:bg-gradient-to-r 
              before:from-white/10 before:to-transparent before:opacity-0 hover:before:opacity-100 
              before:transition-opacity before:duration-300`
    }
    
    return `${base} ${padding} text-slate-300 hover:text-white relative 
            hover:bg-gradient-to-r hover:from-slate-700/50 hover:to-slate-600/30 
            hover:shadow-md hover:shadow-slate-900/20 hover:border-r-2 hover:border-slate-500/50 
            before:absolute before:inset-0 before:bg-gradient-to-r before:from-white/5 
            before:to-transparent before:opacity-0 hover:before:opacity-100 
            before:transition-all before:duration-300 hover:backdrop-blur-sm`
  }

  const renderMenuItem = (item: MenuItem, index: number) => {
    if (!hasAccess(item)) return null

    const isActive = item.path === location.pathname || (item.submenu?.some(sub => sub.path === location.pathname) ?? false)
    const isDropdownOpen = openDropdowns.includes(item.label) || isActive // Auto open if active
    const showSectionLabel = item.section && sidebarOpen && (index === 0 || menuItems[index - 1].section !== item.section)

    return (
      <div key={item.label}>
        {/* Enhanced Section Label */}
        {showSectionLabel && (
          <div className="px-4 mt-6 mb-3 relative">
            <div className="flex items-center">
              <div className="h-px bg-gradient-to-r from-slate-600 to-transparent flex-1"></div>
              <p className="text-[10px] font-bold tracking-wider text-slate-400 uppercase px-3 bg-slate-900 
                         border border-slate-700 rounded-full py-1 shadow-sm">
                {item.section}
              </p>
              <div className="h-px bg-gradient-to-l from-slate-600 to-transparent flex-1"></div>
            </div>
          </div>
        )}

        {item.submenu ? (
          // --- Dropdown Menu ---
          <div>
            <button
              onClick={() => toggleDropdown(item.label)}
              className={`w-full flex items-center justify-between ${getLinkClasses(isActive)} 
                         rounded-lg mx-2 mb-1 z-10 relative`}
              title={!sidebarOpen ? item.label : undefined}
            >
              <div className="flex items-center gap-3 z-10">
                <div className={`transition-all duration-300 transform group-hover:scale-110 
                               ${isActive ? 'text-white drop-shadow-sm' : 'text-slate-400 group-hover:text-white'} 
                               ${isDropdownOpen ? 'rotate-3' : ''}`}>
                  {item.icon}
                </div>
                {sidebarOpen && (
                  <span className="font-medium tracking-wide truncate z-10">{item.label}</span>
                )}
              </div>
              {sidebarOpen && (
                <ChevronRight 
                  size={16} 
                  className={`transition-all duration-300 transform z-10 
                            ${isDropdownOpen ? 'rotate-90 text-white' : 'text-slate-400 group-hover:text-white'} 
                            group-hover:scale-110`} 
                />
              )}
            </button>
            
            {/* Enhanced Submenu with Smooth Animation */}
            {sidebarOpen && (
              <div className={`overflow-hidden transition-all duration-300 ease-in-out 
                            ${isDropdownOpen ? 'max-h-96 opacity-100' : 'max-h-0 opacity-0'}`}>
                <div className="mt-1 mb-2 space-y-1 pl-2 pr-2">
                  {item.submenu.filter(hasAccess).map((sub, subIndex) => (
                    <Link
                      key={sub.path}
                      to={sub.path}
                      className={`${getLinkClasses(location.pathname === sub.path, true)} 
                                rounded-md mx-1 transform transition-all duration-300 
                                hover:translate-x-1 border border-transparent 
                                hover:border-slate-600/30 hover:shadow-sm 
                                ${location.pathname === sub.path ? 'border-blue-400/30' : ''}`}
                      style={{
                        animationDelay: `${subIndex * 50}ms`,
                        animation: isDropdownOpen ? 'slideInLeft 0.3s ease-out forwards' : ''
                      }}
                    >
                      <div className={`w-2 h-2 rounded-full mr-2 transition-all duration-300 
                                     ${location.pathname === sub.path 
                                       ? 'bg-blue-400 shadow-lg shadow-blue-400/50 scale-125' 
                                       : 'bg-slate-600 group-hover:bg-slate-400'}`}>
                      </div>
                      <span className="truncate font-medium">{sub.label}</span>
                    </Link>
                  ))}
                </div>
              </div>
            )}
          </div>
        ) : (
          // --- Single Menu ---
          <Link
            to={item.path!}
            className={`${getLinkClasses(isActive)} rounded-lg mx-2 mb-1 block relative z-10`}
            title={!sidebarOpen ? item.label : undefined}
          >
            <div className={`transition-all duration-300 transform group-hover:scale-110 z-10 
                           ${isActive ? 'text-white drop-shadow-sm' : 'text-slate-400 group-hover:text-white'}`}>
              {item.icon}
            </div>
            {sidebarOpen && (
              <span className="font-medium tracking-wide truncate z-10">{item.label}</span>
            )}
            {/* Active indicator dot */}
            {isActive && (
              <div className="absolute right-2 top-1/2 transform -translate-y-1/2 w-2 h-2 
                            bg-white rounded-full shadow-lg animate-pulse z-10"></div>
            )}
          </Link>
        )}
      </div>
    )
  }

  return (
    <div className={`bg-gradient-to-b from-slate-900 via-slate-900 to-slate-800 text-slate-300 
                   h-screen shadow-2xl transition-all duration-300 flex flex-col fixed left-0 top-0 z-30
                   before:absolute before:inset-0 before:bg-gradient-to-b before:from-blue-900/5 
                   before:to-purple-900/5 before:pointer-events-none backdrop-blur-sm 
                   ${sidebarOpen ? 'w-64' : 'w-20'}`}>
      {/* Animated background pattern */}
      <div className="absolute inset-0 opacity-5">
        <div className="absolute inset-0 bg-gradient-to-br from-blue-500/10 via-transparent to-purple-500/10"></div>
      </div>
      {/* Enhanced Brand Header */}
      <div className="h-16 flex items-center justify-center border-b border-slate-700/50 
                    bg-gradient-to-r from-slate-950 to-slate-900 relative z-10">
        {sidebarOpen ? (
          <div className="flex items-center gap-3 px-4">
            <div className="w-10 h-10 bg-gradient-to-br from-blue-600 to-blue-500 rounded-xl 
                          flex items-center justify-center text-white font-bold text-lg 
                          shadow-lg shadow-blue-500/25 border border-blue-400/20 
                          hover:shadow-blue-500/40 transition-all duration-300 hover:scale-105">
              Q
            </div>
            <div className="overflow-hidden">
              <h1 className="font-bold text-white leading-none tracking-tight text-lg 
                           bg-gradient-to-r from-white to-blue-100 bg-clip-text text-transparent">
                Quty Karunia
              </h1>
              <span className="text-[11px] text-blue-400 font-medium tracking-wide">
                ERP SYSTEM v1.2
              </span>
            </div>
          </div>
        ) : (
          <div className="w-10 h-10 bg-gradient-to-br from-blue-600 to-blue-500 rounded-xl 
                        flex items-center justify-center text-white font-bold text-lg 
                        shadow-lg shadow-blue-500/25 border border-blue-400/20 
                        hover:shadow-blue-500/40 transition-all duration-300 hover:scale-105">
            Q
          </div>
        )}
      </div>

      {/* Enhanced Menu List */}
      <nav className="flex-1 overflow-y-auto py-4 custom-scrollbar relative z-10 
                   scrollbar-thin scrollbar-track-slate-800 scrollbar-thumb-slate-600 
                   hover:scrollbar-thumb-slate-500">
        <style>{`
          @keyframes slideInLeft {
            from { transform: translateX(-20px); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
          }
          .custom-scrollbar::-webkit-scrollbar {
            width: 6px;
          }
          .custom-scrollbar::-webkit-scrollbar-track {
            background: rgb(30 41 59);
          }
          .custom-scrollbar::-webkit-scrollbar-thumb {
            background: rgb(71 85 105);
            border-radius: 3px;
          }
          .custom-scrollbar::-webkit-scrollbar-thumb:hover {
            background: rgb(100 116 139);
          }
        `}</style>
        {menuItems.map((item, idx) => renderMenuItem(item, idx))}
      </nav>

      {/* Enhanced Footer Profile */}
      {sidebarOpen && user && (
        <div className="p-4 border-t border-slate-700/50 bg-gradient-to-r from-slate-950 to-slate-900 
                      relative z-10 backdrop-blur-sm">
          <div className="flex items-center gap-3 group hover:bg-slate-800/30 rounded-lg p-2 
                        transition-all duration-300 border border-transparent 
                        hover:border-slate-600/30 hover:shadow-lg">
            <div className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-500 to-purple-500 
                          flex items-center justify-center border-2 border-white/10 
                          shadow-lg group-hover:shadow-blue-500/20 transition-all duration-300 
                          group-hover:scale-105">
              <span className="font-bold text-sm text-white drop-shadow-sm">
                {user.username.substring(0, 2).toUpperCase()}
              </span>
            </div>
            <div className="overflow-hidden flex-1">
              <p className="text-sm font-semibold text-white truncate tracking-wide 
                         group-hover:text-blue-100 transition-colors">
                {user.username}
              </p>
              <p className="text-xs text-slate-400 truncate capitalize tracking-wide 
                         group-hover:text-slate-300 transition-colors">
                {user.role.replace('_', ' ')}
              </p>
            </div>
            <div className="w-2 h-2 rounded-full bg-green-400 shadow-lg shadow-green-400/50 
                          animate-pulse group-hover:scale-125 transition-transform"></div>
          </div>
        </div>
      )}
    </div>
  )
}
