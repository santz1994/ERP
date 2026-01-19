/**
 * Copyright (c) 2026 PT Quty Karunia / Daniel Rizaldy - All Rights Reserved
 * File: ReportsPage.tsx | Author: Daniel Rizaldy | Date: 2026-01-19
 */

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { format } from 'date-fns';
import { 
  FileText, 
  Download,
  Calendar,
  TrendingUp,
  BarChart3,
  PieChart,
  FileSpreadsheet
} from 'lucide-react';
import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

export default function ReportsPage() {
  const [reportType, setReportType] = useState('production');
  const [startDate, setStartDate] = useState(format(new Date(), 'yyyy-MM-dd'));
  const [endDate, setEndDate] = useState(format(new Date(), 'yyyy-MM-dd'));
  const [exportFormat, setExportFormat] = useState<'pdf' | 'excel'>('pdf');

  // Fetch production statistics
  const { data: productionStats } = useQuery({
    queryKey: ['production-stats', startDate, endDate],
    queryFn: async () => {
      const token = localStorage.getItem('access_token');
      const response = await axios.get(`${API_BASE}/reports/production-stats`, {
        params: { start_date: startDate, end_date: endDate },
        headers: { Authorization: `Bearer ${token}` }
      });
      return response.data;
    }
  });

  // Fetch QC statistics
  const { data: qcStats } = useQuery({
    queryKey: ['qc-stats', startDate, endDate],
    queryFn: async () => {
      const token = localStorage.getItem('access_token');
      const response = await axios.get(`${API_BASE}/reports/qc-stats`, {
        params: { start_date: startDate, end_date: endDate },
        headers: { Authorization: `Bearer ${token}` }
      });
      return response.data;
    }
  });

  // Fetch inventory summary
  const { data: inventoryStats } = useQuery({
    queryKey: ['inventory-stats'],
    queryFn: async () => {
      const token = localStorage.getItem('access_token');
      const response = await axios.get(`${API_BASE}/reports/inventory-summary`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      return response.data;
    }
  });

  const downloadReport = async (type: string, format: string) => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await axios.get(`${API_BASE}/reports/${type}/export`, {
        params: {
          start_date: startDate,
          end_date: endDate,
          format: format
        },
        headers: { Authorization: `Bearer ${token}` },
        responseType: 'blob'
      });

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `${type}_report_${format === 'pdf' ? '.pdf' : '.xlsx'}`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (error) {
      console.error('Download failed:', error);
      alert('Failed to download report');
    }
  };

  const reportTypes = [
    { value: 'production', label: 'Production Report', icon: TrendingUp },
    { value: 'qc', label: 'QC Report', icon: BarChart3 },
    { value: 'inventory', label: 'Inventory Report', icon: PieChart },
  ];

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 flex items-center">
          <FileText className="w-8 h-8 mr-3 text-indigo-600" />
          Reports Dashboard
        </h1>
        <p className="text-gray-500 mt-1">
          Generate and download production, QC, and inventory reports
        </p>
      </div>

      {/* Report Controls */}
      <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {/* Report Type */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Report Type
            </label>
            <select
              value={reportType}
              onChange={(e) => setReportType(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              {reportTypes.map(type => (
                <option key={type.value} value={type.value}>{type.label}</option>
              ))}
            </select>
          </div>

          {/* Start Date */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Start Date
            </label>
            <input
              type="date"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          </div>

          {/* End Date */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              End Date
            </label>
            <input
              type="date"
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          </div>

          {/* Export Format */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Export Format
            </label>
            <select
              value={exportFormat}
              onChange={(e) => setExportFormat(e.target.value as 'pdf' | 'excel')}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              <option value="pdf">PDF</option>
              <option value="excel">Excel</option>
            </select>
          </div>
        </div>

        {/* Download Button */}
        <div className="mt-4 flex justify-end">
          <button
            onClick={() => downloadReport(reportType, exportFormat)}
            className="bg-indigo-600 text-white px-6 py-2 rounded-lg hover:bg-indigo-700 transition flex items-center shadow-md"
          >
            <Download className="w-5 h-5 mr-2" />
            Download Report
          </button>
        </div>
      </div>

      {/* Report Preview */}
      {reportType === 'production' && productionStats && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
          {/* Summary Cards */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-lg font-semibold text-gray-900">Total Output</h3>
              <TrendingUp className="w-6 h-6 text-green-600" />
            </div>
            <p className="text-3xl font-bold text-gray-900">{productionStats.total_output || 0}</p>
            <p className="text-sm text-gray-500 mt-1">units produced</p>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-lg font-semibold text-gray-900">Work Orders</h3>
              <FileText className="w-6 h-6 text-blue-600" />
            </div>
            <p className="text-3xl font-bold text-gray-900">{productionStats.total_work_orders || 0}</p>
            <p className="text-sm text-gray-500 mt-1">completed</p>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-lg font-semibold text-gray-900">Efficiency</h3>
              <BarChart3 className="w-6 h-6 text-purple-600" />
            </div>
            <p className="text-3xl font-bold text-gray-900">
              {productionStats.efficiency ? `${productionStats.efficiency.toFixed(1)}%` : '0%'}
            </p>
            <p className="text-sm text-gray-500 mt-1">overall efficiency</p>
          </div>
        </div>
      )}

      {reportType === 'production' && productionStats?.by_department && (
        <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
          <h3 className="text-xl font-semibold text-gray-900 mb-4">Production by Department</h3>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Department
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Work Orders
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Input Qty
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Output Qty
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Reject Qty
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Efficiency
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {Object.entries(productionStats.by_department).map(([dept, stats]: [string, any]) => (
                  <tr key={dept} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap font-medium text-gray-900">{dept}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-gray-700">{stats.work_orders}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-gray-700">{stats.input_qty}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-blue-600 font-medium">{stats.output_qty}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-red-600 font-medium">{stats.reject_qty}</td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                        stats.efficiency >= 95 ? 'bg-green-100 text-green-800' :
                        stats.efficiency >= 85 ? 'bg-yellow-100 text-yellow-800' :
                        'bg-red-100 text-red-800'
                      }`}>
                        {stats.efficiency.toFixed(1)}%
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {reportType === 'qc' && qcStats && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-lg font-semibold text-gray-900">Total Inspections</h3>
              <BarChart3 className="w-6 h-6 text-blue-600" />
            </div>
            <p className="text-3xl font-bold text-gray-900">{qcStats.total_inspections || 0}</p>
            <p className="text-sm text-gray-500 mt-1">QC inspections performed</p>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-lg font-semibold text-gray-900">Pass Rate</h3>
              <TrendingUp className="w-6 h-6 text-green-600" />
            </div>
            <p className="text-3xl font-bold text-gray-900">
              {qcStats.pass_rate ? `${qcStats.pass_rate.toFixed(1)}%` : '0%'}
            </p>
            <p className="text-sm text-gray-500 mt-1">quality pass rate</p>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-lg font-semibold text-gray-900">Defects Found</h3>
              <FileText className="w-6 h-6 text-red-600" />
            </div>
            <p className="text-3xl font-bold text-gray-900">{qcStats.total_defects || 0}</p>
            <p className="text-sm text-gray-500 mt-1">total defects</p>
          </div>
        </div>
      )}

      {reportType === 'qc' && qcStats?.defect_breakdown && (
        <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
          <h3 className="text-xl font-semibold text-gray-900 mb-4">Defect Breakdown</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {Object.entries(qcStats.defect_breakdown).map(([defect, count]: [string, any]) => (
              <div key={defect} className="bg-red-50 p-4 rounded-lg">
                <p className="text-sm text-red-700">{defect}</p>
                <p className="text-2xl font-bold text-red-600">{count}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {reportType === 'inventory' && inventoryStats && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-lg font-semibold text-gray-900">Total Items</h3>
              <PieChart className="w-6 h-6 text-purple-600" />
            </div>
            <p className="text-3xl font-bold text-gray-900">{inventoryStats.total_items || 0}</p>
            <p className="text-sm text-gray-500 mt-1">unique items</p>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-lg font-semibold text-gray-900">Low Stock Items</h3>
              <FileSpreadsheet className="w-6 h-6 text-orange-600" />
            </div>
            <p className="text-3xl font-bold text-gray-900">{inventoryStats.low_stock_count || 0}</p>
            <p className="text-sm text-gray-500 mt-1">need replenishment</p>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-lg font-semibold text-gray-900">Out of Stock</h3>
              <FileText className="w-6 h-6 text-red-600" />
            </div>
            <p className="text-3xl font-bold text-gray-900">{inventoryStats.out_of_stock_count || 0}</p>
            <p className="text-sm text-gray-500 mt-1">items unavailable</p>
          </div>
        </div>
      )}

      {reportType === 'inventory' && inventoryStats?.categories && (
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h3 className="text-xl font-semibold text-gray-900 mb-4">Inventory by Category</h3>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Category
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Items
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Total Quantity
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Low Stock
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {Object.entries(inventoryStats.categories).map(([category, data]: [string, any]) => (
                  <tr key={category} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap font-medium text-gray-900">{category}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-gray-700">{data.item_count}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-blue-600 font-medium">{data.total_qty}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-orange-600">{data.low_stock_count}</td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                        data.low_stock_count === 0 ? 'bg-green-100 text-green-800' :
                        data.low_stock_count <= 2 ? 'bg-yellow-100 text-yellow-800' :
                        'bg-red-100 text-red-800'
                      }`}>
                        {data.low_stock_count === 0 ? 'Healthy' : 'Attention Needed'}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
