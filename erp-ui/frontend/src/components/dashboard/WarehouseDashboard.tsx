import React, { useEffect, useState } from 'react'
import { Package, TrendingDown, AlertCircle, CheckCircle, RefreshCw, Truck, Box, Layers } from 'lucide-react'
import { apiClient } from '@/api/client'

interface WarehouseDashboardData {
  // Stock levels
  total_material_items: number
  low_stock_count: number
  expired_materials_count: number
  fg_ready_ship: number
  
  // Movement today
  material_in_today: number
  material_out_today: number
  fg_in_today: number
  fg_out_today: number
  
  // Critical alerts
  low_stock_materials: LowStockMaterial[]
  expired_materials: ExpiredMaterial[]
  
  // FG Status
  fg_by_destination: FGByDestination[]
  
  // Stock movement heatmap data
  stock_movement_trend: StockMovementDay[]
}

interface LowStockMaterial {
  material_code: string
  material_name: string
  current_stock: number
  minimum_stock: number
  uom: string
  status: 'warning' | 'critical' | 'debt'
  percentage: number
}

interface ExpiredMaterial {
  material_code: string
  material_name: string
  quantity: number
  uom: string
  expired_date: string
  location: string
}

interface FGByDestination {
  destination: string
  week: string
  article_code: string
  ready_quantity: number
  cartons: number
}

interface StockMovementDay {
  date: string
  material_in: number
  material_out: number
  fg_in: number
  fg_out: number
}

