import React, { useEffect, useState } from 'react'
import { BarChart3, TrendingUp, AlertCircle, CheckCircle, RefreshCw, Layers, Factory } from 'lucide-react'
import { useAuthStore, useUIStore } from '@/store'
import { EnvironmentBanner } from '@/components/EnvironmentBanner'
import { apiClient } from '@/api/client'
import { MaterialShortageAlerts, WorkOrdersDashboard } from '@/components/manufacturing'
import { PPICDashboard } from '@/components/dashboard/PPICDashboard'
import { ManagerDashboard } from '@/components/dashboard/ManagerDashboard'
import { DirectorDashboard } from '@/components/dashboard/DirectorDashboard'
import { WarehouseDashboard } from '@/components/dashboard/WarehouseDashboard'
import { UserRole } from '@/types'

// Tipe data tetap sama
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

// --- SUB-COMPONENTS (Internal) ---

const StatCard: React.FC<{
  title: string
  value: number | string
  icon: React.ReactNode
  variant: 'blue' | 'green' | 'amber' | 'rose'
  trend?: string
}> = ({ title, value, icon, variant, trend }) => {
  const variants = {
    blue: { bg: 'bg-blue-50', text: 'text-blue-600', border: 'border-blue-100' },
    green: { bg: 'bg-emerald-50', text: 'text-emerald-600', border: 'border-emerald-100' },
    amber: { bg: 'bg-amber-50', text: 'text-amber-600', border: 'border-amber-100' },
    rose: { bg: 'bg-rose-50', text: 'text-rose-600', border: 'border-rose-100' },
  }
  const color = variants[variant]

  return (
    <div className={`bg-white rounded-xl p-6 border ${color.border} shadow-sm hover:shadow-md transition-all duration-300`}>
      <div className="flex items-start justify-between mb-4">
        <div className={`p-3 rounded-lg ${color.bg} ${color.text}`}>
          {React.cloneElement(icon as React.ReactElement, { size: 24 })}
        </div>
        {trend && (
          <span className="text-xs font-medium text-slate-400 bg-slate-50 px-2 py-1 rounded-full">
            {trend}
          </span>
        )}
      </div>
      <div>
        <h3 className="text-3xl font-bold text-slate-900 tracking-tight">{value}</h3>
        <p className="text-sm font-medium text-slate-500 mt-1">{title}</p>
      </div>
    </div>
  )
}

const DeptProgressRow: React.FC<ProductionStatus> = ({ dept, progress, status, total_jobs, in_progress }) => {
  const statusColor = status === 'Running' ? 'text-emerald-600 bg-emerald-50 border-emerald-100' :
                      status === 'Pending' ? 'text-amber-600 bg-amber-50 border-amber-100' :
                      'text-slate-500 bg-slate-100 border-slate-200'
  
  const barColor = status === 'Running' ? 'bg-emerald-500' : status === 'Pending' ? 'bg-amber-500' : 'bg-slate-400'

  return (
    <div className="group p-4 rounded-lg hover:bg-slate-50 transition-colors border border-transparent hover:border-slate-100">
      <div className="flex justify-between items-center mb-3">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded bg-slate-100 flex items-center justify-center text-slate-500 font-bold text-xs">
            {dept.substring(0, 2).toUpperCase()}
          </div>
          <div>
            <h4 className="text-sm font-bold text-slate-800">{dept}</h4>
            <p className="text-xs text-slate-500">{total_jobs} jobs • {in_progress} active</p>
          </div>
        </div>
        <span className={`text-xs font-semibold px-2.5 py-1 rounded-full border ${statusColor}`}>
          {status}
        </span>
      </div>
      <div className="relative w-full h-2 bg-slate-100 rounded-full overflow-hidden">
        <div 
          className={`absolute top-0 left-0 h-full rounded-full transition-all duration-1000 ${barColor}`} 
          style={{ width: `${progress}%` }}
        />
      </div>
      <div className="flex justify-end mt-1">
        <span className="text-xs font-mono text-slate-400">{progress}%</span>
      </div>
    </div>
  )
}

// --- MAIN COMPONENT ---

export const DashboardPage: React.FC = () => {
  const { addNotification } = useUIStore()
  const user = useAuthStore(state => state.user)
  
  // Role-based Dashboard Selection (Spec Lines 97-122)
  const renderDashboardByRole = () => {
    if (!user) return <GenericDashboard />
    
    // PPIC Dashboard (Spec Lines 97-103)
    if (user.role === UserRole.PPIC_MANAGER || user.role === UserRole.PPIC_ADMIN) {
      return <PPICDashboard />
    }
    
    // Manager Dashboard (Spec Lines 105-109)
    if (user.role === UserRole.MANAGER || user.role === UserRole.FINANCE_MANAGER) {
      return <ManagerDashboard />
    }
    
    // Director Dashboard (Spec Lines 111-115) COMPLETE
    if (user.role === UserRole.SUPERADMIN || user.role === UserRole.DEVELOPER) {
      return <DirectorDashboard />
    }
    
    // Warehouse Dashboard (Spec Lines 117-122) COMPLETE
    if (user.role === UserRole.WAREHOUSE_ADMIN || user.role === UserRole.WAREHOUSE_OP) {
      return <WarehouseDashboard />
    }
    
    // Default: Generic Dashboard
    return <GenericDashboard />
  }

  return (
    <div className="space-y-6">
      <EnvironmentBanner />
      {renderDashboardByRole()}
    </div>
  )
}

