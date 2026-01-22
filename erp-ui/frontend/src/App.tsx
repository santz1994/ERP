import React, { useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { useAuthStore } from '@/store'
import { Navbar } from '@/components/Navbar'
import { Sidebar } from '@/components/Sidebar'
import { NotificationCenter } from '@/components/NotificationCenter'
import { LoginPage } from '@/pages/LoginPage'
import { DashboardPage } from '@/pages/DashboardPage'
import { UnauthorizedPage } from '@/pages/UnauthorizedPage'
import { canAccessModule } from '@/utils/roleGuard'
import PPICPage from '@/pages/PPICPage'
import CuttingPage from '@/pages/CuttingPage'
import EmbroideryPage from '@/pages/EmbroideryPage'
import SewingPage from '@/pages/SewingPage'
import FinishingPage from '@/pages/FinishingPage'
import PackingPage from '@/pages/PackingPage'
import PurchasingPage from '@/pages/PurchasingPage'
import FinishgoodsPage from '@/pages/FinishgoodsPage'
import WarehousePage from '@/pages/WarehousePage'
import KanbanPage from '@/pages/KanbanPage'
import ReportsPage from '@/pages/ReportsPage'
import QCPage from '@/pages/QCPage'
import AdminUserPage from '@/pages/AdminUserPage'
import PermissionManagementPage from '@/pages/PermissionManagementPage'
import AdminMasterdataPage from '@/pages/AdminMasterdataPage'
import AdminImportExportPage from '@/pages/AdminImportExportPage'
import AuditTrailPage from '@/pages/AuditTrailPage'
import ChangePasswordPage from '@/pages/settings/ChangePasswordPage'
import { SettingsPlaceholder } from '@/pages/settings/SettingsPlaceholder'
import { LanguageTimezoneSettings } from '@/pages/settings/LanguageTimezoneSettings'
import { NotificationsSettings } from '@/pages/settings/NotificationsSettings'
import { DisplayPreferencesSettings } from '@/pages/settings/DisplayPreferencesSettings'
import { AccessControlSettings } from '@/pages/settings/AccessControlSettings'
import { EmailConfigurationSettings } from '@/pages/settings/EmailConfigurationSettings'
import { DocumentTemplatesSettings } from '@/pages/settings/DocumentTemplatesSettings'
import { CompanySettings } from '@/pages/settings/CompanySettings'
import { SecuritySettings } from '@/pages/settings/SecuritySettings'
import { DatabaseManagementSettings } from '@/pages/settings/DatabaseManagementSettings'

// Create QueryClient instance
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  },
})

const ProtectedLayout: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <div className="flex h-screen bg-gray-100 relative">
    {/* Sidebar */}
    <Sidebar />
    
    {/* Main Content Area */}
    <div className="flex-1 flex flex-col overflow-hidden relative z-0">
      {/* Navbar - positioned above main content */}
      <div className="relative z-10">
        <Navbar />
      </div>
      
      {/* Page Content */}
      <main className="flex-1 overflow-auto">
        {children}
      </main>
    </div>
    
    {/* Notifications - positioned at top right with high z-index */}
    <div className="absolute top-0 right-0 z-50">
      <NotificationCenter />
    </div>
  </div>
)

const PrivateRoute: React.FC<{ 
  children: React.ReactNode
  module?: string 
}> = ({ children, module }) => {
  const { user, initialized } = useAuthStore()
  
  console.log('[PrivateRoute] Check:', { initialized, hasUser: !!user, userRole: user?.role })
  
  // CRITICAL: Wait for auth initialization before checking user
  // initializeAuth() is synchronous but we need to ensure React has processed it
  if (!initialized) {
    console.log('[PrivateRoute] Still initializing auth...')
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-brand-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Initializing...</p>
        </div>
      </div>
    )
  }
  
  // Check authentication
  if (!user) {
    console.log('[PrivateRoute] No user found, redirecting to login')
    return <Navigate to="/login" replace />
  }
  
  // Check module access if specified
  if (module && !canAccessModule(user.role, module)) {
    console.log('[PrivateRoute] Module access denied:', module, 'for role:', user.role)
    return <Navigate to="/unauthorized" replace />
  }
  
  console.log('[PrivateRoute] Access granted to:', module || 'page', 'for user:', user.username)
  return <>{children}</>
}

const RootRedirect: React.FC = () => {
  const { user } = useAuthStore()
  return user ? <Navigate to="/dashboard" replace /> : <Navigate to="/login" replace />
}

