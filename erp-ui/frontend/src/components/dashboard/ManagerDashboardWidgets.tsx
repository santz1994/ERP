/**
 * Manager Dashboard Widgets - Role-Specific Components
 * Spec: Lines 106-108 (Rencana Tampilan.md)
 */

import React from 'react'
import { Activity, DollarSign, TrendingUp, AlertTriangle } from 'lucide-react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

export const ManagerDashboardWidgets: React.FC = () => {
  // Mock data - will be replaced with real API
  const oeeData = {
    availability: 85.5,
    performance: 92.3,
    quality: 96.8,
    overall_oee: 76.3
  }

  const copqData = {
    total_defects: 245,
    rework_cost: 5940000,
    scrap_cost: 8230000,
    total_copq: 15400000,
    trend: [
      { month: 'Oct', cost: 18500000 },
      { month: 'Nov', cost: 17200000 },
      { month: 'Dec', cost: 16100000 },
      { month: 'Jan', cost: 15400000 }
    ]
  }

  const deptPerformance = [
    { dept: 'Cutting', efficiency: 95, color: '#ef4444' },
    { dept: 'Sewing', efficiency: 88, color: '#3b82f6' },
    { dept: 'Finishing', efficiency: 91, color: '#10b981' },
    { dept: 'Packing', efficiency: 97, color: '#f59e0b' }
  ]

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
      {/* Widget 1: OEE (Overall Equipment Effectiveness) */}
      <div className="bg-gradient-to-br from-white to-green-50 rounded-xl shadow-sm border-2 border-green-100 p-6">
        <div className="flex items-center gap-3 mb-4">
          <div className="p-2 bg-green-500 rounded-lg">
            <Activity className="text-white" size={20} />
          </div>
          <h3 className="text-lg font-bold text-slate-800">Production Efficiency (OEE)</h3>
        </div>
        
        <div className="mb-4">
          <div className="flex items-baseline justify-between mb-1">
            <span className="text-4xl font-bold text-green-700">{oeeData.overall_oee}%</span>
            <span className="text-xs text-green-600 bg-green-50 px-2 py-1 rounded-full">Overall OEE</span>
          </div>
          <div className="text-xs text-slate-600">
            Target: 80% | Status: <span className="text-green-600 font-semibold">Above Target ✅</span>
          </div>
        </div>
        
        <div className="space-y-3">
          <div>
            <div className="flex justify-between text-xs mb-1">
              <span className="text-slate-600">Availability</span>
              <span className="font-bold text-slate-700">{oeeData.availability}%</span>
            </div>
            <div className="w-full h-2 bg-slate-100 rounded-full overflow-hidden">
              <div className="h-full bg-blue-500 rounded-full" style={{ width: `${oeeData.availability}%` }} />
            </div>
          </div>
          
          <div>
            <div className="flex justify-between text-xs mb-1">
              <span className="text-slate-600">Performance</span>
              <span className="font-bold text-slate-700">{oeeData.performance}%</span>
            </div>
            <div className="w-full h-2 bg-slate-100 rounded-full overflow-hidden">
              <div className="h-full bg-purple-500 rounded-full" style={{ width: `${oeeData.performance}%` }} />
            </div>
          </div>
          
          <div>
            <div className="flex justify-between text-xs mb-1">
              <span className="text-slate-600">Quality</span>
              <span className="font-bold text-slate-700">{oeeData.quality}%</span>
            </div>
            <div className="w-full h-2 bg-slate-100 rounded-full overflow-hidden">
              <div className="h-full bg-green-500 rounded-full" style={{ width: `${oeeData.quality}%` }} />
            </div>
          </div>
        </div>
      </div>

      {/* Widget 2: COPQ Summary */}
      <div className="bg-gradient-to-br from-white to-red-50 rounded-xl shadow-sm border-2 border-red-100 p-6">
        <div className="flex items-center gap-3 mb-4">
          <div className="p-2 bg-red-500 rounded-lg">
            <DollarSign className="text-white" size={20} />
          </div>
          <h3 className="text-lg font-bold text-slate-800">Cost of Poor Quality</h3>
        </div>
        
        <div className="mb-4">
          <div className="text-3xl font-bold text-red-700">
            Rp {(copqData.total_copq / 1000000).toFixed(1)}M
          </div>
          <div className="text-xs text-slate-600 mt-1">This Month</div>
        </div>
        
        <div className="h-32 mb-4">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={copqData.trend}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
              <XAxis dataKey="month" tick={{ fontSize: 10 }} />
              <YAxis tick={{ fontSize: 10 }} tickFormatter={(value) => `${(value / 1000000).toFixed(0)}M`} />
              <Tooltip formatter={(value: number) => `Rp ${(value / 1000000).toFixed(1)}M`} />
              <Bar dataKey="cost" fill="#ef4444" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
        
        <div className="grid grid-cols-2 gap-2 text-xs">
          <div className="p-2 bg-orange-50 rounded border border-orange-200">
            <div className="text-orange-600">Rework Cost</div>
            <div className="font-bold text-orange-700">Rp {(copqData.rework_cost / 1000000).toFixed(1)}M</div>
          </div>
          <div className="p-2 bg-red-50 rounded border border-red-200">
            <div className="text-red-600">Scrap Cost</div>
            <div className="font-bold text-red-700">Rp {(copqData.scrap_cost / 1000000).toFixed(1)}M</div>
          </div>
        </div>
      </div>

      {/* Widget 3: Department Performance */}
      <div className="bg-gradient-to-br from-white to-blue-50 rounded-xl shadow-sm border-2 border-blue-100 p-6">
        <div className="flex items-center gap-3 mb-4">
          <div className="p-2 bg-blue-500 rounded-lg">
            <TrendingUp className="text-white" size={20} />
          </div>
          <h3 className="text-lg font-bold text-slate-800">Department Performance</h3>
        </div>
        
        <div className="space-y-4">
          {deptPerformance.map((dept) => (
            <div key={dept.dept} className="group">
              <div className="flex justify-between items-center mb-2">
                <span className="text-sm font-medium text-slate-700">{dept.dept}</span>
                <span className={`text-sm font-bold ${
                  dept.efficiency >= 90 ? 'text-green-600' : 
                  dept.efficiency >= 80 ? 'text-yellow-600' : 
                  'text-red-600'
                }`}>
                  {dept.efficiency}%
                </span>
              </div>
              <div className="w-full h-2 bg-slate-100 rounded-full overflow-hidden">
                <div 
                  className="h-full rounded-full transition-all duration-500"
                  style={{ 
                    width: `${dept.efficiency}%`,
                    backgroundColor: dept.color
                  }}
                />
              </div>
            </div>
          ))}
        </div>
        
        <div className="mt-4 p-3 bg-blue-50 rounded-lg border border-blue-200">
          <div className="flex items-center gap-2 text-xs text-blue-700">
            <AlertTriangle size={14} />
            <span>Sewing below target (90%) - Review required</span>
          </div>
        </div>
      </div>
    </div>
  )
}
