import React, { useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { useAuthStore } from '@/store'
import { useUIStore } from '@/store'
import { Navbar } from '@/components/Navbar'
import { Sidebar } from '@/components/Sidebar'
import { NotificationCenter } from '@/components/NotificationCenter'
import { LoginPage } from '@/pages/LoginPage'
import { DashboardPage } from '@/pages/DashboardPage'
import { UnauthorizedPage } from '@/pages/UnauthorizedPage'
import { canAccessModule } from '@/utils/roleGuard'
import PPICPage from '@/pages/PPICPage'
import MOListPage from '@/pages/ppic/MOListPage'
import MODetailPage from '@/pages/ppic/MODetailPage'
import SPKListPage from '@/pages/ppic/SPKListPage'
import DailyProductionPage from '@/pages/DailyProductionPage'
import ProductionCalendarPage from '@/pages/production/ProductionCalendarPage'
import CuttingInputPage from '@/pages/production/CuttingInputPage'
import WIPDashboardPage from '@/pages/production/WIPDashboardPage'
import CuttingPage from '@/pages/CuttingPage'
import EmbroideryPage from '@/pages/EmbroideryPage'
import SewingPage from '@/pages/SewingPage'
import FinishingPage from '@/pages/FinishingPage'
import PackingPage from '@/pages/PackingPage'
import PurchasingPage from '@/pages/PurchasingPage'
import FinishgoodsPage from '@/pages/FinishgoodsPage'
import WarehousePage from '@/pages/WarehousePage'
import MaterialStockPage from '@/pages/warehouse/MaterialStockPage'
import MaterialReceiptPage from '@/pages/warehouse/MaterialReceiptPage'
import FGStockPage from '@/pages/warehouse/FGStockPage'
import FGReceiptPage from '@/pages/warehouse/FGReceiptPage'
import MaterialIssuePage from '@/pages/warehouse/MaterialIssuePage'
import FinishingWarehousePage from '@/pages/warehouse/FinishingWarehousePage'
import StockOpnamePage from '@/pages/warehouse/StockOpnamePage'
import MaterialAllocationPage from '@/pages/ppic/MaterialAllocationPage'
import EmbroideryInputPage from '@/pages/production/EmbroideryInputPage'
import SewingInputPage from '@/pages/production/SewingInputPage'
import FinishingInputPage from '@/pages/production/FinishingInputPage'
import PackingInputPage from '@/pages/production/PackingInputPage'
import KanbanPage from '@/pages/KanbanPage'
import ReportsPage from '@/pages/ReportsPage'
import QCPage from '@/pages/QCPage'
import ReworkManagementPage from '@/pages/ReworkManagementPage'
import QCCheckpointPage from '@/pages/qc/QCCheckpointPage'

import AdminUserPage from '@/pages/AdminUserPage'
import PermissionManagementPage from '@/pages/PermissionManagementPage'
import AdminMasterdataPage from '@/pages/AdminMasterdataPage'
import AdminImportExportPage from '@/pages/AdminImportExportPage'
import BulkImportPage from '@/pages/BulkImportPage'  // ✅ NEW: Session 49 Phase 8
import AuditTrailPage from '@/pages/AuditTrailPage'
import MaterialDebtPage from '@/pages/MaterialDebtPage'
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

const ProtectedLayout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { sidebarOpen } = useUIStore();
  
  return (
    <div className="flex h-screen bg-gray-100">
      {/* Sidebar - Fixed positioning for proper stacking */}
      <Sidebar />
      
      {/* Main Content Area - Adjusted for sidebar width */}
      <div className={`flex-1 flex flex-col overflow-hidden transition-all duration-300 ${sidebarOpen ? 'ml-64' : 'ml-20'}`}>
        {/* Navbar - Level 2: Sticky and above content */}
        <div className="sticky top-0 z-40 shadow-sm">
          <Navbar />
        </div>
        
        {/* Page Content - Level 0 */}
        <main className="flex-1 overflow-auto">
          {children}
        </main>
      </div>
      
      {/* Notifications - Level 3: Above navbar */}
      <div className="fixed top-4 right-4 z-50 pointer-events-none">
        <div className="pointer-events-auto">
          <NotificationCenter />
        </div>
      </div>
    </div>
  )
}

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
  // Load UI settings on app startup (theme, language, etc)
  const { loadSettings } = useUIStore()
  
  useEffect(() => {
    loadSettings()
  }, [loadSettings])
  
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
          path="/ppic/mo"
          element={
            <PrivateRoute module="ppic">
              <ProtectedLayout>
                <MOListPage />
              </ProtectedLayout>
            </PrivateRoute>
          }
        />



        <Route
          path="/ppic/mo/:id"
          element={
            <PrivateRoute module="ppic">
              <ProtectedLayout>
                <MODetailPage />
              </ProtectedLayout>
            </PrivateRoute>
          }
        />

        <Route
          path="/ppic/spk"
          element={
            <PrivateRoute module="ppic">
              <ProtectedLayout>
                <SPKListPage />
              </ProtectedLayout>
            </PrivateRoute>
          }
        />



        <Route
          path="/daily-production"
          element={
            <PrivateRoute module="production">
              <ProtectedLayout>
                <DailyProductionPage />
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
          path="/production/calendar"
          element={
            <PrivateRoute module="production">
              <ProtectedLayout>
                <ProductionCalendarPage />
              </ProtectedLayout>
            </PrivateRoute>
          }
        />

        <Route
          path="/production/input/cutting"
          element={
            <PrivateRoute module="production">
              <ProtectedLayout>
                <CuttingInputPage />
              </ProtectedLayout>
            </PrivateRoute>
          }
        />

        <Route
          path="/production/wip"
          element={
            <PrivateRoute module="production">
              <ProtectedLayout>
                <WIPDashboardPage />
              </ProtectedLayout>
            </PrivateRoute>
          }
        />

        {/* Purchasing Module Routes */}
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

        {/* QC Module Routes */}
        <Route
          path="/quality"
          element={<Navigate to="/qc/checkpoint" replace />}
        />

        <Route
          path="/qc/checkpoint"
          element={
            <PrivateRoute module="qc">
              <ProtectedLayout>
                <QCCheckpointPage />
              </ProtectedLayout>
            </PrivateRoute>
          }
        />

        <Route
          path="/rework-management"
          element={
            <PrivateRoute module="qc">
              <ProtectedLayout>
                <ReworkManagementPage />
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
          path="/warehouse/material/stock"
          element={
            <PrivateRoute module="warehouse">
              <ProtectedLayout>
                <MaterialStockPage />
              </ProtectedLayout>
            </PrivateRoute>
          }
        />

        <Route
          path="/warehouse/material/receipt"
          element={
            <PrivateRoute module="warehouse">
              <ProtectedLayout>
                <MaterialReceiptPage />
              </ProtectedLayout>
            </PrivateRoute>
          }
        />

        <Route
          path="/warehouse/fg/stock"
          element={
            <PrivateRoute module="warehouse">
              <ProtectedLayout>
                <FGStockPage />
              </ProtectedLayout>
            </PrivateRoute>
          }
        />

        <Route
          path="/warehouse/fg/receipt"
          element={
            <PrivateRoute module="warehouse">
              <ProtectedLayout>
                <FGReceiptPage />
              </ProtectedLayout>
            </PrivateRoute>
          }
        />

        <Route
          path="/warehouse/material/issue"
          element={
            <PrivateRoute module="warehouse">
              <ProtectedLayout>
                <MaterialIssuePage />
              </ProtectedLayout>
            </PrivateRoute>
          }
        />

        <Route
          path="/warehouse/finishing-warehouse"
          element={
            <PrivateRoute module="warehouse">
              <ProtectedLayout>
                <FinishingWarehousePage />
              </ProtectedLayout>
            </PrivateRoute>
          }
        />

        <Route
          path="/warehouse/stock-opname"
          element={
            <PrivateRoute module="warehouse">
              <ProtectedLayout>
                <StockOpnamePage />
              </ProtectedLayout>
            </PrivateRoute>
          }
        />

        <Route
          path="/ppic/material-allocation"
          element={
            <PrivateRoute module="ppic">
              <ProtectedLayout>
                <MaterialAllocationPage />
              </ProtectedLayout>
            </PrivateRoute>
          }
        />

        <Route
          path="/production/input/embroidery"
          element={
            <PrivateRoute module="production">
              <ProtectedLayout>
                <EmbroideryInputPage />
              </ProtectedLayout>
            </PrivateRoute>
          }
        />

        <Route
          path="/production/input/sewing"
          element={
            <PrivateRoute module="production">
              <ProtectedLayout>
                <SewingInputPage />
              </ProtectedLayout>
            </PrivateRoute>
          }
        />

        <Route
          path="/production/input/finishing"
          element={
            <PrivateRoute module="production">
              <ProtectedLayout>
                <FinishingInputPage />
              </ProtectedLayout>
            </PrivateRoute>
          }
        />

        <Route
          path="/production/input/packing"
          element={
            <PrivateRoute module="production">
              <ProtectedLayout>
                <PackingInputPage />
              </ProtectedLayout>
            </PrivateRoute>
          }
        />

        <Route
          path="/material-debt"
          element={
            <PrivateRoute module="warehouse">
              <ProtectedLayout>
                <MaterialDebtPage />
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

        {/* ✅ NEW: Masterdata Bulk Import - Session 49 Phase 8 */}
        <Route
          path="/admin/bulk-import"
          element={
            <PrivateRoute module="masterdata">
              <ProtectedLayout>
                <BulkImportPage />
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
