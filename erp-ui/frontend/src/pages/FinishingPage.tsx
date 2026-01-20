/**
 * Copyright (c) 2026 PT Quty Karunia / Daniel Rizaldy - All Rights Reserved
 * File: FinishingPage.tsx | Author: Daniel Rizaldy | Date: 2026-01-19
 */

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { format } from 'date-fns';
import { 
  Package2, 
  CheckCircle, 
  XOctagon, 
  Sparkles,
  ArrowRight
} from 'lucide-react';
import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

interface WorkOrder {
  id: number;
  mo_id: number;
  department: string;
  status: string;
  input_qty: number;
  output_qty: number;
  reject_qty: number;
}

export default function FinishingPage() {
  const [selectedWO, setSelectedWO] = useState<number | null>(null);
  const [stuffedQty, setStuffedQty] = useState<number>(0);
  const [defectQty, setDefectQty] = useState<number>(0);
  const queryClient = useQueryClient();

  const { data: workOrders, isLoading } = useQuery({
    queryKey: ['finishing-work-orders'],
    queryFn: async () => {
      const token = localStorage.getItem('access_token');
      const response = await axios.get(`${API_BASE}/finishing/work-orders`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      return response.data;
    },
    refetchInterval: 5000
  });

  const startWO = useMutation({
    mutationFn: async (woId: number) => {
      const token = localStorage.getItem('access_token');
      return axios.post(`${API_BASE}/finishing/work-order/${woId}/start`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['finishing-work-orders'] });
    }
  });

  const recordStuffing = useMutation({
    mutationFn: async (data: { woId: number; stuffed_qty: number }) => {
      const token = localStorage.getItem('access_token');
      return axios.post(`${API_BASE}/finishing/work-order/${data.woId}/stuffing`, {
        stuffed_qty: data.stuffed_qty
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['finishing-work-orders'] });
      setSelectedWO(null);
      setStuffedQty(0);
    }
  });

  const finalQC = useMutation({
    mutationFn: async (data: { woId: number; pass_qty: number; defect_qty: number }) => {
      const token = localStorage.getItem('access_token');
      return axios.post(`${API_BASE}/finishing/work-order/${data.woId}/final-qc`, {
        pass_qty: data.pass_qty,
        defect_qty: data.defect_qty
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['finishing-work-orders'] });
      setSelectedWO(null);
      setDefectQty(0);
    }
  });

  const completeFinishing = useMutation({
    mutationFn: async (woId: number) => {
      const token = localStorage.getItem('access_token');
      return axios.post(`${API_BASE}/finishing/work-order/${woId}/complete`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['finishing-work-orders'] });
    }
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 flex items-center">
          <Sparkles className="w-8 h-8 mr-3 text-green-600" />
          Finishing Department
        </h1>
        <p className="text-gray-500 mt-1">
          {format(new Date(), 'EEEE, dd MMMM yyyy • HH:mm')} WIB
        </p>
      </div>

      {/* Work Orders Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {workOrders?.map((wo: WorkOrder) => (
          <div key={wo.id} className="bg-white rounded-lg shadow-lg overflow-hidden hover:shadow-xl transition-shadow">
            {/* Card Header */}
            <div className="bg-gradient-to-r from-green-600 to-green-700 p-4 text-white">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-lg font-semibold">WO #{wo.id}</h3>
                  <p className="text-sm opacity-90">MO #{wo.mo_id}</p>
                </div>
                <span className={`px-2.5 py-1 rounded-full text-xs font-medium ${
                  wo.status === 'Running' ? 'bg-blue-100 text-blue-800' :
                  wo.status === 'Finished' ? 'bg-green-100 text-green-800' :
                  'bg-gray-100 text-gray-800'
                }`}>
                  {wo.status}
                </span>
              </div>
            </div>

            {/* Card Body */}
            <div className="p-4 space-y-4">
              {/* Progress Bar */}
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-gray-600">Progress</span>
                  <span className="font-medium text-gray-900">
                    {wo.output_qty} / {wo.input_qty}
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-green-600 h-2 rounded-full transition-all"
                    style={{ width: `${(wo.output_qty / wo.input_qty) * 100}%` }}
                  ></div>
                </div>
              </div>

              {/* Stats */}
              <div className="grid grid-cols-2 gap-3 text-center">
                <div className="bg-green-50 p-3 rounded">
                  <p className="text-xs text-green-700 mb-1">Output</p>
                  <p className="text-xl font-bold text-green-600">{wo.output_qty}</p>
                </div>
                <div className="bg-red-50 p-3 rounded">
                  <p className="text-xs text-red-700 mb-1">Defects</p>
                  <p className="text-xl font-bold text-red-600">{wo.reject_qty}</p>
                </div>
              </div>

              {/* Quality Rate */}
              <div className="bg-blue-50 p-3 rounded">
                <p className="text-xs text-blue-700 mb-1">Quality Rate</p>
                <p className="text-lg font-bold text-blue-600">
                  {wo.output_qty > 0 
                    ? ((wo.output_qty - wo.reject_qty) / wo.output_qty * 100).toFixed(1)
                    : '0.0'}%
                </p>
              </div>

              {/* Actions */}
              <div className="space-y-2">
                {wo.status === 'Pending' && (
                  <button
                    onClick={() => startWO.mutate(wo.id)}
                    disabled={startWO.isPending}
                    className="w-full bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 transition disabled:opacity-50 text-sm font-medium"
                  >
                    Start Finishing
                  </button>
                )}

                {wo.status === 'Running' && (
                  <>
                    <button
                      onClick={() => setSelectedWO(wo.id)}
                      className="w-full bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 transition text-sm font-medium flex items-center justify-center"
                    >
                      <Package2 className="w-4 h-4 mr-2" />
                      Record Stuffing
                    </button>

                    <button
                      onClick={() => {
                        setSelectedWO(wo.id);
                        setDefectQty(0);
                      }}
                      className="w-full bg-purple-600 text-white px-4 py-2 rounded hover:bg-purple-700 transition text-sm font-medium flex items-center justify-center"
                    >
                      <CheckCircle className="w-4 h-4 mr-2" />
                      Final QC
                    </button>

                    <button
                      onClick={() => completeFinishing.mutate(wo.id)}
                      disabled={completeFinishing.isPending}
                      className="w-full bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 transition disabled:opacity-50 text-sm font-medium flex items-center justify-center"
                    >
                      <ArrowRight className="w-4 h-4 mr-2" />
                      Complete Finishing
                    </button>
                  </>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Stuffing Modal */}
      {selectedWO && stuffedQty === 0 && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4">
            <div className="p-6">
              <h3 className="text-xl font-bold mb-4 flex items-center">
                <Package2 className="w-6 h-6 mr-2 text-blue-600" />
                Record Stuffing - WO #{selectedWO}
              </h3>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Stuffed Quantity
                  </label>
                  <input
                    type="number"
                    value={stuffedQty}
                    onChange={(e) => setStuffedQty(Number(e.target.value))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Enter stuffed quantity"
                  />
                </div>

                <div className="bg-blue-50 p-3 rounded text-sm text-blue-700">
                  <p>Process: Stuffing with filling material</p>
                  <p className="mt-1">Ensure proper filling density</p>
                </div>
              </div>

              <div className="flex gap-3 mt-6">
                <button
                  onClick={() => {
                    setSelectedWO(null);
                    setStuffedQty(0);
                  }}
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-50 transition"
                >
                  Cancel
                </button>
                <button
                  onClick={() => recordStuffing.mutate({ 
                    woId: selectedWO, 
                    stuffed_qty: stuffedQty 
                  })}
                  disabled={recordStuffing.isPending || stuffedQty === 0}
                  className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition disabled:opacity-50"
                >
                  {recordStuffing.isPending ? 'Recording...' : 'Record Stuffing'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Final QC Modal */}
      {selectedWO && defectQty >= 0 && stuffedQty === 0 && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4">
            <div className="p-6">
              <h3 className="text-xl font-bold mb-4 flex items-center">
                <CheckCircle className="w-6 h-6 mr-2 text-purple-600" />
                Final QC - WO #{selectedWO}
              </h3>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Total Inspected
                  </label>
                  <input
                    type="number"
                    value={stuffedQty}
                    onChange={(e) => {
                      const val = Number(e.target.value);
                      setStuffedQty(val);
                      if (defectQty > val) setDefectQty(0);
                    }}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                    placeholder="Enter total inspected"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Defect Quantity
                  </label>
                  <input
                    type="number"
                    value={defectQty}
                    onChange={(e) => setDefectQty(Number(e.target.value))}
                    max={stuffedQty}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-red-500"
                    placeholder="Enter defect quantity"
                  />
                </div>

                {stuffedQty > 0 && (
                  <div className="bg-green-50 p-3 rounded">
                    <div className="flex justify-between text-sm">
                      <span className="text-green-700">Pass Quantity:</span>
                      <span className="font-bold text-green-800">{stuffedQty - defectQty}</span>
                    </div>
                    <div className="flex justify-between text-sm mt-1">
                      <span className="text-green-700">Pass Rate:</span>
                      <span className="font-bold text-green-800">
                        {((stuffedQty - defectQty) / stuffedQty * 100).toFixed(1)}%
                      </span>
                    </div>
                  </div>
                )}
              </div>

              <div className="flex gap-3 mt-6">
                <button
                  onClick={() => {
                    setSelectedWO(null);
                    setStuffedQty(0);
                    setDefectQty(0);
                  }}
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-50 transition"
                >
                  Cancel
                </button>
                <button
                  onClick={() => finalQC.mutate({ 
                    woId: selectedWO, 
                    pass_qty: stuffedQty - defectQty,
                    defect_qty: defectQty 
                  })}
                  disabled={finalQC.isPending || stuffedQty === 0}
                  className="flex-1 px-4 py-2 bg-purple-600 text-white rounded-md hover:bg-purple-700 transition disabled:opacity-50"
                >
                  {finalQC.isPending ? 'Submitting...' : 'Submit QC'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Empty State */}
      {workOrders?.length === 0 && (
        <div className="text-center py-12">
          <Sparkles className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No Work Orders</h3>
          <p className="text-gray-500">There are no active work orders for finishing department.</p>
        </div>
      )}
    </div>
  );
}
