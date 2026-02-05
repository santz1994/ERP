import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { api } from '../../api';
import { Card, CardHeader, CardTitle, CardContent } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Badge } from '../../components/ui/badge';
import { cn, formatNumber, getStockStatusColor } from '../../lib/utils';

/**
 * WIP Dashboard Page - Production Module
 * 
 * Features:
 * - Real-time WIP (Work In Progress) stock per department
 * - 6-stage production flow visualization
 * - Material flow tracking (Dept A → Dept B)
 * - Bottleneck detection (highlight lowest output dept)
 * - Color-coded alerts (Green/Yellow/Red/Black for negative)
 * - Live refresh every 30 seconds
 * 
 * WIP Buffer Concept:
 * - Each department has output buffer (transferred to next dept automatically)
 * - System tracks ACTUAL physical stock at each stage
 * - Negative balance = Dept B consumed more than Dept A produced (reconciliation needed)
 */

interface WIPStock {
  department: string;
  departmentLabel: string;
  icon: string;
  articleCode: string;
  articleName: string;
  spkNumber: string;
  bufferStock: number;
  targetQty: number;
  cumulativeProduced: number;
  cumulativeConsumed: number;
  status: 'ABUNDANT' | 'SUFFICIENT' | 'LOW' | 'CRITICAL' | 'NEGATIVE';
}

interface DepartmentFlow {
  from: string;
  to: string;
  todayTransferred: number;
  pendingTransfer: number;
}

