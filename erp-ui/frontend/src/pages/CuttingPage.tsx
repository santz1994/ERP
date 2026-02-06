/**
 * Copyright (c) 2026 PT Quty Karunia - All Rights Reserved
 * File: CuttingPage.tsx | Date: 2026-02-06
 * Purpose: Cutting Department Landing Dashboard (REFACTORED)
 * Architecture: Level 2 - Module Landing Page (Dashboard → Landing → Detail)
 */

import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { format } from 'date-fns'
import { 
  Scissors, 
  CheckCircle, 
  Clock, 
  Package,
  TrendingUp,
  Calendar,
  LayoutDashboard,
  Edit3
} from 'lucide-react'
import axios from 'axios'
import { NavigationCard } from '@/components/ui/NavigationCard'
import { Card } from '@/components/ui/card'
import { WorkOrder, CuttingStats } from '@/types'
import { getWorkOrderStatusBadgeClass } from '@/utils'

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'

export default function CuttingPage() {
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    fetchData()
    const interval = setInterval(fetchData, 30000) // Poll every 30 seconds
    return () => clearInterval(interval)
  }, [])

  const fetchData = async () => {
    setLoading(true)
    try {
      // Placeholder - will be implemented with actual API
      await new Promise(resolve => setTimeout(resolve, 500))
    } catch (error) {
      console.error('Failed to fetch cutting data:', error)
    } finally {
      setLoading(false)
    }
  }

  // Fetch work orders for recent activity
  const { data: workOrders = [] } = useQuery({
    queryKey: ['cutting-work-orders'],
    queryFn: async () => {
      const token = localStorage.getItem('access_token')
      const response = await axios.get(`${API_BASE}/production/cutting/pending`, {
        headers: { Authorization: `Bearer ${token}` }
      })
      return response.data
    },
    refetchInterval: 30000
  })

  // Calculate stats
  const stats: CuttingStats = {
    today_output: workOrders.reduce((sum: number, wo: WorkOrder) => sum + wo.output_qty, 0),
    active_wos: workOrders.filter((wo: WorkOrder) => wo.status === 'Running').length,
    completed_today: workOrders.filter((wo: WorkOrder) => wo.status === 'Finished').length,
    efficiency_rate: workOrders.length > 0 
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
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 flex items-center">
              <Scissors className="w-8 h-8 mr-3 text-blue-600" />
              Cutting Department
            </h1>
            <p className="text-gray-500 mt-1">
              {new Date().toLocaleDateString('id-ID', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })} • {new Date().toLocaleTimeString('id-ID', { hour: '2-digit', minute: '2-digit' })} WIB
            </p>
            <p className="text-sm text-gray-400 mt-1">
              📍 Department Landing Page • Material ↔ Pieces Conversion
            </p>
          </div>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <Card className="bg-white shadow-lg border-l-4 border-blue-500">
          <div className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500 mb-1">Today's Output</p>
                <p className="text-3xl font-bold text-blue-600">{stats.today_output}</p>
                <p className="text-xs text-gray-400 mt-1">pieces cut</p>
              </div>
              <Scissors className="w-12 h-12 text-blue-400" />
            </div>
          </div>
        </Card>

        <Card className="bg-white shadow-lg border-l-4 border-green-500">
          <div className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500 mb-1">Efficiency Rate</p>
                <p className="text-3xl font-bold text-green-600">{stats.efficiency_rate.toFixed(1)}%</p>
                <p className="text-xs text-gray-400 mt-1">output vs target</p>
              </div>
              <TrendingUp className="w-12 h-12 text-green-400" />
            </div>
          </div>
        </Card>

        <Card className="bg-white shadow-lg border-l-4 border-red-500">
          <div className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500 mb-1">Defect Rate</p>
                <p className="text-3xl font-bold text-red-600">{stats.defect_rate.toFixed(1)}%</p>
                <p className="text-xs text-gray-400 mt-1">reject vs output</p>
              </div>
              <Package className="w-12 h-12 text-red-400" />
            </div>
          </div>
        </Card>

        <Card className="bg-white shadow-lg border-l-4 border-purple-500">
          <div className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500 mb-1">Active Work Orders</p>
                <p className="text-3xl font-bold text-purple-600">{stats.active_wos}</p>
                <p className="text-xs text-gray-400 mt-1">{stats.completed_today} completed</p>
              </div>
              <Clock className="w-12 h-12 text-purple-400" />
            </div>
          </div>
        </Card>
      </div>

      {/* Navigation Cards - CRITICAL for 3-Tier Architecture */}
      <div className="mb-8">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <NavigationCard
            title="Input Production"
            description="Record daily cutting production: input fabric yards, output pieces, material consumption tracking."
            icon={Edit3}
            link="/production/cutting/input"
            color="blue"
            badge="Daily Entry"
          />
          
          <NavigationCard
            title="Production Calendar"
            description="View production schedule, track progress by date, monitor cumulative achievement vs target."
            icon={Calendar}
            link="/production/calendar"
            color="green"
            badge="Timeline"
          />
          
          <NavigationCard
            title="WIP Dashboard"
            description="Real-time Work-In-Progress tracking across all departments. Monitor material flow and bottlenecks."
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
                <CheckCircle className="w-10 h-10 text-green-400 mx-auto mb-2" />
                <p className="text-3xl font-bold text-green-600">{stats.completed_today}</p>
                <p className="text-sm text-gray-500">Completed WOs</p>
              </div>
              <div className="text-center">
                <Clock className="w-10 h-10 text-blue-400 mx-auto mb-2" />
                <p className="text-3xl font-bold text-blue-600">{stats.active_wos}</p>
                <p className="text-sm text-gray-500">Active WOs</p>
              </div>
              <div className="text-center">
                <TrendingUp className="w-10 h-10 text-purple-400 mx-auto mb-2" />
                <p className="text-3xl font-bold text-purple-600">{stats.efficiency_rate.toFixed(0)}%</p>
                <p className="text-sm text-gray-500">Efficiency</p>
              </div>
              <div className="text-center">
                <Package className="w-10 h-10 text-orange-400 mx-auto mb-2" />
                <p className="text-3xl font-bold text-orange-600">{stats.today_output}</p>
                <p className="text-sm text-gray-500">Total Output</p>
              </div>
            </div>
            
            {/* Efficiency Progress Bar */}
            <div className="mt-6">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-gray-700">Overall Efficiency</span>
                <span className="text-sm font-medium text-gray-900">{stats.efficiency_rate.toFixed(1)}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-3">
                <div 
                  className={`h-3 rounded-full transition-all ${
                    stats.efficiency_rate >= 95 ? 'bg-green-500' :
                    stats.efficiency_rate >= 85 ? 'bg-yellow-500' :
                    'bg-red-500'
                  }`}
                  style={{ width: `${Math.min(stats.efficiency_rate, 100)}%` }}
                />
              </div>
              <div className="flex justify-between text-xs text-gray-500 mt-1">
                <span>Target: 95%</span>
                <span className={stats.efficiency_rate >= 95 ? 'text-green-600 font-medium' : ''}>
                  {stats.efficiency_rate >= 95 ? '✓ Target achieved!' : `${(95 - stats.efficiency_rate).toFixed(1)}% to target`}
                </span>
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
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    WO ID
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    MO ID
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Target
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Output
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Reject
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Started
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {recentWOs.length === 0 ? (
                  <tr>
                    <td colSpan={7} className="px-6 py-12 text-center">
                      <Scissors className="w-12 h-12 text-gray-400 mx-auto mb-3" />
                      <p className="text-gray-500">No work orders yet</p>
                      <button
                        onClick={() => navigate('/production/cutting/input')}
                        className="mt-4 text-blue-600 hover:text-blue-700 text-sm font-medium"
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
                        <div className="text-sm font-medium text-blue-600">{wo.output_qty} pcs</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-red-600">{wo.reject_qty} pcs</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-500">
                          {wo.start_time ? format(new Date(wo.start_time), 'dd MMM HH:mm') : '-'}
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
      <Card className="bg-blue-50 border-blue-200">
        <div className="p-6">
          <h3 className="text-lg font-semibold text-blue-900 mb-2">💡 Cutting Department Guide</h3>
          <div className="text-sm text-blue-800 space-y-1">
            <p>• <strong>Material Conversion</strong>: System auto-converts fabric yards → pieces using BOM marker data</p>
            <p>• <strong>Buffer System</strong>: +10% cutting target for waste anticipation (configured in BOM)</p>
            <p>• <strong>Daily Input</strong>: Record production daily via calendar view, cumulative tracking automatic</p>
            <p>• <strong>Quality Tracking</strong>: Classify rejects as Fixable ( → Rework) or Scrap immediately</p>
          </div>
        </div>
      </Card>
    </div>
  )
}
