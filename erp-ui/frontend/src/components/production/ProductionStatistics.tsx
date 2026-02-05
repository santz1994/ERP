/**
 * Copyright (c) 2026 PT Quty Karunia / Daniel Rizaldy - All Rights Reserved
 * File: ProductionStatistics.tsx | Author: Daniel Rizaldy | Date: 2026-02-04
 * Production Statistics Dashboard Component
 */

import { TrendingUp, TrendingDown, Target, CheckCircle, XCircle, Award } from 'lucide-react';

interface ProductionStatisticsProps {
  workOrderId: number;
  targetQty: number;
  actualQty: number;
  goodQty: number;
  defectQty: number;
  dailyAverage: number;
  targetDailyAverage: number;
  workingDays: number;
  bufferPercent?: number;
  yieldRate: number;
  defectRate: number;
  efficiency: number;
  daysRemaining?: number;
  className?: string;
}

export const ProductionStatistics: React.FC<ProductionStatisticsProps> = ({
  targetQty,
  actualQty,
  goodQty,
  defectQty,
  dailyAverage,
  targetDailyAverage,
  workingDays,
  bufferPercent = 0,
  yieldRate,
  defectRate,
  efficiency,
  daysRemaining,
  className = ''
}) => {
  const completionRate = (actualQty / targetQty) * 100;
  const isAheadOfSchedule = dailyAverage > targetDailyAverage;
  const projectedTotal = daysRemaining ? actualQty + (dailyAverage * daysRemaining) : actualQty;
  const willMeetTarget = projectedTotal >= targetQty;

  return (
    <div className={`bg-white rounded-lg shadow-sm border border-gray-200 p-6 ${className}`}>
      <h3 className="text-xl font-bold text-gray-900 mb-6 flex items-center gap-2">
        📊 Production Statistics & Performance
      </h3>

      {/* KPI Cards */}
      <div className="grid grid-cols-4 gap-4 mb-6">
        {/* Target Progress */}
        <div className="bg-gradient-to-br from-blue-50 to-blue-100 p-4 rounded-lg border border-blue-200">
          <div className="flex items-center justify-between mb-2">
            <Target className="w-5 h-5 text-blue-600" />
            <span className={`text-xs font-semibold px-2 py-1 rounded ${
              completionRate >= 100 ? 'bg-green-500 text-white' :
              completionRate >= 75 ? 'bg-yellow-500 text-white' :
              'bg-red-500 text-white'
            }`}>
              {completionRate.toFixed(1)}%
            </span>
          </div>
          <div className="text-2xl font-bold text-blue-900">{actualQty}</div>
          <div className="text-xs text-blue-700">of {targetQty} pcs target</div>
          {bufferPercent > 0 && (
            <div className="text-[10px] text-blue-600 mt-1">
              +{bufferPercent}% buffer ({Math.round(targetQty * bufferPercent / 100)} pcs)
            </div>
          )}
        </div>

        {/* Yield Rate */}
        <div className="bg-gradient-to-br from-green-50 to-green-100 p-4 rounded-lg border border-green-200">
          <div className="flex items-center justify-between mb-2">
            <CheckCircle className="w-5 h-5 text-green-600" />
            <span className={`text-xs font-semibold px-2 py-1 rounded ${
              yieldRate >= 98 ? 'bg-green-500 text-white' :
              yieldRate >= 95 ? 'bg-yellow-500 text-white' :
              'bg-red-500 text-white'
            }`}>
              {yieldRate.toFixed(1)}%
            </span>
          </div>
          <div className="text-2xl font-bold text-green-900">{goodQty}</div>
          <div className="text-xs text-green-700">Good output (Yield)</div>
          <div className="text-[10px] text-green-600 mt-1">
            Target: ≥95% yield
          </div>
        </div>

        {/* Defect Rate */}
        <div className="bg-gradient-to-br from-red-50 to-red-100 p-4 rounded-lg border border-red-200">
          <div className="flex items-center justify-between mb-2">
            <XCircle className="w-5 h-5 text-red-600" />
            <span className={`text-xs font-semibold px-2 py-1 rounded ${
              defectRate <= 2 ? 'bg-green-500 text-white' :
              defectRate <= 5 ? 'bg-yellow-500 text-white' :
              'bg-red-500 text-white'
            }`}>
              {defectRate.toFixed(1)}%
            </span>
          </div>
          <div className="text-2xl font-bold text-red-900">{defectQty}</div>
          <div className="text-xs text-red-700">Defects found</div>
          <div className="text-[10px] text-red-600 mt-1">
            Target: {'<'}5% defect rate
          </div>
        </div>

        {/* Daily Performance */}
        <div className="bg-gradient-to-br from-purple-50 to-purple-100 p-4 rounded-lg border border-purple-200">
          <div className="flex items-center justify-between mb-2">
            {isAheadOfSchedule ? (
              <TrendingUp className="w-5 h-5 text-purple-600" />
            ) : (
              <TrendingDown className="w-5 h-5 text-purple-600" />
            )}
            <span className={`text-xs font-semibold px-2 py-1 rounded ${
              isAheadOfSchedule ? 'bg-green-500 text-white' : 'bg-orange-500 text-white'
            }`}>
              {((dailyAverage / targetDailyAverage) * 100).toFixed(0)}%
            </span>
          </div>
          <div className="text-2xl font-bold text-purple-900">{Math.round(dailyAverage)}</div>
          <div className="text-xs text-purple-700">pcs/day average</div>
          <div className="text-[10px] text-purple-600 mt-1">
            Target: {Math.round(targetDailyAverage)} pcs/day
          </div>
        </div>
      </div>

      {/* Detailed Metrics */}
      <div className="grid grid-cols-2 gap-6">
        {/* Left Column: Performance Metrics */}
        <div className="space-y-4">
          <h4 className="font-semibold text-gray-900 text-sm flex items-center gap-2">
            <Award className="w-4 h-4 text-yellow-500" />
            Performance Metrics
          </h4>
          
          <div className="space-y-3">
            {/* Efficiency */}
            <div>
              <div className="flex items-center justify-between mb-1">
                <span className="text-xs text-gray-600">Overall Efficiency</span>
                <span className="text-sm font-bold text-gray-900">{efficiency.toFixed(1)}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className={`h-2 rounded-full ${
                    efficiency >= 90 ? 'bg-green-500' :
                    efficiency >= 75 ? 'bg-yellow-500' :
                    'bg-red-500'
                  }`}
                  style={{ width: `${Math.min(efficiency, 100)}%` }}
                />
              </div>
            </div>

            {/* Working Days */}
            <div className="flex items-center justify-between py-2 border-b border-gray-200">
              <span className="text-xs text-gray-600">Working Days</span>
              <span className="text-sm font-bold text-gray-900">{workingDays} days</span>
            </div>

            {/* Avg Output */}
            <div className="flex items-center justify-between py-2 border-b border-gray-200">
              <span className="text-xs text-gray-600">Daily Average Output</span>
              <span className="text-sm font-bold text-gray-900">{Math.round(dailyAverage)} pcs</span>
            </div>

            {/* Target Daily */}
            <div className="flex items-center justify-between py-2 border-b border-gray-200">
              <span className="text-xs text-gray-600">Target Daily Output</span>
              <span className="text-sm font-bold text-gray-900">{Math.round(targetDailyAverage)} pcs</span>
            </div>

            {/* Variance */}
            <div className="flex items-center justify-between py-2">
              <span className="text-xs text-gray-600">Daily Variance</span>
              <span className={`text-sm font-bold ${
                isAheadOfSchedule ? 'text-green-600' : 'text-red-600'
              }`}>
                {isAheadOfSchedule ? '+' : ''}{Math.round(dailyAverage - targetDailyAverage)} pcs
              </span>
            </div>
          </div>
        </div>

        {/* Right Column: Projection & Quality */}
        <div className="space-y-4">
          <h4 className="font-semibold text-gray-900 text-sm flex items-center gap-2">
            <Target className="w-4 h-4 text-blue-500" />
            Projection & Quality
          </h4>

          {daysRemaining !== undefined && daysRemaining > 0 && (
            <div className="bg-blue-50 p-3 rounded-lg border border-blue-200">
              <div className="text-xs text-blue-700 font-medium mb-2">📈 Forecast</div>
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-xs text-blue-600">Days Remaining</span>
                  <span className="text-sm font-bold text-blue-900">{daysRemaining} days</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-xs text-blue-600">Projected Total</span>
                  <span className="text-sm font-bold text-blue-900">{Math.round(projectedTotal)} pcs</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-xs text-blue-600">Will Meet Target?</span>
                  <span className={`text-sm font-bold ${willMeetTarget ? 'text-green-600' : 'text-red-600'}`}>
                    {willMeetTarget ? '✅ YES' : '❌ NO'}
                  </span>
                </div>
              </div>
            </div>
          )}

          <div className="space-y-2">
            {/* Quality Rating */}
            <div className="bg-green-50 p-3 rounded-lg border border-green-200">
              <div className="text-xs text-green-700 font-medium mb-1">Quality Rating</div>
              <div className="text-2xl font-bold text-green-900">
                {yieldRate >= 98 ? 'A+' :
                 yieldRate >= 95 ? 'A' :
                 yieldRate >= 90 ? 'B' :
                 yieldRate >= 85 ? 'C' : 'D'}
              </div>
              <div className="text-[10px] text-green-600 mt-1">
                Based on {yieldRate.toFixed(1)}% yield rate
              </div>
            </div>

            {/* Recommendations */}
            <div className="bg-yellow-50 p-3 rounded-lg border border-yellow-200">
              <div className="text-xs text-yellow-700 font-medium mb-2">💡 Recommendations</div>
              <ul className="text-[10px] text-yellow-800 space-y-1">
                {!isAheadOfSchedule && (
                  <li>• Increase daily output by {Math.abs(Math.round(dailyAverage - targetDailyAverage))} pcs</li>
                )}
                {defectRate > 5 && (
                  <li>• Focus on quality - defect rate above target</li>
                )}
                {yieldRate < 95 && (
                  <li>• Improve yield rate - currently below 95% target</li>
                )}
                {isAheadOfSchedule && defectRate <= 5 && yieldRate >= 95 && (
                  <li>• ✅ Excellent performance - maintain current pace!</li>
                )}
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
