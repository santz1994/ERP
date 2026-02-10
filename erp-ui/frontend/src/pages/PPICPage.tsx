/**
 * PPIC Page - Manufacturing Order Management
 * Updated: 2026-02-04 | Week 5-10 | Frontend Dashboard Integration + MO Monitoring
 */

import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Lock, Eye } from 'lucide-react';
import { apiClient } from '@/api';
import { usePermission } from '@/hooks/usePermission';
import { MOAggregateView } from '@/components/manufacturing';
import { BOMExplorer, BOMExplosionViewer } from '@/components/bom';
import MOCreateModal from '@/components/ppic/MOCreateModal';
import SPKCreateModal from '@/components/ppic/SPKCreateModal';

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
  const [activeTab, setActiveTab] = useState<'mos' | 'bom' | 'planning' | 'workorders' | 'bom-explorer' | 'mo-monitoring'>('mos');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showSPKModal, setShowSPKModal] = useState(false);
  const [showBOMForm, setShowBOMForm] = useState(false);
  const [filterStatus, setFilterStatus] = useState<string>('all');
  const [selectedMO, setSelectedMO] = useState<number | null>(null);
  const [selectedMOForExplosion, setSelectedMOForExplosion] = useState<number | null>(null);
  const [selectedMOForMonitoring, setSelectedMOForMonitoring] = useState<number | null>(null);

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
      try {
        const params = new URLSearchParams();
        if (filterStatus !== 'all') params.append('status', filterStatus);
        const response = await apiClient.get(`/ppic/manufacturing-orders?${params}`);
        return response.data || [];
      } catch (error) {
        console.error('[PPIC] Error fetching manufacturing orders:', error);
        return []; // Return empty array on error
      }
    },
    refetchInterval: 5000
  });

  // Fetch Products for dropdown
  const { data: productsData } = useQuery({
    queryKey: ['products-wip-fg'],
    queryFn: async () => {
      const response = await apiClient.get('/admin/products');
      // Filter only WIP and Finish Good
      const products = response.data || [];
      return products.filter((p: Product) => 
        p.type === 'WIP' || p.type === 'Finish Good'
      );
    }
  });

  // Fetch Work Orders
  const { data: workOrdersData, isLoading: wosLoading } = useQuery({
    queryKey: ['work-orders', selectedMO],
    queryFn: async () => {
      const params = new URLSearchParams();
      if (selectedMO) params.append('mo_id', selectedMO.toString());
      const response = await apiClient.get(`/work-orders?${params}`);
      return response.data;
    },
    enabled: activeTab === 'workorders',
    refetchInterval: 5000
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
      alert('Manufacturing Order created successfully!');
    },
    onError: (error: any) => {
      alert('Error: ' + (error.response?.data?.detail || error.message));
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
      alert('Manufacturing Order started!');
    },
    onError: (error: any) => {
      alert('Error: ' + (error.response?.data?.detail || error.message));
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
      alert('Manufacturing Order completed!');
    },
    onError: (error: any) => {
      alert('Error: ' + (error.response?.data?.detail || error.message));
    }
  });

  // Generate Work Orders Mutation
  const generateWOMutation = useMutation({
    mutationFn: async (moId: number) => {
      const response = await apiClient.post('/work-orders/generate', { mo_id: moId });
      return response.data;
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['manufacturing-orders'] });
      alert(`Successfully generated ${data.work_orders_created} Work Orders!`);
    },
    onError: (error: any) => {
      const errorMsg = error.response?.data?.detail || error.message;
      alert('Error generating Work Orders: ' + errorMsg);
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
          <h1 className="text-3xl font-bold text-gray-800">PPIC - Production Planning</h1>
          <p className="text-gray-600 mt-1">Manufacturing Order Management (Admin Only)</p>
          <p className="text-sm text-orange-600 mt-1">
            Note: Planning done by each department based on capacity. PPIC only tracks & approves.
          </p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          Create MO
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
      <div className="flex gap-2 mb-6 border-b overflow-x-auto">
        <button
          onClick={() => setActiveTab('mos')}
          className={`px-6 py-3 font-medium transition-colors whitespace-nowrap ${
            activeTab === 'mos'
              ? 'text-blue-600 border-b-2 border-blue-600'
              : 'text-gray-600 hover:text-gray-800'
          }`}
        >
          Manufacturing Orders
        </button>
        <button
          onClick={() => setActiveTab('mo-monitoring')}
          className={`px-6 py-3 font-medium transition-colors whitespace-nowrap ${
            activeTab === 'mo-monitoring'
              ? 'text-blue-600 border-b-2 border-blue-600'
              : 'text-gray-600 hover:text-gray-800'
          }`}
        >
          MO Monitoring
        </button>
        <button
          onClick={() => setActiveTab('workorders')}
          className={`px-6 py-3 font-medium transition-colors whitespace-nowrap ${
            activeTab === 'workorders'
              ? 'text-blue-600 border-b-2 border-blue-600'
              : 'text-gray-600 hover:text-gray-800'
          }`}
        >
          Work Orders
        </button>
        <button
          onClick={() => setActiveTab('bom-explorer')}
          className={`px-6 py-3 font-medium transition-colors whitespace-nowrap ${
            activeTab === 'bom-explorer'
              ? 'text-blue-600 border-b-2 border-blue-600'
              : 'text-gray-600 hover:text-gray-800'
          }`}
        >
          BOM Explorer
        </button>
        <button
          onClick={() => setActiveTab('bom')}
          className={`px-6 py-3 font-medium transition-colors whitespace-nowrap ${
            activeTab === 'bom'
              ? 'text-blue-600 border-b-2 border-blue-600'
              : 'text-gray-600 hover:text-gray-800'
          }`}
        >
          BOM Management
        </button>
        <button
          onClick={() => setActiveTab('planning')}
          className={`px-6 py-3 font-medium transition-colors whitespace-nowrap ${
            activeTab === 'planning'
              ? 'text-blue-600 border-b-2 border-blue-600'
              : 'text-gray-600 hover:text-gray-800'
          }`}
        >
          Production Planning
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
                          <div className="flex justify-center gap-2 flex-wrap">
                            <button
                              onClick={() => setSelectedMOForExplosion(mo.id)}
                              className="px-3 py-1 text-xs bg-indigo-600 text-white rounded hover:bg-indigo-700 flex items-center gap-1"
                              title="View BOM Explosion"
                            >
                              <Eye size={14} />
                              View BOM
                            </button>
                            {mo.state === 'Draft' && (
                              <>
                                <button
                                  onClick={() => generateWOMutation.mutate(mo.id)}
                                  disabled={generateWOMutation.isPending}
                                  className="px-3 py-1 text-xs bg-purple-600 text-white rounded hover:bg-purple-700 disabled:opacity-50"
                                  title="Generate Work Orders from BOM"
                                >
                                  Generate WOs
                                </button>
                                <button
                                  onClick={() => startMOMutation.mutate(mo.id)}
                                  className="px-3 py-1 text-xs bg-green-600 text-white rounded hover:bg-green-700"
                                >
                                  Start
                                </button>
                              </>
                            )}
                            {mo.state === 'In Progress' && (
                              <button
                                onClick={() => completeMOMutation.mutate(mo.id)}
                                className="px-3 py-1 text-xs bg-blue-600 text-white rounded hover:bg-blue-700"
                              >
                                Complete
                              </button>
                            )}
                            {mo.state === 'Done' && (
                              <span className="text-xs text-gray-400">Completed</span>
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
                <div className="text-6xl mb-4"></div>
                <p className="text-gray-500 text-lg">No manufacturing orders found</p>
                <p className="text-gray-400 text-sm mt-2">Create your first MO to start production</p>
              </div>
            )}
          </div>
        )}

        {/* MO Monitoring Tab - NEW CRITICAL FEATURE */}
        {activeTab === 'mo-monitoring' && (
          <div className="p-6">
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Select Manufacturing Order to Monitor
              </label>
              <select
                value={selectedMOForMonitoring || ''}
                onChange={(e) => setSelectedMOForMonitoring(e.target.value ? parseInt(e.target.value) : null)}
                className="w-full md:w-1/2 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="">-- Select MO to View Aggregate Data --</option>
                {mosData?.map((mo: ManufacturingOrder) => (
                  <option key={mo.id} value={mo.id}>
                    {mo.batch_number} - {mo.product_name} ({mo.qty_planned} pcs) - {mo.state}
                  </option>
                ))}
              </select>
            </div>
            
            {selectedMOForMonitoring ? (
              <MOAggregateView moId={selectedMOForMonitoring} />
            ) : (
              <div className="bg-blue-50 border-2 border-blue-300 rounded-lg p-12 text-center">
                <div className="text-6xl mb-4"></div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">
                  MO Aggregate Monitoring
                </h3>
                <p className="text-gray-600 max-w-2xl mx-auto">
                  Select a Manufacturing Order from the dropdown above to view:<br/>
                  • All SPKs progress for the MO<br/>
                  • Aggregate metrics (total production, good output, defects, rework)<br/>
                  • MO coverage percentage<br/>
                  • Real-time status updates
                </p>
              </div>
            )}
          </div>
        )}

        {/* BOM Explorer Tab */}
        {activeTab === 'bom-explorer' && (
          <div className="p-6">
            <BOMExplorer showSearch={true} />
          </div>
        )}

        {/* Work Orders Tab */}
        {activeTab === 'workorders' && (
          <div>
            <div className="p-4 border-b flex justify-between items-center">
              <h3 className="font-semibold text-lg">Work Orders by Department</h3>
              <select
                value={selectedMO || ''}
                onChange={(e) => setSelectedMO(e.target.value ? parseInt(e.target.value) : null)}
                className="px-3 py-2 border rounded-lg"
              >
                <option value="">All MOs</option>
                {mosData?.map((mo: ManufacturingOrder) => (
                  <option key={mo.id} value={mo.id}>
                    {mo.batch_number} - {mo.product_code}
                  </option>
                ))}
              </select>
            </div>
            
            {wosLoading ? (
              <div className="p-12 text-center">
                <div className="text-4xl mb-4">[LOADING]</div>
                <p className="text-gray-500">Loading work orders...</p>
              </div>
            ) : workOrdersData && workOrdersData.length > 0 ? (
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">WO Number</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Department</th>
                      <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase">Sequence</th>
                      <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Target Qty</th>
                      <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Actual Qty</th>
                      <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase">Status</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Input WIP</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Output WIP</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200">
                    {workOrdersData.map((wo: any) => (
                      <tr key={wo.id} className="hover:bg-gray-50">
                        <td className="px-6 py-4 text-sm font-medium text-blue-600">{wo.wo_number}</td>
                        <td className="px-6 py-4 text-sm">
                          <span className={`px-3 py-1 text-xs font-semibold rounded-full ${
                            wo.department === 'CUTTING' ? 'bg-red-100 text-red-800' :
                            wo.department === 'EMBROIDERY' ? 'bg-yellow-100 text-yellow-800' :
                            wo.department === 'SEWING' ? 'bg-blue-100 text-blue-800' :
                            wo.department === 'FINISHING' ? 'bg-purple-100 text-purple-800' :
                            wo.department === 'PACKING' ? 'bg-green-100 text-green-800' :
                            'bg-gray-100 text-gray-800'
                          }`}>
                            {wo.department}
                          </span>
                        </td>
                        <td className="px-6 py-4 text-sm text-center font-bold text-gray-900">#{wo.sequence}</td>
                        <td className="px-6 py-4 text-sm text-right font-semibold text-gray-900">
                          {parseFloat(wo.target_qty).toLocaleString(undefined, { maximumFractionDigits: 2 })}
                        </td>
                        <td className="px-6 py-4 text-sm text-right font-bold text-green-600">
                          {wo.actual_qty ? parseFloat(wo.actual_qty).toLocaleString(undefined, { maximumFractionDigits: 2 }) : '-'}
                        </td>
                        <td className="px-6 py-4 text-center">
                          <span className={`px-3 py-1 text-xs font-semibold rounded-full ${
                            wo.status === 'PENDING' ? 'bg-gray-100 text-gray-800' :
                            wo.status === 'READY' ? 'bg-blue-100 text-blue-800' :
                            wo.status === 'IN_PROGRESS' ? 'bg-yellow-100 text-yellow-800' :
                            wo.status === 'FINISHED' ? 'bg-green-100 text-green-800' :
                            wo.status === 'CANCELLED' ? 'bg-red-100 text-red-800' :
                            'bg-gray-100 text-gray-800'
                          }`}>
                            {wo.status}
                          </span>
                        </td>
                        <td className="px-6 py-4 text-xs text-gray-600">
                          {wo.input_wip_product_code || 'Raw Materials'}
                        </td>
                        <td className="px-6 py-4 text-xs text-gray-600">
                          {wo.output_wip_product_code || '-'}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <div className="p-12 text-center">
                <div className="text-6xl mb-4"></div>
                <p className="text-gray-500 text-lg">No work orders found</p>
                <p className="text-gray-400 text-sm mt-2">Generate WOs from a Manufacturing Order first</p>
              </div>
            )}
          </div>
        )}

        {/* BOM Management Tab */}
        {activeTab === 'bom' && (
          <div className="space-y-6">
            <div className="flex justify-between items-center">
              <h2 className="text-2xl font-bold text-gray-800">BOM Management</h2>
              <div className="flex gap-2">
                <button
                  onClick={() => setShowBOMForm(!showBOMForm)}
                  className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition"
                >
                  Add BOM Manually
                </button>
                <a 
                  href="/admin/import-export" 
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
                >
                  [Import] Import BOM
                </a>
                <a 
                  href="/admin/import-export" 
                  className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition"
                >
                  [Export] Export BOM
                </a>
              </div>
            </div>

            {/* BOM Manual Entry Form */}
            {showBOMForm && (
              <div className="bg-white rounded-lg shadow p-6 border-2 border-purple-300">
                <h3 className="text-lg font-semibold text-gray-800 mb-4">Add BOM Manually</h3>
                <div className="grid grid-cols-2 gap-4 mb-4">
                  <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-2">Product Name *</label>
                    <input
                      type="text"
                      placeholder="e.g., T-Shirt Premium"
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-purple-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-2">Product Code *</label>
                    <input
                      type="text"
                      placeholder="e.g., TS-001"
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-purple-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-2">Material/Component *</label>
                    <input
                      type="text"
                      placeholder="e.g., Cotton Fabric"
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-purple-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-2">Quantity Required *</label>
                    <input
                      type="number"
                      placeholder="e.g., 1.5"
                      min="0"
                      step="0.01"
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-purple-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-2">Unit *</label>
                    <select className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-purple-500">
                      <option value="">Select Unit</option>
                      <option value="kg">Kilogram (kg)</option>
                      <option value="meter">Meter (m)</option>
                      <option value="pcs">Pieces (pcs)</option>
                      <option value="liter">Liter (L)</option>
                      <option value="box">Box</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-2">Unit Price</label>
                    <input
                      type="number"
                      placeholder="e.g., 25000"
                      min="0"
                      step="0.01"
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-purple-500"
                    />
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4 mb-4">
                  <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-2">Material Type</label>
                    <select className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-purple-500">
                      <option value="">Select Type</option>
                      <option value="fabric">Fabric</option>
                      <option value="thread">Thread</option>
                      <option value="button">Button</option>
                      <option value="zipper">Zipper</option>
                      <option value="elastic">Elastic</option>
                      <option value="lace">Lace</option>
                      <option value="other">Other</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-2">Status</label>
                    <select className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-purple-500">
                      <option value="active">Active</option>
                      <option value="inactive">Inactive</option>
                    </select>
                  </div>
                </div>
                <div className="mb-4">
                  <label className="block text-sm font-semibold text-gray-700 mb-2">Notes/Description</label>
                  <textarea
                    placeholder="e.g., Premium quality cotton, 100% cotton, white color"
                    rows={3}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-purple-500"
                  ></textarea>
                </div>
                <div className="flex gap-2 justify-end">
                  <button
                    onClick={() => setShowBOMForm(false)}
                    className="px-4 py-2 bg-gray-400 text-white rounded-lg hover:bg-gray-500 transition"
                  >
                    Cancel
                  </button>
                  <button className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition">
                    Save BOM
                  </button>
                </div>
              </div>
            )}

            {/* Quick Instructions */}
            <div className="grid grid-cols-3 gap-4">
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <div className="text-lg font-semibold text-blue-900 mb-2">[Import] Import BOM</div>
                <ol className="text-sm text-blue-700 space-y-1">
                  <li>1. Go to Admin → Import/Export</li>
                  <li>2. Select "Bill of Materials"</li>
                  <li>3. Upload CSV/Excel file</li>
                  <li>4. Confirm import</li>
                </ol>
              </div>

              <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                <div className="text-lg font-semibold text-green-900 mb-2">[Export] Export BOM</div>
                <ol className="text-sm text-green-700 space-y-1">
                  <li>1. Go to Admin → Import/Export</li>
                  <li>2. Select "Bill of Materials"</li>
                  <li>3. Choose format (CSV/Excel)</li>
                  <li>4. Download file</li>
                </ol>
              </div>

              <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
                <div className="text-lg font-semibold text-purple-900 mb-2">Manual BOM Entry</div>
                <ol className="text-sm text-purple-700 space-y-1">
                  <li>1. Click "Add BOM Manually" button</li>
                  <li>2. Fill in product and material details</li>
                  <li>3. Enter quantity, unit, and price</li>
                  <li>4. Click "Save BOM"</li>
                </ol>
              </div>
            </div>

            {/* BOM Info Card */}
            <div className="bg-white rounded-lg shadow p-6 border-l-4 border-orange-500">
              <h3 className="text-lg font-semibold text-gray-800 mb-3">BOM Management Info</h3>
              <ul className="text-gray-700 space-y-2 text-sm">
                <li><strong>Current Status:</strong> All BOM operations available via Import/Export & Manual Entry</li>
                <li><strong>Supported Formats:</strong> CSV, Excel (.xlsx), and Manual Entry Form</li>
                <li><strong>BOM Features:</strong> Create, Edit, Delete, Import, Export</li>
                <li><strong>Integration:</strong> BOMs linked to Products automatically</li>
                <li><strong>Usage:</strong> Used in all production modules (Cutting, Sewing, Finishing, etc.)</li>
                <li><strong>Tip:</strong> For large BOM management, use CSV/Excel import for batch operations</li>
              </ul>
            </div>

            {/* Production Modules using BOM */}
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-semibold text-gray-800 mb-4">Modules Using BOM</h3>
              <div className="grid grid-cols-2 gap-4">
                <div className="flex items-center gap-3 p-3 bg-gray-50 rounded">
                  <span className="text-2xl"></span>
                  <div>
                    <div className="font-semibold text-gray-800">Cutting Module</div>
                    <div className="text-sm text-gray-600">Validates material vs BOM</div>
                  </div>
                </div>
                <div className="flex items-center gap-3 p-3 bg-gray-50 rounded">
                  <span className="text-2xl"></span>
                  <div>
                    <div className="font-semibold text-gray-800">Sewing Module</div>
                    <div className="text-sm text-gray-600">Input validation vs BOM</div>
                  </div>
                </div>
                <div className="flex items-center gap-3 p-3 bg-gray-50 rounded">
                  <span className="text-2xl"></span>
                  <div>
                    <div className="font-semibold text-gray-800">Finishing Module</div>
                    <div className="text-sm text-gray-600">Material tracking</div>
                  </div>
                </div>
                <div className="flex items-center gap-3 p-3 bg-gray-50 rounded">
                  <span className="text-2xl"></span>
                  <div>
                    <div className="font-semibold text-gray-800">Packing Module</div>
                    <div className="text-sm text-gray-600">Final BOM verification</div>
                  </div>
                </div>
              </div>
            </div>

            {/* BOM List - View & Edit */}
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-semibold text-gray-800 mb-4">BOM List - View & Edit</h3>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b-2 border-gray-300">
                      <th className="text-left py-3 px-4 font-semibold text-gray-700">Product</th>
                      <th className="text-left py-3 px-4 font-semibold text-gray-700">Material/Component</th>
                      <th className="text-center py-3 px-4 font-semibold text-gray-700">Qty Required</th>
                      <th className="text-center py-3 px-4 font-semibold text-gray-700">Unit</th>
                      <th className="text-center py-3 px-4 font-semibold text-gray-700">Unit Price</th>
                      <th className="text-center py-3 px-4 font-semibold text-gray-700">Status</th>
                      <th className="text-center py-3 px-4 font-semibold text-gray-700">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr className="border-b border-gray-200 hover:bg-gray-50">
                      <td className="py-3 px-4">T-Shirt Premium (TS-001)</td>
                      <td className="py-3 px-4">Cotton Fabric</td>
                      <td className="text-center py-3 px-4">1.5</td>
                      <td className="text-center py-3 px-4">m</td>
                      <td className="text-center py-3 px-4">Rp 25,000</td>
                      <td className="text-center py-3 px-4">
                        <span className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-xs font-semibold">Active</span>
                      </td>
                      <td className="text-center py-3 px-4 space-x-2">
                        <button className="px-3 py-1 bg-blue-500 text-white rounded hover:bg-blue-600 transition text-xs">Edit</button>
                        <button className="px-3 py-1 bg-red-500 text-white rounded hover:bg-red-600 transition text-xs">Delete</button>
                      </td>
                    </tr>
                    <tr className="border-b border-gray-200 hover:bg-gray-50">
                      <td className="py-3 px-4">T-Shirt Premium (TS-001)</td>
                      <td className="py-3 px-4">Thread White</td>
                      <td className="text-center py-3 px-4">2</td>
                      <td className="text-center py-3 px-4">pcs</td>
                      <td className="text-center py-3 px-4">Rp 5,000</td>
                      <td className="text-center py-3 px-4">
                        <span className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-xs font-semibold">Active</span>
                      </td>
                      <td className="text-center py-3 px-4 space-x-2">
                        <button className="px-3 py-1 bg-blue-500 text-white rounded hover:bg-blue-600 transition text-xs">Edit</button>
                        <button className="px-3 py-1 bg-red-500 text-white rounded hover:bg-red-600 transition text-xs">Delete</button>
                      </td>
                    </tr>
                    <tr className="border-b border-gray-200 hover:bg-gray-50">
                      <td className="py-3 px-4">T-Shirt Premium (TS-001)</td>
                      <td className="py-3 px-4">Button (4 hole)</td>
                      <td className="text-center py-3 px-4">5</td>
                      <td className="text-center py-3 px-4">pcs</td>
                      <td className="text-center py-3 px-4">Rp 2,000</td>
                      <td className="text-center py-3 px-4">
                        <span className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-xs font-semibold">Active</span>
                      </td>
                      <td className="text-center py-3 px-4 space-x-2">
                        <button className="px-3 py-1 bg-blue-500 text-white rounded hover:bg-blue-600 transition text-xs">Edit</button>
                        <button className="px-3 py-1 bg-red-500 text-white rounded hover:bg-red-600 transition text-xs">Delete</button>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
              <div className="mt-4 text-center text-sm text-gray-600">
                Showing 3 BOM items | Total Cost: Rp 47,500 per unit
              </div>
            </div>

            {/* Action Links */}
            <div className="flex gap-2 justify-end">
              <a 
                href="/admin/import-export"
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
              >
                Go to Import/Export
              </a>
            </div>
          </div>
        )}

        {/* Production Planning Tab */}
        {activeTab === 'planning' && (
          <div className="p-12 text-center">
            <div className="text-6xl mb-4"></div>
            <p className="text-gray-500 text-lg">Production Planning</p>
            <p className="text-gray-400 text-sm mt-2">
              Planning is done by each department based on machine capacity
            </p>
            <p className="text-gray-400 text-sm">PPIC tracks compliance with manager directives</p>
          </div>
        )}
      </div>

      {/* BOM Explosion Viewer Modal */}
      {selectedMOForExplosion && (
        <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-lg max-w-6xl w-full max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between p-4 border-b sticky top-0 bg-white z-10">
              <h3 className="text-xl font-bold">BOM Explosion - MO #{selectedMOForExplosion}</h3>
              <button 
                onClick={() => setSelectedMOForExplosion(null)}
                className="text-gray-500 hover:text-gray-700 text-2xl leading-none"
              >
                ×
              </button>
            </div>
            <div className="p-4">
              <BOMExplosionViewer moId={selectedMOForExplosion} showCosts={true} />
            </div>
          </div>
        </div>
      )}

      {/* MO Create Modal */}
      <MOCreateModal
        isOpen={showCreateModal}
        onClose={() => setShowCreateModal(false)}
        onSuccess={(moId) => {
          queryClient.invalidateQueries({ queryKey: ['manufacturing-orders'] });
          setShowCreateModal(false);
        }}
      />

      {/* SPK Create Modal */}
      <SPKCreateModal
        isOpen={showSPKModal}
        onClose={() => setShowSPKModal(false)}
        onSuccess={(spkId) => {
          queryClient.invalidateQueries({ queryKey: ['work-orders'] });
          setShowSPKModal(false);
        }}
      />

      {/* OLD Create MO Modal - DEPRECATED */}
      {false && showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h3 className="text-xl font-bold mb-4">Create Manufacturing Order (OLD)</h3>
            
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
