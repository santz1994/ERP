/**
 * PermissionBadge - Reusable Permission Display Component
 * Created: 2026-01-21 | Phase 16 Week 4 | PBAC Integration
 * Purpose: Visual display of user permissions with color coding and tooltips
 */

import React from 'react'
import { Shield, Calendar, AlertCircle } from 'lucide-react'

interface PermissionBadgeProps {
  code: string
  source?: 'role' | 'custom'
  expiresAt?: string | null
  description?: string
  size?: 'sm' | 'md' | 'lg'
  showIcon?: boolean
}

/**
 * Get module-specific color scheme
 */
const getModuleColor = (code: string): string => {
  const module = code.split('.')[0]
  
  const colorMap: Record<string, string> = {
    admin: 'purple',
    dashboard: 'blue',
    cutting: 'orange',
    sewing: 'pink',
    finishing: 'green',
    packing: 'yellow',
    ppic: 'indigo',
    warehouse: 'gray',
    purchasing: 'cyan',
    qc: 'red',
  }
  
  return colorMap[module] || 'gray'
}

/**
 * Check if permission is expired
 */
const isExpired = (expiresAt?: string | null): boolean => {
  if (!expiresAt) return false
  return new Date(expiresAt) < new Date()
}

/**
 * Format expiration date
 */
const formatExpiration = (expiresAt: string): string => {
  const date = new Date(expiresAt)
  const now = new Date()
  const diffMs = date.getTime() - now.getTime()
  const diffDays = Math.ceil(diffMs / (1000 * 60 * 60 * 24))
  
  if (diffDays < 0) return 'Expired'
  if (diffDays === 0) return 'Expires today'
  if (diffDays === 1) return 'Expires tomorrow'
  if (diffDays <= 7) return `Expires in ${diffDays} days`
  return date.toLocaleDateString()
}

export const PermissionBadge: React.FC<PermissionBadgeProps> = ({
  code,
  source = 'role',
  expiresAt,
  description,
  size = 'md',
  showIcon = true,
}) => {
  const color = getModuleColor(code)
  const expired = isExpired(expiresAt)
  
  // Size variants
  const sizeClasses = {
    sm: 'px-2 py-1 text-xs',
    md: 'px-3 py-1.5 text-sm',
    lg: 'px-4 py-2 text-base',
  }
  
  const iconSizes = {
    sm: 'w-3 h-3',
    md: 'w-4 h-4',
    lg: 'w-5 h-5',
  }
  
  // Color variants based on module
  const colorClasses: Record<string, string> = {
    purple: expired ? 'bg-gray-200 text-gray-500' : 'bg-purple-100 text-purple-700 border-purple-300',
    blue: expired ? 'bg-gray-200 text-gray-500' : 'bg-blue-100 text-blue-700 border-blue-300',
    orange: expired ? 'bg-gray-200 text-gray-500' : 'bg-orange-100 text-orange-700 border-orange-300',
    pink: expired ? 'bg-gray-200 text-gray-500' : 'bg-pink-100 text-pink-700 border-pink-300',
    green: expired ? 'bg-gray-200 text-gray-500' : 'bg-green-100 text-green-700 border-green-300',
    yellow: expired ? 'bg-gray-200 text-gray-500' : 'bg-yellow-100 text-yellow-700 border-yellow-300',
    indigo: expired ? 'bg-gray-200 text-gray-500' : 'bg-indigo-100 text-indigo-700 border-indigo-300',
    gray: expired ? 'bg-gray-200 text-gray-500' : 'bg-gray-100 text-gray-700 border-gray-300',
    cyan: expired ? 'bg-gray-200 text-gray-500' : 'bg-cyan-100 text-cyan-700 border-cyan-300',
    red: expired ? 'bg-gray-200 text-gray-500' : 'bg-red-100 text-red-700 border-red-300',
  }
  
  // Source badge
  const sourceBadge = source === 'custom' ? (
    <span className="ml-1 text-[10px] font-semibold px-1 py-0.5 bg-white rounded">
      CUSTOM
    </span>
  ) : null
  
  return (
    <div className="group relative inline-block">
      <div 
        className={`
          ${sizeClasses[size]} 
          ${colorClasses[color]}
          border rounded-lg font-mono font-medium
          flex items-center gap-1
          transition-all duration-200
          ${expired ? 'opacity-50 line-through' : 'hover:shadow-md'}
        `}
      >
        {showIcon && !expired && <Shield className={iconSizes[size]} />}
        {expired && <AlertCircle className={iconSizes[size]} />}
        <span>{code}</span>
        {sourceBadge}
        {expiresAt && !expired && (
          <Calendar className={`${iconSizes[size]} ml-1 opacity-50`} />
        )}
      </div>
      
      {/* Tooltip */}
      <div className="absolute z-50 bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-3 py-2 bg-gray-900 text-white text-xs rounded-lg shadow-lg opacity-0 group-hover:opacity-100 pointer-events-none transition-opacity whitespace-nowrap">
        {description && <div className="font-semibold mb-1">{description}</div>}
        <div className="text-gray-300">
          Source: <span className="font-medium">{source === 'role' ? 'Role-based' : 'Custom Grant'}</span>
        </div>
        {expiresAt && (
          <div className={expired ? 'text-red-400' : 'text-yellow-400'}>
            <Calendar className="w-3 h-3 inline mr-1" />
            {formatExpiration(expiresAt)}
          </div>
        )}
        {/* Tooltip arrow */}
        <div className="absolute top-full left-1/2 transform -translate-x-1/2 -mt-1 w-2 h-2 bg-gray-900 rotate-45"></div>
      </div>
    </div>
  )
}

/**
 * PermissionBadgeList - Display multiple permissions in a grid
 */
interface PermissionBadgeListProps {
  permissions: Array<{
    code: string
    source?: 'role' | 'custom'
    expiresAt?: string | null
    description?: string
  }>
  columns?: 1 | 2 | 3 | 4
  size?: 'sm' | 'md' | 'lg'
}

export const PermissionBadgeList: React.FC<PermissionBadgeListProps> = ({
  permissions,
  columns = 2,
  size = 'sm',
}) => {
  const gridClasses = {
    1: 'grid-cols-1',
    2: 'grid-cols-1 md:grid-cols-2',
    3: 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3',
    4: 'grid-cols-1 md:grid-cols-2 lg:grid-cols-4',
  }
  
  return (
    <div className={`grid ${gridClasses[columns]} gap-2`}>
      {permissions.map((perm) => (
        <PermissionBadge
          key={perm.code}
          code={perm.code}
          source={perm.source}
          expiresAt={perm.expiresAt}
          description={perm.description}
          size={size}
        />
      ))}
    </div>
  )
}

export default PermissionBadge
