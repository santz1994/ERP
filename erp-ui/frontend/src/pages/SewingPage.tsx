/**
 * Copyright (c) 2026 PT Quty Karunia / Daniel Rizaldy - All Rights Reserved
 * File: SewingPage.tsx | Author: Daniel Rizaldy | Date: 2026-01-19
 * Updated: 2026-01-21 | Phase 16 Week 4 | PBAC Integration
 */

import { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { format } from 'date-fns';
import { 
  Shirt, 
  CheckSquare, 
  XCircle, 
  AlertTriangle,
  Tag,
  ArrowRight,
  RefreshCw,
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
  defect_summary?: Record<string, number>;
}

interface QCRecord {
  id: number;
  work_order_id: number;
  inspector_id: number;
  check_qty: number;
  pass_qty: number;
  fail_qty: number;
  defects_found: Record<string, number>;
  timestamp: string;
}

export default function SewingPage() {
  const [selectedWO, setSelectedWO] = useState<number | null>(null);
  const [qcMode, setQcMode] = useState(false);
  const [checkQty, setCheckQty] = useState<number>(0);
  const [passQty, setPassQty] = useState<number>(0);
  const [failQty, setFailQty] = useState<number>(0);
  const [defects, setDefects] = useState<Record<string, number>>({});
  const queryClient = useQueryClient();

  // Permission checks (PBAC - Phase 16 Week 4)
  const canViewStatus = usePermission('sewing.view_status');
  const canAcceptTransfer = usePermission('sewing.accept_transfer');
  const canValidateInput = usePermission('sewing.validate_input');
  const canInlineQC = usePermission('sewing.inline_qc');
  const canCreateTransfer = usePermission('sewing.create_transfer');
  const canReturnToStage = usePermission('sewing.return_to_stage');

  const defectTypes = [
    'Broken Stitch',
    'Skip Stitch',
    'Wrong Thread Color',
    'Dirty/Stained',
    'Uneven Seam',
    'Missing Component',
    'Wrong Size',
    'Measurement Error'
  ];

  // Fetch work orders
  const { data: workOrders, isLoading } = useQuery({
    queryKey: ['sewing-work-orders'],
    queryFn: async () => {
      const token = localStorage.getItem('access_token');
      const response = await axios.get(`${API_BASE}/sewing/work-orders`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      return response.data;
    },
    refetchInterval: 5000
  });

  // Fetch QC history
  const { data: qcHistory } = useQuery({
    queryKey: ['sewing-qc', selectedWO],
    queryFn: async () => {
      if (!selectedWO) return [];
      const token = localStorage.getItem('access_token');
      const response = await axios.get(`${API_BASE}/qc/work-order/${selectedWO}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      return response.data;
    },
    enabled: !!selectedWO
  });

  // Start WO
  const startWO = useMutation({
    mutationFn: async (woId: number) => {
      const token = localStorage.getItem('access_token');
      return axios.post(`${API_BASE}/sewing/work-order/${woId}/start`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['sewing-work-orders'] });
    }
  });

  // Submit QC inspection
  const submitQC = useMutation({
    mutationFn: async (data: {
      work_order_id: number;
      check_qty: number;
      pass_qty: number;
      fail_qty: number;
      defects_found: Record<string, number>;
    }) => {
      const token = localStorage.getItem('access_token');
      return axios.post(`${API_BASE}/qc/inspect`, data, {
        headers: { Authorization: `Bearer ${token}` }
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['sewing-work-orders'] });
      queryClient.invalidateQueries({ queryKey: ['sewing-qc'] });
      resetQCForm();
    }
  });

  // Attach label
  const attachLabel = useMutation({
    mutationFn: async (woId: number) => {
      const token = localStorage.getItem('access_token');
      return axios.post(`${API_BASE}/sewing/work-order/${woId}/attach-label`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['sewing-work-orders'] });
    }
  });

  // Request rework
  const requestRework = useMutation({
    mutationFn: async (data: { woId: number; rework_qty: number; reason: string }) => {
      const token = localStorage.getItem('access_token');
      return axios.post(`${API_BASE}/sewing/work-order/${data.woId}/rework`, {
        rework_qty: data.rework_qty,
        reason: data.reason
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['sewing-work-orders'] });
    }
  });

  const resetQCForm = () => {
    setQcMode(false);
    setCheckQty(0);
    setPassQty(0);
    setFailQty(0);
    setDefects({});
  };

  const handleDefectChange = (defectType: string, value: number) => {
    setDefects(prev => ({
      ...prev,
      [defectType]: value
    }));
  };

  const getTotalDefects = () => {
    return Object.values(defects).reduce((sum, count) => sum + count, 0);
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 flex items-center">
          <Shirt className="w-8 h-8 mr-3 text-purple-600" />
          Sewing Department
        </h1>
        <p className="text-gray-500 mt-1">
          {format(new Date(), 'EEEE, dd MMMM yyyy • HH:mm')} WIB
        </p>
      </div>

      {/* Work Orders Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {workOrders?.map((wo: WorkOrder) => (
          <div key={wo.id} className="bg-white rounded-lg shadow-lg overflow-hidden">
            {/* Card Header */}
            <div className="bg-gradient-to-r from-purple-600 to-purple-700 p-4 text-white">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-lg font-semibold">WO #{wo.id}</h3>
                  <p className="text-sm opacity-90">MO #{wo.mo_id}</p>
                </div>
                <span className={`px-3 py-1 rounded-full text-xs font-medium ${
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
              {/* Quantities */}
              <div className="grid grid-cols-3 gap-4 text-center">
                <div>
                  <p className="text-xs text-gray-500">Input</p>
                  <p className="text-xl font-bold text-gray-900">{wo.input_qty}</p>
                </div>
                <div>
                  <p className="text-xs text-gray-500">Output</p>
                  <p className="text-xl font-bold text-green-600">{wo.output_qty}</p>
                </div>
                <div>
                  <p className="text-xs text-gray-500">Reject</p>
                  <p className="text-xl font-bold text-red-600">{wo.reject_qty}</p>
                </div>
              </div>

              {/* Defect Summary */}
              {wo.defect_summary && Object.keys(wo.defect_summary).length > 0 && (
                <div className="bg-red-50 p-3 rounded">
                  <div className="flex items-center mb-2">
                    <AlertTriangle className="w-4 h-4 text-red-600 mr-2" />
                    <span className="text-sm font-medium text-red-800">Defects Found</span>
                  </div>
                  <div className="text-xs text-red-700 space-y-1">
                    {Object.entries(wo.defect_summary).map(([defect, count]) => (
                      <div key={defect} className="flex justify-between">
                        <span>{defect}:</span>
                        <span className="font-medium">{count}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Actions */}
              <div className="space-y-2">
                {wo.status === 'Pending' && canAcceptTransfer && (
                  <button
                    onClick={() => startWO.mutate(wo.id)}
                    disabled={startWO.isPending}
                    className="w-full bg-purple-600 text-white px-4 py-2 rounded hover:bg-purple-700 transition disabled:opacity-50 text-sm font-medium"
                  >
                    Start Sewing
                  </button>
                )}
                {wo.status === 'Pending' && !canAcceptTransfer && (
                  <div className="w-full bg-gray-100 text-gray-500 px-4 py-2 rounded text-sm font-medium flex items-center justify-center">
                    <Lock className="w-4 h-4 mr-2" />
                    No Permission
                  </div>
                )}

                {wo.status === 'Running' && (
                  <>
                    {canInlineQC ? (
                      <button
                        onClick={() => {
                          setSelectedWO(wo.id);
                          setQcMode(true);
                        }}
                        className="w-full bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 transition text-sm font-medium flex items-center justify-center"
                      >
                        <CheckSquare className="w-4 h-4 mr-2" />
                        QC Inspection (Inspector Only)
                      </button>
                    ) : (
                      <div className="w-full bg-gray-100 text-gray-500 px-4 py-2 rounded text-sm font-medium flex items-center justify-center">
                        <Lock className="w-4 h-4 mr-2" />
                        QC Inspector Only
                      </div>
                    )}

                    {canValidateInput && (
                      <button
                        onClick={() => attachLabel.mutate(wo.id)}
                        disabled={attachLabel.isPending}
                        className="w-full bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 transition disabled:opacity-50 text-sm font-medium flex items-center justify-center"
                      >
                        <Tag className="w-4 h-4 mr-2" />
                        Attach Label
                      </button>
                    )}
                  </>
                )}

                {wo.reject_qty > 0 && canReturnToStage && (
                  <button
                    onClick={() => {
                      const reason = prompt('Rework reason:');
                      if (reason) {
                        requestRework.mutate({
                          woId: wo.id,
                          rework_qty: wo.reject_qty,
                          reason
                        });
                      }
                    }}
                    className="w-full bg-orange-600 text-white px-4 py-2 rounded hover:bg-orange-700 transition text-sm font-medium flex items-center justify-center"
                  >
                    <RefreshCw className="w-4 h-4 mr-2" />
                    Request Rework ({wo.reject_qty} units)
                  </button>
                )}

                <button
                  onClick={() => setSelectedWO(wo.id)}
                  className="w-full bg-gray-100 text-gray-700 px-4 py-2 rounded hover:bg-gray-200 transition text-sm font-medium"
                >
                  View QC History
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* QC Inspection Modal */}
      {qcMode && selectedWO && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <h3 className="text-xl font-bold mb-4 flex items-center">
                <CheckSquare className="w-6 h-6 mr-2 text-blue-600" />
                QC Inspection - WO #{selectedWO}
              </h3>
              
              <div className="space-y-4">
                {/* Quantities */}
                <div className="grid grid-cols-3 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Check Qty
                    </label>
                    <input
                      type="number"
                      value={checkQty}
                      onChange={(e) => {
                        const val = Number(e.target.value);
                        setCheckQty(val);
                        setPassQty(0);
                        setFailQty(0);
                      }}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Pass Qty
                    </label>
                    <input
                      type="number"
                      value={passQty}
                      onChange={(e) => {
                        const val = Number(e.target.value);
                        setPassQty(val);
                        setFailQty(checkQty - val);
                      }}
                      max={checkQty}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Fail Qty
                    </label>
                    <input
                      type="number"
                      value={failQty}
                      readOnly
                      className="w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-50"
                    />
                  </div>
                </div>

                {/* Defect Types */}
                {failQty > 0 && (
                  <div className="border-t pt-4">
                    <h4 className="font-medium text-gray-900 mb-3">Defect Classification</h4>
                    <div className="grid grid-cols-2 gap-3">
                      {defectTypes.map(defectType => (
                        <div key={defectType}>
                          <label className="block text-sm text-gray-700 mb-1">
                            {defectType}
                          </label>
                          <input
                            type="number"
                            value={defects[defectType] || 0}
                            onChange={(e) => handleDefectChange(defectType, Number(e.target.value))}
                            min={0}
                            max={failQty}
                            className="w-full px-2 py-1 border border-gray-300 rounded text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                          />
                        </div>
                      ))}
                    </div>
                    <div className="mt-3 p-2 bg-gray-50 rounded">
                      <span className="text-sm text-gray-700">
                        Total Defects: <span className="font-medium">{getTotalDefects()}</span> / {failQty}
                      </span>
                    </div>
                  </div>
                )}
              </div>

              <div className="flex gap-3 mt-6">
                <button
                  onClick={resetQCForm}
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-50 transition"
                >
                  Cancel
                </button>
                <button
                  onClick={() => submitQC.mutate({
                    work_order_id: selectedWO,
                    check_qty: checkQty,
                    pass_qty: passQty,
                    fail_qty: failQty,
                    defects_found: defects
                  })}
                  disabled={submitQC.isPending || checkQty === 0 || passQty + failQty !== checkQty}
                  className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition disabled:opacity-50"
                >
                  {submitQC.isPending ? 'Submitting...' : 'Submit Inspection'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* QC History Modal */}
      {!qcMode && selectedWO && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-xl font-bold">QC History - WO #{selectedWO}</h3>
                <button
                  onClick={() => setSelectedWO(null)}
                  className="text-gray-500 hover:text-gray-700"
                >
                  ×
                </button>
              </div>
              
              <div className="space-y-4">
                {qcHistory?.map((record: QCRecord) => (
                  <div key={record.id} className="border rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm text-gray-500">
                        {format(new Date(record.timestamp), 'dd MMM yyyy HH:mm')}
                      </span>
                      <span className="text-sm font-medium">
                        Inspector #{record.inspector_id}
                      </span>
                    </div>
                    <div className="grid grid-cols-3 gap-4 text-center mb-3">
                      <div>
                        <p className="text-xs text-gray-500">Checked</p>
                        <p className="text-lg font-bold">{record.check_qty}</p>
                      </div>
                      <div>
                        <p className="text-xs text-gray-500">Pass</p>
                        <p className="text-lg font-bold text-green-600">{record.pass_qty}</p>
                      </div>
                      <div>
                        <p className="text-xs text-gray-500">Fail</p>
                        <p className="text-lg font-bold text-red-600">{record.fail_qty}</p>
                      </div>
                    </div>
                    {Object.keys(record.defects_found).length > 0 && (
                      <div className="bg-red-50 p-2 rounded text-xs">
                        <span className="font-medium">Defects:</span>
                        {Object.entries(record.defects_found).map(([defect, count]) => (
                          <span key={defect} className="ml-2">
                            {defect}: {count}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
