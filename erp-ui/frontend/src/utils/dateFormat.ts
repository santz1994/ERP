/**
 * Date Formatting Utilities
 * ERP Quty Karunia - Standardized date handling
 * Date: 4 Februari 2026
 */

import { format, formatDistance, formatRelative, parseISO } from 'date-fns';
import { id } from 'date-fns/locale';

/**
 * Standardized date format patterns used across the application
 */
export const dateFormats = {
  /** 04/02/26 - Compact format for tables */
  short: 'dd/MM/yy',
  
  /** 04 Feb 2026 - Standard format for UI */
  medium: 'dd MMM yyyy',
  
  /** 04 Februari 2026 - Full month name */
  long: 'dd MMMM yyyy',
  
  /** Selasa, 04 Februari 2026 - Full weekday and date */
  full: 'EEEE, dd MMMM yyyy',
  
  /** 14:30 - Time only */
  time: 'HH:mm',
  
  /** 14:30:45 - Time with seconds */
  timeFull: 'HH:mm:ss',
  
  /** 04/02/26 14:30 - Date and time compact */
  datetime: 'dd/MM/yy HH:mm',
  
  /** 04 Feb 2026, 14:30 - Date and time readable */
  datetimeMedium: 'dd MMM yyyy, HH:mm',
  
  /** 2026-02-04 - ISO date (for APIs) */
  isoDate: 'yyyy-MM-dd',
  
  /** 2026-02-04T14:30:00 - ISO datetime (for APIs) */
  iso: "yyyy-MM-dd'T'HH:mm:ss",
  
  /** 05-2026 - Week format (for production planning) */
  week: "'Week' II-yyyy",
  
  /** Feb 2026 - Month and year */
  monthYear: 'MMM yyyy',
  
  /** Februari 2026 - Full month and year */
  monthYearLong: 'MMMM yyyy',
} as const;

/**
 * Format a date using predefined patterns
 * 
 * @param date - Date string or Date object
 * @param pattern - Format pattern key (default: 'medium')
 * @returns Formatted date string or '-' if invalid
 * 
 * @example
 * formatDate('2026-02-04', 'medium')  // '04 Feb 2026'
 * formatDate(new Date(), 'datetime')  // '04/02/26 14:30'
 * formatDate('2026-02-04', 'week')    // 'Week 05-2026'
 */
export const formatDate = (
  date: string | Date | null | undefined, 
  pattern: keyof typeof dateFormats = 'medium'
): string => {
  if (!date) return '-';
  
  try {
    const dateObj = typeof date === 'string' ? parseISO(date) : date;
    return format(dateObj, dateFormats[pattern], { locale: id });
  } catch (error) {
    console.error('Invalid date format:', date, error);
    return '-';
  }
};

/**
 * Format date as relative time (e.g., "2 hours ago")
 * 
 * @param date - Date string or Date object
 * @returns Relative time string or '-' if invalid
 * 
 * @example
 * formatRelativeDate('2026-02-04T12:00:00')  // '2 jam yang lalu'
 * formatRelativeDate(new Date())             // 'kurang dari satu menit yang lalu'
 */
export const formatRelativeDate = (date: string | Date | null | undefined): string => {
  if (!date) return '-';
  
  try {
    const dateObj = typeof date === 'string' ? parseISO(date) : date;
    return formatDistance(dateObj, new Date(), { 
      addSuffix: true, 
      locale: id 
    });
  } catch (error) {
    console.error('Invalid date format:', date, error);
    return '-';
  }
};

/**
 * Format date relative to now with more context
 * (e.g., "kemarin jam 14:30", "hari ini jam 09:00")
 * 
 * @param date - Date string or Date object
 * @returns Contextual relative date or '-' if invalid
 * 
 * @example
 * formatRelativeWithContext('2026-02-03T14:30:00')  // 'kemarin jam 14:30'
 * formatRelativeWithContext('2026-02-04T09:00:00')  // 'hari ini jam 09:00'
 */
export const formatRelativeWithContext = (date: string | Date | null | undefined): string => {
  if (!date) return '-';
  
  try {
    const dateObj = typeof date === 'string' ? parseISO(date) : date;
    return formatRelative(dateObj, new Date(), { locale: id });
  } catch (error) {
    console.error('Invalid date format:', date, error);
    return '-';
  }
};

