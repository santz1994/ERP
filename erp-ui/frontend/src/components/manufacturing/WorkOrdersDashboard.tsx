/**
 * Work Orders Dashboard - Production Department View
 * Priority 1.3: Enhanced Production Dashboard
 * Created: 2026-02-04
 */

import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/api/client';
import { 
  Factory, 
  Play, 
  Pause, 
  CheckCircle, 
  Clock, 
  AlertCircle,
  TrendingUp,
  Package,
  Filter
} from 'lucide-react';

interface WorkOrder {
  id: number;
  wo_code: string;
  mo_id: number;
  department: string;
  product_id: number;
  product_code: string;
  product_name: string;
  qty_target: number;
  qty_good: number;
  qty_defect: number;
  qty_rework: number;
  state: 'PENDING' | 'READY' | 'RUNNING' | 'PAUSED' | 'COMPLETED' | 'CANCELLED';
  priority: number;
  can_start: boolean;
  dependency_reason?: string;
  created_at: string;
  started_at?: string;
  completed_at?: string;
  progress_percentage: number;
}

interface WorkOrdersDashboardProps {
  departmentFilter?: string;
}

export const WorkOrdersDashboard: React.FC<WorkOrdersDashboardProps> = ({ 
  departmentFilter 
}) => {
  const queryClient = useQueryClient();
  const [selectedDepartment, setSelectedDepartment] = useState<string>(departmentFilter || 'ALL');
  const [statusFilter, setStatusFilter] = useState<string>('ALL');

  const departments = [
    'ALL',
    'CUTTING',
    'EMBROIDERY',
    'SEWING',
    'FINISHING',
    'PACKING',
    'FG_RECEIVING'
  ];

  const statuses = [
    'ALL',
    'PENDING',
    'READY',
    'RUNNING',
    'PAUSED',
    'COMPLETED'
  ];

  // Fetch Work Orders
  const { data: workOrders, isLoading } = useQuery({
    queryKey: ['work-orders', selectedDepartment, statusFilter],
    queryFn: async () => {
      const params = new URLSearchParams();
      if (selectedDepartment !== 'ALL') params.append('department', selectedDepartment);
      if (statusFilter !== 'ALL') params.append('state', statusFilter);
      const response = await apiClient.get(`/work-orders?${params}`);
      return response.data as WorkOrder[];
    },
    refetchInterval: 5000 // Refresh every 5 seconds
  });

  // Start WO Mutation
  const startWOMutation = useMutation({
    mutationFn: async (woId: number) => {
      const response = await apiClient.post(`/work-orders/${woId}/start`);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['work-orders'] });
    },
    onError: (error: any) => {
      alert('❌ ' + (error.response?.data?.detail || 'Failed to start Work Order'));
    }
  });

  // Pause WO Mutation
  const pauseWOMutation = useMutation({
    mutationFn: async (woId: number) => {
      const response = await apiClient.post(`/work-orders/${woId}/pause`);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['work-orders'] });
    },
    onError: (error: any) => {
      alert('❌ ' + (error.response?.data?.detail || 'Failed to pause Work Order'));
    }
  });

  // Complete WO Mutation
  const completeWOMutation = useMutation({
    mutationFn: async (woId: number) => {
      const response = await apiClient.post(`/work-orders/${woId}/complete`);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['work-orders'] });
    },
    onError: (error: any) => {
      alert('❌ ' + (error.response?.data?.detail || 'Failed to complete Work Order'));
    }
  });

  const getStatusColor = (state: string) => {
    switch (state) {
      case 'COMPLETED': return 'bg-green-100 text-green-800 border-green-300';
      case 'RUNNING': return 'bg-blue-100 text-blue-800 border-blue-300';
      case 'READY': return 'bg-purple-100 text-purple-800 border-purple-300';
      case 'PAUSED': return 'bg-yellow-100 text-yellow-800 border-yellow-300';
      case 'PENDING': return 'bg-gray-100 text-gray-800 border-gray-300';
      default: return 'bg-gray-100 text-gray-800 border-gray-300';
    }
  };

  const getStatusIcon = (state: string) => {
    switch (state) {
      case 'COMPLETED': return <CheckCircle size={16} />;
      case 'RUNNING': return <Play size={16} />;
      case 'READY': return <Clock size={16} />;
      case 'PAUSED': return <Pause size={16} />;
      case 'PENDING': return <AlertCircle size={16} />;
      default: return <Clock size={16} />;
    }
  };

  const stats = {
    total: workOrders?.length || 0,
    pending: workOrders?.filter(wo => wo.state === 'PENDING').length || 0,
    ready: workOrders?.filter(wo => wo.state === 'READY').length || 0,
    running: workOrders?.filter(wo => wo.state === 'RUNNING').length || 0,
    completed: workOrders?.filter(wo => wo.state === 'COMPLETED').length || 0
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading Work Orders...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header & Filters */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <div className="bg-blue-100 p-3 rounded-lg">
              <Factory className="text-blue-600" size={32} />
            </div>
            <div>
              <h2 className="text-2xl font-bold text-gray-900">Work Orders</h2>
              <p className="text-gray-600">Production department view</p>
            </div>
          </div>
        </div>

        {/* Filters */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Department
            </label>
            <select
              value={selectedDepartment}
              onChange={(e) => setSelectedDepartment(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              {departments.map(dept => (
                <option key={dept} value={dept}>{dept}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Status
            </label>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              {statuses.map(status => (
                <option key={status} value={status}>{status}</option>
              ))}
            </select>
          </div>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-5 gap-4 mt-6">
          <div className="bg-gray-50 rounded-lg p-3 text-center">
            <div className="text-2xl font-bold text-gray-700">{stats.total}</div>
            <div className="text-xs text-gray-600">Total</div>
          </div>
          <div className="bg-gray-50 rounded-lg p-3 text-center">
            <div className="text-2xl font-bold text-gray-600">{stats.pending}</div>
            <div className="text-xs text-gray-600">Pending</div>
          </div>
          <div className="bg-purple-50 rounded-lg p-3 text-center">
            <div className="text-2xl font-bold text-purple-600">{stats.ready}</div>
            <div className="text-xs text-gray-600">Ready</div>
          </div>
          <div className="bg-blue-50 rounded-lg p-3 text-center">
            <div className="text-2xl font-bold text-blue-600">{stats.running}</div>
            <div className="text-xs text-gray-600">Running</div>
          </div>
          <div className="bg-green-50 rounded-lg p-3 text-center">
            <div className="text-2xl font-bold text-green-600">{stats.completed}</div>
            <div className="text-xs text-gray-600">Completed</div>
          </div>
        </div>
      </div>

      {/* Work Orders List */}
      <div className="space-y-4">
        {workOrders?.length === 0 ? (
          <div className="bg-white rounded-lg shadow-md p-12 text-center">
            <Package className="mx-auto text-gray-400 mb-4" size={64} />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">No Work Orders Found</h3>
            <p className="text-gray-600">Try adjusting your filters</p>
          </div>
        ) : (
          workOrders?.map((wo) => (
            <div key={wo.id} className="bg-white rounded-lg shadow-md overflow-hidden">
              <div className="p-6">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h3 className="text-xl font-bold text-gray-900">{wo.wo_code}</h3>
                      <span className={`px-3 py-1 rounded-full text-xs font-semibold border flex items-center gap-1 ${getStatusColor(wo.state)}`}>
                        {getStatusIcon(wo.state)}
                        {wo.state}
                      </span>
                    </div>
                    
                    <p className="text-gray-600 mb-1">
                      {wo.department} • {wo.product_name}
                    </p>
                    
                    <div className="flex items-center gap-4 text-sm text-gray-500">
                      <span>📦 {wo.product_code}</span>
                      <span>🎯 Target: {wo.qty_target} pcs</span>
                      <span>✅ Good: {wo.qty_good} pcs</span>
                      {wo.qty_defect > 0 && <span className="text-red-600">❌ Defect: {wo.qty_defect} pcs</span>}
                    </div>
                  </div>

                  {/* Action Buttons */}
                  <div className="flex gap-2">
                    {wo.state === 'READY' && wo.can_start && (
                      <button
                        onClick={() => startWOMutation.mutate(wo.id)}
                        className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors flex items-center gap-2"
                        disabled={startWOMutation.isPending}
                      >
                        <Play size={16} />
                        Start
                      </button>
                    )}
                    
                    {wo.state === 'RUNNING' && (
                      <>
                        <button
                          onClick={() => pauseWOMutation.mutate(wo.id)}
                          className="px-4 py-2 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700 transition-colors flex items-center gap-2"
                          disabled={pauseWOMutation.isPending}
                        >
                          <Pause size={16} />
                          Pause
                        </button>
                        <button
                          onClick={() => completeWOMutation.mutate(wo.id)}
                          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2"
                          disabled={completeWOMutation.isPending}
                        >
                          <CheckCircle size={16} />
                          Complete
                        </button>
                      </>
                    )}
                    
                    {wo.state === 'PAUSED' && (
                      <button
                        onClick={() => startWOMutation.mutate(wo.id)}
                        className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors flex items-center gap-2"
                        disabled={startWOMutation.isPending}
                      >
                        <Play size={16} />
                        Resume
                      </button>
                    )}
                  </div>
                </div>

                {/* Progress Bar */}
                <div className="mb-4">
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-sm font-medium text-gray-700">Progress</span>
                    <span className="text-sm font-bold text-blue-600">{wo.progress_percentage.toFixed(1)}%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2.5">
                    <div
                      className="bg-blue-600 h-2.5 rounded-full transition-all"
                      style={{ width: `${wo.progress_percentage}%` }}
                    ></div>
                  </div>
                </div>

                {/* Dependency Warning */}
                {wo.state === 'PENDING' && !wo.can_start && wo.dependency_reason && (
                  <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3 flex items-start gap-2">
                    <AlertCircle className="text-yellow-600 flex-shrink-0 mt-0.5" size={18} />
                    <div>
                      <p className="text-sm font-medium text-yellow-900">Cannot Start Yet</p>
                      <p className="text-sm text-yellow-700">{wo.dependency_reason}</p>
                    </div>
                  </div>
                )}

                {/* Timestamps */}
                <div className="flex items-center gap-4 text-xs text-gray-500 mt-4 pt-4 border-t">
                  <span>Created: {new Date(wo.created_at).toLocaleString()}</span>
                  {wo.started_at && <span>Started: {new Date(wo.started_at).toLocaleString()}</span>}
                  {wo.completed_at && <span>Completed: {new Date(wo.completed_at).toLocaleString()}</span>}
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};
