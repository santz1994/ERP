import React, { useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from '@/store'
import { Navbar } from '@/components/Navbar'
import { Sidebar } from '@/components/Sidebar'
import { NotificationCenter } from '@/components/NotificationCenter'
import { LoginPage } from '@/pages/LoginPage'
import { DashboardPage } from '@/pages/DashboardPage'

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
              <PlaceholderPage title="PPIC - Manufacturing Planning" />
            </ProtectedLayout>
          }
        />

        <Route
          path="/cutting"
          element={
            <ProtectedLayout>
              <PlaceholderPage title="Cutting Department" />
            </ProtectedLayout>
          }
        />

        <Route
          path="/sewing"
          element={
            <ProtectedLayout>
              <PlaceholderPage title="Sewing Department" />
            </ProtectedLayout>
          }
        />

        <Route
          path="/finishing"
          element={
            <ProtectedLayout>
              <PlaceholderPage title="Finishing Department" />
            </ProtectedLayout>
          }
        />

        <Route
          path="/packing"
          element={
            <ProtectedLayout>
              <PlaceholderPage title="Packing Department" />
            </ProtectedLayout>
          }
        />

        <Route
          path="/quality"
          element={
            <ProtectedLayout>
              <PlaceholderPage title="Quality Control" />
            </ProtectedLayout>
          }
        />

        <Route
          path="/warehouse"
          element={
            <ProtectedLayout>
              <PlaceholderPage title="Warehouse Management" />
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

        <Route path="/" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </Router>
  )
}

export default App
