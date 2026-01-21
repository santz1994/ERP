import React, { useEffect, useState } from 'react'
import { BarChart3, TrendingUp, AlertCircle, CheckCircle } from 'lucide-react'
import { useUIStore } from '@/store'
import { EnvironmentBanner } from '@/components/EnvironmentBanner'
import { apiClient } from '@/api/client'

interface DashboardStats {
  total_mos: number
  completed_today: number
  pending_qc: number
  critical_alerts: number
  refreshed_at: string | null
}

interface ProductionStatus {
  dept: string
  total_jobs: number
  completed: number
  in_progress: number
  pending: number
  progress: number
  status: 'Running' | 'Pending' | 'Idle'
}

interface Alert {
  id: number
  type: 'critical' | 'warning' | 'info'
  message: string
  created_at: string
}

export const DashboardPage: React.FC = () => {
  const { addNotification } = useUIStore()
  const [stats, setStats] = useState<DashboardStats>({
    total_mos: 0,
    completed_today: 0,
    pending_qc: 0,
    critical_alerts: 0,
    refreshed_at: null
  })
  const [productionStatus, setProductionStatus] = useState<ProductionStatus[]>([])
  const [alerts, setAlerts] = useState<Alert[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadDashboardData()
  }, [])

  const loadDashboardData = async () => {
    try {
      setLoading(true)
      
      // Fetch dashboard stats (from materialized view - <100ms)
      const statsResponse = await apiClient.get('/dashboard/stats')
      setStats(statsResponse.data)
      
      // Fetch production status (from materialized view - <100ms)
      const prodResponse = await apiClient.get('/dashboard/production-status')
      setProductionStatus(prodResponse.data)
      
      // Fetch recent alerts (from materialized view - <100ms)
      const alertsResponse = await apiClient.get('/dashboard/alerts')
      setAlerts(alertsResponse.data)
      
    } catch (error) {
      console.error('Failed to load dashboard data:', error)
      addNotification('error', 'Failed to load dashboard data')
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    )
  }

  return (
    <div>
      <EnvironmentBanner />
      <div className="p-6">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-600">
            Welcome back! Here's your production overview.
            {stats.refreshed_at && (
              <span className="text-xs text-gray-400 ml-2">
                (Updated: {new Date(stats.refreshed_at).toLocaleTimeString()})
              </span>
            )}
          </p>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <StatCard
            title="Total MOs"
            value={stats.total_mos}
            icon={<BarChart3 className="w-8 h-8" />}
            color="bg-blue-50 text-blue-600"
          />
          <StatCard
            title="Completed Today"
            value={stats.completed_today}
            icon={<CheckCircle className="w-8 h-8" />}
            color="bg-green-50 text-green-600"
          />
          <StatCard
            title="Pending QC"
            value={stats.pending_qc}
            icon={<AlertCircle className="w-8 h-8" />}
            color="bg-yellow-50 text-yellow-600"
          />
          <StatCard
            title="Critical Alerts"
            value={stats.critical_alerts}
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
            {productionStatus.map((dept) => (
              <ProductionStatusItem 
                key={dept.dept}
                dept={dept.dept} 
                progress={dept.progress} 
                status={dept.status}
                totalJobs={dept.total_jobs}
                inProgress={dept.in_progress}
              />
            ))}
          </div>
        </div>

        {/* Recent Alerts */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Recent Alerts</h2>
          <div className="space-y-3">
            {alerts.length > 0 ? (
              alerts.map((alert) => (
                <AlertItem 
                  key={alert.id}
                  type={alert.type} 
                  message={alert.message} 
                />
              ))
            ) : (
              <p className="text-sm text-gray-500 text-center py-4">No recent alerts</p>
            )}
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
  status: 'Running' | 'Pending' | 'Idle'
  totalJobs: number
  inProgress: number
}

const ProductionStatusItem: React.FC<ProductionStatusProps> = ({ 
  dept, 
  progress, 
  status,
  totalJobs,
  inProgress 
}) => (
  <div>
    <div className="flex justify-between mb-2">
      <div>
        <p className="text-sm font-medium text-gray-700">{dept}</p>
        <p className="text-xs text-gray-500">
          {totalJobs} total jobs, {inProgress} in progress
        </p>
      </div>
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
