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

      {/* Create PO Modal - MULTI-ITEM SUPPORT */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-2xl font-bold text-gray-900">Create Purchase Order</h3>
                <span className="text-sm text-gray-500">📦 Multi-Item Support</span>
              </div>
              
              <form onSubmit={(e) => {
                e.preventDefault();
                const formData = new FormData(e.currentTarget);
                
                // Validate items
                const validItems = poItems.filter(item => 
                  item.product_id && item.quantity && item.unit_price
                );

                if (validItems.length === 0) {
                  alert('⚠️ Please add at least one product item!');
                  return;
                }

                const newPO = {
                  supplier_id: parseInt(formData.get('supplier_id') as string),
                  order_date: formData.get('order_date') as string,
                  expected_date: formData.get('expected_date') as string,
                  items: validItems.map(item => ({
                    product_id: parseInt(item.product_id),
                    quantity: parseFloat(item.quantity),
                    unit_price: parseFloat(item.unit_price)
                  })),
                  notes: formData.get('notes') as string
                };

                const token = localStorage.getItem('access_token');
                axios.post(`${API_BASE}/purchasing/purchase-orders`, newPO, {
                  headers: { Authorization: `Bearer ${token}` }
                })
                .then(() => {
                  queryClient.invalidateQueries({ queryKey: ['purchase-orders'] });
                  setShowCreateModal(false);
                  setPOItems([{ id: Date.now(), product_id: '', quantity: '', unit_price: '' }]);
                  alert(`✅ Purchase Order created!\n📦 ${validItems.length} items added`);
                })
                .catch(err => {
                  console.error('Failed to create PO:', err);
                  alert('❌ Failed: ' + (err.response?.data?.detail || err.message));
                });
              }}>
                <div className="space-y-4">
                  {/* Supplier */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Supplier ID <span className="text-red-500">*</span>
                    </label>
                    <input
                      type="number"
                      name="supplier_id"
                      required
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="Enter supplier ID"
                    />
                  </div>

                  {/* Dates */}
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Order Date <span className="text-red-500">*</span>
                      </label>
                      <input
                        type="date"
                        name="order_date"
                        required
                        defaultValue={format(new Date(), 'yyyy-MM-dd')}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Expected Date <span className="text-red-500">*</span>
                      </label>
                      <input
                        type="date"
                        name="expected_date"
                        required
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      />
                    </div>
                  </div>

                  {/* Multiple Items Section */}
                  <div className="border-t pt-4 mt-4">
                    <div className="flex items-center justify-between mb-4">
                      <h4 className="text-lg font-semibold text-gray-900">
                        📦 Product Items ({poItems.length})
                      </h4>
                      <button
                        type="button"
                        onClick={() => setPOItems([...poItems, { 
                          id: Date.now(), 
                          product_id: '', 
                          quantity: '', 
                          unit_price: '' 
                        }])}
                        className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition text-sm font-medium"
                      >
                        <Plus className="w-4 h-4" />
                        Add Item
                      </button>
                    </div>

                    <div className="space-y-3 max-h-96 overflow-y-auto">
                      {poItems.map((item, index) => (
                        <div key={item.id} className="bg-gray-50 p-4 rounded-lg border border-gray-200">
                          <div className="flex items-start gap-3">
                            <span className="flex-shrink-0 w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center font-bold text-sm">
                              {index + 1}
                            </span>
                            
                            <div className="flex-1 grid grid-cols-1 md:grid-cols-3 gap-3">
                              <div>
                                <label className="block text-xs font-medium text-gray-600 mb-1">
                                  Product ID <span className="text-red-500">*</span>
                                </label>
                                <input
                                  type="number"
                                  value={item.product_id}
                                  onChange={(e) => {
                                    const newItems = [...poItems];
                                    newItems[index].product_id = e.target.value;
                                    setPOItems(newItems);
                                  }}
                                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
                                  placeholder="ID"
                                />
                              </div>
                              
                              <div>
                                <label className="block text-xs font-medium text-gray-600 mb-1">
                                  Quantity <span className="text-red-500">*</span>
                                </label>
                                <input
                                  type="number"
                                  value={item.quantity}
                                  onChange={(e) => {
                                    const newItems = [...poItems];
                                    newItems[index].quantity = e.target.value;
                                    setPOItems(newItems);
                                  }}
                                  step="0.01"
                                  min="0"
                                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
                                  placeholder="0"
                                />
                              </div>
                              
                              <div>
                                <label className="block text-xs font-medium text-gray-600 mb-1">
                                  Unit Price (IDR) <span className="text-red-500">*</span>
                                </label>
                                <input
                                  type="number"
                                  value={item.unit_price}
                                  onChange={(e) => {
                                    const newItems = [...poItems];
                                    newItems[index].unit_price = e.target.value;
                                    setPOItems(newItems);
                                  }}
                                  step="0.01"
                                  min="0"
                                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
                                  placeholder="0"
                                />
                              </div>
                            </div>

                            {poItems.length > 1 && (
                              <button
                                type="button"
                                onClick={() => setPOItems(poItems.filter((_, i) => i !== index))}
                                className="flex-shrink-0 p-2 text-red-600 hover:bg-red-50 rounded-lg transition"
                                title="Remove item"
                              >
                                <Trash2 className="w-5 h-5" />
                              </button>
                            )}
                          </div>

                          {/* Subtotal */}
                          {item.quantity && item.unit_price && (
                            <div className="mt-2 text-right text-sm font-medium text-blue-600">
                              Subtotal: {formatCurrency(parseFloat(item.quantity) * parseFloat(item.unit_price))}
                            </div>
                          )}
                        </div>
                      ))}
                    </div>

                    {/* Total Amount */}
                    <div className="mt-4 bg-blue-50 p-4 rounded-lg border-2 border-blue-200">
                      <div className="flex justify-between items-center">
                        <span className="text-lg font-semibold text-gray-700">Total Amount:</span>
                        <span className="text-2xl font-bold text-blue-600">
                          {formatCurrency(
                            poItems.reduce((sum, item) => {
                              const qty = parseFloat(item.quantity) || 0;
                              const price = parseFloat(item.unit_price) || 0;
                              return sum + (qty * price);
                            }, 0)
                          )}
                        </span>
                      </div>
                    </div>
                  </div>

                  {/* Notes */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Notes
                    </label>
                    <textarea
                      name="notes"
                      rows={2}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="Add any additional notes..."
                    />
                  </div>
                </div>

                {/* Actions */}
                <div className="flex gap-3 mt-6 pt-6 border-t">
                  <button
                    type="button"
                    onClick={() => {
                      setShowCreateModal(false);
                      setPOItems([{ id: Date.now(), product_id: '', quantity: '', unit_price: '' }]);
                    }}
                    className="flex-1 px-6 py-3 border border-gray-300 rounded-lg hover:bg-gray-50 transition font-medium"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="flex-1 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition font-medium"
                  >
                    Create Purchase Order ({poItems.filter(i => i.product_id && i.quantity && i.unit_price).length} items)
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
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
