/**
 * PPIC Dashboard Widgets - Role-Specific Components
 * Spec: Lines 100-104 (Rencana Tampilan.md)
 */

import React from 'react'
import { Package, AlertCircle, CheckCircle, Clock, TrendingUp, Zap } from 'lucide-react'

interface PPICDashboardProps {
  // Props will be passed from API
}

export const PPICDashboardWidgets: React.FC<PPICDashboardProps> = () => {
  // Mock data - will be replaced with real API calls
  const moStats = {
    partial_count: 3,
    released_count: 7,
    draft_count: 2,
    total_mos: 12
  }

  const materialAllocation = {
    total_reserved: 850,
    total_available: 1200,
    items_with_debt: 2
  }

  const spkQueue = {
    pending_generation: 5,
    auto_generated_today: 8
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
      {/* Widget 1: MO Release Status */}
      <div className="bg-gradient-to-br from-white to-blue-50 rounded-xl shadow-sm border-2 border-blue-100 p-6">
        <div className="flex items-center gap-3 mb-4">
          <div className="p-2 bg-blue-500 rounded-lg">
            <TrendingUp className="text-white" size={20} />
          </div>
          <h3 className="text-lg font-bold text-slate-800">MO Release Status</h3>
        </div>
        
        <div className="space-y-3">
          {/* DRAFT */}
          <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg border border-gray-200">
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 bg-gray-400 rounded-full"></div>
              <span className="text-sm font-medium text-gray-700">DRAFT</span>
            </div>
            <span className="text-xl font-bold text-gray-600">{moStats.draft_count}</span>
          </div>
          
          {/* PARTIAL */}
          <div className="flex items-center justify-between p-3 bg-yellow-50 rounded-lg border border-yellow-200">
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 bg-yellow-500 rounded-full animate-pulse"></div>
              <span className="text-sm font-medium text-yellow-700">PARTIAL</span>
            </div>
            <span className="text-xl font-bold text-yellow-700">{moStats.partial_count}</span>
          </div>
          
          {/* RELEASED */}
          <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg border border-green-200">
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 bg-green-500 rounded-full"></div>
              <span className="text-sm font-medium text-green-700">RELEASED</span>
            </div>
            <span className="text-xl font-bold text-green-700">{moStats.released_count}</span>
          </div>
        </div>
        
        <button className="mt-4 w-full bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition text-sm font-medium">
          View Partial MOs →
        </button>
      </div>

      {/* Widget 2: Material Allocation */}
      <div className="bg-gradient-to-br from-white to-purple-50 rounded-xl shadow-sm border-2 border-purple-100 p-6">
        <div className="flex items-center gap-3 mb-4">
          <div className="p-2 bg-purple-500 rounded-lg">
            <Package className="text-white" size={20} />
          </div>
          <h3 className="text-lg font-bold text-slate-800">Material Allocation</h3>
        </div>
        
        <div className="space-y-4">
          <div>
            <div className="flex justify-between text-sm mb-2">
              <span className="text-slate-600">Reserved for MOs</span>
              <span className="font-bold text-purple-700">{materialAllocation.total_reserved} items</span>
            </div>
            <div className="w-full h-2 bg-slate-100 rounded-full overflow-hidden">
              <div 
                className="h-full bg-gradient-to-r from-purple-500 to-purple-600 rounded-full"
                style={{ width: `${(materialAllocation.total_reserved / materialAllocation.total_available) * 100}%` }}
              />
            </div>
          </div>
          
          <div className="grid grid-cols-2 gap-3">
            <div className="p-3 bg-green-50 rounded-lg border border-green-200">
              <div className="text-xs text-green-600 mb-1">Available</div>
              <div className="text-xl font-bold text-green-700">{materialAllocation.total_available}</div>
            </div>
            <div className="p-3 bg-red-50 rounded-lg border border-red-200">
              <div className="text-xs text-red-600 mb-1">Debt Items</div>
              <div className="text-xl font-bold text-red-700">{materialAllocation.items_with_debt}</div>
            </div>
          </div>
        </div>
        
        <button className="mt-4 w-full bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700 transition text-sm font-medium">
          View BOM Explosion →
        </button>
      </div>

      {/* Widget 3: SPK Generation Queue */}
      <div className="bg-gradient-to-br from-white to-amber-50 rounded-xl shadow-sm border-2 border-amber-100 p-6">
        <div className="flex items-center gap-3 mb-4">
          <div className="p-2 bg-amber-500 rounded-lg">
            <Zap className="text-white" size={20} />
          </div>
          <h3 className="text-lg font-bold text-slate-800">SPK Auto-Generation</h3>
        </div>
        
        <div className="space-y-4">
          <div className="p-4 bg-amber-50 rounded-lg border-2 border-amber-200">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-amber-700">Pending Generation</span>
              <Clock className="text-amber-500" size={18} />
            </div>
            <div className="text-3xl font-bold text-amber-900">{spkQueue.pending_generation}</div>
            <div className="text-xs text-amber-600 mt-1">MOs waiting for SPK</div>
          </div>
          
          <div className="p-4 bg-green-50 rounded-lg border border-green-200">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-green-700">Generated Today</span>
              <CheckCircle className="text-green-500" size={18} />
            </div>
            <div className="text-3xl font-bold text-green-900">{spkQueue.auto_generated_today}</div>
            <div className="text-xs text-green-600 mt-1">Auto-created from MO RELEASED</div>
          </div>
        </div>
        
        <button className="mt-4 w-full bg-amber-600 text-white px-4 py-2 rounded-lg hover:bg-amber-700 transition text-sm font-medium">
          Generate Pending SPKs →
        </button>
      </div>
    </div>
  )
}
