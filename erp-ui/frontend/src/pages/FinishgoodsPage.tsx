import React, { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/api/client';
import BarcodeScanner from '../components/BarcodeScanner';

// Types
interface FinishGoodInventory {
  product_id: number;
  product_code: string;
  product_name: string;
  available_qty: number;
  reserved_qty: number;
  total_qty: number;
  uom: string;
  low_stock: boolean;
  min_stock: number;
}

interface ShipmentReadyProduct {
  mo_id: number;
  mo_number: string;
  product_code: string;
  product_name: string;
  completed_qty: number;
  available_stock: number;
  destination: string;
  delivery_week: number;
}

interface StockAgingItem {
  product_code: string;
  product_name: string;
  aging_category: string;
  qty: number;
  days_in_stock: number;
  location: string;
}

const FinishgoodsPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'inventory' | 'ready' | 'aging' | 'barcode'>('inventory');
  const [showReceiveModal, setShowReceiveModal] = useState(false);
  const [showShipmentModal, setShowShipmentModal] = useState(false);
  const [selectedProduct, setSelectedProduct] = useState<any>(null);
  const [lowStockOnly, setLowStockOnly] = useState(false);

  // Barcode states
  const [barcodeOperation, setBarcodeOperation] = useState<'receive' | 'pick'>('receive');
  const [scannedBarcode, setScannedBarcode] = useState('');
  const [transactionQty, setTransactionQty] = useState('');
  const [transactionNotes, setTransactionNotes] = useState('');
  const [transactionLoading, setTransactionLoading] = useState(false);
  const [transactionSuccess, setTransactionSuccess] = useState('');
  const [barcodeHistory, setBarcodeHistory] = useState<any[]>([]);

  // Form states
  const [receiveForm, setReceiveForm] = useState({
    transfer_slip_number: '',
    mo_id: '',
    product_id: '',
    qty_received: '',
    notes: ''
  });

  const [shipmentForm, setShipmentForm] = useState({
    shipment_number: '',
    destination: '',
    shipping_marks: '',
    products: [] as Array<{ product_id: number; qty: number }>
  });

  // Fetch inventory
  const { data: inventoryData, refetch: refetchInventory } = useQuery({
    queryKey: ['finishgoods-inventory', lowStockOnly],
    queryFn: async () => {
      const params = new URLSearchParams();
      if (lowStockOnly) params.append('low_stock_only', 'true');
      const response = await apiClient.get(`/finishgoods/inventory?${params}`);
      return response.data;
    },
    refetchInterval: 5000
  });

  // Fetch ready for shipment
  const { data: readyData, refetch: refetchReady } = useQuery({
    queryKey: ['finishgoods-ready'],
    queryFn: async () => {
      const response = await apiClient.get('/finishgoods/ready-for-shipment');
      return response.data;
    },
    refetchInterval: 5000
  });

  // Fetch stock aging
  const { data: agingData, refetch: refetchAging } = useQuery({
    queryKey: ['finishgoods-aging'],
    queryFn: async () => {
      const response = await apiClient.get('/finishgoods/stock-aging');
      return response.data;
    },
    refetchInterval: 10000
  });

  // Statistics
  const totalProducts = inventoryData?.inventory?.length || 0;
  const lowStockProducts = inventoryData?.inventory?.filter((item: FinishGoodInventory) => item.low_stock).length || 0;
  const readyToShip = readyData?.products?.length || 0;
  const totalStock = inventoryData?.inventory?.reduce((sum: number, item: FinishGoodInventory) => sum + item.total_qty, 0) || 0;

  // Handle receive from packing
  const handleReceiveSubmit = async () => {
    try {
      await apiClient.post('/finishgoods/receive-from-packing', {
        transfer_slip_number: receiveForm.transfer_slip_number,
        mo_id: parseInt(receiveForm.mo_id),
        product_id: parseInt(receiveForm.product_id),
        qty_received: parseFloat(receiveForm.qty_received),
        notes: receiveForm.notes
      });
      
      alert('✅ Successfully received from Packing!');
      setShowReceiveModal(false);
      setReceiveForm({
        transfer_slip_number: '',
        mo_id: '',
        product_id: '',
        qty_received: '',
        notes: ''
      });
      refetchInventory();
      refetchReady();
    } catch (error: any) {
      alert('❌ Error: ' + (error.response?.data?.detail || error.message));
    }
  };

  // Handle prepare shipment
  const handlePrepareShipment = async () => {
    try {
      await apiClient.post('/finishgoods/prepare-shipment', {
        shipment_number: shipmentForm.shipment_number,
        destination: shipmentForm.destination,
        shipping_marks: shipmentForm.shipping_marks,
        products: shipmentForm.products
      });
      
      alert('✅ Shipment prepared successfully!');
      setShowShipmentModal(false);
      setShipmentForm({
        shipment_number: '',
        destination: '',
        shipping_marks: '',
        products: []
      });
      refetchInventory();
    } catch (error: any) {
      alert('❌ Error: ' + (error.response?.data?.detail || error.message));
    }
  };

  // Barcode scanner handlers
  const handleBarcodeScan = (barcode: string) => {
    setScannedBarcode(barcode);
    setTransactionSuccess('');
  };

  const handleTransactionSubmit = async () => {
    if (!scannedBarcode || !transactionQty) {
      alert('⚠️ Please scan barcode and enter quantity');
      return;
    }

    setTransactionLoading(true);
    setTransactionSuccess('');

    try {
      const endpoint = barcodeOperation === 'receive' 
        ? '/barcode/receive' 
        : '/barcode/pick';
      
      const response = await apiClient.post(endpoint, {
        barcode: scannedBarcode,
        qty: parseFloat(transactionQty),
        location: 'finishgoods',
        notes: transactionNotes
      });

      setTransactionSuccess(
        barcodeOperation === 'receive'
          ? `✅ Received ${transactionQty} units successfully!`
          : `✅ Picked ${transactionQty} units successfully!`
      );

      // Reset form
      setScannedBarcode('');
      setTransactionQty('');
      setTransactionNotes('');

      // Refresh data
      refetchInventory();
      fetchBarcodeHistory();
    } catch (error: any) {
      alert('❌ Error: ' + (error.response?.data?.detail || error.message));
    } finally {
      setTransactionLoading(false);
    }
  };

  const fetchBarcodeHistory = async () => {
    try {
      const response = await apiClient.get('/barcode/history', {
        params: { location: 'finishgoods', limit: 10 }
      });
      setBarcodeHistory(response.data.history || []);
    } catch (error) {
      console.error('Failed to fetch barcode history:', error);
    }
  };

  // Fetch barcode history when tab changes
  useEffect(() => {
    if (activeTab === 'barcode') {
      fetchBarcodeHistory();
    }
  }, [activeTab]);

  // Get aging category color
  const getAgingColor = (category: string) => {
    switch (category) {
      case 'Fresh': return 'bg-green-100 text-green-800';
      case 'Normal': return 'bg-blue-100 text-blue-800';
      case 'Aging': return 'bg-yellow-100 text-yellow-800';
      case 'Old': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="p-6">
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-800">🏭 Finish Goods Warehouse</h1>
          <p className="text-gray-600 mt-1">Final product storage before shipment</p>
        </div>
        <div className="flex gap-3">
          <button
            onClick={() => setShowReceiveModal(true)}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            📦 Receive from Packing
          </button>
          <button
            onClick={() => setShowShipmentModal(true)}
            className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
          >
            🚢 Prepare Shipment
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
          <div className="text-3xl font-bold mt-2">{totalStock.toLocaleString()}</div>
          <div className="text-xs mt-1 opacity-75">Total Units</div>
        </div>
        
        <div className="bg-gradient-to-br from-orange-500 to-orange-600 rounded-lg p-5 text-white shadow-lg">
          <div className="text-sm opacity-90">Low Stock Alert</div>
          <div className="text-3xl font-bold mt-2">{lowStockProducts}</div>
          <div className="text-xs mt-1 opacity-75">Products below min</div>
        </div>
        
        <div className="bg-gradient-to-br from-green-500 to-green-600 rounded-lg p-5 text-white shadow-lg">
          <div className="text-sm opacity-90">Ready to Ship</div>
          <div className="text-3xl font-bold mt-2">{readyToShip}</div>
          <div className="text-xs mt-1 opacity-75">Completed MOs</div>
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
          📊 Inventory
        </button>
        <button
          onClick={() => setActiveTab('ready')}
          className={`px-6 py-3 font-medium transition-colors ${
            activeTab === 'ready'
              ? 'text-blue-600 border-b-2 border-blue-600'
              : 'text-gray-600 hover:text-gray-800'
          }`}
        >
          🚢 Ready to Ship
        </button>
        <button
          onClick={() => setActiveTab('aging')}
          className={`px-6 py-3 font-medium transition-colors ${
            activeTab === 'aging'
              ? 'text-blue-600 border-b-2 border-blue-600'
              : 'text-gray-600 hover:text-gray-800'
          }`}
        >
          ⏱️ Stock Aging
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
        {/* Inventory Tab */}
        {activeTab === 'inventory' && (
          <div>
            <div className="p-4 border-b flex justify-between items-center">
              <h3 className="font-semibold text-lg">Finish Goods Inventory</h3>
              <label className="flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={lowStockOnly}
                  onChange={(e) => setLowStockOnly(e.target.checked)}
                  className="rounded"
                />
                <span className="text-sm text-gray-600">Low Stock Only</span>
              </label>
            </div>
            
            {inventoryData?.inventory?.length > 0 ? (
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Product Code</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Product Name</th>
                      <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Available</th>
                      <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Reserved</th>
                      <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Total</th>
                      <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase">UOM</th>
                      <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase">Status</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200">
                    {inventoryData.inventory.map((item: FinishGoodInventory) => (
                      <tr key={item.product_id} className="hover:bg-gray-50">
                        <td className="px-6 py-4 text-sm font-medium text-gray-900">{item.product_code}</td>
                        <td className="px-6 py-4 text-sm text-gray-700">{item.product_name}</td>
                        <td className="px-6 py-4 text-sm text-right font-semibold text-gray-900">
                          {item.available_qty.toLocaleString()}
                        </td>
                        <td className="px-6 py-4 text-sm text-right text-orange-600">
                          {item.reserved_qty.toLocaleString()}
                        </td>
                        <td className="px-6 py-4 text-sm text-right font-bold text-blue-600">
                          {item.total_qty.toLocaleString()}
                        </td>
                        <td className="px-6 py-4 text-sm text-center text-gray-500">{item.uom}</td>
                        <td className="px-6 py-4 text-center">
                          {item.low_stock ? (
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
            ) : (
              <div className="p-12 text-center">
                <div className="text-6xl mb-4">📦</div>
                <p className="text-gray-500 text-lg">No inventory data available</p>
                <p className="text-gray-400 text-sm mt-2">Receive products from Packing department</p>
              </div>
            )}
          </div>
        )}

        {/* Ready to Ship Tab */}
        {activeTab === 'ready' && (
          <div>
            <div className="p-4 border-b">
              <h3 className="font-semibold text-lg">Products Ready for Shipment</h3>
              <p className="text-sm text-gray-600 mt-1">Completed MOs with available stock</p>
            </div>
            
            {readyData?.products?.length > 0 ? (
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">MO Number</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Product</th>
                      <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Completed Qty</th>
                      <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Available Stock</th>
                      <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase">Destination</th>
                      <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase">Week</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200">
                    {readyData.products.map((item: ShipmentReadyProduct) => (
                      <tr key={item.mo_id} className="hover:bg-gray-50">
                        <td className="px-6 py-4 text-sm font-medium text-blue-600">{item.mo_number}</td>
                        <td className="px-6 py-4">
                          <div className="text-sm font-medium text-gray-900">{item.product_code}</div>
                          <div className="text-xs text-gray-500">{item.product_name}</div>
                        </td>
                        <td className="px-6 py-4 text-sm text-right font-semibold text-gray-900">
                          {item.completed_qty.toLocaleString()}
                        </td>
                        <td className="px-6 py-4 text-sm text-right font-bold text-green-600">
                          {item.available_stock.toLocaleString()}
                        </td>
                        <td className="px-6 py-4 text-sm text-center">
                          <span className="px-3 py-1 text-xs font-semibold rounded-full bg-blue-100 text-blue-800">
                            {item.destination}
                          </span>
                        </td>
                        <td className="px-6 py-4 text-sm text-center text-gray-600">Week {item.delivery_week}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <div className="p-12 text-center">
                <div className="text-6xl mb-4">🚢</div>
                <p className="text-gray-500 text-lg">No products ready for shipment</p>
              </div>
            )}
          </div>
        )}

        {/* Stock Aging Tab */}
        {activeTab === 'aging' && (
          <div>
            <div className="p-4 border-b">
              <h3 className="font-semibold text-lg">Stock Aging Analysis</h3>
              <p className="text-sm text-gray-600 mt-1">
                Fresh (&lt;7d) | Normal (7-14d) | Aging (14-30d) | Old (&gt;30d)
              </p>
            </div>
            
            {agingData?.aging_analysis?.length > 0 ? (
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Product Code</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Product Name</th>
                      <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase">Category</th>
                      <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Quantity</th>
                      <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Days in Stock</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Location</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200">
                    {agingData.aging_analysis.map((item: StockAgingItem, index: number) => (
                      <tr key={index} className="hover:bg-gray-50">
                        <td className="px-6 py-4 text-sm font-medium text-gray-900">{item.product_code}</td>
                        <td className="px-6 py-4 text-sm text-gray-700">{item.product_name}</td>
                        <td className="px-6 py-4 text-center">
                          <span className={`px-3 py-1 text-xs font-semibold rounded-full ${getAgingColor(item.aging_category)}`}>
                            {item.aging_category}
                          </span>
                        </td>
                        <td className="px-6 py-4 text-sm text-right font-semibold text-gray-900">
                          {item.qty.toLocaleString()}
                        </td>
                        <td className="px-6 py-4 text-sm text-right text-gray-600">
                          {item.days_in_stock} days
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-600">{item.location}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <div className="p-12 text-center">
                <div className="text-6xl mb-4">⏱️</div>
                <p className="text-gray-500 text-lg">No aging data available</p>
              </div>
            )}
          </div>
        )}

        {/* Barcode Scanner Tab */}
        {activeTab === 'barcode' && (
          <div>
            <div className="p-4 border-b">
              <h3 className="font-semibold text-lg">📷 Barcode Scanner - Finishgoods</h3>
              <p className="text-sm text-gray-600 mt-1">
                Scan or enter barcode to receive or pick goods
              </p>
            </div>

            <div className="p-6">
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Left: Scanner */}
                <div>
                  {/* Operation Toggle */}
                  <div className="flex gap-2 mb-4">
                    <button
                      onClick={() => setBarcodeOperation('receive')}
                      className={`flex-1 py-2 px-4 rounded-lg font-medium transition-colors ${
                        barcodeOperation === 'receive'
                          ? 'bg-blue-600 text-white'
                          : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                      }`}
                    >
                      📥 Receive Goods
                    </button>
                    <button
                      onClick={() => setBarcodeOperation('pick')}
                      className={`flex-1 py-2 px-4 rounded-lg font-medium transition-colors ${
                        barcodeOperation === 'pick'
                          ? 'bg-green-600 text-white'
                          : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                      }`}
                    >
                      📤 Pick/Ship Goods
                    </button>
                  </div>

                  {/* Barcode Scanner Component */}
                  <BarcodeScanner
                    onScan={handleBarcodeScan}
                    operation={barcodeOperation}
                    location="finishgoods"
                  />

                  {/* Transaction Form */}
                  {scannedBarcode && (
                    <div className="mt-6 p-4 bg-gray-50 rounded-lg space-y-4">
                      <h4 className="font-semibold text-gray-800">Transaction Details</h4>
                      
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Scanned Barcode
                        </label>
                        <input
                          type="text"
                          value={scannedBarcode}
                          readOnly
                          className="w-full px-3 py-2 bg-white border rounded-lg text-gray-700"
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Quantity *
                        </label>
                        <input
                          type="number"
                          value={transactionQty}
                          onChange={(e) => setTransactionQty(e.target.value)}
                          className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                          placeholder="Enter quantity"
                          step="0.01"
                          min="0.01"
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Notes (Optional)
                        </label>
                        <textarea
                          value={transactionNotes}
                          onChange={(e) => setTransactionNotes(e.target.value)}
                          className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                          rows={2}
                          placeholder="Additional notes..."
                        />
                      </div>

                      <button
                        onClick={handleTransactionSubmit}
                        disabled={transactionLoading || !transactionQty}
                        className={`w-full py-2 px-4 rounded-lg font-medium transition-colors ${
                          transactionLoading || !transactionQty
                            ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                            : barcodeOperation === 'receive'
                            ? 'bg-blue-600 text-white hover:bg-blue-700'
                            : 'bg-green-600 text-white hover:bg-green-700'
                        }`}
                      >
                        {transactionLoading
                          ? 'Processing...'
                          : barcodeOperation === 'receive'
                          ? '📥 Confirm Receive'
                          : '📤 Confirm Pick'}
                      </button>

                      {transactionSuccess && (
                        <div className="p-3 bg-green-50 border border-green-200 rounded-lg">
                          <p className="text-green-800 text-sm">{transactionSuccess}</p>
                        </div>
                      )}
                    </div>
                  )}
                </div>

                {/* Right: Recent History */}
                <div>
                  <h4 className="font-semibold text-gray-800 mb-3">📋 Recent Transactions</h4>
                  <div className="space-y-2 max-h-[600px] overflow-y-auto">
                    {barcodeHistory.length > 0 ? (
                      barcodeHistory.map((item: any, index: number) => (
                        <div key={index} className="p-3 bg-white border rounded-lg">
                          <div className="flex justify-between items-start mb-2">
                            <span className="font-mono text-sm font-semibold text-gray-900">
                              {item.barcode}
                            </span>
                            <span className={`px-2 py-1 text-xs font-semibold rounded ${
                              item.operation === 'receive'
                                ? 'bg-blue-100 text-blue-800'
                                : 'bg-green-100 text-green-800'
                            }`}>
                              {item.operation === 'receive' ? '📥 Receive' : '📤 Pick'}
                            </span>
                          </div>
                          <div className="text-sm text-gray-600 space-y-1">
                            <div className="flex justify-between">
                              <span>Product:</span>
                              <span className="font-medium text-gray-900">{item.product_name}</span>
                            </div>
                            <div className="flex justify-between">
                              <span>Quantity:</span>
                              <span className="font-medium text-gray-900">{item.qty}</span>
                            </div>
                            <div className="flex justify-between">
                              <span>Time:</span>
                              <span className="text-gray-500">
                                {new Date(item.timestamp).toLocaleString()}
                              </span>
                            </div>
                            {item.notes && (
                              <div className="mt-2 pt-2 border-t">
                                <p className="text-xs text-gray-500">{item.notes}</p>
                              </div>
                            )}
                          </div>
                        </div>
                      ))
                    ) : (
                      <div className="p-8 text-center">
                        <div className="text-4xl mb-2">📋</div>
                        <p className="text-gray-500 text-sm">No recent transactions</p>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Receive from Packing Modal */}
      {showReceiveModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h3 className="text-xl font-bold mb-4">📦 Receive from Packing</h3>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Transfer Slip Number *
                </label>
                <input
                  type="text"
                  value={receiveForm.transfer_slip_number}
                  onChange={(e) => setReceiveForm({...receiveForm, transfer_slip_number: e.target.value})}
                  className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                  placeholder="TSL-PACK-001"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Manufacturing Order ID *
                </label>
                <input
                  type="number"
                  value={receiveForm.mo_id}
                  onChange={(e) => setReceiveForm({...receiveForm, mo_id: e.target.value})}
                  className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                  placeholder="123"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Product ID *
                </label>
                <input
                  type="number"
                  value={receiveForm.product_id}
                  onChange={(e) => setReceiveForm({...receiveForm, product_id: e.target.value})}
                  className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                  placeholder="456"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Quantity Received *
                </label>
                <input
                  type="number"
                  value={receiveForm.qty_received}
                  onChange={(e) => setReceiveForm({...receiveForm, qty_received: e.target.value})}
                  className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                  placeholder="1000"
                  step="0.01"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Notes (Optional)
                </label>
                <textarea
                  value={receiveForm.notes}
                  onChange={(e) => setReceiveForm({...receiveForm, notes: e.target.value})}
                  className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                  rows={3}
                  placeholder="Additional notes..."
                />
              </div>
            </div>
            
            <div className="flex gap-3 mt-6">
              <button
                onClick={() => setShowReceiveModal(false)}
                className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                onClick={handleReceiveSubmit}
                className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                Receive
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Prepare Shipment Modal */}
      {showShipmentModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h3 className="text-xl font-bold mb-4">🚢 Prepare Shipment</h3>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Shipment Number *
                </label>
                <input
                  type="text"
                  value={shipmentForm.shipment_number}
                  onChange={(e) => setShipmentForm({...shipmentForm, shipment_number: e.target.value})}
                  className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-green-500"
                  placeholder="SHIP-2026-001"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Destination *
                </label>
                <input
                  type="text"
                  value={shipmentForm.destination}
                  onChange={(e) => setShipmentForm({...shipmentForm, destination: e.target.value})}
                  className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-green-500"
                  placeholder="DE, US, JP"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Shipping Marks *
                </label>
                <textarea
                  value={shipmentForm.shipping_marks}
                  onChange={(e) => setShipmentForm({...shipmentForm, shipping_marks: e.target.value})}
                  className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-green-500"
                  rows={2}
                  placeholder="Container marks, handling instructions..."
                />
              </div>
              
              <div className="p-3 bg-blue-50 rounded-lg">
                <p className="text-sm text-blue-800">
                  ℹ️ Product selection will be added in next enhancement
                </p>
              </div>
            </div>
            
            <div className="flex gap-3 mt-6">
              <button
                onClick={() => setShowShipmentModal(false)}
                className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                onClick={handlePrepareShipment}
                className="flex-1 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
              >
                Prepare
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default FinishgoodsPage;
