/**
 * Copyright (c) 2026 PT Quty Karunia - All Rights Reserved
 * File: index.ts | Date: 2026-02-06
 * Purpose: Central export for all shared utilities (Phase 3 - Code Duplication Elimination)
 * Usage: Import from '@/utils' for convenience
 */

// Status Badge Utilities
export * from './statusBadge'

// Date Formatting Utilities
export * from './dateFormatters'

// Re-export commonly used utilities for convenience
export {
  getWorkOrderStatusBadgeClass,
  getMOStatusBadgeClass,
  getPOStatusBadgeClass,
  getQCStatusBadgeClass,
  getStockStatusBadgeClass,
  getReworkStatusBadgeClass,
  getPriorityBadgeClass,
  getStockAlertBadgeClass,
  StatusBadge
} from './statusBadge'

export {
  formatDateIndonesian,
  formatDateShort,
  formatDateTimeIndonesian,
  formatDateTimeShort,
  formatTime,
  formatTimeShort,
  formatDateForAPI,
  formatDateTimeForAPI,
  formatRelativeTime,
  formatDateDistance,
  formatDateWithWeekday,
  formatMonthYear,
  getWeekNumber,
  getISOWeekYear,
  getWeekStart,
  getWeekEnd,
  isToday,
  getTodayFormatted,
  getNowFormatted,
  addDaysAndFormat,
  DateFormat,
  WeekUtils
} from './dateFormatters'
