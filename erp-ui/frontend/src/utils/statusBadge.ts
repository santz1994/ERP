/**
 * Copyright (c) 2026 PT Quty Karunia - All Rights Reserved
 * File: statusBadge.ts | Date: 2026-02-06
 * Purpose: Shared Status Badge Utilities (Phase 3 - Code Duplication Elimination)
 * Usage: Import from '@/utils/statusBadge' instead of defining inline functions
 */

/**
 * Get Tailwind CSS classes for Work Order status badge
 * Used in: CuttingPage, SewingPage, FinishingPage, PackingPage, QCPage, ReworkManagementPage
 */
export const getWorkOrderStatusBadgeClass = (status: string): string => {
  switch (status) {
    case 'Pending':
      return 'bg-yellow-100 text-yellow-800'
    case 'Running':
      return 'bg-blue-100 text-blue-800'
    case 'Finished':
      return 'bg-green-100 text-green-800'
    case 'Cancelled':
      return 'bg-red-100 text-red-800'
    default:
      return 'bg-gray-100 text-gray-800'
  }
}

/**
 * Get Tailwind CSS classes for Manufacturing Order (MO) status badge
 * Used in: MOListPage, MODetailPage, PPICDashboard, CreateSPKPage
 */
export const getMOStatusBadgeClass = (status: string): string => {
  switch (status) {
    case 'Draft':
      return 'bg-gray-100 text-gray-800'
    case 'Confirmed':
      return 'bg-blue-100 text-blue-800'
    case 'In Production':
      return 'bg-indigo-100 text-indigo-800'
    case 'Completed':
      return 'bg-green-100 text-green-800'
    case 'Cancelled':
      return 'bg-red-100 text-red-800'
    default:
      return 'bg-gray-100 text-gray-800'
  }
}

/**
 * Get Tailwind CSS classes for Purchase Order (PO) status badge
 * Used in: PurchasingPage, POListPage, PODetailPage
 */
export const getPOStatusBadgeClass = (status: string): string => {
  switch (status) {
    case 'Draft':
      return 'bg-gray-100 text-gray-800'
    case 'Submitted':
      return 'bg-yellow-100 text-yellow-800'
    case 'Approved':
      return 'bg-blue-100 text-blue-800'
    case 'Partially Received':
      return 'bg-indigo-100 text-indigo-800'
    case 'Received':
      return 'bg-green-100 text-green-800'
    case 'Cancelled':
      return 'bg-red-100 text-red-800'
    default:
      return 'bg-gray-100 text-gray-800'
  }
}

/**
 * Get Tailwind CSS classes for QC Inspection status badge
 * Used in: QCPage, QCCheckpointPage, ReworkManagementPage
 */
export const getQCStatusBadgeClass = (status: string): string => {
  switch (status) {
    case 'Pending':
      return 'bg-yellow-100 text-yellow-800'
    case 'In Progress':
      return 'bg-blue-100 text-blue-800'
    case 'Pass':
      return 'bg-green-100 text-green-800'
    case 'Fail':
      return 'bg-red-100 text-red-800'
    case 'Rework':
      return 'bg-orange-100 text-orange-800'
    default:
      return 'bg-gray-100 text-gray-800'
  }
}

/**
 * Get Tailwind CSS classes for Stock status badge
 * Used in: WarehousePage, StockManagement, FinishgoodsPage
 */
export const getStockStatusBadgeClass = (status: string): string => {
  switch (status) {
    case 'Available':
      return 'bg-green-100 text-green-800'
    case 'Reserved':
      return 'bg-blue-100 text-blue-800'
    case 'Blocked':
      return 'bg-red-100 text-red-800'
    case 'Quarantine':
      return 'bg-yellow-100 text-yellow-800'
    default:
      return 'bg-gray-100 text-gray-800'
  }
}

/**
 * Get Tailwind CSS classes for Rework status badge
 * Used in: ReworkManagementPage, QCPage
 */
export const getReworkStatusBadgeClass = (status: string): string => {
  switch (status) {
    case 'Pending':
      return 'bg-yellow-100 text-yellow-800'
    case 'In Progress':
      return 'bg-blue-100 text-blue-800'
    case 'Completed':
      return 'bg-green-100 text-green-800'
    case 'Scrapped':
      return 'bg-red-100 text-red-800'
    default:
      return 'bg-gray-100 text-gray-800'
  }
}

/**
 * Get Tailwind CSS classes for Priority badge
 * Used in: MOListPage, CreateSPKPage, PPICDashboard
 */
export const getPriorityBadgeClass = (priority: string): string => {
  switch (priority) {
    case 'Urgent':
      return 'bg-red-100 text-red-800'
    case 'High':
      return 'bg-orange-100 text-orange-800'
    case 'Medium':
      return 'bg-yellow-100 text-yellow-800'
    case 'Low':
      return 'bg-green-100 text-green-800'
    default:
      return 'bg-gray-100 text-gray-800'
  }
}

/**
 * Get Tailwind CSS classes for Stock Alert Level badge
 * Used in: WarehousePage, StockManagement, Dashboard widgets
 */
export const getStockAlertBadgeClass = (level: string): string => {
  switch (level) {
    case 'Critical':
      return 'bg-red-100 text-red-800 animate-pulse'
    case 'Warning':
      return 'bg-yellow-100 text-yellow-800'
    case 'Normal':
      return 'bg-green-100 text-green-800'
    default:
      return 'bg-gray-100 text-gray-800'
  }
}

/**
 * Get status badge with icon (returns JSX-ready object)
 * Used for more advanced badge rendering with icons
 */
export const getStatusWithIcon = (status: string, type: 'workorder' | 'mo' | 'po' | 'qc' | 'stock' = 'workorder') => {
  let badgeClass = ''
  let icon = ''

  switch (type) {
    case 'workorder':
      badgeClass = getWorkOrderStatusBadgeClass(status)
      icon = status === 'Running' ? '▶️' : status === 'Finished' ? '✔️' : status === 'Pending' ? '⏳' : '❌'
      break
    case 'mo':
      badgeClass = getMOStatusBadgeClass(status)
      icon = status === 'In Production' ? '🏭' : status === 'Completed' ? '✔️' : status === 'Draft' ? '📝' : '❌'
      break
    case 'po':
      badgeClass = getPOStatusBadgeClass(status)
      icon = status === 'Received' ? '✔️' : status === 'Approved' ? '👍' : status === 'Submitted' ? '📤' : '📝'
      break
    case 'qc':
      badgeClass = getQCStatusBadgeClass(status)
      icon = status === 'Pass' ? '✔️' : status === 'Fail' ? '❌' : status === 'Rework' ? '🔧' : '⏳'
      break
    case 'stock':
      badgeClass = getStockStatusBadgeClass(status)
      icon = status === 'Available' ? '✔️' : status === 'Reserved' ? '🔒' : status === 'Blocked' ? '❌' : '⚠️'
      break
  }

  return { badgeClass, icon, status }
}

/**
 * Export all badge utilities as a single object (alternative usage pattern)
 */
export const StatusBadge = {
  workOrder: getWorkOrderStatusBadgeClass,
  mo: getMOStatusBadgeClass,
  po: getPOStatusBadgeClass,
  qc: getQCStatusBadgeClass,
  stock: getStockStatusBadgeClass,
  rework: getReworkStatusBadgeClass,
  priority: getPriorityBadgeClass,
  stockAlert: getStockAlertBadgeClass,
  withIcon: getStatusWithIcon
}
