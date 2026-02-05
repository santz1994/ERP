/**
 * MO Aggregate View Component
 * Purpose: Monitor Multiple SPKs for 1 Manufacturing Order
 * Features:
 * - Shows all SPKs associated with an MO
 * - Displays aggregate metrics (total production, good output, defects, MO coverage)
 * - Real-time progress tracking per SPK
 * - Visual status indicators (completed/in-progress/pending)
 * 
 * Priority: CRITICAL - Missing feature from documentation
 * Created: 2026-02-04
 */

import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/api/client';
import {
 TrendingUp,
  CheckCircle,
  AlertTriangle,
  Target,
  Factory,
  Package,
  Activity,
  Award
} from 'lucide-react';

interface SPKProgress {
  id: number;
  spk_number: string;
  department: string;
  target_qty: number;
  actual_qty: number;
  good_qty: number;
  defect_qty: number;
  rework_qty: number;
  completion_pct: number;
  status: 'PENDING' | 'IN_PROGRESS' | 'COMPLETED' | 'CANCELLED';
}

interface AggregateMetrics {
  total_spk_target: number;
  total_production: number;
  output_good: number;
  total_defects: number;
  total_rework: number;
  yield_pct: number;
  defect_pct: number;
  rework_pct: number;
  mo_coverage_pct: number;
  all_spks_completed: boolean;
  spks_completed: number;
  total_spks: number;
}

interface MOAggregateData {
  mo_id: number;
  mo_number: string;
  product_name: string;
  mo_target: number;
  spks: SPKProgress[];
  aggregate: AggregateMetrics;
}

interface MOAggregateViewProps {
  moId: number;
  onClose?: () => void;
}

