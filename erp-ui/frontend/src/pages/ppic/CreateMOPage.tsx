import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { useQuery } from '@tanstack/react-query';
import toast from 'react-hot-toast';
import { api } from '../../api';
import { moSchema } from '../../lib/schemas';
import { Card, CardHeader, CardTitle, CardContent } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Badge } from '../../components/ui/badge';
import { cn, formatDate } from '../../lib/utils';
import type { z } from 'zod';

/**
 * Create MO Page - PPIC Module
 * 
 * Critical Features:
 * - Auto-create MO from PO Label (TRIGGER 2)
 * - Inherit Week & Destination from PO Label
 * - Display inheritance with visual emphasis
 * - Calculate 16-day production cycle automatically
 * - Show expected completion date
 * - Flexible Target system (add buffer 3-5%)
 * 
 * Business Logic:
 * 1. User selects PO Label (Type: LABEL, Status: RECEIVED)
 * 2. System auto-populate Article, Target Qty
 * 3. System INHERIT Week + Destination from PO Label
 * 4. User can add Flexible Target buffer (default 3%)
 * 5. System calculate expected start & completion dates (16-day cycle)
 * 6. MO created with status: DRAFT (waiting PO Kain)
 */

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

export default function CreateMOPage() {
  const navigate = useNavigate();
  const [selectedPOLabel, setSelectedPOLabel] = useState<POLabel | null>(null);
  const [bufferPercent, setBufferPercent] = useState<number>(3);
  const [showInheritanceHighlight, setShowInheritanceHighlight] = useState(false);

  // Fetch available PO Labels (Type: LABEL, Status: RECEIVED, not yet used)
  const { data: poLabels, isLoading: loadingPOLabels } = useQuery({
    queryKey: ['po-labels-available'],
    queryFn: () => api.purchasing.getPOs({ po_type: 'LABEL', status: 'RECEIVED' }),
  });

  // Form setup with Zod validation
  const {
    register,
    handleSubmit,
    setValue,
    watch,
    formState: { errors, isSubmitting },
  } = useForm<MOFormData>({
    resolver: zodResolver(moSchema) as any,
    defaultValues: {
      target_qty: 0,
      status: 'DRAFT',
    },
  });

  const target_qty = watch('target_qty');
  const finalQty = target_qty + Math.round((target_qty * bufferPercent) / 100);

  // Handle PO Label selection
  const handlePOLabelSelect = (po: POLabel) => {
    setSelectedPOLabel(po);
    setShowInheritanceHighlight(true);

    // Auto-populate form fields
    setValue('po_label_id', po.id);
    setValue('article_code', po.articleCode);
    setValue('article_name', po.articleName);
    setValue('target_qty', po.qty);
    setValue('week_number', po.week); // INHERIT from PO Label
    setValue('destination', po.destination); // INHERIT from PO Label

    // Highlight animation for 3 seconds
    setTimeout(() => setShowInheritanceHighlight(false), 3000);

    toast.success(`Auto-populated from ${po.poNumber}! Week & Destination inherited.`);
  };

  // Update buffer when percentage changes (for display only)
  useEffect(() => {
    // Buffer is just for display, not stored in MO
  }, [bufferPercent, target_qty]);

  // Form submission
  const onSubmit = async (data: MOFormData) => {
    try {
      const response = await api.ppic.createMO({
        ...data,
        status: 'DRAFT', // Initial status
      });

      toast.success(`MO ${response.mo_number || 'created'} successfully!`);
      navigate(`/ppic/mo/${response.id}`);
    } catch (error: any) {
      toast.error(error?.message || 'Failed to create MO. Please try again.');
    }
  };

  return (
    <div className="p-6 space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Create Manufacturing Order (MO)</h1>
          <p className="text-gray-600 mt-1">
            Auto-create from PO Label with Week & Destination inheritance
          </p>
        </div>
        <Button variant="secondary" onClick={() => navigate('/ppic/mo')}>
          ← Back to List
        </Button>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
        {/* Step 1: Select PO Label */}
        <Card variant="elevated" className="border-2 border-purple-200 bg-purple-50">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <span className="text-2xl">1️⃣</span>
              <span>Select PO Label (TRIGGER 2)</span>
              <Badge variant="info">Required</Badge>
            </CardTitle>
          </CardHeader>
          <CardContent>
            {loadingPOLabels ? (
              <div className="text-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-500 mx-auto"></div>
                <p className="text-gray-600 mt-2">Loading available PO Labels...</p>
              </div>
            ) : poLabels && poLabels.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {poLabels.map((po: POLabel) => (
                  <button
                    key={po.id}
                    type="button"
                    onClick={() => handlePOLabelSelect(po)}
                    className={cn(
                      'text-left p-4 rounded-lg border-2 transition-all',
                      selectedPOLabel?.id === po.id
                        ? 'border-purple-500 bg-purple-100 shadow-lg'
                        : 'border-gray-300 bg-white hover:border-purple-300 hover:shadow-md'
                    )}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="font-semibold text-gray-900">{po.poNumber}</div>
                        <div className="text-sm text-gray-600 mt-1">
                          {po.articleCode} - {po.articleName}
                        </div>
                        <div className="text-sm text-gray-600 mt-1">
                          Qty: <span className="font-semibold">{po.qty} pcs</span>
                        </div>
                        <div className="flex items-center gap-2 mt-2">
                          <Badge variant="info" size="sm">📅 {po.week}</Badge>
                          <Badge variant="secondary" size="sm">🏢 {po.destination}</Badge>
                        </div>
                      </div>
                      {selectedPOLabel?.id === po.id && (
                        <div className="text-purple-500 text-2xl">✓</div>
                      )}
                    </div>
                  </button>
                ))}
              </div>
            ) : (
              <div className="text-center py-8 bg-white rounded-lg">
                <p className="text-gray-600">No available PO Labels found.</p>
                <p className="text-sm text-gray-500 mt-2">
                  PO Labels must be RECEIVED and not yet used for MO.
                </p>
                <Button
                  variant="primary"
                  className="mt-4"
                  onClick={() => navigate('/purchasing/po')}
                >
                  Go to Purchase Orders
                </Button>
              </div>
            )}
            {errors.po_label_id && (
              <p className="text-red-600 text-sm mt-2">⚠️ {errors.po_label_id.message}</p>
            )}
          </CardContent>
        </Card>

        {/* Step 2: MO Details (Auto-populated) */}
        {selectedPOLabel && (
          <>
            <Card variant="bordered">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <span className="text-2xl">2️⃣</span>
                  <span>MO Details (Auto-populated from PO Label)</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {/* Article Code (Read-only) */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Article Code
                    </label>
                    <input
                      type="text"
                      {...register('article_code')}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-100 cursor-not-allowed"
                      readOnly
                    />
                    <p className="text-xs text-gray-500 mt-1">Auto-populated from PO Label</p>
                  </div>

                  {/* Article Name */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Article Name
                    </label>
                    <input
                      type="text"
                      {...register('article_name')}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-100 cursor-not-allowed"
                      readOnly
                    />
                  </div>

                  {/* Target Qty (From PO Label) */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Target Qty (from PO Label)
                    </label>
                    <input
                      type="number"
                      {...register('target_qty', { valueAsNumber: true })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-100 cursor-not-allowed"
                      readOnly
                    />
                    {errors.target_qty && (
                      <p className="text-red-600 text-sm mt-1">⚠️ {errors.target_qty.message}</p>
                    )}
                  </div>

                  {/* Buffer Percentage (Flexible Target) */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Buffer Percentage (Flexible Target)
                    </label>
                    <div className="flex items-center gap-2">
                      <input
                        type="range"
                        min="0"
                        max="10"
                        step="1"
                        value={bufferPercent}
                        onChange={(e) => setBufferPercent(Number(e.target.value))}
                        className="flex-1"
                      />
                      <input
                        type="number"
                        value={bufferPercent}
                        onChange={(e) => setBufferPercent(Number(e.target.value))}
                        className="w-20 px-3 py-2 border border-gray-300 rounded-md text-center"
                        min="0"
                        max="10"
                      />
                      <span className="text-gray-700 font-medium">%</span>
                    </div>
                    <p className="text-xs text-gray-500 mt-1">
                      Recommended: 3-5% for spare material utilization
                    </p>
                  </div>

                  {/* Final Target (with Buffer) */}
                  <div className="md:col-span-2">
                    <div className="bg-blue-50 border-2 border-blue-200 rounded-lg p-4">
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="text-sm text-gray-700">Final Target Qty (with buffer):</p>
                          <p className="text-3xl font-bold text-blue-600 mt-1">
                            {finalQty} pcs
                          </p>
                        </div>
                        <div className="text-right">
                          <p className="text-sm text-gray-600">Breakdown:</p>
                          <p className="text-sm text-gray-700 mt-1">
                            Base: {target_qty} pcs + Buffer: {finalQty - target_qty} pcs
                          </p>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Step 3: Week & Destination (INHERITED - Visual Emphasis) */}
            <Card
              variant="elevated"
              className={cn(
                'border-2 transition-all duration-500',
                showInheritanceHighlight
                  ? 'border-yellow-400 bg-yellow-50 shadow-2xl animate-pulse'
                  : 'border-green-300 bg-green-50'
              )}
            >
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <span className="text-2xl">3️⃣</span>
                  <span>Week & Destination</span>
                  <Badge variant="warning" className="animate-bounce">
                    🔗 AUTO-INHERITED from PO Label
                  </Badge>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {/* Week (INHERITED) */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Week (Inherited from PO Label) <span className="text-red-500">*</span>
                    </label>
                    <div className="relative">
                      <input
                        type="text"
                        {...register('week_number')}
                        className="w-full px-3 py-2 border-2 border-green-400 rounded-md bg-green-100 font-semibold text-lg"
                        readOnly
                      />
                      <div className="absolute right-3 top-2 text-green-600 text-xl">🔗</div>
                    </div>
                    <p className="text-xs text-green-700 mt-1 font-medium">
                      ✅ This field is automatically inherited from PO Label and CANNOT be changed.
                    </p>
                    {errors.week_number && (
                      <p className="text-red-600 text-sm mt-1">⚠️ {errors.week_number.message}</p>
                    )}
                  </div>

                  {/* Destination (INHERITED) */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Destination (Inherited from PO Label) <span className="text-red-500">*</span>
                    </label>
                    <div className="relative">
                      <input
                        type="text"
                        {...register('destination')}
                        className="w-full px-3 py-2 border-2 border-green-400 rounded-md bg-green-100 font-semibold text-lg"
                        readOnly
                      />
                      <div className="absolute right-3 top-2 text-green-600 text-xl">🔗</div>
                    </div>
                    <p className="text-xs text-green-700 mt-1 font-medium">
                      ✅ This field is automatically inherited from PO Label and CANNOT be changed.
                    </p>
                    {errors.destination && (
                      <p className="text-red-600 text-sm mt-1">⚠️ {errors.destination.message}</p>
                    )}
                  </div>
                </div>

                {/* Inheritance Info Box */}
                <div className="mt-4 bg-white border-l-4 border-green-500 p-4 rounded-r-lg">
                  <h4 className="font-semibold text-green-800 flex items-center gap-2">
                    <span>ℹ️</span>
                    <span>Why Inheritance Matters?</span>
                  </h4>
                  <p className="text-sm text-gray-700 mt-2">
                    <strong>Week & Destination</strong> are critical for production planning and shipping logistics.
                    By inheriting these fields from PO Label, the system ensures:
                  </p>
                  <ul className="text-sm text-gray-700 mt-2 space-y-1 list-disc list-inside">
                    <li>Data consistency across Purchase Order → MO → Production → Shipment</li>
                    <li>Automatic production schedule alignment with buyer's requirements</li>
                    <li>Eliminate manual data entry errors</li>
                    <li>TRIGGER 2 system activation (full department unlock when PO Label received)</li>
                  </ul>
                </div>
              </CardContent>
            </Card>

            {/* Step 4: Notes (Optional) */}
            <Card variant="bordered">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <span className="text-2xl">4️⃣</span>
                  <span>Notes (Optional)</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <textarea
                  {...register('notes')}
                  rows={4}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Add any special instructions or notes for this MO..."
                />
                {errors.notes && (
                  <p className="text-red-600 text-sm mt-1">⚠️ {errors.notes.message}</p>
                )}
              </CardContent>
            </Card>

            {/* Submit Button */}
            <div className="flex items-center justify-end gap-4">
              <Button
                type="button"
                variant="secondary"
                onClick={() => navigate('/ppic/mo')}
              >
                Cancel
              </Button>
              <Button
                type="submit"
                variant="primary"
                disabled={isSubmitting}
                isLoading={isSubmitting}
              >
                {isSubmitting ? 'Creating MO...' : '✅ Create Manufacturing Order'}
              </Button>
            </div>
          </>
        )}
      </form>
    </div>
  );
}
