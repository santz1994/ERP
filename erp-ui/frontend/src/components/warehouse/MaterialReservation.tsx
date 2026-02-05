/**
 * Material Reservation Interface - Soft Allocation for WOs
 * Priority 3.2: Warehouse Integration
 * Created: 2026-02-04
 */

import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/api/client';
import { 
  Lock, 
  Unlock, 
  CheckCircle, 
  AlertCircle,
  Package,
  Calendar,
  Info
} from 'lucide-react';

interface MaterialReservation {
  id: number;
  wo_id: number;
  wo_code: string;
  material_id: number;
  material_code: string;
  material_name: string;
  qty_reserved: number;
  uom: string;
  stock_quant_id?: number;
  lot_number?: string;
  reserved_at: string;
  released_at?: string;
  state: 'RESERVED' | 'RELEASED' | 'CONSUMED';
}

interface MaterialReservationProps {
  woId?: number;
  materialId?: number;
}

export const MaterialReservation: React.FC<MaterialReservationProps> = ({
  woId,
  materialId
}) => {
  const queryClient = useQueryClient();
  const [selectedWO, setSelectedWO] = useState<number | undefined>(woId);

  // Fetch Work Orders
  const { data: workOrders } = useQuery({
    queryKey: ['work-orders-for-reservation'],
    queryFn: async () => {
      const response = await apiClient.get('/work-orders?state=READY,RUNNING');
      return response.data;
    }
  });

  // Fetch Material Reservations
  const { data: reservations, isLoading } = useQuery({
    queryKey: ['material-reservations', selectedWO, materialId],
    queryFn: async () => {
      const params = new URLSearchParams();
      if (selectedWO) params.append('wo_id', selectedWO.toString());
      if (materialId) params.append('material_id', materialId.toString());
      const response = await apiClient.get(`/material-allocation/reservations?${params}`);
      return response.data as MaterialReservation[];
    },
    enabled: !!selectedWO || !!materialId
  });

  // Reserve Materials Mutation
  const reserveMutation = useMutation({
    mutationFn: async (data: { wo_id: number; auto_allocate?: boolean }) => {
      const response = await apiClient.post('/material-allocation/reserve', data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['material-reservations'] });
      queryClient.invalidateQueries({ queryKey: ['stock-quants'] });
      alert('Materials reserved successfully!');
    },
    onError: (error: any) => {
      alert('Error: ' + (error.response?.data?.detail || 'Failed to reserve materials'));
    }
  });

  // Release Reservation Mutation
  const releaseMutation = useMutation({
    mutationFn: async (reservationId: number) => {
      const response = await apiClient.post(`/material-allocation/reservations/${reservationId}/release`);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['material-reservations'] });
      queryClient.invalidateQueries({ queryKey: ['stock-quants'] });
      alert('Reservation released!');
    },
    onError: (error: any) => {
      alert('Error: ' + (error.response?.data?.detail || 'Failed to release reservation'));
    }
  });

  const handleReserveForWO = (woId: number) => {
    if (confirm('Reserve materials for this Work Order?\n\nSystem will auto-allocate based on BOM and FIFO.')) {
      reserveMutation.mutate({ wo_id: woId, auto_allocate: true });
    }
  };

  const handleReleaseReservation = (reservationId: number, materialName: string) => {
    if (confirm(`Release reservation for "${materialName}"?\n\nMaterial will become available again.`)) {
      releaseMutation.mutate(reservationId);
    }
  };

  const getStateColor = (state: string) => {
    switch (state) {
      case 'RESERVED': return 'bg-orange-100 text-orange-800 border-orange-300';
      case 'CONSUMED': return 'bg-green-100 text-green-800 border-green-300';
      case 'RELEASED': return 'bg-gray-100 text-gray-800 border-gray-300';
      default: return 'bg-gray-100 text-gray-800 border-gray-300';
    }
  };

  const getStateIcon = (state: string) => {
    switch (state) {
      case 'RESERVED': return <Lock size={14} />;
      case 'CONSUMED': return <CheckCircle size={14} />;
      case 'RELEASED': return <Unlock size={14} />;
      default: return <Info size={14} />;
    }
  };

  const totalReserved = reservations?.filter(r => r.state === 'RESERVED').length || 0;
  const totalConsumed = reservations?.filter(r => r.state === 'CONSUMED').length || 0;
  const totalReleased = reservations?.filter(r => r.state === 'RELEASED').length || 0;

  return (
    <div className="space-y-6">
      {/* Header & Controls */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <div className="bg-orange-100 p-3 rounded-lg">
              <Lock className="text-orange-600" size={32} />
            </div>
            <div>
              <h2 className="text-2xl font-bold text-gray-900">Material Reservations</h2>
              <p className="text-gray-600">Soft allocation for work orders</p>
            </div>
          </div>
        </div>

        {/* WO Selector */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Work Order
            </label>
            <select
              value={selectedWO || ''}
              onChange={(e) => setSelectedWO(e.target.value ? Number(e.target.value) : undefined)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">Select Work Order...</option>
              {workOrders?.map((wo: any) => (
                <option key={wo.id} value={wo.id}>
                  {wo.wo_code} - {wo.department} ({wo.state})
                </option>
              ))}
            </select>
          </div>

          {selectedWO && (
            <div className="flex items-end">
              <button
                onClick={() => handleReserveForWO(selectedWO)}
                disabled={reserveMutation.isPending}
                className="w-full px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 transition-colors flex items-center justify-center gap-2 disabled:opacity-50"
              >
                {reserveMutation.isPending ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                    Reserving...
                  </>
                ) : (
                  <>
                    <Lock size={18} />
                    Reserve Materials (Auto FIFO)
                  </>
                )}
              </button>
            </div>
          )}
        </div>

        {/* Summary Stats */}
        {reservations && reservations.length > 0 && (
          <div className="grid grid-cols-4 gap-4 mt-6">
            <div className="bg-gray-50 rounded-lg p-3 text-center">
              <div className="text-2xl font-bold text-gray-700">{reservations.length}</div>
              <div className="text-xs text-gray-600">Total Lines</div>
            </div>
            <div className="bg-orange-50 rounded-lg p-3 text-center">
              <div className="text-2xl font-bold text-orange-600">{totalReserved}</div>
              <div className="text-xs text-gray-600">Reserved</div>
            </div>
            <div className="bg-green-50 rounded-lg p-3 text-center">
              <div className="text-2xl font-bold text-green-600">{totalConsumed}</div>
              <div className="text-xs text-gray-600">Consumed</div>
            </div>
            <div className="bg-gray-50 rounded-lg p-3 text-center">
              <div className="text-2xl font-bold text-gray-600">{totalReleased}</div>
              <div className="text-xs text-gray-600">Released</div>
            </div>
          </div>
        )}
      </div>

      {/* Reservations List */}
      <div className="bg-white rounded-lg shadow-md">
        {isLoading ? (
          <div className="p-12 text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p className="text-gray-600">Loading reservations...</p>
          </div>
        ) : !selectedWO && !materialId ? (
          <div className="p-12 text-center">
            <Lock className="mx-auto text-gray-400 mb-4" size={64} />
            <h4 className="text-lg font-semibold text-gray-900 mb-2">No Work Order Selected</h4>
            <p className="text-gray-600">Select a work order to view its material reservations</p>
          </div>
        ) : reservations?.length === 0 ? (
          <div className="p-12 text-center">
            <AlertCircle className="mx-auto text-gray-400 mb-4" size={64} />
            <h4 className="text-lg font-semibold text-gray-900 mb-2">No Reservations Found</h4>
            <p className="text-gray-600">Click "Reserve Materials" to auto-allocate based on BOM</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 border-b-2 border-gray-200">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Material</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Work Order</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Lot/Batch</th>
                  <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Qty Reserved</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Reserved At</th>
                  <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase">State</th>
                  <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {reservations?.map((reservation) => (
                  <tr key={reservation.id} className="hover:bg-gray-50">
                    <td className="px-4 py-3">
                      <div>
                        <div className="font-semibold text-gray-900">{reservation.material_code}</div>
                        <div className="text-sm text-gray-600 truncate max-w-xs">{reservation.material_name}</div>
                      </div>
                    </td>
                    <td className="px-4 py-3 text-sm">
                      <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded text-xs font-medium">
                        {reservation.wo_code}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-sm">
                      {reservation.lot_number ? (
                        <span className="px-2 py-1 bg-purple-100 text-purple-800 rounded text-xs font-medium">
                          {reservation.lot_number}
                        </span>
                      ) : (
                        <span className="text-gray-400">-</span>
                      )}
                    </td>
                    <td className="px-4 py-3 text-right">
                      <div className="font-bold text-gray-900">{reservation.qty_reserved.toFixed(2)}</div>
                      <div className="text-xs text-gray-600">{reservation.uom}</div>
                    </td>
                    <td className="px-4 py-3 text-sm">
                      <div className="flex items-center gap-1 text-gray-700">
                        <Calendar size={14} />
                        {new Date(reservation.reserved_at).toLocaleDateString()}
                      </div>
                      <div className="text-xs text-gray-500">
                        {new Date(reservation.reserved_at).toLocaleTimeString()}
                      </div>
                    </td>
                    <td className="px-4 py-3 text-center">
                      <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-semibold border ${getStateColor(reservation.state)}`}>
                        {getStateIcon(reservation.state)}
                        {reservation.state}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-right">
                      {reservation.state === 'RESERVED' && (
                        <button
                          onClick={() => handleReleaseReservation(reservation.id, reservation.material_name)}
                          disabled={releaseMutation.isPending}
                          className="px-3 py-1 text-sm text-red-600 hover:bg-red-50 rounded transition-colors flex items-center gap-1 ml-auto disabled:opacity-50"
                        >
                          <Unlock size={14} />
                          Release
                        </button>
                      )}
                      {reservation.state === 'CONSUMED' && (
                        <span className="text-xs text-green-600 font-medium">Used</span>
                      )}
                      {reservation.state === 'RELEASED' && (
                        <span className="text-xs text-gray-500">Released</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Info Box */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 flex items-start gap-3">
        <Info className="text-blue-600 flex-shrink-0 mt-0.5" size={20} />
        <div className="text-sm text-blue-900">
          <p className="font-semibold mb-1">How Material Reservation Works:</p>
          <ul className="list-disc list-inside space-y-1 text-blue-800">
            <li><strong>Reserve:</strong> Soft allocation when WO is generated. Material marked as "reserved" but not yet consumed.</li>
            <li><strong>FIFO:</strong> System automatically selects oldest stock first for reservation.</li>
            <li><strong>Consume:</strong> When WO starts, reserved materials are hard-consumed and deducted from stock.</li>
            <li><strong>Release:</strong> If WO is cancelled, reservations can be released back to available stock.</li>
          </ul>
        </div>
      </div>
    </div>
  );
};
