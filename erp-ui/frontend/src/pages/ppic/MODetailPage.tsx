import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import toast from 'react-hot-toast';
import { api } from '../../api';
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Badge } from '../../components/ui/badge';
import { cn, formatDate, formatNumber, calculatePercentage } from '../../lib/utils';

/**
 * MO Detail Page - PPIC Module
 * 
 * Critical Features:
 * - Display complete MO information
 * - Show PARTIAL → RELEASED status transition buttons
 * - Display Week & Destination (inherited from PO Label)
 * - Show PO Kain (TRIGGER 1) and PO Label (TRIGGER 2) linkage
 * - Display SPK breakdown (Body & Baju parallel)
 * - Material allocation status
 * - Production progress tracking
 * - Audit trail
 * 
 * Status Transitions:
 * - DRAFT → PARTIAL: When PO Kain (TRIGGER 1) is received
 * - PARTIAL → RELEASED: When PO Label (TRIGGER 2) is received
 * - RELEASED → COMPLETED: When all production is finished
 */

interface MODetail {
  id: number;
  moNumber: string;
  moDate: string;
  articleCode: string;
  articleName: string;
  targetQty: number;
  bufferQty: number;
  finalQty: number;
  actualQty: number;
  week?: string;
  destination?: string;
  status: 'DRAFT' | 'PARTIAL' | 'RELEASED' | 'COMPLETED';
  expectedStartDate: string;
  expectedCompletionDate: string;
  poKainId?: number;
  poKainNumber?: string;
  poKainReceivedDate?: string;
  poLabelId: number;
  poLabelNumber: string;
  poLabelReceivedDate?: string;
  spks: Array<{
    id: number;
    spkNumber: string;
    department: string;
    targetQty: number;
    actualQty: number;
    status: string;
  }>;
  materialAllocation: Array<{
    materialCode: string;
    materialName: string;
    requiredQty: number;
    allocatedQty: number;
    availableQty: number;
    uom: string;
  }>;
  notes?: string;
  createdAt: string;
  createdBy: string;
  updatedAt: string;
  updatedBy: string;
}

