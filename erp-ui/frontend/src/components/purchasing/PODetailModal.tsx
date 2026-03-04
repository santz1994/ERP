/**
 * Copyright (c) 2026 PT Quty Karunia / Daniel Rizaldy - All Rights Reserved
 * File: PODetailModal.tsx | Author: Daniel Rizaldy | Date: 2026-03-02
 * Purpose: View PO detail + status actions (Send, Cancel)
 */

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { format } from 'date-fns';
import toast from 'react-hot-toast';
import axios from 'axios';
import {
  X,
  FileText,
  Package,
  Truck,
  CheckCircle,
  XCircle,
  Clock,
  User,
  Calendar,
  AlertTriangle,
  Trash2,
} from 'lucide-react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { formatCurrency } from '@/lib/utils';
import { useAuthStore } from '@/store';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

interface PODetailItem {
  material_code: string;
  material_name: string;
  supplier_id: number;
  quantity: number;
  uom: string;
  unit_price: number;
  total_price: number;
  description?: string;
}

interface PODetail {
  id: number;
  po_number: string;
  po_type: string | null;
  status: string | null;
  supplier_id: number;
  supplier_name: string;
  order_date: string;
  expected_date: string;
  total_amount: number;
  currency: string;
  article_id: number | null;
  article_name: string | null;
  article_qty: number | null;
  week: string | null;
  destination: string | null;
  source_po_kain_id: number | null;
  source_po_number: string | null;
  notes: string | null;
  created_at: string | null;
  items: PODetailItem[];
  // PO KAIN batch split
  linked_labels: {
    id: number;
    po_number: string;
    status: string | null;
    week: string | null;
    destination: string | null;
    article_qty: number;
    order_date: string | null;
  }[];
  total_allocated: number;
  remaining_qty: number;
  // Manufacturing Order (PO KAIN only)
  linked_mo: {
    id: number;
    batch_number: string;
    state: string | null;
    trigger_mode: string;
    qty_planned: number;
    qty_produced: number;
    routing_type: string | null;
    created_at: string | null;
    work_orders: {
      id: number;
      wo_number: string;
      department: string | null;
      status: string | null;
      target_qty: number;
      output_qty: number;
      sequence: number | null;
    }[];
  } | null;
}

interface PODetailModalProps {
  poId: number | null;
  isOpen: boolean;
  onClose: () => void;
  onStatusChanged?: () => void;
}

const STATUS_COLORS: Record<string, string> = {
  Draft: 'bg-gray-100 text-gray-800',
  Sent: 'bg-blue-100 text-blue-800',
  Received: 'bg-orange-100 text-orange-800',
  Done: 'bg-green-100 text-green-800',
  Cancelled: 'bg-red-100 text-red-800',
};

const TYPE_COLORS: Record<string, string> = {
  KAIN: 'bg-purple-100 text-purple-800',
  LABEL: 'bg-blue-100 text-blue-800',
  ACCESSORIES: 'bg-gray-100 text-gray-800',
};

const ADMIN_ROLES_PO = ['Admin', 'Superadmin', 'Developer'];

