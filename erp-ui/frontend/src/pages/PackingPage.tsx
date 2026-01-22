/**
 * Copyright (c) 2026 PT Quty Karunia / Daniel Rizaldy - All Rights Reserved
 * File: PackingPage.tsx | Author: Daniel Rizaldy | Date: 2026-01-19
 * Updated: 2026-01-21 | Phase 16 Week 4 | PBAC Integration
 */

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { format } from 'date-fns';
import { 
  Box, 
  FileText, 
  Truck,
  CheckCircle,
  AlertCircle,
  Plus,
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
  cartons_packed: number;
}

interface KanbanCard {
  id: number;
  card_number: string;
  department: string;
  item_code: string;
  qty_per_card: number;
  status: string;
  priority: number;
}

export default function PackingPage() {
  const [selectedWO, setSelectedWO] = useState<number | null>(null);
  const [cartonQty, setCartonQty] = useState<number>(0);
  const [pcsPerCarton, setPcsPerCarton] = useState<number>(0);
  const [showKanbanRequest, setShowKanbanRequest] = useState(false);
  const [kanbanItem, setKanbanItem] = useState('');
  const [kanbanQty, setKanbanQty] = useState<number>(0);
  const queryClient = useQueryClient();

  // Permission checks (PBAC - Phase 16 Week 4)
  const canViewStatus = usePermission('packing.view_status');
  const canSortByDestination = usePermission('packing.sort_by_destination');
  const canPackProduct = usePermission('packing.pack_product');
  const canLabelCarton = usePermission('packing.label_carton');
  const canCompleteOperation = usePermission('packing.complete_operation');

  const { data: workOrders, isLoading } = useQuery({
    queryKey: ['packing-work-orders'],
    queryFn: async () => {
      const token = localStorage.getItem('access_token');
      const response = await axios.get(`${API_BASE}/production/packing/pending`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      return response.data;
    },
    refetchInterval: 5000
  });

  const { data: kanbanCards } = useQuery({
    queryKey: ['kanban-cards'],
    queryFn: async () => {
      const token = localStorage.getItem('access_token');
      const response = await axios.get(`${API_BASE}/kanban/cards`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      return response.data;
    },
    refetchInterval: 3000
  });

  const startWO = useMutation({
    mutationFn: async (woId: number) => {
      const token = localStorage.getItem('access_token');
      return axios.post(`${API_BASE}/production/packing/work-order/${woId}/start`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['packing-work-orders'] });
    }
  });

  const recordPacking = useMutation({
    mutationFn: async (data: { woId: number; carton_qty: number; pcs_per_carton: number }) => {
      const token = localStorage.getItem('access_token');
      return axios.post(`${API_BASE}/production/packing/work-order/${data.woId}/pack`, {
        carton_qty: data.carton_qty,
        pcs_per_carton: data.pcs_per_carton
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['packing-work-orders'] });
      setSelectedWO(null);
      setCartonQty(0);
      setPcsPerCarton(0);
    }
  });

  const completePacking = useMutation({
    mutationFn: async (woId: number) => {
      const token = localStorage.getItem('access_token');
      return axios.post(`${API_BASE}/production/packing/work-order/${woId}/complete`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['packing-work-orders'] });
    }
  });

  const createKanbanCard = useMutation({
    mutationFn: async (data: { item_code: string; qty_per_card: number; priority: number }) => {
      const token = localStorage.getItem('access_token');
      return axios.post(`${API_BASE}/kanban/cards`, {
        department: 'Packing',
        ...data
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['kanban-cards'] });
      setShowKanbanRequest(false);
      setKanbanItem('');
      setKanbanQty(0);
    }
  });

  const getKanbanStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      'Requested': 'bg-yellow-100 text-yellow-800',
      'Approved': 'bg-blue-100 text-blue-800',
      'In Transit': 'bg-purple-100 text-purple-800',
      'Received': 'bg-green-100 text-green-800',
      'Rejected': 'bg-red-100 text-red-800'
    };
    return colors[status] || 'bg-gray-100 text-gray-800';
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-orange-600"></div>
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
              <Box className="w-8 h-8 mr-3 text-orange-600" />
              Packing Department
            </h1>
            <p className="text-gray-500 mt-1">
              {format(new Date(), 'EEEE, dd MMMM yyyy • HH:mm')} WIB
            </p>
          </div>
          <button
            onClick={() => setShowKanbanRequest(true)}
            className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition flex items-center shadow-md"
          >
            <Plus className="w-5 h-5 mr-2" />
            E-Kanban Request
          </button>
        </div>
      </div>

      {/* E-Kanban Cards Section */}
      {kanbanCards && kanbanCards.length > 0 && (
        <div className="mb-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
            <FileText className="w-6 h-6 mr-2 text-blue-600" />
            Active E-Kanban Cards
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {kanbanCards.map((card: KanbanCard) => (
              <div key={card.id} className="bg-white rounded-lg shadow p-4 border-l-4 border-blue-500">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs font-mono text-gray-500">{card.card_number}</span>
                  <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${getKanbanStatusColor(card.status)}`}>
                    {card.status}
                  </span>
                </div>
                <h3 className="font-semibold text-gray-900 mb-1">{card.item_code}</h3>
                <p className="text-sm text-gray-600">Qty: {card.qty_per_card} units</p>
                {card.priority === 1 && (
                  <div className="mt-2 flex items-center text-red-600 text-xs">
                    <AlertCircle className="w-3 h-3 mr-1" />
                    High Priority
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Work Orders Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {workOrders?.map((wo: WorkOrder) => (
          <div key={wo.id} className="bg-white rounded-lg shadow-lg overflow-hidden hover:shadow-xl transition-shadow">
            {/* Card Header */}
            <div className="bg-gradient-to-r from-orange-600 to-orange-700 p-4 text-white">
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
              {/* Progress */}
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-gray-600">Packing Progress</span>
                  <span className="font-medium text-gray-900">
                    {wo.output_qty} / {wo.input_qty}
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-orange-600 h-2 rounded-full transition-all"
                    style={{ width: `${Math.min((wo.output_qty / wo.input_qty) * 100, 100)}%` }}
                  ></div>
                </div>
              </div>

              {/* Stats */}
              <div className="space-y-2">
                <div className="flex items-center justify-between p-2 bg-blue-50 rounded">
                  <div className="flex items-center">
                    <Box className="w-4 h-4 text-blue-600 mr-2" />
                    <span className="text-sm text-blue-700">Cartons Packed</span>
                  </div>
                  <span className="text-lg font-bold text-blue-600">{wo.cartons_packed}</span>
                </div>

                <div className="flex items-center justify-between p-2 bg-green-50 rounded">
                  <span className="text-sm text-green-700">Pieces Packed</span>
                  <span className="text-lg font-bold text-green-600">{wo.output_qty}</span>
                </div>

                <div className="flex items-center justify-between p-2 bg-gray-50 rounded">
                  <span className="text-sm text-gray-700">Remaining</span>
                  <span className="text-lg font-bold text-gray-600">{wo.input_qty - wo.output_qty}</span>
                </div>
              </div>

              {/* Actions */}
              <div className="space-y-2">
                {wo.status === 'Pending' && (
                  <button
                    onClick={() => startWO.mutate(wo.id)}
                    disabled={startWO.isPending}
                    className="w-full bg-orange-600 text-white px-4 py-2 rounded hover:bg-orange-700 transition disabled:opacity-50 text-sm font-medium"
                  >
                    Start Packing
                  </button>
                )}

                {wo.status === 'Running' && (
                  <>
                    <button
                      onClick={() => setSelectedWO(wo.id)}
                      className="w-full bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 transition text-sm font-medium flex items-center justify-center"
                    >
                      <Box className="w-4 h-4 mr-2" />
                      Record Packing
                    </button>

                    <button
                      onClick={() => completePacking.mutate(wo.id)}
                      disabled={completePacking.isPending}
                      className="w-full bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 transition disabled:opacity-50 text-sm font-medium flex items-center justify-center"
                    >
                      <Truck className="w-4 h-4 mr-2" />
                      Complete & Ship
                    </button>
                  </>
                )}

                {wo.status === 'Finished' && (
                  <div className="flex items-center justify-center p-3 bg-green-50 rounded">
                    <CheckCircle className="w-5 h-5 text-green-600 mr-2" />
                    <span className="text-sm font-medium text-green-700">Ready for Shipment</span>
                  </div>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Record Packing Modal */}
      {selectedWO && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4">
            <div className="p-6">
              <h3 className="text-xl font-bold mb-4 flex items-center">
                <Box className="w-6 h-6 mr-2 text-blue-600" />
                Record Packing - WO #{selectedWO}
              </h3>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Number of Cartons
                  </label>
                  <input
                    type="number"
                    value={cartonQty}
                    onChange={(e) => setCartonQty(Number(e.target.value))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Enter carton quantity"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Pieces per Carton
                  </label>
                  <input
                    type="number"
                    value={pcsPerCarton}
                    onChange={(e) => setPcsPerCarton(Number(e.target.value))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Enter pieces per carton"
                  />
                </div>

                {cartonQty > 0 && pcsPerCarton > 0 && (
                  <div className="bg-blue-50 p-3 rounded">
                    <div className="flex justify-between text-sm">
                      <span className="text-blue-700">Total Pieces:</span>
                      <span className="font-bold text-blue-800">{cartonQty * pcsPerCarton}</span>
                    </div>
                  </div>
                )}

                <div className="bg-orange-50 p-3 rounded text-sm text-orange-700">
                  <p className="font-medium mb-1">Packing Requirements:</p>
                  <ul className="list-disc list-inside space-y-1 text-xs">
                    <li>Verify shipping marks</li>
                    <li>Check carton quality</li>
                    <li>Secure with proper sealing</li>
                    <li>Attach shipping labels</li>
                  </ul>
                </div>
              </div>

              <div className="flex gap-3 mt-6">
                <button
                  onClick={() => {
                    setSelectedWO(null);
                    setCartonQty(0);
                    setPcsPerCarton(0);
                  }}
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-50 transition"
                >
                  Cancel
                </button>
                <button
                  onClick={() => recordPacking.mutate({ 
                    woId: selectedWO, 
                    carton_qty: cartonQty,
                    pcs_per_carton: pcsPerCarton
                  })}
                  disabled={recordPacking.isPending || cartonQty === 0 || pcsPerCarton === 0}
                  className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition disabled:opacity-50"
                >
                  {recordPacking.isPending ? 'Recording...' : 'Record Packing'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* E-Kanban Request Modal */}
      {showKanbanRequest && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4">
            <div className="p-6">
              <h3 className="text-xl font-bold mb-4 flex items-center">
                <FileText className="w-6 h-6 mr-2 text-blue-600" />
                Create E-Kanban Card
              </h3>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Item Code
                  </label>
                  <input
                    type="text"
                    value={kanbanItem}
                    onChange={(e) => setKanbanItem(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="e.g., HOOK-001, BUTTON-002"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Quantity per Card
                  </label>
                  <input
                    type="number"
                    value={kanbanQty}
                    onChange={(e) => setKanbanQty(Number(e.target.value))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Enter quantity needed"
                  />
                </div>

                <div className="bg-blue-50 p-3 rounded text-sm text-blue-700">
                  <p className="font-medium mb-1">E-Kanban System:</p>
                  <p className="text-xs">
                    This card will be sent to Warehouse for accessory preparation.
                    You'll be notified when items are ready for pickup.
                  </p>
                </div>
              </div>

              <div className="flex gap-3 mt-6">
                <button
                  onClick={() => {
                    setShowKanbanRequest(false);
                    setKanbanItem('');
                    setKanbanQty(0);
                  }}
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-50 transition"
                >
                  Cancel
                </button>
                <button
                  onClick={() => createKanbanCard.mutate({ 
                    item_code: kanbanItem,
                    qty_per_card: kanbanQty,
                    priority: 0
                  })}
                  disabled={createKanbanCard.isPending || !kanbanItem || kanbanQty === 0}
                  className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition disabled:opacity-50"
                >
                  {createKanbanCard.isPending ? 'Creating...' : 'Create Card'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Empty State */}
      {workOrders?.length === 0 && (
        <div className="text-center py-12">
          <Box className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No Work Orders</h3>
          <p className="text-gray-500">There are no active work orders for packing department.</p>
        </div>
      )}
    </div>
  );
}