/**
 * Format date as week number (Week 05-2026)
 * 
 * @param date - Date string or Date object
 * @returns Week format or '-' if invalid
 * 
 * @example
 * formatWeek('2026-02-04')  // 'Week 05-2026'
 */
export const formatWeek = (date: string | Date | null | undefined): string => {
  if (!date) return '-';
  
  try {
    const dateObj = typeof date === 'string' ? parseISO(date) : date;
    return format(dateObj, dateFormats.week, { locale: id });
  } catch (error) {
    console.error('Invalid date format:', date, error);
    return '-';
  }
};

/**
 * Format date as month-year (Feb 2026)
 * 
 * @param date - Date string or Date object
 * @param long - Use full month name if true
 * @returns Month-year format or '-' if invalid
 * 
 * @example
 * formatMonthYear('2026-02-04')        // 'Feb 2026'
 * formatMonthYear('2026-02-04', true)  // 'Februari 2026'
 */
export const formatMonthYear = (
  date: string | Date | null | undefined, 
  long: boolean = false
): string => {
  if (!date) return '-';
  
  try {
    const dateObj = typeof date === 'string' ? parseISO(date) : date;
    return format(dateObj, long ? dateFormats.monthYearLong : dateFormats.monthYear, { locale: id });
  } catch (error) {
    console.error('Invalid date format:', date, error);
    return '-';
  }
};

/**
 * Parse date string to Date object safely
 * 
 * @param dateStr - Date string (ISO format recommended)
 * @returns Date object or null if invalid
 * 
 * @example
 * const date = parseDate('2026-02-04');
 * if (date) {
 *   // Use date
 * }
 */
export const parseDate = (dateStr: string | null | undefined): Date | null => {
  if (!dateStr) return null;
  
  try {
    return parseISO(dateStr);
  } catch (error) {
    console.error('Invalid date string:', dateStr, error);
    return null;
  }
};

/**
 * Get current date in ISO format (for API calls)
 * 
 * @returns Current date as 'YYYY-MM-DD'
 * 
 * @example
 * const today = getCurrentDateISO();  // '2026-02-04'
 */
export const getCurrentDateISO = (): string => {
  return format(new Date(), dateFormats.isoDate);
};

/**
 * Get current datetime in ISO format (for API calls)
 * 
 * @returns Current datetime as 'YYYY-MM-DDTHH:mm:ss'
 * 
 * @example
 * const now = getCurrentDateTimeISO();  // '2026-02-04T14:30:00'
 */
export const getCurrentDateTimeISO = (): string => {
  return format(new Date(), dateFormats.iso);
};

/**
 * Check if date is today
 * 
 * @param date - Date string or Date object
 * @returns True if date is today
 * 
 * @example
 * isToday('2026-02-04')  // true if today is Feb 4, 2026
 */
export const isToday = (date: string | Date): boolean => {
  const dateObj = typeof date === 'string' ? parseISO(date) : date;
  const today = new Date();
  
  return dateObj.getDate() === today.getDate() &&
    dateObj.getMonth() === today.getMonth() &&
    dateObj.getFullYear() === today.getFullYear();
};

/**
 * Check if date is in the past
 * 
 * @param date - Date string or Date object
 * @returns True if date is before now
 * 
 * @example
 * isPast('2026-01-01')  // true if current date is after Jan 1, 2026
 */
export const isPast = (date: string | Date): boolean => {
  const dateObj = typeof date === 'string' ? parseISO(date) : date;
  return dateObj < new Date();
};

/**
 * Check if date is in the future
 * 
 * @param date - Date string or Date object
 * @returns True if date is after now
 * 
 * @example
 * isFuture('2026-12-31')  // true if current date is before Dec 31, 2026
 */
export const isFuture = (date: string | Date): boolean => {
  const dateObj = typeof date === 'string' ? parseISO(date) : date;
  return dateObj > new Date();
};

/**
 * Format duration between two dates
 * 
 * @param startDate - Start date
 * @param endDate - End date (defaults to now)
 * @returns Duration string
 * 
 * @example
 * formatDuration('2026-02-04T10:00:00', '2026-02-04T14:30:00')  // '4 jam 30 menit'
 */
export const formatDuration = (
  startDate: string | Date,
  endDate: string | Date = new Date()
): string => {
  const start = typeof startDate === 'string' ? parseISO(startDate) : startDate;
  const end = typeof endDate === 'string' ? parseISO(endDate) : endDate;
  
  return formatDistance(start, end, { locale: id });
};
