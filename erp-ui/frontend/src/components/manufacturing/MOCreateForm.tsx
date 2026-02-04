/**
 * MO Create Form Component - Enhanced for Dual Trigger System
 * Priority 1.2: PPIC Dashboard Enhancement
 * Created: 2026-02-04
 */

import React, { useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/api/client';
import { X, AlertCircle, CheckCircle, Package, Calendar, Target } from 'lucide-react';

interface Product {
  id: number;
  code: string;
  name: string;
  type: string;
  uom: string;
  bom_id?: number;
}

interface MOCreateFormProps {
  onClose: () => void;
  onSuccess?: () => void;
}

export const MOCreateForm: React.FC<MOCreateFormProps> = ({ onClose, onSuccess }) => {
  const queryClient = useQueryClient();
  
  const [formData, setFormData] = useState({
    product_id: '',
    qty_planned: '',
    routing_type: 'STANDARD',
    batch_number: '',
    so_line_id: '',
    production_week: '',
    destination_country: '',
    po_fabric_id: '',
    po_label_id: '',
    planned_production_date: '',
    target_shipment_date: ''
  });

  const [triggerMode, setTriggerMode] = useState<'PARTIAL' | 'RELEASED'>('PARTIAL');

  // Fetch available products (WIP and Finish Good)
  const { data: products, isLoading: productsLoading } = useQuery({
    queryKey: ['products-for-mo'],
    queryFn: async () => {
      const response = await apiClient.get('/admin/products');
      return response.data.filter((p: Product) => 
        p.type === 'WIP' || p.type === 'Finish Good'
      );
    }
  });

  // Fetch PO Fabric list
  const { data: poFabrics } = useQuery({
    queryKey: ['po-fabrics'],
    queryFn: async () => {
      const response = await apiClient.get('/purchasing/po?type=fabric');
      return response.data;
    }
  });

  // Fetch PO Label list
  const { data: poLabels } = useQuery({
    queryKey: ['po-labels'],
    queryFn: async () => {
      const response = await apiClient.get('/purchasing/po?type=label');
      return response.data;
    }
  });

  // Create MO Mutation
  const createMOMutation = useMutation({
    mutationFn: async (data: any) => {
      const response = await apiClient.post('/ppic/manufacturing-order', {
        ...data,
        trigger_mode: triggerMode,
        qty_planned: parseFloat(data.qty_planned)
      });
      return response.data;
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['manufacturing-orders'] });
      alert(`✅ Manufacturing Order ${data.id} created successfully!\n🔥 Mode: ${triggerMode}\n📦 Product: ${data.product_name}\n🎯 Qty: ${data.qty_planned} pcs`);
      onSuccess?.();
      onClose();
    },
    onError: (error: any) => {
      const message = error.response?.data?.detail || error.message;
      alert(`❌ Failed to create MO: ${message}`);
    }
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    // Validation
    if (!formData.product_id || !formData.qty_planned) {
      alert('⚠️ Product and Quantity are required!');
      return;
    }

    if (triggerMode === 'PARTIAL' && !formData.po_fabric_id) {
      alert('⚠️ PARTIAL mode requires PO Fabric!');
      return;
    }

    if (triggerMode === 'RELEASED' && (!formData.po_fabric_id || !formData.po_label_id)) {
      alert('⚠️ RELEASED mode requires both PO Fabric and PO Label!');
      return;
    }

    createMOMutation.mutate(formData);
  };

  const handleChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="sticky top-0 bg-blue-600 text-white px-6 py-4 flex items-center justify-between rounded-t-lg">
          <div className="flex items-center gap-3">
            <Package size={24} />
            <h2 className="text-xl font-bold">Create Manufacturing Order</h2>
          </div>
          <button
            onClick={onClose}
            className="hover:bg-blue-700 rounded-full p-1 transition-colors"
          >
            <X size={24} />
          </button>
        </div>

        {/* Dual Trigger Mode Selector */}
        <div className="px-6 py-4 bg-gradient-to-r from-blue-50 to-purple-50 border-b">
          <h3 className="text-sm font-semibold text-gray-700 mb-3">🔑 Production Trigger Mode</h3>
          <div className="grid grid-cols-2 gap-4">
            <button
              type="button"
              onClick={() => setTriggerMode('PARTIAL')}
              className={`p-4 rounded-lg border-2 transition-all ${
                triggerMode === 'PARTIAL'
                  ? 'border-orange-500 bg-orange-50 shadow-md'
                  : 'border-gray-300 bg-white hover:border-orange-300'
              }`}
            >
              <div className="flex items-start gap-3">
                <div className={`mt-1 ${triggerMode === 'PARTIAL' ? 'text-orange-600' : 'text-gray-400'}`}>
                  <AlertCircle size={24} />
                </div>
                <div className="text-left">
                  <h4 className="font-bold text-gray-900">PARTIAL</h4>
                  <p className="text-xs text-gray-600 mt-1">
                    🧵 PO Fabric only<br/>
                    ✂️ Cutting & Embroidery can start<br/>
                    ⏳ Other depts wait for PO Label
                  </p>
                </div>
              </div>
            </button>

            <button
              type="button"
              onClick={() => setTriggerMode('RELEASED')}
              className={`p-4 rounded-lg border-2 transition-all ${
                triggerMode === 'RELEASED'
                  ? 'border-green-500 bg-green-50 shadow-md'
                  : 'border-gray-300 bg-white hover:border-green-300'
              }`}
            >
              <div className="flex items-start gap-3">
                <div className={`mt-1 ${triggerMode === 'RELEASED' ? 'text-green-600' : 'text-gray-400'}`}>
                  <CheckCircle size={24} />
                </div>
                <div className="text-left">
                  <h4 className="font-bold text-gray-900">RELEASED</h4>
                  <p className="text-xs text-gray-600 mt-1">
                    🧵 PO Fabric + 🏷️ PO Label ready<br/>
                    🚀 All departments can start<br/>
                    ✅ Full production release
                  </p>
                </div>
              </div>
            </button>
          </div>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="px-6 py-4 space-y-6">
          {/* Product Selection */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Product <span className="text-red-500">*</span>
              </label>
              <select
                value={formData.product_id}
                onChange={(e) => handleChange('product_id', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                required
              >
                <option value="">Select Product...</option>
                {products?.map((p: Product) => (
                  <option key={p.id} value={p.id}>
                    [{p.code}] {p.name} ({p.type})
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Quantity Planned <span className="text-red-500">*</span>
              </label>
              <input
                type="number"
                value={formData.qty_planned}
                onChange={(e) => handleChange('qty_planned', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="450"
                min="1"
                required
              />
            </div>
          </div>

          {/* PO Selection */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2 flex items-center gap-2">
                🧵 PO Fabric {triggerMode === 'PARTIAL' && <span className="text-red-500">*</span>}
              </label>
              <select
                value={formData.po_fabric_id}
                onChange={(e) => handleChange('po_fabric_id', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                required={triggerMode === 'PARTIAL'}
              >
                <option value="">Select PO Fabric...</option>
                {poFabrics?.map((po: any) => (
                  <option key={po.id} value={po.id}>
                    {po.po_number} - {po.vendor_name} ({po.status})
                  </option>
                ))}
              </select>
              {triggerMode === 'PARTIAL' && (
                <p className="text-xs text-orange-600 mt-1">
                  ⚠️ Required for PARTIAL mode
                </p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2 flex items-center gap-2">
                🏷️ PO Label {triggerMode === 'RELEASED' && <span className="text-red-500">*</span>}
              </label>
              <select
                value={formData.po_label_id}
                onChange={(e) => handleChange('po_label_id', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                required={triggerMode === 'RELEASED'}
              >
                <option value="">Select PO Label...</option>
                {poLabels?.map((po: any) => (
                  <option key={po.id} value={po.id}>
                    {po.po_number} - {po.vendor_name} ({po.status})
                  </option>
                ))}
              </select>
              {triggerMode === 'RELEASED' && (
                <p className="text-xs text-green-600 mt-1">
                  ✅ Required for full RELEASED mode
                </p>
              )}
            </div>
          </div>

          {/* Production Details */}
          <div className="grid grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Production Week
              </label>
              <input
                type="text"
                value={formData.production_week}
                onChange={(e) => handleChange('production_week', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="05-2026"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Destination Country
              </label>
              <input
                type="text"
                value={formData.destination_country}
                onChange={(e) => handleChange('destination_country', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Belgium"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Batch Number
              </label>
              <input
                type="text"
                value={formData.batch_number}
                onChange={(e) => handleChange('batch_number', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Auto-generated if empty"
              />
            </div>
          </div>

          {/* Dates */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Planned Production Date
              </label>
              <input
                type="date"
                value={formData.planned_production_date}
                onChange={(e) => handleChange('planned_production_date', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Target Shipment Date
              </label>
              <input
                type="date"
                value={formData.target_shipment_date}
                onChange={(e) => handleChange('target_shipment_date', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex items-center justify-end gap-3 pt-4 border-t">
            <button
              type="button"
              onClick={onClose}
              className="px-6 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={createMOMutation.isPending}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 flex items-center gap-2"
            >
              {createMOMutation.isPending ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                  Creating...
                </>
              ) : (
                <>
                  <CheckCircle size={18} />
                  Create MO ({triggerMode})
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