function App() {
  // Note: Auth initialization happens automatically in store via initializeAuth()
  // No need to call loadUserFromStorage() here as it causes race condition
  
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/unauthorized" element={<UnauthorizedPage />} />

        {/* Protected Routes */}
        <Route
          path="/dashboard"
          element={
            <PrivateRoute module="dashboard">
              <ProtectedLayout>
                <DashboardPage />
              </ProtectedLayout>
            </PrivateRoute>
          }
        />

        <Route
          path="/ppic"
          element={
            <PrivateRoute module="ppic">
              <ProtectedLayout>
                <PPICPage />
              </ProtectedLayout>
            </PrivateRoute>
          }
        />

        <Route
          path="/cutting"
          element={
            <PrivateRoute module="cutting">
              <ProtectedLayout>
                <CuttingPage />
              </ProtectedLayout>
            </PrivateRoute>
          }
        />

        <Route
          path="/embroidery"
          element={
            <PrivateRoute module="embroidery">
              <ProtectedLayout>
                <EmbroideryPage />
              </ProtectedLayout>
            </PrivateRoute>
          }
        />

        <Route
          path="/sewing"
          element={
            <PrivateRoute module="sewing">
              <ProtectedLayout>
                <SewingPage />
              </ProtectedLayout>
            </PrivateRoute>
          }
        />

        <Route
          path="/finishing"
          element={
            <PrivateRoute module="finishing">
              <ProtectedLayout>
                <FinishingPage />
              </ProtectedLayout>
            </PrivateRoute>
          }
        />

        <Route
          path="/packing"
          element={
            <PrivateRoute module="packing">
              <ProtectedLayout>
                <PackingPage />
              </ProtectedLayout>
            </PrivateRoute>
          }
        />

        <Route
          path="/purchasing"
          element={
            <PrivateRoute module="purchasing">
              <ProtectedLayout>
                <PurchasingPage />
              </ProtectedLayout>
            </PrivateRoute>
          }
        />

        <Route
          path="/finishgoods"
          element={
            <PrivateRoute module="finishgoods">
              <ProtectedLayout>
                <FinishgoodsPage />
              </ProtectedLayout>
            </PrivateRoute>
          }
        />

        <Route
          path="/kanban"
          element={
            <PrivateRoute module="kanban">
              <ProtectedLayout>
                <KanbanPage />
              </ProtectedLayout>
            </PrivateRoute>
          }
        />

        <Route
          path="/reports"
          element={
            <PrivateRoute module="reports">
              <ProtectedLayout>
                <ReportsPage />
              </ProtectedLayout>
            </PrivateRoute>
          }
        />

        <Route
          path="/quality"
          element={
            <PrivateRoute module="qc">
              <ProtectedLayout>
                <QCPage />
              </ProtectedLayout>
            </PrivateRoute>
          }
        />

        <Route
          path="/warehouse"
          element={
            <PrivateRoute module="warehouse">
              <ProtectedLayout>
                <WarehousePage />
              </ProtectedLayout>
            </PrivateRoute>
          }
        />

        <Route
          path="/admin"
          element={<Navigate to="/admin/users" replace />}
        />

        <Route
          path="/admin/users"
          element={
            <PrivateRoute module="admin">
              <ProtectedLayout>
                <AdminUserPage />
              </ProtectedLayout>
            </PrivateRoute>
          }
        />

        <Route
          path="/admin/permissions"
          element={
            <PrivateRoute module="admin">
              <ProtectedLayout>
                <PermissionManagementPage />
              </ProtectedLayout>
            </PrivateRoute>
          }
        />

        <Route
          path="/admin/masterdata"
          element={
            <PrivateRoute module="masterdata">
              <ProtectedLayout>
                <AdminMasterdataPage />
              </ProtectedLayout>
            </PrivateRoute>
          }
        />

        <Route
          path="/admin/import-export"
          element={
            <PrivateRoute module="import_export">
              <ProtectedLayout>
                <AdminImportExportPage />
              </ProtectedLayout>
            </PrivateRoute>
          }
        />

        <Route
          path="/admin/audit-trail"
          element={
            <PrivateRoute module="audit">
              <ProtectedLayout>
                <AuditTrailPage />
              </ProtectedLayout>
            </PrivateRoute>
          }
        />

        {/* Settings Routes */}
        <Route
          path="/settings/password"
          element={
            <PrivateRoute>
              <ProtectedLayout>
                <ChangePasswordPage />
              </ProtectedLayout>
            </PrivateRoute>
          }
        />

        <Route
          path="/settings/language"
          element={
            <PrivateRoute>
              <ProtectedLayout>
                <LanguageTimezoneSettings />
              </ProtectedLayout>
            </PrivateRoute>
          }
        />

        <Route
          path="/settings/notifications"
          element={
            <PrivateRoute>
              <ProtectedLayout>
                <NotificationsSettings />
              </ProtectedLayout>
            </PrivateRoute>
          }
        />

        <Route
          path="/settings/display"
          element={
            <PrivateRoute>
              <ProtectedLayout>
                <DisplayPreferencesSettings />
              </ProtectedLayout>
            </PrivateRoute>
          }
        />

        <Route
          path="/settings/access-control"
          element={
            <PrivateRoute module="admin">
              <ProtectedLayout>
                <AccessControlSettings />
              </ProtectedLayout>
            </PrivateRoute>
          }
        />

        <Route
          path="/settings/email"
          element={
            <PrivateRoute module="admin">
              <ProtectedLayout>
                <EmailConfigurationSettings />
              </ProtectedLayout>
            </PrivateRoute>
          }
        />

        <Route
          path="/settings/templates"
          element={
            <PrivateRoute module="admin">
              <ProtectedLayout>
                <DocumentTemplatesSettings />
              </ProtectedLayout>
            </PrivateRoute>
          }
        />

        <Route
          path="/settings/company"
          element={
            <PrivateRoute module="admin">
              <ProtectedLayout>
                <CompanySettings />
              </ProtectedLayout>
            </PrivateRoute>
          }
        />

        <Route
          path="/settings/security"
          element={
            <PrivateRoute module="admin">
              <ProtectedLayout>
                <SecuritySettings />
              </ProtectedLayout>
            </PrivateRoute>
          }
        />

        <Route
          path="/settings/database"
          element={
            <PrivateRoute module="admin">
              <ProtectedLayout>
                <DatabaseManagementSettings />
              </ProtectedLayout>
            </PrivateRoute>
          }
        />

        <Route 
          path="/" 
          element={<RootRedirect />} 
        />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Router>
    </QueryClientProvider>
  )
}

export default App
