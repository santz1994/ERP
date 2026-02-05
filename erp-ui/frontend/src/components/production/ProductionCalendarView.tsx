/**
 * Copyright (c) 2026 PT Quty Karunia / Daniel Rizaldy - All Rights Reserved
 * File: ProductionCalendarView.tsx | Author: Daniel Rizaldy | Date: 2026-02-04
 * Production Calendar View with Daily Progress Input
 */

import { useState } from 'react';
import { format, startOfMonth, endOfMonth, eachDayOfInterval, isSameMonth, isSameDay, isWeekend } from 'date-fns';
import { Calendar, ChevronLeft, ChevronRight } from 'lucide-react';

interface DailyProgress {
  date: string; // ISO format YYYY-MM-DD
  production_qty: number;
  good_qty: number;
  defect_qty: number;
  notes?: string;
  defect_reasons?: Record<string, number>;
}

interface ProductionCalendarViewProps {
  workOrderId: number;
  targetQty: number;
  dailyProgress: DailyProgress[];
  onDateClick: (date: Date) => void;
  className?: string;
}

export const ProductionCalendarView: React.FC<ProductionCalendarViewProps> = ({
  workOrderId,
  targetQty,
  dailyProgress,
  onDateClick,
  className = ''
}) => {
  const [currentMonth, setCurrentMonth] = useState(new Date());

  const monthStart = startOfMonth(currentMonth);
  const monthEnd = endOfMonth(currentMonth);
  const daysInMonth = eachDayOfInterval({ start: monthStart, end: monthEnd });

  const previousMonth = () => {
    setCurrentMonth(new Date(currentMonth.getFullYear(), currentMonth.getMonth() - 1, 1));
  };

  const nextMonth = () => {
    setCurrentMonth(new Date(currentMonth.getFullYear(), currentMonth.getMonth() + 1, 1));
  };

  const getDayProgress = (date: Date): DailyProgress | undefined => {
    const dateStr = format(date, 'yyyy-MM-dd');
    return dailyProgress.find(p => p.date === dateStr);
  };

  const getDayColor = (date: Date): string => {
    const progress = getDayProgress(date);
    const today = new Date();
    
    if (isWeekend(date)) {
      return 'bg-gray-100 text-gray-400'; // Weekend
    }
    
    if (!progress) {
      if (date < today) {
        return 'bg-white text-gray-500 hover:bg-gray-50'; // Past, no data
      }
      return 'bg-white text-gray-700 hover:bg-blue-50'; // Future/Today, no data yet
    }

    // Has production data
    const completionRate = targetQty > 0 ? (progress.production_qty / (targetQty / 30)) * 100 : 0; // Assume 30 working days
    
    if (completionRate >= 100) {
      return 'bg-green-100 text-green-800 border-green-300'; // ✅ Completed
    } else if (completionRate >= 50) {
      return 'bg-yellow-100 text-yellow-800 border-yellow-300'; // 🟡 Partial
    } else if (completionRate > 0) {
      return 'bg-orange-100 text-orange-800 border-orange-300'; // 🟠 Low output
    }
    
    return 'bg-red-100 text-red-800 border-red-300'; // 🔴 Problem
  };

  const totalProduced = dailyProgress.reduce((sum, p) => sum + p.production_qty, 0);
  const totalGood = dailyProgress.reduce((sum, p) => sum + p.good_qty, 0);
  const totalDefect = dailyProgress.reduce((sum, p) => sum + p.defect_qty, 0);
  const yieldRate = totalProduced > 0 ? (totalGood / totalProduced) * 100 : 0;

  // Get first day of month offset (0 = Sunday, 1 = Monday, etc.)
  const firstDayOfMonth = monthStart.getDay();

  return (
    <div className={`bg-white rounded-lg shadow-sm border border-gray-200 p-6 ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <Calendar className="w-6 h-6 text-blue-600" />
          <h3 className="text-xl font-bold text-gray-900">
            📅 Daily Progress - {format(currentMonth, 'MMMM yyyy')}
          </h3>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={previousMonth}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <ChevronLeft className="w-5 h-5 text-gray-600" />
          </button>
          <button
            onClick={nextMonth}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <ChevronRight className="w-5 h-5 text-gray-600" />
          </button>
        </div>
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-4 gap-4 mb-6">
        <div className="bg-blue-50 p-3 rounded-lg">
          <div className="text-xs text-blue-600 font-medium">Total Produced</div>
          <div className="text-2xl font-bold text-blue-900">{totalProduced}</div>
          <div className="text-xs text-blue-600">{((totalProduced / targetQty) * 100).toFixed(1)}% of target</div>
        </div>
        <div className="bg-green-50 p-3 rounded-lg">
          <div className="text-xs text-green-600 font-medium">Good Output</div>
          <div className="text-2xl font-bold text-green-900">{totalGood}</div>
          <div className="text-xs text-green-600">Yield: {yieldRate.toFixed(1)}%</div>
        </div>
        <div className="bg-red-50 p-3 rounded-lg">
          <div className="text-xs text-red-600 font-medium">Defects</div>
          <div className="text-2xl font-bold text-red-900">{totalDefect}</div>
          <div className="text-xs text-red-600">{totalProduced > 0 ? ((totalDefect / totalProduced) * 100).toFixed(1) : 0}% rate</div>
        </div>
        <div className="bg-purple-50 p-3 rounded-lg">
          <div className="text-xs text-purple-600 font-medium">Working Days</div>
          <div className="text-2xl font-bold text-purple-900">{dailyProgress.length}</div>
          <div className="text-xs text-purple-600">Avg: {dailyProgress.length > 0 ? Math.round(totalProduced / dailyProgress.length) : 0} pcs/day</div>
        </div>
      </div>

      {/* Calendar Grid */}
      <div className="border border-gray-200 rounded-lg overflow-hidden">
        {/* Day Headers */}
        <div className="grid grid-cols-7 bg-gray-50 border-b border-gray-200">
          {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map(day => (
            <div key={day} className="py-2 text-center text-xs font-semibold text-gray-600">
              {day}
            </div>
          ))}
        </div>

        {/* Calendar Days */}
        <div className="grid grid-cols-7">
          {/* Empty cells for days before month starts */}
          {Array.from({ length: firstDayOfMonth }).map((_, index) => (
            <div key={`empty-${index}`} className="aspect-square border-r border-b border-gray-200 bg-gray-50" />
          ))}
          
          {/* Days of the month */}
          {daysInMonth.map(day => {
            const progress = getDayProgress(day);
            const colorClass = getDayColor(day);
            const isToday = isSameDay(day, new Date());

            return (
              <button
                key={format(day, 'yyyy-MM-dd')}
                onClick={() => onDateClick(day)}
                className={`aspect-square border-r border-b border-gray-200 p-2 transition-all hover:scale-105 hover:shadow-md ${colorClass} ${
                  isToday ? 'ring-2 ring-blue-500 ring-inset' : ''
                } relative group`}
              >
                <div className="flex flex-col h-full">
                  <div className="text-sm font-semibold">{format(day, 'd')}</div>
                  {progress && (
                    <div className="mt-auto text-[10px] leading-tight">
                      <div className="font-bold">{progress.production_qty}</div>
                      <div className="text-[9px]">{progress.good_qty}</div>
                      {progress.defect_qty > 0 && (
                        <div className="text-[9px]">{progress.defect_qty}</div>
                      )}
                    </div>
                  )}
                </div>
                
                {/* Tooltip on hover */}
                {progress && (
                  <div className="hidden group-hover:block absolute z-10 -top-24 left-1/2 transform -translate-x-1/2 bg-gray-900 text-white text-xs rounded-lg px-3 py-2 shadow-xl w-48">
                    <div className="font-bold mb-1">{format(day, 'dd MMM yyyy')}</div>
                    <div>Production: {progress.production_qty} pcs</div>
                    <div>Good: {progress.good_qty} pcs</div>
                    <div>Defect: {progress.defect_qty} pcs</div>
                    {progress.notes && (
                      <div className="mt-1 italic text-gray-300">{progress.notes}</div>
                    )}
                  </div>
                )}
              </button>
            );
          })}
        </div>
      </div>

      {/* Legend */}
      <div className="mt-4 flex items-center gap-6 text-xs">
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 bg-green-100 border border-green-300 rounded"></div>
          <span className="text-gray-600">Completed (≥100%)</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 bg-yellow-100 border border-yellow-300 rounded"></div>
          <span className="text-gray-600">Partial (50-99%)</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 bg-red-100 border border-red-300 rounded"></div>
          <span className="text-gray-600">Delayed ({'<'}50%)</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 bg-gray-100 border border-gray-300 rounded"></div>
          <span className="text-gray-600">Weekend/Holiday</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 border-2 border-blue-500 rounded"></div>
          <span className="text-gray-600">Today</span>
        </div>
      </div>
    </div>
  );
};
