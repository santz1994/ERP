import React, { useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from '@/store'
import { Navbar } from '@/components/Navbar'
import { Sidebar } from '@/components/Sidebar'
import { NotificationCenter } from '@/components/NotificationCenter'
import { LoginPage } from '@/pages/LoginPage'
import { DashboardPage } from '@/pages/DashboardPage'
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
import AdminMasterdataPage from '@/pages/AdminMasterdataPage'
import AdminImportExportPage from '@/pages/AdminImportExportPage'

// Placeholder for other pages
const PlaceholderPage = ({ title }: { title: string }) => (
  <div className="p-6">
    <h1 className="text-3xl font-bold text-gray-900">{title}</h1>
    <p className="text-gray-600 mt-2">Page under development...</p>
  </div>
)

const ProtectedLayout: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <div className="flex h-screen bg-gray-100">
    <Sidebar />
    <div className="flex-1 flex flex-col overflow-hidden">
      <Navbar />
      <main className="flex-1 overflow-auto">
        {children}
      </main>
    </div>
    <NotificationCenter />
  </div>
)

const PrivateRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { user } = useAuthStore()
  
  if (!user) {
    return <Navigate to="/login" replace />
  }
  
  return <>{children}</>
}

const RootRedirect: React.FC = () => {
  const { user } = useAuthStore()
  return user ? <Navigate to="/dashboard" replace /> : <Navigate to="/login" replace />
}

function App() {
  const { loadUserFromStorage } = useAuthStore()

  useEffect(() => {
    loadUserFromStorage()
  }, [])

  return (
    <Router>
      <Routes>
        <Route path="/login" element={<LoginPage />} />

        {/* Protected Routes */}
        <Route
          path="/dashboard"
          element={
            <PrivateRoute>
              <ProtectedLayout>
                <DashboardPage />
              </ProtectedLayout>
            </PrivateRoute>
          }
        />

        <Route
          path="/ppic"
          element={
            <PrivateRoute>
              <ProtectedLayout>
                <PPICPage />
              </ProtectedLayout>
            </PrivateRoute>
          }
        />

        <Route
          path="/cutting"
          element={
            <PrivateRoute>
              <ProtectedLayout>
                <CuttingPage />
              </ProtectedLayout>
            </PrivateRoute>
          }
        />

        <Route
          path="/embroidery"
          element={
            <PrivateRoute>
              <ProtectedLayout>
                <EmbroideryPage />
              </ProtectedLayout>
            </PrivateRoute>
          }
        />

        <Route
          path="/sewing"
          element={
            <PrivateRoute>
              <ProtectedLayout>
                <SewingPage />
              </ProtectedLayout>
            </PrivateRoute>
          }
        />

        <Route
          path="/finishing"
          element={
            <PrivateRoute>
              <ProtectedLayout>
                <FinishingPage />
              </ProtectedLayout>
            </PrivateRoute>
          }
        />

        <Route
          path="/packing"
          element={
            <PrivateRoute>
              <ProtectedLayout>
                <PackingPage />
              </ProtectedLayout>
            </PrivateRoute>
          }
        />

        <Route
          path="/purchasing"
          element={
            <PrivateRoute>
              <ProtectedLayout>
                <PurchasingPage />
              </ProtectedLayout>
            </PrivateRoute>
          }
        />

        <Route
          path="/finishgoods"
          element={
            <PrivateRoute>
              <ProtectedLayout>
                <FinishgoodsPage />
              </ProtectedLayout>
            </PrivateRoute>
          }
        />

        <Route
          path="/kanban"
          element={
            <PrivateRoute>
              <ProtectedLayout>
                <KanbanPage />
              </ProtectedLayout>
            </PrivateRoute>
          }
        />

        <Route
          path="/reports"
          element={
            <PrivateRoute>
              <ProtectedLayout>
                <ReportsPage />
              </ProtectedLayout>
            </PrivateRoute>
          }
        />

        <Route
          path="/quality"
          element={
            <PrivateRoute>
              <ProtectedLayout>
                <QCPage />
              </ProtectedLayout>
            </PrivateRoute>
          }
        />

        <Route
          path="/warehouse"
          element={
            <PrivateRoute>
              <ProtectedLayout>
                <WarehousePage />
              </ProtectedLayout>
            </PrivateRoute>
          }
        />

        <Route
          path="/admin"
          element={
            <ProtectedLayout>
              <PlaceholderPage title="System Administration" />
            </ProtectedLayout>
          }
        />

        <Route
          path="/admin/users"
          element={
            <PrivateRoute>
              <ProtectedLayout>
                <AdminUserPage />
              </ProtectedLayout>
            </PrivateRoute>
          }
        />

        <Route
          path="/admin/masterdata"
          element={
            <PrivateRoute>
              <ProtectedLayout>
                <AdminMasterdataPage />
              </ProtectedLayout>
            </PrivateRoute>
          }
        />

        <Route
          path="/admin/import-export"
          element={
            <PrivateRoute>
              <ProtectedLayout>
                <AdminImportExportPage />
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
  )
}

export default App