export default function MODetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [showReleaseConfirm, setShowReleaseConfirm] = useState(false);

  // Fetch MO details
  const { data: mo, isLoading } = useQuery<MODetail>({
    queryKey: ['mo-detail', id],
    queryFn: () => api.ppic.getMO(Number(id)),
    enabled: !!id,
    refetchInterval: 30000, // Refresh every 30 seconds
  });

  // Release PARTIAL mutation
  const releasePartialMutation = useMutation({
    mutationFn: () => api.ppic.releasePartial(Number(id)),
    onSuccess: () => {
      toast.success('MO released to PARTIAL status! Cutting & Embroidery unlocked.');
      queryClient.invalidateQueries({ queryKey: ['mo-detail', id] });
    },
    onError: (error: any) => {
      toast.error(error?.message || 'Failed to release MO to PARTIAL.');
    },
  });

  // Release FULL mutation
  const releaseFullMutation = useMutation({
    mutationFn: () => api.ppic.releaseFull(Number(id)),
    onSuccess: () => {
      toast.success('MO released to FULL status! All departments unlocked.');
      queryClient.invalidateQueries({ queryKey: ['mo-detail', id] });
      setShowReleaseConfirm(false);
    },
    onError: (error: any) => {
      toast.error(error?.message || 'Failed to release MO to FULL.');
    },
  });

  // Status badge helper
  const getStatusBadge = (status: MODetail['status']) => {
    const configs = {
      DRAFT: { variant: 'secondary' as const, label: '📝 DRAFT', description: 'Waiting PO Kain' },
      PARTIAL: { variant: 'warning' as const, label: '🟡 PARTIAL', description: 'Cutting & Embroidery only' },
      RELEASED: { variant: 'success' as const, label: '✅ RELEASED', description: 'All departments active' },
      COMPLETED: { variant: 'success' as const, label: '✅ COMPLETED', description: 'Production finished' },
    };
    return configs[status];
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-500 mx-auto"></div>
          <p className="text-gray-600 mt-4">Loading MO details...</p>
        </div>
      </div>
    );
  }

  if (!mo) {
    return (
      <div className="p-6">
        <Card variant="bordered">
          <CardContent className="text-center py-12">
            <p className="text-gray-600 text-lg">MO not found.</p>
            <Button variant="primary" onClick={() => navigate('/ppic/mo')} className="mt-4">
              Back to MO List
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  const statusConfig = getStatusBadge(mo.status);
  const progressPercent = calculatePercentage(mo.actualQty, mo.targetQty);

  return (
    <div className="p-6 space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-3xl font-bold text-gray-900">{mo.moNumber}</h1>
            <Badge variant={statusConfig.variant} className="text-lg px-4 py-1">
              {statusConfig.label}
            </Badge>
          </div>
          <p className="text-gray-600 mt-1">{statusConfig.description}</p>
        </div>
        <Button variant="secondary" onClick={() => navigate('/ppic/mo')}>
          ← Back to List
        </Button>
      </div>

      {/* Status Transition Buttons */}
      {mo.status === 'DRAFT' && mo.poKainNumber && (
        <Card variant="elevated" className="bg-gradient-to-r from-yellow-50 to-orange-50 border-2 border-yellow-400">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  🔓 Ready to Release PARTIAL
                </h3>
                <p className="text-gray-700">
                  PO Kain ({mo.poKainNumber}) has been received. You can now release this MO to PARTIAL status
                  to unlock <strong>Cutting & Embroidery</strong> departments.
                </p>
                <p className="text-sm text-gray-600 mt-2">
                  Note: Sewing, Finishing, and Packing will remain locked until PO Label is received (TRIGGER 2).
                </p>
              </div>
              <Button
                variant="warning"
                size="lg"
                onClick={() => releasePartialMutation.mutate()}
                loading={releasePartialMutation.isPending}
              >
                🔓 Release to PARTIAL
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {mo.status === 'PARTIAL' && mo.poLabelReceivedDate && (
        <Card variant="elevated" className="bg-gradient-to-r from-green-50 to-blue-50 border-2 border-green-400">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  🎉 Ready to Release FULL
                </h3>
                <p className="text-gray-700">
                  PO Label ({mo.poLabelNumber}) has been received on {formatDate(mo.poLabelReceivedDate)}!
                  You can now release this MO to FULL (RELEASED) status to unlock <strong>ALL departments</strong>.
                </p>
                <p className="text-sm text-gray-600 mt-2">
                  Week & Destination will be auto-inherited: <strong>{mo.week}</strong> → <strong>{mo.destination}</strong>
                </p>
              </div>
              <Button
                variant="success"
                size="lg"
                onClick={() => setShowReleaseConfirm(true)}
              >
                ✅ Release to FULL
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Confirmation Modal for Full Release */}
      {showReleaseConfirm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <Card variant="elevated" className="max-w-lg w-full mx-4">
            <CardHeader>
              <CardTitle>Confirm Full Release</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-gray-700">
                Are you sure you want to release this MO to <strong>FULL (RELEASED)</strong> status?
              </p>
              <div className="mt-4 bg-blue-50 border-l-4 border-blue-500 p-4 rounded-r-lg">
                <p className="text-sm text-gray-700">
                  <strong>This action will:</strong>
                </p>
                <ul className="text-sm text-gray-700 mt-2 space-y-1 list-disc list-inside">
                  <li>Unlock all production departments (Sewing, Finishing, Packing)</li>
                  <li>Auto-inherit Week: <strong>{mo.week}</strong></li>
                  <li>Auto-inherit Destination: <strong>{mo.destination}</strong></li>
                  <li>Trigger SPK auto-generation for all departments</li>
                  <li>Allocate materials from warehouse</li>
                </ul>
              </div>
            </CardContent>
            <CardFooter className="flex justify-end gap-2">
              <Button variant="secondary" onClick={() => setShowReleaseConfirm(false)}>
                Cancel
              </Button>
              <Button
                variant="success"
                onClick={() => releaseFullMutation.mutate()}
                loading={releaseFullMutation.isPending}
              >
                ✅ Confirm Release
              </Button>
            </CardFooter>
          </Card>
        </div>
      )}

      {/* MO Information Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: MO Details */}
        <div className="lg:col-span-2 space-y-6">
          {/* Basic Info */}
          <Card variant="bordered">
            <CardHeader>
              <CardTitle>📝 MO Information</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-gray-600">MO Number</p>
                  <p className="font-semibold text-gray-900">{mo.moNumber}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">MO Date</p>
                  <p className="font-semibold text-gray-900">{formatDate(mo.moDate)}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Article Code</p>
                  <p className="font-semibold text-gray-900">{mo.articleCode}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Article Name</p>
                  <p className="font-semibold text-gray-900">{mo.articleName}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Week & Destination (INHERITED) */}
          <Card variant="elevated" className="bg-gradient-to-r from-green-50 to-blue-50 border-2 border-green-300">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <span>🔗 Week & Destination</span>
                <Badge variant="warning">AUTO-INHERITED from PO Label</Badge>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-white p-4 rounded-lg border-2 border-green-400">
                  <p className="text-sm text-gray-600 mb-1">Week</p>
                  <p className="text-2xl font-bold text-green-700">{mo.week || 'Not inherited yet'}</p>
                </div>
                <div className="bg-white p-4 rounded-lg border-2 border-green-400">
                  <p className="text-sm text-gray-600 mb-1">Destination</p>
                  <p className="text-2xl font-bold text-green-700">{mo.destination || 'Not inherited yet'}</p>
                </div>
              </div>
              <p className="text-xs text-green-700 mt-3 font-medium">
                ✅ These fields are automatically inherited from PO Label and propagate to all SPKs and production records.
              </p>
            </CardContent>
          </Card>

          {/* Production Progress */}
          <Card variant="bordered">
            <CardHeader>
              <CardTitle>📊 Production Progress</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {/* Quantity Breakdown */}
                <div className="grid grid-cols-3 gap-4">
                  <div className="bg-blue-50 p-4 rounded-lg">
                    <p className="text-sm text-gray-600">Target Qty</p>
                    <p className="text-2xl font-bold text-blue-700">{formatNumber(mo.targetQty)}</p>
                    <p className="text-xs text-gray-600">From PO Label</p>
                  </div>
                  <div className="bg-purple-50 p-4 rounded-lg">
                    <p className="text-sm text-gray-600">Buffer Qty</p>
                    <p className="text-2xl font-bold text-purple-700">{formatNumber(mo.bufferQty)}</p>
                    <p className="text-xs text-gray-600">Flexible Target</p>
                  </div>
                  <div className="bg-green-50 p-4 rounded-lg">
                    <p className="text-sm text-gray-600">Final Target</p>
                    <p className="text-2xl font-bold text-green-700">{formatNumber(mo.finalQty)}</p>
                    <p className="text-xs text-gray-600">With Buffer</p>
                  </div>
                </div>

                {/* Progress Bar */}
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium text-gray-700">Actual Output</span>
                    <span className="text-lg font-bold text-gray-900">
                      {formatNumber(mo.actualQty)} / {formatNumber(mo.targetQty)} pcs
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-4">
                    <div
                      className={cn(
                        'h-4 rounded-full transition-all',
                        progressPercent >= 100 ? 'bg-green-500' :
                        progressPercent >= 75 ? 'bg-blue-500' :
                        progressPercent >= 50 ? 'bg-yellow-500' : 'bg-red-500'
                      )}
                      style={{ width: `${Math.min(progressPercent, 100)}%` }}
                    />
                  </div>
                  <p className="text-sm text-gray-600 mt-1">
                    Achievement: <span className="font-semibold">{progressPercent}%</span>
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* SPK Breakdown */}
          <Card variant="bordered">
            <CardHeader>
              <CardTitle>📋 SPK Breakdown</CardTitle>
            </CardHeader>
            <CardContent>
              {mo.spks && mo.spks.length > 0 ? (
                <div className="space-y-3">
                  {mo.spks.map((spk) => (
                    <div
                      key={spk.id}
                      className="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
                    >
                      <div className="flex-1">
                        <div className="flex items-center gap-2">
                          <p className="font-semibold text-gray-900">{spk.spkNumber}</p>
                          <Badge variant="secondary" size="sm">{spk.department}</Badge>
                        </div>
                        <div className="flex items-center gap-4 mt-2">
                          <p className="text-sm text-gray-600">
                            Target: <span className="font-medium">{formatNumber(spk.targetQty)} pcs</span>
                          </p>
                          <p className="text-sm text-gray-600">
                            Actual: <span className="font-medium">{formatNumber(spk.actualQty)} pcs</span>
                          </p>
                          <p className="text-sm text-gray-600">
                            Progress: <span className="font-semibold">{calculatePercentage(spk.actualQty, spk.targetQty)}%</span>
                          </p>
                        </div>
                      </div>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => navigate(`/ppic/spk/${spk.id}`)}
                      >
                        View →
                      </Button>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-gray-600 text-center py-4">No SPKs generated yet.</p>
              )}
            </CardContent>
          </Card>

          {/* Material Allocation */}
          <Card variant="bordered">
            <CardHeader>
              <CardTitle>📦 Material Allocation Status</CardTitle>
            </CardHeader>
            <CardContent>
              {mo.materialAllocation && mo.materialAllocation.length > 0 ? (
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-4 py-2 text-left">Material</th>
                        <th className="px-4 py-2 text-center">Required</th>
                        <th className="px-4 py-2 text-center">Allocated</th>
                        <th className="px-4 py-2 text-center">Available</th>
                        <th className="px-4 py-2 text-center">Status</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y">
                      {mo.materialAllocation.map((mat, idx) => {
                        const allocationPercent = calculatePercentage(mat.allocatedQty, mat.requiredQty);
                        return (
                          <tr key={idx}>
                            <td className="px-4 py-2">
                              <div className="font-medium">{mat.materialCode}</div>
                              <div className="text-xs text-gray-600">{mat.materialName}</div>
                            </td>
                            <td className="px-4 py-2 text-center">
                              {formatNumber(mat.requiredQty)} {mat.uom}
                            </td>
                            <td className="px-4 py-2 text-center font-semibold">
                              {formatNumber(mat.allocatedQty)} {mat.uom}
                            </td>
                            <td className="px-4 py-2 text-center">
                              {formatNumber(mat.availableQty)} {mat.uom}
                            </td>
                            <td className="px-4 py-2 text-center">
                              <Badge
                                variant={
                                  allocationPercent >= 100 ? 'success' :
                                  allocationPercent >= 50 ? 'warning' : 'error'
                                }
                                size="sm"
                              >
                                {allocationPercent}%
                              </Badge>
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              ) : (
                <p className="text-gray-600 text-center py-4">No material allocation data yet.</p>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Right Column: Status & Actions */}
        <div className="space-y-6">
          {/* PO Linkage */}
          <Card variant="bordered">
            <CardHeader>
              <CardTitle>🔗 PO Linkage</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* PO Kain (TRIGGER 1) */}
              <div className="bg-orange-50 p-4 rounded-lg border-2 border-orange-300">
                <p className="text-sm font-semibold text-orange-800 mb-2">🔑 TRIGGER 1: PO Kain</p>
                {mo.poKainNumber ? (
                  <>
                    <p className="font-medium text-gray-900">{mo.poKainNumber}</p>
                    {mo.poKainReceivedDate && (
                      <p className="text-xs text-gray-600 mt-1">
                        Received: {formatDate(mo.poKainReceivedDate)}
                      </p>
                    )}
                    <Badge variant="success" size="sm" className="mt-2">
                      ✅ Received
                    </Badge>
                  </>
                ) : (
                  <p className="text-sm text-gray-600">Not linked yet</p>
                )}
              </div>

              {/* PO Label (TRIGGER 2) */}
              <div className="bg-purple-50 p-4 rounded-lg border-2 border-purple-300">
                <p className="text-sm font-semibold text-purple-800 mb-2">🔑 TRIGGER 2: PO Label</p>
                <p className="font-medium text-gray-900">{mo.poLabelNumber}</p>
                {mo.poLabelReceivedDate ? (
                  <>
                    <p className="text-xs text-gray-600 mt-1">
                      Received: {formatDate(mo.poLabelReceivedDate)}
                    </p>
                    <Badge variant="success" size="sm" className="mt-2">
                      ✅ Received
                    </Badge>
                  </>
                ) : (
                  <Badge variant="warning" size="sm" className="mt-2">
                    ⏳ Waiting
                  </Badge>
                )}
              </div>
            </CardContent>
          </Card>

          {/* Schedule */}
          <Card variant="bordered">
            <CardHeader>
              <CardTitle>📅 Production Schedule</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div>
                <p className="text-sm text-gray-600">Expected Start</p>
                <p className="font-semibold text-gray-900">{formatDate(mo.expectedStartDate)}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Expected Completion</p>
                <p className="font-semibold text-gray-900">{formatDate(mo.expectedCompletionDate)}</p>
              </div>
            </CardContent>
          </Card>

          {/* Notes */}
          {mo.notes && (
            <Card variant="bordered">
              <CardHeader>
                <CardTitle>📌 Notes</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-gray-700">{mo.notes}</p>
              </CardContent>
            </Card>
          )}

          {/* Audit Trail */}
          <Card variant="bordered">
            <CardHeader>
              <CardTitle>🕐 Audit Trail</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3 text-sm">
              <div>
                <p className="text-gray-600">Created</p>
                <p className="font-medium text-gray-900">{formatDate(mo.createdAt)}</p>
                <p className="text-xs text-gray-600">by {mo.createdBy}</p>
              </div>
              <div>
                <p className="text-gray-600">Last Updated</p>
                <p className="font-medium text-gray-900">{formatDate(mo.updatedAt)}</p>
                <p className="text-xs text-gray-600">by {mo.updatedBy}</p>
              </div>
            </CardContent>
          </Card>

          {/* Actions */}
          <Card variant="bordered">
            <CardHeader>
              <CardTitle>⚡ Quick Actions</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              <Button
                variant="primary"
                fullWidth
                onClick={() => navigate(`/ppic/spk?moId=${mo.id}`)}
              >
                📋 View All SPKs
              </Button>
              <Button
                variant="secondary"
                fullWidth
                onClick={() => navigate(`/ppic/material-allocation/${mo.id}`)}
              >
                📦 Material Allocation
              </Button>
              {mo.status === 'DRAFT' && (
                <Button
                  variant="warning"
                  fullWidth
                  onClick={() => navigate(`/ppic/mo/${mo.id}/edit`)}
                >
                  ✏️ Edit MO
                </Button>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
