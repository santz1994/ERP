import React, { useEffect, useState } from 'react'
import { BarChart3, TrendingUp, AlertCircle, CheckCircle } from 'lucide-react'
import { useUIStore } from '@/store'

export const DashboardPage: React.FC = () => {
  const { addNotification } = useUIStore()
  const [stats, setStats] = useState({
    totalMOs: 0,
    completedToday: 0,
    pendingQC: 0,
    criticalAlerts: 0,
  })

  useEffect(() => {
    // Load dashboard data
    loadDashboardStats()
  }, [])

  const loadDashboardStats = async () => {
    try {
      // This would call actual API endpoints to fetch stats
      // For now, showing placeholder data
      setStats({
        totalMOs: 42,
        completedToday: 8,
        pendingQC: 3,
        criticalAlerts: 1,
      })
    } catch (error) {
      addNotification('error', 'Failed to load dashboard data')
    }
  }

  return (
    <div className="p-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-600">Welcome back! Here's your production overview.</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <StatCard
          title="Total MOs"
          value={stats.totalMOs}
          icon={<BarChart3 className="w-8 h-8" />}
          color="bg-blue-50 text-blue-600"
        />
        <StatCard
          title="Completed Today"
          value={stats.completedToday}
          icon={<CheckCircle className="w-8 h-8" />}
          color="bg-green-50 text-green-600"
        />
        <StatCard
          title="Pending QC"
          value={stats.pendingQC}
          icon={<AlertCircle className="w-8 h-8" />}
          color="bg-yellow-50 text-yellow-600"
        />
        <StatCard
          title="Critical Alerts"
          value={stats.criticalAlerts}
          icon={<TrendingUp className="w-8 h-8" />}
          color="bg-red-50 text-red-600"
        />
      </div>

      {/* Main Content */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Production Status */}
        <div className="lg:col-span-2 bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Production Status</h2>
          <div className="space-y-4">
            <ProductionStatus dept="Cutting" progress={75} status="Running" />
            <ProductionStatus dept="Sewing" progress={60} status="Running" />
            <ProductionStatus dept="Finishing" progress={45} status="Pending" />
            <ProductionStatus dept="Packing" progress={30} status="Pending" />
          </div>
        </div>

        {/* Recent Alerts */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Recent Alerts</h2>
          <div className="space-y-3">
            <AlertItem type="critical" message="Metal detector fail - Batch 001" />
            <AlertItem type="warning" message="Line clearance required - Cutting" />
            <AlertItem type="info" message="New MO created - MO-2024-042" />
          </div>
        </div>
      </div>
    </div>
  )
}

interface StatCardProps {
  title: string
  value: number
  icon: React.ReactNode
  color: string
}

const StatCard: React.FC<StatCardProps> = ({ title, value, icon, color }) => (
  <div className="bg-white rounded-lg shadow p-6">
    <div className={`w-12 h-12 rounded-lg ${color} flex items-center justify-center mb-4`}>
      {icon}
    </div>
    <p className="text-gray-600 text-sm font-medium">{title}</p>
    <p className="text-3xl font-bold text-gray-900 mt-1">{value}</p>
  </div>
)

interface ProductionStatusProps {
  dept: string
  progress: number
  status: 'Running' | 'Pending' | 'Completed'
}

const ProductionStatus: React.FC<ProductionStatusProps> = ({ dept, progress, status }) => (
  <div>
    <div className="flex justify-between mb-2">
      <p className="text-sm font-medium text-gray-700">{dept}</p>
      <p className={`text-xs font-semibold ${
        status === 'Running' ? 'text-green-600' :
        status === 'Pending' ? 'text-yellow-600' :
        'text-gray-600'
      }`}>
        {status}
      </p>
    </div>
    <div className="w-full bg-gray-200 rounded-full h-2">
      <div
        className={`h-2 rounded-full transition-all ${
          status === 'Running' ? 'bg-green-500' :
          status === 'Pending' ? 'bg-yellow-500' :
          'bg-gray-500'
        }`}
        style={{ width: `${progress}%` }}
      />
    </div>
    <p className="text-xs text-gray-500 mt-1">{progress}% complete</p>
  </div>
)

interface AlertItemProps {
  type: 'critical' | 'warning' | 'info'
  message: string
}

const AlertItem: React.FC<AlertItemProps> = ({ type, message }) => (
  <div className={`p-3 rounded-lg border-l-4 ${
    type === 'critical' ? 'bg-red-50 border-red-500' :
    type === 'warning' ? 'bg-yellow-50 border-yellow-500' :
    'bg-blue-50 border-blue-500'
  }`}>
    <p className={`text-sm ${
      type === 'critical' ? 'text-red-700' :
      type === 'warning' ? 'text-yellow-700' :
      'text-blue-700'
    }`}>
      {message}
    </p>
  </div>
)
