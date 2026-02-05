import React from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { cn } from '@/lib/utils'

interface KPICardProps {
  title: string
  value: string | number
  subtitle?: string
  icon?: React.ReactNode
  trend?: {
    value: number
    isPositive: boolean
  }
  variant?: 'default' | 'success' | 'warning' | 'error' | 'info'
  onClick?: () => void
}

export const KPICard: React.FC<KPICardProps> = ({
  title,
  value,
  subtitle,
  icon,
  trend,
  variant = 'default',
  onClick,
}) => {
  const variantClasses = {
    default: 'border-gray-200',
    success: 'border-green-500 bg-green-50',
    warning: 'border-yellow-500 bg-yellow-50',
    error: 'border-red-500 bg-red-50',
    info: 'border-blue-500 bg-blue-50',
  }

  return (
    <Card
      className={cn(
        'border-l-4 transition-all hover:shadow-md',
        variantClasses[variant],
        onClick && 'cursor-pointer'
      )}
      onClick={onClick}
    >
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <CardTitle className="text-sm font-medium text-gray-600">{title}</CardTitle>
        {icon && <div className="text-2xl">{icon}</div>}
      </CardHeader>
      <CardContent>
        <div className="text-3xl font-bold">{value}</div>
        {subtitle && <p className="text-xs text-gray-500 mt-1">{subtitle}</p>}
        {trend && (
          <div className="flex items-center mt-2 text-sm">
            <span
              className={cn(
                'flex items-center',
                trend.isPositive ? 'text-green-600' : 'text-red-600'
              )}
            >
              {trend.isPositive ? '↑' : '↓'} {Math.abs(trend.value)}%
            </span>
            <span className="text-gray-500 ml-2">vs last period</span>
          </div>
        )}
      </CardContent>
    </Card>
  )
}

interface StatusCardProps {
  title: string
  data: Array<{
    label: string
    value: number
    percentage: number
    color: string
  }>
  total?: number
}

