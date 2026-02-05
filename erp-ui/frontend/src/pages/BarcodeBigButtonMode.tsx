/**
 * Big Button Mode - Barcode Scanner Workflow
 * Optimized for warehouse operations
 * Scan → Validate → Confirm workflow
 */

import React, { useState, useRef, useEffect } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import axios from 'axios';
import {
  BigButton,
  StatusCard,
  FullScreenLayout,
  LargeDisplay,
} from '../components/BigButtonMode';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

interface BarcodeData {
  product_id: number;
  product_name: string;
  quantity: number;
  barcode: string;
}

type WorkflowPhase = 'scan' | 'validate' | 'confirm' | 'success';

export default function BarcodeBigButtonMode() {
  const [phase, setPhase] = useState<WorkflowPhase>('scan');
  const [scannedBarcode, setScannedBarcode] = useState('');
  const [barcodeData, setBarcodeData] = useState<BarcodeData | null>(null);
  const [scannedCount, setScannedCount] = useState(0);
  const [totalExpected, setTotalExpected] = useState(0);
  const scanInputRef = useRef<HTMLInputElement>(null);
  const queryClient = useQueryClient();

  // Validate barcode
  const validateBarcodeMutation = useMutation({
    mutationFn: async (barcode: string) => {
      const token = localStorage.getItem('access_token');
      const response = await axios.post(
        `${API_BASE}/barcode/validate`,
        { barcode },
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );
      return response.data;
    },
    onSuccess: (data) => {
      setBarcodeData(data);
      setScannedCount(1);
      setPhase('validate');
    },
  });

  // Process received items
  const receiveItemsMutation = useMutation({
    mutationFn: async () => {
      const token = localStorage.getItem('access_token');
      return axios.post(
        `${API_BASE}/barcode/receive`,
        {
          barcode: scannedBarcode,
          quantity: scannedCount,
        },
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['inventory'] });
      setPhase('success');
    },
  });

  // Handle barcode scan
  const handleScan = async (barcode: string) => {
    if (barcode.trim()) {
      setScannedBarcode(barcode);
      validateBarcodeMutation.mutate(barcode);
    }
  };

  // Auto-focus on input when on scan phase
  useEffect(() => {
    if (phase === 'scan') {
      scanInputRef.current?.focus();
    }
  }, [phase]);

  // ==================== PHASE 1: SCAN BARCODE ====================
  if (phase === 'scan') {
    return (
      <FullScreenLayout title="SCAN BARCODE">
        <StatusCard
          status="ready"
          title="Ready to Scan"
          details={{
            'Status': 'Waiting for barcode...',
            'Items Received': scannedCount,
          }}
        />

        {/* Hidden input for barcode scanner */}
        <input
          ref={scanInputRef}
          type="text"
          value={scannedBarcode}
          onChange={(e) => setScannedBarcode(e.target.value)}
          onKeyPress={(e) => {
            if (e.key === 'Enter') {
              handleScan(scannedBarcode);
            }
          }}
          className="sr-only"
          autoFocus
        />

        <div className="bg-blue-50 border-4 border-blue-300 rounded-lg p-8 mb-8 text-center">
          <p className="text-3xl font-bold text-blue-700 mb-4">📱 SCANNER READY</p>
          <p className="text-2xl text-blue-600">
            Point scanner at barcode or type barcode:
          </p>
        </div>

        <div className="bg-white border-4 border-gray-300 rounded-lg p-6 text-center">
          <input
            type="text"
            value={scannedBarcode}
            onChange={(e) => setScannedBarcode(e.target.value)}
            onKeyPress={(e) => {
              if (e.key === 'Enter') {
                handleScan(scannedBarcode);
              }
            }}
            className="w-full text-3xl font-mono p-4 rounded border-2 border-gray-400 text-center"
            placeholder="Barcode will appear here..."
            autoFocus
          />
        </div>

        <div className="mt-8 space-y-4">
          <BigButton
            variant="primary"
            size="xlarge"
            onClick={() => handleScan(scannedBarcode)}
            disabled={!scannedBarcode || validateBarcodeMutation.isPending}
            icon="✓"
          >
            {validateBarcodeMutation.isPending ? '⏳ VALIDATING...' : 'SCAN'}
          </BigButton>

          {validateBarcodeMutation.isError && (
            <StatusCard status="error" title="Invalid Barcode">
              <p className="text-lg">The barcode could not be found. Try again.</p>
            </StatusCard>
          )}
        </div>
      </FullScreenLayout>
    );
  }

  // ==================== PHASE 2: VALIDATE ====================
  if (phase === 'validate' && barcodeData) {
    return (
      <FullScreenLayout title="VALIDATE ITEM" showBackButton onBack={() => setPhase('scan')}>
        <StatusCard
          status="ready"
          title="Item Details"
          details={{
            'Product': barcodeData.product_name,
            'Barcode': barcodeData.barcode,
            'Quantity': `${barcodeData.quantity} pieces`,
          }}
        />

        <div className="bg-yellow-50 border-4 border-yellow-300 rounded-lg p-6 mb-8">
          <p className="text-2xl font-bold text-yellow-700 text-center">
            ❓ Is this correct?
          </p>
        </div>

        <LargeDisplay label="Scanned" value={`${scannedCount}/${barcodeData.quantity}`} />

        <div className="space-y-4 mt-8">
          <BigButton
            variant="success"
            size="xlarge"
            onClick={() => setPhase('confirm')}
            icon="✓"
          >
            CONFIRM & RECEIVE
          </BigButton>

          <BigButton
            variant="danger"
            onClick={() => {
              setScannedBarcode('');
              setBarcodeData(null);
              setPhase('scan');
            }}
            icon="✗"
          >
            NOT CORRECT - SCAN AGAIN
          </BigButton>
        </div>
      </FullScreenLayout>
    );
  }

  // ==================== PHASE 3: CONFIRM ====================
  if (phase === 'confirm' && barcodeData) {
    return (
      <FullScreenLayout
        title="CONFIRM RECEIPT"
        showBackButton
        onBack={() => setPhase('validate')}
      >
        <StatusCard status="processing" title="Processing Receipt">
          <div className="space-y-4">
            <LargeDisplay label="Product" value={barcodeData.product_name} size="large" />
            <LargeDisplay label="Quantity" value={`${scannedCount} pieces`} size="large" />
          </div>
        </StatusCard>

        <p className="text-2xl text-center text-gray-700 mb-8">
          Ready to confirm receipt of this item?
        </p>

        <div className="space-y-4">
          <BigButton
            variant="success"
            size="xlarge"
            onClick={() => receiveItemsMutation.mutate()}
            disabled={receiveItemsMutation.isPending}
            icon="✓"
          >
            {receiveItemsMutation.isPending ? '⏳ CONFIRMING...' : 'CONFIRM RECEIPT'}
          </BigButton>

          <BigButton
            variant="secondary"
            onClick={() => setPhase('validate')}
            disabled={receiveItemsMutation.isPending}
          >
            BACK
          </BigButton>
        </div>
      </FullScreenLayout>
    );
  }

  // ==================== PHASE 4: SUCCESS ====================
  if (phase === 'success' && barcodeData) {
    return (
      <FullScreenLayout title="🎉 SUCCESS!">
        <StatusCard
          status="completed"
          title="Item Received"
          details={{
            'Product': barcodeData.product_name,
            'Quantity': `${scannedCount} pieces`,
            'Status': 'Added to inventory',
          }}
        />

        <p className="text-2xl text-center text-gray-700 mb-8">
          Great! Ready to scan the next item?
        </p>

        <div className="space-y-4">
          <BigButton
            variant="primary"
            size="xlarge"
            onClick={() => {
              setScannedBarcode('');
              setBarcodeData(null);
              setScannedCount(0);
              setPhase('scan');
            }}
            icon="🔄"
          >
            SCAN NEXT ITEM
          </BigButton>

          <BigButton
            variant="secondary"
            onClick={() => {
              // Navigate back to main warehouse view
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
