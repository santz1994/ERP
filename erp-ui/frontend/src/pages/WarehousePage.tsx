import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/api/client';
import BarcodeScanner from '../components/BarcodeScanner';
import MaterialRequestModal, { MaterialRequestFormData } from '../components/warehouse/MaterialRequestModal';
import MaterialRequestsList from '../components/warehouse/MaterialRequestsList';
import { useUIStore } from '@/store';

// Types
interface StockItem {
  product_id: number;
  product_code: string;
  product_name: string;
  qty_on_hand: number;
  qty_reserved: number;
  qty_available: number;
  location: string;
  uom: string;
}

interface StockMovement {
  id: number;
  product_id: number;
  product_code: string;
  product_name: string;
  from_location: string;
  to_location: string;
  qty: number;
  move_type: string;
  created_at: string;
  created_by: string;
}

const WarehousePage: React.FC = () => {
  const { addNotification } = useUIStore();
  const [activeTab, setActiveTab] = useState<'inventory' | 'movements' | 'barcode' | 'transfers' | 'material-requests'>('inventory');
  const [searchTerm, setSearchTerm] = useState('');
  const [showLowStockOnly, setShowLowStockOnly] = useState(false);
  
  // Modal states for Stock Adjustment and Internal Transfer
  const [showStockAdjustmentModal, setShowStockAdjustmentModal] = useState(false);
  const [showInternalTransferModal, setShowInternalTransferModal] = useState(false);
  const [showMaterialRequestModal, setShowMaterialRequestModal] = useState(false);
  const [materialRequestLoading, setMaterialRequestLoading] = useState(false);
  const [materialRequestError, setMaterialRequestError] = useState<string | null>(null);
  const [adjustmentData, setAdjustmentData] = useState({
    product_id: '',
    adjustment_qty: 0,
    reason: '',
    notes: ''
  });
  const [transferData, setTransferData] = useState({
    product_id: '',
    from_location: '',
    to_location: '',
    qty: 0,
    reference: ''
  });
  const [adjustmentLoading, setAdjustmentLoading] = useState(false);
  const [transferLoading, setTransferLoading] = useState(false);
  
  // Barcode scanning states
  const [barcodeOperation, setBarcodeOperation] = useState<'receive' | 'pick'>('receive');
  const [scannedBarcode, setScannedBarcode] = useState('');
  const [transactionQty, setTransactionQty] = useState<number>(0);
  const [transactionNotes, setTransactionNotes] = useState('');
  const [transactionLoading, setTransactionLoading] = useState(false);
  const [transactionSuccess, setTransactionSuccess] = useState<any>(null);

  // Fetch Stock Inventory
  const { data: inventoryData, isLoading: inventoryLoading } = useQuery({
    queryKey: ['warehouse-inventory', searchTerm],
    queryFn: async () => {
      // This would need an inventory endpoint - for now mock data
      const response = await apiClient.get('/warehouse/inventory');
      return response.data;
    },
    refetchInterval: 5000,
    enabled: false // Disable until endpoint exists
  });

  // Fetch Stock Movements
  const { data: movementsData } = useQuery({
    queryKey: ['stock-movements'],
    queryFn: async () => {
      const response = await apiClient.get('/warehouse/stock-movements');
      return response.data;
    },
    refetchInterval: 10000,
    enabled: false // Disable until endpoint exists
  });
  
  // Fetch Barcode History
  const { data: barcodeHistory, refetch: refetchHistory } = useQuery({
    queryKey: ['barcode-history'],
    queryFn: async () => {
      const response = await apiClient.get('/barcode/history?location=warehouse&limit=20');
      return response.data;
    },
    refetchInterval: 10000
  });

  // Handle barcode scan
  const handleBarcodeScan = (barcode: string) => {
    setScannedBarcode(barcode);
    setTransactionQty(0);
    setTransactionSuccess(null);
  };

  // Handle transaction submission
  const handleTransactionSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!scannedBarcode || transactionQty <= 0) {
      alert('Please scan a barcode and enter quantity');
      return;
    }

    setTransactionLoading(true);
    
    try {
      const endpoint = barcodeOperation === 'receive' ? '/barcode/receive' : '/barcode/pick';
      const response = await apiClient.post(endpoint, {
        barcode: scannedBarcode,
        qty: transactionQty,
        location: 'warehouse',
        notes: transactionNotes || null
      });

      setTransactionSuccess(response.data);
      setScannedBarcode('');
      setTransactionQty(0);
      setTransactionNotes('');
      refetchHistory();
      
      // Auto-clear success message after 5 seconds
      setTimeout(() => setTransactionSuccess(null), 5000);
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Transaction failed');
    } finally {
      setTransactionLoading(false);
    }
  };

  // Mock data for demonstration
  const mockInventory: StockItem[] = [
    {
      product_id: 1,
      product_code: 'FAB-VEL-BLU',
      product_name: 'Velboa Blue Fabric',
      qty_on_hand: 5000,
      qty_reserved: 1200,
      qty_available: 3800,
      location: 'WH-RAW-A1',
      uom: 'Meter'
    },
    {
      product_id: 2,
      product_code: 'WIP-CUT-SHARK',
      product_name: 'Cut Parts - Shark',
      qty_on_hand: 2500,
      qty_reserved: 800,
      qty_available: 1700,
      location: 'WH-WIP-B2',
      uom: 'Pcs'
    },
    {
      product_id: 3,
      product_code: 'ACC-EYE-10MM',
      product_name: 'Safety Eyes 10mm',
      qty_on_hand: 15000,
      qty_reserved: 5000,
      qty_available: 10000,
      location: 'WH-ACC-C3',
      uom: 'Pcs'
    }
  ];

  const mockMovements: StockMovement[] = [
    {
      id: 1,
      product_id: 1,
      product_code: 'FAB-VEL-BLU',
      product_name: 'Velboa Blue Fabric',
      from_location: 'WH-RAW-A1',
      to_location: 'CUTTING-LINE1',
      qty: 500,
      move_type: 'Internal Transfer',
      created_at: '2026-01-19T10:30:00',
      created_by: 'Admin Warehouse'
    },
    {
      id: 2,
      product_id: 2,
      product_code: 'WIP-CUT-SHARK',
      product_name: 'Cut Parts - Shark',
      from_location: 'CUTTING-LINE1',
      to_location: 'WH-WIP-B2',
      qty: 1000,
      move_type: 'Production Output',
      created_at: '2026-01-19T11:15:00',
      created_by: 'SPV Cutting'
    }
  ];

  // Handle Stock Adjustment
  const handleStockAdjustmentSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!adjustmentData.product_id || adjustmentData.adjustment_qty === 0) {
      alert('Please fill in all required fields');
      return;
    }

    setAdjustmentLoading(true);
    try {
      await apiClient.post('/warehouse/stock-adjustment', {
        product_id: parseInt(adjustmentData.product_id),
        qty_adjustment: adjustmentData.adjustment_qty,
        reason: adjustmentData.reason,
        notes: adjustmentData.notes
      });
      alert('Stock adjustment recorded successfully');
      setShowStockAdjustmentModal(false);
      setAdjustmentData({ product_id: '', adjustment_qty: 0, reason: '', notes: '' });
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Stock adjustment failed');
    } finally {
      setAdjustmentLoading(false);
    }
  };

  // Handle Internal Transfer
  const handleInternalTransferSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!transferData.product_id || !transferData.from_location || !transferData.to_location || transferData.qty === 0) {
      alert('Please fill in all required fields');
      return;
    }

    setTransferLoading(true);
    try {
      await apiClient.post('/warehouse/internal-transfer', {
        product_id: parseInt(transferData.product_id),
        from_location: transferData.from_location,
        to_location: transferData.to_location,
        qty: transferData.qty,
        reference: transferData.reference
      });
      alert('Internal transfer completed successfully');
      setShowInternalTransferModal(false);
      setTransferData({ product_id: '', from_location: '', to_location: '', qty: 0, reference: '' });
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Internal transfer failed');
    } finally {
      setTransferLoading(false);
    }
  };

  // Handle Material Request
  const handleMaterialRequestSubmit = async (data: MaterialRequestFormData) => {
    setMaterialRequestLoading(true);
    setMaterialRequestError(null);
    try {
      const response = await apiClient.post('/warehouse/material-requests', {
        product_id: data.product_id,
        location_id: data.location_id,
        qty_requested: data.qty_requested,
        uom: data.uom,
        purpose: data.purpose
      });
      
      addNotification('success', 'Material request submitted for approval');
      setShowMaterialRequestModal(false);
      
      // Refetch material requests if there's a list component
      return response.data;
    } catch (error: any) {
      const errorMsg = error.response?.data?.detail || 'Failed to submit material request';
      setMaterialRequestError(errorMsg);
      addNotification('error', errorMsg);
      throw error;
    } finally {
      setMaterialRequestLoading(false);
    }
  };

  // Filter inventory
  const filteredInventory = mockInventory.filter(item => {
    const matchesSearch = item.product_code.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         item.product_name.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesLowStock = !showLowStockOnly || (item.qty_available < item.qty_on_hand * 0.3);
    return matchesSearch && matchesLowStock;
  });

  // Statistics
  const totalProducts = mockInventory.length;
  const lowStockItems = mockInventory.filter(item => item.qty_available < item.qty_on_hand * 0.3).length;
  const totalValue = mockInventory.reduce((sum, item) => sum + item.qty_on_hand, 0);
  const totalReserved = mockInventory.reduce((sum, item) => sum + item.qty_reserved, 0);

  return (
    <>
    <div className="p-6">
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-800">🏭 Warehouse Management</h1>
          <p className="text-gray-600 mt-1">Stock inventory, movements, and transfers</p>
        </div>
        <div className="flex gap-3">
          <button 
            onClick={() => setShowStockAdjustmentModal(true)}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
            📦 Stock Adjustment
          </button>
          <button 
            onClick={() => setShowInternalTransferModal(true)}
            className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors">
            🔄 Internal Transfer
          </button>
        </div>
      </div>

      {/* Statistics Cards */}
      <div className="grid grid-cols-4 gap-4 mb-6">
        <div className="bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg p-5 text-white shadow-lg">
          <div className="text-sm opacity-90">Total Products</div>
          <div className="text-3xl font-bold mt-2">{totalProducts}</div>
          <div className="text-xs mt-1 opacity-75">Active SKUs</div>
        </div>
        
        <div className="bg-gradient-to-br from-purple-500 to-purple-600 rounded-lg p-5 text-white shadow-lg">
          <div className="text-sm opacity-90">Total Stock</div>
          <div className="text-3xl font-bold mt-2">{totalValue.toLocaleString()}</div>
          <div className="text-xs mt-1 opacity-75">All locations</div>
        </div>
        
        <div className="bg-gradient-to-br from-orange-500 to-orange-600 rounded-lg p-5 text-white shadow-lg">
          <div className="text-sm opacity-90">Reserved</div>
          <div className="text-3xl font-bold mt-2">{totalReserved.toLocaleString()}</div>
          <div className="text-xs mt-1 opacity-75">Allocated to SPK</div>
        </div>
        
        <div className="bg-gradient-to-br from-red-500 to-red-600 rounded-lg p-5 text-white shadow-lg">
          <div className="text-sm opacity-90">Low Stock Alert</div>
          <div className="text-3xl font-bold mt-2">{lowStockItems}</div>
          <div className="text-xs mt-1 opacity-75">Below 30% available</div>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 mb-6 border-b overflow-x-auto">
        <button
          onClick={() => setActiveTab('inventory')}
          className={`px-6 py-3 font-medium transition-colors whitespace-nowrap ${
            activeTab === 'inventory'
              ? 'text-blue-600 border-b-2 border-blue-600'
              : 'text-gray-600 hover:text-gray-800'
          }`}
        >
          📦 Stock Inventory
        </button>
        <button
          onClick={() => setActiveTab('movements')}
          className={`px-6 py-3 font-medium transition-colors whitespace-nowrap ${
            activeTab === 'movements'
              ? 'text-blue-600 border-b-2 border-blue-600'
              : 'text-gray-600 hover:text-gray-800'
          }`}
        >
          🔄 Stock Movements
        </button>
        <button
          onClick={() => setActiveTab('barcode')}
          className={`px-6 py-3 font-medium transition-colors whitespace-nowrap ${
            activeTab === 'barcode'
              ? 'text-blue-600 border-b-2 border-blue-600'
              : 'text-gray-600 hover:text-gray-800'
          }`}
        >
          📷 Barcode Scanner
        </button>
        <button
          onClick={() => setActiveTab('material-requests')}
          className={`px-6 py-3 font-medium transition-colors whitespace-nowrap ${
            activeTab === 'material-requests'
              ? 'text-blue-600 border-b-2 border-blue-600'
              : 'text-gray-600 hover:text-gray-800'
          }`}
        >
          📋 Material Requests
        </button>
      </div>

      {/* Content Area */}
      <div className="bg-white rounded-lg shadow">
        {/* Barcode Scanner Tab */}
        {activeTab === 'barcode' && (
          <div className="p-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Left: Scanner */}
              <div>
                {/* Operation Selector */}
                <div className="mb-6 flex gap-4">
                  <button
                    onClick={() => setBarcodeOperation('receive')}
                    className={`flex-1 px-6 py-3 rounded-lg font-medium transition ${
                      barcodeOperation === 'receive'
                        ? 'bg-green-600 text-white shadow-lg'
                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                    }`}
                  >
                    📥 Receive Goods
                  </button>
                  <button
                    onClick={() => setBarcodeOperation('pick')}
                    className={`flex-1 px-6 py-3 rounded-lg font-medium transition ${
                      barcodeOperation === 'pick'
                        ? 'bg-blue-600 text-white shadow-lg'
                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                    }`}
                  >
                    📤 Pick Goods
                  </button>
                </div>

                {/* Barcode Scanner Component */}
                <BarcodeScanner
                  onScan={handleBarcodeScan}
                  operation={barcodeOperation}
                  location="warehouse"
                />

                {/* Transaction Form */}
                {scannedBarcode && (
                  <form onSubmit={handleTransactionSubmit} className="mt-6 bg-gray-50 border rounded-lg p-6">
                    <h4 className="font-semibold mb-4">Complete Transaction</h4>
                    
                    <div className="mb-4">
                      <label className="block text-sm font-medium mb-2">Scanned Barcode</label>
                      <input
                        type="text"
                        value={scannedBarcode}
                        readOnly
                        className="w-full border rounded-lg px-4 py-2 bg-white"
                      />
                    </div>

                    <div className="mb-4">
                      <label className="block text-sm font-medium mb-2">Quantity *</label>
                      <input
                        type="number"
                        value={transactionQty}
                        onChange={(e) => setTransactionQty(parseFloat(e.target.value))}
                        min="0"
                        step="any"
                        required
                        className="w-full border rounded-lg px-4 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      />
                    </div>

                    <div className="mb-4">
                      <label className="block text-sm font-medium mb-2">Notes (Optional)</label>
                      <textarea
                        value={transactionNotes}
                        onChange={(e) => setTransactionNotes(e.target.value)}
                        rows={3}
                        className="w-full border rounded-lg px-4 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        placeholder="Add any notes..."
                      />
                    </div>

                    <button
                      type="submit"
                      disabled={transactionLoading || transactionQty <= 0}
                      className="w-full bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition disabled:bg-gray-400 disabled:cursor-not-allowed"
                    >
                      {transactionLoading ? 'Processing...' : `Complete ${barcodeOperation === 'receive' ? 'Receiving' : 'Picking'}`}
                    </button>
                  </form>
                )}

                {/* Success Message */}
                {transactionSuccess && (
                  <div className="mt-6 bg-green-50 border border-green-200 rounded-lg p-4">
                    <h4 className="font-semibold text-green-800 mb-2">✓ Transaction Successful!</h4>
                    <p className="text-sm text-green-700">{transactionSuccess.message}</p>
                    <p className="text-xs text-green-600 mt-2">
                      Lot: {transactionSuccess.lot_number || transactionSuccess.picked_lots?.[0]?.lot_number}
                    </p>
                  </div>
                )}
              </div>

              {/* Right: Recent Scans History */}
              <div>
                <h3 className="text-xl font-bold mb-4">📋 Recent Scans</h3>
                <div className="space-y-3">
                  {barcodeHistory?.map((item: any) => (
                    <div key={item.id} className="border rounded-lg p-4 hover:bg-gray-50 transition">
                      <div className="flex justify-between items-start mb-2">
                        <div>
                          <span className={`inline-block px-2 py-1 rounded text-xs font-medium ${
                            item.operation === 'receive' ? 'bg-green-100 text-green-800' : 'bg-blue-100 text-blue-800'
                          }`}>
                            {item.operation === 'receive' ? '📥 Receive' : '📤 Pick'}
                          </span>
                          <p className="font-semibold mt-2">{item.product_name}</p>
                          <p className="text-sm text-gray-600">{item.barcode}</p>
                        </div>
                        <div className="text-right">
                          <p className="font-bold text-lg">{item.qty}</p>
                          <p className="text-xs text-gray-500">{new Date(item.timestamp).toLocaleString()}</p>
                        </div>
                      </div>
                      <div className="text-xs text-gray-500 border-t pt-2 mt-2">
                        <span>By: {item.user}</span> • <span>{item.location}</span>
                      </div>
                    </div>
                  ))}
                  
                  {(!barcodeHistory || barcodeHistory.length === 0) && (
                    <div className="text-center py-12 text-gray-400">
                      <p>No barcode scans yet</p>
                      <p className="text-sm mt-2">Start scanning to see history here</p>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}
        
        {/* Stock Inventory Tab */}
        {activeTab === 'inventory' && (
          <div>
            <div className="p-4 border-b flex justify-between items-center">
              <div className="flex gap-4 items-center">
                <input
                  type="text"
                  placeholder="Search products..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="px-4 py-2 border rounded-lg w-64 focus:ring-2 focus:ring-blue-500"
                />
                <label className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    checked={showLowStockOnly}
                    onChange={(e) => setShowLowStockOnly(e.target.checked)}
                    className="rounded"
                  />
                  <span className="text-sm text-gray-600">Low Stock Only</span>
                </label>
              </div>
            </div>
            
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Product Code</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Product Name</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Location</th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">On Hand</th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Reserved</th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Available</th>
                    <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase">UOM</th>
                    <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {filteredInventory.map((item) => (
                    <tr key={item.product_id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 text-sm font-medium text-gray-900">{item.product_code}</td>
                      <td className="px-6 py-4 text-sm text-gray-700">{item.product_name}</td>
                      <td className="px-6 py-4 text-sm text-gray-600">{item.location}</td>
                      <td className="px-6 py-4 text-sm text-right font-semibold text-gray-900">
                        {item.qty_on_hand.toLocaleString()}
                      </td>
                      <td className="px-6 py-4 text-sm text-right text-orange-600">
                        {item.qty_reserved.toLocaleString()}
                      </td>
                      <td className="px-6 py-4 text-sm text-right font-bold text-green-600">
                        {item.qty_available.toLocaleString()}
                      </td>
                      <td className="px-6 py-4 text-sm text-center text-gray-500">{item.uom}</td>
                      <td className="px-6 py-4 text-center">
                        {item.qty_available < item.qty_on_hand * 0.3 ? (
                          <span className="px-3 py-1 text-xs font-semibold rounded-full bg-red-100 text-red-800">
                            ⚠️ Low Stock
                          </span>
                        ) : (
                          <span className="px-3 py-1 text-xs font-semibold rounded-full bg-green-100 text-green-800">
                            ✅ Normal
                          </span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Stock Movements Tab */}
        {activeTab === 'movements' && (
          <div>
            <div className="p-4 border-b">
              <h3 className="font-semibold text-lg">Stock Movement History</h3>
              <p className="text-sm text-gray-600 mt-1">Track all stock movements and transfers</p>
            </div>
            
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date/Time</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Product</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">From Location</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">To Location</th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Quantity</th>
                    <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase">Move Type</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Created By</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {mockMovements.map((movement) => (
                    <tr key={movement.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 text-sm text-gray-600">
                        {new Date(movement.created_at).toLocaleString('id-ID')}
                      </td>
                      <td className="px-6 py-4">
                        <div className="text-sm font-medium text-gray-900">{movement.product_code}</div>
                        <div className="text-xs text-gray-500">{movement.product_name}</div>
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-700">{movement.from_location}</td>
                      <td className="px-6 py-4 text-sm text-gray-700">{movement.to_location}</td>
                      <td className="px-6 py-4 text-sm text-right font-semibold text-gray-900">
                        {movement.qty.toLocaleString()}
                      </td>
                      <td className="px-6 py-4 text-center">
                        <span className="px-3 py-1 text-xs font-semibold rounded-full bg-blue-100 text-blue-800">
                          {movement.move_type}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-600">{movement.created_by}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Inter-Dept Transfers Tab */}
        {activeTab === 'transfers' && (
          <div className="p-12 text-center">
            <div className="text-6xl mb-4">🚚</div>
            <p className="text-gray-500 text-lg">Inter-Department Transfers</p>
            <p className="text-gray-400 text-sm mt-2">
              View transfers between departments with QT-09 handshake protocol
            </p>
            <p className="text-gray-400 text-sm">Feature coming soon</p>
          </div>
        )}
      </div>

      {/* Note about mock data */}
      <div className="mt-4 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
        <p className="text-sm text-yellow-800">
          ℹ️ <strong>Note:</strong> Currently displaying mock data. Full warehouse integration coming soon with inventory endpoints.
        </p>
      </div>

      {/* Stock Adjustment Modal */}
      {showStockAdjustmentModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-lg p-6 max-w-md w-full mx-4">
            <h3 className="text-xl font-bold mb-4">📦 Stock Adjustment</h3>
            <form onSubmit={handleStockAdjustmentSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">Product *</label>
                <select
                  value={adjustmentData.product_id}
                  onChange={(e) => setAdjustmentData({...adjustmentData, product_id: e.target.value})}
                  className="mt-1 block w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-blue-500"
                  required
                >
                  <option value="">Select Product</option>
                  {mockInventory.map(item => (
                    <option key={item.product_id} value={item.product_id}>{item.product_code} - {item.product_name}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Adjustment Quantity *</label>
                <input
                  type="number"
                  value={adjustmentData.adjustment_qty}
                  onChange={(e) => setAdjustmentData({...adjustmentData, adjustment_qty: parseInt(e.target.value) || 0})}
                  className="mt-1 block w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-blue-500"
                  placeholder="Enter quantity (positive/negative)"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Reason *</label>
                <select
                  value={adjustmentData.reason}
                  onChange={(e) => setAdjustmentData({...adjustmentData, reason: e.target.value})}
                  className="mt-1 block w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-blue-500"
                  required
                >
                  <option value="">Select Reason</option>
                  <option value="stock_take">Physical Stock Take</option>
                  <option value="inventory_discrepancy">Inventory Discrepancy</option>
                  <option value="damage">Damage/Loss</option>
                  <option value="correction">Data Correction</option>
                  <option value="sample">Sample/Testing</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Notes</label>
                <textarea
                  value={adjustmentData.notes}
                  onChange={(e) => setAdjustmentData({...adjustmentData, notes: e.target.value})}
                  className="mt-1 block w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-blue-500"
                  placeholder="Additional notes"
                  rows={3}
                />
              </div>
              <div className="flex gap-2 pt-4">
                <button
                  type="submit"
                  disabled={adjustmentLoading}
                  className="flex-1 bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 disabled:bg-gray-400"
                >
                  {adjustmentLoading ? 'Processing...' : 'Submit Adjustment'}
                </button>
                <button
                  type="button"
                  onClick={() => setShowStockAdjustmentModal(false)}
                  className="flex-1 bg-gray-300 text-gray-700 py-2 rounded-lg hover:bg-gray-400"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Internal Transfer Modal */}
      {showInternalTransferModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-lg p-6 max-w-md w-full mx-4">
            <h3 className="text-xl font-bold mb-4">🔄 Internal Transfer</h3>
            <form onSubmit={handleInternalTransferSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">Product *</label>
                <select
                  value={transferData.product_id}
                  onChange={(e) => setTransferData({...transferData, product_id: e.target.value})}
                  className="mt-1 block w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-green-500"
                  required
                >
                  <option value="">Select Product</option>
                  {mockInventory.map(item => (
                    <option key={item.product_id} value={item.product_id}>{item.product_code} - {item.product_name}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">From Location *</label>
                <input
                  type="text"
                  value={transferData.from_location}
                  onChange={(e) => setTransferData({...transferData, from_location: e.target.value})}
                  className="mt-1 block w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-green-500"
                  placeholder="e.g., WH-RAW-A1"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">To Location *</label>
                <input
                  type="text"
                  value={transferData.to_location}
                  onChange={(e) => setTransferData({...transferData, to_location: e.target.value})}
                  className="mt-1 block w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-green-500"
                  placeholder="e.g., CUTTING-LINE1"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Quantity *</label>
                <input
                  type="number"
                  value={transferData.qty}
                  onChange={(e) => setTransferData({...transferData, qty: parseInt(e.target.value) || 0})}
                  className="mt-1 block w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-green-500"
                  placeholder="Enter quantity"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Reference (SPK/MO)</label>
                <input
                  type="text"
                  value={transferData.reference}
                  onChange={(e) => setTransferData({...transferData, reference: e.target.value})}
                  className="mt-1 block w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-green-500"
                  placeholder="Related SPK or MO number"
                />
              </div>
              <div className="flex gap-2 pt-4">
                <button
                  type="submit"
                  disabled={transferLoading}
                  className="flex-1 bg-green-600 text-white py-2 rounded-lg hover:bg-green-700 disabled:bg-gray-400"
                >
                  {transferLoading ? 'Processing...' : 'Submit Transfer'}
                </button>
                <button
                  type="button"
                  onClick={() => setShowInternalTransferModal(false)}
                  className="flex-1 bg-gray-300 text-gray-700 py-2 rounded-lg hover:bg-gray-400"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Material Requests Tab */}
      {activeTab === 'material-requests' && (
        <div className="p-6">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-xl font-bold text-gray-900">Material Requests</h2>
            <button
              onClick={() => setShowMaterialRequestModal(true)}
              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors flex items-center gap-2"
            >
              + Request Material
            </button>
          </div>
          <MaterialRequestsList 
            statusFilter="ALL"
            onApprovalChange={() => {
              // Refetch material requests
            }}
          />
        </div>
      )}
    </div>

    {/* Material Request Modal */}
    <MaterialRequestModal
      isOpen={showMaterialRequestModal}
      onClose={() => {
        setShowMaterialRequestModal(false);
        setMaterialRequestError(null);
      }}
      onSubmit={handleMaterialRequestSubmit}
      loading={materialRequestLoading}
      error={materialRequestError}
    />
    </>
  );
};

export default WarehousePage;
