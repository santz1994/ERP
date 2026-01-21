/**
 * Copyright (c) 2026 PT Quty Karunia / Daniel Rizaldy - All Rights Reserved
 * File: CuttingPage.tsx | Author: Daniel Rizaldy | Date: 2026-01-19
 * Updated: 2026-01-21 | Phase 16 Week 4 | PBAC Integration
 */

import { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { format } from 'date-fns';
import { 
  Scissors, 
  AlertCircle, 
  CheckCircle, 
  Clock, 
  Package,
  TrendingUp,
  TrendingDown,
  ArrowRight,
  Lock
} from 'lucide-react';
import axios from 'axios';
import { usePermission } from '@/hooks/usePermission';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

interface WorkOrder {
  id: number;
  mo_id: number;
  department: string;
  status: string;
  input_qty: number;
  output_qty: number;
  reject_qty: number;
  start_time: string | null;
  end_time: string | null;
}

interface LineStatus {
  line_id: string;
  current_article: string | null;
  is_occupied: boolean;
  destination: string | null;
}

export default function CuttingPage() {
  const [selectedWO, setSelectedWO] = useState<WorkOrder | null>(null);
  const [outputQty, setOutputQty] = useState<number>(0);
  const [rejectQty, setRejectQty] = useState<number>(0);
  const queryClient = useQueryClient();

  // Permission checks (PBAC - Phase 16 Week 4)
  const canViewStatus = usePermission('cutting.view_status');
  const canAllocateMaterial = usePermission('cutting.allocate_material');
  const canCompleteOperation = usePermission('cutting.complete_operation');
  const canHandleVariance = usePermission('cutting.handle_variance');
  const canLineClearance = usePermission('cutting.line_clearance');
  const canCreateTransfer = usePermission('cutting.create_transfer');

  // Fetch active work orders
  const { data: workOrders, isLoading } = useQuery({
    queryKey: ['cutting-work-orders'],
    queryFn: async () => {
      const token = localStorage.getItem('access_token');
      const response = await axios.get(`${API_BASE}/cutting/work-orders`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      return response.data;
    },
    refetchInterval: 5000 // Refresh every 5 seconds
  });

  // Fetch line status
  const { data: lineStatus } = useQuery({
    queryKey: ['line-status', 'cutting'],
    queryFn: async () => {
      const token = localStorage.getItem('access_token');
      const response = await axios.get(`${API_BASE}/cutting/line-status`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      return response.data;
    },
    refetchInterval: 3000
  });

  // Start work order mutation
  const startWO = useMutation({
    mutationFn: async (woId: number) => {
      const token = localStorage.getItem('access_token');
      return axios.post(`${API_BASE}/cutting/work-order/${woId}/start`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['cutting-work-orders'] });
    }
  });

  // Complete work order mutation
  const completeWO = useMutation({
    mutationFn: async (data: { woId: number; output_qty: number; reject_qty: number }) => {
      const token = localStorage.getItem('access_token');
      return axios.post(`${API_BASE}/cutting/work-order/${data.woId}/complete`, {
        output_qty: data.output_qty,
        reject_qty: data.reject_qty
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['cutting-work-orders'] });
      setSelectedWO(null);
      setOutputQty(0);
      setRejectQty(0);
    }
  });

  // Transfer to next department
  const transferToNext = useMutation({
    mutationFn: async (woId: number) => {
      const token = localStorage.getItem('access_token');
      return axios.post(`${API_BASE}/cutting/work-order/${woId}/transfer`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['cutting-work-orders'] });
    }
  });

  const getStatusBadge = (status: string) => {
    const badges: Record<string, { color: string; icon: any }> = {
      'Pending': { color: 'bg-gray-100 text-gray-800', icon: Clock },
      'Running': { color: 'bg-blue-100 text-blue-800', icon: Scissors },
      'Finished': { color: 'bg-green-100 text-green-800', icon: CheckCircle },
    };
    const badge = badges[status] || badges['Pending'];
    const Icon = badge.icon;
    return (
      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${badge.color}`}>
        <Icon className="w-3 h-3 mr-1" />
        {status}
      </span>
    );
  };

  const calculateVariance = (target: number, actual: number) => {
    const variance = actual - target;
    const percentageVariance = target > 0 ? (variance / target) * 100 : 0;
    return { variance, percentageVariance };
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 flex items-center">
              <Scissors className="w-8 h-8 mr-3 text-blue-600" />
              Cutting Department
            </h1>
            <p className="text-gray-500 mt-1">
              {format(new Date(), 'EEEE, dd MMMM yyyy • HH:mm')} WIB
            </p>
          </div>
          {lineStatus && (
            <div className="bg-white rounded-lg shadow p-4">
              <div className="flex items-center">
                <div className={`w-3 h-3 rounded-full mr-2 ${lineStatus.is_occupied ? 'bg-red-500' : 'bg-green-500'}`}></div>
                <span className="text-sm font-medium">
                  Line Status: {lineStatus.is_occupied ? 'Occupied' : 'Clear'}
                </span>
              </div>
              {lineStatus.current_article && (
                <p className="text-xs text-gray-500 mt-1">
                  Current: {lineStatus.current_article}
                </p>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Work Orders Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
        {workOrders?.map((wo: WorkOrder) => {
          const { variance, percentageVariance } = calculateVariance(wo.input_qty, wo.output_qty);
          
          return (
            <div key={wo.id} className="bg-white rounded-lg shadow-lg overflow-hidden hover:shadow-xl transition-shadow">
              {/* Card Header */}
              <div className="bg-gradient-to-r from-blue-600 to-blue-700 p-4 text-white">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-lg font-semibold">WO #{wo.id}</h3>
                    <p className="text-sm opacity-90">MO #{wo.mo_id}</p>
                  </div>
                  {getStatusBadge(wo.status)}
                </div>
              </div>

              {/* Card Body */}
              <div className="p-4 space-y-4">
                {/* Quantities */}
                <div className="grid grid-cols-3 gap-4">
                  <div className="text-center">
                    <p className="text-xs text-gray-500 mb-1">Target</p>
                    <p className="text-2xl font-bold text-gray-900">{wo.input_qty}</p>
                  </div>
                  <div className="text-center">
                    <p className="text-xs text-gray-500 mb-1">Output</p>
                    <p className="text-2xl font-bold text-blue-600">{wo.output_qty}</p>
                  </div>
                  <div className="text-center">
                    <p className="text-xs text-gray-500 mb-1">Reject</p>
                    <p className="text-2xl font-bold text-red-600">{wo.reject_qty}</p>
                  </div>
                </div>

                {/* Variance Indicator */}
                {wo.output_qty > 0 && (
                  <div className={`flex items-center justify-center p-2 rounded ${
                    variance > 0 ? 'bg-green-50' : variance < 0 ? 'bg-red-50' : 'bg-gray-50'
                  }`}>
                    {variance > 0 ? (
                      <TrendingUp className="w-4 h-4 text-green-600 mr-2" />
                    ) : variance < 0 ? (
                      <TrendingDown className="w-4 h-4 text-red-600 mr-2" />
                    ) : null}
                    <span className={`text-sm font-medium ${
                      variance > 0 ? 'text-green-600' : variance < 0 ? 'text-red-600' : 'text-gray-600'
                    }`}>
                      {variance > 0 ? 'Surplus' : variance < 0 ? 'Shortage' : 'On Target'}: {Math.abs(variance)} units ({Math.abs(percentageVariance).toFixed(1)}%)
                    </span>
                  </div>
                )}

                {/* Time Info */}
                <div className="text-xs text-gray-500 space-y-1">
                  {wo.start_time && (
                    <div className="flex items-center">
                      <Clock className="w-3 h-3 mr-1" />
                      Started: {format(new Date(wo.start_time), 'HH:mm')}
                    </div>
                  )}
                  {wo.end_time && (
                    <div className="flex items-center">
                      <CheckCircle className="w-3 h-3 mr-1" />
                      Completed: {format(new Date(wo.end_time), 'HH:mm')}
                    </div>
                  )}
                </div>

                {/* Actions */}
                <div className="flex gap-2">
                  {wo.status === 'Pending' && canAllocateMaterial && (
                    <button
                      onClick={() => startWO.mutate(wo.id)}
                      disabled={startWO.isPending}
                      className="flex-1 bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 transition disabled:opacity-50 text-sm font-medium"
                    >
                      Start Cutting
                    </button>
                  )}
                  {wo.status === 'Pending' && !canAllocateMaterial && (
                    <div className="flex-1 bg-gray-100 text-gray-500 px-4 py-2 rounded text-sm font-medium flex items-center justify-center">
                      <Lock className="w-4 h-4 mr-2" />
                      No Permission
                    </div>
                  )}

                  {wo.status === 'Running' && canCompleteOperation && (
                    <button
                      onClick={() => setSelectedWO(wo)}
                      className="flex-1 bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 transition text-sm font-medium"
                    >
                      Complete
                    </button>
                  )}
                  {wo.status === 'Running' && !canCompleteOperation && (
                    <div className="flex-1 bg-gray-100 text-gray-500 px-4 py-2 rounded text-sm font-medium flex items-center justify-center">
                      <Lock className="w-4 h-4 mr-2" />
                      No Permission
                    </div>
                  )}

                  {wo.status === 'Finished' && canCreateTransfer && (
                    <button
                      onClick={() => transferToNext.mutate(wo.id)}
                      disabled={transferToNext.isPending}
                      className="flex-1 bg-purple-600 text-white px-4 py-2 rounded hover:bg-purple-700 transition disabled:opacity-50 flex items-center justify-center text-sm font-medium"
                    >
                      Transfer to Next
                      <ArrowRight className="w-4 h-4 ml-2" />
                    </button>
                  )}
                  {wo.status === 'Finished' && !canCreateTransfer && (
                    <div className="flex-1 bg-gray-100 text-gray-500 px-4 py-2 rounded text-sm font-medium flex items-center justify-center">
                      <Lock className="w-4 h-4 mr-2" />
                      No Permission
                    </div>
                  )}
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Complete Work Order Modal */}
      {selectedWO && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4">
            <div className="p-6">
              <h3 className="text-xl font-bold mb-4">Complete Work Order #{selectedWO.id}</h3>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Output Quantity
                  </label>
                  <input
                    type="number"
                    value={outputQty}
                    onChange={(e) => setOutputQty(Number(e.target.value))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Enter actual output"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Reject Quantity
                  </label>
                  <input
                    type="number"
                    value={rejectQty}
                    onChange={(e) => setRejectQty(Number(e.target.value))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Enter reject quantity"
                  />
                </div>

                {/* Variance Preview */}
                {outputQty > 0 && (
                  <div className="bg-gray-50 p-3 rounded">
                    <p className="text-sm text-gray-700">
                      <span className="font-medium">Target:</span> {selectedWO.input_qty} units
                    </p>
                    <p className="text-sm text-gray-700 mt-1">
                      <span className="font-medium">Variance:</span>{' '}
                      <span className={outputQty > selectedWO.input_qty ? 'text-green-600' : outputQty < selectedWO.input_qty ? 'text-red-600' : 'text-gray-600'}>
                        {outputQty - selectedWO.input_qty > 0 ? '+' : ''}{outputQty - selectedWO.input_qty} units
                      </span>
                    </p>
                  </div>
                )}
              </div>

              <div className="flex gap-3 mt-6">
                <button
                  onClick={() => {
                    setSelectedWO(null);
                    setOutputQty(0);
                    setRejectQty(0);
                  }}
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-50 transition"
                >
                  Cancel
                </button>
                <button
                  onClick={() => completeWO.mutate({ 
                    woId: selectedWO.id, 
                    output_qty: outputQty, 
                    reject_qty: rejectQty 
                  })}
                  disabled={completeWO.isPending || outputQty === 0}
                  className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition disabled:opacity-50"
                >
                  {completeWO.isPending ? 'Saving...' : 'Complete WO'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Empty State */}
      {workOrders?.length === 0 && (
        <div className="text-center py-12">
          <Package className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No Work Orders</h3>
          <p className="text-gray-500">There are no active work orders for cutting department.</p>
        </div>
      )}
    </div>
  );
}
