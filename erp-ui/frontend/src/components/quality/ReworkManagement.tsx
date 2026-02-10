/**
 * Rework Management Component
 * Purpose: Track defects, assign rework, monitor recovery, analyze COPQ
 * Features:
 * - Auto-capture defects from each department
 * - Workflow: Defect → QC Inspection → Rework → Re-QC → Approve
 * - Recovery rate tracking
 * - COPQ (Cost of Poor Quality) analysis
 * - Department-wise filtering
 * 
 * Priority: CRITICAL - Quality tracking missing from UI
 * Created: 2026-02-04
 */

import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/api/client';
import {
  AlertTriangle,
  CheckCircle,
  Clock,
  TrendingDown,
  DollarSign,
  Filter,
  RefreshCw,
  Eye,
  Wrench,
  X,
  Activity,
  BarChart3
} from 'lucide-react';

interface Defect {
  id: number;
  wo_id: number;
  wo_number: string;
  department: string;
  product_name: string;
  defect_qty: number;
  rework_qty: number;
  recovered_qty: number;
  scrap_qty: number;
  recovery_rate: number;
  rework_status: 'PENDING' | 'ASSIGNED' | 'IN_PROGRESS' | 'COMPLETED' | 'CANCELLED';
  defect_type: string;
  root_cause: string;
  created_at: string;
  assigned_to: string;
}

interface DefectSummary {
  total_defects: number;
  pending_rework: number;
  in_progress: number;
  recovered: number;
  scrap: number;
  recovery_rate: number;
  copq: number;
  rework_cost: number;
  scrap_cost: number;
}

interface DefectsData {
  defects: Defect[];
  summary: DefectSummary;
}