export const MOAggregateView: React.FC<MOAggregateViewProps> = ({ moId, onClose }) => {
  const { data, isLoading, error } = useQuery<MOAggregateData>({
    queryKey: ['mo-aggregate', moId],
    queryFn: async () => {
      const response = await apiClient.get(`/ppic/manufacturing-orders/${moId}/aggregate`);
      return response.data;
    },
    refetchInterval: 5000, // Real-time updates every 5 seconds
    enabled: !!moId
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading MO aggregate data...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6">
        <div className="flex items-center gap-3">
          <AlertTriangle className="w-6 h-6 text-red-600" />
          <div>
            <h3 className="font-semibold text-red-900">Error Loading Data</h3>
            <p className="text-sm text-red-700">Failed to fetch MO aggregate data. Please try again.</p>
          </div>
        </div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
        <p className="text-yellow-800">No data available for this MO.</p>
      </div>
    );
  }

  const { mo_number, product_name, mo_target, spks, aggregate } = data;

  const getDepartmentColor = (dept: string) => {
    switch (dept.toUpperCase()) {
      case 'CUTTING': return 'bg-blue-500';
      case 'EMBROIDERY': return 'bg-purple-500';
      case 'SEWING': return 'bg-yellow-500';
      case 'FINISHING': return 'bg-green-500';
      case 'PACKING': return 'bg-orange-500';
      default: return 'bg-gray-500';
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'COMPLETED':
        return <span className="px-2 py-1 bg-green-100 text-green-800 rounded-full text-xs font-medium">Completed</span>;
      case 'IN_PROGRESS':
        return <span className="px-2 py-1 bg-yellow-100 text-yellow-800 rounded-full text-xs font-medium">🔄 In Progress</span>;
      case 'PENDING':
        return <span className="px-2 py-1 bg-gray-100 text-gray-800 rounded-full text-xs font-medium">⏳ Pending</span>;
      case 'CANCELLED':
        return <span className="px-2 py-1 bg-red-100 text-red-800 rounded-full text-xs font-medium">Cancelled</span>;
      default:
        return <span className="px-2 py-1 bg-gray-100 text-gray-800 rounded-full text-xs font-medium">{status}</span>;
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-xl border-2 border-blue-500">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-blue-700 text-white px-6 py-4 rounded-t-lg">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Factory className="w-6 h-6" />
            <div>
              <h2 className="text-2xl font-bold">{mo_number}</h2>
              <p className="text-blue-100 text-sm">{product_name}</p>
            </div>
          </div>
          {onClose && (
            <button
              onClick={onClose}
              className="hover:bg-blue-800 rounded-full p-2 transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          )}
        </div>
        
        <div className="flex items-center gap-6 mt-4 text-sm">
          <div className="flex items-center gap-2">
            <Target className="w-5 h-5" />
            <span>MO Target: <strong>{mo_target} pcs</strong></span>
          </div>
          <div className="flex items-center gap-2">
            <TrendingUp className="w-5 h-5" />
            <span>Total SPK Target: <strong>{aggregate.total_spk_target} pcs</strong> (with buffer)</span>
          </div>
        </div>
      </div>

      <div className="p-6">
        {/* Progress by SPK */}
        <div className="mb-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
            <Activity className="w-5 h-5 text-blue-600" />
            Progress by SPK
          </h3>
          <div className="space-y-3">
            {spks.map((spk) => (
              <div key={spk.id} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg border border-gray-200 hover:border-blue-300 transition-colors">
                <div className="flex items-center gap-4 flex-1">
                  <div className={`w-3 h-3 rounded-full ${
                    spk.status === 'COMPLETED' ? 'bg-green-500' :
                    spk.status === 'IN_PROGRESS' ? 'bg-yellow-500' :
                    spk.status === 'CANCELLED' ? 'bg-red-500' :
                    'bg-gray-400'
                  }`}></div>
                  
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-1">
                      <p className="font-semibold text-gray-900">{spk.spk_number}</p>
                      <span className={`px-2 py-0.5 rounded text-xs font-medium text-white ${getDepartmentColor(spk.department)}`}>
                        {spk.department}
                      </span>
                      {getStatusBadge(spk.status)}
                    </div>
                    
                    {/* Progress Bar */}
                    <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
                      <div
                        className={`h-2 rounded-full transition-all ${
                          spk.completion_pct >= 100 ? 'bg-green-500' :
                          spk.completion_pct >= 80 ? 'bg-yellow-500' :
                          'bg-red-500'
                        }`}
                        style={{ width: `${Math.min(spk.completion_pct, 100)}%` }}
                      />
                    </div>
                  </div>
                </div>
                
                <div className="text-right ml-4">
                  <p className="text-lg font-bold text-gray-900">
                    {spk.actual_qty}/{spk.target_qty} pcs
                  </p>
                  <p className={`text-sm font-semibold ${
                    spk.completion_pct >= 100 ? 'text-green-600' :
                    spk.completion_pct >= 80 ? 'text-yellow-600' :
                    'text-red-600'
                  }`}>
                    ({spk.completion_pct.toFixed(1)}%)
                  </p>
                  <div className="flex items-center gap-3 mt-1 text-xs text-gray-600">
                    <span className="text-green-600">{spk.good_qty}</span>
                    <span className="text-red-600">{spk.defect_qty}</span>
                    <span className="text-yellow-600">🔧 {spk.rework_qty}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Aggregate Total */}
        <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg p-6 border-2 border-blue-300">
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
            <Award className="w-5 h-5 text-purple-600" />
            Aggregate Total
          </h3>
          
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
            <div className="bg-white rounded-lg p-4 shadow-sm">
              <p className="text-xs text-gray-600 mb-1">Total Production</p>
              <p className="text-2xl font-bold text-gray-900">{aggregate.total_production}</p>
              <p className="text-xs text-gray-500">pcs</p>
            </div>
            
            <div className="bg-white rounded-lg p-4 shadow-sm">
              <p className="text-xs text-gray-600 mb-1">Output Good</p>
              <p className="text-2xl font-bold text-green-600">{aggregate.output_good}</p>
              <p className="text-xs text-gray-500">{aggregate.yield_pct.toFixed(1)}% yield</p>
            </div>
            
            <div className="bg-white rounded-lg p-4 shadow-sm">
              <p className="text-xs text-gray-600 mb-1">Defects</p>
              <p className="text-2xl font-bold text-red-600">{aggregate.total_defects}</p>
              <p className="text-xs text-gray-500">{aggregate.defect_pct.toFixed(1)}% defect rate</p>
            </div>
            
            <div className="bg-white rounded-lg p-4 shadow-sm">
              <p className="text-xs text-gray-600 mb-1">Rework</p>
              <p className="text-2xl font-bold text-yellow-600">{aggregate.total_rework}</p>
              <p className="text-xs text-gray-500">{aggregate.rework_pct.toFixed(1)}% recovery</p>
            </div>
          </div>

          {/* MO Coverage */}
          <div className="bg-white rounded-lg p-4 shadow-md border-2 border-blue-400">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 mb-1">MO Coverage</p>
                <p className={`text-3xl font-bold ${
                  aggregate.mo_coverage_pct >= 100 ? 'text-green-600' : 'text-yellow-600'
                }`}>
                  {aggregate.output_good}/{mo_target} pcs
                </p>
                <p className={`text-sm font-medium ${
                  aggregate.mo_coverage_pct >= 100 ? 'text-green-600' : 'text-yellow-600'
                }`}>
                  {aggregate.mo_coverage_pct.toFixed(1)}%
                  {aggregate.mo_coverage_pct >= 100 ? ' surplus' : ' pending'}
                </p>
              </div>
              <Package className="w-12 h-12 text-blue-300" />
            </div>
          </div>
        </div>

        {/* Status Badge */}
        <div className="mt-6 text-center">
          {aggregate.all_spks_completed ? (
            <div className="inline-flex items-center gap-3 px-6 py-3 bg-green-100 text-green-800 rounded-full border-2 border-green-500">
              <CheckCircle className="w-6 h-6" />
              <span className="font-semibold text-lg">All SPKs Completed - Ready for Next Stage! 🎉</span>
            </div>
          ) : (
            <div className="inline-flex items-center gap-3 px-6 py-3 bg-yellow-100 text-yellow-800 rounded-full border-2 border-yellow-500">
              <AlertTriangle className="w-6 h-6" />
              <span className="font-semibold text-lg">
                {aggregate.spks_completed}/{aggregate.total_spks} SPKs Completed - Production in Progress
              </span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
