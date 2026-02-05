/**
 * Copyright (c) 2026 PT Quty Karunia / Daniel Rizaldy - All Rights Reserved
 * File: PurchasingPage.tsx | Author: Daniel Rizaldy | Date: 2026-01-19
 */

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { format } from 'date-fns';
import { 
  ShoppingCart, 
  CheckCircle, 
  Clock, 
  XCircle,
  PackageCheck,
  TrendingUp,
  FileText,
  Plus,
  Trash2
} from 'lucide-react';
import axios from 'axios';
import { PurchaseOrderCreate } from '@/components/purchasing/PurchaseOrderCreate';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

interface PurchaseOrder {
  id: number;
  po_number: string;
  supplier_id: number;
  order_date: string;
  expected_date: string;
  status: string;
  total_amount: number;
  currency: string;
  metadata?: {
    items?: Array<{
      product_id: number;
      quantity: number;
      unit_price: number;
    }>;
  };
}

export default function PurchasingPage() {
  const [selectedPO, setSelectedPO] = useState<PurchaseOrder | null>(null);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showReceiveModal, setShowReceiveModal] = useState(false);
  const [poItems, setPOItems] = useState([{
    id: Date.now(),
    product_id: '',
    quantity: '',
    unit_price: ''
  }]);
  const queryClient = useQueryClient();

  // Fetch purchase orders
  const { data: purchaseOrders, isLoading } = useQuery({
    queryKey: ['purchase-orders'],
    queryFn: async () => {
      const token = localStorage.getItem('access_token');
      const response = await axios.get(`${API_BASE}/purchasing/purchase-orders`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      return response.data;
    },
    refetchInterval: 5000
  });

  // Approve PO mutation
  const approvePO = useMutation({
    mutationFn: async (poId: number) => {
      const token = localStorage.getItem('access_token');
      return axios.post(`${API_BASE}/purchasing/purchase-order/${poId}/approve`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['purchase-orders'] });
    }
  });

  // Receive PO mutation
  const receivePO = useMutation({
    mutationFn: async (data: { poId: number; received_items: any[] }) => {
      const token = localStorage.getItem('access_token');
      return axios.post(
        `${API_BASE}/purchasing/purchase-order/${data.poId}/receive`,
        { received_items: data.received_items, location_id: 1 },
        { headers: { Authorization: `Bearer ${token}` } }
      );
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['purchase-orders'] });
      setShowReceiveModal(false);
      setSelectedPO(null);
    }
  });

  // Cancel PO mutation
  const cancelPO = useMutation({
    mutationFn: async (data: { poId: number; reason: string }) => {
      const token = localStorage.getItem('access_token');
      return axios.post(
        `${API_BASE}/purchasing/purchase-order/${data.poId}/cancel`,
        { reason: data.reason },
        { headers: { Authorization: `Bearer ${token}` } }
      );
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['purchase-orders'] });
    }
  });

  const getStatusBadge = (status: string) => {
    const badges: Record<string, { color: string; icon: any }> = {
      'Draft': { color: 'bg-gray-100 text-gray-800', icon: FileText },
      'Sent': { color: 'bg-blue-100 text-blue-800', icon: Clock },
      'Received': { color: 'bg-green-100 text-green-800', icon: PackageCheck },
      'Done': { color: 'bg-purple-100 text-purple-800', icon: CheckCircle },
      'Cancelled': { color: 'bg-red-100 text-red-800', icon: XCircle },
    };
    const badge = badges[status] || badges['Draft'];
    const Icon = badge.icon;
    return (
      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${badge.color}`}>
        <Icon className="w-3 h-3 mr-1" />
        {status}
      </span>
    );
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('id-ID', {
      style: 'currency',
      currency: 'IDR',
      minimumFractionDigits: 0
    }).format(amount);
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
              <ShoppingCart className="w-8 h-8 mr-3 text-blue-600" />
              Purchasing Department
            </h1>
            <p className="text-gray-500 mt-1">
              {format(new Date(), 'EEEE, dd MMMM yyyy • HH:mm')} WIB
            </p>
          </div>
          <button
            onClick={() => setShowCreateModal(true)}
            className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition flex items-center shadow-lg"
          >
            <ShoppingCart className="w-5 h-5 mr-2" />
            Create Purchase Order
          </button>
        </div>
      </div>

      {/* Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500 mb-1">Total POs</p>
              <p className="text-2xl font-bold text-gray-900">{purchaseOrders?.length || 0}</p>
            </div>
            <FileText className="w-10 h-10 text-gray-400" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500 mb-1">Pending Approval</p>
              <p className="text-2xl font-bold text-blue-600">
                {purchaseOrders?.filter((po: PurchaseOrder) => po.status === 'Draft').length || 0}
              </p>
            </div>
            <Clock className="w-10 h-10 text-blue-400" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500 mb-1">In Transit</p>
              <p className="text-2xl font-bold text-orange-600">
                {purchaseOrders?.filter((po: PurchaseOrder) => po.status === 'Sent').length || 0}
              </p>
            </div>
            <PackageCheck className="w-10 h-10 text-orange-400" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500 mb-1">Received</p>
              <p className="text-2xl font-bold text-green-600">
                {purchaseOrders?.filter((po: PurchaseOrder) => po.status === 'Received').length || 0}
              </p>
            </div>
            <CheckCircle className="w-10 h-10 text-green-400" />
          </div>
        </div>
      </div>

      {/* Purchase Orders Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
        {purchaseOrders?.map((po: PurchaseOrder) => (
          <div key={po.id} className="bg-white rounded-lg shadow-lg overflow-hidden hover:shadow-xl transition-shadow">
            {/* Card Header */}
            <div className="bg-gradient-to-r from-blue-600 to-blue-700 p-4 text-white">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-lg font-semibold">{po.po_number}</h3>
                  <p className="text-sm opacity-90">Supplier ID: {po.supplier_id}</p>
                </div>
                {getStatusBadge(po.status)}
              </div>
            </div>

            {/* Card Body */}
            <div className="p-4 space-y-4">
              {/* Dates */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-xs text-gray-500 mb-1">Order Date</p>
                  <p className="text-sm font-medium">{format(new Date(po.order_date), 'dd MMM yyyy')}</p>
                </div>
                <div>
                  <p className="text-xs text-gray-500 mb-1">Expected Date</p>
                  <p className="text-sm font-medium">{format(new Date(po.expected_date), 'dd MMM yyyy')}</p>
                </div>
              </div>

              {/* Amount */}
              <div className="bg-blue-50 p-3 rounded">
                <p className="text-xs text-gray-600 mb-1">Total Amount</p>
                <p className="text-xl font-bold text-blue-600">{formatCurrency(po.total_amount)}</p>
              </div>

              {/* Items Count */}
              {po.metadata?.items && (
                <div className="text-sm text-gray-600">
                  <TrendingUp className="w-4 h-4 inline mr-1" />
                  {po.metadata.items.length} items in this PO
                </div>
              )}

              {/* Actions */}
              <div className="flex gap-2">
                {po.status === 'Draft' && (
                  <button
                    onClick={() => approvePO.mutate(po.id)}
                    disabled={approvePO.isPending}
                    className="flex-1 bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 transition disabled:opacity-50 text-sm font-medium"
                  >
                    Approve
                  </button>
                )}

                {po.status === 'Sent' && (
                  <button
                    onClick={() => {
                      setSelectedPO(po);
                      setShowReceiveModal(true);
                    }}
                    className="flex-1 bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 transition text-sm font-medium"
                  >
                    Receive Materials
                  </button>
                )}

                {(po.status === 'Draft' || po.status === 'Sent') && (
                  <button
                    onClick={() => {
                      const reason = prompt('Reason for cancellation:');
                      if (reason) {
                        cancelPO.mutate({ poId: po.id, reason });
                      }
                    }}
                    disabled={cancelPO.isPending}
                    className="flex-1 bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700 transition disabled:opacity-50 text-sm font-medium"
                  >
                    Cancel
                  </button>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Empty State */}
      {purchaseOrders?.length === 0 && (
        <div className="text-center py-12">
          <ShoppingCart className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No Purchase Orders</h3>
          <p className="text-gray-500 mb-4">Create your first purchase order to get started.</p>
          <button
            onClick={() => setShowCreateModal(true)}
            className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition"
          >
            Create Purchase Order
          </button>
        </div>
      )}

      {/* Create PO Modal - DUAL-MODE SYSTEM (AUTO-BOM + MANUAL) */}
      {showCreateModal && (
        <PurchaseOrderCreate
          onClose={() => setShowCreateModal(false)}
          onSuccess={() => {
            queryClient.invalidateQueries({ queryKey: ['purchase-orders'] });
          }}
        />
      )}

      {/* Receive Materials Modal */}
      {showReceiveModal && selectedPO && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4">
            <div className="p-6">
              <h3 className="text-xl font-bold mb-4">Receive Materials - {selectedPO.po_number}</h3>
              <p className="text-gray-600 mb-4">
                Confirm material receipt for PO {selectedPO.po_number}. 
                This will update inventory and create stock lots for traceability.
              </p>

              <div className="flex gap-3 mt-6">
                <button
                  onClick={() => {
                    setShowReceiveModal(false);
                    setSelectedPO(null);
                  }}
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-50 transition"
                >
                  Cancel
                </button>
                <button
                  onClick={() => {
                    if (selectedPO.metadata?.items) {
                      const receivedItems = selectedPO.metadata.items.map(item => ({
                        product_id: item.product_id,
                        quantity: item.quantity,
                        lot_number: `LOT-${selectedPO.po_number}-${item.product_id}`
                      }));
                      receivePO.mutate({ poId: selectedPO.id, received_items: receivedItems });
                    }
                  }}
                  disabled={receivePO.isPending}
                  className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition disabled:opacity-50"
                >
                  {receivePO.isPending ? 'Receiving...' : 'Confirm Receipt'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
