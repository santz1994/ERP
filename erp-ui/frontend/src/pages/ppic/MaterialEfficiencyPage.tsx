/**
 * Copyright (c) 2026 PT Quty Karunia - All Rights Reserved
 * File: MaterialEfficiencyPage.tsx
 * Purpose: Material Efficiency Report — BOM planned qty vs actual issued qty
 */

import React, { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { api } from '@/api'
import { Card } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import {
  BarChart3,
  TrendingUp,
  TrendingDown,
  AlertTriangle,
  CheckCircle,
  RefreshCw,
  Package,
} from 'lucide-react'
import { formatNumber, cn } from '@/lib/utils'

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface EfficiencyItem {
  wo_id: number
  wo_reference: string
  department: string
  material_code: string
  material_name: string
  planned_qty: number
  actual_qty: number
  efficiency_pct: number | null
  variance: number
  status: 'EFFICIENT' | 'OVER_USED' | 'UNDER_USED' | 'OK' | 'NO_DATA'
}

interface EfficiencySummary {
  total_materials: number
  total_with_data: number
  avg_efficiency_pct: number
  over_used_count: number
  under_used_count: number
}

interface EfficiencyReport {
  items: EfficiencyItem[]
  summary: EfficiencySummary
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

const statusBadge = (status: EfficiencyItem['status'], effPct: number | null) => {
  switch (status) {
    case 'EFFICIENT':
      return <Badge className="bg-green-600 text-white">Efficient</Badge>
    case 'OVER_USED':
      return <Badge className="bg-red-600 text-white">Over-used</Badge>
    case 'UNDER_USED':
      return <Badge className="bg-blue-600 text-white">Under-used</Badge>
    case 'NO_DATA':
      return <Badge variant="outline" className="text-gray-500">No Data</Badge>
    default:
      return <Badge className="bg-yellow-600 text-white">OK</Badge>
  }
}

const efficiencyColor = (pct: number | null) => {
  if (pct === null) return 'text-gray-400'
  if (pct >= 95 && pct <= 105) return 'text-green-600'
  if (pct < 85 || pct > 115) return 'text-red-600'
  return 'text-yellow-600'
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

const MaterialEfficiencyPage: React.FC = () => {
  const [moId, setMoId] = useState('')
  const [woId, setWoId] = useState('')
  const [dept, setDept] = useState('')
  const [filters, setFilters] = useState<{ mo_id?: number; wo_id?: number; dept?: string }>({})

  const { data, isLoading, isFetching, refetch } = useQuery<EfficiencyReport>({
    queryKey: ['material-efficiency', filters],
    queryFn: () => api.ppic.getMaterialEfficiency(filters),
    enabled: Object.keys(filters).length > 0,
  })

  const handleApply = () => {
    const f: typeof filters = {}
    if (moId) f.mo_id = parseInt(moId)
    if (woId) f.wo_id = parseInt(woId)
    if (dept) f.dept = dept
    setFilters(f)
  }

  const handleClear = () => {
    setMoId('')
    setWoId('')
    setDept('')
    setFilters({})
  }

  const summary = data?.summary
  const items = data?.items || []

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
          <BarChart3 className="w-8 h-8 text-blue-600" />
          Material Efficiency Report
        </h1>
        <p className="text-gray-500 mt-1">
          Compare BOM planned quantities vs actual material issued per SPK
        </p>
      </div>

      {/* Filter Card */}
      <Card className="p-6 mb-6 bg-white shadow">
        <h2 className="text-lg font-semibold mb-4">Filters</h2>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">MO ID</label>
            <input
              type="number"
              value={moId}
              onChange={e => setMoId(e.target.value)}
              placeholder="e.g. 42"
              className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Work Order ID</label>
            <input
              type="number"
              value={woId}
              onChange={e => setWoId(e.target.value)}
              placeholder="e.g. 101"
              className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Department</label>
            <select
              value={dept}
              onChange={e => setDept(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">All Departments</option>
              <option value="CUTTING">Cutting</option>
              <option value="EMBROIDERY">Embroidery</option>
              <option value="SEWING">Sewing</option>
              <option value="FINISHING">Finishing</option>
              <option value="PACKING">Packing</option>
            </select>
          </div>
          <div className="flex items-end gap-2">
            <button
              onClick={handleApply}
              disabled={isLoading || isFetching}
              className="flex-1 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md text-sm font-medium disabled:opacity-50"
            >
              {isFetching ? 'Loading...' : 'Apply'}
            </button>
            <button
              onClick={handleClear}
              className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium hover:bg-gray-50"
            >
              Clear
            </button>
          </div>
        </div>
      </Card>

      {/* Summary KPIs */}
      {summary && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          <Card className="p-5 border-l-4 border-blue-500 bg-white shadow">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Total Materials</p>
                <p className="text-3xl font-bold text-gray-900">{summary.total_materials}</p>
                <p className="text-xs text-gray-400 mt-1">{summary.total_with_data} with data</p>
              </div>
              <Package className="w-10 h-10 text-blue-400" />
            </div>
          </Card>

          <Card className="p-5 border-l-4 border-green-500 bg-white shadow">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Avg Efficiency</p>
                <p className={cn('text-3xl font-bold', efficiencyColor(summary.avg_efficiency_pct))}>
                  {summary.avg_efficiency_pct.toFixed(1)}%
                </p>
                <p className="text-xs text-gray-400 mt-1">Planned / Actual</p>
              </div>
              <TrendingUp className="w-10 h-10 text-green-400" />
            </div>
          </Card>

          <Card className="p-5 border-l-4 border-red-500 bg-white shadow">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Over-used</p>
                <p className="text-3xl font-bold text-red-600">{summary.over_used_count}</p>
                <p className="text-xs text-gray-400 mt-1">materials</p>
              </div>
              <TrendingDown className="w-10 h-10 text-red-400" />
            </div>
          </Card>

          <Card className="p-5 border-l-4 border-yellow-500 bg-white shadow">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Under-used</p>
                <p className="text-3xl font-bold text-yellow-600">{summary.under_used_count}</p>
                <p className="text-xs text-gray-400 mt-1">materials</p>
              </div>
              <AlertTriangle className="w-10 h-10 text-yellow-400" />
            </div>
          </Card>
        </div>
      )}

      {/* Table */}
      <Card className="bg-white shadow overflow-hidden">
        <div className="flex items-center justify-between px-6 py-4 border-b">
          <h2 className="text-lg font-semibold text-gray-900">
            Material Efficiency Details
          </h2>
          <button
            onClick={() => refetch()}
            className="flex items-center gap-1 text-blue-600 hover:text-blue-700 text-sm font-medium"
          >
            <RefreshCw className="w-4 h-4" />
            Refresh
          </button>
        </div>

        {Object.keys(filters).length === 0 ? (
          <div className="p-12 text-center">
            <BarChart3 className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-500 text-lg">Apply filters to load efficiency data</p>
            <p className="text-gray-400 text-sm mt-1">Select an MO, Work Order, or Department above</p>
          </div>
        ) : isLoading ? (
          <div className="p-12 text-center">
            <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-600 mx-auto" />
            <p className="text-gray-500 mt-4">Calculating efficiency...</p>
          </div>
        ) : items.length === 0 ? (
          <div className="p-12 text-center">
            <CheckCircle className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-500">No data found for selected filters</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200 text-sm">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">SPK Ref</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Dept</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Material Code</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Material Name</th>
                  <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Planned Qty</th>
                  <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Actual Qty</th>
                  <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Efficiency %</th>
                  <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Variance</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {items.map((item, idx) => (
                  <tr
                    key={`${item.wo_id}-${item.material_code}-${idx}`}
                    className={cn(
                      'hover:bg-gray-50 transition-colors',
                      item.status === 'OVER_USED' ? 'bg-red-50' :
                      item.status === 'EFFICIENT' ? 'bg-green-50' : ''
                    )}
                  >
                    <td className="px-4 py-3 font-medium text-gray-900">{item.wo_reference}</td>
                    <td className="px-4 py-3 text-gray-600">{item.department}</td>
                    <td className="px-4 py-3 font-mono text-xs text-gray-700">{item.material_code}</td>
                    <td className="px-4 py-3 text-gray-700 max-w-xs truncate">{item.material_name}</td>
                    <td className="px-4 py-3 text-right text-gray-900">{formatNumber(item.planned_qty)}</td>
                    <td className="px-4 py-3 text-right text-gray-900">{formatNumber(item.actual_qty)}</td>
                    <td className={cn('px-4 py-3 text-right font-semibold', efficiencyColor(item.efficiency_pct))}>
                      {item.efficiency_pct !== null ? `${item.efficiency_pct.toFixed(1)}%` : '—'}
                    </td>
                    <td className={cn(
                      'px-4 py-3 text-right font-medium',
                      item.variance > 0 ? 'text-red-600' : item.variance < 0 ? 'text-blue-600' : 'text-gray-600'
                    )}>
                      {item.variance > 0 ? '+' : ''}{formatNumber(item.variance)}
                    </td>
                    <td className="px-4 py-3">
                      {statusBadge(item.status, item.efficiency_pct)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Card>

      {/* Legend */}
      <Card className="mt-6 p-5 bg-blue-50 border-blue-200">
        <h3 className="font-semibold text-blue-900 mb-3">📖 How to read this report</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-sm text-blue-800">
          <p>• <strong>Planned Qty</strong>: BOM qty × SPK target qty (incl. wastage%)</p>
          <p>• <strong>Actual Qty</strong>: Total StockMoves issued for that SPK (DONE only)</p>
          <p>• <strong>Efficiency %</strong>: Planned ÷ Actual × 100. Target: 95–105%</p>
          <p>• <strong>Variance</strong>: Actual − Planned. Positive = over-used material</p>
          <div>• <Badge className="bg-green-600 text-white mr-1">Efficient</Badge>: 95–105% range</div>
          <div>• <Badge className="bg-red-600 text-white mr-1">Over-used</Badge>: Actual &gt; Planned</div>
          <div>• <Badge className="bg-blue-600 text-white mr-1">Under-used</Badge>: Actual much less than planned</div>
          <div>• <Badge variant="outline" className="mr-1">No Data</Badge>: No StockMoves recorded yet</div>
        </div>
      </Card>
    </div>
  )
}

export default MaterialEfficiencyPage
