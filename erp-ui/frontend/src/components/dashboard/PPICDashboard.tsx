/**
 * PPIC Dashboard - Specialized Dashboard for PPIC Role
 * Specification: Rencana Tampilan.md Lines 97-103
 * 
 * Focus: MO management, SPK tracking, material allocation
 * Widget: MO Release Status (PARTIAL vs RELEASED)
 * Alert: Material shortage, Delayed SPK
 */

import React, { useEffect, useState } from 'react'
import { Package, AlertTriangle, Clock, TrendingUp, Factory, Box, CheckCircle2, XCircle } from 'lucide-react'
import { apiClient } from '@/api/client'

interface MOStatusCount {
  draft: number
  partial: number
  released: number
  in_progress: number
  completed: number
}

interface SPKDelayed {
  spk_number: string
  article_name: string
  delay_days: number
  department: string
}

interface MaterialCritical {
  material_code: string
  material_name: string
  current_stock: number
  minimum_stock: number
  uom: string
  status: 'safe' | 'warning' | 'critical' | 'debt'
  status_percentage: number
}

interface PPICDashboardData {
  total_spk_active: number
  material_critical_count: number
  mo_delayed_count: number
  production_today: number
  qc_pending: number
  fg_ready_ship: number
  mo_status_count: MOStatusCount
  spk_delayed: SPKDelayed[]
  material_critical: MaterialCritical[]
}

