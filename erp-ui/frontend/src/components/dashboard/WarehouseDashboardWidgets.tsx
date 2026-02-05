/**
 * Warehouse Dashboard Widgets - Role-Specific Components
 * Spec: Lines 114-116 (Rencana Tampilan.md)
 */

import React from 'react'
import { Package, AlertTriangle, TrendingUp, Clock } from 'lucide-react'

export const WarehouseDashboardWidgets: React.FC = () => {
  // Mock data - will be replaced with real API
  const stockMovement = {
    today_in: 1250,
    today_out: 980,
    pending_grn: 5,
    pending_transfer: 3
  }

  const expiryAlerts = [
    { material: '[IKHR504] KOHAIR D.BROWN', qty: 125, expiry_days: 5, status: 'urgent' },
    { material: '[IKP20157] Filling Dacron', qty: 45, expiry_days: 15, status: 'warning' },
    { material: '[ACB30104] Carton Box', qty: 200, expiry_days: 30, status: 'normal' }
  ]

  const spaceUtilization = {
    total_capacity: 10000, // m²
    used_space: 7850,
    reserved_space: 1200,
    available_space: 950,
    utilization_percent: 90.5
  }

  const movementHeatmap = [
    { zone: 'Raw Material', in: 450, out: 380, activity: 'high' },
    { zone: 'WIP Storage', in: 520, out: 420, activity: 'high' },
    { zone: 'Finished Goods', in: 280, out: 180, activity: 'medium' },
    { zone: 'Quarantine', in: 0, out: 0, activity: 'low' }
  ]

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
      {/* Widget 1: Stock Movement Heatmap */}
      <div className="bg-gradient-to-br from-white to-cyan-50 rounded-xl shadow-sm border-2 border-cyan-100 p-6">
        <div className="flex items-center gap-3 mb-4">
          <div className="p-2 bg-cyan-500 rounded-lg">
            <TrendingUp className="text-white" size={20} />
          </div>
          <h3 className="text-lg font-bold text-slate-800">Stock Movement Heatmap</h3>
        </div>
        
        <div className="grid grid-cols-2 gap-3 mb-4">
          <div className="p-3 bg-green-50 rounded-lg border border-green-200">
            <div className="text-xs text-green-600 mb-1">Total IN Today</div>
            <div className="text-2xl font-bold text-green-700">{stockMovement.today_in}</div>
            <div className="text-[10px] text-green-600 mt-1">pcs received</div>
          </div>
          <div className="p-3 bg-blue-50 rounded-lg border border-blue-200">
            <div className="text-xs text-blue-600 mb-1">Total OUT Today</div>
            <div className="text-2xl font-bold text-blue-700">{stockMovement.today_out}</div>
            <div className="text-[10px] text-blue-600 mt-1">pcs issued</div>
          </div>
        </div>
        
        <div className="space-y-2 mb-4">
          {movementHeatmap.map((zone) => (
            <div key={zone.zone} className="p-3 rounded-lg border border-slate-200 hover:bg-slate-50 transition">
              <div className="flex justify-between items-center mb-2">
                <span className="text-xs font-semibold text-slate-700">{zone.zone}</span>
                <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                  zone.activity === 'high' ? 'bg-red-100 text-red-700' :
                  zone.activity === 'medium' ? 'bg-yellow-100 text-yellow-700' :
                  'bg-green-100 text-green-700'
                }`}>
                  {zone.activity.toUpperCase()}
                </span>
              </div>
              <div className="flex gap-2 text-xs">
                <div className="flex-1 text-center p-1 bg-green-50 rounded">
                  <div className="text-green-600">IN</div>
                  <div className="font-bold text-green-700">{zone.in}</div>
                </div>
                <div className="flex-1 text-center p-1 bg-blue-50 rounded">
                  <div className="text-blue-600">OUT</div>
                  <div className="font-bold text-blue-700">{zone.out}</div>
                </div>
              </div>
            </div>
          ))}
        </div>
        
        <div className="grid grid-cols-2 gap-2 text-xs">
          <div className="p-2 bg-amber-50 rounded border border-amber-200">
            <div className="text-amber-600">Pending GRN</div>
            <div className="font-bold text-amber-700">{stockMovement.pending_grn}</div>
          </div>
          <div className="p-2 bg-purple-50 rounded border border-purple-200">
            <div className="text-purple-600">Pending Transfer</div>
            <div className="font-bold text-purple-700">{stockMovement.pending_transfer}</div>
          </div>
        </div>
      </div>

      {/* Widget 2: Expiry Alert */}
      <div className="bg-gradient-to-br from-white to-orange-50 rounded-xl shadow-sm border-2 border-orange-100 p-6">
        <div className="flex items-center gap-3 mb-4">
          <div className="p-2 bg-orange-500 rounded-lg">
            <Clock className="text-white" size={20} />
          </div>
          <h3 className="text-lg font-bold text-slate-800">Material Expiry Alert</h3>
        </div>
        
        <div className="space-y-3 mb-4">
          {expiryAlerts.map((item, index) => {
            const isUrgent = item.expiry_days <= 7
            const isWarning = item.expiry_days > 7 && item.expiry_days <= 15
            
            return (
              <div key={index} className={`p-3 rounded-lg border-2 ${
                isUrgent ? 'bg-red-50 border-red-300' :
                isWarning ? 'bg-yellow-50 border-yellow-300' :
                'bg-green-50 border-green-200'
              }`}>
                <div className="flex items-start justify-between mb-2">
                  <div className="flex-1">
                    <p className={`text-xs font-bold ${
                      isUrgent ? 'text-red-700' :
                      isWarning ? 'text-yellow-700' :
                      'text-green-700'
                    }`}>
                      {item.material}
                    </p>
                    <p className="text-[10px] text-slate-600 mt-1">
                      Qty: {item.qty} {item.material.includes('Carton') ? 'pcs' : 'kg'}
                    </p>
                  </div>
                  <div className={`text-right ${
                    isUrgent ? 'text-red-700' :
                    isWarning ? 'text-yellow-700' :
                    'text-green-700'
                  }`}>
                    <div className="text-lg font-bold">{item.expiry_days}</div>
                    <div className="text-[10px]">days</div>
                  </div>
                </div>
                {isUrgent && (
                  <div className="text-[10px] font-semibold text-red-600">
                    URGENT: Dispose or use immediately
                  </div>
                )}
              </div>
            )
          })}
        </div>
        
        <button className="w-full bg-orange-600 text-white px-4 py-2 rounded-lg hover:bg-orange-700 transition text-sm font-medium">
          View All Expiry Items →
        </button>
      </div>

      {/* Widget 3: Space Utilization */}
      <div className="bg-gradient-to-br from-white to-violet-50 rounded-xl shadow-sm border-2 border-violet-100 p-6">
        <div className="flex items-center gap-3 mb-4">
          <div className="p-2 bg-violet-500 rounded-lg">
            <Package className="text-white" size={20} />
          </div>
          <h3 className="text-lg font-bold text-slate-800">Space Utilization</h3>
        </div>
        
        <div className="mb-4">
          <div className="flex items-baseline gap-2">
            <span className="text-4xl font-bold text-violet-700">{spaceUtilization.utilization_percent}%</span>
            <span className={`text-xs font-semibold px-2 py-1 rounded-full ${
              spaceUtilization.utilization_percent > 90 ? 'bg-red-100 text-red-700' :
              spaceUtilization.utilization_percent > 80 ? 'bg-yellow-100 text-yellow-700' :
              'bg-green-100 text-green-700'
            }`}>
              {spaceUtilization.utilization_percent > 90 ? 'CRITICAL' :
               spaceUtilization.utilization_percent > 80 ? 'WARNING' : 'OPTIMAL'}
            </span>
          </div>
          <div className="text-xs text-slate-600 mt-1">Warehouse Capacity</div>
        </div>
        
        <div className="mb-4">
          <div className="w-full h-6 bg-slate-100 rounded-full overflow-hidden relative">
            <div 
              className="absolute top-0 left-0 h-full bg-gradient-to-r from-violet-500 to-violet-600 rounded-full"
              style={{ width: `${(spaceUtilization.used_space / spaceUtilization.total_capacity) * 100}%` }}
            />
            <div 
              className="absolute top-0 h-full bg-gradient-to-r from-yellow-400 to-yellow-500 rounded-full"
              style={{ 
                left: `${(spaceUtilization.used_space / spaceUtilization.total_capacity) * 100}%`,
                width: `${(spaceUtilization.reserved_space / spaceUtilization.total_capacity) * 100}%`
              }}
            />
          </div>
          <div className="flex justify-between text-[10px] text-slate-600 mt-1">
            <span>0 m²</span>
            <span>{spaceUtilization.total_capacity} m²</span>
          </div>
        </div>
        
        <div className="space-y-2">
          <div className="flex justify-between items-center p-2 bg-violet-50 rounded border border-violet-200">
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 bg-violet-500 rounded"></div>
              <span className="text-xs text-slate-700">Used Space</span>
            </div>
            <span className="text-xs font-bold text-violet-700">{spaceUtilization.used_space} m²</span>
          </div>
          <div className="flex justify-between items-center p-2 bg-yellow-50 rounded border border-yellow-200">
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 bg-yellow-500 rounded"></div>
              <span className="text-xs text-slate-700">Reserved</span>
            </div>
            <span className="text-xs font-bold text-yellow-700">{spaceUtilization.reserved_space} m²</span>
          </div>
          <div className="flex justify-between items-center p-2 bg-green-50 rounded border border-green-200">
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 bg-green-500 rounded"></div>
              <span className="text-xs text-slate-700">Available</span>
            </div>
            <span className="text-xs font-bold text-green-700">{spaceUtilization.available_space} m²</span>
          </div>
        </div>
        
        {spaceUtilization.utilization_percent > 90 && (
          <div className="mt-4 p-3 bg-red-50 border-2 border-red-200 rounded-lg">
            <div className="flex items-center gap-2 text-xs text-red-700">
              <AlertTriangle size={14} />
              <span className="font-semibold">Action required: Space optimization needed</span>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
