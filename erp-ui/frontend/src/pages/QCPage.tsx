/**
 * Copyright (c) 2026 PT Quty Karunia - All Rights Reserved
 * File: QCPage.tsx | Date: 2026-02-06
 * Purpose: QC Module Landing Dashboard (REFACTORED)
 * Architecture: Level 2 - Module Landing Page (Dashboard → Landing → Detail)
 */

import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { 
  CheckCircle, 
  XCircle, 
  BarChart3, 
  TrendingUp,
  AlertTriangle,
  Award,
  RefreshCw
} from 'lucide-react'
import { apiClient } from '@/api'
import { NavigationCard } from '@/components/ui/NavigationCard'
import { Card } from '@/components/ui/card'

interface QCInspection {
  id: number
  work_order_id: number
  type: string
  status: string
  defect_reason?: string
  inspected_by: number
  inspector_name?: string
  created_at: string
}

interface QCStats {
  total_inspections: number
  passed: number
  failed: number
  pass_rate: number
  today_inspections: number
}

const QCPage: React.FC = () => {
  const navigate = useNavigate()
  const [inspections, setInspections] = useState<QCInspection[]>([])
  const [stats, setStats] = useState<QCStats | null>(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    fetchData()
    const interval = setInterval(fetchData, 30000) // Poll every 30 seconds
    return () => clearInterval(interval)
  }, [])

  const fetchData = async () => {
    setLoading(true)
    try {
      // Fetch QC stats
      const statsRes = await apiClient.get('/quality/stats')
      setStats(statsRes.data)
      
      // Fetch recent inspections (last 10)
      const inspRes = await apiClient.get('/quality/inspections?limit=10')
      const inspData = Array.isArray(inspRes.data) ? inspRes.data : (inspRes.data?.data || [])
      setInspections(inspData)
    } catch (error) {
      console.error('Failed to fetch QC data:', error)
      setInspections([])
    } finally {
      setLoading(false)
    }
  }

  const getStatusBadgeClass = (status: string) => {
    return status === 'Pass' 
      ? 'bg-green-100 text-green-800'
      : 'bg-red-100 text-red-800'
  }

  if (loading && !stats) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600"></div>
      </div>
    )
  }

  // Calculate FPY (First Pass Yield)
  const fpy = stats ? stats.pass_rate : 0

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 flex items-center">
              <CheckCircle className="w-8 h-8 mr-3 text-green-600" />
              Quality Control
            </h1>
            <p className="text-gray-500 mt-1">
              {new Date().toLocaleDateString('id-ID', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })} • {new Date().toLocaleTimeString('id-ID', { hour: '2-digit', minute: '2-digit' })} WIB
            </p>
            <p className="text-sm text-gray-400 mt-1">
              📍 Module Landing Page • 4-Checkpoint QC System
            </p>
          </div>
        </div>
      </div>

      {/* KPI Cards */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <Card className="bg-white shadow-lg border-l-4 border-blue-500">
            <div className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-500 mb-1">Today's Inspections</p>
                  <p className="text-3xl font-bold text-gray-900">{stats.today_inspections}</p>
                  <p className="text-xs text-gray-400 mt-1">Active checks</p>
                </div>
                <CheckCircle className="w-12 h-12 text-blue-400" />
              </div>
            </div>
          </Card>

          <Card className="bg-white shadow-lg border-l-4 border-green-500">
            <div className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-500 mb-1">Pass Rate</p>
                  <p className="text-3xl font-bold text-green-600">{stats.pass_rate.toFixed(1)}%</p>
                  <p className="text-xs text-gray-400 mt-1">{stats.passed} passed</p>
                </div>
                <Award className="w-12 h-12 text-green-400" />
              </div>
            </div>
          </Card>

          <Card className="bg-white shadow-lg border-l-4 border-red-500">
            <div className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-500 mb-1">Defects This Week</p>
                  <p className="text-3xl font-bold text-red-600">{stats.failed}</p>
                  <p className="text-xs text-gray-400 mt-1">Requires attention</p>
                </div>
                <AlertTriangle className="w-12 h-12 text-red-400" />
              </div>
            </div>
          </Card>

          <Card className="bg-white shadow-lg border-l-4 border-purple-500">
            <div className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-500 mb-1">First Pass Yield</p>
                  <p className="text-3xl font-bold text-purple-600">{fpy.toFixed(1)}%</p>
                  <p className="text-xs text-gray-400 mt-1">Quality metric</p>
                </div>
                <TrendingUp className="w-12 h-12 text-purple-400" />
              </div>
            </div>
          </Card>
        </div>
      )}

      {/* Navigation Cards - CRITICAL for 3-Tier Architecture */}
      <div className="mb-8">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <NavigationCard
            title="QC Checkpoint Input"
            description="4-Checkpoint QC system: Cutting → Sewing → Finishing → Pre-Packing. Real-time defect tracking with classification."
            icon={CheckCircle}
            link="/qc/checkpoint"
            color="green"
            badge="4 Checkpoints"
          />
          
          <NavigationCard
            title="Defect Analysis"
            description="Pareto chart, root cause analysis, defect trends. Identify quality improvement opportunities."
            icon={BarChart3}
            link="/qc/defect-analysis"
            color="orange"
            badge="Analytics"
            disabled={true}
          />
          
          <NavigationCard
            title="Rework Management"
            description="Rework queue, recovery tracking, COPQ analysis. Minimize waste and improve quality."
            icon={RefreshCw}
            link="/rework/dashboard"
            color="red"
            badge="COPQ"
            disabled={false}
          />
        </div>
      </div>

      {/* Pass/Fail Trend (7 Days) */}
      {stats && (
        <div className="mb-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Quality Performance</h2>
          <Card className="bg-white shadow-lg">
            <div className="p-6">
              <div className="grid grid-cols-2 md:grid-cols-3 gap-6">
                <div className="text-center">
                  <CheckCircle className="w-10 h-10 text-green-400 mx-auto mb-2" />
                  <p className="text-3xl font-bold text-green-600">{stats.passed}</p>
                  <p className="text-sm text-gray-500">Passed</p>
                  <p className="text-xs text-gray-400 mt-1">
                    {stats.total_inspections > 0 ? ((stats.passed / stats.total_inspections) * 100).toFixed(1) : 0}% of total
                  </p>
                </div>
                <div className="text-center">
                  <XCircle className="w-10 h-10 text-red-400 mx-auto mb-2" />
                  <p className="text-3xl font-bold text-red-600">{stats.failed}</p>
                  <p className="text-sm text-gray-500">Failed</p>
                  <p className="text-xs text-gray-400 mt-1">
                    {stats.total_inspections > 0 ? ((stats.failed / stats.total_inspections) * 100).toFixed(1) : 0}% of total
                  </p>
                </div>
                <div className="text-center">
                  <BarChart3 className="w-10 h-10 text-blue-400 mx-auto mb-2" />
                  <p className="text-3xl font-bold text-blue-600">{stats.total_inspections}</p>
                  <p className="text-sm text-gray-500">Total</p>
                  <p className="text-xs text-gray-400 mt-1">All inspections</p>
                </div>
              </div>
              
              {/* Pass Rate Progress Bar */}
              <div className="mt-6">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-gray-700">Overall Pass Rate</span>
                  <span className="text-sm font-medium text-gray-900">{stats.pass_rate.toFixed(1)}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-3">
                  <div 
                    className={`h-3 rounded-full transition-all ${
                      stats.pass_rate >= 95 ? 'bg-green-500' :
                      stats.pass_rate >= 85 ? 'bg-yellow-500' :
                      'bg-red-500'
                    }`}
                    style={{ width: `${stats.pass_rate}%` }}
                  />
                </div>
                <div className="flex justify-between text-xs text-gray-500 mt-1">
                  <span>Target: 95%</span>
                  <span className={stats.pass_rate >= 95 ? 'text-green-600 font-medium' : ''}>
                    {stats.pass_rate >= 95 ? '✓ Target achieved!' : `${(95 - stats.pass_rate).toFixed(1)}% to target`}
                  </span>
                </div>
              </div>
            </div>
          </Card>
        </div>
      )}

      {/* Recent Inspections Table */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold text-gray-900">Recent Inspections</h2>
          <button
            onClick={fetchData}
            className="text-blue-600 hover:text-blue-700 text-sm font-medium flex items-center gap-1"
          >
            <RefreshCw className="w-4 h-4" />
            Refresh
          </button>
        </div>
        
        <Card className="bg-white shadow-lg overflow-hidden">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    ID
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Work Order
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Type
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Defect Reason
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Inspector
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Date
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {inspections.length === 0 ? (
                  <tr>
                    <td colSpan={7} className="px-6 py-12 text-center">
                      <CheckCircle className="w-12 h-12 text-gray-400 mx-auto mb-3" />
                      <p className="text-gray-500">No inspections yet</p>
                      <button
                        onClick={() => navigate('/qc/checkpoint')}
                        className="mt-4 text-blue-600 hover:text-blue-700 text-sm font-medium"
                      >
                        Start QC Checkpoint →
                      </button>
                    </td>
                  </tr>
                ) : (
                  inspections.map((inspection) => (
                    <tr key={inspection.id} className="hover:bg-gray-50 transition-colors">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900">{inspection.id}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">WO #{inspection.work_order_id}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">{inspection.type}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`px-2.5 py-0.5 text-xs font-semibold rounded-full ${getStatusBadgeClass(inspection.status)}`}>
                          {inspection.status}
                        </span>
                      </td>
                      <td className="px-6 py-4">
                        <div className="text-sm text-gray-900 max-w-xs truncate">
                          {inspection.defect_reason || '-'}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">
                          {inspection.inspector_name || `ID: ${inspection.inspected_by}`}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-500">
                          {new Date(inspection.created_at).toLocaleDateString('id-ID', { 
                            day: '2-digit', 
                            month: 'short', 
                            year: 'numeric' 
                          })}
                        </div>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </Card>
      </div>

      {/* Help Section */}
      <Card className="bg-green-50 border-green-200">
        <div className="p-6">
          <h3 className="text-lg font-semibold text-green-900 mb-2">💡 QC Module Guide</h3>
          <div className="text-sm text-green-800 space-y-1">
            <p>• <strong>4-Checkpoint System</strong>: Cutting → Sewing → Finishing → Pre-Packing for comprehensive quality control</p>
            <p>• <strong>Defect Classification</strong>: Classify defects as Fixable (send to Rework) or Scrap</p>
            <p>• <strong>Real-time Tracking</strong>: Monitor pass/fail rates and FPY (First Pass Yield) in real-time</p>
            <p>• <strong>Rework Integration</strong>: Defects automatically create rework requests for recovery tracking</p>
          </div>
        </div>
      </Card>
    </div>
  )
}

export default QCPage
