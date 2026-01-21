import React from 'react'
import { Menu, X, LogOut, Bell } from 'lucide-react'
import { useAuthStore, useUIStore } from '@/store'
import { useNavigate } from 'react-router-dom'
import { EnvironmentIndicator } from './EnvironmentBanner'

export const Navbar: React.FC = () => {
  const { user, logout } = useAuthStore()
  const { sidebarOpen, toggleSidebar } = useUIStore()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <nav className="bg-white shadow-md border-b border-gray-200">
      <div className="px-4 sm:px-6 lg:px-8 py-3">
        <div className="flex justify-between items-center">
          <div className="flex items-center gap-4">
            <button
              onClick={toggleSidebar}
              className="p-2 rounded-md text-gray-600 hover:bg-gray-100"
            >
              {sidebarOpen ? <X size={24} /> : <Menu size={24} />}
            </button>
            <h1 className="ml-4 text-2xl font-bold text-brand-600">
              Quty Karunia ERP
            </h1>
            {(user?.role === 'Developer' || user?.role === 'Admin' || user?.role === 'Superadmin') && (
              <EnvironmentIndicator />
            )}
          </div>

          <div className="flex items-center gap-4">
            <button className="p-2 text-gray-600 hover:bg-gray-100 rounded-md relative">
              <Bell size={20} />
              <span className="absolute top-1 right-1 h-2 w-2 bg-red-500 rounded-full"></span>
            </button>

            <div className="text-right">
              <p className="text-sm font-medium text-gray-900">{user?.full_name}</p>
              <p className="text-xs text-gray-500">{user?.role}</p>
            </div>

            <button
              onClick={handleLogout}
              className="p-2 text-gray-600 hover:bg-gray-100 rounded-md"
              title="Logout"
            >
              <LogOut size={20} />
            </button>
          </div>
        </div>
      </div>
    </nav>
  )
}
