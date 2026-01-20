import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import apiClient from '../api/client';
import BarcodeScanner from '../components/BarcodeScanner';

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
  const [activeTab, setActiveTab] = useState<'inventory' | 'movements' | 'barcode'>('inventory');
  const [searchTerm, setSearchTerm] = useState('');
  const [showLowStockOnly, setShowLowStockOnly] = useState(false);
  
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
    <div className="p-6">
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-800">🏭 Warehouse Management</h1>
          <p className="text-gray-600 mt-1">Stock inventory, movements, and transfers</p>
        </div>
        <div className="flex gap-3">
          <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
            📦 Stock Adjustment
          </button>
          <button className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors">
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
      <div className="flex gap-2 mb-6 border-b">
        <button
          onClick={() => setActiveTab('inventory')}
          className={`px-6 py-3 font-medium transition-colors ${
            activeTab === 'inventory'
              ? 'text-blue-600 border-b-2 border-blue-600'
              : 'text-gray-600 hover:text-gray-800'
          }`}
        >
          📦 Stock Inventory
        </button>
        <button
          onClick={() => setActiveTab('movements')}
          className={`px-6 py-3 font-medium transition-colors ${
            activeTab === 'movements'
              ? 'text-blue-600 border-b-2 border-blue-600'
              : 'text-gray-600 hover:text-gray-800'
          }`}
        >
          🔄 Stock Movements
        </button>
        <button
          onClick={() => setActiveTab('barcode')}
          className={`px-6 py-3 font-medium transition-colors ${
            activeTab === 'barcode'
              ? 'text-blue-600 border-b-2 border-blue-600'
              : 'text-gray-600 hover:text-gray-800'
          }`}
        >
          📷 Barcode Scanner
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
    </div>
  );
};

export default WarehousePage;
