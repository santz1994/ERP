/**
 * Director Dashboard Widgets - Role-Specific Components
 * Spec: Lines 110-112 (Rencana Tampilan.md)
 */

import React from 'react'
import { DollarSign, TrendingUp, AlertCircle, BarChart3 } from 'lucide-react'
import { BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

export const DirectorDashboardWidgets: React.FC = () => {
  // Mock data - will be replaced with real API
  const revenuePerArtikel = [
    { artikel: 'AFTONSPARV', revenue: 45000000, units: 850, profit_margin: 28 },
    { artikel: 'KRAMIG', revenue: 38000000, units: 720, profit_margin: 32 },
    { artikel: 'GOSIG', revenue: 32000000, units: 650, profit_margin: 25 },
    { artikel: 'BLAHAJ', revenue: 28000000, units: 520, profit_margin: 30 },
    { artikel: 'DJUNGELSKOG', revenue: 25000000, units: 480, profit_margin: 22 }
  ]

  const materialDebtCost = {
    total_debt_items: 8,
    total_financial_impact: 25000000,
    at_risk_orders: 5,
    urgent_purchases_needed: 3
  }

  const monthComparison = [
    { month: 'Aug', revenue: 168000000, orders: 12 },
    { month: 'Sep', revenue: 172000000, orders: 14 },
    { month: 'Oct', revenue: 185000000, orders: 15 },
    { month: 'Nov', revenue: 178000000, orders: 13 },
    { month: 'Dec', revenue: 192000000, orders: 16 },
    { month: 'Jan', revenue: 198000000, orders: 17 }
  ]

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
      {/* Widget 1: Revenue per Artikel */}
      <div className="bg-gradient-to-br from-white to-emerald-50 rounded-xl shadow-sm border-2 border-emerald-100 p-6">
        <div className="flex items-center gap-3 mb-4">
          <div className="p-2 bg-emerald-500 rounded-lg">
            <BarChart3 className="text-white" size={20} />
          </div>
          <h3 className="text-lg font-bold text-slate-800">Top Revenue Artikel</h3>
        </div>
        
        <div className="space-y-3 mb-4">
          {revenuePerArtikel.map((item, index) => (
            <div key={item.artikel} className="group hover:bg-emerald-50 p-2 rounded-lg transition">
              <div className="flex items-center justify-between mb-1">
                <div className="flex items-center gap-2">
                  <div className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold ${
                    index === 0 ? 'bg-yellow-400 text-yellow-900' :
                    index === 1 ? 'bg-slate-300 text-slate-700' :
                    index === 2 ? 'bg-amber-600 text-white' :
                    'bg-emerald-100 text-emerald-700'
                  }`}>
                    {index + 1}
                  </div>
                  <span className="text-sm font-bold text-slate-800">{item.artikel}</span>
                </div>
                <span className="text-xs font-semibold text-emerald-600 bg-emerald-100 px-2 py-0.5 rounded-full">
                  {item.profit_margin}% margin
                </span>
              </div>
              <div className="flex justify-between text-xs text-slate-600 ml-8">
                <span>Rp {(item.revenue / 1000000).toFixed(1)}M</span>
                <span>{item.units} units</span>
              </div>
            </div>
          ))}
        </div>
        
        <button className="w-full bg-emerald-600 text-white px-4 py-2 rounded-lg hover:bg-emerald-700 transition text-sm font-medium">
          View Full Report →
        </button>
      </div>

      {/* Widget 2: Material Debt Cost Impact */}
      <div className="bg-gradient-to-br from-white to-rose-50 rounded-xl shadow-sm border-2 border-rose-100 p-6">
        <div className="flex items-center gap-3 mb-4">
          <div className="p-2 bg-rose-500 rounded-lg">
            <AlertCircle className="text-white" size={20} />
          </div>
          <h3 className="text-lg font-bold text-slate-800">Material Debt Cost</h3>
        </div>
        
        <div className="mb-4">
          <div className="text-3xl font-bold text-rose-700">
            Rp {(materialDebtCost.total_financial_impact / 1000000).toFixed(1)}M
          </div>
          <div className="text-xs text-slate-600 mt-1">Financial Impact (Outstanding)</div>
        </div>
        
        <div className="grid grid-cols-2 gap-3 mb-4">
          <div className="p-3 bg-red-50 rounded-lg border border-red-200">
            <div className="text-xs text-red-600 mb-1">Debt Items</div>
            <div className="text-2xl font-bold text-red-700">{materialDebtCost.total_debt_items}</div>
          </div>
          <div className="p-3 bg-orange-50 rounded-lg border border-orange-200">
            <div className="text-xs text-orange-600 mb-1">At Risk MOs</div>
            <div className="text-2xl font-bold text-orange-700">{materialDebtCost.at_risk_orders}</div>
          </div>
        </div>
        
        <div className="p-4 bg-rose-50 border-2 border-rose-200 rounded-lg">
          <div className="flex items-start gap-2">
            <AlertCircle className="text-rose-600 flex-shrink-0 mt-0.5" size={16} />
            <div className="text-xs text-rose-700">
              <p className="font-semibold mb-1">⚠️ Urgent Action Required:</p>
              <p>{materialDebtCost.urgent_purchases_needed} critical items need immediate purchase to prevent production delays</p>
            </div>
          </div>
        </div>
        
        <button className="mt-4 w-full bg-rose-600 text-white px-4 py-2 rounded-lg hover:bg-rose-700 transition text-sm font-medium">
          View Material Debt Report →
        </button>
      </div>

      {/* Widget 3: Month-over-Month Comparison */}
      <div className="bg-gradient-to-br from-white to-indigo-50 rounded-xl shadow-sm border-2 border-indigo-100 p-6">
        <div className="flex items-center gap-3 mb-4">
          <div className="p-2 bg-indigo-500 rounded-lg">
            <TrendingUp className="text-white" size={20} />
          </div>
          <h3 className="text-lg font-bold text-slate-800">M-o-M Performance</h3>
        </div>
        
        <div className="mb-4">
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-bold text-indigo-700">
              Rp {(monthComparison[monthComparison.length - 1].revenue / 1000000).toFixed(0)}M
            </span>
            <span className="text-xs text-green-600 bg-green-50 px-2 py-1 rounded-full font-semibold">
              +3.1% ↗
            </span>
          </div>
          <div className="text-xs text-slate-600 mt-1">January 2026 Revenue</div>
        </div>
        
        <div className="h-32 mb-4">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={monthComparison}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
              <XAxis dataKey="month" tick={{ fontSize: 10 }} />
              <YAxis tick={{ fontSize: 10 }} tickFormatter={(value) => `${(value / 1000000).toFixed(0)}M`} />
              <Tooltip formatter={(value: number) => `Rp ${(value / 1000000).toFixed(1)}M`} />
              <Line type="monotone" dataKey="revenue" stroke="#6366f1" strokeWidth={2} dot={{ r: 4, fill: '#6366f1' }} />
            </LineChart>
          </ResponsiveContainer>
        </div>
        
        <div className="grid grid-cols-2 gap-2 text-xs">
          <div className="p-2 bg-blue-50 rounded border border-blue-200">
            <div className="text-blue-600">Total Orders</div>
            <div className="font-bold text-blue-700">{monthComparison[monthComparison.length - 1].orders} MOs</div>
          </div>
          <div className="p-2 bg-green-50 rounded border border-green-200">
            <div className="text-green-600">Avg Order Value</div>
            <div className="font-bold text-green-700">
              Rp {((monthComparison[monthComparison.length - 1].revenue / monthComparison[monthComparison.length - 1].orders) / 1000000).toFixed(1)}M
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
