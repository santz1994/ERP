/**
 * Stock Management UI - FIFO Tracking & Lot Management
 * Priority 3.1: Warehouse Integration
 * Created: 2026-02-04
 */

import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/api/client';
import { 
  Package, 
  TrendingUp, 
  TrendingDown, 
  Calendar,
  MapPin,
  Filter,
  Search,
  AlertTriangle,
  CheckCircle,
  Clock
} from 'lucide-react';

interface StockQuant {
  id: number;
  product_id: number;
  product_code: string;
  product_name: string;
  location_id: number;
  location_name: string;
  lot_id?: number;
  lot_number?: string;
  quantity: number;
  reserved_quantity: number;
  available_quantity: number;
  uom: string;
  fifo_date: string;
  expiry_date?: string;
  owner_id?: number;
  owner_name?: string;
  package_id?: number;
  in_date: string;
  created_at: string;
}

interface StockMove {
  id: number;
  product_id: number;
  product_code: string;
  product_name: string;
  quantity: number;
  uom: string;
  location_id: number;
  location_dest_id: number;
  location_name: string;
  location_dest_name: string;
  move_type: string;
  state: string;
  reference?: string;
  date: string;
  created_at: string;
}

interface StockManagementProps {
  locationFilter?: number;
  productFilter?: number;
}

