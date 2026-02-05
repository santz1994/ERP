import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { api } from '../../api';
import { Card, CardHeader, CardTitle, CardContent } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Badge } from '../../components/ui/badge';
import { cn, formatDate, formatNumber, calculatePercentage } from '../../lib/utils';

/**
 * MO List Page - PPIC Module
 * 
 * Features:
 * - MO list with comprehensive filters
 * - Real-time status tracking
 * - PARTIAL vs RELEASED status visualization
 * - Week & Destination display (inherited from PO Label)
 * - Progress tracking with percentage
 * - Quick actions (View, Edit, Release)
 * 
 * Critical Business Logic:
 * - DRAFT: MO baru dibuat, belum ada PO
 * - PARTIAL: PO Kain received (TRIGGER 1) - Unlock Cutting + Embroidery
 * - RELEASED: PO Label received (TRIGGER 2) - Unlock all departments
 * - COMPLETED: Production finished
 */

interface MOFilter {
  status?: 'DRAFT' | 'PARTIAL' | 'RELEASED' | 'COMPLETED';
  articleCode?: string;
  week?: string;
  search?: string;
}

interface MO {
  id: number;
  moNumber: string;
  moDate: string;
  articleCode: string;
  articleName: string;
  targetQty: number;
  actualQty: number;
  week?: string; // Inherited from PO Label
  destination?: string; // Inherited from PO Label
  status: 'DRAFT' | 'PARTIAL' | 'RELEASED' | 'COMPLETED';
  daysRemaining: number;
  poKainNumber?: string; // TRIGGER 1
  poLabelNumber?: string; // TRIGGER 2
  createdAt: string;
  createdBy: string;
}