export const WarehouseDashboard: React.FC = () => {
  const [data, setData] = useState<WarehouseDashboardData | null>(null)
  const [loading, setLoading] = useState(true)

  const fetchDashboardData = async () => {
    try {
      setLoading(true)
      const response = await apiClient.get('/dashboard/warehouse')
      setData(response.data || null)
    } catch (error) {
      console.error('Failed to fetch warehouse dashboard:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchDashboardData()
    const interval = setInterval(fetchDashboardData, 120000) // Refresh every 2 minutes
    return () => clearInterval(interval)
  }, [])

  if (loading || !data) {
    return (
      <div className="flex items-center justify-center h-64">
        <RefreshCw className="w-8 h-8 animate-spin text-blue-500" />
        <span className="ml-3 text-gray-600">Loading Warehouse Dashboard...</span>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-gray-800">Warehouse Dashboard</h2>
          <p className="text-sm text-gray-600">Stock levels, material in/out, FG ready</p>
        </div>
        <button
          onClick={fetchDashboardData}
          className="flex items-center gap-2 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
        >
          <RefreshCw className="w-4 h-4" />
          Refresh
        </button>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <WarehouseKPICard
          icon={<Package className="w-6 h-6" />}
          title="Total Material Items"
          value={data.total_material_items.toString()}
          subtitle="Active materials"
          variant="info"
        />
        <WarehouseKPICard
          icon={<AlertCircle className="w-6 h-6" />}
          title="Low Stock Alert"
          value={data.low_stock_count.toString()}
          subtitle="Needs reorder"
          variant={data.low_stock_count > 0 ? 'warning' : 'success'}
        />
        <WarehouseKPICard
          icon={<TrendingDown className="w-6 h-6" />}
          title="Expired Materials"
          value={data.expired_materials_count.toString()}
          subtitle="Requires action"
          variant={data.expired_materials_count > 0 ? 'danger' : 'success'}
        />
        <WarehouseKPICard
          icon={<CheckCircle className="w-6 h-6" />}
          title="FG Ready Ship"
          value={data.fg_ready_ship.toString()}
          subtitle="Cartons ready"
          variant="success"
        />
      </div>

      {/* Material Movement Today */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-800 mb-4">Material Movement Today</h3>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <MovementCard
            label="Material IN"
            value={data.material_in_today}
            icon={<Truck className="w-5 h-5" />}
            color="emerald"
          />
          <MovementCard
            label="Material OUT"
            value={data.material_out_today}
            icon={<Box className="w-5 h-5" />}
            color="blue"
          />
          <MovementCard
            label="FG IN"
            value={data.fg_in_today}
            icon={<Package className="w-5 h-5" />}
            color="indigo"
          />
          <MovementCard
            label="FG OUT"
            value={data.fg_out_today}
            icon={<Truck className="w-5 h-5" />}
            color="violet"
          />
        </div>
      </div>

      {/* Stock Movement Heatmap (7 days) */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-800 mb-4">Stock Movement Heatmap (7 Days)</h3>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-200">
                <th className="text-left py-2 px-3 text-sm font-semibold text-gray-600">Date</th>
                <th className="text-center py-2 px-3 text-sm font-semibold text-gray-600">Material IN</th>
                <th className="text-center py-2 px-3 text-sm font-semibold text-gray-600">Material OUT</th>
                <th className="text-center py-2 px-3 text-sm font-semibold text-gray-600">FG IN</th>
                <th className="text-center py-2 px-3 text-sm font-semibold text-gray-600">FG OUT</th>
              </tr>
            </thead>
            <tbody>
              {data.stock_movement_trend.map((day, index) => {
                const maxValue = Math.max(
                  day.material_in,
                  day.material_out,
                  day.fg_in,
                  day.fg_out
                )
                return (
                  <tr key={index} className="border-b border-gray-100 hover:bg-gray-50">
                    <td className="py-2 px-3 text-sm font-medium text-gray-700">
                      {new Date(day.date).toLocaleDateString('id-ID', { weekday: 'short', day: '2-digit', month: 'short' })}
                    </td>
                    <td className="py-2 px-3">
                      <HeatmapCell value={day.material_in} max={maxValue} color="emerald" />
                    </td>
                    <td className="py-2 px-3">
                      <HeatmapCell value={day.material_out} max={maxValue} color="blue" />
                    </td>
                    <td className="py-2 px-3">
                      <HeatmapCell value={day.fg_in} max={maxValue} color="indigo" />
                    </td>
                    <td className="py-2 px-3">
                      <HeatmapCell value={day.fg_out} max={maxValue} color="violet" />
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Low Stock Materials Alert */}
      {data.low_stock_materials.length > 0 && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-800">Low Stock Materials (Top 5)</h3>
            <span className="px-3 py-1 bg-amber-100 text-amber-700 text-sm font-medium rounded-full">
              {data.low_stock_count} Total
            </span>
          </div>
          <div className="space-y-3">
            {data.low_stock_materials.slice(0, 5).map((material) => (
              <div key={material.material_code} className="p-3 border border-gray-200 rounded-lg">
                <div className="flex justify-between items-start mb-2">
                  <div>
                    <p className="font-medium text-gray-800">{material.material_code}</p>
                    <p className="text-sm text-gray-600">{material.material_name}</p>
                  </div>
                  <StatusBadge status={material.status} />
                </div>
                <div className="flex justify-between items-center text-sm">
                  <span className="text-gray-600">
                    Stock: {material.current_stock} {material.uom} / Min: {material.minimum_stock} {material.uom}
                  </span>
                  <span className={`font-semibold ${
                    material.status === 'debt' ? 'text-black' :
                    material.status === 'critical' ? 'text-rose-600' : 'text-amber-600'
                  }`}>
                    {material.percentage.toFixed(0)}%
                  </span>
                </div>
                <div className="mt-2 h-2 bg-gray-200 rounded-full overflow-hidden">
                  <div
                    className={`h-full ${
                      material.status === 'debt' ? 'bg-black' :
                      material.status === 'critical' ? 'bg-rose-500' : 'bg-amber-500'
                    }`}
                    style={{ width: `${Math.min(material.percentage, 100)}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Expired Materials Alert */}
      {data.expired_materials.length > 0 && (
        <div className="bg-white rounded-xl shadow-sm border border-rose-200 p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-rose-800">Expired Materials</h3>
            <span className="px-3 py-1 bg-rose-100 text-rose-700 text-sm font-medium rounded-full">
              {data.expired_materials_count} Items
            </span>
          </div>
          <div className="space-y-2">
            {data.expired_materials.map((material, index) => (
              <div key={index} className="flex justify-between items-center p-3 bg-rose-50 rounded-lg">
                <div>
                  <p className="font-medium text-gray-800">{material.material_code} - {material.material_name}</p>
                  <p className="text-sm text-gray-600">
                    Location: {material.location} • Expired: {new Date(material.expired_date).toLocaleDateString('id-ID')}
                  </p>
                </div>
                <div className="text-right">
                  <p className="font-semibold text-rose-600">{material.quantity} {material.uom}</p>
                  <button className="text-sm text-rose-600 hover:underline">Mark for disposal</button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* FG Ready by Destination */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-800 mb-4">FG Ready to Ship (by Destination)</h3>
        <div className="space-y-3">
          {data.fg_by_destination.map((fg, index) => (
            <div key={index} className="flex justify-between items-center p-3 bg-emerald-50 rounded-lg border border-emerald-200">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-emerald-100 rounded-lg">
                  <Layers className="w-5 h-5 text-emerald-600" />
                </div>
                <div>
                  <p className="font-medium text-gray-800">{fg.destination}</p>
                  <p className="text-sm text-gray-600">
                    Week {fg.week} • {fg.article_code}
                  </p>
                </div>
              </div>
              <div className="text-right">
                <p className="text-lg font-bold text-emerald-600">{fg.ready_quantity} pcs</p>
                <p className="text-sm text-gray-600">{fg.cartons} cartons</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Quick Actions */}
      <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl shadow-sm border border-blue-200 p-6">
        <h3 className="text-lg font-semibold text-gray-800 mb-4">Quick Actions</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          <button className="flex items-center gap-3 p-3 bg-white border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
            <Truck className="w-5 h-5 text-blue-600" />
            <span className="font-medium text-gray-700">Material Receipt</span>
          </button>
          <button className="flex items-center gap-3 p-3 bg-white border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
            <Box className="w-5 h-5 text-emerald-600" />
            <span className="font-medium text-gray-700">Stock Adjustment</span>
          </button>
          <button className="flex items-center gap-3 p-3 bg-white border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
            <Package className="w-5 h-5 text-violet-600" />
            <span className="font-medium text-gray-700">FG Shipment</span>
          </button>
        </div>
      </div>
    </div>
  )
}

// Sub-components

interface WarehouseKPICardProps {
  icon: React.ReactNode
  title: string
  value: string
  subtitle: string
  variant: 'info' | 'success' | 'warning' | 'danger'
}

const WarehouseKPICard: React.FC<WarehouseKPICardProps> = ({ icon, title, value, subtitle, variant }) => {
  const variantColors = {
    info: 'from-blue-500 to-cyan-600',
    success: 'from-emerald-500 to-green-600',
    warning: 'from-amber-500 to-orange-600',
    danger: 'from-rose-500 to-red-600'
  }

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-5 hover:shadow-md transition-shadow">
      <div className={`inline-flex p-2 rounded-lg bg-gradient-to-br ${variantColors[variant]} mb-3`}>
        <div className="text-white">{icon}</div>
      </div>
      <h3 className="text-sm font-medium text-gray-600 mb-1">{title}</h3>
      <p className="text-3xl font-bold text-gray-900 mb-1">{value}</p>
      <p className="text-xs text-gray-500">{subtitle}</p>
    </div>
  )
}

interface MovementCardProps {
  label: string
  value: number
  icon: React.ReactNode
  color: 'emerald' | 'blue' | 'indigo' | 'violet'
}

const MovementCard: React.FC<MovementCardProps> = ({ label, value, icon, color }) => {
  const colorClasses = {
    emerald: 'bg-emerald-100 text-emerald-600',
    blue: 'bg-blue-100 text-blue-600',
    indigo: 'bg-indigo-100 text-indigo-600',
    violet: 'bg-violet-100 text-violet-600'
  }

  return (
    <div className="text-center p-4 bg-gray-50 rounded-lg">
      <div className={`inline-flex p-2 rounded-lg ${colorClasses[color]} mb-2`}>
        {icon}
      </div>
      <p className="text-sm font-medium text-gray-600 mb-1">{label}</p>
      <p className="text-2xl font-bold text-gray-900">{value}</p>
    </div>
  )
}

interface HeatmapCellProps {
  value: number
  max: number
  color: 'emerald' | 'blue' | 'indigo' | 'violet'
}

const HeatmapCell: React.FC<HeatmapCellProps> = ({ value, max, color }) => {
  const intensity = max > 0 ? (value / max) * 100 : 0
  
  const colorClasses = {
    emerald: 'bg-emerald-500',
    blue: 'bg-blue-500',
    indigo: 'bg-indigo-500',
    violet: 'bg-violet-500'
  }

  return (
    <div className="flex items-center justify-center gap-2">
      <div className="relative w-full max-w-[80px] h-6 bg-gray-100 rounded">
        <div
          className={`absolute inset-0 ${colorClasses[color]} rounded transition-all`}
          style={{ width: `${intensity}%`, opacity: 0.3 + (intensity / 100) * 0.7 }}
        />
      </div>
      <span className="text-sm font-medium text-gray-700 min-w-[40px]">{value}</span>
    </div>
  )
}

interface StatusBadgeProps {
  status: 'warning' | 'critical' | 'debt'
}

const StatusBadge: React.FC<StatusBadgeProps> = ({ status }) => {
  const statusConfig = {
    warning: { label: 'Low', bg: 'bg-amber-100', text: 'text-amber-700' },
    critical: { label: 'Critical', bg: 'bg-rose-100', text: 'text-rose-700' },
    debt: { label: 'DEBT', bg: 'bg-gray-900', text: 'text-white' }
  }

  const config = statusConfig[status]

  return (
    <span className={`px-2 py-1 ${config.bg} ${config.text} text-xs font-semibold rounded`}>
      {config.label}
    </span>
  )
}