export const StockManagement: React.FC<StockManagementProps> = ({
  locationFilter,
  productFilter
}) => {
  const queryClient = useQueryClient();
  const [selectedLocation, setSelectedLocation] = useState<number | undefined>(locationFilter);
  const [selectedProduct, setSelectedProduct] = useState<number | undefined>(productFilter);
  const [searchTerm, setSearchTerm] = useState('');
  const [viewMode, setViewMode] = useState<'stock' | 'moves'>('stock');
  const [showLowStock, setShowLowStock] = useState(false);

  // Fetch Locations
  const { data: locations } = useQuery({
    queryKey: ['warehouse-locations'],
    queryFn: async () => {
      const response = await apiClient.get('/warehouse/locations');
      return response.data;
    }
  });

  // Fetch Stock Quants
  const { data: stockQuants, isLoading: stockLoading } = useQuery({
    queryKey: ['stock-quants', selectedLocation, selectedProduct, searchTerm, showLowStock],
    queryFn: async () => {
      const params = new URLSearchParams();
      if (selectedLocation) params.append('location_id', selectedLocation.toString());
      if (selectedProduct) params.append('product_id', selectedProduct.toString());
      if (searchTerm) params.append('search', searchTerm);
      if (showLowStock) params.append('low_stock', 'true');
      const response = await apiClient.get(`/warehouse/stock-quants?${params}`);
      return response.data as StockQuant[];
    },
    refetchInterval: 10000 // Refresh every 10 seconds
  });

  // Fetch Stock Moves
  const { data: stockMoves, isLoading: movesLoading } = useQuery({
    queryKey: ['stock-moves', selectedProduct],
    queryFn: async () => {
      const params = new URLSearchParams();
      if (selectedProduct) params.append('product_id', selectedProduct.toString());
      params.append('limit', '50');
      const response = await apiClient.get(`/warehouse/stock-moves?${params}`);
      return response.data as StockMove[];
    },
    enabled: viewMode === 'moves'
  });

  // Fetch Products
  const { data: products } = useQuery({
    queryKey: ['products-for-stock'],
    queryFn: async () => {
      const response = await apiClient.get('/admin/products');
      return response.data;
    }
  });

  const getStockStatus = (quant: StockQuant) => {
    if (quant.available_quantity <= 0) {
      return { label: 'Out of Stock', color: 'bg-red-100 text-red-800 border-red-300', icon: <AlertTriangle size={14} /> };
    } else if (quant.available_quantity < 10) {
      return { label: 'Low Stock', color: 'bg-yellow-100 text-yellow-800 border-yellow-300', icon: <Clock size={14} /> };
    } else {
      return { label: 'In Stock', color: 'bg-green-100 text-green-800 border-green-300', icon: <CheckCircle size={14} /> };
    }
  };

  const getFIFOAge = (fifoDate: string): number => {
    const date = new Date(fifoDate);
    const now = new Date();
    const diffTime = Math.abs(now.getTime() - date.getTime());
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return diffDays;
  };

  const totalStock = stockQuants?.reduce((sum, q) => sum + q.quantity, 0) || 0;
  const totalAvailable = stockQuants?.reduce((sum, q) => sum + q.available_quantity, 0) || 0;
  const totalReserved = stockQuants?.reduce((sum, q) => sum + q.reserved_quantity, 0) || 0;

  return (
    <div className="space-y-6">
      {/* Header & Controls */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <div className="bg-green-100 p-3 rounded-lg">
              <Package className="text-green-600" size={32} />
            </div>
            <div>
              <h2 className="text-2xl font-bold text-gray-900">Stock Management</h2>
              <p className="text-gray-600">FIFO tracking & lot management</p>
            </div>
          </div>

          {/* View Mode Toggle */}
          <div className="flex gap-2">
            <button
              onClick={() => setViewMode('stock')}
              className={`px-4 py-2 rounded-lg transition-colors ${
                viewMode === 'stock'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              Stock Quants
            </button>
            <button
              onClick={() => setViewMode('moves')}
              className={`px-4 py-2 rounded-lg transition-colors ${
                viewMode === 'moves'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              Stock Moves
            </button>
          </div>
        </div>

        {/* Filters */}
        <div className="grid grid-cols-3 gap-4 mb-4">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={18} />
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search products..."
              className="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          <select
            value={selectedLocation || ''}
            onChange={(e) => setSelectedLocation(e.target.value ? Number(e.target.value) : undefined)}
            className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="">All Locations</option>
            {locations?.map((loc: any) => (
              <option key={loc.id} value={loc.id}>{loc.name}</option>
            ))}
          </select>

          <select
            value={selectedProduct || ''}
            onChange={(e) => setSelectedProduct(e.target.value ? Number(e.target.value) : undefined)}
            className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="">All Products</option>
            {products?.map((prod: any) => (
              <option key={prod.id} value={prod.id}>
                [{prod.code}] {prod.name}
              </option>
            ))}
          </select>
        </div>

        {/* Low Stock Toggle */}
        <div className="flex items-center gap-2">
          <input
            type="checkbox"
            id="lowStockFilter"
            checked={showLowStock}
            onChange={(e) => setShowLowStock(e.target.checked)}
            className="w-4 h-4 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
          />
          <label htmlFor="lowStockFilter" className="text-sm text-gray-700 cursor-pointer">
            Show only low stock items
          </label>
        </div>

        {/* Summary Stats */}
        {viewMode === 'stock' && (
          <div className="grid grid-cols-3 gap-4 mt-6">
            <div className="bg-blue-50 rounded-lg p-3 text-center">
              <div className="text-2xl font-bold text-blue-600">{totalStock.toFixed(2)}</div>
              <div className="text-xs text-gray-600">Total Stock</div>
            </div>
            <div className="bg-green-50 rounded-lg p-3 text-center">
              <div className="text-2xl font-bold text-green-600">{totalAvailable.toFixed(2)}</div>
              <div className="text-xs text-gray-600">Available</div>
            </div>
            <div className="bg-orange-50 rounded-lg p-3 text-center">
              <div className="text-2xl font-bold text-orange-600">{totalReserved.toFixed(2)}</div>
              <div className="text-xs text-gray-600">Reserved</div>
            </div>
          </div>
        )}
      </div>

      {/* Stock Quants View */}
      {viewMode === 'stock' && (
        <div className="bg-white rounded-lg shadow-md overflow-hidden">
          {stockLoading ? (
            <div className="p-12 text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
              <p className="text-gray-600">Loading stock data...</p>
            </div>
          ) : stockQuants?.length === 0 ? (
            <div className="p-12 text-center">
              <Package className="mx-auto text-gray-400 mb-4" size={64} />
              <h4 className="text-lg font-semibold text-gray-900 mb-2">No Stock Found</h4>
              <p className="text-gray-600">Try adjusting your filters</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50 border-b-2 border-gray-200">
                  <tr>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Product</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Location</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Lot/Batch</th>
                    <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Total Qty</th>
                    <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Reserved</th>
                    <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Available</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">FIFO Age</th>
                    <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {stockQuants?.map((quant) => {
                    const status = getStockStatus(quant);
                    const fifoAge = getFIFOAge(quant.fifo_date);
                    
                    return (
                      <tr key={quant.id} className="hover:bg-gray-50">
                        <td className="px-4 py-3">
                          <div>
                            <div className="font-semibold text-gray-900">{quant.product_code}</div>
                            <div className="text-sm text-gray-600 truncate max-w-xs">{quant.product_name}</div>
                          </div>
                        </td>
                        <td className="px-4 py-3 text-sm">
                          <div className="flex items-center gap-1 text-gray-700">
                            <MapPin size={14} />
                            {quant.location_name}
                          </div>
                        </td>
                        <td className="px-4 py-3 text-sm">
                          {quant.lot_number ? (
                            <span className="px-2 py-1 bg-purple-100 text-purple-800 rounded text-xs font-medium">
                              {quant.lot_number}
                            </span>
                          ) : (
                            <span className="text-gray-400">-</span>
                          )}
                        </td>
                        <td className="px-4 py-3 text-right">
                          <div className="font-bold text-gray-900">{quant.quantity.toFixed(2)}</div>
                          <div className="text-xs text-gray-600">{quant.uom}</div>
                        </td>
                        <td className="px-4 py-3 text-right">
                          <div className="font-semibold text-orange-600">{quant.reserved_quantity.toFixed(2)}</div>
                          <div className="text-xs text-gray-600">{quant.uom}</div>
                        </td>
                        <td className="px-4 py-3 text-right">
                          <div className="font-bold text-green-600">{quant.available_quantity.toFixed(2)}</div>
                          <div className="text-xs text-gray-600">{quant.uom}</div>
                        </td>
                        <td className="px-4 py-3 text-sm">
                          <div className="flex items-center gap-1 text-gray-700">
                            <Calendar size={14} />
                            {fifoAge} days
                          </div>
                          <div className="text-xs text-gray-500">
                            {new Date(quant.fifo_date).toLocaleDateString()}
                          </div>
                        </td>
                        <td className="px-4 py-3 text-center">
                          <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-semibold border ${status.color}`}>
                            {status.icon}
                            {status.label}
                          </span>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {/* Stock Moves View */}
      {viewMode === 'moves' && (
        <div className="bg-white rounded-lg shadow-md overflow-hidden">
          {movesLoading ? (
            <div className="p-12 text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
              <p className="text-gray-600">Loading stock moves...</p>
            </div>
          ) : stockMoves?.length === 0 ? (
            <div className="p-12 text-center">
              <TrendingUp className="mx-auto text-gray-400 mb-4" size={64} />
              <h4 className="text-lg font-semibold text-gray-900 mb-2">No Stock Moves Found</h4>
              <p className="text-gray-600">No recent stock movements</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50 border-b-2 border-gray-200">
                  <tr>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Product</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">From → To</th>
                    <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Quantity</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Reference</th>
                    <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase">State</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {stockMoves?.map((move) => (
                    <tr key={move.id} className="hover:bg-gray-50">
                      <td className="px-4 py-3 text-sm text-gray-600">
                        {new Date(move.date).toLocaleString()}
                      </td>
                      <td className="px-4 py-3">
                        <div>
                          <div className="font-semibold text-gray-900">{move.product_code}</div>
                          <div className="text-sm text-gray-600 truncate max-w-xs">{move.product_name}</div>
                        </div>
                      </td>
                      <td className="px-4 py-3 text-sm">
                        <div className="flex items-center gap-2">
                          <span className="text-gray-700">{move.location_name}</span>
                          <TrendingUp size={14} className="text-blue-600" />
                          <span className="text-gray-700">{move.location_dest_name}</span>
                        </div>
                      </td>
                      <td className="px-4 py-3 text-right">
                        <div className="font-bold text-gray-900">{move.quantity.toFixed(2)}</div>
                        <div className="text-xs text-gray-600">{move.uom}</div>
                      </td>
                      <td className="px-4 py-3 text-sm">
                        <span className={`px-2 py-1 rounded text-xs font-medium ${
                          move.move_type === 'IN' ? 'bg-green-100 text-green-800' :
                          move.move_type === 'OUT' ? 'bg-red-100 text-red-800' :
                          'bg-blue-100 text-blue-800'
                        }`}>
                          {move.move_type}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-700">
                        {move.reference || '-'}
                      </td>
                      <td className="px-4 py-3 text-center">
                        <span className={`px-2 py-1 rounded text-xs font-semibold ${
                          move.state === 'DONE' ? 'bg-green-100 text-green-800' :
                          move.state === 'IN_PROGRESS' ? 'bg-blue-100 text-blue-800' :
                          'bg-gray-100 text-gray-800'
                        }`}>
                          {move.state}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
