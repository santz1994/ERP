/**
 * Big Button Mode - Warehouse Workflow
 * Optimized for warehouse operations
 * Pick → Pack → Ship workflow
 */

import React, { useState } from 'react';
import { useMutation, useQueryClient, useQuery } from '@tanstack/react-query';
import axios from 'axios';
import {
  BigButton,
  StatusCard,
  FullScreenLayout,
  LargeDisplay,
} from '../components/BigButtonMode';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

interface TransferOrder {
  id: number;
  reference: string;
  source_location: string;
  destination_location: string;
  product_id: number;
  product_name: string;
  quantity: number;
  status: string;
}

type WorkflowPhase = 'select' | 'pick' | 'pack' | 'ship' | 'success';

export default function WarehouseBigButtonMode() {
  const [phase, setPhase] = useState<WorkflowPhase>('select');
  const [selectedTransfer, setSelectedTransfer] = useState<TransferOrder | null>(null);
  const [pickedQty, setPickedQty] = useState(0);
  const [packedQty, setPackedQty] = useState(0);
  const queryClient = useQueryClient();

  // Fetch pending transfers
  const { data: pendingTransfers = [], isLoading } = useQuery({
    queryKey: ['warehouse-transfers'],
    queryFn: async () => {
      const token = localStorage.getItem('access_token');
      const response = await axios.get(`${API_BASE}/warehouse/stock/pending`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      return response.data || [];
    },
    refetchInterval: 3000,
  });

  // Transfer stock
  const transferMutation = useMutation({
    mutationFn: async () => {
      if (!selectedTransfer) throw new Error('No transfer selected');
      const token = localStorage.getItem('access_token');
      return axios.post(
        `${API_BASE}/warehouse/transfer`,
        {
          product_id: selectedTransfer.product_id,
          source: selectedTransfer.source_location,
          destination: selectedTransfer.destination_location,
          quantity: selectedTransfer.quantity,
        },
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['warehouse-transfers'] });
      setPhase('pack');
    },
  });

  // Accept transfer
  const acceptTransferMutation = useMutation({
    mutationFn: async () => {
      if (!selectedTransfer) throw new Error('No transfer selected');
      const token = localStorage.getItem('access_token');
      return axios.post(
        `${API_BASE}/warehouse/transfer/${selectedTransfer.id}/accept`,
        {},
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['warehouse-transfers'] });
      setPhase('success');
    },
  });

  // ==================== PHASE 1: SELECT TRANSFER ====================
  if (phase === 'select') {
    return (
      <FullScreenLayout title="WAREHOUSE - SELECT TRANSFER">
        {isLoading ? (
          <StatusCard status="processing" title="Loading Transfers...">
            <p className="text-xl">Please wait...</p>
          </StatusCard>
        ) : pendingTransfers.length === 0 ? (
          <StatusCard status="warning" title="No Transfers Pending">
            <p className="text-xl">All transfers are up to date. Check back soon!</p>
          </StatusCard>
        ) : (
          <div className="space-y-4">
            {pendingTransfers.map((transfer: TransferOrder) => (
              <button
                key={transfer.id}
                onClick={() => {
                  setSelectedTransfer(transfer);
                  setPickedQty(0);
                  setPackedQty(0);
                  setPhase('pick');
                }}
                className="w-full p-6 bg-white border-4 border-gray-300 rounded-lg hover:border-blue-500 hover:shadow-lg transition-all duration-200"
              >
                <div className="flex justify-between items-start">
                  <div className="text-left">
                    <p className="text-2xl font-bold text-gray-900">{transfer.product_name}</p>
                    <p className="text-lg text-gray-600">
                      {transfer.source_location} → {transfer.destination_location}
                    </p>
                    <p className="text-lg text-gray-600">Qty: {transfer.quantity} pieces</p>
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

  // ==================== PHASE 2: PICK ====================
  if (phase === 'pick' && selectedTransfer) {
    return (
      <FullScreenLayout title="[Location] PICK ITEMS" showBackButton onBack={() => setPhase('select')}>
        <StatusCard
          status="processing"
          title="Picking Items"
          details={{
            'Product': selectedTransfer.product_name,
            'Location': selectedTransfer.source_location,
            'Target Qty': `${selectedTransfer.quantity} pieces`,
          }}
        />

        <div className="bg-white border-4 border-gray-300 rounded-lg p-8 text-center mb-8">
          <LargeDisplay label="Picked So Far" value={`${pickedQty}/${selectedTransfer.quantity}`} size="xlarge" />
        </div>

        <p className="text-2xl text-center text-gray-700 mb-8">
          How many items have you picked?
        </p>

        <div className="grid grid-cols-2 gap-4 mb-8">
          {[5, 10, 25, 50].map((qty) => (
            <BigButton
              key={qty}
              variant="secondary"
              onClick={() =>
                setPickedQty(Math.min(pickedQty + qty, selectedTransfer.quantity))
              }
              disabled={pickedQty >= selectedTransfer.quantity}
            >
              +{qty}
            </BigButton>
          ))}
        </div>

        <div className="space-y-4">
          <BigButton
            variant="success"
            size="xlarge"
            onClick={() => setPhase('pack')}
            disabled={pickedQty !== selectedTransfer.quantity}
            icon=""
          >
            {pickedQty === selectedTransfer.quantity
              ? 'ALL PICKED - NEXT STEP'
              : `PICK ${selectedTransfer.quantity - pickedQty} MORE`}
          </BigButton>

          <BigButton
            variant="secondary"
            onClick={() => setPhase('select')}
          >
            CANCEL
          </BigButton>
        </div>
      </FullScreenLayout>
    );
  }

  // ==================== PHASE 3: PACK ====================
  if (phase === 'pack' && selectedTransfer) {
    return (
      <FullScreenLayout title="PACK ITEMS" showBackButton onBack={() => setPhase('pick')}>
        <StatusCard
          status="processing"
          title="Packing Items"
          details={{
            'Product': selectedTransfer.product_name,
            'Picked': `${pickedQty} pieces`,
            'Target Qty': `${selectedTransfer.quantity} pieces`,
          }}
        />

        <div className="bg-white border-4 border-gray-300 rounded-lg p-8 text-center mb-8">
          <LargeDisplay label="Packed So Far" value={`${packedQty}/${selectedTransfer.quantity}`} size="xlarge" />
        </div>

        <p className="text-2xl text-center text-gray-700 mb-8">
          How many items have you packed?
        </p>

        <div className="grid grid-cols-2 gap-4 mb-8">
          {[5, 10, 25, 50].map((qty) => (
            <BigButton
              key={qty}
              variant="secondary"
              onClick={() =>
                setPackedQty(Math.min(packedQty + qty, selectedTransfer.quantity))
              }
              disabled={packedQty >= selectedTransfer.quantity}
            >
              +{qty}
            </BigButton>
          ))}
        </div>

        <div className="space-y-4">
          <BigButton
            variant="success"
            size="xlarge"
            onClick={() => setPhase('ship')}
            disabled={packedQty !== selectedTransfer.quantity}
            icon=""
          >
            {packedQty === selectedTransfer.quantity
              ? 'ALL PACKED - SHIP IT'
              : `PACK ${selectedTransfer.quantity - packedQty} MORE`}
          </BigButton>

          <BigButton
            variant="secondary"
            onClick={() => setPhase('pick')}
          >
            BACK
          </BigButton>
        </div>
      </FullScreenLayout>
    );
  }

  // ==================== PHASE 4: SHIP ====================
  if (phase === 'ship' && selectedTransfer) {
    return (
      <FullScreenLayout title="READY TO SHIP" showBackButton onBack={() => setPhase('pack')}>
        <StatusCard
          status="ready"
          title="Ready for Shipment"
          details={{
            'Product': selectedTransfer.product_name,
            'Quantity': `${selectedTransfer.quantity} pieces`,
            'Destination': selectedTransfer.destination_location,
            'Status': 'Ready to ship',
          }}
        />

        <p className="text-2xl text-center text-gray-700 mb-8">
          Confirm shipment to next location?
        </p>

        <div className="space-y-4">
          <BigButton
            variant="success"
            size="xlarge"
            onClick={() => transferMutation.mutate()}
            disabled={transferMutation.isPending}
            icon=""
          >
            {transferMutation.isPending ? '[LOADING] PROCESSING...' : 'CONFIRM SHIPMENT'}
          </BigButton>

          <BigButton
            variant="secondary"
            onClick={() => setPhase('pack')}
            disabled={transferMutation.isPending}
          >
            BACK
          </BigButton>
        </div>
      </FullScreenLayout>
    );
  }

  // ==================== PHASE 5: SUCCESS ====================
  if (phase === 'success' && selectedTransfer) {
    return (
      <FullScreenLayout title="[Success] SUCCESS!">
        <StatusCard
          status="completed"
          title="Transfer Complete"
          details={{
            'Product': selectedTransfer.product_name,
            'Quantity': `${selectedTransfer.quantity} pieces`,
            'From': selectedTransfer.source_location,
            'To': selectedTransfer.destination_location,
            'Status': 'Shipment confirmed',
          }}
        />

        <p className="text-2xl text-center text-gray-700 mb-8">
          Excellent work! Ready to process the next transfer?
        </p>

        <div className="space-y-4">
          <BigButton
            variant="primary"
            size="xlarge"
            onClick={() => {
              setSelectedTransfer(null);
              setPickedQty(0);
              setPackedQty(0);
              setPhase('select');
            }}
            icon="[Refresh]"
          >
            NEXT TRANSFER
          </BigButton>

          <BigButton
            variant="secondary"
            onClick={() => {
              window.location.href = '/warehouse';
            }}
          >
            BACK TO WAREHOUSE
          </BigButton>
        </div>
      </FullScreenLayout>
    );
  }

  return null;
}
