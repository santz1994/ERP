/**
 * Copyright (c) 2026 PT Quty Karunia - All Rights Reserved
 * File: FinishingPage.tsx | Date: 2026-02-06
 * Purpose: Finishing Department Landing Dashboard (REFACTORED)
 * Architecture: Level 2 - Module Landing Page (Dashboard → Landing → Detail)
 */

import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { format } from 'date-fns'
import { 
  Package2, 
  Sparkles,
  TrendingUp,
  CheckCircle,
  Calendar,
  LayoutDashboard,
  Edit3
} from 'lucide-react'
import axios from 'axios'
import { NavigationCard } from '@/components/ui/NavigationCard'
import { Card } from '@/components/ui/card'
import { WorkOrder, FinishingStats } from '@/types'
import { getWorkOrderStatusBadgeClass } from '@/utils'

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'

export default function FinishingPage() {
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
      console.error('Failed to fetch finishing data:', error)
    } finally {
      setLoading(false)
    }
  }

  const { data: workOrders = [] } = useQuery({
    queryKey: ['finishing-work-orders'],
    queryFn: async () => {
      const token = localStorage.getItem('access_token')
      const response = await axios.get(`${API_BASE}/production/finishing/pending`, {
        headers: { Authorization: `Bearer ${token}` }
      })
      return response.data
    },
    refetchInterval: 30000
  })

  const stats: FinishingStats = {
    today_stuffed: workOrders.reduce((sum: number, wo: WorkOrder) => sum + wo.output_qty, 0),
    today_closed: workOrders.filter((wo: WorkOrder) => wo.status === 'Finished').length * 100,
    active_wos: workOrders.filter((wo: WorkOrder) => wo.status === 'Running').length,
    filling_consumption_kg: workOrders.reduce((sum: number, wo: WorkOrder) => sum + (wo.output_qty * 0.054), 0)
  }

  const recentWOs = workOrders.slice(0, 10)

  const getStatusBadgeClass = (status: string) => {
    switch (status) {
      case 'Pending': return 'bg-yellow-100 text-yellow-800'
      case 'Running': return 'bg-blue-100 text-blue-800'
      case 'Finished': return 'bg-green-100 text-green-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  if (loading && workOrders.length === 0) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      {/* Header */}
      <div className="mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 flex items-center">
            <Package2 className="w-8 h-8 mr-3 text-purple-600" />
            Finishing Department
          </h1>
          <p className="text-gray-500 mt-1">
            {new Date().toLocaleDateString('id-ID', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })} • {new Date().toLocaleTimeString('id-ID', { hour: '2-digit', minute: '2-digit' })} WIB
          </p>
          <p className="text-sm text-gray-400 mt-1">
            📍 Department Landing Page • 2-Stage Process (Stuffing + Closing)
          </p>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <Card className="bg-white shadow-lg border-l-4 border-purple-500">
          <div className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500 mb-1">Stuffed Today</p>
                <p className="text-3xl font-bold text-purple-600">{stats.today_stuffed}</p>
                <p className="text-xs text-gray-400 mt-1">bodies stuffed</p>
              </div>
              <Package2 className="w-12 h-12 text-purple-400" />
            </div>
          </div>
        </Card>

        <Card className="bg-white shadow-lg border-l-4 border-green-500">
          <div className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500 mb-1">Closed Today</p>
                <p className="text-3xl font-bold text-green-600">{stats.today_closed}</p>
                <p className="text-xs text-gray-400 mt-1">dolls finished</p>
              </div>
              <CheckCircle className="w-12 h-12 text-green-400" />
            </div>
          </div>
        </Card>

        <Card className="bg-white shadow-lg border-l-4 border-blue-500">
          <div className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500 mb-1">Filling Used</p>
                <p className="text-3xl font-bold text-blue-600">{stats.filling_consumption_kg.toFixed(1)}</p>
                <p className="text-xs text-gray-400 mt-1">kg kapas</p>
              </div>
              <Sparkles className="w-12 h-12 text-blue-400" />
            </div>
          </div>
        </Card>

        <Card className="bg-white shadow-lg border-l-4 border-orange-500">
          <div className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500 mb-1">Active Lines</p>
                <p className="text-3xl font-bold text-orange-600">{stats.active_wos}</p>
                <p className="text-xs text-gray-400 mt-1">in process</p>
              </div>
              <TrendingUp className="w-12 h-12 text-orange-400" />
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
            description="Stage 1 (Stuffing): Skin → Stuffed Body. Stage 2 (Closing): Hang tag → Finished Doll."
            icon={Edit3}
            link="/production/finishing/input"
            color="purple"
            badge="2-Stage"
          />
          
          <NavigationCard
            title="Production Calendar"
            description="Track daily progress per stage, monitor filling consumption, cumulative output."
            icon={Calendar}
            link="/production/calendar"
            color="green"
            badge="Timeline"
          />
          
          <NavigationCard
            title="WIP Dashboard"
            description="3 stock levels: Skin, Stuffed Body, Finished Doll. Demand-driven allocation."
            icon={LayoutDashboard}
            link="/production/wip"
            color="blue"
            badge="3 Stocks"
          />
        </div>
      </div>

      {/* Production Performance */}
      <div className="mb-8">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Department Performance</h2>
        <Card className="bg-white shadow-lg">
          <div className="p-6">
            <div className="grid grid-cols-2 md:grid-cols-3 gap-6">
              <div className="text-center">
                <Package2 className="w-10 h-10 text-purple-400 mx-auto mb-2" />
                <p className="text-3xl font-bold text-purple-600">{stats.today_stuffed}</p>
                <p className="text-sm text-gray-500">Stuffed Bodies</p>
                <p className="text-xs text-gray-400 mt-1">Stage 1 Output</p>
              </div>
              <div className="text-center">
                <CheckCircle className="w-10 h-10 text-green-400 mx-auto mb-2" />
                <p className="text-3xl font-bold text-green-600">{stats.today_closed}</p>
                <p className="text-sm text-gray-500">Finished Dolls</p>
                <p className="text-xs text-gray-400 mt-1">Stage 2 Output</p>
              </div>
              <div className="text-center">
                <Sparkles className="w-10 h-10 text-blue-400 mx-auto mb-2" />
                <p className="text-3xl font-bold text-blue-600">{stats.filling_consumption_kg.toFixed(1)}</p>
                <p className="text-sm text-gray-500">Filling (kg)</p>
                <p className="text-xs text-gray-400 mt-1">Material Consumption</p>
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
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Reject</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {recentWOs.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="px-6 py-12 text-center">
                      <Package2 className="w-12 h-12 text-gray-400 mx-auto mb-3" />
                      <p className="text-gray-500">No work orders yet</p>
                      <button
                        onClick={() => navigate('/production/finishing/input')}
                        className="mt-4 text-purple-600 hover:text-purple-700 text-sm font-medium"
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
                        <span className={`px-2.5 py-0.5 text-xs font-semibold rounded-full ${getStatusBadgeClass(wo.status)}`}>
                          {wo.status}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">{wo.input_qty} pcs</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-purple-600">{wo.output_qty} pcs</div>
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
      <Card className="bg-purple-50 border-purple-200">
        <div className="p-6">
          <h3 className="text-lg font-semibold text-purple-900 mb-2">💡 Finishing Department Guide</h3>
          <div className="text-sm text-purple-800 space-y-1">
            <p>• <strong>Stage 1 - Stuffing</strong>: Input Skin + Filling → Output Stuffed Body (track filling gram/pcs)</p>
            <p>• <strong>Stage 2 - Closing</strong>: Input Stuffed Body + Hang Tag → Output Finished Doll</p>
            <p>• <strong>Warehouse Finishing</strong>: Internal stock tracking (no surat jalan), demand-driven production</p>
            <p>• <strong>Final QC</strong>: Metal detector check + visual inspection before transfer to Warehouse FG</p>
          </div>
        </div>
      </Card>
    </div>
  )
}
