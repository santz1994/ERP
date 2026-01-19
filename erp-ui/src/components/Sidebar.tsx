import React from 'react'
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
} from 'lucide-react'
import { useAuthStore, useUIStore } from '@/store'
import { UserRole } from '@/types'

interface MenuItem {
  icon: React.ReactNode
  label: string
  path: string
  roles: UserRole[]
}

const menuItems: MenuItem[] = [
  { icon: <BarChart3 />, label: 'Dashboard', path: '/dashboard', roles: Object.values(UserRole) },
  { icon: <BarChart3 />, label: 'PPIC', path: '/ppic', roles: [UserRole.PPIC, UserRole.ADMIN] },
  { icon: <ShoppingCart />, label: 'Purchasing', path: '/purchasing', roles: [UserRole.PPIC, UserRole.ADMIN] },
  { icon: <Warehouse />, label: 'Warehouse', path: '/warehouse', roles: [UserRole.WAREHOUSE_ADMIN, UserRole.ADMIN] },
  { icon: <Scissors />, label: 'Cutting', path: '/cutting', roles: [UserRole.OPERATOR_CUTTING, UserRole.SPV_CUTTING, UserRole.ADMIN] },
  { icon: <Palette />, label: 'Embroidery', path: '/embroidery', roles: [UserRole.OPERATOR_CUTTING, UserRole.SPV_CUTTING, UserRole.ADMIN] },
  { icon: <Zap />, label: 'Sewing', path: '/sewing', roles: [UserRole.OPERATOR_SEWING, UserRole.SPV_SEWING, UserRole.ADMIN] },
  { icon: <Sparkles />, label: 'Finishing', path: '/finishing', roles: [UserRole.OPERATOR_FINISHING, UserRole.SPV_FINISHING, UserRole.ADMIN] },
  { icon: <Package />, label: 'Packing', path: '/packing', roles: [UserRole.OPERATOR_PACKING, UserRole.ADMIN] },
  { icon: <TruckIcon />, label: 'Finish Goods', path: '/finishgoods', roles: [UserRole.WAREHOUSE_ADMIN, UserRole.ADMIN] },
  { icon: <Beaker />, label: 'Quality', path: '/quality', roles: [UserRole.QC_INSPECTOR, UserRole.ADMIN] },
  { icon: <Users />, label: 'Admin', path: '/admin', roles: [UserRole.ADMIN] },
]

export const Sidebar: React.FC = () => {
  const { user } = useAuthStore()
  const { sidebarOpen } = useUIStore()
  const location = useLocation()

  const visibleItems = menuItems.filter((item) =>
    user && item.roles.includes(user.role as UserRole)
  )

  return (
    <div
      className={`bg-gray-900 text-white h-screen shadow-lg transition-all duration-300 ${
        sidebarOpen ? 'w-64' : 'w-20'
      }`}
    >
      <div className="p-4">
        {sidebarOpen && (
          <div className="text-center mb-8">
            <h2 className="text-xl font-bold text-brand-400">QK ERP</h2>
            <p className="text-xs text-gray-400">Manufacturing System</p>
          </div>
        )}

        <nav className="space-y-2">
          {visibleItems.map((item) => (
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
          ))}
        </nav>
      </div>

      {sidebarOpen && (
        <div className="absolute bottom-4 left-4 right-4 p-4 bg-gray-800 rounded-lg">
          <p className="text-xs text-gray-400 mb-2">Version</p>
          <p className="text-sm font-semibold">1.0.0</p>
        </div>
      )}
    </div>
  )
}