export const PPICDashboard: React.FC = () => {
  const [data, setData] = useState<PPICDashboardData | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchDashboardData()
  }, [])

  const fetchDashboardData = async () => {
    try {
      setLoading(true)
      const response = await apiClient.get('/api/v1/dashboard/ppic')
      setData(response.data.data)
    } catch (error) {
      console.error('Failed to fetch PPIC dashboard:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-brand-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-slate-500">Loading PPIC Dashboard...</p>
        </div>
      </div>
    )
  }

  if (!data) {
    return (
      <div className="text-center text-slate-500 py-12">
        <AlertTriangle className="w-12 h-12 mx-auto mb-4 text-amber-500" />
        <p>Failed to load dashboard data</p>
      </div>
    )
  }

  // Material status color coding (Spec Lines 55-75)
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'safe': return 'text-emerald-600 bg-emerald-50 border-emerald-200'
      case 'warning': return 'text-amber-600 bg-amber-50 border-amber-200'
      case 'critical': return 'text-rose-600 bg-rose-50 border-rose-200'
      case 'debt': return 'text-slate-900 bg-slate-100 border-slate-300'
      default: return 'text-slate-600 bg-slate-50 border-slate-200'
    }
  }

  const getStatusLabel = (status: string, percentage: number) => {
    switch (status) {
      case 'safe': return `Stock Aman (${percentage}%)`
      case 'warning': return `Low (${percentage}%) - Reorder`
      case 'critical': return 'Critical! - Urgent Purchase'
      case 'debt': return 'DEBT! - Production at risk'
      default: return 'Unknown'
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 flex items-center gap-3">
            <Factory className="w-8 h-8 text-brand-600" />
            Dashboard PPIC - PT Quty Karunia
          </h1>
          <p className="text-sm text-slate-500 mt-1">Real-time Production Planning & Material Control</p>
        </div>
        <button
          onClick={fetchDashboardData}
          className="px-4 py-2 bg-white border border-slate-200 rounded-lg hover:bg-slate-50 transition-colors flex items-center gap-2 text-sm font-medium"
        >
          <Clock className="w-4 h-4" />
          Refresh
        </button>
      </div>

      {/* KPI Cards (Spec Lines 38-47) */}
      <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-6 gap-4">
        <KPICard
          title="Total SPK Aktif"
          value={data.total_spk_active}
          icon={<Package />}
          variant="blue"
        />
        <KPICard
          title="Material Critical"
          value={data.material_critical_count}
          icon={<AlertTriangle />}
          variant="amber"
          highlight={data.material_critical_count > 0}
        />
        <KPICard
          title="MO Terlambat"
          value={data.mo_delayed_count}
          icon={<Clock />}
          variant="rose"
          highlight={data.mo_delayed_count > 0}
        />
        <KPICard
          title="Produksi Hari Ini"
          value={`${data.production_today} pcs`}
          icon={<Factory />}
          variant="green"
        />
        <KPICard
          title="QC Pending"
          value={`${data.qc_pending} pcs`}
          icon={<Box />}
          variant="amber"
        />
        <KPICard
          title="FG Ready Ship"
          value={`${data.fg_ready_ship} Cartons`}
          icon={<TrendingUp />}
          variant="green"
        />
      </div>

      {/* MO Release Status Widget (Spec Lines 99) - CRITICAL FEATURE */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6">
        <h2 className="text-lg font-bold text-slate-900 mb-4 flex items-center gap-2">
          <CheckCircle2 className="w-5 h-5 text-brand-600" />
          MO Release Status (PARTIAL vs RELEASED)
        </h2>
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          <StatusBadge label="Draft" count={data.mo_status_count.draft} color="slate" />
          <StatusBadge label="PARTIAL" count={data.mo_status_count.partial} color="amber" pulse />
          <StatusBadge label="RELEASED" count={data.mo_status_count.released} color="emerald" pulse />
          <StatusBadge label="In Progress" count={data.mo_status_count.in_progress} color="blue" />
          <StatusBadge label="Completed" count={data.mo_status_count.completed} color="green" />
        </div>
        <p className="text-xs text-slate-500 mt-4 bg-blue-50 px-3 py-2 rounded border border-blue-100">
          <strong>PARTIAL:</strong> PO Kain ready - Cutting can start | <strong>RELEASED:</strong> PO Label ready - Full production unlocked
        </p>
      </div>

      {/* Material Stock Alert (Spec Lines 55-75) - Color-coded with Black for Debt */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6">
        <h2 className="text-lg font-bold text-slate-900 mb-4 flex items-center gap-2">
          <AlertTriangle className="w-5 h-5 text-amber-600" />
          Material Stock Critical (Top 5)
        </h2>
        {data.material_critical.length === 0 ? (
          <div className="text-center py-8 text-slate-400">
            <CheckCircle2 className="w-12 h-12 mx-auto mb-2 text-emerald-400" />
            <p>All materials are at safe stock levels</p>
          </div>
        ) : (
          <div className="space-y-3">
            {data.material_critical.slice(0, 5).map((material, idx) => (
              <div key={idx} className={`border rounded-lg p-4 ${getStatusColor(material.status)}`}>
                <div className="flex justify-between items-start mb-2">
                  <div>
                    <h3 className="font-bold text-sm">[{material.material_code}] {material.material_name}</h3>
                    <p className="text-xs mt-1">
                      Stock: <span className="font-semibold">{material.current_stock} {material.uom}</span> | 
                      Min: <span className="font-semibold">{material.minimum_stock} {material.uom}</span>
                    </p>
                  </div>
                  <span className={`px-3 py-1 rounded-full text-xs font-bold border`}>
                    {getStatusLabel(material.status, material.status_percentage)}
                  </span>
                </div>
                {material.status === 'debt' && (
                  <div className="mt-2 pt-2 border-t border-slate-200">
                    <p className="text-xs font-medium">Negative Stock - Material Debt Active</p>
                    <p className="text-xs text-slate-600">Production continues with debt tracking</p>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* SPK Delayed Alert (Spec Lines 85-91) */}
      {data.spk_delayed.length > 0 && (
        <div className="bg-rose-50 border border-rose-200 rounded-xl p-6">
          <h2 className="text-lg font-bold text-rose-900 mb-4 flex items-center gap-2">
            <Clock className="w-5 h-5" />
            SPK Terlambat
          </h2>
          <div className="space-y-2">
            {data.spk_delayed.map((spk, idx) => (
              <div key={idx} className="flex justify-between items-center bg-white rounded-lg p-3 border border-rose-100">
                <div>
                  <p className="font-semibold text-sm text-slate-900">
                    • {spk.spk_number} - {spk.article_name}
                  </p>
                  <p className="text-xs text-slate-600">{spk.department}</p>
                </div>
                <span className="px-3 py-1 bg-rose-100 text-rose-700 rounded-full text-xs font-bold">
                  Delay: {spk.delay_days} hari
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

// KPI Card Component
const KPICard: React.FC<{
  title: string
  value: string | number
  icon: React.ReactNode
  variant: 'blue' | 'green' | 'amber' | 'rose'
  highlight?: boolean
}> = ({ title, value, icon, variant, highlight }) => {
  const variants = {
    blue: { bg: 'bg-blue-50', text: 'text-blue-600', border: 'border-blue-100' },
    green: { bg: 'bg-emerald-50', text: 'text-emerald-600', border: 'border-emerald-100' },
    amber: { bg: 'bg-amber-50', text: 'text-amber-600', border: 'border-amber-100' },
    rose: { bg: 'bg-rose-50', text: 'text-rose-600', border: 'border-rose-100' },
  }
  const color = variants[variant]

  return (
    <div className={`bg-white rounded-xl p-4 border ${color.border} shadow-sm ${highlight ? 'ring-2 ring-rose-400 ring-offset-2' : ''}`}>
      <div className={`w-10 h-10 rounded-lg ${color.bg} ${color.text} flex items-center justify-center mb-3`}>
        {React.cloneElement(icon as React.ReactElement, { size: 20 })}
      </div>
      <h3 className="text-2xl font-bold text-slate-900">{value}</h3>
      <p className="text-xs font-medium text-slate-500 mt-1">{title}</p>
    </div>
  )
}

// Status Badge Component
const StatusBadge: React.FC<{
  label: string
  count: number
  color: 'slate' | 'amber' | 'emerald' | 'blue' | 'green'
  pulse?: boolean
}> = ({ label, count, color, pulse }) => {
  const colors = {
    slate: 'bg-slate-100 text-slate-700 border-slate-200',
    amber: 'bg-amber-100 text-amber-700 border-amber-200',
    emerald: 'bg-emerald-100 text-emerald-700 border-emerald-200',
    blue: 'bg-blue-100 text-blue-700 border-blue-200',
    green: 'bg-green-100 text-green-700 border-green-200',
  }

  return (
    <div className={`text-center p-4 rounded-lg border ${colors[color]} ${pulse ? 'animate-pulse' : ''}`}>
      <p className="text-3xl font-bold">{count}</p>
      <p className="text-xs font-medium mt-1">{label}</p>
    </div>
  )
}
