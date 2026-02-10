import React, { useState, useEffect } from 'react'
import { Menu, X, LogOut, Bell, User, Settings, ChevronRight, Home } from 'lucide-react'
import { useAuthStore, useUIStore } from '@/store'
import { useNavigate, useLocation } from 'react-router-dom'
import { EnvironmentIndicator } from './EnvironmentBanner'
import { UserRole } from '@/types'

// Breadcrumb mapping
const routeLabels: Record<string, string> = {
  dashboard: 'Dashboard', ppic: 'PPIC', 'daily-production': 'Daily Production',
  cutting: 'Cutting', embroidery: 'Embroidery', sewing: 'Sewing', finishing: 'Finishing',
  packing: 'Packing', quality: 'Quality Control', purchasing: 'Purchasing',
  warehouse: 'Warehouse', 'material-debt': 'Material Debt', finishgoods: 'Finish Goods',
  po: 'Purchase Orders', mo: 'Manufacturing Orders', spk: 'Work Orders', create: 'Create',
}

export const Navbar: React.FC = () => {
  const { user, logout } = useAuthStore()
  const { sidebarOpen, toggleSidebar } = useUIStore()
  const navigate = useNavigate()
  const location = useLocation()
  
  const [scrolled, setScrolled] = useState(false)
  const [showNotifications, setShowNotifications] = useState(false)
  const [showUserMenu, setShowUserMenu] = useState(false)

  // Detect scroll for navbar shadow
  useEffect(() => {
    const handleScroll = () => {
      const mainContent = document.querySelector('main')
      if (mainContent) {
        setScrolled(mainContent.scrollTop > 10)
      }
    }
    const mainContent = document.querySelector('main')
    mainContent?.addEventListener('scroll', handleScroll)
    return () => mainContent?.removeEventListener('scroll', handleScroll)
  }, [])

  // Generate breadcrumbs
  const generateBreadcrumbs = () => {
    const pathSegments = location.pathname.split('/').filter(Boolean)
    return pathSegments.map((segment, index) => {
      const path = '/' + pathSegments.slice(0, index + 1).join('/')
      const label = routeLabels[segment] || segment.charAt(0).toUpperCase() + segment.slice(1)
      return { path, label }
    })
  }
  const breadcrumbs = generateBreadcrumbs()
  const getCurrentModule = () => {
    const firstSegment = location.pathname.split('/')[1]
    return routeLabels[firstSegment] || 'ERP System'
  }

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  // Mock notifications
  const notifications = [
    { id: 1, type: 'info', message: 'PO #2026-001 approved', time: '5m ago', read: false },
    { id: 2, type: 'warning', message: 'Low stock alert: Material IKHR504', time: '1h ago', read: false },
    { id: 3, type: 'success', message: 'MO #MO-2026-045 completed', time: '2h ago', read: true },
  ]
  const unreadCount = notifications.filter(n => !n.read).length

  return (
    <nav className={`bg-white transition-shadow duration-200 ${scrolled ? 'shadow-md' : 'shadow-sm'} border-b border-gray-200`}>
      {/* Main Navbar */}
      <div className="px-4 sm:px-6 lg:px-8 py-3">
        <div className="flex justify-between items-center">
          {/* Left Section */}
          <div className="flex items-center gap-4 flex-1">
            <button
              onClick={toggleSidebar}
              className="p-2 rounded-lg text-gray-600 hover:bg-gray-100 transition-colors"
            >
              {sidebarOpen ? <X size={24} /> : <Menu size={24} />}
            </button>
            
            <div className="flex items-center gap-3">
              <h1 className="text-xl sm:text-2xl font-bold text-brand-600">DR ERP</h1>
              {(user?.role === UserRole.DEVELOPER || user?.role === UserRole.ADMIN || user?.role === UserRole.SUPERADMIN) && (
                <EnvironmentIndicator />
              )}
            </div>

            {/* Module Indicator */}
            <div className="hidden md:flex items-center gap-2 ml-4 px-3 py-1 bg-blue-50 rounded-md border border-blue-200">
              <span className="text-xs font-medium text-blue-700">{getCurrentModule()}</span>
            </div>
          </div>

          {/* Right Section */}
          <div className="flex items-center gap-2 sm:gap-4">
            {/* Notifications Dropdown */}
            <div className="relative">
              <button
                onClick={() => {
                  setShowNotifications(!showNotifications)
                  setShowUserMenu(false)
                }}
                className="p-2 text-gray-600 hover:bg-gray-100 rounded-lg transition-colors relative"
              >
                <Bell size={20} />
                {unreadCount > 0 && (
                  <span className="absolute top-1 right-1 h-5 w-5 bg-red-500 text-white text-xs font-bold rounded-full flex items-center justify-center">
                    {unreadCount}
                  </span>
                )}
              </button>

              {showNotifications && (
                <>
                  <div className="fixed inset-0 z-10" onClick={() => setShowNotifications(false)} />
                  <div className="absolute right-0 mt-2 w-80 bg-white rounded-lg shadow-xl border border-gray-200 z-20 max-h-96 overflow-y-auto">
                    <div className="p-4 border-b border-gray-200">
                      <h3 className="font-semibold text-gray-900">Notifications</h3>
                      <p className="text-xs text-gray-500">{unreadCount} unread</p>
                    </div>
                    <div className="divide-y divide-gray-100">
                      {notifications.map((notif) => (
                        <div key={notif.id} className={`p-3 hover:bg-gray-50 cursor-pointer transition-colors ${!notif.read ? 'bg-blue-50' : ''}`}>
                          <p className="text-sm text-gray-900">{notif.message}</p>
                          <p className="text-xs text-gray-500 mt-1">{notif.time}</p>
                        </div>
                      ))}
                    </div>
                    <div className="p-3 border-t border-gray-200 text-center">
                      <button className="text-sm text-blue-600 hover:text-blue-700 font-medium">View all notifications</button>
                    </div>
                  </div>
                </>
              )}
            </div>

            {/* User Profile Dropdown */}
            <div className="relative">
              <button
                onClick={() => {
                  setShowUserMenu(!showUserMenu)
                  setShowNotifications(false)
                }}
                className="flex items-center gap-2 p-2 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <div className="hidden sm:block text-right">
                  <p className="text-sm font-medium text-gray-900">{user?.full_name}</p>
                  <p className="text-xs text-gray-500">{user?.role}</p>
                </div>
                <div className="w-8 h-8 rounded-full bg-gradient-to-br from-brand-500 to-brand-600 flex items-center justify-center text-white font-semibold text-sm">
                  {user?.full_name?.charAt(0).toUpperCase() || 'U'}
                </div>
              </button>

              {showUserMenu && (
                <>
                  <div className="fixed inset-0 z-10" onClick={() => setShowUserMenu(false)} />
                  <div className="absolute right-0 mt-2 w-64 bg-white rounded-lg shadow-xl border border-gray-200 z-20">
                    <div className="p-4 border-b border-gray-200">
                      <p className="font-semibold text-gray-900">{user?.full_name}</p>
                      <p className="text-sm text-gray-500">{user?.email}</p>
                      <span className="inline-block mt-2 px-2 py-1 bg-blue-100 text-blue-700 text-xs font-medium rounded">{user?.role}</span>
                    </div>
                    <div className="py-2">
                      <button onClick={() => { navigate('/profile'); setShowUserMenu(false) }} className="w-full flex items-center gap-3 px-4 py-2 text-gray-700 hover:bg-gray-50 transition-colors">
                        <User size={16} /><span className="text-sm">My Profile</span>
                      </button>
                      <button onClick={() => { navigate('/settings'); setShowUserMenu(false) }} className="w-full flex items-center gap-3 px-4 py-2 text-gray-700 hover:bg-gray-50 transition-colors">
                        <Settings size={16} /><span className="text-sm">Settings</span>
                      </button>
                    </div>
                    <div className="border-t border-gray-200 py-2">
                      <button onClick={handleLogout} className="w-full flex items-center gap-3 px-4 py-2 text-red-600 hover:bg-red-50 transition-colors">
                        <LogOut size={16} /><span className="text-sm font-medium">Logout</span>
                      </button>
                    </div>
                  </div>
                </>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Breadcrumb Navigation */}
      {breadcrumbs.length > 0 && (
        <div className="px-4 sm:px-6 lg:px-8 py-2 bg-gray-50 border-t border-gray-200">
          <div className="flex items-center gap-2 text-sm overflow-x-auto">
            <button onClick={() => navigate('/')} className="text-gray-500 hover:text-gray-700 transition-colors">
              <Home size={16} />
            </button>
            {breadcrumbs.map((crumb, index) => (
              <div key={crumb.path} className="flex items-center gap-2 whitespace-nowrap">
                <ChevronRight size={16} className="text-gray-400" />
                {index === breadcrumbs.length - 1 ? (
                  <span className="text-gray-900 font-medium">{crumb.label}</span>
                ) : (
                  <button onClick={() => navigate(crumb.path)} className="text-gray-600 hover:text-gray-900 transition-colors">{crumb.label}</button>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </nav>
  )
}
