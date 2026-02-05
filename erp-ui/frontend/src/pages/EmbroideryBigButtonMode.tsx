/**
 * Big Button Mode - Embroidery Workflow
 * Optimized for factory floor operators
 * Single large button per action, clear status displays
 */

import React, { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import axios from 'axios';
import {
  BigButton,
  StatusCard,
  FullScreenLayout,
  LargeDisplay,
} from '../components/BigButtonMode';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

interface WorkOrder {
  id: number;
  mo_id: number;
  status: string;
  input_qty: number;
  output_qty: number;
  reject_qty: number;
  start_time: string | null;
  end_time: string | null;
}

type WorkflowPhase = 'select' | 'ready' | 'working' | 'complete' | 'transfer';

export default function EmbroideryBigButtonMode() {
  const [phase, setPhase] = useState<WorkflowPhase>('select');
  const [selectedWO, setSelectedWO] = useState<WorkOrder | null>(null);
  const [embroideredQty, setEmbroideredQty] = useState(0);
  const queryClient = useQueryClient();

  // Fetch active work orders
  const { data: workOrders = [], isLoading } = useQuery({
    queryKey: ['embroidery-work-orders'],
    queryFn: async () => {
      const token = localStorage.getItem('access_token');
      const response = await axios.get(`${API_BASE}/embroidery/work-orders`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      return response.data || [];
    },
    refetchInterval: 3000,
  });

  // Start work order
  const startWOMutation = useMutation({
    mutationFn: async (woId: number) => {
      const token = localStorage.getItem('access_token');
      return axios.post(`${API_BASE}/embroidery/work-order/${woId}/start`, {}, {
        headers: { Authorization: `Bearer ${token}` },
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['embroidery-work-orders'] });
      setPhase('working');
    },
  });

  // Record output
  const recordOutputMutation = useMutation({
    mutationFn: async () => {
      if (!selectedWO) throw new Error('No work order selected');
      const token = localStorage.getItem('access_token');
      return axios.post(
        `${API_BASE}/embroidery/work-order/${selectedWO.id}/record-output`,
        {
          output_qty: embroideredQty,
          reject_qty: 0,
        },
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['embroidery-work-orders'] });
      setPhase('complete');
    },
  });

  // Complete work order
  const completeWOMutation = useMutation({
    mutationFn: async () => {
      if (!selectedWO) throw new Error('No work order selected');
      const token = localStorage.getItem('access_token');
      return axios.post(`${API_BASE}/embroidery/work-order/${selectedWO.id}/complete`, {}, {
        headers: { Authorization: `Bearer ${token}` },
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['embroidery-work-orders'] });
      setPhase('transfer');
    },
  });

  // Transfer to next station
  const transferMutation = useMutation({
    mutationFn: async () => {
      if (!selectedWO) throw new Error('No work order selected');
      const token = localStorage.getItem('access_token');
      return axios.post(
        `${API_BASE}/embroidery/work-order/${selectedWO.id}/transfer`,
        { destination: 'packing' },
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['embroidery-work-orders'] });
      // Reset to select phase for next work order
      setSelectedWO(null);
      setEmbroideredQty(0);
      setPhase('select');
    },
  });

  // ==================== PHASE 1: SELECT WORK ORDER ====================
  if (phase === 'select') {
    return (
      <FullScreenLayout title="EMBROIDERY - SELECT WORK ORDER">
        {isLoading ? (
          <StatusCard status="processing" title="Loading Work Orders...">
            <p className="text-xl">Please wait...</p>
          </StatusCard>
        ) : workOrders.length === 0 ? (
          <StatusCard status="warning" title="No Work Orders Available">
            <p className="text-xl">Please check back soon or contact your supervisor.</p>
          </StatusCard>
        ) : (
          <div className="space-y-4">
            {workOrders.map((wo: WorkOrder) => (
              <button
                key={wo.id}
                onClick={() => {
                  setSelectedWO(wo);
                  setPhase('ready');
                }}
                className="w-full p-6 bg-white border-4 border-gray-300 rounded-lg hover:border-blue-500 hover:shadow-lg transition-all duration-200"
              >
                <div className="flex justify-between items-center">
                  <div className="text-left">
                    <p className="text-2xl font-bold text-gray-900">MO-{wo.mo_id}</p>
                    <p className="text-lg text-gray-600">Qty: {wo.input_qty}</p>
                  </div>
                  <span className="text-4xl">→</span>
                </div>
              </button>
            ))}
          </div>
        )}
      </FullScreenLayout>
    );
  }

  // ==================== PHASE 2: READY TO START ====================
  if (phase === 'ready' && selectedWO) {
    return (
      <FullScreenLayout title="READY TO START?" showBackButton onBack={() => setPhase('select')}>
        <StatusCard
          status="ready"
          title="Work Order Ready"
          details={{
            'Work Order': `MO-${selectedWO.mo_id}`,
            'Quantity': `${selectedWO.input_qty} pieces`,
            'Status': 'Ready to start',
          }}
        />

        <div className="space-y-4">
          <BigButton
            variant="success"
            size="xlarge"
            onClick={() => startWOMutation.mutate(selectedWO.id)}
            disabled={startWOMutation.isPending}
            icon=""
          >
            {startWOMutation.isPending ? '[LOADING] STARTING...' : 'START EMBROIDERY'}
          </BigButton>

          <BigButton
            variant="secondary"
            onClick={() => setPhase('select')}
            disabled={startWOMutation.isPending}
            icon="←"
          >
            SELECT DIFFERENT WO
          </BigButton>
        </div>
      </FullScreenLayout>
    );
  }

  // ==================== PHASE 3: WORKING ====================
  if (phase === 'working' && selectedWO) {
    return (
      <FullScreenLayout title="EMBROIDERY IN PROGRESS">
        <StatusCard
          status="processing"
          title="Currently Processing"
          details={{
            'Work Order': `MO-${selectedWO.mo_id}`,
            'Total Qty': `${selectedWO.input_qty} pieces`,
            'Time': 'Estimated 15 minutes',
          }}
        />

        <p className="text-2xl text-center font-semibold text-gray-700 mb-8">
          Please continue embroidering...
        </p>

        <div className="bg-blue-50 border-4 border-blue-300 rounded-lg p-6 mb-8">
          <p className="text-2xl font-bold text-blue-700 text-center">
            Press DONE when all pieces are complete
          </p>
        </div>

        <BigButton
          variant="success"
          size="xlarge"
          onClick={() => setPhase('complete')}
          icon=""
        >
          DONE - RECORD OUTPUT
        </BigButton>
      </FullScreenLayout>
    );
  }

  // ==================== PHASE 4: RECORD OUTPUT ====================
  if (phase === 'complete' && selectedWO) {
    return (
      <FullScreenLayout
        title="RECORD OUTPUT"
        showBackButton
        onBack={() => setPhase('working')}
      >
        <StatusCard
          status="ready"
          title="How many pieces completed?"
          details={{
            'Work Order': `MO-${selectedWO.mo_id}`,
            'Target Qty': `${selectedWO.input_qty} pieces`,
          }}
        />

        <div className="bg-white border-4 border-gray-300 rounded-lg p-8 text-center mb-8">
          <LargeDisplay
            label="Pieces Completed"
            value={embroideredQty}
            size="xlarge"
          />
        </div>

        <div className="grid grid-cols-2 gap-4 mb-8">
          {[5, 10, 25, 50].map((qty) => (
            <BigButton
              key={qty}
              variant="secondary"
              onClick={() => setEmbroideredQty(embroideredQty + qty)}
              disabled={embroideredQty + qty > selectedWO.input_qty}
            >
              +{qty}
            </BigButton>
          ))}
        </div>

        <div className="space-y-4">
          <BigButton
            variant="success"
            size="xlarge"
            onClick={() => recordOutputMutation.mutate()}
            disabled={embroideredQty === 0 || recordOutputMutation.isPending}
            icon=""
          >
            {recordOutputMutation.isPending ? 'SAVING...' : 'CONFIRM OUTPUT'}
          </BigButton>

          <BigButton
            variant="secondary"
            onClick={() => setPhase('working')}
            disabled={recordOutputMutation.isPending}
          >
            BACK
          </BigButton>
        </div>
      </FullScreenLayout>
    );
  }

  // ==================== PHASE 5: COMPLETE ====================
  if (phase === 'complete' && selectedWO) {
    return (
      <FullScreenLayout title="WORK ORDER COMPLETED">
        <StatusCard
          status="completed"
          title="Complete!"
          details={{
            'Work Order': `MO-${selectedWO.mo_id}`,
            'Output': `${embroideredQty} pieces`,
            'Status': 'Ready to transfer',
          }}
        />

        <p className="text-2xl text-center text-gray-700 mb-8">
          Excellent work! Ready to transfer to next station?
        </p>

        <div className="space-y-4">
          <BigButton
            variant="success"
            size="xlarge"
            onClick={() => transferMutation.mutate()}
            disabled={transferMutation.isPending}
            icon="→"
          >
            {transferMutation.isPending ? 'TRANSFERRING...' : 'TRANSFER TO PACKING'}
          </BigButton>

          <BigButton
            variant="secondary"
            onClick={() => setPhase('working')}
            disabled={transferMutation.isPending}
          >
            BACK
          </BigButton>
        </div>
      </FullScreenLayout>
    );
  }

  // ==================== PHASE 6: TRANSFER ====================
  if (phase === 'transfer' && selectedWO) {
    return (
      <FullScreenLayout title="[Success] SUCCESS!">
        <StatusCard
          status="completed"
          title="Transferred Successfully"
          details={{
            'Work Order': `MO-${selectedWO.mo_id}`,
            'Output': `${embroideredQty} pieces`,
            'Status': 'Sent to packing station',
          }}
        />

        <p className="text-2xl text-center text-gray-700 mb-8">
          Great job! Ready to start the next work order?
        </p>

        <BigButton
          variant="primary"
          size="xlarge"
          onClick={() => setPhase('select')}
          icon="[Refresh]"
        >
          START NEXT WORK ORDER
        </BigButton>
      </FullScreenLayout>
    );
  }

  return null;
}
