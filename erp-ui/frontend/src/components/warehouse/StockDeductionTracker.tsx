/**
 * Stock Deduction Tracker - Material Consumption Monitoring
 * Priority 3.3: Warehouse Integration
 * Created: 2026-02-04
 */

import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/api/client';
import { 
  TrendingDown, 
  Package, 
  Calendar,
  MapPin,
  Factory,
  CheckCircle,
  AlertCircle,
  Clock,
  BarChart3
} from 'lucide-react';

interface StockDeduction {
  id: number;
  wo_id: number;
  wo_code: string;
  department: string;
  material_id: number;
  material_code: string;
  material_name: string;
  qty_deducted: number;
  uom: string;
  stock_quant_id: number;
  lot_number?: string;
  location_name: string;
  deducted_at: string;
  deducted_by?: string;
  reference?: string;
}

interface StockDeductionTrackerProps {
  woId?: number;
  materialId?: number;
  department?: string;
}

export const StockDeductionTracker: React.FC<StockDeductionTrackerProps> = ({
  woId,
  materialId,
  department
}) => {
  const [selectedWO, setSelectedWO] = useState<number | undefined>(woId);
  const [selectedDepartment, setSelectedDepartment] = useState<string | undefined>(department);
  const [dateRange, setDateRange] = useState<'today' | 'week' | 'month' | 'all'>('week');

  const departments = ['ALL', 'CUTTING', 'EMBROIDERY', 'SEWING', 'FINISHING', 'PACKING'];

  // Fetch Work Orders
  const { data: workOrders } = useQuery({
    queryKey: ['work-orders-for-deduction'],
    queryFn: async () => {
      const response = await apiClient.get('/work-orders?state=RUNNING,COMPLETED');
      return response.data;
    }
  });

  // Fetch Stock Deductions
  const { data: deductions, isLoading } = useQuery({
    queryKey: ['stock-deductions', selectedWO, materialId, selectedDepartment, dateRange],
    queryFn: async () => {
      const params = new URLSearchParams();
      if (selectedWO) params.append('wo_id', selectedWO.toString());
      if (materialId) params.append('material_id', materialId.toString());
      if (selectedDepartment && selectedDepartment !== 'ALL') {
        params.append('department', selectedDepartment);
      }
      params.append('date_range', dateRange);
      const response = await apiClient.get(`/material-allocation/deductions?${params}`);
      return response.data as StockDeduction[];
    }
  });

  // Calculate stats
  const totalDeductions = deductions?.length || 0;
  const uniqueMaterials = new Set(deductions?.map(d => d.material_id)).size;
  const uniqueWOs = new Set(deductions?.map(d => d.wo_id)).size;
  const totalQty = deductions?.reduce((sum, d) => sum + d.qty_deducted, 0) || 0;

  const deductionsByDepartment = deductions?.reduce((acc, d) => {
    acc[d.department] = (acc[d.department] || 0) + d.qty_deducted;
    return acc;
  }, {} as Record<string, number>);

  return (
    <div className="space-y-6">
      {/* Header & Controls */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <div className="bg-red-100 p-3 rounded-lg">
              <TrendingDown className="text-red-600" size={32} />
            </div>
            <div>
              <h2 className="text-2xl font-bold text-gray-900">Stock Deduction Tracker</h2>
              <p className="text-gray-600">Real-time material consumption monitoring</p>
            </div>
          </div>
        </div>

        {/* Filters */}
        <div className="grid grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Work Order
            </label>
            <select
              value={selectedWO || ''}
              onChange={(e) => setSelectedWO(e.target.value ? Number(e.target.value) : undefined)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">All Work Orders</option>
              {workOrders?.map((wo: any) => (
                <option key={wo.id} value={wo.id}>
                  {wo.wo_code} - {wo.department}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Department
            </label>
            <select
              value={selectedDepartment || 'ALL'}
              onChange={(e) => setSelectedDepartment(e.target.value === 'ALL' ? undefined : e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              {departments.map(dept => (
                <option key={dept} value={dept}>{dept}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Date Range
            </label>
            <select
              value={dateRange}
              onChange={(e) => setDateRange(e.target.value as any)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="today">Today</option>
              <option value="week">This Week</option>
              <option value="month">This Month</option>
              <option value="all">All Time</option>
            </select>
          </div>
        </div>

        {/* Summary Stats */}
        <div className="grid grid-cols-4 gap-4 mt-6">
          <div className="bg-red-50 rounded-lg p-3 text-center">
            <div className="text-2xl font-bold text-red-600">{totalDeductions}</div>
            <div className="text-xs text-gray-600">Total Deductions</div>
          </div>
          <div className="bg-blue-50 rounded-lg p-3 text-center">
            <div className="text-2xl font-bold text-blue-600">{uniqueMaterials}</div>
            <div className="text-xs text-gray-600">Unique Materials</div>
          </div>
          <div className="bg-purple-50 rounded-lg p-3 text-center">
            <div className="text-2xl font-bold text-purple-600">{uniqueWOs}</div>
            <div className="text-xs text-gray-600">Work Orders</div>
          </div>
          <div className="bg-green-50 rounded-lg p-3 text-center">
            <div className="text-2xl font-bold text-green-600">{totalQty.toFixed(2)}</div>
            <div className="text-xs text-gray-600">Total Qty Consumed</div>
          </div>
        </div>

        {/* Department Breakdown */}
        {deductionsByDepartment && Object.keys(deductionsByDepartment).length > 0 && (
          <div className="mt-6 bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg p-4">
            <h4 className="text-sm font-semibold text-gray-700 mb-3 flex items-center gap-2">
              <BarChart3 size={18} />
              Consumption by Department
            </h4>
            <div className="grid grid-cols-5 gap-3">
              {Object.entries(deductionsByDepartment).map(([dept, qty]) => (
                <div key={dept} className="bg-white rounded-lg p-3 text-center">
                  <div className="text-lg font-bold text-gray-900">{(qty as number).toFixed(0)}</div>
                  <div className="text-xs text-gray-600">{dept}</div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Deductions List */}
      <div className="bg-white rounded-lg shadow-md">
        {isLoading ? (
          <div className="p-12 text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p className="text-gray-600">Loading deduction records...</p>
          </div>
        ) : deductions?.length === 0 ? (
          <div className="p-12 text-center">
            <Package className="mx-auto text-gray-400 mb-4" size={64} />
            <h4 className="text-lg font-semibold text-gray-900 mb-2">No Deductions Found</h4>
            <p className="text-gray-600">No material consumption records for selected filters</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 border-b-2 border-gray-200">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date/Time</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Material</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Work Order</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Department</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Location</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Lot/Batch</th>
                  <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Qty Deducted</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">By</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {deductions?.map((deduction) => (
                  <tr key={deduction.id} className="hover:bg-gray-50">
                    <td className="px-4 py-3 text-sm">
                      <div className="flex items-center gap-1 text-gray-700">
                        <Calendar size={14} />
                        <div>
                          <div className="font-medium">{new Date(deduction.deducted_at).toLocaleDateString()}</div>
                          <div className="text-xs text-gray-500">{new Date(deduction.deducted_at).toLocaleTimeString()}</div>
                        </div>
                      </div>
                    </td>
                    <td className="px-4 py-3">
                      <div>
                        <div className="font-semibold text-gray-900">{deduction.material_code}</div>
                        <div className="text-sm text-gray-600 truncate max-w-xs">{deduction.material_name}</div>
                      </div>
                    </td>
                    <td className="px-4 py-3 text-sm">
                      <div className="flex items-center gap-1">
                        <Factory size={14} className="text-blue-600" />
                        <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded text-xs font-medium">
                          {deduction.wo_code}
                        </span>
                      </div>
                    </td>
                    <td className="px-4 py-3 text-sm">
                      <span className="px-2 py-1 bg-purple-100 text-purple-800 rounded text-xs font-semibold">
                        {deduction.department}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-sm">
                      <div className="flex items-center gap-1 text-gray-700">
                        <MapPin size={14} />
                        {deduction.location_name}
                      </div>
                    </td>
                    <td className="px-4 py-3 text-sm">
                      {deduction.lot_number ? (
                        <span className="px-2 py-1 bg-orange-100 text-orange-800 rounded text-xs font-medium">
                          {deduction.lot_number}
                        </span>
                      ) : (
                        <span className="text-gray-400">-</span>
                      )}
                    </td>
                    <td className="px-4 py-3 text-right">
                      <div className="font-bold text-red-600">-{deduction.qty_deducted.toFixed(2)}</div>
                      <div className="text-xs text-gray-600">{deduction.uom}</div>
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-700">
                      {deduction.deducted_by || '-'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Info Box */}
      <div className="bg-green-50 border border-green-200 rounded-lg p-4 flex items-start gap-3">
        <CheckCircle className="text-green-600 flex-shrink-0 mt-0.5" size={20} />
        <div className="text-sm text-green-900">
          <p className="font-semibold mb-1">Stock Deduction Process:</p>
          <ul className="list-disc list-inside space-y-1 text-green-800">
            <li><strong>Trigger:</strong> When WO starts (status: PENDING → RUNNING), system auto-deducts reserved materials.</li>
            <li><strong>FIFO:</strong> Oldest stock (by FIFO date) is consumed first.</li>
            <li><strong>Lot Tracking:</strong> Each deduction tracks specific lot/batch for traceability.</li>
            <li><strong>Audit Trail:</strong> Complete history of who consumed what, when, and for which work order.</li>
          </ul>
        </div>
      </div>
    </div>
  );
};
