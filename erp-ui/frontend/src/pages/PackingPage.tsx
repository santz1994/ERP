/**
 * Copyright (c) 2026 PT Quty Karunia - All Rights Reserved
 * File: PackingPage.tsx | Date: 2026-02-06
 * Purpose: Packing Department Landing Dashboard (REFACTORED)
 * Architecture: Level 2 - Module Landing Page (Dashboard → Landing → Detail)
 */

import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { format } from 'date-fns'
import { 
  Box, 
  Truck,
  CheckCircle,
  TrendingUp,
  Calendar,
  LayoutDashboard,
  Edit3,
  Package
} from 'lucide-react'
import axios from 'axios'
import { NavigationCard } from '@/components/ui/NavigationCard'
import { Card } from '@/components/ui/card'
import { WorkOrder, PackingStats } from '@/types'
import { getWorkOrderStatusBadgeClass } from '@/utils'

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'

export default function PackingPage() {
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
      console.error('Failed to fetch packing data:', error)
    } finally {
      setLoading(false)
    }
  }

  const { data: workOrders = [] } = useQuery({
    queryKey: ['packing-work-orders'],
    queryFn: async () => {
      const token = localStorage.getItem('access_token')
      const response = await axios.get(`${API_BASE}/production/packing/pending`, {
        headers: { Authorization: `Bearer ${token}` }
      })
      return response.data
    },
    refetchInterval: 30000
  })

  const stats: PackingStats = {
    today_packed: workOrders.reduce((sum: number, wo: WorkOrder) => sum + wo.output_qty, 0),
    cartons_completed: workOrders.reduce((sum: number, wo: WorkOrder) => sum + wo.cartons_packed, 0),
    active_wos: workOrders.filter((wo: WorkOrder) => wo.status === 'Running').length,
    fg_ready_ship: workOrders.filter((wo: WorkOrder) => wo.status === 'Finished').reduce((sum: number, wo: WorkOrder) => sum + wo.cartons_packed, 0)
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
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      {/* Header */}
      <div className="mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 flex items-center">
            <Box className="w-8 h-8 mr-3 text-indigo-600" />
            Packing Department
          </h1>
          <p className="text-gray-500 mt-1">
            {new Date().toLocaleDateString('id-ID', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })} • {new Date().toLocaleTimeString('id-ID', { hour: '2-digit', minute: '2-digit' })} WIB
          </p>
          <p className="text-sm text-gray-400 mt-1">
            📍 Department Landing Page • Doll + Baju Assembly → FG Carton
          </p>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <Card className="bg-white shadow-lg border-l-4 border-indigo-500">
          <div className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500 mb-1">Packed Today</p>
                <p className="text-3xl font-bold text-indigo-600">{stats.today_packed}</p>
                <p className="text-xs text-gray-400 mt-1">sets packed</p>
              </div>
              <Box className="w-12 h-12 text-indigo-400" />
            </div>
          </div>
        </Card>

        <Card className="bg-white shadow-lg border-l-4 border-green-500">
          <div className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500 mb-1">Cartons Ready</p>
                <p className="text-3xl font-bold text-green-600">{stats.cartons_completed}</p>
                <p className="text-xs text-gray-400 mt-1">cartons completed</p>
              </div>
              <Package className="w-12 h-12 text-green-400" />
            </div>
          </div>
        </Card>

        <Card className="bg-white shadow-lg border-l-4 border-blue-500">
          <div className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500 mb-1">Ready to Ship</p>
                <p className="text-3xl font-bold text-blue-600">{stats.fg_ready_ship}</p>
                <p className="text-xs text-gray-400 mt-1">cartons in Warehouse FG</p>
              </div>
              <Truck className="w-12 h-12 text-blue-400" />
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
            description="Pack sets (Doll + Baju), scan barcodes, assign week/destination, generate FG labels."
            icon={Edit3}
            link="/production/packing/input"
            color="blue"
            badge="FG Generate"
          />
          
          <NavigationCard
            title="Production Calendar"
            description="Track packing progress by week assignment, urgency-based prioritization."
            icon={Calendar}
            link="/production/calendar"
            color="green"
            badge="Timeline"
          />
          
          <NavigationCard
            title="WIP Dashboard"
            description="Monitor constraint: Doll readiness vs Baju readiness. Packing can only start when BOTH ready."
            icon={LayoutDashboard}
            link="/production/wip"
            color="purple"
            badge="Constraint Check"
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
                <Box className="w-10 h-10 text-indigo-400 mx-auto mb-2" />
                <p className="text-3xl font-bold text-indigo-600">{stats.today_packed}</p>
                <p className="text-sm text-gray-500">Sets Packed</p>
              </div>
              <div className="text-center">
                <Package className="w-10 h-10 text-green-400 mx-auto mb-2" />
                <p className="text-3xl font-bold text-green-600">{stats.cartons_completed}</p>
                <p className="text-sm text-gray-500">Cartons Done</p>
              </div>
              <div className="text-center">
                <Truck className="w-10 h-10 text-blue-400 mx-auto mb-2" />
                <p className="text-3xl font-bold text-blue-600">{stats.fg_ready_ship}</p>
                <p className="text-sm text-gray-500">Ready Ship</p>
              </div>
              <div className="text-center">
                <CheckCircle className="w-10 h-10 text-orange-400 mx-auto mb-2" />
                <p className="text-3xl font-bold text-orange-600">{stats.active_wos}</p>
                <p className="text-sm text-gray-500">Active WOs</p>
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
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Packed</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Cartons</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {recentWOs.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="px-6 py-12 text-center">
                      <Box className="w-12 h-12 text-gray-400 mx-auto mb-3" />
                      <p className="text-gray-500">No work orders yet</p>
                      <button
                        onClick={() => navigate('/production/packing/input')}
                        className="mt-4 text-indigo-600 hover:text-indigo-700 text-sm font-medium"
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
                        <div className="text-sm text-gray-900">{wo.input_qty} sets</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-indigo-600">{wo.output_qty} sets</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-green-600">{wo.cartons_packed} CTN</div>
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
      <Card className="bg-indigo-50 border-indigo-200">
        <div className="p-6">
          <h3 className="text-lg font-semibold text-indigo-900 mb-2">💡 Packing Department Guide</h3>
          <div className="text-sm text-indigo-800 space-y-1">
            <p>• <strong>Constraint Check</strong>: Can only pack when BOTH Doll (from Finishing) AND Baju (from Sewing) are ready</p>
            <p>• <strong>Week Assignment</strong>: Inherited from PO Label → determines packing priority (urgency-based)</p>
            <p>• <strong>Barcode System</strong>: Scan Doll + Scan Baju → Generate FG Barcode (1 set = 1 barcode)</p>
            <p>• <strong>FG Transfer</strong>: After carton packing → auto-transfer to Warehouse FG with carton label</p>
          </div>
        </div>
      </Card>
    </div>
  )
}
