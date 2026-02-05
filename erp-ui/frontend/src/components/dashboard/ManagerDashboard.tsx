/**
 * Manager Dashboard - Specialized Dashboard for Manager Role
 * Specification: Rencana Tampilan.md Lines 105-109
 * 
 * Focus: High-level overview, performance metrics
 * Widget: Production Efficiency, OEE, COPQ
 * Export: PDF reports untuk management meeting
 */

import React, { useEffect, useState } from 'react'
import { TrendingUp, Target, AlertCircle, DollarSign, Download, BarChart3, Activity } from 'lucide-react'
import { apiClient } from '@/api/client'

interface ManagerDashboardData {
  production_efficiency: number // %
  oee: number // Overall Equipment Effectiveness %
  copq_this_month: number // Cost of Poor Quality (Rp)
  copq_last_month: number
  defect_rate: number // %
  rework_recovery_rate: number // %
  on_time_delivery: number // %
  total_output_today: number
  target_today: number
  efficiency_trend: { date: string; efficiency: number }[]
}

export const ManagerDashboard: React.FC = () => {
  const [data, setData] = useState<ManagerDashboardData | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchDashboardData()
  }, [])

  const fetchDashboardData = async () => {
    try {
      setLoading(true)
      const response = await apiClient.get('/api/v1/dashboard/manager')
      setData(response.data.data)
    } catch (error) {
      console.error('Failed to fetch Manager dashboard:', error)
    } finally {
      setLoading(false)
    }
  }

  const exportToPDF = async () => {
    try {
      const response = await apiClient.get('/api/v1/dashboard/manager/export-pdf', {
        responseType: 'blob'
      })
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', `manager-report-${new Date().toISOString().split('T')[0]}.pdf`)
      document.body.appendChild(link)
      link.click()
      link.remove()
    } catch (error) {
      console.error('Failed to export PDF:', error)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-brand-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-slate-500">Loading Manager Dashboard...</p>
        </div>
      </div>
    )
  }

  if (!data) {
    return (
      <div className="text-center text-slate-500 py-12">
        <AlertCircle className="w-12 h-12 mx-auto mb-4 text-amber-500" />
        <p>Failed to load dashboard data</p>
      </div>
    )
  }

  const copqTrend = ((data.copq_this_month - data.copq_last_month) / data.copq_last_month * 100).toFixed(1)
  const isCopqIncreasing = data.copq_this_month > data.copq_last_month

  return (
    <div className="space-y-6">
      {/* Header with Export */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 flex items-center gap-3">
            <BarChart3 className="w-8 h-8 text-brand-600" />
            Dashboard Manager - Performance Metrics
          </h1>
          <p className="text-sm text-slate-500 mt-1">High-level Overview & Strategic Analysis</p>
        </div>
        <button
          onClick={exportToPDF}
          className="px-4 py-2 bg-brand-600 text-white rounded-lg hover:bg-brand-700 transition-colors flex items-center gap-2 text-sm font-medium shadow-sm"
        >
          <Download className="w-4 h-4" />
          Export PDF Report
        </button>
      </div>

      {/* Production Efficiency (Spec Line 107) */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <MetricCard
          title="Production Efficiency"
          value={`${data.production_efficiency}%`}
          icon={<TrendingUp />}
          variant="blue"
          subtitle={`Target vs Actual: ${data.total_output_today}/${data.target_today}`}
          status={data.production_efficiency >= 90 ? 'excellent' : data.production_efficiency >= 75 ? 'good' : 'warning'}
        />
        
        {/* OEE (Overall Equipment Effectiveness) - Spec Line 107 */}
        <MetricCard
          title="OEE (Overall Equipment Effectiveness)"
          value={`${data.oee}%`}
          icon={<Activity />}
          variant="emerald"
          subtitle="World Class Target: 85%"
          status={data.oee >= 85 ? 'excellent' : data.oee >= 70 ? 'good' : 'warning'}
        />
        
        {/* COPQ (Cost of Poor Quality) - Spec Line 107 */}
        <MetricCard
          title="COPQ (Cost of Poor Quality)"
          value={`Rp ${(data.copq_this_month / 1000000).toFixed(1)}M`}
          icon={<DollarSign />}
          variant={isCopqIncreasing ? 'rose' : 'emerald'}
          subtitle={`${isCopqIncreasing ? '↑' : '↓'} ${Math.abs(Number(copqTrend))}% vs last month`}
          status={isCopqIncreasing ? 'warning' : 'good'}
        />
      </div>

      {/* Quality Metrics */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6">
        <h2 className="text-lg font-bold text-slate-900 mb-6">Quality Performance</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <QualityMetric
            label="Defect Rate"
            value={data.defect_rate}
            target={5}
            unit="%"
            reverse // Lower is better
          />
          <QualityMetric
            label="Rework Recovery Rate"
            value={data.rework_recovery_rate}
            target={90}
            unit="%"
          />
          <QualityMetric
            label="On-Time Delivery"
            value={data.on_time_delivery}
            target={95}
            unit="%"
          />
        </div>
      </div>

      {/* Efficiency Trend (7 days) */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6">
        <h2 className="text-lg font-bold text-slate-900 mb-4">Production Efficiency Trend (7 Days)</h2>
        <div className="h-64 flex items-end justify-between gap-2">
          {data.efficiency_trend.map((day, idx) => {
            const height = (day.efficiency / 100) * 100
            const color = day.efficiency >= 90 ? 'bg-emerald-500' : day.efficiency >= 75 ? 'bg-blue-500' : 'bg-amber-500'
            return (
              <div key={idx} className="flex-1 flex flex-col items-center gap-2">
                <div className="w-full relative group">
                  <div 
                    className={`w-full ${color} rounded-t transition-all duration-500 hover:opacity-80 cursor-pointer`}
                    style={{ height: `${height}%` }}
                  >
                    <div className="absolute -top-8 left-1/2 transform -translate-x-1/2 opacity-0 group-hover:opacity-100 transition-opacity bg-slate-900 text-white text-xs px-2 py-1 rounded whitespace-nowrap">
                      {day.efficiency}%
                    </div>
                  </div>
                </div>
                <p className="text-xs text-slate-600 font-medium">{new Date(day.date).toLocaleDateString('id-ID', { day: '2-digit', month: 'short' })}</p>
              </div>
            )
          })}
        </div>
        <div className="mt-4 flex items-center justify-center gap-4 text-xs">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-emerald-500 rounded"></div>
            <span>Excellent (≥90%)</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-blue-500 rounded"></div>
            <span>Good (75-89%)</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-amber-500 rounded"></div>
            <span>Need Improvement (&lt;75%)</span>
          </div>
        </div>
      </div>

      {/* COPQ Breakdown */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6">
        <h2 className="text-lg font-bold text-slate-900 mb-4 flex items-center gap-2">
          <Target className="w-5 h-5 text-rose-600" />
          COPQ Breakdown This Month
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <COPQItem label="Rework Cost" value={data.copq_this_month * 0.4} />
          <COPQItem label="Scrap Cost" value={data.copq_this_month * 0.3} />
          <COPQItem label="Inspection Cost" value={data.copq_this_month * 0.2} />
          <COPQItem label="Downtime Cost" value={data.copq_this_month * 0.1} />
        </div>
        <p className="text-xs text-slate-500 mt-4 bg-rose-50 px-3 py-2 rounded border border-rose-100">
          💡 <strong>Focus:</strong> Reduce rework cost through root cause analysis and preventive actions
        </p>
      </div>
    </div>
  )
}

// Metric Card Component
const MetricCard: React.FC<{
  title: string
  value: string
  icon: React.ReactNode
  variant: 'blue' | 'emerald' | 'rose'
  subtitle: string
  status: 'excellent' | 'good' | 'warning'
}> = ({ title, value, icon, variant, subtitle, status }) => {
  const variants = {
    blue: { bg: 'bg-blue-50', text: 'text-blue-600', border: 'border-blue-100' },
    emerald: { bg: 'bg-emerald-50', text: 'text-emerald-600', border: 'border-emerald-100' },
    rose: { bg: 'bg-rose-50', text: 'text-rose-600', border: 'border-rose-100' },
  }
  const statusColors = {
    excellent: 'bg-emerald-100 text-emerald-700 border-emerald-200',
    good: 'bg-blue-100 text-blue-700 border-blue-200',
    warning: 'bg-amber-100 text-amber-700 border-amber-200',
  }
  const color = variants[variant]

  return (
    <div className={`bg-white rounded-xl p-6 border ${color.border} shadow-sm`}>
      <div className="flex items-start justify-between mb-4">
        <div className={`w-12 h-12 rounded-lg ${color.bg} ${color.text} flex items-center justify-center`}>
          {React.cloneElement(icon as React.ReactElement, { size: 24 })}
        </div>
        <span className={`text-xs font-bold px-2 py-1 rounded-full border ${statusColors[status]}`}>
          {status.toUpperCase()}
        </span>
      </div>
      <h3 className="text-3xl font-bold text-slate-900 mb-1">{value}</h3>
      <p className="text-sm font-medium text-slate-900 mb-2">{title}</p>
      <p className="text-xs text-slate-500">{subtitle}</p>
    </div>
  )
}

// Quality Metric Component
const QualityMetric: React.FC<{
  label: string
  value: number
  target: number
  unit: string
  reverse?: boolean
}> = ({ label, value, target, unit, reverse }) => {
  const isGood = reverse ? value <= target : value >= target
  const percentage = reverse 
    ? (target / value) * 100 
    : (value / target) * 100

  return (
    <div className="text-center">
      <p className="text-sm font-medium text-slate-600 mb-2">{label}</p>
      <div className="relative w-32 h-32 mx-auto">
        <svg className="transform -rotate-90" width="128" height="128">
          <circle
            cx="64"
            cy="64"
            r="56"
            stroke="#e2e8f0"
            strokeWidth="8"
            fill="none"
          />
          <circle
            cx="64"
            cy="64"
            r="56"
            stroke={isGood ? '#10b981' : '#f59e0b'}
            strokeWidth="8"
            fill="none"
            strokeDasharray={`${(percentage / 100) * 351.86} 351.86`}
            className="transition-all duration-1000"
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <p className={`text-2xl font-bold ${isGood ? 'text-emerald-600' : 'text-amber-600'}`}>
            {value}{unit}
          </p>
          <p className="text-xs text-slate-500">Target: {target}{unit}</p>
        </div>
      </div>
    </div>
  )
}

// COPQ Item Component
const COPQItem: React.FC<{
  label: string
  value: number
}> = ({ label, value }) => (
  <div className="bg-slate-50 rounded-lg p-4 border border-slate-200">
    <p className="text-xs text-slate-600 mb-1">{label}</p>
    <p className="text-xl font-bold text-slate-900">Rp {(value / 1000000).toFixed(1)}M</p>
  </div>
)
