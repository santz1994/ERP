/**
 * Copyright (c) 2026 PT Quty Karunia - All Rights Reserved
 * File: dateFormatters.ts | Date: 2026-02-06
 * Purpose: Shared Date Formatting Utilities (Phase 3 - Code Duplication Elimination)
 * Usage: Import from '@/utils/dateFormatters' instead of calling date-fns directly
 */

import { format, parseISO, formatDistance, formatDistanceToNow, isValid, addDays, startOfWeek, endOfWeek } from 'date-fns'
import { id as indonesianLocale } from 'date-fns/locale'

/**
 * Format date to Indonesian locale (dd MMMM yyyy)
 * Example: "05 Februari 2026"
 */
export const formatDateIndonesian = (date: string | Date | null): string => {
  if (!date) return '-'
  try {
    const dateObj = typeof date === 'string' ? parseISO(date) : date
    if (!isValid(dateObj)) return '-'
    return format(dateObj, 'dd MMMM yyyy', { locale: indonesianLocale })
  } catch {
    return '-'
  }
}

/**
 * Format date to short format (dd/MM/yyyy)
 * Example: "05/02/2026"
 */
export const formatDateShort = (date: string | Date | null): string => {
  if (!date) return '-'
  try {
    const dateObj = typeof date === 'string' ? parseISO(date) : date
    if (!isValid(dateObj)) return '-'
    return format(dateObj, 'dd/MM/yyyy')
  } catch {
    return '-'
  }
}

/**
 * Format datetime to Indonesian locale with time (dd MMMM yyyy, HH:mm)
 * Example: "05 Februari 2026, 14:30"
 */
export const formatDateTimeIndonesian = (date: string | Date | null): string => {
  if (!date) return '-'
  try {
    const dateObj = typeof date === 'string' ? parseISO(date) : date
    if (!isValid(dateObj)) return '-'
    return format(dateObj, 'dd MMMM yyyy, HH:mm', { locale: indonesianLocale })
  } catch {
    return '-'
  }
}

/**
 * Format datetime to short format with time (dd/MM/yyyy HH:mm)
 * Example: "05/02/2026 14:30"
 */
export const formatDateTimeShort = (date: string | Date | null): string => {
  if (!date) return '-'
  try {
    const dateObj = typeof date === 'string' ? parseISO(date) : date
    if (!isValid(dateObj)) return '-'
    return format(dateObj, 'dd/MM/yyyy HH:mm')
  } catch {
    return '-'
  }
}

/**
 * Format time only (HH:mm:ss)
 * Example: "14:30:25"
 */
export const formatTime = (date: string | Date | null): string => {
  if (!date) return '-'
  try {
    const dateObj = typeof date === 'string' ? parseISO(date) : date
    if (!isValid(dateObj)) return '-'
    return format(dateObj, 'HH:mm:ss')
  } catch {
    return '-'
  }
}

/**
 * Format time only (short) (HH:mm)
 * Example: "14:30"
 */
export const formatTimeShort = (date: string | Date | null): string => {
  if (!date) return '-'
  try {
    const dateObj = typeof date === 'string' ? parseISO(date) : date
    if (!isValid(dateObj)) return '-'
    return format(dateObj, 'HH:mm')
  } catch {
    return '-'
  }
}

/**
 * Format date for API calls (yyyy-MM-dd)
 * Example: "2026-02-05"
 */
export const formatDateForAPI = (date: string | Date | null): string => {
  if (!date) return ''
  try {
    const dateObj = typeof date === 'string' ? parseISO(date) : date
    if (!isValid(dateObj)) return ''
    return format(dateObj, 'yyyy-MM-dd')
  } catch {
    return ''
  }
}

/**
 * Format datetime for API calls (yyyy-MM-dd HH:mm:ss)
 * Example: "2026-02-05 14:30:25"
 */
export const formatDateTimeForAPI = (date: string | Date | null): string => {
  if (!date) return ''
  try {
    const dateObj = typeof date === 'string' ? parseISO(date) : date
    if (!isValid(dateObj)) return ''
    return format(dateObj, 'yyyy-MM-dd HH:mm:ss')
  } catch {
    return ''
  }
}

/**
 * Format relative time (e.g., "2 hours ago", "in 3 days")
 * Example: "2 jam yang lalu"
 */
export const formatRelativeTime = (date: string | Date | null): string => {
  if (!date) return '-'
  try {
    const dateObj = typeof date === 'string' ? parseISO(date) : date
    if (!isValid(dateObj)) return '-'
    return formatDistanceToNow(dateObj, { addSuffix: true, locale: indonesianLocale })
  } catch {
    return '-'
  }
}

/**
 * Format distance between two dates (e.g., "2 hours")
 * Example: "2 jam"
 */
export const formatDateDistance = (dateLeft: string | Date, dateRight: string | Date): string => {
  try {
    const leftObj = typeof dateLeft === 'string' ? parseISO(dateLeft) : dateLeft
    const rightObj = typeof dateRight === 'string' ? parseISO(dateRight) : dateRight
    if (!isValid(leftObj) || !isValid(rightObj)) return '-'
    return formatDistance(leftObj, rightObj, { locale: indonesianLocale })
  } catch {
    return '-'
  }
}