// Generic Dashboard Component (Original implementation)
const GenericDashboard: React.FC = () => {
  const { addNotification } = useUIStore()
  const [stats, setStats] = useState<DashboardStats>({
    total_mos: 0, completed_today: 0, pending_qc: 0, critical_alerts: 0, refreshed_at: null
  })
  const [productionStatus, setProductionStatus] = useState<ProductionStatus[]>([])
  const [alerts, setAlerts] = useState<Alert[]>([])
  const [loading, setLoading] = useState(true)

  const loadDashboardData = async () => {
    try {
      setLoading(true)
      const [statsRes, prodRes, alertsRes] = await Promise.all([
        apiClient.get('/dashboard/stats'),
        apiClient.get('/dashboard/production-status'),
        apiClient.get('/dashboard/alerts')
      ])
      setStats(statsRes.data)
      setProductionStatus(prodRes.data)
      setAlerts(alertsRes.data)
    } catch (error) {
      console.error('Failed to load dashboard data:', error)
      addNotification('error', 'Gagal memuat data dashboard')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { loadDashboardData() }, [])

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center h-[calc(100vh-4rem)] bg-slate-50">
        <div className="w-12 h-12 border-4 border-brand-200 border-t-brand-600 rounded-full animate-spin mb-4"></div>
        <p className="text-slate-500 font-medium animate-pulse">Menyiapkan Dashboard...</p>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-slate-50 pb-12">
      <EnvironmentBanner />
      
      <div className="p-8 max-w-7xl mx-auto">
        {/* Header Section */}
        <div className="flex flex-col md:flex-row md:items-end justify-between mb-8 gap-4">
          <div>
            <h1 className="text-3xl font-bold text-slate-900 tracking-tight">Production Overview</h1>
            <p className="text-slate-500 mt-1">Pantau performa pabrik secara real-time.</p>
          </div>
          <div className="flex items-center gap-2 text-xs text-slate-400 bg-white px-3 py-1.5 rounded-full shadow-sm border border-slate-200">
            <RefreshCw size={12} />
            <span>Last updated: {stats.refreshed_at ? new Date(stats.refreshed_at).toLocaleTimeString() : '-'}</span>
          </div>
        </div>

        {/* Top Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <StatCard
            title="Active MOs"
            value={stats.total_mos}
            icon={<Layers />}
            variant="blue"
            trend="On Track"
          />
          <StatCard
            title="Output Today"
            value={stats.completed_today}
            icon={<CheckCircle />}
            variant="green"
            trend="+12% vs yest."
          />
          <StatCard
            title="Waiting QC"
            value={stats.pending_qc}
            icon={<BarChart3 />}
            variant="amber"
          />
          <StatCard
            title="System Alerts"
            value={stats.critical_alerts}
            icon={<AlertCircle />}
            variant="rose"
            trend={stats.critical_alerts > 0 ? "Action Needed" : "All Good"}
          />
        </div>

        {/* Material Alerts - Full Width */}
        <div className="mb-8 bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
          <div className="p-4 border-b border-slate-100 bg-slate-50/50 flex items-center gap-2">
            <AlertCircle size={18} className="text-amber-500" />
            <h3 className="font-bold text-slate-800">Material Shortages & Warnings</h3>
          </div>
          <div className="p-4">
             <MaterialShortageAlerts maxItems={3} />
          </div>
        </div>

        {/* Main Split: Status & Alerts */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          
          {/* Left: Production Progress (2/3 width) */}
          <div className="lg:col-span-2 bg-white rounded-xl shadow-sm border border-slate-200 p-6">
            <h2 className="text-lg font-bold text-slate-900 mb-6 flex items-center gap-2">
              <Factory className="text-slate-400" size={20} />
              Department Status
            </h2>
            <div className="space-y-2">
              {productionStatus.map((dept) => (
                <DeptProgressRow key={dept.dept} {...dept} />
              ))}
            </div>
          </div>

          {/* Right: Recent Alerts Feed (1/3 width) */}
          <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 h-fit">
            <h2 className="text-lg font-bold text-slate-900 mb-6 flex items-center gap-2">
              <TrendingUp className="text-slate-400" size={20} />
              Activity Feed
            </h2>
            <div className="space-y-4 max-h-[400px] overflow-y-auto pr-2 custom-scrollbar">
              {alerts.length > 0 ? (
                alerts.map((alert) => (
                  <div key={alert.id} className="flex gap-3 items-start p-3 rounded-lg bg-slate-50 border border-slate-100">
                    <div className={`w-2 h-2 rounded-full mt-2 flex-shrink-0 ${
                      alert.type === 'critical' ? 'bg-rose-500' :
                      alert.type === 'warning' ? 'bg-amber-500' : 'bg-blue-500'
                    }`} />
                    <div>
                      <p className="text-sm text-slate-700 font-medium leading-tight">{alert.message}</p>
                      <span className="text-[10px] text-slate-400 mt-1 block">
                        {new Date(alert.created_at).toLocaleString()}
                      </span>
                    </div>
                  </div>
                ))
              ) : (
                <div className="text-center py-8 text-slate-400">
                  <CheckCircle size={32} className="mx-auto mb-2 opacity-20" />
                  <p className="text-sm">No new alerts</p>
                </div>
              )}
            </div>
          </div>

        </div>

        {/* Work Orders Table */}
        <div className="mt-8">
          <WorkOrdersDashboard departmentFilter="ALL" />
        </div>
      </div>
    </div>
  )
}
