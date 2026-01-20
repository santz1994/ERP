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

function App() {
  const { user, loadUserFromStorage } = useAuthStore()

  useEffect(() => {
    loadUserFromStorage()
  }, [])

  if (!user) {
    return <LoginPage />
  }

  return (
    <Router>
      <Routes>
        <Route path="/login" element={<LoginPage />} />

        {/* Protected Routes */}
        <Route
          path="/dashboard"
          element={
            <ProtectedLayout>
              <DashboardPage />
            </ProtectedLayout>
          }
        />

        <Route
          path="/ppic"
          element={
            <ProtectedLayout>
              <PPICPage />
            </ProtectedLayout>
          }
        />

        <Route
          path="/cutting"
          element={
            <ProtectedLayout>
              <CuttingPage />
            </ProtectedLayout>
          }
        />

        <Route
          path="/embroidery"
          element={
            <ProtectedLayout>
              <EmbroideryPage />
            </ProtectedLayout>
          }
        />

        <Route
          path="/sewing"
          element={
            <ProtectedLayout>
              <SewingPage />
            </ProtectedLayout>
          }
        />

        <Route
          path="/finishing"
          element={
            <ProtectedLayout>
              <FinishingPage />
            </ProtectedLayout>
          }
        />

        <Route
          path="/packing"
          element={
            <ProtectedLayout>
              <PackingPage />
            </ProtectedLayout>
          }
        />

        <Route
          path="/purchasing"
          element={
            <ProtectedLayout>
              <PurchasingPage />
            </ProtectedLayout>
          }
        />

        <Route
          path="/finishgoods"
          element={
            <ProtectedLayout>
              <FinishgoodsPage />
            </ProtectedLayout>
          }
        />

        <Route
          path="/kanban"
          element={
            <ProtectedLayout>
              <KanbanPage />
            </ProtectedLayout>
          }
        />

        <Route
          path="/reports"
          element={
            <ProtectedLayout>
              <ReportsPage />
            </ProtectedLayout>
          }
        />

        <Route
          path="/quality"
          element={
            <ProtectedLayout>
              <QCPage />
            </ProtectedLayout>
          }
        />

        <Route
          path="/warehouse"
          element={
            <ProtectedLayout>
              <WarehousePage />
            </ProtectedLayout>
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
            <ProtectedLayout>
              <AdminUserPage />
            </ProtectedLayout>
          }
        />

        <Route
          path="/admin/masterdata"
          element={
            <ProtectedLayout>
              <AdminMasterdataPage />
            </ProtectedLayout>
          }
        />

        <Route
          path="/admin/import-export"
          element={
            <ProtectedLayout>
              <AdminImportExportPage />
            </ProtectedLayout>
          }
        />

        <Route path="/" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </Router>
  )
}

export default App