export default function PODetailModal({ poId, isOpen, onClose, onStatusChanged }: PODetailModalProps) {
  const queryClient = useQueryClient();
  const [confirmAction, setConfirmAction] = useState<string | null>(null);

  // Delete PO state
  const { user } = useAuthStore();
  const isAdmin = ADMIN_ROLES_PO.includes(user?.role ?? '');
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [showRequestModal, setShowRequestModal] = useState(false);
  const [deleteReason, setDeleteReason] = useState('');
  const [directDeleteReason, setDirectDeleteReason] = useState('');

  const token = () => localStorage.getItem('access_token');

  const { data: po, isLoading, error } = useQuery<PODetail>({
    queryKey: ['po-detail', poId],
    queryFn: async () => {
      const response = await axios.get(`${API_BASE}/purchasing/purchase-orders/${poId}`, {
        headers: { Authorization: `Bearer ${token()}` },
      });
      return response.data;
    },
    enabled: isOpen && !!poId,
  });

  const statusMutation = useMutation({
    mutationFn: async (newStatus: string) => {
      const response = await axios.patch(
        `${API_BASE}/purchasing/purchase-orders/${poId}/status?new_status=${encodeURIComponent(newStatus)}`,
        {},
        { headers: { Authorization: `Bearer ${token()}` } }
      );
      return response.data;
    },
    onSuccess: (data) => {
      const moInfo = data.mo_created;
      const stockInfo = data.stock_received;
      if (moInfo?.action === 'created') {
        toast.success(
          `${data.message}\n✅ MO ${moInfo.mo_production_batch || moInfo.batch_number} dibuat — WO: ${moInfo.work_orders_created?.join(', ')}`,
          { duration: 6000 }
        );
      } else if (moInfo?.action === 'released') {
        toast.success(
          `${data.message}\n🚀 Produksi penuh dirilis! WO baru: ${moInfo.work_orders_created?.join(', ')}`,
          { duration: 6000 }
        );
      } else if (stockInfo?.received_lines > 0) {
        toast.success(
          `${data.message}\n📦 ${stockInfo.received_lines} material masuk ke stok gudang!`,
          { duration: 5000 }
        );
      } else {
        toast.success(data.message || 'Status updated');
      }
      queryClient.invalidateQueries({ queryKey: ['po-detail', poId] });
      queryClient.invalidateQueries({ queryKey: ['purchase-orders'] });
      setConfirmAction(null);
      onStatusChanged?.();
    },
    onError: (error: any) => {
      const msg = error?.response?.data?.detail || error?.message || 'Failed to update status';
      toast.error(msg);
      setConfirmAction(null);
    },
  });

  // ── Generate MO (manual retroactive trigger) ────────────────────────────────
  const generateMOMutation = useMutation({
    mutationFn: async () => {
      const response = await axios.post(
        `${API_BASE}/purchasing/purchase-orders/${poId}/generate-mo`,
        {},
        { headers: { Authorization: `Bearer ${token()}` } }
      );
      return response.data;
    },
    onSuccess: (data) => {
      const mo = data.mo_info;
      const batchLabel = mo?.mo_production_batch || mo?.batch_number || 'N/A';
      toast.success(`MO berhasil dibuat! Batch: ${batchLabel}`, { duration: 5000 });
      queryClient.invalidateQueries({ queryKey: ['po-detail', poId] });
      queryClient.invalidateQueries({ queryKey: ['purchase-orders'] });
    },
    onError: (e: any) => toast.error(e?.response?.data?.detail ?? 'Gagal generate MO'),
  });

  // ── Delete / Request-Delete mutations ─────────────────────────────────────
  const directDeleteMutation = useMutation({
    mutationFn: async (reason: string) => {
      await axios.delete(`${API_BASE}/purchasing/purchase-orders/${poId}`, {
        data: { reason },
        headers: { Authorization: `Bearer ${token()}` },
      });
    },
    onSuccess: () => {
      toast.success('PO deleted successfully.');
      queryClient.invalidateQueries({ queryKey: ['purchase-orders'] });
      onClose();
      onStatusChanged?.();
    },
    onError: (e: any) => toast.error(e?.response?.data?.detail ?? 'Failed to delete PO'),
  });

  const requestDeleteMutation = useMutation({
    mutationFn: async (reason: string) => {
      await axios.post(
        `${API_BASE}/purchasing/purchase-orders/${poId}/request-delete`,
        { reason },
        { headers: { Authorization: `Bearer ${token()}` } }
      );
    },
    onSuccess: () => {
      toast.success('Deletion request submitted. Menunggu persetujuan atasan.');
      setShowRequestModal(false);
      setDeleteReason('');
    },
    onError: (e: any) => toast.error(e?.response?.data?.detail ?? 'Failed to submit request'),
  });

  if (!isOpen) return null;

  const poTypeLabel = po?.po_type === 'KAIN' ? 'PO Kain (Fabric)' :
    po?.po_type === 'LABEL' ? 'PO Label' :
    po?.po_type === 'ACCESSORIES' ? 'PO Accessories' : po?.po_type || '-';

  const canSend = po?.status === 'Draft';
  const canCancel = po?.status === 'Draft' || po?.status === 'Sent';
  const canReceive = po?.status === 'Sent';
  const canDone = po?.status === 'Received';

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      {/* Backdrop */}
      <div className="fixed inset-0 bg-black bg-opacity-50" onClick={onClose} />

      {/* Modal */}
      <div className="relative min-h-screen flex items-start justify-center p-4 pt-8">
        <div className="relative bg-white rounded-xl shadow-2xl w-full max-w-4xl">
          {/* Header */}
          <div className="flex items-center justify-between p-6 border-b border-gray-200">
            <div className="flex items-center gap-3">
              <FileText className="w-6 h-6 text-blue-600" />
              <div>
                <h2 className="text-xl font-bold text-gray-900">
                  {po?.po_number || 'Loading...'}
                </h2>
                <p className="text-sm text-gray-500">Purchase Order Detail</p>
              </div>
              {po?.po_type && (
                <span className={`ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${TYPE_COLORS[po.po_type] || 'bg-gray-100 text-gray-800'}`}>
                  {po.po_type}
                </span>
              )}
              {po?.status && (
                <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${STATUS_COLORS[po.status] || 'bg-gray-100 text-gray-800'}`}>
                  {po.status}
                </span>
              )}
            </div>
            <button onClick={onClose} className="p-2 hover:bg-gray-100 rounded-lg transition-colors">
              <X className="w-5 h-5 text-gray-500" />
            </button>
          </div>

          {/* Body */}
          <div className="p-6 space-y-6">
            {isLoading && (
              <div className="flex items-center justify-center py-12">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" />
              </div>
            )}

            {error && (
              <div className="flex items-center gap-2 text-red-600 bg-red-50 p-4 rounded-lg">
                <AlertTriangle className="w-5 h-5" />
                <span>Failed to load PO detail. Please try again.</span>
              </div>
            )}

            {po && (
              <>
                {/* Info Grid */}
                <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                  <div className="bg-gray-50 rounded-lg p-4">
                    <div className="flex items-center gap-2 text-gray-500 text-xs mb-1">
                      <User className="w-3 h-3" /> Supplier
                    </div>
                    <p className="font-semibold text-gray-900 text-sm">{po.supplier_name}</p>
                  </div>

                  <div className="bg-gray-50 rounded-lg p-4">
                    <div className="flex items-center gap-2 text-gray-500 text-xs mb-1">
                      <Calendar className="w-3 h-3" /> Order Date
                    </div>
                    <p className="font-semibold text-gray-900 text-sm">
                      {po.order_date ? format(new Date(po.order_date), 'dd MMM yyyy') : '-'}
                    </p>
                  </div>

                  <div className="bg-gray-50 rounded-lg p-4">
                    <div className="flex items-center gap-2 text-gray-500 text-xs mb-1">
                      <Truck className="w-3 h-3" /> Expected Delivery
                    </div>
                    <p className="font-semibold text-gray-900 text-sm">
                      {po.expected_date ? format(new Date(po.expected_date), 'dd MMM yyyy') : '-'}
                    </p>
                  </div>

                  {po.article_name && (
                    <div className="bg-purple-50 rounded-lg p-4">
                      <div className="flex items-center gap-2 text-purple-500 text-xs mb-1">
                        <Package className="w-3 h-3" /> Article
                      </div>
                      <p className="font-semibold text-purple-900 text-sm">{po.article_name}</p>
                      {po.article_qty && (
                        <p className="text-xs text-purple-600 mt-0.5">Qty: {po.article_qty.toLocaleString()} pcs</p>
                      )}
                    </div>
                  )}

                  {po.week && (
                    <div className="bg-blue-50 rounded-lg p-4">
                      <div className="text-blue-500 text-xs mb-1">Week / Destination</div>
                      <p className="font-semibold text-blue-900 text-sm">W{po.week}</p>
                      {po.destination && <p className="text-xs text-blue-600 mt-0.5">{po.destination}</p>}
                    </div>
                  )}

                  {po.source_po_number && (
                    <div className="bg-yellow-50 rounded-lg p-4">
                      <div className="text-yellow-600 text-xs mb-1">Source PO Kain</div>
                      <p className="font-semibold text-yellow-900 text-sm">{po.source_po_number}</p>
                    </div>
                  )}
                </div>

                {/* PO KAIN: Batch-split (linked PO LABELs) */}
                {po.po_type === 'KAIN' && po.article_qty && (
                  <div>
                    <h3 className="text-base font-semibold text-gray-900 mb-3 flex items-center gap-2">
                      <Truck className="w-4 h-4 text-purple-600" />
                      Delivery Batches (PO LABEL)
                      <span className="ml-auto text-xs font-normal text-gray-500">
                        {po.total_allocated?.toLocaleString() || 0} / {po.article_qty.toLocaleString()} pcs allocated
                      </span>
                    </h3>

                    {/* Progress bar */}
                    <div className="w-full bg-gray-100 rounded-full h-2 mb-3">
                      <div
                        className={`h-2 rounded-full transition-all ${
                          (po.total_allocated || 0) >= po.article_qty ? 'bg-green-500' : 'bg-purple-500'
                        }`}
                        style={{ width: `${Math.min(100, Math.round(((po.total_allocated || 0) / po.article_qty) * 100))}%` }}
                      />
                    </div>

                    {(po.linked_labels?.length ?? 0) === 0 ? (
                      <p className="text-sm text-gray-400 italic py-2">Belum ada PO LABEL dibuat untuk PO KAIN ini.</p>
                    ) : (
                      <div className="overflow-x-auto rounded-lg border border-purple-100">
                        <table className="min-w-full divide-y divide-purple-100 text-sm">
                          <thead className="bg-purple-50">
                            <tr>
                              <th className="px-4 py-2 text-left text-xs font-medium text-purple-600 uppercase">#</th>
                              <th className="px-4 py-2 text-left text-xs font-medium text-purple-600 uppercase">PO Number</th>
                              <th className="px-4 py-2 text-left text-xs font-medium text-purple-600 uppercase">Week</th>
                              <th className="px-4 py-2 text-left text-xs font-medium text-purple-600 uppercase">Destination</th>
                              <th className="px-4 py-2 text-right text-xs font-medium text-purple-600 uppercase">Qty (pcs)</th>
                              <th className="px-4 py-2 text-left text-xs font-medium text-purple-600 uppercase">Status</th>
                            </tr>
                          </thead>
                          <tbody className="bg-white divide-y divide-purple-50">
                            {po.linked_labels.map((lbl, idx) => (
                              <tr key={lbl.id} className="hover:bg-purple-50">
                                <td className="px-4 py-2 text-gray-400 text-xs">{idx + 1}</td>
                                <td className="px-4 py-2 font-mono text-xs text-purple-800">{lbl.po_number}</td>
                                <td className="px-4 py-2 text-gray-700 text-xs">{lbl.week ? `W${lbl.week}` : '-'}</td>
                                <td className="px-4 py-2 text-gray-700 text-xs">{lbl.destination || '-'}</td>
                                <td className="px-4 py-2 text-right font-medium text-gray-900">{lbl.article_qty.toLocaleString()}</td>
                                <td className="px-4 py-2">
                                  <span className={`px-2 py-0.5 rounded text-xs font-medium ${
                                    STATUS_COLORS[lbl.status || ''] || 'bg-gray-100 text-gray-600'
                                  }`}>{lbl.status || '?'}</span>
                                </td>
                              </tr>
                            ))}
                          </tbody>
                          <tfoot className="bg-purple-50">
                            <tr>
                              <td colSpan={4} className="px-4 py-2 text-right text-xs font-semibold text-purple-700">Total allocated</td>
                              <td className="px-4 py-2 text-right font-bold text-purple-900">{(po.total_allocated || 0).toLocaleString()}</td>
                              <td />
                            </tr>
                            {(po.remaining_qty ?? 0) > 0 && (
                              <tr>
                                <td colSpan={4} className="px-4 py-2 text-right text-xs text-orange-600">Remaining (unallocated)</td>
                                <td className="px-4 py-2 text-right font-semibold text-orange-700">{po.remaining_qty.toLocaleString()}</td>
                                <td />
                              </tr>
                            )}
                          </tfoot>
                        </table>
                      </div>
                    )}
                  </div>
                )}

                {/* PO KAIN: Linked Accessories */}
                {po.po_type === 'KAIN' && (po.linked_accessories?.length ?? 0) > 0 && (
                  <div>
                    <h3 className="text-base font-semibold text-gray-900 mb-3 flex items-center gap-2">
                      <Package className="w-4 h-4 text-amber-600" />
                      PO Accessories Terkait
                      <span className="ml-auto text-xs font-normal text-gray-500">
                        {po.linked_accessories.length} PO
                      </span>
                    </h3>
                    <div className="overflow-x-auto rounded-lg border border-amber-100">
                      <table className="min-w-full divide-y divide-amber-100 text-sm">
                        <thead className="bg-amber-50">
                          <tr>
                            <th className="px-4 py-2 text-left text-xs font-medium text-amber-700 uppercase">PO Number</th>
                            <th className="px-4 py-2 text-left text-xs font-medium text-amber-700 uppercase">Supplier</th>
                            <th className="px-4 py-2 text-left text-xs font-medium text-amber-700 uppercase">Tgl Order</th>
                            <th className="px-4 py-2 text-right text-xs font-medium text-amber-700 uppercase">Total</th>
                            <th className="px-4 py-2 text-left text-xs font-medium text-amber-700 uppercase">Status</th>
                          </tr>
                        </thead>
                        <tbody className="bg-white divide-y divide-amber-50">
                          {po.linked_accessories.map((acc) => (
                            <tr key={acc.id} className="hover:bg-amber-50">
                              <td className="px-4 py-2 font-mono text-xs text-amber-800">{acc.po_number}</td>
                              <td className="px-4 py-2 text-gray-700 text-xs">{acc.supplier_name}</td>
                              <td className="px-4 py-2 text-gray-500 text-xs">
                                {acc.order_date ? format(new Date(acc.order_date), 'dd MMM yyyy') : '-'}
                              </td>
                              <td className="px-4 py-2 text-right font-medium text-gray-900">{formatCurrency(acc.total_amount)}</td>
                              <td className="px-4 py-2">
                                <span className={`px-2 py-0.5 rounded text-xs font-medium ${
                                  STATUS_COLORS[acc.status || ''] || 'bg-gray-100 text-gray-600'
                                }`}>{acc.status || '?'}</span>
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                )}

                {/* PO LABEL: Manufacturing Order Released */}
                {po.po_type === 'LABEL' && po.linked_mo && (
                  <div>
                    <h3 className="text-base font-semibold text-gray-900 mb-3 flex items-center gap-2">
                      <Package className="w-4 h-4 text-purple-600" />
                      Manufacturing Order Dirilis
                      <span className={`ml-2 px-2 py-0.5 text-xs rounded-full font-medium ${
                        po.linked_mo.trigger_mode === 'RELEASED' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
                      }`}>
                        {po.linked_mo.trigger_mode}
                      </span>
                    </h3>
                    <div className="bg-purple-50 border border-purple-200 rounded-lg p-4 space-y-3">
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                        <div>
                          <p className="text-xs text-purple-600 font-medium">Batch Number</p>
                          <p className="text-sm font-bold text-purple-900 font-mono">{po.linked_mo.batch_number}</p>
                        </div>
                        <div>
                          <p className="text-xs text-purple-600 font-medium">Status MO</p>
                          <span className={`inline-block px-2 py-0.5 text-xs rounded-full font-medium ${
                            po.linked_mo.state === 'Done' ? 'bg-green-100 text-green-800' :
                            po.linked_mo.state === 'In Progress' ? 'bg-blue-100 text-blue-800' :
                            'bg-gray-100 text-gray-700'
                          }`}>{po.linked_mo.state || 'Draft'}</span>
                        </div>
                        <div>
                          <p className="text-xs text-purple-600 font-medium">Qty Planned</p>
                          <p className="text-sm font-semibold text-gray-900">{po.linked_mo.qty_planned.toLocaleString()} pcs</p>
                        </div>
                        <div>
                          <p className="text-xs text-purple-600 font-medium">Qty Produced</p>
                          <p className="text-sm font-semibold text-gray-900">{po.linked_mo.qty_produced.toLocaleString()} pcs</p>
                        </div>
                      </div>
                      {po.linked_mo.work_orders.filter(wo => ['SEWING','FINISHING','PACKING'].includes(wo.department || '')).length > 0 && (
                        <div className="overflow-x-auto rounded-lg border border-purple-100">
                          <table className="min-w-full divide-y divide-purple-100 text-sm">
                            <thead className="bg-purple-100">
                              <tr>
                                <th className="px-4 py-2 text-left text-xs font-medium text-purple-700 uppercase">WO Number</th>
                                <th className="px-4 py-2 text-left text-xs font-medium text-purple-700 uppercase">Dept</th>
                                <th className="px-4 py-2 text-right text-xs font-medium text-purple-700 uppercase">Target Qty</th>
                                <th className="px-4 py-2 text-center text-xs font-medium text-purple-700 uppercase">Status</th>
                              </tr>
                            </thead>
                            <tbody className="bg-white divide-y divide-purple-50">
                              {po.linked_mo.work_orders
                                .filter(wo => ['SEWING','FINISHING','PACKING'].includes(wo.department || ''))
                                .map((wo) => (
                                <tr key={wo.id} className="hover:bg-purple-50">
                                  <td className="px-4 py-2 font-mono text-xs text-gray-700">{wo.wo_number}</td>
                                  <td className="px-4 py-2 text-gray-900 font-medium">{wo.department}</td>
                                  <td className="px-4 py-2 text-right text-gray-900">{wo.target_qty.toLocaleString()}</td>
                                  <td className="px-4 py-2 text-center">
                                    <span className={`px-2 py-0.5 rounded text-xs font-medium ${
                                      wo.status === 'Done' || wo.status === 'DONE' ? 'bg-green-100 text-green-800' :
                                      wo.status === 'In Progress' || wo.status === 'RUNNING' ? 'bg-blue-100 text-blue-800' :
                                      'bg-gray-100 text-gray-600'
                                    }`}>{wo.status}</span>
                                  </td>
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </div>
                      )}
                    </div>
                  </div>
                )}

                {/* Manufacturing Order Section (PO KAIN only) */}
                {po.po_type === 'KAIN' && (
                  <div>
                    <h3 className="text-base font-semibold text-gray-900 mb-3 flex items-center gap-2">
                      <Package className="w-4 h-4 text-green-600" />
                      Manufacturing Order (MO)
                      {po.linked_mo && (
                        <span className={`ml-2 px-2 py-0.5 text-xs rounded-full font-medium ${
                          po.linked_mo.trigger_mode === 'RELEASED' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
                        }`}>
                          {po.linked_mo.trigger_mode}
                        </span>
                      )}
                    </h3>

                    {!po.linked_mo ? (
                      <div className="bg-gray-50 border border-dashed border-gray-300 rounded-lg p-4 text-center">
                        <p className="text-sm text-gray-400">MO belum dibuat.</p>
                        <p className="text-xs text-gray-400 mt-1">MO akan otomatis dibuat saat PO di-Send ke supplier.</p>
                        {['Draft', 'Sent', 'Done', 'Received', 'Confirmed'].includes(po.status ?? '') && (
                          <button
                            onClick={() => generateMOMutation.mutate()}
                            disabled={generateMOMutation.isPending}
                            className="mt-3 px-4 py-2 bg-green-600 text-white text-sm rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
                          >
                            {generateMOMutation.isPending ? 'Generating...' : 'Generate MO Sekarang'}
                          </button>
                        )}
                      </div>
                    ) : (
                      <div className="space-y-3">
                        {/* MO Header card */}
                        <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                            <div>
                              <p className="text-xs text-green-600 font-medium">Batch Number</p>
                              <p className="text-sm font-bold text-green-900 font-mono">{po.linked_mo.batch_number}</p>
                            </div>
                            <div>
                              <p className="text-xs text-green-600 font-medium">Status MO</p>
                              <span className={`inline-block px-2 py-0.5 text-xs rounded-full font-medium ${
                                po.linked_mo.state === 'Done' ? 'bg-green-100 text-green-800' :
                                po.linked_mo.state === 'In Progress' ? 'bg-blue-100 text-blue-800' :
                                po.linked_mo.state === 'Cancelled' ? 'bg-red-100 text-red-800' :
                                'bg-gray-100 text-gray-700'
                              }`}>{po.linked_mo.state || 'Draft'}</span>
                            </div>
                            <div>
                              <p className="text-xs text-green-600 font-medium">Qty Planned</p>
                              <p className="text-sm font-semibold text-gray-900">{po.linked_mo.qty_planned.toLocaleString()} pcs</p>
                            </div>
                            <div>
                              <p className="text-xs text-green-600 font-medium">Qty Produced</p>
                              <p className="text-sm font-semibold text-gray-900">{po.linked_mo.qty_produced.toLocaleString()} pcs</p>
                            </div>
                          </div>
                        </div>

                        {/* Work Orders table */}
                        {po.linked_mo.work_orders.length > 0 && (
                          <div className="overflow-x-auto rounded-lg border border-green-100">
                            <table className="min-w-full divide-y divide-green-100 text-sm">
                              <thead className="bg-green-50">
                                <tr>
                                  <th className="px-4 py-2 text-left text-xs font-medium text-green-700 uppercase">WO Number</th>
                                  <th className="px-4 py-2 text-left text-xs font-medium text-green-700 uppercase">Dept</th>
                                  <th className="px-4 py-2 text-right text-xs font-medium text-green-700 uppercase">Target Qty</th>
                                  <th className="px-4 py-2 text-right text-xs font-medium text-green-700 uppercase">Output</th>
                                  <th className="px-4 py-2 text-center text-xs font-medium text-green-700 uppercase">Status</th>
                                </tr>
                              </thead>
                              <tbody className="bg-white divide-y divide-green-50">
                                {po.linked_mo.work_orders.map((wo) => (
                                  <tr key={wo.id} className="hover:bg-green-50">
                                    <td className="px-4 py-2 font-mono text-xs text-gray-700">{wo.wo_number}</td>
                                    <td className="px-4 py-2 text-gray-900 font-medium">{wo.department}</td>
                                    <td className="px-4 py-2 text-right text-gray-900">{wo.target_qty.toLocaleString()}</td>
                                    <td className="px-4 py-2 text-right text-gray-900">{wo.output_qty.toLocaleString()}</td>
                                    <td className="px-4 py-2 text-center">
                                      <span className={`px-2 py-0.5 rounded text-xs font-medium ${
                                        wo.status === 'Done' || wo.status === 'DONE' || wo.status === 'Completed' ? 'bg-green-100 text-green-800' :
                                        wo.status === 'In Progress' || wo.status === 'RUNNING' ? 'bg-blue-100 text-blue-800' :
                                        wo.status === 'Blocked' ? 'bg-red-100 text-red-800' :
                                        'bg-gray-100 text-gray-600'
                                      }`}>{wo.status}</span>
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
                )}

                {/* Materials Table */}
                <div>
                  <h3 className="text-base font-semibold text-gray-900 mb-3 flex items-center gap-2">
                    <Package className="w-4 h-4 text-blue-600" />
                    Materials ({po.items.length} items)
                  </h3>
                  <div className="overflow-x-auto rounded-lg border border-gray-200">
                    <table className="min-w-full divide-y divide-gray-200 text-sm">
                      <thead className="bg-gray-50">
                        <tr>
                          <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">#</th>
                          <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Code</th>
                          <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Material</th>
                          <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Qty</th>
                          <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">UOM</th>
                          <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Unit Price</th>
                          <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Total</th>
                        </tr>
                      </thead>
                      <tbody className="bg-white divide-y divide-gray-100">
                        {po.items.length === 0 ? (
                          <tr>
                            <td colSpan={7} className="px-4 py-8 text-center text-gray-400">No materials found</td>
                          </tr>
                        ) : (
                          po.items.map((item, idx) => (
                            <tr key={idx} className="hover:bg-gray-50">
                              <td className="px-4 py-3 text-gray-400">{idx + 1}</td>
                              <td className="px-4 py-3 font-mono text-xs text-gray-600">{item.material_code || '-'}</td>
                              <td className="px-4 py-3 text-gray-900">{item.material_name || '-'}</td>
                              <td className="px-4 py-3 text-right text-gray-900">{item.quantity?.toLocaleString()}</td>
                              <td className="px-4 py-3 text-gray-500">{item.uom}</td>
                              <td className="px-4 py-3 text-right text-gray-900">{formatCurrency(item.unit_price)}</td>
                              <td className="px-4 py-3 text-right font-medium text-gray-900">{formatCurrency(item.total_price)}</td>
                            </tr>
                          ))
                        )}
                      </tbody>
                      <tfoot className="bg-gray-50">
                        <tr>
                          <td colSpan={6} className="px-4 py-3 text-right text-sm font-semibold text-gray-700">Total Amount</td>
                          <td className="px-4 py-3 text-right text-base font-bold text-gray-900">{formatCurrency(po.total_amount)}</td>
                        </tr>
                      </tfoot>
                    </table>
                  </div>
                </div>

                {/* Notes */}
                {po.notes && (
                  <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                    <p className="text-xs font-medium text-yellow-700 mb-1">Notes</p>
                    <p className="text-sm text-yellow-900">{po.notes}</p>
                  </div>
                )}

                {/* MO/WO Info Banner */}
                {po.po_type === 'KAIN' && po.status === 'Draft' && (
                  <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                    <div className="flex items-start gap-3">
                      <AlertTriangle className="w-5 h-5 text-blue-500 mt-0.5 flex-shrink-0" />
                      <div>
                        <p className="text-sm font-semibold text-blue-800">Dual Trigger System — TRIGGER 1</p>
                        <p className="text-xs text-blue-700 mt-1">
                          Klik <strong>Send PO to Supplier</strong> → sistem akan otomatis membuat
                          <strong> Manufacturing Order (PARTIAL)</strong> + <strong>Work Order Cutting</strong>.
                          Proses Cutting bisa segera dimulai tanpa menunggu Label.
                        </p>
                      </div>
                    </div>
                  </div>
                )}

                {po.po_type === 'LABEL' && (po.status === 'Draft' || po.status === 'Sent') && (
                  <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
                    <div className="flex items-start gap-3">
                      <AlertTriangle className="w-5 h-5 text-purple-500 mt-0.5 flex-shrink-0" />
                      <div>
                        <p className="text-sm font-semibold text-purple-800">Dual Trigger System — TRIGGER 2</p>
                        <p className="text-xs text-purple-700 mt-1">
                          Klik <strong>Send PO to Supplier</strong> → sistem akan otomatis merilis
                          <strong> Work Order penuh</strong>: Sewing, Finishing, Packing.
                          Manufacturing Order akan diupdate ke mode <strong>RELEASED</strong>.
                        </p>
                      </div>
                    </div>
                  </div>
                )}

                {/* Confirm panel */}
                {confirmAction && (
                  <div className={`rounded-lg p-4 border ${confirmAction === 'Cancelled' ? 'bg-red-50 border-red-200' : 'bg-amber-50 border-amber-200'}`}>
                    <p className={`text-sm font-semibold mb-3 ${confirmAction === 'Cancelled' ? 'text-red-800' : 'text-amber-800'}`}>
                      Konfirmasi: Ubah status ke "{confirmAction}"?
                    </p>
                    <div className="flex gap-2">
                      <Button
                        size="sm"
                        variant={confirmAction === 'Cancelled' ? 'danger' : 'default'}
                        onClick={() => statusMutation.mutate(confirmAction)}
                        disabled={statusMutation.isPending}
                      >
                        {statusMutation.isPending ? 'Processing...' : `Ya, ${confirmAction}`}
                      </Button>
                      <Button size="sm" variant="outline" onClick={() => setConfirmAction(null)}>
                        Batal
                      </Button>
                    </div>
                  </div>
                )}
              </>
            )}
          </div>

          {/* Footer Actions */}
          {po && (
            <div className="flex items-center justify-between p-6 border-t border-gray-200 bg-gray-50 rounded-b-xl">
              {/* Left: creation date + delete buttons */}
              <div className="flex items-center gap-3">
                <span className="text-xs text-gray-400">
                  {po.created_at && `Dibuat: ${format(new Date(po.created_at), 'dd MMM yyyy HH:mm')}`}
                </span>
                {po.status !== 'Done' && po.status !== 'Cancelled' && (
                  <>
                    {isAdmin ? (
                      <Button
                        variant="outline"
                        size="sm"
                        className="border-red-400 text-red-600 hover:bg-red-50"
                        onClick={() => setShowDeleteConfirm(true)}
                      >
                        <Trash2 className="w-3.5 h-3.5 mr-1" /> Hapus PO
                      </Button>
                    ) : (
                      <Button
                        variant="outline"
                        size="sm"
                        className="border-orange-300 text-orange-600 hover:bg-orange-50"
                        onClick={() => setShowRequestModal(true)}
                      >
                        <Trash2 className="w-3.5 h-3.5 mr-1" /> Request Hapus
                      </Button>
                    )}
                  </>
                )}
              </div>

              <div className="flex gap-2">
                {canCancel && !confirmAction && (
                  <Button
                    variant="outline"
                    className="border-red-300 text-red-600 hover:bg-red-50"
                    onClick={() => setConfirmAction('Cancelled')}
                    size="sm"
                  >
                    <XCircle className="w-4 h-4 mr-1" /> Cancel PO
                  </Button>
                )}
                {canReceive && !confirmAction && (
                  <Button
                    variant="outline"
                    className="border-orange-300 text-orange-600 hover:bg-orange-50"
                    onClick={() => setConfirmAction('Received')}
                    size="sm"
                  >
                    <Package className="w-4 h-4 mr-1" /> Mark Received
                  </Button>
                )}
                {canDone && !confirmAction && (
                  <Button
                    variant="outline"
                    className="border-green-300 text-green-600 hover:bg-green-50"
                    onClick={() => setConfirmAction('Done')}
                    size="sm"
                  >
                    <CheckCircle className="w-4 h-4 mr-1" /> Mark Done
                  </Button>
                )}
                {canSend && !confirmAction && (
                  <Button
                    className="bg-blue-600 hover:bg-blue-700 text-white"
                    onClick={() => setConfirmAction('Sent')}
                    size="sm"
                  >
                    <Truck className="w-4 h-4 mr-1" /> Send PO to Supplier
                  </Button>
                )}
                {po.status === 'Done' && (
                  <span className="flex items-center gap-1 text-green-600 text-sm font-medium">
                    <CheckCircle className="w-4 h-4" /> Completed
                  </span>
                )}
                {po.status === 'Cancelled' && (
                  <span className="flex items-center gap-1 text-red-500 text-sm font-medium">
                    <XCircle className="w-4 h-4" /> Cancelled
                  </span>
                )}
                {(po.status === 'Sent' || po.status === 'Received') && !confirmAction && (
                  <span className="flex items-center gap-1 text-blue-600 text-sm font-medium">
                    <Clock className="w-4 h-4" /> {po.status === 'Sent' ? 'Waiting for delivery' : 'Goods received, pending verification'}
                  </span>
                )}
                <Button variant="outline" onClick={onClose} size="sm">
                  Tutup
                </Button>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* ── Direct Delete Confirm (Admin) ───────────────────────────────── */}
      {showDeleteConfirm && (
        <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-[60] p-4">
          <div className="bg-white rounded-xl shadow-2xl w-full max-w-md p-6 space-y-4">
            <div className="flex items-center gap-2 text-red-600">
              <Trash2 className="w-5 h-5" />
              <h3 className="text-lg font-bold">Hapus PO {po?.po_number}?</h3>
            </div>
            <p className="text-sm text-gray-600">
              PO akan <strong>dihapus permanen</strong>. Tindakan ini tidak dapat dibatalkan.
            </p>
            <label className="block">
              <span className="text-sm font-medium text-gray-700">Alasan penghapusan *</span>
              <textarea
                className="mt-1 w-full border rounded-lg px-3 py-2 text-sm"
                rows={3}
                value={directDeleteReason}
                onChange={e => setDirectDeleteReason(e.target.value)}
                placeholder="Tulis alasan…"
              />
            </label>
            <div className="flex justify-end gap-2">
              <Button variant="outline" size="sm" onClick={() => { setShowDeleteConfirm(false); setDirectDeleteReason('') }}>Batal</Button>
              <Button
                size="sm"
                className="bg-red-600 hover:bg-red-700 text-white"
                disabled={directDeleteReason.length < 5 || directDeleteMutation.isPending}
                onClick={() => directDeleteMutation.mutate(directDeleteReason)}
              >
                {directDeleteMutation.isPending ? 'Menghapus…' : 'Ya, Hapus PO'}
              </Button>
            </div>
          </div>
        </div>
      )}

      {/* ── Request Deletion (Non-admin) ────────────────────────────────── */}
      {showRequestModal && (
        <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-[60] p-4">
          <div className="bg-white rounded-xl shadow-2xl w-full max-w-md p-6 space-y-4">
            <div className="flex items-center gap-2 text-orange-600">
              <Trash2 className="w-5 h-5" />
              <h3 className="text-lg font-bold">Request Hapus PO {po?.po_number}</h3>
            </div>
            <p className="text-sm text-gray-600">
              Permintaan penghapusan akan dikirim ke <strong>Atasan / Admin</strong> untuk disetujui.
            </p>
            <label className="block">
              <span className="text-sm font-medium text-gray-700">Alasan *</span>
              <textarea
                className="mt-1 w-full border rounded-lg px-3 py-2 text-sm"
                rows={3}
                value={deleteReason}
                onChange={e => setDeleteReason(e.target.value)}
                placeholder="Mengapa PO ini perlu dihapus?"
              />
            </label>
            <div className="flex justify-end gap-2">
              <Button variant="outline" size="sm" onClick={() => { setShowRequestModal(false); setDeleteReason('') }}>Batal</Button>
              <Button
                size="sm"
                className="bg-orange-500 hover:bg-orange-600 text-white"
                disabled={deleteReason.length < 5 || requestDeleteMutation.isPending}
                onClick={() => requestDeleteMutation.mutate(deleteReason)}
              >
                {requestDeleteMutation.isPending ? 'Mengirim…' : 'Kirim Request'}
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

