import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { api } from '../../api';
import { Card, CardHeader, CardTitle, CardContent } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Badge } from '../../components/ui/badge';
import { cn, formatNumber, getStockStatusColor } from '../../lib/utils';

/**
 * Material Stock Page - Warehouse Module
 * 
 * Features:
 * - Material stock list with 4-level color coding
 * - Color coding: Green (>50%), Yellow (15-50%), Red (<15%), Black (negative/debt)
 * - Filter by material type, supplier, low stock alert
 * - Search by material code/name
 * - Quick actions: Receipt, Issue, Adjust
 * - Real-time stock updates
 * - Low stock alerts (Top 10 critical)
 * 
 * Material Debt:
 * - Negative stock = Production consumed before receipt (allowed with approval)
 * - Black color indicates debt requiring reconciliation
 */

interface MaterialStock {
  id: number;
  materialCode: string;
  materialName: string;
  materialType: 'FABRIC' | 'THREAD' | 'LABEL' | 'ACCESSORIES' | 'FILLING';
  currentStock: number;
  minStock: number;
  maxStock: number;
  uom: string;
  supplierName: string;
  avgPrice: number;
  lastReceiptDate?: string;
  lastIssueDate?: string;
  status: 'ABUNDANT' | 'SUFFICIENT' | 'LOW' | 'CRITICAL' | 'DEBT';
  stockValue: number;
}

const MATERIAL_TYPES = [
  { value: 'FABRIC', label: 'Fabric (KOHAIR)', icon: '🧵' },
  { value: 'THREAD', label: 'Thread', icon: '🪡' },
  { value: 'LABEL', label: 'Label', icon: '🏷️' },
  { value: 'ACCESSORIES', label: 'Accessories', icon: '📌' },
  { value: 'FILLING', label: 'Filling', icon: '🧺' },
];