export default function WIPDashboardPage() {
  const navigate = useNavigate();
  const [selectedArticle, setSelectedArticle] = useState<string | null>(null);

  // Fetch WIP data
  const { data: wipData, isLoading } = useQuery<WIPStock[]>({
    queryKey: ['wip-dashboard', selectedArticle],
    queryFn: () => api.production.getWIP(selectedArticle ? { articleCode: selectedArticle } : undefined),
    refetchInterval: 30000, // Refresh every 30 seconds
  });

  // Fetch material flow
  const { data: flowData } = useQuery<DepartmentFlow[]>({
    queryKey: ['material-flow'],
    queryFn: () => api.production.getMaterialFlow(),
    refetchInterval: 30000,
  });

  // Get unique articles for filter
  const articles = Array.from(new Set(wipData?.map(w => w.articleCode) || []));

  // Get status badge
  const getStatusBadge = (status: WIPStock['status']) => {
    const configs = {
      ABUNDANT: { variant: 'success' as const, label: '✅ Abundant' },
      SUFFICIENT: { variant: 'info' as const, label: '🟢 Sufficient' },
      LOW: { variant: 'warning' as const, label: '🟡 Low' },
      CRITICAL: { variant: 'error' as const, label: '🔴 Critical' },
      NEGATIVE: { variant: 'error' as const, label: '⚫ DEBT' },
    };
    return configs[status];
  };

  // Detect bottleneck (dept with lowest output)
  const bottleneckDept = wipData?.reduce((min, curr) => 
    curr.cumulativeProduced < min.cumulativeProduced ? curr : min
  , wipData[0])?.department;

  return (
    <div className="p-6 space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">📊 Real-Time WIP Dashboard</h1>
          <p className="text-gray-600 mt-1">
            Monitor Work-In-Progress stock across all production stages
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Badge variant="info">
            🔄 Auto-refresh: 30s
          </Badge>
          <Button variant="secondary" onClick={() => navigate('/production/calendar')}>
            📅 View Calendar
          </Button>
        </div>
      </div>

      {/* Article Filter */}
      <Card variant="bordered">
        <CardContent className="p-4">
          <div className="flex items-center gap-4">
            <label className="text-sm font-medium text-gray-700">Filter by Article:</label>
            <select
              value={selectedArticle || ''}
              onChange={(e) => setSelectedArticle(e.target.value || null)}
              className="px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">All Articles</option>
              {articles.map((article) => (
                <option key={article} value={article}>{article}</option>
              ))}
            </select>
            {selectedArticle && (
              <Button variant="ghost" size="sm" onClick={() => setSelectedArticle(null)}>
                ✕ Clear
              </Button>
            )}
          </div>
        </CardContent>
      </Card>

      {isLoading ? (
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-500 mx-auto"></div>
          <p className="text-gray-600 mt-4">Loading WIP data...</p>
        </div>
      ) : wipData && wipData.length > 0 ? (
        <>
          {/* WIP Stock Table */}
          <Card variant="bordered">
            <CardHeader>
              <CardTitle>📦 WIP Buffer Stock by Department</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead className="bg-gray-50 border-b">
                    <tr>
                      <th className="px-4 py-3 text-left font-semibold text-gray-700">Department</th>
                      <th className="px-4 py-3 text-left font-semibold text-gray-700">Article</th>
                      <th className="px-4 py-3 text-left font-semibold text-gray-700">SPK</th>
                      <th className="px-4 py-3 text-center font-semibold text-gray-700">Buffer Stock</th>
                      <th className="px-4 py-3 text-center font-semibold text-gray-700">Cumulative Produced</th>
                      <th className="px-4 py-3 text-center font-semibold text-gray-700">Cumulative Consumed</th>
                      <th className="px-4 py-3 text-center font-semibold text-gray-700">Target</th>
                      <th className="px-4 py-3 text-center font-semibold text-gray-700">Status</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200">
                    {wipData.map((wip, idx) => {
                      const isBottleneck = wip.department === bottleneckDept;
                      return (
                        <tr 
                          key={idx} 
                          className={cn(
                            'hover:bg-gray-50 transition-colors',
                            isBottleneck && 'bg-red-50'
                          )}
                        >
                          {/* Department */}
                          <td className="px-4 py-4">
                            <div className="flex items-center gap-2">
                              <span className="text-2xl">{wip.icon}</span>
                              <div>
                                <div className="font-semibold text-gray-900">{wip.departmentLabel}</div>
                                {isBottleneck && (
                                  <Badge variant="error" size="sm" className="mt-1">
                                    ⚠️ Bottleneck
                                  </Badge>
                                )}
                              </div>
                            </div>
                          </td>

                          {/* Article */}
                          <td className="px-4 py-4">
                            <div className="font-medium text-gray-900">{wip.articleCode}</div>
                            <div className="text-xs text-gray-600">{wip.articleName}</div>
                          </td>

                          {/* SPK */}
                          <td className="px-4 py-4">
                            <button
                              onClick={() => navigate(`/ppic/spk/${wip.spkNumber}`)}
                              className="text-blue-600 hover:text-blue-800 font-medium hover:underline"
                            >
                              {wip.spkNumber}
                            </button>
                          </td>

                          {/* Buffer Stock */}
                          <td className="px-4 py-4 text-center">
                            <div className={cn(
                              'inline-flex items-center justify-center px-4 py-2 rounded-lg font-bold text-lg',
                              wip.bufferStock < 0 ? 'bg-black text-white' :
                              wip.status === 'ABUNDANT' ? 'bg-green-100 text-green-800' :
                              wip.status === 'SUFFICIENT' ? 'bg-blue-100 text-blue-800' :
                              wip.status === 'LOW' ? 'bg-yellow-100 text-yellow-800' :
                              'bg-red-100 text-red-800'
                            )}>
                              {formatNumber(wip.bufferStock)} pcs
                            </div>
                            {wip.bufferStock < 0 && (
                              <p className="text-xs text-red-600 mt-1 font-semibold">
                                MATERIAL DEBT
                              </p>
                            )}
                          </td>

                          {/* Cumulative Produced */}
                          <td className="px-4 py-4 text-center">
                            <div className="font-semibold text-green-700">
                              {formatNumber(wip.cumulativeProduced)} pcs
                            </div>
                          </td>

                          {/* Cumulative Consumed */}
                          <td className="px-4 py-4 text-center">
                            <div className="font-semibold text-blue-700">
                              {formatNumber(wip.cumulativeConsumed)} pcs
                            </div>
                          </td>

                          {/* Target */}
                          <td className="px-4 py-4 text-center">
                            <div className="font-semibold text-gray-900">
                              {formatNumber(wip.targetQty)} pcs
                            </div>
                            <div className="text-xs text-gray-600 mt-1">
                              {((wip.cumulativeProduced / wip.targetQty) * 100).toFixed(0)}%
                            </div>
                          </td>

                          {/* Status */}
                          <td className="px-4 py-4 text-center">
                            <Badge variant={getStatusBadge(wip.status).variant}>
                              {getStatusBadge(wip.status).label}
                            </Badge>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>

          {/* Material Flow Visualization */}
          {flowData && flowData.length > 0 && (
            <Card variant="bordered">
              <CardHeader>
                <CardTitle>🔄 Today's Material Flow (Department → Department)</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {flowData.map((flow, idx) => (
                    <div key={idx} className="flex items-center gap-4 p-4 bg-gray-50 rounded-lg">
                      <div className="flex-1 flex items-center gap-3">
                        <div className="bg-blue-100 px-4 py-2 rounded-lg font-semibold text-blue-800">
                          {flow.from}
                        </div>
                        <div className="flex-1 border-t-2 border-dashed border-gray-400 relative">
                          <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 bg-white px-3 py-1 rounded-full border-2 border-green-500">
                            <span className="text-green-700 font-bold">
                              {formatNumber(flow.todayTransferred)} pcs
                            </span>
                          </div>
                        </div>
                        <div className="text-2xl text-green-600">→</div>
                        <div className="bg-green-100 px-4 py-2 rounded-lg font-semibold text-green-800">
                          {flow.to}
                        </div>
                      </div>
                      {flow.pendingTransfer > 0 && (
                        <Badge variant="warning">
                          ⏳ Pending: {formatNumber(flow.pendingTransfer)} pcs
                        </Badge>
                      )}
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Alerts & Recommendations */}
          <Card variant="elevated" className="bg-gradient-to-r from-orange-50 to-red-50 border-2 border-orange-300">
            <CardHeader>
              <CardTitle>⚠️ Alerts & Recommendations</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {/* Bottleneck Alert */}
                {bottleneckDept && (
                  <div className="bg-white p-4 rounded-lg border-l-4 border-red-500">
                    <h4 className="font-semibold text-red-800 mb-2">🚨 Bottleneck Detected</h4>
                    <p className="text-sm text-gray-700">
                      <strong>{bottleneckDept}</strong> has the lowest cumulative output. 
                      Consider allocating more resources or investigating delays.
                    </p>
                  </div>
                )}

                {/* Negative Stock Alert */}
                {wipData.some(w => w.bufferStock < 0) && (
                  <div className="bg-white p-4 rounded-lg border-l-4 border-black">
                    <h4 className="font-semibold text-gray-900 mb-2">⚫ Material Debt Detected</h4>
                    <p className="text-sm text-gray-700 mb-2">
                      The following departments have negative WIP buffer (consumed more than received):
                    </p>
                    <ul className="text-sm text-gray-700 space-y-1 list-disc list-inside">
                      {wipData.filter(w => w.bufferStock < 0).map((w, i) => (
                        <li key={i}>
                          <strong>{w.departmentLabel}</strong>: {formatNumber(w.bufferStock)} pcs 
                          (Reconciliation required within 24 hours)
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Low Stock Alert */}
                {wipData.some(w => w.status === 'LOW' || w.status === 'CRITICAL') && (
                  <div className="bg-white p-4 rounded-lg border-l-4 border-yellow-500">
                    <h4 className="font-semibold text-yellow-800 mb-2">🟡 Low Stock Alert</h4>
                    <p className="text-sm text-gray-700">
                      Some departments are running low on WIP buffer. Upstream departments should prioritize production.
                    </p>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </>
      ) : (
        <Card variant="bordered">
          <CardContent className="text-center py-12">
            <div className="text-gray-400 text-6xl mb-4">📊</div>
            <h3 className="text-lg font-semibold text-gray-700 mb-2">No WIP Data Available</h3>
            <p className="text-gray-600 mb-4">
              Start production to see real-time WIP buffer tracking.
            </p>
            <Button variant="primary" onClick={() => navigate('/production/calendar')}>
              Go to Production Calendar
            </Button>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
