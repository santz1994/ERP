"""
DailyProductionPage Component - Daily Production Input & Progress Tracking
Feature #3: Daily Production Input + Progress Tracking
Path: src/pages/DailyProductionPage.tsx
Session 35: Enhanced implementation with predictive completion

Features:
- Calendar grid view with daily input
- Progress tracking (daily vs cumulative)
- Predictive completion date calculation
- Behind-schedule alerts
- Real-time progress updates
"""

import React, { useState, useEffect } from 'react';
import { format, parseISO, addDays, differenceInDays } from 'date-fns';
import { Calendar, TrendingUp, AlertTriangle, CheckCircle, Clock, Loader } from 'lucide-react';

interface SPKProductionData {
  spk_id: number;
  article_id: string;
  target_qty: number;
  produced_qty: number;
  rejected_qty: number;
  target_completion_date: string;
  daily_inputs: DailyInput[];
}

interface DailyInput {
  input_date: string;
  qty_produced: number;
  qty_rejected: number;
  cumulative_qty: number;
  notes?: string;
}

export const DailyProductionPage: React.FC = () => {
  const [selectedSPK, setSelectedSPK] = useState<SPKProductionData | null>(null);
  const [dailyInputs, setDailyInputs] = useState<DailyInput[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [newInput, setNewInput] = useState({
    qty_produced: 0,
    qty_rejected: 0,
    notes: '',
  });

  // Calculations
  const calculateProgress = () => {
    if (!selectedSPK) return null;
    
    const produced = dailyInputs.length > 0 
      ? dailyInputs[dailyInputs.length - 1].cumulative_qty 
      : 0;
    
    const progress = (produced / selectedSPK.target_qty) * 100;
    const remaining = selectedSPK.target_qty - produced;
    
    return {
      produced,
      remaining,
      progress,
      isCompleted: progress >= 100,
    };
  };

  const calculatePredictiveCompletion = () => {
    if (!selectedSPK || dailyInputs.length < 2) return null;

    // Calculate daily average
    const firstDay = parseISO(dailyInputs[0].input_date);
    const lastDay = parseISO(dailyInputs[dailyInputs.length - 1].input_date);
    const daysElapsed = differenceInDays(lastDay, firstDay);
    
    const lastProduction = dailyInputs[dailyInputs.length - 1].cumulative_qty;
    const dailyAverage = daysElapsed > 0 ? lastProduction / (daysElapsed + 1) : 0;

    if (dailyAverage === 0) return null;

    const progress = calculateProgress();
    if (!progress) return null;

    const daysRemaining = Math.ceil(progress.remaining / dailyAverage);
    const predictedCompletion = addDays(new Date(), daysRemaining);

    const targetDate = parseISO(selectedSPK.target_completion_date);
    const daysLate = differenceInDays(predictedCompletion, targetDate);

    return {
      predictedDate: predictedCompletion,
      daysRemaining,
      dailyAverage,
      isOnSchedule: daysLate <= 0,
      daysLate: Math.max(0, daysLate),
    };
  };

  const progress = calculateProgress();
  const prediction = calculatePredictiveCompletion();

  const handleAddInput = async () => {
    if (!selectedSPK) return;

    try {
      const response = await fetch(
        `/api/v1/production/spk/${selectedSPK.spk_id}/daily-input`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            input_date: format(new Date(), 'yyyy-MM-dd'),
            quantity_produced: newInput.qty_produced,
            quantity_rejected: newInput.qty_rejected,
            notes: newInput.notes,
          }),
        }
      );

      if (!response.ok) throw new Error('Failed to save daily input');

      // Update local state
      const input: DailyInput = {
        input_date: format(new Date(), 'yyyy-MM-dd'),
        qty_produced: newInput.qty_produced,
        qty_rejected: newInput.qty_rejected,
        cumulative_qty: (dailyInputs[dailyInputs.length - 1]?.cumulative_qty || 0) + newInput.qty_produced,
        notes: newInput.notes,
      };

      setDailyInputs([...dailyInputs, input]);
      setNewInput({ qty_produced: 0, qty_rejected: 0, notes: '' });

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save input');
    }
  };

  if (!selectedSPK) {
    return (
      <div className="min-h-screen bg-gray-50 p-6">
        <div className="max-w-6xl mx-auto">
          <h1 className="text-3xl font-bold text-gray-900 mb-6">Daily Production Input</h1>
          <div className="bg-white rounded-lg shadow p-12 text-center">
            <Calendar className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-600">Select an SPK to start tracking production</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-6xl mx-auto space-y-6">
        {/* Header */}
        <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg p-6 border border-blue-200">
          <div className="flex items-start justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">Daily Production Tracking</h1>
              <p className="text-gray-600">
                SPK: <span className="font-mono font-semibold">{selectedSPK.spk_id}</span> | 
                Article: <span className="font-semibold ml-1">{selectedSPK.article_id}</span>
              </p>
            </div>
            <button
              onClick={() => setSelectedSPK(null)}
              className="px-4 py-2 bg-white border border-gray-300 rounded-lg text-sm font-medium hover:bg-gray-50"
            >
              Change SPK
            </button>
          </div>
        </div>

        {/* KPI Cards */}
        {progress && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-white rounded-lg shadow p-6 border-l-4 border-blue-500">
              <p className="text-sm text-gray-600">Target Quantity</p>
              <p className="text-3xl font-bold text-blue-600">{selectedSPK.target_qty.toLocaleString()}</p>
              <p className="text-xs text-gray-500 mt-1">units</p>
            </div>

            <div className="bg-white rounded-lg shadow p-6 border-l-4 border-green-500">
              <p className="text-sm text-gray-600">Produced</p>
              <p className="text-3xl font-bold text-green-600">{progress.produced.toLocaleString()}</p>
              <p className="text-xs text-gray-500 mt-1">{progress.progress.toFixed(1)}% complete</p>
            </div>

            <div className="bg-white rounded-lg shadow p-6 border-l-4 border-yellow-500">
              <p className="text-sm text-gray-600">Remaining</p>
              <p className="text-3xl font-bold text-yellow-600">{progress.remaining.toLocaleString()}</p>
              <p className="text-xs text-gray-500 mt-1">units</p>
            </div>

            <div className={`bg-white rounded-lg shadow p-6 border-l-4 ${
              progress.isCompleted ? 'border-green-500' : 'border-gray-300'
            }`}>
              <p className="text-sm text-gray-600">Status</p>
              <p className={`text-2xl font-bold ${progress.isCompleted ? 'text-green-600' : 'text-gray-600'}`}>
                {progress.isCompleted ? '✅ Done' : '🔄 In Progress'}
              </p>
            </div>
          </div>
        )}

        {/* Progress Bar */}
        {progress && (
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="font-semibold text-gray-900 mb-4">Overall Progress</h3>
            <div className="space-y-2">
              <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
                <div
                  className={`h-full transition-all duration-500 ${
                    progress.progress >= 100 ? 'bg-green-500' : 'bg-blue-500'
                  }`}
                  style={{ width: `${Math.min(progress.progress, 100)}%` }}
                />
              </div>
              <div className="flex justify-between text-sm text-gray-600">
                <span>{progress.progress.toFixed(1)}%</span>
                <span>{progress.produced.toLocaleString()} / {selectedSPK.target_qty.toLocaleString()}</span>
              </div>
            </div>
          </div>
        )}

        {/* Predictive Completion Alert */}
        {prediction && (
          <div className={`rounded-lg p-6 border ${
            prediction.isOnSchedule
              ? 'bg-green-50 border-green-200'
              : 'bg-orange-50 border-orange-200'
          }`}>
            <div className="flex items-start gap-3">
              {prediction.isOnSchedule ? (
                <CheckCircle className="w-6 h-6 text-green-600 flex-shrink-0 mt-0.5" />
              ) : (
                <AlertTriangle className="w-6 h-6 text-orange-600 flex-shrink-0 mt-0.5" />
              )}
              <div className="flex-1">
                <h4 className={`font-semibold ${
                  prediction.isOnSchedule ? 'text-green-900' : 'text-orange-900'
                }`}>
                  {prediction.isOnSchedule 
                    ? '✅ On Schedule' 
                    : `⚠️ Behind Schedule by ${prediction.daysLate} days`}
                </h4>
                <p className={`text-sm mt-1 ${
                  prediction.isOnSchedule ? 'text-green-800' : 'text-orange-800'
                }`}>
                  Predicted completion: <span className="font-semibold">{format(prediction.predictedDate, 'dd MMM yyyy')}</span>
                  <br />
                  Daily average: <span className="font-semibold">{prediction.dailyAverage.toFixed(0)} units/day</span>
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Daily Input Form */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="font-semibold text-gray-900 mb-4">Add Today's Production</h3>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Quantity Produced
              </label>
              <input
                type="number"
                min="0"
                value={newInput.qty_produced}
                onChange={(e) => setNewInput({ ...newInput, qty_produced: parseInt(e.target.value) || 0 })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                placeholder="0"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Quantity Rejected
              </label>
              <input
                type="number"
                min="0"
                value={newInput.qty_rejected}
                onChange={(e) => setNewInput({ ...newInput, qty_rejected: parseInt(e.target.value) || 0 })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                placeholder="0"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Notes
              </label>
              <input
                type="text"
                value={newInput.notes}
                onChange={(e) => setNewInput({ ...newInput, notes: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                placeholder="Optional notes"
              />
            </div>
            <div className="flex items-end">
              <button
                onClick={handleAddInput}
                className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors"
              >
                Save Input
              </button>
            </div>
          </div>
        </div>

        {/* Daily Input History */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="font-semibold text-gray-900 mb-4">Daily Input History</h3>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">Date</th>
                  <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">Produced</th>
                  <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">Rejected</th>
                  <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">Cumulative</th>
                  <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">Notes</th>
                </tr>
              </thead>
              <tbody className="divide-y">
                {dailyInputs.map((input, idx) => (
                  <tr key={idx} className="hover:bg-gray-50">
                    <td className="px-4 py-3 text-sm text-gray-900">{format(parseISO(input.input_date), 'dd MMM yyyy')}</td>
                    <td className="px-4 py-3 text-sm text-green-600 font-medium">{input.qty_produced}</td>
                    <td className="px-4 py-3 text-sm text-red-600 font-medium">{input.qty_rejected}</td>
                    <td className="px-4 py-3 text-sm font-semibold text-blue-600">{input.cumulative_qty}</td>
                    <td className="px-4 py-3 text-sm text-gray-600">{input.notes || '-'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DailyProductionPage;