export const ReworkManagement: React.FC = () => {
  const queryClient = useQueryClient();
  const [selectedDept, setSelectedDept] = useState<string>('ALL');
  const [selectedStatus, setSelectedStatus] = useState<string>('ALL');
  const [selectedDefect, setSelectedDefect] = useState<Defect | null>(null);
  const [showDetailModal, setShowDetailModal] = useState(false);

  // Fetch defects data
  const { data, isLoading, error } = useQuery<DefectsData>({
    queryKey: ['defects', selectedDept, selectedStatus],
    queryFn: async () => {
      const params = new URLSearchParams();
      if (selectedDept !== 'ALL') params.append('department', selectedDept);
      if (selectedStatus !== 'ALL') params.append('status', selectedStatus);
      
      const response = await apiClient.get(`/quality/defects?${params}`);
      return response.data;
    },
    refetchInterval: 10000 // Auto-refresh every 10 seconds
  });

  // Create rework WO mutation
  const createReworkMutation = useMutation({
    mutationFn: async (defectId: number) => {
      const response = await apiClient.post(`/quality/defects/${defectId}/create-rework`);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['defects'] });
      alert('Rework WO created successfully!');
    },
    onError: (error: any) => {
      alert(`Failed to create rework: ${error.response?.data?.detail || error.message}`);
    }
  });

  // Mark rework completed mutation
  const completeReworkMutation = useMutation({
    mutationFn: async (data: { defectId: number; recoveredQty: number }) => {
      const response = await apiClient.post(`/quality/defects/${data.defectId}/complete-rework`, {
        recovered_qty: data.recoveredQty
      });
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['defects'] });
      setShowDetailModal(false);
      alert('Rework completed successfully!');
    }
  });

  const departments = ['ALL', 'CUTTING', 'EMBROIDERY', 'SEWING', 'FINISHING', 'PACKING'];
  const statuses = ['ALL', 'PENDING', 'ASSIGNED', 'IN_PROGRESS', 'COMPLETED'];

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading defects data...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <AlertTriangle className="w-12 h-12 text-red-500 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-gray-800">Error Loading Data</h2>
          <p className="text-gray-600 mt-2">Failed to fetch defects data. Please try again.</p>
        </div>
      </div>
    );
  }

  const { defects = [], summary } = data || { defects: [], summary: {} as DefectSummary };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'COMPLETED': return 'bg-green-100 text-green-800 border-green-300';
      case 'IN_PROGRESS': return 'bg-yellow-100 text-yellow-800 border-yellow-300';
      case 'ASSIGNED': return 'bg-blue-100 text-blue-800 border-blue-300';
      case 'PENDING': return 'bg-red-100 text-red-800 border-red-300';
      case 'CANCELLED': return 'bg-gray-100 text-gray-800 border-gray-300';
      default: return 'bg-gray-100 text-gray-800 border-gray-300';
    }
  };

  const getDepartmentColor = (dept: string) => {
    switch (dept.toUpperCase()) {
      case 'CUTTING': return 'text-blue-600 bg-blue-50';
      case 'EMBROIDERY': return 'text-purple-600 bg-purple-50';
      case 'SEWING': return 'text-yellow-600 bg-yellow-50';
      case 'FINISHING': return 'text-green-600 bg-green-50';
      case 'PACKING': return 'text-orange-600 bg-orange-50';
      default: return 'text-gray-600 bg-gray-50';
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-red-50 to-orange-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-2">
            <Wrench className="w-8 h-8 text-red-600" />
            <h1 className="text-4xl font-bold text-gray-900">Rework Management</h1>
          </div>
          <p className="text-gray-600">Track defects, assign rework, and monitor quality recovery</p>
        </div>

        {/* Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4 mb-8">
          <div className="bg-white rounded-lg shadow-md p-6 border-l-4 border-red-500">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs text-gray-600 font-medium">Total Defects</p>
                <p className="text-3xl font-bold text-red-600">{summary.total_defects || 0}</p>
                <p className="text-xs text-gray-500 mt-1">pcs</p>
              </div>
              <AlertTriangle className="w-10 h-10 text-red-200" />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6 border-l-4 border-yellow-500">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs text-gray-600 font-medium">Pending Rework</p>
                <p className="text-3xl font-bold text-yellow-600">{summary.pending_rework || 0}</p>
                <p className="text-xs text-gray-500 mt-1">pcs</p>
              </div>
              <Clock className="w-10 h-10 text-yellow-200" />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6 border-l-4 border-blue-500">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs text-gray-600 font-medium">In Progress</p>
                <p className="text-3xl font-bold text-blue-600">{summary.in_progress || 0}</p>
                <p className="text-xs text-gray-500 mt-1">pcs</p>
              </div>
              <Activity className="w-10 h-10 text-blue-200" />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6 border-l-4 border-green-500">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs text-gray-600 font-medium">Recovered</p>
                <p className="text-3xl font-bold text-green-600">{summary.recovered || 0}</p>
                <p className="text-xs text-gray-500 mt-1">{summary.recovery_rate?.toFixed(1) || 0}% rate</p>
              </div>
              <CheckCircle className="w-10 h-10 text-green-200" />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6 border-l-4 border-purple-500">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs text-gray-600 font-medium">COPQ (Rp)</p>
                <p className="text-3xl font-bold text-purple-600">
                  {((summary.copq || 0) / 1000000).toFixed(1)}M
                </p>
                <p className="text-xs text-gray-500 mt-1">this month</p>
              </div>
              <DollarSign className="w-10 h-10 text-purple-200" />
            </div>
          </div>
        </div>

        {/* Filters */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <div className="flex flex-col md:flex-row gap-4 items-start md:items-center justify-between">
            <div className="flex flex-col md:flex-row gap-4 items-start md:items-center flex-1">
              <div className="flex items-center gap-2">
                <Filter className="w-5 h-5 text-gray-600" />
                <label className="text-sm font-medium text-gray-700">Department:</label>
                <select
                  value={selectedDept}
                  onChange={(e) => setSelectedDept(e.target.value)}
                  className="px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  {departments.map(dept => (
                    <option key={dept} value={dept}>{dept}</option>
                  ))}
                </select>
              </div>

              <div className="flex items-center gap-2">
                <label className="text-sm font-medium text-gray-700">Status:</label>
                <select
                  value={selectedStatus}
                  onChange={(e) => setSelectedStatus(e.target.value)}
                  className="px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  {statuses.map(status => (
                    <option key={status} value={status}>{status}</option>
                  ))}
                </select>
              </div>
            </div>

            <button
              onClick={() => queryClient.invalidateQueries({ queryKey: ['defects'] })}
              className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
            >
              <RefreshCw className="w-4 h-4" />
              Refresh
            </button>
          </div>
        </div>

        {/* Defects Table */}
        <div className="bg-white rounded-lg shadow-md overflow-hidden">
          <div className="p-6 border-b border-gray-200 bg-gray-50">
            <h2 className="text-xl font-semibold text-gray-900 flex items-center gap-2">
              <BarChart3 className="w-5 h-5 text-blue-600" />
              Defects & Rework Status ({defects.length} items)
            </h2>
          </div>
          
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-100">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-gray-700">WO Number</th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-gray-700">Department</th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-gray-700">Product</th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-gray-700">Defect</th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-gray-700">Rework</th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-gray-700">Recovered</th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-gray-700">Scrap</th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-gray-700">Recovery Rate</th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-gray-700">Status</th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-gray-700">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {defects.length === 0 ? (
                  <tr>
                    <td colSpan={10} className="px-4 py-8 text-center text-gray-500">
                      <CheckCircle className="w-12 h-12 text-green-400 mx-auto mb-2" />
                      <p>No defects found. Quality is excellent! [Success]</p>
                    </td>
                  </tr>
                ) : (
                  defects.map((defect) => (
                    <tr key={defect.id} className="hover:bg-gray-50 transition-colors">
                      <td className="px-4 py-3 text-sm font-medium text-gray-900">{defect.wo_number}</td>
                      <td className="px-4 py-3">
                        <span className={`px-2 py-1 rounded text-xs font-medium ${getDepartmentColor(defect.department)}`}>
                          {defect.department}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-700 max-w-xs truncate">{defect.product_name}</td>
                      <td className="px-4 py-3 text-sm font-bold text-red-600">{defect.defect_qty} pcs</td>
                      <td className="px-4 py-3 text-sm font-bold text-yellow-600">{defect.rework_qty} pcs</td>
                      <td className="px-4 py-3 text-sm font-bold text-green-600">{defect.recovered_qty} pcs</td>
                      <td className="px-4 py-3 text-sm font-bold text-gray-600">{defect.scrap_qty} pcs</td>
                      <td className="px-4 py-3">
                        <div className={`text-sm font-semibold ${
                          defect.recovery_rate >= 80 ? 'text-green-600' :
                          defect.recovery_rate >= 50 ? 'text-yellow-600' :
                          'text-red-600'
                        }`}>
                          {defect.recovery_rate.toFixed(1)}%
                        </div>
                      </td>
                      <td className="px-4 py-3">
                        <span className={`px-2 py-1 rounded-full text-xs font-medium border ${getStatusColor(defect.rework_status)}`}>
                          {defect.rework_status}
                        </span>
                      </td>
                      <td className="px-4 py-3">
                        <div className="flex gap-2">
                          {defect.rework_status === 'PENDING' && (
                            <button
                              onClick={() => createReworkMutation.mutate(defect.id)}
                              className="px-3 py-1 bg-blue-600 text-white rounded text-xs hover:bg-blue-700 transition-colors flex items-center gap-1"
                              disabled={createReworkMutation.isPending}
                            >
                              <Wrench className="w-3 h-3" />
                              Assign Rework
                            </button>
                          )}
                          {(defect.rework_status === 'IN_PROGRESS' || defect.rework_status === 'ASSIGNED') && (
                            <button
                              onClick={() => {
                                setSelectedDefect(defect);
                                setShowDetailModal(true);
                              }}
                              className="px-3 py-1 bg-green-600 text-white rounded text-xs hover:bg-green-700 transition-colors flex items-center gap-1"
                            >
                              <CheckCircle className="w-3 h-3" />
                              Complete
                            </button>
                          )}
                          <button
                            onClick={() => {
                              setSelectedDefect(defect);
                              setShowDetailModal(true);
                            }}
                            className="px-3 py-1 bg-gray-600 text-white rounded text-xs hover:bg-gray-700 transition-colors flex items-center gap-1"
                          >
                            <Eye className="w-3 h-3" />
                            View
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* COPQ Analysis */}
        <div className="mt-8 bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center gap-2">
            <DollarSign className="w-5 h-5 text-purple-600" />
            [Cost] COPQ Analysis (Cost of Poor Quality)
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-yellow-50 rounded-lg p-6 border border-yellow-200">
              <p className="text-sm text-gray-700 font-medium mb-2">Rework Cost</p>
              <p className="text-3xl font-bold text-yellow-600">
                Rp {((summary.rework_cost || 0) / 1000000).toFixed(1)}M
              </p>
              <p className="text-xs text-gray-600 mt-2">Labor + Material for rework</p>
            </div>
            <div className="bg-red-50 rounded-lg p-6 border border-red-200">
              <p className="text-sm text-gray-700 font-medium mb-2">Scrap Cost</p>
              <p className="text-3xl font-bold text-red-600">
                Rp {((summary.scrap_cost || 0) / 1000000).toFixed(1)}M
              </p>
              <p className="text-xs text-gray-600 mt-2">Unrecoverable defects</p>
            </div>
            <div className="bg-purple-50 rounded-lg p-6 border border-purple-200">
              <p className="text-sm text-gray-700 font-medium mb-2">Total COPQ</p>
              <p className="text-3xl font-bold text-purple-600">
                Rp {((summary.copq || 0) / 1000000).toFixed(1)}M
              </p>
              <p className="text-xs text-gray-600 mt-2">This month (cumulative)</p>
            </div>
          </div>
        </div>
      </div>

      {/* Detail Modal */}
      {showDetailModal && selectedDefect && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-[9999] p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="sticky top-0 bg-blue-600 text-white px-6 py-4 flex items-center justify-between rounded-t-lg">
              <h3 className="text-xl font-bold">Defect Details - {selectedDefect.wo_number}</h3>
              <button
                onClick={() => setShowDetailModal(false)}
                className="hover:bg-blue-700 rounded-full p-1"
              >
                <X size={24} />
              </button>
            </div>
            
            <div className="p-6">
              <div className="grid grid-cols-2 gap-4 mb-6">
                <div>
                  <label className="text-xs text-gray-600">Department</label>
                  <p className="font-semibold">{selectedDefect.department}</p>
                </div>
                <div>
                  <label className="text-xs text-gray-600">Product</label>
                  <p className="font-semibold">{selectedDefect.product_name}</p>
                </div>
                <div>
                  <label className="text-xs text-gray-600">Defect Type</label>
                  <p className="font-semibold text-red-600">{selectedDefect.defect_type || 'N/A'}</p>
                </div>
                <div>
                  <label className="text-xs text-gray-600">Root Cause</label>
                  <p className="font-semibold text-orange-600">{selectedDefect.root_cause || 'Under investigation'}</p>
                </div>
              </div>

              <div className="bg-gray-50 rounded-lg p-4 mb-6">
                <h4 className="font-semibold mb-3">Quantities</h4>
                <div className="grid grid-cols-4 gap-4">
                  <div>
                    <p className="text-xs text-gray-600">Defect</p>
                    <p className="text-xl font-bold text-red-600">{selectedDefect.defect_qty}</p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-600">Rework</p>
                    <p className="text-xl font-bold text-yellow-600">{selectedDefect.rework_qty}</p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-600">Recovered</p>
                    <p className="text-xl font-bold text-green-600">{selectedDefect.recovered_qty}</p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-600">Scrap</p>
                    <p className="text-xl font-bold text-gray-600">{selectedDefect.scrap_qty}</p>
                  </div>
                </div>
              </div>

              {selectedDefect.rework_status === 'IN_PROGRESS' && (
                <div className="mt-6">
                  <button
                    onClick={() => {
                      const recoveredQty = prompt(`Enter recovered quantity (max: ${selectedDefect.rework_qty}):`);
                      if (recoveredQty) {
                        completeReworkMutation.mutate({
                          defectId: selectedDefect.id,
                          recoveredQty: parseInt(recoveredQty)
                        });
                      }
                    }}
                    className="w-full py-3 bg-green-600 text-white rounded-lg font-semibold hover:bg-green-700 transition-colors"
                    disabled={completeReworkMutation.isPending}
                  >
                    Complete Rework
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
