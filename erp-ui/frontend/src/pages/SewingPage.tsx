/**
 * Copyright (c) 2026 PT Quty Karunia - All Rights Reserved
 * File: SewingPage.tsx | Date: 2026-02-06
 * Purpose: Sewing Department Landing Dashboard (REFACTORED)
 * Architecture: Level 2 - Module Landing Page (Dashboard → Landing → Detail)
 */

import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { format } from 'date-fns'
import { 
  Shirt, 
  CheckSquare,
  TrendingUp,
 AlertTriangle,
  Tag,
  Calendar,
  LayoutDashboard,
  Edit3
} from 'lucide-react'
import axios from 'axios'
import { NavigationCard } from '@/components/ui/NavigationCard'
import { Card } from '@/components/ui/card'
import { WorkOrder, SewingStats } from '@/types'
import { getWorkOrderStatusBadgeClass } from '@/utils'

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'

export default function SewingPage() {
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    fetchData()
    const interval = setInterval(fetchData, 30000)
    return () => clearInterval(interval)
  }, [])

  const fetchData = async () => {
    setLoading(true)
    try {
      await new Promise(resolve => setTimeout(resolve, 500))
    } catch (error) {
      console.error('Failed to fetch sewing data:', error)
    } finally {
      setLoading(false)
    }
  }

  const { data: workOrders = [] } = useQuery({
    queryKey: ['sewing-work-orders'],
    queryFn: async () => {
      const token = localStorage.getItem('access_token')
      const response = await axios.get(`${API_BASE}/production/sewing/pending`, {
        headers: { Authorization: `Bearer ${token}` }
      })
      return response.data
    },
    refetchInterval: 30000
  })

  const stats: SewingStats = {
    today_output: workOrders.reduce((sum: number, wo: WorkOrder) => sum + wo.output_qty, 0),
    active_wos: workOrders.filter((wo: WorkOrder) => wo.status === 'Running').length,
    completed_today: workOrders.filter((wo: WorkOrder) => wo.status === 'Finished').length,
    inline_qc_rate: workOrders.length > 0
      ? (workOrders.reduce((sum: number, wo: WorkOrder) => sum + wo.output_qty, 0) /
         workOrders.reduce((sum: number, wo: WorkOrder) => sum + wo.input_qty, 0) * 100)
      : 0,
    defect_rate: workOrders.length > 0
      ? (workOrders.reduce((sum: number, wo: WorkOrder) => sum + wo.reject_qty, 0) /
         workOrders.reduce((sum: number, wo: WorkOrder) => sum + wo.output_qty, 0) * 100)
      : 0
  }

  const recentWOs = workOrders.slice(0, 10)

  if (loading && workOrders.length === 0) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-orange-600"></div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      {/* Header */}
      <div className="mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 flex items-center">
            <Shirt className="w-8 h-8 mr-3 text-orange-600" />
            Sewing Department
          </h1>
          <p className="text-gray-500 mt-1">
            {new Date().toLocaleDateString('id-ID', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })} • {new Date().toLocaleTimeString('id-ID', { hour: '2-digit', minute: '2-digit' })} WIB
          </p>
          <p className="text-sm text-gray-400 mt-1">
            📍 Department Landing Page • 2 Parallel Streams (Body + Baju)
          </p>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <Card className="bg-white shadow-lg border-l-4 border-orange-500">
          <div className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500 mb-1">Today's Output</p>
                <p className="text-3xl font-bold text-orange-600">{stats.today_output}</p>
                <p className="text-xs text-gray-400 mt-1">pieces sewn</p>
              </div>
              <Shirt className="w-12 h-12 text-orange-400" />
            </div>
          </div>
        </Card>

        <Card className="bg-white shadow-lg border-l-4 border-green-500">
          <div className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500 mb-1">Inline QC Rate</p>
                <p className="text-3xl font-bold text-green-600">{stats.inline_qc_rate.toFixed(1)}%</p>
                <p className="text-xs text-gray-400 mt-1">pass rate</p>
              </div>
              <CheckSquare className="w-12 h-12 text-green-400" />
            </div>
          </div>
        </Card>

        <Card className="bg-white shadow-lg border-l-4 border-red-500">
          <div className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500 mb-1">Defect Rate</p>
                <p className="text-3xl font-bold text-red-600">{stats.defect_rate.toFixed(1)}%</p>
                <p className="text-xs text-gray-400 mt-1">vs output</p>
              </div>
              <AlertTriangle className="w-12 h-12 text-red-400" />
            </div>
          </div>
        </Card>

        <Card className="bg-white shadow-lg border-l-4 border-purple-500">
          <div className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500 mb-1">Active Lines</p>
                <p className="text-3xl font-bold text-purple-600">{stats.active_wos}</p>
                <p className="text-xs text-gray-400 mt-1">{stats.completed_today} completed</p>
              </div>
              <Tag className="w-12 h-12 text-purple-400" />
            </div>
          </div>
        </Card>
      </div>

      {/* Navigation Cards */}
      <div className="mb-8">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <NavigationCard
            title="Input Production"
            description="Record daily sewing output: Body stream, Baju stream. Inline QC with defect classification."
            icon={Edit3}
            link="/production/sewing/input"
            color="orange"
            badge="2 Streams"
          />
          
          <NavigationCard
            title="Production Calendar"
            description="Track progress by date, monitor parallel streams, cumulative achievement tracking."
            icon={Calendar}
            link="/production/calendar"
            color="green"
            badge="Timeline"
          />
          
          <NavigationCard
            title="WIP Dashboard"
            description="Real-time tracking: Body readiness, Baju readiness for final assembly (Packing)."
            icon={LayoutDashboard}
            link="/production/wip"
            color="purple"
            badge="Real-time"
          />
        </div>
      </div>

      {/* Production Performance */}
      <div className="mb-8">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Department Performance</h2>
        <Card className="bg-white shadow-lg">
          <div className="p-6">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
              <div className="text-center">
                <CheckSquare className="w-10 h-10 text-green-400 mx-auto mb-2" />
                <p className="text-3xl font-bold text-green-600">{stats.completed_today}</p>
                <p className="text-sm text-gray-500">Completed WOs</p>
              </div>
              <div className="text-center">
                <Tag className="w-10 h-10 text-orange-400 mx-auto mb-2" />
                <p className="text-3xl font-bold text-orange-600">{stats.active_wos}</p>
                <p className="text-sm text-gray-500">Active Lines</p>
              </div>
              <div className="text-center">
                <TrendingUp className="w-10 h-10 text-purple-400 mx-auto mb-2" />
                <p className="text-3xl font-bold text-purple-600">{stats.inline_qc_rate.toFixed(0)}%</p>
                <p className="text-sm text-gray-500">QC Pass Rate</p>
              </div>
              <div className="text-center">
                <Shirt className="w-10 h-10 text-blue-400 mx-auto mb-2" />
                <p className="text-3xl font-bold text-blue-600">{stats.today_output}</p>
                <p className="text-sm text-gray-500">Total Output</p>
              </div>
            </div>
          </div>
        </Card>
      </div>

      {/* Recent Work Orders Table */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold text-gray-900">Recent Work Orders</h2>
        </div>
        
        <Card className="bg-white shadow-lg overflow-hidden">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">WO ID</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">MO ID</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Target</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Output</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Defects</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {recentWOs.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="px-6 py-12 text-center">
                      <Shirt className="w-12 h-12 text-gray-400 mx-auto mb-3" />
                      <p className="text-gray-500">No work orders yet</p>
                      <button
                        onClick={() => navigate('/production/sewing/input')}
                        className="mt-4 text-orange-600 hover:text-orange-700 text-sm font-medium"
                      >
                        Start Production Input →
                      </button>
                    </td>
                  </tr>
                ) : (
                  recentWOs.map((wo: WorkOrder) => (
                    <tr key={wo.id} className="hover:bg-gray-50 transition-colors">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900">WO #{wo.id}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">MO #{wo.mo_id}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`px-2.5 py-0.5 text-xs font-semibold rounded-full ${getWorkOrderStatusBadgeClass(wo.status)}`}>
                          {wo.status}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">{wo.input_qty} pcs</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-orange-600">{wo.output_qty} pcs</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-red-600">{wo.reject_qty} pcs</div>
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
      <Card className="bg-orange-50 border-orange-200">
        <div className="p-6">
          <h3 className="text-lg font-semibold text-orange-900 mb-2">💡 Sewing Department Guide</h3>
          <div className="text-sm text-orange-800 space-y-1">
            <p>• <strong>2 Parallel Streams</strong>: Body sewing & Baju sewing run simultaneously (independent progress tracking)</p>
            <p>• <strong>Inline QC</strong>: Defects classified during sewing → Send to Rework or Scrap immediately</p>
            <p>• <strong>Constraint Check</strong>: Packing can only start when BOTH streams reach target (OR constraint)</p>
            <p>• <strong>Thread Consumption</strong>: System tracks thread usage per piece for material costing</p>
          </div>
        </div>
      </Card>
    </div>
  )
}