export default function MaterialStockPage() {
  const navigate = useNavigate();
  const [filters, setFilters] = useState<{
    type?: string;
    status?: string;
    search?: string;
  }>({});

  // Fetch material stock
  const { data: materials, isLoading } = useQuery<MaterialStock[]>({
    queryKey: ['material-stock', filters],
    queryFn: () => api.warehouse.getMaterialStock(filters),
    refetchInterval: 60000, // Refresh every minute
  });

  // Get status badge
  const getStatusBadge = (status: MaterialStock['status']) => {
    const configs = {
      ABUNDANT: { variant: 'success' as const, label: '✅ Abundant', color: 'text-green-700' },
      SUFFICIENT: { variant: 'info' as const, label: '🟢 Sufficient', color: 'text-blue-700' },
      LOW: { variant: 'warning' as const, label: '🟡 Low Stock', color: 'text-yellow-700' },
      CRITICAL: { variant: 'error' as const, label: '🔴 Critical', color: 'text-red-700' },
      DEBT: { variant: 'error' as const, label: '⚫ DEBT', color: 'text-black' },
    };
    return configs[status];
  };

  // Get stock percentage
  const getStockPercentage = (current: number, min: number, max: number) => {
    if (current < 0) return -1; // Debt
    return ((current - min) / (max - min)) * 100;
  };

  // Get row color based on stock level
  const getRowColor = (material: MaterialStock) => {
    const percent = getStockPercentage(material.currentStock, material.minStock, material.maxStock);
    if (percent < 0) return 'bg-black bg-opacity-5'; // Debt (Black)
    if (percent < 15) return 'bg-red-50'; // Critical (Red)
    if (percent < 50) return 'bg-yellow-50'; // Low (Yellow)
    return 'bg-green-50'; // Sufficient/Abundant (Green)
  };

  // Calculate totals
  const totalStockValue = materials?.reduce((sum, m) => sum + m.stockValue, 0) || 0;
  const lowStockCount = materials?.filter(m => m.status === 'LOW' || m.status === 'CRITICAL').length || 0;
  const debtCount = materials?.filter(m => m.status === 'DEBT').length || 0;

  return (
    <div className="p-6 space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">📦 Material Stock Management</h1>
          <p className="text-gray-600 mt-1">
            Monitor and manage material inventory with 4-level color coding
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="success" onClick={() => navigate('/warehouse/material/receipt')}>
            📥 Material Receipt
          </Button>
          <Button variant="primary" onClick={() => navigate('/warehouse/material/issue')}>
            📤 Issue to Production
          </Button>
        </div>
      </div>

      {/* Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card variant="bordered">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Total Materials</p>
                <p className="text-2xl font-bold mt-1">{materials?.length || 0}</p>
              </div>
              <div className="w-12 h-12 rounded-full bg-blue-500 flex items-center justify-center text-white text-2xl">
                📦
              </div>
            </div>
          </CardContent>
        </Card>

        <Card variant="bordered">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Total Stock Value</p>
                <p className="text-2xl font-bold mt-1">${formatNumber(totalStockValue)}</p>
              </div>
              <div className="w-12 h-12 rounded-full bg-green-500 flex items-center justify-center text-white text-2xl">
                💰
              </div>
            </div>
          </CardContent>
        </Card>

        <Card variant="bordered">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Low Stock Alert</p>
                <p className="text-2xl font-bold mt-1 text-yellow-600">{lowStockCount}</p>
              </div>
              <div className="w-12 h-12 rounded-full bg-yellow-500 flex items-center justify-center text-white text-2xl">
                ⚠️
              </div>
            </div>
          </CardContent>
        </Card>

        <Card variant="bordered">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Material Debt</p>
                <p className="text-2xl font-bold mt-1 text-black">{debtCount}</p>
              </div>
              <div className="w-12 h-12 rounded-full bg-black flex items-center justify-center text-white text-2xl">
                ⚫
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Filters */}
      <Card variant="bordered">
        <CardHeader>
          <CardTitle>🔍 Filters</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            {/* Material Type */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Material Type</label>
              <select
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                value={filters.type || ''}
                onChange={(e) => setFilters(prev => ({ ...prev, type: e.target.value || undefined }))}
              >
                <option value="">All Types</option>
                {MATERIAL_TYPES.map(type => (
                  <option key={type.value} value={type.value}>
                    {type.icon} {type.label}
                  </option>
                ))}
              </select>
            </div>

            {/* Status */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Stock Status</label>
              <select
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                value={filters.status || ''}
                onChange={(e) => setFilters(prev => ({ ...prev, status: e.target.value || undefined }))}
              >
                <option value="">All Status</option>
                <option value="ABUNDANT">✅ Abundant</option>
                <option value="SUFFICIENT">🟢 Sufficient</option>
                <option value="LOW">🟡 Low Stock</option>
                <option value="CRITICAL">🔴 Critical</option>
                <option value="DEBT">⚫ DEBT</option>
              </select>
            </div>

            {/* Search */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Search</label>
              <input
                type="text"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Material code or name..."
                value={filters.search || ''}
                onChange={(e) => setFilters(prev => ({ ...prev, search: e.target.value || undefined }))}
              />
            </div>

            {/* Actions */}
            <div className="flex items-end gap-2">
              <Button 
                variant="secondary" 
                onClick={() => setFilters({})}
                className="flex-1"
              >
                Clear
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Material Stock Table */}
      <Card variant="bordered">
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>📋 Material Inventory</CardTitle>
            <Badge variant="info">
              {isLoading ? 'Loading...' : `${materials?.length || 0} materials`}
            </Badge>
          </div>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="text-center py-12">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto"></div>
              <p className="text-gray-600 mt-4">Loading material stock...</p>
            </div>
          ) : materials && materials.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="bg-gray-50 border-b">
                  <tr>
                    <th className="px-4 py-3 text-left font-semibold text-gray-700">Material</th>
                    <th className="px-4 py-3 text-center font-semibold text-gray-700">Type</th>
                    <th className="px-4 py-3 text-center font-semibold text-gray-700">Current Stock</th>
                    <th className="px-4 py-3 text-center font-semibold text-gray-700">Min / Max</th>
                    <th className="px-4 py-3 text-center font-semibold text-gray-700">Stock Level</th>
                    <th className="px-4 py-3 text-center font-semibold text-gray-700">Status</th>
                    <th className="px-4 py-3 text-center font-semibold text-gray-700">Value</th>
                    <th className="px-4 py-3 text-center font-semibold text-gray-700">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {materials.map((material) => {
                    const stockPercent = getStockPercentage(material.currentStock, material.minStock, material.maxStock);
                    const statusConfig = getStatusBadge(material.status);
                    
                    return (
                      <tr key={material.id} className={cn('hover:bg-opacity-70 transition-colors', getRowColor(material))}>
                        {/* Material */}
                        <td className="px-4 py-4">
                          <div className="font-semibold text-gray-900">{material.materialCode}</div>
                          <div className="text-xs text-gray-600 mt-1">{material.materialName}</div>
                          <div className="text-xs text-gray-500 mt-1">Supplier: {material.supplierName}</div>
                        </td>

                        {/* Type */}
                        <td className="px-4 py-4 text-center">
                          <Badge variant="secondary" size="sm">
                            {MATERIAL_TYPES.find(t => t.value === material.materialType)?.icon} {material.materialType}
                          </Badge>
                        </td>

                        {/* Current Stock */}
                        <td className="px-4 py-4 text-center">
                          <div className={cn(
                            'text-xl font-bold',
                            material.currentStock < 0 ? 'text-black' :
                            material.status === 'CRITICAL' ? 'text-red-700' :
                            material.status === 'LOW' ? 'text-yellow-700' :
                            'text-green-700'
                          )}>
                            {formatNumber(material.currentStock)}
                          </div>
                          <div className="text-xs text-gray-600 mt-1">{material.uom}</div>
                        </td>

                        {/* Min / Max */}
                        <td className="px-4 py-4 text-center text-sm text-gray-700">
                          <div>Min: {formatNumber(material.minStock)}</div>
                          <div>Max: {formatNumber(material.maxStock)}</div>
                        </td>

                        {/* Stock Level Bar */}
                        <td className="px-4 py-4">
                          <div className="w-32 mx-auto">
                            <div className="w-full bg-gray-200 rounded-full h-3">
                              <div
                                className={cn(
                                  'h-3 rounded-full transition-all',
                                  material.currentStock < 0 ? 'bg-black' :
                                  stockPercent < 15 ? 'bg-red-500' :
                                  stockPercent < 50 ? 'bg-yellow-500' :
                                  'bg-green-500'
                                )}
                                style={{ 
                                  width: material.currentStock < 0 ? '100%' : `${Math.min(Math.max(stockPercent, 0), 100)}%` 
                                }}
                              />
                            </div>
                            <div className="text-xs text-center mt-1 font-semibold">
                              {material.currentStock < 0 ? 'DEBT' : `${stockPercent.toFixed(0)}%`}
                            </div>
                          </div>
                        </td>

                        {/* Status */}
                        <td className="px-4 py-4 text-center">
                          <Badge variant={statusConfig.variant}>
                            {statusConfig.label}
                          </Badge>
                        </td>

                        {/* Value */}
                        <td className="px-4 py-4 text-center">
                          <div className="font-semibold text-gray-900">
                            ${formatNumber(material.stockValue)}
                          </div>
                          <div className="text-xs text-gray-600 mt-1">
                            @${material.avgPrice.toFixed(2)}/{material.uom}
                          </div>
                        </td>

                        {/* Actions */}
                        <td className="px-4 py-4">
                          <div className="flex items-center justify-center gap-1">
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => navigate(`/warehouse/material/${material.id}`)}
                              title="View Details"
                            >
                              👁️
                            </Button>
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => navigate(`/warehouse/material/issue?materialId=${material.id}`)}
                              title="Issue to Production"
                            >
                              📤
                            </Button>
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => navigate(`/warehouse/material/adjust?materialId=${material.id}`)}
                              title="Stock Adjustment"
                            >
                              ⚙️
                            </Button>
                          </div>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="text-center py-12">
              <div className="text-gray-400 text-6xl mb-4">📦</div>
              <h3 className="text-lg font-semibold text-gray-700 mb-2">No Materials Found</h3>
              <p className="text-gray-600 mb-4">
                {Object.keys(filters).length > 0
                  ? 'Try adjusting your filters.'
                  : 'Start by receiving materials from purchase orders.'}
              </p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Color Coding Legend */}
      <Card variant="bordered">
        <CardHeader>
          <CardTitle>ℹ️ Stock Level Color Coding</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="flex items-center gap-3 p-3 bg-green-50 rounded-lg border border-green-200">
              <div className="w-6 h-6 bg-green-500 rounded"></div>
              <div>
                <p className="font-semibold text-green-800">Green (&gt;50%)</p>
                <p className="text-xs text-gray-600">Sufficient/Abundant</p>
              </div>
            </div>
            <div className="flex items-center gap-3 p-3 bg-yellow-50 rounded-lg border border-yellow-200">
              <div className="w-6 h-6 bg-yellow-500 rounded"></div>
              <div>
                <p className="font-semibold text-yellow-800">Yellow (15-50%)</p>
                <p className="text-xs text-gray-600">Low Stock - Reorder Soon</p>
              </div>
            </div>
            <div className="flex items-center gap-3 p-3 bg-red-50 rounded-lg border border-red-200">
              <div className="w-6 h-6 bg-red-500 rounded"></div>
              <div>
                <p className="font-semibold text-red-800">Red (&lt;15%)</p>
                <p className="text-xs text-gray-600">Critical - Urgent Reorder</p>
              </div>
            </div>
            <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg border border-gray-400">
              <div className="w-6 h-6 bg-black rounded"></div>
              <div>
                <p className="font-semibold text-black">Black (Negative)</p>
                <p className="text-xs text-gray-600">Material Debt - Reconcile</p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
