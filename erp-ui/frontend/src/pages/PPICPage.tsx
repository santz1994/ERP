/**
 * PPIC Page - Manufacturing Order Management
 * Updated: 2026-01-21 | Phase 16 Week 4 | PBAC Integration
 */

import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Lock } from 'lucide-react';
import { apiClient } from '@/api/client';
import { usePermission } from '@/hooks/usePermission';

// Types
interface ManufacturingOrder {
  id: number;
  so_line_id?: number;
  product_id: number;
  product_code: string;
  product_name: string;
  qty_planned: number;
  qty_produced: number;
  routing_type: string;
  batch_number: string;
  state: string;
  created_at: string;
}

interface Product {
  id: number;
  code: string;
  name: string;
  type: string;
  uom: string;
}

const PPICPage: React.FC = () => {
  const queryClient = useQueryClient();
  const [activeTab, setActiveTab] = useState<'mos' | 'bom' | 'planning'>('mos');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [filterStatus, setFilterStatus] = useState<string>('all');

  // Permission checks (PBAC - Phase 16 Week 4)
  const canViewMO = usePermission('ppic.view_mo');
  const canCreateMO = usePermission('ppic.create_mo');
  const canScheduleProduction = usePermission('ppic.schedule_production');
  const canApproveMO = usePermission('ppic.approve_mo');

  // Form state
  const [moForm, setMoForm] = useState({
    product_id: '',
    qty_planned: '',
    routing_type: 'Route1',
    batch_number: '',
    so_line_id: ''
  });

  // Fetch Manufacturing Orders
  const { data: mosData, isLoading: mosLoading } = useQuery({
    queryKey: ['manufacturing-orders', filterStatus],
    queryFn: async () => {
      const params = new URLSearchParams();
      if (filterStatus !== 'all') params.append('status', filterStatus);
      const response = await apiClient.get(`/ppic/manufacturing-orders?${params}`);
      return response.data;
    },
    refetchInterval: 5000
  });

  // Fetch Products for dropdown
  const { data: productsData } = useQuery({
    queryKey: ['products-wip-fg'],
    queryFn: async () => {
      const response = await apiClient.get('/admin/products');
      // Filter only WIP and Finish Good
      return response.data.filter((p: Product) => 
        p.type === 'WIP' || p.type === 'Finish Good'
      );
    }
  });

  // Create MO Mutation
  const createMOMutation = useMutation({
    mutationFn: async (data: any) => {
      const response = await apiClient.post('/ppic/manufacturing-order', data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['manufacturing-orders'] });
      setShowCreateModal(false);
      setMoForm({
        product_id: '',
        qty_planned: '',
        routing_type: 'Route1',
        batch_number: '',
        so_line_id: ''
      });
      alert('✅ Manufacturing Order created successfully!');
    },
    onError: (error: any) => {
      alert('❌ Error: ' + (error.response?.data?.detail || error.message));
    }
  });

  // Start MO Mutation
  const startMOMutation = useMutation({
    mutationFn: async (moId: number) => {
      const response = await apiClient.post(`/ppic/manufacturing-order/${moId}/start`);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['manufacturing-orders'] });
      alert('✅ Manufacturing Order started!');
    },
    onError: (error: any) => {
      alert('❌ Error: ' + (error.response?.data?.detail || error.message));
    }
  });

  // Complete MO Mutation
  const completeMOMutation = useMutation({
    mutationFn: async (moId: number) => {
      const response = await apiClient.post(`/ppic/manufacturing-order/${moId}/complete`);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['manufacturing-orders'] });
      alert('✅ Manufacturing Order completed!');
    },
    onError: (error: any) => {
      alert('❌ Error: ' + (error.response?.data?.detail || error.message));
    }
  });

  // Handle create MO submit
  const handleCreateSubmit = () => {
    if (!moForm.product_id || !moForm.qty_planned || !moForm.batch_number) {
      alert('Please fill all required fields');
      return;
    }

    createMOMutation.mutate({
      product_id: parseInt(moForm.product_id),
      qty_planned: parseFloat(moForm.qty_planned),
      routing_type: moForm.routing_type,
      batch_number: moForm.batch_number,
      so_line_id: moForm.so_line_id ? parseInt(moForm.so_line_id) : null
    });
  };

  // Get state color
  const getStateColor = (state: string) => {
    switch (state) {
      case 'Draft': return 'bg-gray-100 text-gray-800';
      case 'In Progress': return 'bg-blue-100 text-blue-800';
      case 'Done': return 'bg-green-100 text-green-800';
      case 'Cancel': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  // Get routing color
  const getRoutingColor = (routing: string) => {
    switch (routing) {
      case 'Route1': return 'bg-purple-100 text-purple-800';
      case 'Route2': return 'bg-indigo-100 text-indigo-800';
      case 'Route3': return 'bg-pink-100 text-pink-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  // Statistics
  const totalMOs = mosData?.length || 0;
  const draftMOs = mosData?.filter((mo: ManufacturingOrder) => mo.state === 'Draft').length || 0;
  const inProgressMOs = mosData?.filter((mo: ManufacturingOrder) => mo.state === 'In Progress').length || 0;
  const completedMOs = mosData?.filter((mo: ManufacturingOrder) => mo.state === 'Done').length || 0;

  return (
    <div className="p-6">
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-800">📋 PPIC - Production Planning</h1>
          <p className="text-gray-600 mt-1">Manufacturing Order Management (Admin Only)</p>
          <p className="text-sm text-orange-600 mt-1">
            ⚠️ Note: Planning done by each department based on capacity. PPIC only tracks & approves.
          </p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          ➕ Create MO
        </button>
      </div>

      {/* Statistics Cards */}
      <div className="grid grid-cols-4 gap-4 mb-6">
        <div className="bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg p-5 text-white shadow-lg">
          <div className="text-sm opacity-90">Total MOs</div>
          <div className="text-3xl font-bold mt-2">{totalMOs}</div>
          <div className="text-xs mt-1 opacity-75">All Manufacturing Orders</div>
        </div>
        
        <div className="bg-gradient-to-br from-gray-500 to-gray-600 rounded-lg p-5 text-white shadow-lg">
          <div className="text-sm opacity-90">Draft</div>
          <div className="text-3xl font-bold mt-2">{draftMOs}</div>
          <div className="text-xs mt-1 opacity-75">Pending Approval</div>
        </div>
        
        <div className="bg-gradient-to-br from-orange-500 to-orange-600 rounded-lg p-5 text-white shadow-lg">
          <div className="text-sm opacity-90">In Progress</div>
          <div className="text-3xl font-bold mt-2">{inProgressMOs}</div>
          <div className="text-xs mt-1 opacity-75">Active Production</div>
        </div>
        
        <div className="bg-gradient-to-br from-green-500 to-green-600 rounded-lg p-5 text-white shadow-lg">
          <div className="text-sm opacity-90">Completed</div>
          <div className="text-3xl font-bold mt-2">{completedMOs}</div>
          <div className="text-xs mt-1 opacity-75">Finished MOs</div>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 mb-6 border-b">
        <button
          onClick={() => setActiveTab('mos')}
          className={`px-6 py-3 font-medium transition-colors ${
            activeTab === 'mos'
              ? 'text-blue-600 border-b-2 border-blue-600'
              : 'text-gray-600 hover:text-gray-800'
          }`}
        >
          📦 Manufacturing Orders
        </button>
        <button
          onClick={() => setActiveTab('bom')}
          className={`px-6 py-3 font-medium transition-colors ${
            activeTab === 'bom'
              ? 'text-blue-600 border-b-2 border-blue-600'
              : 'text-gray-600 hover:text-gray-800'
          }`}
        >
          🔧 BOM Management
        </button>
        <button
          onClick={() => setActiveTab('planning')}
          className={`px-6 py-3 font-medium transition-colors ${
            activeTab === 'planning'
              ? 'text-blue-600 border-b-2 border-blue-600'
              : 'text-gray-600 hover:text-gray-800'
          }`}
        >
          📊 Production Planning
        </button>
      </div>

      {/* Content Area */}
      <div className="bg-white rounded-lg shadow">
        {/* Manufacturing Orders Tab */}
        {activeTab === 'mos' && (
          <div>
            <div className="p-4 border-b flex justify-between items-center">
              <h3 className="font-semibold text-lg">Manufacturing Orders (SPK Induk)</h3>
              <select
                value={filterStatus}
                onChange={(e) => setFilterStatus(e.target.value)}
                className="px-3 py-2 border rounded-lg"
              >
                <option value="all">All Status</option>
                <option value="Draft">Draft</option>
                <option value="In Progress">In Progress</option>
                <option value="Done">Done</option>
                <option value="Cancel">Cancelled</option>
              </select>
            </div>
            
            {mosLoading ? (
              <div className="p-12 text-center">
                <div className="text-4xl mb-4">⏳</div>
                <p className="text-gray-500">Loading manufacturing orders...</p>
              </div>
            ) : mosData && mosData.length > 0 ? (
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">MO ID</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Batch Number</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Product</th>
                      <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase">Routing</th>
                      <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Planned</th>
                      <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Produced</th>
                      <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase">Status</th>
                      <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200">
                    {mosData.map((mo: ManufacturingOrder) => (
                      <tr key={mo.id} className="hover:bg-gray-50">
                        <td className="px-6 py-4 text-sm font-medium text-blue-600">MO-{mo.id}</td>
                        <td className="px-6 py-4 text-sm font-semibold text-gray-900">{mo.batch_number}</td>
                        <td className="px-6 py-4">
                          <div className="text-sm font-medium text-gray-900">{mo.product_code}</div>
                          <div className="text-xs text-gray-500">{mo.product_name}</div>
                        </td>
                        <td className="px-6 py-4 text-center">
                          <span className={`px-3 py-1 text-xs font-semibold rounded-full ${getRoutingColor(mo.routing_type)}`}>
                            {mo.routing_type}
                          </span>
                        </td>
                        <td className="px-6 py-4 text-sm text-right font-semibold text-gray-900">
                          {mo.qty_planned.toLocaleString()}
                        </td>
                        <td className="px-6 py-4 text-sm text-right font-bold text-green-600">
                          {mo.qty_produced.toLocaleString()}
                        </td>
                        <td className="px-6 py-4 text-center">
                          <span className={`px-3 py-1 text-xs font-semibold rounded-full ${getStateColor(mo.state)}`}>
                            {mo.state}
                          </span>
                        </td>
                        <td className="px-6 py-4">
                          <div className="flex justify-center gap-2">
                            {mo.state === 'Draft' && (
                              <button
                                onClick={() => startMOMutation.mutate(mo.id)}
                                className="px-3 py-1 text-xs bg-green-600 text-white rounded hover:bg-green-700"
                              >
                                ▶️ Start
                              </button>
                            )}
                            {mo.state === 'In Progress' && (
                              <button
                                onClick={() => completeMOMutation.mutate(mo.id)}
                                className="px-3 py-1 text-xs bg-blue-600 text-white rounded hover:bg-blue-700"
                              >
                                ✅ Complete
                              </button>
                            )}
                            {mo.state === 'Done' && (
                              <span className="text-xs text-gray-400">No actions</span>
                            )}
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <div className="p-12 text-center">
                <div className="text-6xl mb-4">📋</div>
                <p className="text-gray-500 text-lg">No manufacturing orders found</p>
                <p className="text-gray-400 text-sm mt-2">Create your first MO to start production</p>
              </div>
            )}
          </div>
        )}

        {/* BOM Management Tab */}
        {activeTab === 'bom' && (
          <div className="p-12 text-center">
            <div className="text-6xl mb-4">🔧</div>
            <p className="text-gray-500 text-lg">BOM Management</p>
            <p className="text-gray-400 text-sm mt-2">Feature coming soon - Manage Bill of Materials</p>
          </div>
        )}

        {/* Production Planning Tab */}
        {activeTab === 'planning' && (
          <div className="p-12 text-center">
            <div className="text-6xl mb-4">📊</div>
            <p className="text-gray-500 text-lg">Production Planning</p>
            <p className="text-gray-400 text-sm mt-2">
              Planning is done by each department based on machine capacity
            </p>
            <p className="text-gray-400 text-sm">PPIC tracks compliance with manager directives</p>
          </div>
        )}
      </div>

      {/* Create MO Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h3 className="text-xl font-bold mb-4">➕ Create Manufacturing Order</h3>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Product (WIP/FG) *
                </label>
                <select
                  value={moForm.product_id}
                  onChange={(e) => setMoForm({...moForm, product_id: e.target.value})}
                  className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">Select product...</option>
                  {productsData?.map((product: Product) => (
                    <option key={product.id} value={product.id}>
                      {product.code} - {product.name} ({product.type})
                    </option>
                  ))}
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Planned Quantity *
                </label>
                <input
                  type="number"
                  value={moForm.qty_planned}
                  onChange={(e) => setMoForm({...moForm, qty_planned: e.target.value})}
                  className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                  placeholder="1000"
                  min="1"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Routing Type *
                </label>
                <select
                  value={moForm.routing_type}
                  onChange={(e) => setMoForm({...moForm, routing_type: e.target.value})}
                  className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                >
                  <option value="Route1">Route 1 (Full Process)</option>
                  <option value="Route2">Route 2 (Direct to Sewing)</option>
                  <option value="Route3">Route 3 (With Subcon)</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Batch Number *
                </label>
                <input
                  type="text"
                  value={moForm.batch_number}
                  onChange={(e) => setMoForm({...moForm, batch_number: e.target.value})}
                  className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                  placeholder="BATCH-2026-001"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Sales Order Line ID (Optional)
                </label>
                <input
                  type="number"
                  value={moForm.so_line_id}
                  onChange={(e) => setMoForm({...moForm, so_line_id: e.target.value})}
                  className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                  placeholder="123"
                />
              </div>
            </div>
            
            <div className="flex gap-3 mt-6">
              <button
                onClick={() => setShowCreateModal(false)}
                className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                onClick={handleCreateSubmit}
                disabled={createMOMutation.isPending}
                className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
              >
                {createMOMutation.isPending ? 'Creating...' : 'Create MO'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default PPICPage;