/**
 * Get week number from date (ISO week)
 * Example: 5 (for 5th week of year)
 */
export const getWeekNumber = (date: string | Date): number => {
  try {
    const dateObj = typeof date === 'string' ? parseISO(date) : date
    if (!isValid(dateObj)) return 0
    return parseInt(format(dateObj, 'w'))
  } catch {
    return 0
  }
}

/**
 * Get ISO week-year (format: "2026-W05")
 * Example: "2026-W05"
 */
export const getISOWeekYear = (date: string | Date): string => {
  try {
    const dateObj = typeof date === 'string' ? parseISO(date) : date
    if (!isValid(dateObj)) return ''
    return format(dateObj, 'YYYY-\'W\'ww')
  } catch {
    return ''
  }
}

/**
 * Format date for display with weekday (EEEE, dd MMMM yyyy)
 * Example: "Kamis, 05 Februari 2026"
 */
export const formatDateWithWeekday = (date: string | Date | null): string => {
  if (!date) return '-'
  try {
    const dateObj = typeof date === 'string' ? parseISO(date) : date
    if (!isValid(dateObj)) return '-'
    return format(dateObj, 'EEEE, dd MMMM yyyy', { locale: indonesianLocale })
  } catch {
    return '-'
  }
}

/**
 * Check if date is today
 */
export const isToday = (date: string | Date): boolean => {
  try {
    const dateObj = typeof date === 'string' ? parseISO(date) : date
    if (!isValid(dateObj)) return false
    const today = new Date()
    return format(dateObj, 'yyyy-MM-dd') === format(today, 'yyyy-MM-dd')
  } catch {
    return false
  }
}

/**
 * Get today's date formatted
 * Example: "05 Februari 2026"
 */
export const getTodayFormatted = (): string => {
  return formatDateIndonesian(new Date())
}

/**
 * Get current datetime formatted
 * Example: "05 Februari 2026, 14:30"
 */
export const getNowFormatted = (): string => {
  return formatDateTimeIndonesian(new Date())
}

/**
 * Add days to date and format
 * Example: addDaysAndFormat('2026-02-05', 7) => "12 Februari 2026"
 */
export const addDaysAndFormat = (date: string | Date, days: number): string => {
  try {
    const dateObj = typeof date === 'string' ? parseISO(date) : date
    if (!isValid(dateObj)) return '-'
    const newDate = addDays(dateObj, days)
    return formatDateIndonesian(newDate)
  } catch {
    return '-'
  }
}

/**
 * Get week start date (Monday)
 * Example: getWeekStart('2026-02-05') => "2026-02-03"
 */
export const getWeekStart = (date: string | Date): string => {
  try {
    const dateObj = typeof date === 'string' ? parseISO(date) : date
    if (!isValid(dateObj)) return ''
    const weekStart = startOfWeek(dateObj, { weekStartsOn: 1 }) // Monday
    return formatDateForAPI(weekStart)
  } catch {
    return ''
  }
}

/**
 * Get week end date (Sunday)
 * Example: getWeekEnd('2026-02-05') => "2026-02-09"
 */
export const getWeekEnd = (date: string | Date): string => {
  try {
    const dateObj = typeof date === 'string' ? parseISO(date) : date
    if (!isValid(dateObj)) return ''
    const weekEnd = endOfWeek(dateObj, { weekStartsOn: 1 }) // Sunday
    return formatDateForAPI(weekEnd)
  } catch {
    return ''
  }
}

/**
 * Format month-year (MMMM yyyy)
 * Example: "Februari 2026"
 */
export const formatMonthYear = (date: string | Date | null): string => {
  if (!date) return '-'
  try {
    const dateObj = typeof date === 'string' ? parseISO(date) : date
    if (!isValid(dateObj)) return '-'
    return format(dateObj, 'MMMM yyyy', { locale: indonesianLocale })
  } catch {
    return '-'
  }
}

/**
 * Export all date formatters as a single object (alternative usage pattern)
 */
export const DateFormat = {
  indonesian: formatDateIndonesian,
  short: formatDateShort,
  dateTimeIndonesian: formatDateTimeIndonesian,
  dateTimeShort: formatDateTimeShort,
  time: formatTime,
  timeShort: formatTimeShort,
  forAPI: formatDateForAPI,
  dateTimeForAPI: formatDateTimeForAPI,
  relative: formatRelativeTime,
  distance: formatDateDistance,
  withWeekday: formatDateWithWeekday,
  monthYear: formatMonthYear,
  today: getTodayFormatted,
  now: getNowFormatted
}

/**
 * Export week utilities as a single object
 */
export const WeekUtils = {
  getNumber: getWeekNumber,
  getISOWeekYear: getISOWeekYear,
  getStart: getWeekStart,
  getEnd: getWeekEnd,
  isToday: isToday,
  addDays: addDaysAndFormat
}