export default function MOListPage() {
  const navigate = useNavigate();
  const [filters, setFilters] = useState<MOFilter>({});

  // Fetch MO list with React Query
  const { data: moList, isLoading, refetch } = useQuery({
    queryKey: ['mo-list', filters],
    queryFn: () => api.ppic.getMOs(filters),
    refetchInterval: 30000, // Refresh every 30 seconds for real-time updates
  });

  // Status badge helper
  const getStatusBadge = (status: MO['status']) => {
    const configs = {
      DRAFT: { variant: 'secondary' as const, label: '📝 DRAFT' },
      PARTIAL: { variant: 'warning' as const, label: '🟡 PARTIAL - Waiting PO Label' },
      RELEASED: { variant: 'success' as const, label: '✅ RELEASED' },
      COMPLETED: { variant: 'success' as const, label: '✅ COMPLETED' },
    };
    const config = configs[status];
    return <Badge variant={config.variant}>{config.label}</Badge>;
  };

  // Progress bar color
  const getProgressColor = (percentage: number) => {
    if (percentage >= 100) return 'bg-green-500';
    if (percentage >= 75) return 'bg-blue-500';
    if (percentage >= 50) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  // Handle filter change
  const handleFilterChange = (key: keyof MOFilter, value: string) => {
    setFilters(prev => ({ ...prev, [key]: value || undefined }));
  };

  // Clear filters
  const clearFilters = () => {
    setFilters({});
  };

  return (
    <div className="p-6 space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Manufacturing Orders (MO)</h1>
          <p className="text-gray-600 mt-1">
            Manage production orders with Dual Trigger System (PO Kain + PO Label)
          </p>
        </div>
        <Button
          variant="primary"
          leftIcon={<span>➕</span>}
          onClick={() => navigate('/ppic/mo/create')}
        >
          Create New MO
        </Button>
      </div>

      {/* Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {[
          { label: 'Total MOs', value: moList?.length || 0, color: 'bg-blue-500' },
          { label: 'PARTIAL (Waiting Label)', value: moList?.filter((mo: MO) => mo.status === 'PARTIAL').length || 0, color: 'bg-yellow-500' },
          { label: 'RELEASED (Active)', value: moList?.filter((mo: MO) => mo.status === 'RELEASED').length || 0, color: 'bg-green-500' },
          { label: 'COMPLETED', value: moList?.filter((mo: MO) => mo.status === 'COMPLETED').length || 0, color: 'bg-gray-500' },
        ].map((stat, idx) => (
          <Card key={idx} variant="bordered">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">{stat.label}</p>
                  <p className="text-2xl font-bold mt-1">{stat.value}</p>
                </div>
                <div className={cn('w-12 h-12 rounded-full flex items-center justify-center', stat.color)}>
                  <span className="text-white text-xl">📦</span>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Filters */}
      <Card variant="bordered">
        <CardHeader>
          <CardTitle>🔍 Filters</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
            {/* Status Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Status</label>
              <select
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                value={filters.status || ''}
                onChange={(e) => handleFilterChange('status', e.target.value)}
              >
                <option value="">All Status</option>
                <option value="DRAFT">📝 DRAFT</option>
                <option value="PARTIAL">🟡 PARTIAL</option>
                <option value="RELEASED">✅ RELEASED</option>
                <option value="COMPLETED">✅ COMPLETED</option>
              </select>
            </div>

            {/* Article Code Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Article Code</label>
              <input
                type="text"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Search by article..."
                value={filters.articleCode || ''}
                onChange={(e) => handleFilterChange('articleCode', e.target.value)}
              />
            </div>

            {/* Week Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Week</label>
              <input
                type="text"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="e.g., 2026-W05"
                value={filters.week || ''}
                onChange={(e) => handleFilterChange('week', e.target.value)}
              />
            </div>

            {/* Search Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Search</label>
              <input
                type="text"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="MO Number, Destination..."
                value={filters.search || ''}
                onChange={(e) => handleFilterChange('search', e.target.value)}
              />
            </div>

            {/* Action Buttons */}
            <div className="flex items-end gap-2">
              <Button variant="secondary" onClick={clearFilters} className="flex-1">
                Clear
              </Button>
              <Button variant="primary" onClick={() => refetch()} className="flex-1">
                🔄 Refresh
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* MO Table */}
      <Card variant="bordered">
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>📋 Manufacturing Orders List</CardTitle>
            <Badge variant="info">
              {isLoading ? 'Loading...' : `${moList?.length || 0} MOs`}
            </Badge>
          </div>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="text-center py-12">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto"></div>
              <p className="text-gray-600 mt-4">Loading Manufacturing Orders...</p>
            </div>
          ) : moList && moList.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="bg-gray-50 border-b">
                  <tr>
                    <th className="px-4 py-3 text-left font-semibold text-gray-700">MO Number</th>
                    <th className="px-4 py-3 text-left font-semibold text-gray-700">Article</th>
                    <th className="px-4 py-3 text-center font-semibold text-gray-700">Target Qty</th>
                    <th className="px-4 py-3 text-center font-semibold text-gray-700">Progress</th>
                    <th className="px-4 py-3 text-center font-semibold text-gray-700">Week / Destination</th>
                    <th className="px-4 py-3 text-center font-semibold text-gray-700">Status</th>
                    <th className="px-4 py-3 text-center font-semibold text-gray-700">Days Remaining</th>
                    <th className="px-4 py-3 text-center font-semibold text-gray-700">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {moList.map((mo: MO) => {
                    const progressPercent = calculatePercentage(mo.actualQty, mo.targetQty);
                    return (
                      <tr key={mo.id} className="hover:bg-gray-50 transition-colors">
                        {/* MO Number */}
                        <td className="px-4 py-4">
                          <button
                            onClick={() => navigate(`/ppic/mo/${mo.id}`)}
                            className="text-blue-600 hover:text-blue-800 font-medium hover:underline"
                          >
                            {mo.moNumber}
                          </button>
                          <p className="text-xs text-gray-500 mt-1">
                            {formatDate(mo.moDate)}
                          </p>
                        </td>

                        {/* Article */}
                        <td className="px-4 py-4">
                          <div className="font-medium text-gray-900">{mo.articleCode}</div>
                          <div className="text-xs text-gray-600 mt-1">{mo.articleName}</div>
                        </td>

                        {/* Target Qty */}
                        <td className="px-4 py-4 text-center">
                          <div className="font-semibold text-gray-900">
                            {formatNumber(mo.targetQty)} pcs
                          </div>
                        </td>

                        {/* Progress */}
                        <td className="px-4 py-4">
                          <div className="space-y-1">
                            <div className="flex items-center justify-between text-xs">
                              <span className="font-medium">
                                {formatNumber(mo.actualQty)} / {formatNumber(mo.targetQty)}
                              </span>
                              <span className={cn(
                                'font-semibold',
                                progressPercent >= 100 ? 'text-green-600' : 'text-gray-600'
                              )}>
                                {progressPercent}%
                              </span>
                            </div>
                            <div className="w-full bg-gray-200 rounded-full h-2">
                              <div
                                className={cn('h-2 rounded-full transition-all', getProgressColor(progressPercent))}
                                style={{ width: `${Math.min(progressPercent, 100)}%` }}
                              />
                            </div>
                          </div>
                        </td>

                        {/* Week / Destination */}
                        <td className="px-4 py-4 text-center">
                          {mo.week && mo.destination ? (
                            <div className="space-y-1">
                              <Badge variant="info" size="sm">
                                📅 {mo.week}
                              </Badge>
                              <div className="text-xs text-gray-700 font-medium">
                                {mo.destination}
                              </div>
                            </div>
                          ) : (
                            <span className="text-gray-400 text-xs italic">
                              Not inherited yet
                            </span>
                          )}
                        </td>

                        {/* Status */}
                        <td className="px-4 py-4 text-center">
                          <div className="space-y-1">
                            {getStatusBadge(mo.status)}
                            {mo.status === 'PARTIAL' && mo.poKainNumber && (
                              <div className="text-xs text-gray-600 mt-1">
                                PO Kain: {mo.poKainNumber}
                              </div>
                            )}
                            {mo.status === 'RELEASED' && mo.poLabelNumber && (
                              <div className="text-xs text-gray-600 mt-1">
                                PO Label: {mo.poLabelNumber}
                              </div>
                            )}
                          </div>
                        </td>

                        {/* Days Remaining */}
                        <td className="px-4 py-4 text-center">
                          <div className={cn(
                            'inline-flex items-center px-2 py-1 rounded-md text-xs font-semibold',
                            mo.daysRemaining > 5 ? 'bg-green-100 text-green-800' :
                            mo.daysRemaining > 2 ? 'bg-yellow-100 text-yellow-800' :
                            'bg-red-100 text-red-800'
                          )}>
                            {mo.daysRemaining > 0 ? `${mo.daysRemaining} days` : 'Overdue'}
                          </div>
                        </td>

                        {/* Actions */}
                        <td className="px-4 py-4">
                          <div className="flex items-center justify-center gap-2">
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => navigate(`/ppic/mo/${mo.id}`)}
                            >
                              👁️ View
                            </Button>
                            {mo.status === 'DRAFT' && (
                              <Button
                                variant="warning"
                                size="sm"
                                onClick={() => navigate(`/ppic/mo/${mo.id}/edit`)}
                              >
                                ✏️ Edit
                              </Button>
                            )}
                            {mo.status === 'PARTIAL' && mo.poLabelNumber && (
                              <Button
                                variant="success"
                                size="sm"
                                onClick={() => {
                                  // Release to FULL
                                  api.ppic.releaseFull(mo.id);
                                  refetch();
                                }}
                              >
                                ✅ Release Full
                              </Button>
                            )}
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
              <h3 className="text-lg font-semibold text-gray-700 mb-2">No Manufacturing Orders Found</h3>
              <p className="text-gray-600 mb-4">
                {Object.keys(filters).length > 0
                  ? 'Try adjusting your filters or create a new MO.'
                  : 'Get started by creating your first Manufacturing Order.'}
              </p>
              <Button
                variant="primary"
                onClick={() => navigate('/ppic/mo/create')}
              >
                ➕ Create New MO
              </Button>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Info Panel - Dual Trigger System */}
      <Card variant="elevated" className="bg-gradient-to-r from-purple-50 to-blue-50">
        <CardHeader>
          <CardTitle>ℹ️ Dual Trigger System Explained</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-white p-4 rounded-lg border-l-4 border-gray-400">
              <h4 className="font-semibold text-gray-900 mb-2">📝 DRAFT Status</h4>
              <p className="text-sm text-gray-600">
                MO baru dibuat dari PO Label. Menunggu PO Kain (TRIGGER 1) untuk unlock produksi awal.
              </p>
            </div>
            <div className="bg-white p-4 rounded-lg border-l-4 border-yellow-400">
              <h4 className="font-semibold text-gray-900 mb-2">🟡 PARTIAL Status</h4>
              <p className="text-sm text-gray-600">
                <strong>TRIGGER 1 Active:</strong> PO Kain received. Unlock <strong>Cutting + Embroidery</strong> only.
                Waiting PO Label for full release.
              </p>
            </div>
            <div className="bg-white p-4 rounded-lg border-l-4 border-green-400">
              <h4 className="font-semibold text-gray-900 mb-2">✅ RELEASED Status</h4>
              <p className="text-sm text-gray-600">
                <strong>TRIGGER 2 Active:</strong> PO Label received. Auto-inherit <strong>Week + Destination</strong>.
                Unlock <strong>ALL departments</strong> (Sewing → Finishing → Packing).
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
