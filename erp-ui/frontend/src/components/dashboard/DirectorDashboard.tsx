import React, { useEffect, useState } from 'react'
import { TrendingUp, DollarSign, AlertTriangle, BarChart3, FileText, RefreshCw, Download } from 'lucide-react'
import { apiClient } from '@/api/client'

interface DirectorDashboardData {
  // Revenue metrics
  total_revenue_this_month: number // Rp
  total_revenue_last_month: number
  revenue_by_article: RevenueByArticle[]
  
  // Cost metrics
  total_material_cost: number
  material_debt_cost: number // Interest + Rush order costs
  copq_total: number // Cost of Poor Quality
  
  // Performance comparison
  production_output_this_month: number // pcs
  production_output_last_month: number
  
  // Strategic KPIs
  profit_margin: number // %
  material_turnover_ratio: number
  customer_satisfaction_score: number // %
  on_time_delivery_rate: number // %
}

interface RevenueByArticle {
  article_code: string
  article_name: string
  quantity_produced: number
  revenue: number // Rp
  profit_margin: number // %
}

export const DirectorDashboard: React.FC = () => {
  const [data, setData] = useState<DirectorDashboardData | null>(null)
  const [loading, setLoading] = useState(true)

  const fetchDashboardData = async () => {
    try {
      setLoading(true)
      const response = await apiClient.get('/dashboard/director')
      setData(response.data)
    } catch (error) {
      console.error('Failed to fetch director dashboard:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchDashboardData()
    const interval = setInterval(fetchDashboardData, 300000) // Refresh every 5 minutes
    return () => clearInterval(interval)
  }, [])

  const exportToPDF = async () => {
    try {
      const response = await apiClient.get('/dashboard/director/export-pdf', {
        responseType: 'blob'
      })
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', `director-report-${new Date().toISOString().split('T')[0]}.pdf`)
      document.body.appendChild(link)
      link.click()
      link.remove()
    } catch (error) {
      console.error('Failed to export PDF:', error)
    }
  }

  if (loading || !data) {
    return (
      <div className="flex items-center justify-center h-64">
        <RefreshCw className="w-8 h-8 animate-spin text-blue-500" />
        <span className="ml-3 text-gray-600">Loading Director Dashboard...</span>
      </div>
    )
  }

  // Calculate month-over-month changes
  const revenueChange = data.total_revenue_last_month > 0
    ? ((data.total_revenue_this_month - data.total_revenue_last_month) / data.total_revenue_last_month) * 100
    : 0
  
  const outputChange = data.production_output_last_month > 0
    ? ((data.production_output_this_month - data.production_output_last_month) / data.production_output_last_month) * 100
    : 0

  return (
    <div className="space-y-6">
      {/* Header with Export */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-gray-800">Director Dashboard</h2>
          <p className="text-sm text-gray-600">Strategic metrics and cost analysis</p>
        </div>
        <div className="flex gap-3">
          <button
            onClick={fetchDashboardData}
            className="flex items-center gap-2 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
          >
            <RefreshCw className="w-4 h-4" />
            Refresh
          </button>
          <button
            onClick={exportToPDF}
            className="flex items-center gap-2 px-4 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 transition-colors"
          >
            <Download className="w-4 h-4" />
            Export Executive Report
          </button>
        </div>
      </div>

      {/* Strategic KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StrategicKPICard
          icon={<DollarSign className="w-6 h-6" />}
          title="Total Revenue"
          value={`Rp ${(data.total_revenue_this_month / 1000000).toFixed(1)}M`}
          change={revenueChange}
          subtitle={`vs last month: Rp ${(data.total_revenue_last_month / 1000000).toFixed(1)}M`}
          variant="revenue"
        />
        <StrategicKPICard
          icon={<TrendingUp className="w-6 h-6" />}
          title="Profit Margin"
          value={`${data.profit_margin.toFixed(1)}%`}
          subtitle="Gross profit margin"
          variant={data.profit_margin >= 30 ? 'success' : data.profit_margin >= 20 ? 'warning' : 'danger'}
        />
        <StrategicKPICard
          icon={<AlertTriangle className="w-6 h-6" />}
          title="Material Debt Cost"
          value={`Rp ${(data.material_debt_cost / 1000000).toFixed(1)}M`}
          subtitle="Interest + Rush order costs"
          variant="danger"
        />
        <StrategicKPICard
          icon={<BarChart3 className="w-6 h-6" />}
          title="Production Output"
          value={`${data.production_output_this_month.toLocaleString()} pcs`}
          change={outputChange}
          subtitle={`vs last month: ${data.production_output_last_month.toLocaleString()} pcs`}
          variant="info"
        />
      </div>

      {/* Month-over-Month Comparison */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-800 mb-4">Month-over-Month Performance</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <ComparisonMetric
            label="Revenue Growth"
            value={revenueChange}
            format="percentage"
            isPositiveGood={true}
          />
          <ComparisonMetric
            label="Output Growth"
            value={outputChange}
            format="percentage"
            isPositiveGood={true}
          />
          <ComparisonMetric
            label="Cost Reduction"
            value={data.material_debt_cost > 0 ? -15.5 : 0} // Mock data, should come from backend
            format="percentage"
            isPositiveGood={true}
          />
        </div>
      </div>

      {/* Revenue per Article (Top 5) */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-semibold text-gray-800">Revenue per Article (Top 5)</h3>
          <span className="text-sm text-gray-500">This Month</span>
        </div>
        <div className="space-y-3">
          {data.revenue_by_article.slice(0, 5).map((article, index) => (
            <div key={article.article_code} className="flex items-center gap-4 p-3 bg-gray-50 rounded-lg">
              <div className="flex items-center justify-center w-8 h-8 bg-blue-100 text-blue-600 rounded-full font-semibold text-sm">
                {index + 1}
              </div>
              <div className="flex-1">
                <div className="flex justify-between items-center">
                  <div>
                    <p className="font-medium text-gray-800">{article.article_code}</p>
                    <p className="text-sm text-gray-600">{article.article_name}</p>
                  </div>
                  <div className="text-right">
                    <p className="font-semibold text-gray-800">
                      Rp {(article.revenue / 1000000).toFixed(2)}M
                    </p>
                    <p className="text-sm text-gray-600">
                      {article.quantity_produced.toLocaleString()} pcs • {article.profit_margin.toFixed(1)}% margin
                    </p>
                  </div>
                </div>
                {/* Revenue bar */}
                <div className="mt-2 h-2 bg-gray-200 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-gradient-to-r from-blue-500 to-emerald-500"
                    style={{
                      width: `${Math.min((article.revenue / data.revenue_by_article[0].revenue) * 100, 100)}%`
                    }}
                  />
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Cost Analysis */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Material Cost Breakdown */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">Material Cost Analysis</h3>
          <div className="space-y-3">
            <CostItem
              label="Direct Material Cost"
              value={data.total_material_cost}
              percentage={100}
              color="blue"
            />
            <CostItem
              label="Material Debt Cost"
              value={data.material_debt_cost}
              percentage={(data.material_debt_cost / data.total_material_cost) * 100}
              color="rose"
            />
            <div className="pt-3 border-t border-gray-200">
              <div className="flex justify-between items-center">
                <span className="font-semibold text-gray-800">Total Material Cost</span>
                <span className="text-lg font-bold text-gray-900">
                  Rp {((data.total_material_cost + data.material_debt_cost) / 1000000).toFixed(2)}M
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Quality Cost (COPQ) */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">Cost of Poor Quality (COPQ)</h3>
          <div className="text-center mb-4">
            <p className="text-3xl font-bold text-rose-600">
              Rp {(data.copq_total / 1000000).toFixed(2)}M
            </p>
            <p className="text-sm text-gray-600 mt-1">Total COPQ This Month</p>
          </div>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between items-center p-2 bg-rose-50 rounded">
              <span className="text-gray-700">% of Revenue</span>
              <span className="font-semibold text-rose-600">
                {((data.copq_total / data.total_revenue_this_month) * 100).toFixed(2)}%
              </span>
            </div>
            <div className="flex justify-between items-center p-2 bg-amber-50 rounded">
              <span className="text-gray-700">Target: &lt;3% of Revenue</span>
              <span className="font-semibold text-amber-600">
                {((data.copq_total / data.total_revenue_this_month) * 100) < 3 ? 'On Target' : 'Above Target'}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Customer & Delivery Metrics */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-800 mb-4">Customer Satisfaction & Delivery</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <MetricCircle
            label="Customer Satisfaction"
            value={data.customer_satisfaction_score}
            target={90}
            color="emerald"
          />
          <MetricCircle
            label="On-Time Delivery"
            value={data.on_time_delivery_rate}
            target={95}
            color="blue"
          />
          <MetricCircle
            label="Material Turnover"
            value={data.material_turnover_ratio * 10} // Convert ratio to percentage for display
            target={80}
            color="amber"
          />
        </div>
      </div>
    </div>
  )
}

// Sub-components

interface StrategicKPICardProps {
  icon: React.ReactNode
  title: string
  value: string
  change?: number
  subtitle: string
  variant: 'revenue' | 'success' | 'warning' | 'danger' | 'info'
}

const StrategicKPICard: React.FC<StrategicKPICardProps> = ({ icon, title, value, change, subtitle, variant }) => {
  const variantColors = {
    revenue: 'from-blue-500 to-indigo-600',
    success: 'from-emerald-500 to-green-600',
    warning: 'from-amber-500 to-orange-600',
    danger: 'from-rose-500 to-red-600',
    info: 'from-cyan-500 to-blue-600'
  }

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-5 hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between mb-3">
        <div className={`p-2 rounded-lg bg-gradient-to-br ${variantColors[variant]}`}>
          <div className="text-white">{icon}</div>
        </div>
        {change !== undefined && (
          <div className={`flex items-center gap-1 text-sm font-medium ${
            change >= 0 ? 'text-emerald-600' : 'text-rose-600'
          }`}>
            <TrendingUp className={`w-4 h-4 ${change < 0 ? 'rotate-180' : ''}`} />
            {Math.abs(change).toFixed(1)}%
          </div>
        )}
      </div>
      <h3 className="text-sm font-medium text-gray-600 mb-1">{title}</h3>
      <p className="text-2xl font-bold text-gray-900 mb-1">{value}</p>
      <p className="text-xs text-gray-500">{subtitle}</p>
    </div>
  )
}

interface ComparisonMetricProps {
  label: string
  value: number
  format: 'percentage' | 'number'
  isPositiveGood: boolean
}

const ComparisonMetric: React.FC<ComparisonMetricProps> = ({ label, value, format, isPositiveGood }) => {
  const isPositive = value >= 0
  const isGood = isPositiveGood ? isPositive : !isPositive

  return (
    <div className="text-center">
      <p className="text-sm text-gray-600 mb-2">{label}</p>
      <div className={`text-3xl font-bold ${isGood ? 'text-emerald-600' : 'text-rose-600'}`}>
        {isPositive ? '+' : ''}{value.toFixed(1)}{format === 'percentage' ? '%' : ''}
      </div>
      <div className={`mt-2 inline-flex items-center gap-1 px-3 py-1 rounded-full text-sm font-medium ${
        isGood ? 'bg-emerald-100 text-emerald-700' : 'bg-rose-100 text-rose-700'
      }`}>
        {isGood ? '[Good]' : '[Needs Attention]'} {isGood ? 'Good' : 'Needs Attention'}
      </div>
    </div>
  )
}

interface CostItemProps {
  label: string
  value: number
  percentage: number
  color: 'blue' | 'rose'
}

const CostItem: React.FC<CostItemProps> = ({ label, value, percentage, color }) => {
  const colorClasses = {
    blue: 'bg-blue-500',
    rose: 'bg-rose-500'
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-1">
        <span className="text-sm text-gray-600">{label}</span>
        <span className="text-sm font-semibold text-gray-800">
          Rp {(value / 1000000).toFixed(2)}M
        </span>
      </div>
      <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
        <div
          className={`h-full ${colorClasses[color]}`}
          style={{ width: `${Math.min(percentage, 100)}%` }}
        />
      </div>
    </div>
  )
}

interface MetricCircleProps {
  label: string
  value: number
  target: number
  color: 'emerald' | 'blue' | 'amber'
}

const MetricCircle: React.FC<MetricCircleProps> = ({ label, value, target, color }) => {
  const percentage = (value / 100) * 360

  const colorClasses = {
    emerald: { bg: 'bg-emerald-100', text: 'text-emerald-600', stroke: 'stroke-emerald-500' },
    blue: { bg: 'bg-blue-100', text: 'text-blue-600', stroke: 'stroke-blue-500' },
    amber: { bg: 'bg-amber-100', text: 'text-amber-600', stroke: 'stroke-amber-500' }
  }

  return (
    <div className="text-center">
      <div className="relative inline-flex items-center justify-center mb-3">
        <svg className="w-32 h-32 transform -rotate-90">
          <circle
            cx="64"
            cy="64"
            r="56"
            stroke="currentColor"
            strokeWidth="8"
            fill="none"
            className="text-gray-200"
          />
          <circle
            cx="64"
            cy="64"
            r="56"
            stroke="currentColor"
            strokeWidth="8"
            fill="none"
            strokeDasharray={`${percentage} 360`}
            className={colorClasses[color].stroke}
          />
        </svg>
        <div className="absolute">
          <p className={`text-2xl font-bold ${colorClasses[color].text}`}>{value.toFixed(0)}%</p>
        </div>
      </div>
      <p className="font-medium text-gray-800">{label}</p>
      <p className="text-sm text-gray-500 mt-1">
        Target: {target}% • {value >= target ? 'On Target' : 'Below Target'}
      </p>
    </div>
  )
}
