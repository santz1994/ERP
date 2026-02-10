/**
 * MO Create Modal Component
 * Extracted from CreateMOPage for modal-based UX
 * 
 * Features:
 * - Auto-create MO from PO Label (TRIGGER 2)
 * - Inherit Week & Destination from PO Label
 * - Flexible Target system (buffer 3-5%)
 * - Modal overlay with close on backdrop click
 */

import { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import toast from 'react-hot-toast';
import { X } from 'lucide-react';
import { api } from '../../api';
import { moSchema } from '../../lib/schemas';
import { Card, CardHeader, CardTitle, CardContent } from '../ui/card';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { cn } from '../../lib/utils';
import type { z } from 'zod';

type MOFormData = z.infer<typeof moSchema>;

interface POLabel {
  id: number;
  poNumber: string;
  poDate: string;
  articleCode: string;
  articleName: string;
  qty: number;
  week: string;
  destination: string;
  supplierName: string;
  status: string;
}

interface MOCreateModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess?: (moId: number) => void;
}

export default function MOCreateModal({ isOpen, onClose, onSuccess }: MOCreateModalProps) {
  const queryClient = useQueryClient();
  const [selectedPOLabel, setSelectedPOLabel] = useState<POLabel | null>(null);
  const [bufferPercent, setBufferPercent] = useState<number>(3);
  const [showInheritanceHighlight, setShowInheritanceHighlight] = useState(false);

  // Fetch available PO Labels
  const { data: poLabels, isLoading: loadingPOLabels } = useQuery({
    queryKey: ['po-labels-available'],
    queryFn: () => api.purchasing.getPOs({ po_type: 'LABEL', status: 'RECEIVED' }),
    enabled: isOpen,
  });

  // Form setup
  const {
    register,
    handleSubmit,
    setValue,
    watch,
    reset,
    formState: { errors },
  } = useForm<MOFormData>({
    resolver: zodResolver(moSchema) as any,
    defaultValues: {
      target_qty: 0,
      status: 'DRAFT',
    },
  });

  const target_qty = watch('target_qty');
  const finalQty = target_qty + Math.round((target_qty * bufferPercent) / 100);

  // Create MO mutation
  const createMOMutation = useMutation({
    mutationFn: (data: MOFormData) => api.ppic.createMO({ ...data, status: 'DRAFT' }),
    onSuccess: (response) => {
      toast.success(`MO ${response.mo_number || 'created'} successfully!`);
      queryClient.invalidateQueries({ queryKey: ['manufacturing-orders'] });
      reset();
      setSelectedPOLabel(null);
      onSuccess?.(response.id);
      onClose();
    },
    onError: (error: any) => {
      toast.error(error?.message || 'Failed to create MO. Please try again.');
    },
  });

  // Handle PO Label selection
  const handlePOLabelSelect = (po: POLabel) => {
    setSelectedPOLabel(po);
    setShowInheritanceHighlight(true);

    setValue('po_label_id', po.id);
    setValue('article_code', po.articleCode);
    setValue('article_name', po.articleName);
    setValue('target_qty', po.qty);
    setValue('week_number', po.week);
    setValue('destination', po.destination);

    setTimeout(() => setShowInheritanceHighlight(false), 3000);
    toast.success(`Auto-populated from ${po.poNumber}!`);
  };

  // Reset form when modal closes
  useEffect(() => {
    if (!isOpen) {
      reset();
      setSelectedPOLabel(null);
      setBufferPercent(3);
    }
  }, [isOpen, reset]);

  const onSubmit = (data: MOFormData) => {
    createMOMutation.mutate(data);
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-[9999] p-4 overflow-y-auto">
      <div className="bg-white rounded-lg shadow-2xl w-full max-w-5xl my-8">
        {/* Modal Header */}
        <div className="flex items-center justify-between p-6 border-b sticky top-0 bg-white rounded-t-lg">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Create Manufacturing Order (MO)</h2>
            <p className="text-gray-600 text-sm mt-1">
              Auto-create from PO Label with Week & Destination inheritance
            </p>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Modal Body */}
        <form onSubmit={handleSubmit(onSubmit)} className="p-6 space-y-6 max-h-[calc(100vh-200px)] overflow-y-auto">
          {/* Step 1: Select PO Label */}
          <Card variant="elevated" className="border-2 border-purple-200 bg-purple-50">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <span className="text-xl">1️⃣</span>
                <span>Select PO Label (TRIGGER 2)</span>
                <Badge variant="info">Required</Badge>
              </CardTitle>
            </CardHeader>
            <CardContent>
              {loadingPOLabels ? (
                <div className="text-center py-8">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-500 mx-auto"></div>
                  <p className="text-gray-600 mt-2">Loading PO Labels...</p>
                </div>
              ) : poLabels && poLabels.length > 0 ? (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3 max-h-64 overflow-y-auto">
                  {poLabels.map((po: POLabel) => (
                    <button
                      key={po.id}
                      type="button"
                      onClick={() => handlePOLabelSelect(po)}
                      className={cn(
                        'text-left p-3 rounded-lg border-2 transition-all text-sm',
                        selectedPOLabel?.id === po.id
                          ? 'border-purple-500 bg-purple-100 shadow-lg'
                          : 'border-gray-300 bg-white hover:border-purple-300'
                      )}
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="font-semibold text-gray-900">{po.poNumber}</div>
                          <div className="text-xs text-gray-600 mt-1">
                            {po.articleCode} - {po.articleName}
                          </div>
                          <div className="text-xs text-gray-600 mt-1">
                            Qty: <span className="font-semibold">{po.qty}</span>
                          </div>
                          <div className="flex items-center gap-1 mt-2">
                            <Badge variant="info" size="sm">📅 {po.week}</Badge>
                            <Badge variant="secondary" size="sm">🏢 {po.destination}</Badge>
                          </div>
                        </div>
                        {selectedPOLabel?.id === po.id && (
                          <div className="text-purple-500 text-xl">✓</div>
                        )}
                      </div>
                    </button>
                  ))}
                </div>
              ) : (
                <div className="text-center py-6 bg-white rounded-lg">
                  <p className="text-gray-600 text-sm">No available PO Labels found.</p>
                  <p className="text-xs text-gray-500 mt-1">
                    PO Labels must be RECEIVED status and not yet used.
                  </p>
                </div>
              )}
              {errors.po_label_id && (
                <p className="text-red-600 text-xs mt-2">⚠️ {errors.po_label_id.message}</p>
              )}
            </CardContent>
          </Card>

          {/* Step 2: MO Details (Auto-populated) */}
          {selectedPOLabel && (
            <>
              <Card variant="bordered">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-lg">
                    <span>2️⃣</span>
                    <span>MO Details (Auto-populated)</span>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-xs font-medium text-gray-700 mb-1">
                        Article Code
                      </label>
                      <input
                        type="text"
                        {...register('article_code')}
                        className="w-full px-3 py-2 text-sm border border-gray-300 rounded-md bg-gray-100 cursor-not-allowed"
                        readOnly
                      />
                    </div>

                    <div>
                      <label className="block text-xs font-medium text-gray-700 mb-1">
                        Article Name
                      </label>
                      <input
                        type="text"
                        {...register('article_name')}
                        className="w-full px-3 py-2 text-sm border border-gray-300 rounded-md bg-gray-100 cursor-not-allowed"
                        readOnly
                      />
                    </div>

                    <div>
                      <label className="block text-xs font-medium text-gray-700 mb-1">
                        Target Qty (from PO)
                      </label>
                      <input
                        type="number"
                        {...register('target_qty', { valueAsNumber: true })}
                        className="w-full px-3 py-2 text-sm border border-gray-300 rounded-md bg-gray-100 cursor-not-allowed"
                        readOnly
                      />
                    </div>

                    <div>
                      <label className="block text-xs font-medium text-gray-700 mb-1">
                        Buffer % (Flexible Target)
                      </label>
                      <div className="flex items-center gap-2">
                        <input
                          type="range"
                          min="0"
                          max="10"
                          value={bufferPercent}
                          onChange={(e) => setBufferPercent(Number(e.target.value))}
                          className="flex-1"
                        />
                        <input
                          type="number"
                          value={bufferPercent}
                          onChange={(e) => setBufferPercent(Number(e.target.value))}
                          className="w-16 px-2 py-1 text-sm border rounded text-center"
                          min="0"
                          max="10"
                        />
                        <span className="text-sm">%</span>
                      </div>
                    </div>

                    <div className="md:col-span-2">
                      <div className="bg-blue-50 border-2 border-blue-200 rounded-lg p-3">
                        <div className="flex items-center justify-between">
                          <div>
                            <p className="text-xs text-gray-700">Final Target:</p>
                            <p className="text-2xl font-bold text-blue-600">{finalQty} pcs</p>
                          </div>
                          <div className="text-right">
                            <p className="text-xs text-gray-600">Breakdown:</p>
                            <p className="text-xs text-gray-700">
                              {target_qty} + {finalQty - target_qty} pcs
                            </p>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Step 3: Week & Destination (INHERITED) */}
              <Card
                variant="elevated"
                className={cn(
                  'border-2 transition-all',
                  showInheritanceHighlight
                    ? 'border-yellow-400 bg-yellow-50 animate-pulse'
                    : 'border-green-300 bg-green-50'
                )}
              >
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-lg">
                    <span>3️⃣</span>
                    <span>Week & Destination (INHERITED)</span>
                    <Badge variant="warning">🔗 Auto</Badge>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-xs font-medium text-gray-700 mb-1">
                        Week (Inherited) <span className="text-red-500">*</span>
                      </label>
                      <input
                        type="text"
                        {...register('week_number')}
                        className="w-full px-3 py-2 text-sm border-2 border-green-400 rounded-md bg-green-100 font-semibold"
                        readOnly
                      />
                    </div>

                    <div>
                      <label className="block text-xs font-medium text-gray-700 mb-1">
                        Destination (Inherited) <span className="text-red-500">*</span>
                      </label>
                      <input
                        type="text"
                        {...register('destination')}
                        className="w-full px-3 py-2 text-sm border-2 border-green-400 rounded-md bg-green-100 font-semibold"
                        readOnly
                      />
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Step 4: Notes */}
              <Card variant="bordered">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-lg">
                    <span>4️⃣</span>
                    <span>Notes (Optional)</span>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <textarea
                    {...register('notes')}
                    rows={3}
                    className="w-full px-3 py-2 text-sm border border-gray-300 rounded-md"
                    placeholder="Add special instructions..."
                  />
                </CardContent>
              </Card>
            </>
          )}
        </form>

        {/* Modal Footer */}
        <div className="flex items-center justify-end gap-3 p-6 border-t bg-gray-50 rounded-b-lg sticky bottom-0">
          <Button
            type="button"
            variant="secondary"
            onClick={onClose}
            disabled={createMOMutation.isPending}
          >
            Cancel
          </Button>
          <Button
            type="submit"
            variant="primary"
            onClick={handleSubmit(onSubmit)}
            disabled={!selectedPOLabel || createMOMutation.isPending}
            isLoading={createMOMutation.isPending}
          >
            {createMOMutation.isPending ? 'Creating...' : '✅ Create MO'}
          </Button>
        </div>
      </div>
    </div>
  );
}
