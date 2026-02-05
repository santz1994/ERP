import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { DayPicker } from 'react-day-picker';
import 'react-day-picker/dist/style.css';
import toast from 'react-hot-toast';
import { api } from '../../api';
import { Card, CardHeader, CardTitle, CardContent } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Badge } from '../../components/ui/badge';
import { cn, formatDate, formatNumber } from '../../lib/utils';

/**
 * Production Calendar Page
 * 
 * Features:
 * - Monthly calendar view per department
 * - Daily production output display
 * - Date cell color coding by achievement
 * - Click date to input production
 * - Department tabs (Cutting, Embroidery, Sewing, Finishing, Packing)
 * - Real-time data refresh
 * 
 * Business Logic:
 * - Calendar-based daily input (NOT cumulative per entry)
 * - Each date shows total produced that day
 * - Color coding: Green (>100%), Yellow (75-100%), Red (<75%), Gray (no data)
 * - Hover shows details (SPK, Good Output, Defects)
 */

type Department = 'CUTTING' | 'EMBROIDERY' | 'SEWING' | 'FINISHING' | 'PACKING';

interface DailyProduction {
  date: string;
  spkNumber: string;
  articleCode: string;
  goodOutput: number;
  defectQty: number;
  targetDaily: number;
  achievementPercent: number;
}

interface CalendarData {
  [date: string]: DailyProduction[];
}

const DEPARTMENTS: { id: Department; label: string; icon: string }[] = [
  { id: 'CUTTING', label: 'Cutting', icon: '✂️' },
  { id: 'EMBROIDERY', label: 'Embroidery', icon: '🧵' },
  { id: 'SEWING', label: 'Sewing', icon: '👕' },
  { id: 'FINISHING', label: 'Finishing', icon: '✨' },
  { id: 'PACKING', label: 'Packing', icon: '📦' },
];

