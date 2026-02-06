/**
 * Copyright (c) 2026 PT Quty Karunia / Daniel Rizaldy - All Rights Reserved
 * File: PurchasingPage.tsx | Author: Daniel Rizaldy | Date: 2026-02-06
 * Purpose: Purchasing Module Landing Dashboard (REFACTORED)
 * Architecture: Level 2 - Module Landing Page (Dashboard → Landing → Detail)
 */

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { format } from 'date-fns';
import { 
  ShoppingCart, 
  CheckCircle, 
  Clock, 
  XCircle,
  PackageCheck,
  TrendingUp,
  FileText,
  Plus,
  Users,
  BarChart3
} from 'lucide-react';
import axios from 'axios';
import { NavigationCard } from '@/components/ui/NavigationCard';
import { Card } from '@/components/ui/card';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

interface PurchaseOrder {
  id: number;
  po_number: string;
  supplier_id: number;
  order_date: string;
  expected_date: string;
  status: string;
  total_amount: number;
  currency: string;
  po_type?: string;
  metadata?: {
    items?: Array<{
      product_id: number;
      quantity: number;
      unit_price: number;
    }>;
  };
}

export default function PurchasingPage() {
  const navigate = useNavigate();

  // Fetch purchase orders
  const { data: purchaseOrders, isLoading } = useQuery({
    queryKey: ['purchase-orders'],
    queryFn: async () => {
      const token = localStorage.getItem('access_token');
      const response = await axios.get(`${API_BASE}/purchasing/purchase-orders`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      return response.data;
    },
    refetchInterval: 30000 // Refresh every 30 seconds
  });

  // Calculate statistics
  const stats = {
    total: purchaseOrders?.length || 0,
    draft: purchaseOrders?.filter((po: PurchaseOrder) => po.status === 'Draft').length || 0,
    sent: purchaseOrders?.filter((po: PurchaseOrder) => po.status === 'Sent').length || 0,
    received: purchaseOrders?.filter((po: PurchaseOrder) => po.status === 'Received').length || 0,
    done: purchaseOrders?.filter((po: PurchaseOrder) => po.status === 'Done').length || 0,
    totalSpend: purchaseOrders?.reduce((sum: number, po: PurchaseOrder) => sum + (po.total_amount || 0), 0) || 0,
  };

  // Get recent POs (last 10)
  const recentPOs = purchaseOrders?.slice(0, 10) || [];

  const getStatusBadge = (status: string) => {
    const badges: Record<string, { color: string; icon: any }> = {
      'Draft': { color: 'bg-gray-100 text-gray-800', icon: FileText },
      'Sent': { color: 'bg-blue-100 text-blue-800', icon: Clock },
      'Received': { color: 'bg-green-100 text-green-800', icon: PackageCheck },
      'Done': { color: 'bg-purple-100 text-purple-800', icon: CheckCircle },
      'Cancelled': { color: 'bg-red-100 text-red-800', icon: XCircle },
    };
    const badge = badges[status] || badges['Draft'];
    const Icon = badge.icon;
    return (
      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${badge.color}`}>
        <Icon className="w-3 h-3 mr-1" />
        {status}
      </span>
    );
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('id-ID', {
      style: 'currency',
      currency: 'IDR',
      minimumFractionDigits: 0
    }).format(amount);
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 flex items-center">
              <ShoppingCart className="w-8 h-8 mr-3 text-blue-600" />
              Purchasing Department
            </h1>
            <p className="text-gray-500 mt-1">
              {format(new Date(), 'EEEE, dd MMMM yyyy • HH:mm')} WIB
            </p>
            <p className="text-sm text-gray-400 mt-1">
              📍 Module Landing Page • 3 Specialists: Fabric, Label, Accessories
            </p>
          </div>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <Card className="bg-white shadow-lg border-l-4 border-blue-500">
          <div className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500 mb-1">Total POs</p>
                <p className="text-3xl font-bold text-gray-900">{stats.total}</p>
                <p className="text-xs text-gray-400 mt-1">All time</p>
              </div>
              <FileText className="w-12 h-12 text-blue-400" />
            </div>
          </div>
        </Card>

        <Card className="bg-white shadow-lg border-l-4 border-orange-500">
          <div className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500 mb-1">Pending Approval</p>
                <p className="text-3xl font-bold text-orange-600">{stats.draft}</p>
                <p className="text-xs text-gray-400 mt-1">Draft status</p>
              </div>
              <Clock className="w-12 h-12 text-orange-400" />
            </div>
          </div>
        </Card>

        <Card className="bg-white shadow-lg border-l-4 border-purple-500">
          <div className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500 mb-1">This Month Spend</p>
                <p className="text-2xl font-bold text-purple-600">{formatCurrency(stats.totalSpend)}</p>
                <p className="text-xs text-gray-400 mt-1">Total purchase value</p>
              </div>
              <TrendingUp className="w-12 h-12 text-purple-400" />
            </div>
          </div>
        </Card>

        <Card className="bg-white shadow-lg border-l-4 border-green-500">
          <div className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500 mb-1">Completed</p>
                <p className="text-3xl font-bold text-green-600">{stats.done}</p>
                <p className="text-xs text-gray-400 mt-1">Done status</p>
              </div>
              <CheckCircle className="w-12 h-12 text-green-400" />
            </div>
          </div>
        </Card>
      </div>

      {/* Navigation Cards - CRITICAL for 3-Tier Architecture */}
      <div className="mb-8">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <NavigationCard
            title="Create New PO"
            description="Create purchase order with AUTO (BOM explosion) or MANUAL mode. Supports Dual Trigger System (PO Kain + PO Label)."
            icon={Plus}
            link="/purchasing/po/create"
            color="purple"
            badge="Dual Mode"
          />
          
          <NavigationCard
            title="PO List & Tracking"
            description="View all purchase orders with advanced filters. Track PO status from Draft → Sent → Received → Done."
            icon={BarChart3}
            link="/purchasing/po"
            color="blue"
            badge="Real-time"
            disabled={true}
          />
          
          <NavigationCard
            title="Supplier Management"
            description="Manage supplier database, performance tracking, and payment terms. Multi-supplier per material support."
            icon={Users}
            link="/purchasing/suppliers"
            color="green"
            disabled={true}
          />
        </div>
      </div>

      {/* PO Status Breakdown */}
      <div className="mb-8">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">PO Status Overview</h2>
        <Card className="bg-white shadow-lg">
          <div className="p-6">
            <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
              <div className="text-center">
                <FileText className="w-8 h-8 text-gray-400 mx-auto mb-2" />
                <p className="text-2xl font-bold text-gray-900">{stats.draft}</p>
                <p className="text-sm text-gray-500">Draft</p>
              </div>
              <div className="text-center">
                <Clock className="w-8 h-8 text-blue-400 mx-auto mb-2" />
                <p className="text-2xl font-bold text-blue-600">{stats.sent}</p>
                <p className="text-sm text-gray-500">Sent</p>
              </div>
              <div className="text-center">
                <PackageCheck className="w-8 h-8 text-orange-400 mx-auto mb-2" />
                <p className="text-2xl font-bold text-orange-600">{stats.received}</p>
                <p className="text-sm text-gray-500">Received</p>
              </div>
              <div className="text-center">
                <CheckCircle className="w-8 h-8 text-green-400 mx-auto mb-2" />
                <p className="text-2xl font-bold text-green-600">{stats.done}</p>
                <p className="text-sm text-gray-500">Done</p>
              </div>
              <div className="text-center">
                <TrendingUp className="w-8 h-8 text-purple-400 mx-auto mb-2" />
                <p className="text-2xl font-bold text-purple-600">{stats.total}</p>
                <p className="text-sm text-gray-500">Total</p>
              </div>
            </div>
          </div>
        </Card>
      </div>

      {/* Recent Purchase Orders Table */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold text-gray-900">Recent Purchase Orders</h2>
          <button
            onClick={() => navigate('/purchasing/po')}
            className="text-blue-600 hover:text-blue-700 text-sm font-medium disabled:opacity-50 disabled:cursor-not-allowed"
            disabled={true}
          >
            View All →
          </button>
        </div>
        
        <Card className="bg-white shadow-lg overflow-hidden">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    PO Number
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Type
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Supplier
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Order Date
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Amount
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {recentPOs.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="px-6 py-12 text-center">
                      <ShoppingCart className="w-12 h-12 text-gray-400 mx-auto mb-3" />
                      <p className="text-gray-500">No purchase orders yet</p>
                      <button
                        onClick={() => navigate('/purchasing/po/create')}
                        className="mt-4 text-blue-600 hover:text-blue-700 text-sm font-medium"
                      >
                        Create your first PO →
                      </button>
                    </td>
                  </tr>
                ) : (
                  recentPOs.map((po: PurchaseOrder) => (
                    <tr key={po.id} className="hover:bg-gray-50 transition-colors">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900">{po.po_number}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                          po.po_type === 'KAIN' ? 'bg-purple-100 text-purple-800' :
                          po.po_type === 'LABEL' ? 'bg-blue-100 text-blue-800' :
                          'bg-gray-100 text-gray-800'
                        }`}>
                          {po.po_type || 'N/A'}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">Supplier #{po.supplier_id}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-500">
                          {format(new Date(po.order_date), 'dd MMM yyyy')}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900">
                          {formatCurrency(po.total_amount)}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        {getStatusBadge(po.status)}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </Card>
      </div>

      {/* Help Section */}
      <Card className="bg-blue-50 border-blue-200">
        <div className="p-6">
          <h3 className="text-lg font-semibold text-blue-900 mb-2">💡 Purchasing Module Guide</h3>
          <div className="text-sm text-blue-800 space-y-1">
            <p>• <strong>Dual Mode PO</strong>: AUTO mode uses BOM explosion, MANUAL mode for line-by-line entry</p>
            <p>• <strong>Dual Trigger System</strong>: PO Kain (TRIGGER 1) starts Cutting, PO Label (TRIGGER 2) releases full production</p>
            <p>• <strong>Multi-Supplier</strong>: Each material can have different supplier in the same PO</p>
            <p>• <strong>3 Specialists</strong>: Fabric, Label, and Accessories purchasing handled separately</p>
          </div>
        </div>
      </Card>
    </div>
  );
}