export const StatusCard: React.FC<StatusCardProps> = ({ title, data, total }) => {
  return (
    <Card>
      <CardHeader>
        <CardTitle>{title}</CardTitle>
        {total !== undefined && (
          <p className="text-2xl font-bold mt-2">{total}</p>
        )}
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {data.map((item, index) => (
            <div key={index}>
              <div className="flex items-center justify-between mb-1">
                <span className="text-sm font-medium">{item.label}</span>
                <span className="text-sm text-gray-600">
                  {item.value} ({item.percentage}%)
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="h-2 rounded-full transition-all"
                  style={{
                    width: `${item.percentage}%`,
                    backgroundColor: item.color,
                  }}
                />
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}

interface AlertItem {
  id: number
  title: string
  description: string
  severity: 'critical' | 'warning' | 'info'
  timestamp: string
}

interface AlertListCardProps {
  title: string
  alerts: AlertItem[]
  maxItems?: number
  onViewAll?: () => void
}

export const AlertListCard: React.FC<AlertListCardProps> = ({
  title,
  alerts,
  maxItems = 5,
  onViewAll,
}) => {
  const severityColors = {
    critical: 'bg-red-100 border-red-500 text-red-800',
    warning: 'bg-yellow-100 border-yellow-500 text-yellow-800',
    info: 'bg-blue-100 border-blue-500 text-blue-800',
  }

  const severityIcons = {
    critical: '🔴',
    warning: '⚠️',
    info: 'ℹ️',
  }

  const displayAlerts = alerts.slice(0, maxItems)

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle>{title}</CardTitle>
        <span className="text-sm text-gray-500">{alerts.length} items</span>
      </CardHeader>
      <CardContent>
        {displayAlerts.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <p>✅ No alerts</p>
            <p className="text-sm mt-1">All systems operational</p>
          </div>
        ) : (
          <div className="space-y-2">
            {displayAlerts.map((alert) => (
              <div
                key={alert.id}
                className={cn(
                  'p-3 rounded-md border-l-4',
                  severityColors[alert.severity]
                )}
              >
                <div className="flex items-start">
                  <span className="text-xl mr-2">{severityIcons[alert.severity]}</span>
                  <div className="flex-1">
                    <p className="font-medium text-sm">{alert.title}</p>
                    <p className="text-xs mt-1 opacity-90">{alert.description}</p>
                    <p className="text-xs mt-1 opacity-75">{alert.timestamp}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
        {alerts.length > maxItems && onViewAll && (
          <button
            onClick={onViewAll}
            className="w-full mt-3 text-sm text-blue-600 hover:text-blue-800 font-medium"
          >
            View all {alerts.length} alerts →
          </button>
        )}
      </CardContent>
    </Card>
  )
}

interface QuickActionButton {
  label: string
  icon: string
  onClick: () => void
  variant?: 'primary' | 'secondary' | 'success' | 'warning'
}

interface QuickActionsCardProps {
  actions: QuickActionButton[]
}

export const QuickActionsCard: React.FC<QuickActionsCardProps> = ({ actions }) => {
  const variantClasses = {
    primary: 'bg-blue-600 hover:bg-blue-700 text-white',
    secondary: 'bg-purple-600 hover:bg-purple-700 text-white',
    success: 'bg-green-600 hover:bg-green-700 text-white',
    warning: 'bg-yellow-600 hover:bg-yellow-700 text-white',
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Quick Actions</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-2 gap-3">
          {actions.map((action, index) => (
            <button
              key={index}
              onClick={action.onClick}
              className={cn(
                'p-4 rounded-lg transition-all flex flex-col items-center justify-center space-y-2',
                variantClasses[action.variant || 'primary']
              )}
            >
              <span className="text-3xl">{action.icon}</span>
              <span className="text-sm font-medium">{action.label}</span>
            </button>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}

interface StockStatusItem {
  material_code: string
  material_name: string
  current_stock: number
  minimum_stock: number
  uom: string
  status: 'safe' | 'warning' | 'critical' | 'debt'
}

interface MaterialStockCardProps {
  title: string
  items: StockStatusItem[]
  maxItems?: number
  onViewDetails?: (item: StockStatusItem) => void
}

export const MaterialStockCard: React.FC<MaterialStockCardProps> = ({
  title,
  items,
  maxItems = 5,
  onViewDetails,
}) => {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'safe':
        return { bg: 'bg-green-100', text: 'text-green-800', icon: '🟢' }
      case 'warning':
        return { bg: 'bg-yellow-100', text: 'text-yellow-800', icon: '🟡' }
      case 'critical':
        return { bg: 'bg-red-100', text: 'text-red-800', icon: '🔴' }
      case 'debt':
        return { bg: 'bg-black', text: 'text-white', icon: '⚫' }
      default:
        return { bg: 'bg-gray-100', text: 'text-gray-800', icon: '⚪' }
    }
  }

  const displayItems = items.slice(0, maxItems)

  return (
    <Card>
      <CardHeader>
        <CardTitle>{title}</CardTitle>
      </CardHeader>
      <CardContent>
        {displayItems.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <p>✅ All materials at safe levels</p>
          </div>
        ) : (
          <div className="space-y-3">
            {displayItems.map((item, index) => {
              const colors = getStatusColor(item.status)
              const percentage = (item.current_stock / item.minimum_stock) * 100

              return (
                <div
                  key={index}
                  className={cn(
                    'p-3 rounded-md cursor-pointer transition-all hover:shadow-md',
                    colors.bg,
                    colors.text
                  )}
                  onClick={() => onViewDetails?.(item)}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <div className="flex items-center">
                        <span className="mr-2">{colors.icon}</span>
                        <p className="font-medium text-sm">[{item.material_code}]</p>
                      </div>
                      <p className="text-sm mt-1">{item.material_name}</p>
                      <p className="text-xs mt-1">
                        Stock: {item.current_stock} {item.uom} | Min: {item.minimum_stock}{' '}
                        {item.uom}
                      </p>
                    </div>
                    <div className="text-right ml-4">
                      <p className="text-lg font-bold">
                        {percentage.toFixed(1)}%
                      </p>
                      {item.status === 'debt' && (
                        <p className="text-xs font-bold mt-1">DEBT!</p>
                      )}
                    </div>
                  </div>
                </div>
              )
            })}
          </div>
        )}
      </CardContent>
    </Card>
  )
}
