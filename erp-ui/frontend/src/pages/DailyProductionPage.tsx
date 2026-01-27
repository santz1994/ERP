/**
 * Copyright (c) 2026 PT Quty Karunia / Daniel Rizaldy - All Rights Reserved
 * File: DailyProductionPage.tsx | Author: Daniel Rizaldy | Date: 2026-01-27
 * Phase: 5 (Production Execution) | Type: Web Portal for Daily Production Input
 * 
 * Purpose:
 * - Production staff input daily quantities perhari
 * - Calendar grid view untuk easy daily tracking
 * - Real-time cumulative total calculation
 * - Progress percentage tracking vs target
 * - Multi-day edit capability
 * 
 * Features:
 * - Month navigation (prev/next)
 * - Calendar grid (31 days)
 * - Daily input cells with hover effects
 * - Progress summary card
 * - Real-time calculations
 * - Confirm completion button
 * - Responsive design
 */

import { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { format, getDaysInMonth, startOfMonth, startOfToday, isSameDay } from 'date-fns';
import { 
  ChevronLeft,
  ChevronRight,
  TrendingUp,
  TrendingDown,
  Calendar,
  CheckCircle,
  AlertCircle,
  Clock,
  Zap
} from 'lucide-react';
import axios from 'axios';
import { usePermission } from '@/hooks/usePermission';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

interface DailyInput {
  date: string;
  quantity: number;
  notes?: string;
  status: 'CONFIRMED' | 'PENDING' | 'DRAFT';
}

interface SPKWithProgress {
  spk_id: number;
  spk_number: string;
  product_name: string;
  target_qty: number;
  actual_qty: number;
  completion_pct: number;
  daily_entries: DailyInput[];
  remaining_qty: number;
  estimated_days: number;
}

export default function DailyProductionPage() {
  const canInputProduction = usePermission('production.input_daily');
  const queryClient = useQueryClient();
  
  // State management
  const [currentDate, setCurrentDate] = useState(startOfToday());
  const [selectedSPK, setSelectedSPK] = useState<SPKWithProgress | null>(null);
  const [editingDay, setEditingDay] = useState<number | null>(null);
  const [editValue, setEditValue] = useState<string>('');
  const [dailyInputs, setDailyInputs] = useState<Map<number, DailyInput>>(new Map());

  // Get current month's first day
  const firstDay = startOfMonth(currentDate);
  const daysInMonth = getDaysInMonth(currentDate);

  // Fetch user's SPKs
  const { data: spkList, isLoading: spkLoading } = useQuery({
    queryKey: ['spks/my-spks'],
    queryFn: async () => {
      const response = await axios.get(`${API_BASE}/production/my-spks`, {
        headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
      });
      return response.data.data || [];
    }
  });

  // Fetch SPK progress when selected
  const { data: spkProgress, isLoading: progressLoading } = useQuery({
    queryKey: ['spk-progress', selectedSPK?.spk_id],
    queryFn: async () => {
      if (!selectedSPK) return null;
      const response = await axios.get(`${API_BASE}/production/spk/${selectedSPK.spk_id}/progress`, {
        headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
      });
      return response.data.data;
    },
    enabled: !!selectedSPK
  });

  // Update dailyInputs when progress data arrives
  useEffect(() => {
    if (spkProgress?.daily_entries) {
      const newInputs = new Map(dailyInputs);
      spkProgress.daily_entries.forEach((entry: DailyInput) => {
        const day = new Date(entry.date).getDate();
        newInputs.set(day, entry);
      });
      setDailyInputs(newInputs);
    }
  }, [spkProgress]);

  // Mutation: Record daily input
  const recordInputMutation = useMutation({
    mutationFn: async (data: { day: number; quantity: number }) => {
      if (!selectedSPK) throw new Error('No SPK selected');
      
      const productionDate = new Date(firstDay);
      productionDate.setDate(data.day);
      
      const response = await axios.post(
        `${API_BASE}/production/spk/${selectedSPK.spk_id}/daily-input`,
        {
          production_date: format(productionDate, 'yyyy-MM-dd'),
          input_qty: data.quantity,
          status: 'CONFIRMED'
        },
        {
          headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
        }
      );
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['spk-progress', selectedSPK?.spk_id] });
      setEditingDay(null);
      setEditValue('');
    }
  });

  // Handlers
  const handleMonthChange = (direction: 'prev' | 'next') => {
    const newDate = new Date(firstDay);
    if (direction === 'prev') {
      newDate.setMonth(newDate.getMonth() - 1);
    } else {
      newDate.setMonth(newDate.getMonth() + 1);
    }
    setCurrentDate(newDate);
    setDailyInputs(new Map());
  };

  const handleSelectSPK = (spk: SPKWithProgress) => {
    setSelectedSPK(spk);
    setEditingDay(null);
    setEditValue('');
  };

  const handleDayClick = (day: number) => {
    const existing = dailyInputs.get(day);
    setEditingDay(day);
    setEditValue(existing?.quantity.toString() || '');
  };

  const handleSaveDay = async (day: number) => {
    const quantity = parseInt(editValue, 10);
    if (isNaN(quantity) || quantity < 0) {
      alert('Please enter valid quantity');
      return;
    }
    
    recordInputMutation.mutate({ day, quantity });
  };

  const handleCancel = () => {
    setEditingDay(null);
    setEditValue('');
  };

  // Calculate cumulative and remaining
  const calculateStats = () => {
    let total = 0;
    dailyInputs.forEach(input => {
      if (input.status === 'CONFIRMED') {
        total += input.quantity;
      }
    });
    return {
      totalQty: total,
      remaining: Math.max(0, (selectedSPK?.target_qty || 0) - total),
      completion: (selectedSPK?.target_qty || 0) > 0 
        ? ((total / (selectedSPK?.target_qty || 1)) * 100).toFixed(1)
        : 0
    };
  };

  const stats = calculateStats();

  // Permission check
  if (!canInputProduction) {
    return (
      <div className="flex items-center justify-center h-screen bg-red-50">
        <div className="text-center">
          <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-gray-800">Access Denied</h2>
          <p className="text-gray-600 mt-2">You don't have permission to access daily production input</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-50">
      <div className="max-w-7xl mx-auto px-4 py-8">
        
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-2">
            <Calendar className="w-8 h-8 text-indigo-600" />
            <h1 className="text-3xl font-bold text-gray-900">Daily Production Input</h1>
          </div>
          <p className="text-gray-600">Track daily production quantities by calendar grid</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          
          {/* Left: SPK Selection */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Your SPKs</h2>
              
              {spkLoading ? (
                <div className="space-y-3">
                  {[1, 2, 3].map(i => (
                    <div key={i} className="h-16 bg-gray-100 rounded animate-pulse"></div>
                  ))}
                </div>
              ) : spkList && spkList.length > 0 ? (
                <div className="space-y-3 max-h-96 overflow-y-auto">
                  {spkList.map((spk: SPKWithProgress) => (
                    <button
                      key={spk.spk_id}
                      onClick={() => handleSelectSPK(spk)}
                      className={`w-full text-left p-3 rounded-lg border-2 transition-all ${
                        selectedSPK?.spk_id === spk.spk_id
                          ? 'border-indigo-500 bg-indigo-50'
                          : 'border-gray-200 bg-gray-50 hover:border-indigo-300'
                      }`}
                    >
                      <div className="font-semibold text-sm text-gray-900">{spk.spk_number}</div>
                      <div className="text-xs text-gray-600 mt-1 truncate">{spk.product_name}</div>
                      <div className="text-xs text-indigo-600 mt-1 font-medium">
                        {spk.completion_pct?.toFixed(1) || 0}% complete
                      </div>
                    </button>
                  ))}
                </div>
              ) : (
                <p className="text-gray-500 text-sm">No SPKs assigned to you</p>
              )}
            </div>
          </div>

          {/* Right: Daily Input Calendar */}
          <div className="lg:col-span-3">
            {selectedSPK ? (
              <div className="space-y-6">
                
                {/* Progress Summary Card */}
                <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    {/* Target */}
                    <div className="bg-blue-50 rounded-lg p-4 border border-blue-200">
                      <div className="text-sm text-gray-600 font-medium">Target Qty</div>
                      <div className="text-2xl font-bold text-blue-600 mt-1">
                        {selectedSPK.target_qty?.toLocaleString() || 0}
                      </div>
                    </div>

                    {/* Actual */}
                    <div className="bg-green-50 rounded-lg p-4 border border-green-200">
                      <div className="text-sm text-gray-600 font-medium">Actual Qty</div>
                      <div className="text-2xl font-bold text-green-600 mt-1">
                        {stats.totalQty.toLocaleString()}
                      </div>
                    </div>

                    {/* Remaining */}
                    <div className="bg-orange-50 rounded-lg p-4 border border-orange-200">
                      <div className="text-sm text-gray-600 font-medium">Remaining</div>
                      <div className="text-2xl font-bold text-orange-600 mt-1">
                        {stats.remaining.toLocaleString()}
                      </div>
                    </div>

                    {/* Progress % */}
                    <div className="bg-purple-50 rounded-lg p-4 border border-purple-200">
                      <div className="text-sm text-gray-600 font-medium">Progress</div>
                      <div className="text-2xl font-bold text-purple-600 mt-1">
                        {stats.completion}%
                      </div>
                    </div>
                  </div>

                  {/* Progress Bar */}
                  <div className="mt-6">
                    <div className="flex justify-between items-center mb-2">
                      <span className="text-sm font-medium text-gray-700">Completion Progress</span>
                      <span className="text-xs text-gray-500">
                        {stats.totalQty} / {selectedSPK.target_qty}
                      </span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-3">
                      <div
                        className="bg-indigo-600 h-3 rounded-full transition-all duration-500"
                        style={{ width: `${Math.min(100, parseFloat(stats.completion as string))}%` }}
                      ></div>
                    </div>
                  </div>
                </div>

                {/* Calendar Grid */}
                <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                  
                  {/* Month Navigation */}
                  <div className="flex items-center justify-between mb-6 pb-4 border-b">
                    <button
                      onClick={() => handleMonthChange('prev')}
                      className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                    >
                      <ChevronLeft className="w-5 h-5 text-gray-600" />
                    </button>
                    <h3 className="text-lg font-semibold text-gray-900">
                      {format(firstDay, 'MMMM yyyy')}
                    </h3>
                    <button
                      onClick={() => handleMonthChange('next')}
                      className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                    >
                      <ChevronRight className="w-5 h-5 text-gray-600" />
                    </button>
                  </div>

                  {/* Day Labels */}
                  <div className="grid grid-cols-7 gap-2 mb-4">
                    {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map(day => (
                      <div key={day} className="text-center text-xs font-semibold text-gray-600 py-2">
                        {day}
                      </div>
                    ))}
                  </div>

                  {/* Calendar Days */}
                  <div className="grid grid-cols-7 gap-2">
                    {/* Empty cells for days before month starts */}
                    {Array(firstDay.getDay()).fill(null).map((_, i) => (
                      <div key={`empty-${i}`} className="aspect-square"></div>
                    ))}

                    {/* Day cells */}
                    {Array.from({ length: daysInMonth }).map((_, i) => {
                      const day = i + 1;
                      const dayInput = dailyInputs.get(day);
                      const dayQty = dayInput?.quantity || 0;
                      const isEditing = editingDay === day;

                      return (
                        <div key={day} className="aspect-square">
                          {isEditing ? (
                            <div className="h-full bg-indigo-100 rounded-lg border-2 border-indigo-500 p-2 flex flex-col gap-1">
                              <input
                                type="number"
                                min="0"
                                value={editValue}
                                onChange={(e) => setEditValue(e.target.value)}
                                className="flex-1 px-2 py-1 border border-indigo-300 rounded text-sm"
                                autoFocus
                              />
                              <div className="flex gap-1">
                                <button
                                  onClick={() => handleSaveDay(day)}
                                  className="flex-1 bg-indigo-600 text-white text-xs rounded px-1 py-0.5 hover:bg-indigo-700"
                                  disabled={recordInputMutation.isPending}
                                >
                                  {recordInputMutation.isPending ? '...' : 'Save'}
                                </button>
                                <button
                                  onClick={handleCancel}
                                  className="flex-1 bg-gray-300 text-gray-700 text-xs rounded px-1 py-0.5 hover:bg-gray-400"
                                >
                                  Cancel
                                </button>
                              </div>
                            </div>
                          ) : (
                            <button
                              onClick={() => handleDayClick(day)}
                              className={`w-full h-full rounded-lg border-2 transition-all flex flex-col items-center justify-center cursor-pointer ${
                                dayQty > 0
                                  ? 'bg-green-50 border-green-500 hover:bg-green-100'
                                  : 'bg-gray-50 border-gray-200 hover:bg-gray-100'
                              }`}
                            >
                              <div className="text-sm font-semibold text-gray-900">{day}</div>
                              {dayQty > 0 && (
                                <div className="text-xs font-bold text-green-600 mt-0.5">
                                  {dayQty}
                                </div>
                              )}
                            </button>
                          )}
                        </div>
                      );
                    })}
                  </div>
                </div>

              </div>
            ) : (
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-12 flex flex-col items-center justify-center">
                <Calendar className="w-16 h-16 text-gray-300 mb-4" />
                <p className="text-lg text-gray-600 font-medium">Select an SPK to begin</p>
                <p className="text-gray-500 text-sm mt-2">Choose from your assigned SPKs on the left</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