export default function ProductionCalendarPage() {
  const navigate = useNavigate();
  const [selectedDept, setSelectedDept] = useState<Department>('CUTTING');
  const [selectedMonth, setSelectedMonth] = useState(new Date());
  const [selectedDate, setSelectedDate] = useState<Date | undefined>();

  // Fetch calendar data
  const { data: calendarData, isLoading } = useQuery<CalendarData>({
    queryKey: ['production-calendar', selectedDept, selectedMonth.getMonth(), selectedMonth.getFullYear()],
    queryFn: () => api.production.getCalendar(
      selectedDept,
      selectedMonth.getFullYear(),
      selectedMonth.getMonth() + 1
    ),
    refetchInterval: 60000, // Refresh every minute
  });

  // Get color for date cell based on achievement
  const getDateColor = (date: Date): string => {
    const dateStr = date.toISOString().split('T')[0];
    const dayData = calendarData?.[dateStr];
    
    if (!dayData || dayData.length === 0) return 'bg-gray-100 text-gray-400';
    
    const totalAchievement = dayData.reduce((sum, d) => sum + d.achievementPercent, 0) / dayData.length;
    
    if (totalAchievement >= 100) return 'bg-green-100 text-green-800 font-semibold';
    if (totalAchievement >= 75) return 'bg-yellow-100 text-yellow-800 font-semibold';
    if (totalAchievement >= 50) return 'bg-orange-100 text-orange-800 font-semibold';
    return 'bg-red-100 text-red-800 font-semibold';
  };

  // Custom day content with production data
  const renderDayContent = (date: Date) => {
    const dateStr = date.toISOString().split('T')[0];
    const dayData = calendarData?.[dateStr];
    const totalProduced = dayData?.reduce((sum, d) => sum + d.goodOutput, 0) || 0;

    return (
      <div className="relative w-full h-full flex flex-col items-center justify-center p-1">
        <span className="text-sm">{date.getDate()}</span>
        {dayData && dayData.length > 0 && (
          <span className="text-xs font-bold mt-1">
            {formatNumber(totalProduced)}
          </span>
        )}
      </div>
    );
  };

  // Handle date click
  const handleDateClick = (date: Date | undefined) => {
    if (!date) return;
    setSelectedDate(date);
  };

  // Get selected date details
  const selectedDateStr = selectedDate?.toISOString().split('T')[0];
  const selectedDayData = selectedDateStr ? calendarData?.[selectedDateStr] : undefined;

  return (
    <div className="p-6 space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Production Calendar</h1>
          <p className="text-gray-600 mt-1">
            Track daily production output per department
          </p>
        </div>
        <Button
          variant="primary"
          onClick={() => navigate(`/production/input/${selectedDept.toLowerCase()}`)}
        >
          ➕ Input Production
        </Button>
      </div>

      {/* Department Tabs */}
      <Card variant="bordered">
        <CardContent className="p-4">
          <div className="flex items-center gap-2 flex-wrap">
            {DEPARTMENTS.map((dept) => (
              <button
                key={dept.id}
                onClick={() => setSelectedDept(dept.id)}
                className={cn(
                  'px-6 py-3 rounded-lg font-semibold transition-all',
                  selectedDept === dept.id
                    ? 'bg-blue-500 text-white shadow-lg'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                )}
              >
                <span className="mr-2">{dept.icon}</span>
                {dept.label}
              </button>
            ))}
          </div>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Calendar View */}
        <div className="lg:col-span-2">
          <Card variant="bordered">
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle>📅 {selectedMonth.toLocaleString('en-US', { month: 'long', year: 'numeric' })}</CardTitle>
                <div className="flex items-center gap-2">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => {
                      const prev = new Date(selectedMonth);
                      prev.setMonth(prev.getMonth() - 1);
                      setSelectedMonth(prev);
                    }}
                  >
                    ← Prev
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setSelectedMonth(new Date())}
                  >
                    Today
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => {
                      const next = new Date(selectedMonth);
                      next.setMonth(next.getMonth() + 1);
                      setSelectedMonth(next);
                    }}
                  >
                    Next →
                  </Button>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              {isLoading ? (
                <div className="text-center py-12">
                  <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto"></div>
                  <p className="text-gray-600 mt-4">Loading calendar data...</p>
                </div>
              ) : (
                <div className="production-calendar">
                  <DayPicker
                    mode="single"
                    selected={selectedDate}
                    onSelect={handleDateClick}
                    month={selectedMonth}
                    onMonthChange={setSelectedMonth}
                    modifiers={{
                      produced: (date) => {
                        const dateStr = date.toISOString().split('T')[0];
                        return !!calendarData?.[dateStr];
                      },
                    }}
                    modifiersClassNames={{
                      produced: 'has-production',
                    }}
                    components={{
                      DayContent: ({ date }) => renderDayContent(date),
                    }}
                    className="w-full"
                  />
                  
                  {/* Legend */}
                  <div className="mt-6 pt-4 border-t">
                    <p className="text-sm font-semibold text-gray-700 mb-3">Achievement Legend:</p>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                      <div className="flex items-center gap-2">
                        <div className="w-6 h-6 bg-green-100 border border-green-300 rounded"></div>
                        <span className="text-xs text-gray-700">≥100%</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <div className="w-6 h-6 bg-yellow-100 border border-yellow-300 rounded"></div>
                        <span className="text-xs text-gray-700">75-99%</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <div className="w-6 h-6 bg-orange-100 border border-orange-300 rounded"></div>
                        <span className="text-xs text-gray-700">50-74%</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <div className="w-6 h-6 bg-red-100 border border-red-300 rounded"></div>
                        <span className="text-xs text-gray-700">&lt;50%</span>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Selected Date Details */}
        <div className="space-y-4">
          <Card variant="bordered">
            <CardHeader>
              <CardTitle>
                {selectedDate ? formatDate(selectedDate.toISOString()) : 'Select a Date'}
              </CardTitle>
            </CardHeader>
            <CardContent>
              {selectedDate ? (
                selectedDayData && selectedDayData.length > 0 ? (
                  <div className="space-y-4">
                    {selectedDayData.map((data, idx) => (
                      <div key={idx} className="bg-gray-50 p-4 rounded-lg border border-gray-200">
                        <div className="flex items-center justify-between mb-2">
                          <p className="font-semibold text-gray-900">{data.spkNumber}</p>
                          <Badge
                            variant={
                              data.achievementPercent >= 100 ? 'success' :
                              data.achievementPercent >= 75 ? 'warning' : 'error'
                            }
                            size="sm"
                          >
                            {data.achievementPercent.toFixed(0)}%
                          </Badge>
                        </div>
                        <p className="text-sm text-gray-600 mb-3">{data.articleCode}</p>
                        
                        <div className="space-y-2 text-sm">
                          <div className="flex justify-between">
                            <span className="text-gray-600">Good Output:</span>
                            <span className="font-semibold text-green-700">
                              {formatNumber(data.goodOutput)} pcs
                            </span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-gray-600">Defect:</span>
                            <span className="font-semibold text-red-700">
                              {formatNumber(data.defectQty)} pcs
                            </span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-gray-600">Target:</span>
                            <span className="font-semibold text-gray-900">
                              {formatNumber(data.targetDaily)} pcs
                            </span>
                          </div>
                        </div>

                        <div className="mt-3 pt-3 border-t">
                          <div className="w-full bg-gray-200 rounded-full h-2">
                            <div
                              className={cn(
                                'h-2 rounded-full transition-all',
                                data.achievementPercent >= 100 ? 'bg-green-500' :
                                data.achievementPercent >= 75 ? 'bg-yellow-500' : 'bg-red-500'
                              )}
                              style={{ width: `${Math.min(data.achievementPercent, 100)}%` }}
                            />
                          </div>
                        </div>
                      </div>
                    ))}

                    <Button
                      variant="primary"
                      fullWidth
                      onClick={() => navigate(`/production/input/${selectedDept.toLowerCase()}?date=${selectedDateStr}`)}
                    >
                      ✏️ Edit Production
                    </Button>
                  </div>
                ) : (
                  <div className="text-center py-8">
                    <p className="text-gray-600 mb-4">No production data for this date.</p>
                    <Button
                      variant="primary"
                      onClick={() => navigate(`/production/input/${selectedDept.toLowerCase()}?date=${selectedDateStr}`)}
                    >
                      ➕ Input Production
                    </Button>
                  </div>
                )
              ) : (
                <div className="text-center py-8">
                  <p className="text-gray-500">Click a date on the calendar to view details.</p>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Monthly Summary */}
          <Card variant="bordered">
            <CardHeader>
              <CardTitle>📊 Monthly Summary</CardTitle>
            </CardHeader>
            <CardContent>
              {calendarData && (
                <div className="space-y-3">
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-gray-600">Total Days Produced:</span>
                    <span className="font-semibold text-gray-900">
                      {Object.keys(calendarData).length} days
                    </span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-gray-600">Total Output:</span>
                    <span className="font-semibold text-green-700">
                      {formatNumber(
                        Object.values(calendarData).flat().reduce((sum, d) => sum + d.goodOutput, 0)
                      )} pcs
                    </span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-gray-600">Total Defects:</span>
                    <span className="font-semibold text-red-700">
                      {formatNumber(
                        Object.values(calendarData).flat().reduce((sum, d) => sum + d.defectQty, 0)
                      )} pcs
                    </span>
                  </div>
                  <div className="pt-3 border-t">
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600">Avg Achievement:</span>
                      <span className="font-bold text-blue-700 text-lg">
                        {(
                          Object.values(calendarData).flat().reduce((sum, d) => sum + d.achievementPercent, 0) /
                          Object.values(calendarData).flat().length || 0
                        ).toFixed(1)}%
                      </span>
                    </div>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>

      <style>{`
        .production-calendar .rdp {
          --rdp-cell-size: 60px;
          --rdp-accent-color: #3b82f6;
        }
        .production-calendar .rdp-day {
          height: 60px;
          width: 60px;
        }
        .production-calendar .rdp-day_selected {
          background-color: #3b82f6 !important;
        }
        .production-calendar .has-production {
          font-weight: 600;
        }
      `}</style>
    </div>
  );
}
