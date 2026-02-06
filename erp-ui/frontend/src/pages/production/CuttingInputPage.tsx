import { useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { useQuery } from '@tanstack/react-query';
import toast from 'react-hot-toast';
import { api } from '../../api';
import { productionInputSchema } from '../../lib/schemas';
import { Card, CardHeader, CardTitle, CardContent } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Badge } from '../../components/ui/badge';
import { cn, formatNumber } from '../../lib/utils';
import type { z } from 'zod';

/**
 * Cutting Input Page - Production Module
 * 
 * Features:
 * - Daily production input for Cutting department
 * - Material consumption tracking (Fabric)
 * - UOM conversion (YARD → PCS)
 * - Good output + Defect input
 * - Variance tolerance validation (0-3% auto, 3-5% warning, >5% require reason)
 * - Real-time cumulative check (sum ≤ SPK target)
 * - Auto-transfer to WIP Buffer (Embroidery/Sewing)
 * 
 * Material Tracked:
 * - KOHAIR (Main fabric) - YARD per pcs from BOM
 * - Waste calculation (actual used vs BOM standard)
 */

type CuttingInputData = z.infer<typeof productionInputSchema>;

interface SPK {
  id: number;
  spkNumber: string;
  articleCode: string;
  articleName: string;
  targetQty: number;
  actualQty: number;
  remainingQty: number;
  bomMaterials: Array<{
    materialCode: string;
    materialName: string;
    qtyPerUnit: number;
    uom: string;
  }>;
}

export default function CuttingInputPage() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const preselectedDate = searchParams.get('date') || new Date().toISOString().split('T')[0];
  
  const [selectedSPK, setSelectedSPK] = useState<SPK | null>(null);
  const [showVarianceReason, setShowVarianceReason] = useState(false);

  // Fetch active SPKs for Cutting
  const { data: spks, isLoading: loadingSPKs } = useQuery<SPK[]>({
    queryKey: ['spks-cutting'],
    queryFn: () => api.production.getSPKs('CUTTING', { status: 'ONGOING' }),
  });

  // Form setup
  const {
    register,
    handleSubmit,
    watch,
    setValue,
    formState: { errors, isSubmitting },
  } = useForm<CuttingInputData>({
    resolver: zodResolver(productionInputSchema) as any,
    defaultValues: {
      date: preselectedDate,
      good_output: 0,
      defect_qty: 0,
    },
  });

  const good_output = watch('good_output') || 0;
  const defect_qty = watch('defect_qty') || 0;
  // Note: material_consumption is an array in schema, but we use single value for UI simplicity
  const material_consumption = watch('material_consumption') || [];
  const materialUsedQty = material_consumption[0]?.qty_used || 0;

  // Calculate material variance
  const calculateMaterialVariance = () => {
    if (!selectedSPK || !materialUsedQty || good_output === 0) return null;

    const fabricMaterial = selectedSPK.bomMaterials.find(m => m.materialCode.includes('KOHAIR'));
    if (!fabricMaterial) return null;

    const bomStandard = fabricMaterial.qtyPerUnit * good_output;
    const variance = ((materialUsedQty - bomStandard) / bomStandard) * 100;

    return {
      bomStandard,
      actual: materialUsedQty,
      variance,
      varianceQty: materialUsedQty - bomStandard,
    };
  };

  const materialVariance = calculateMaterialVariance();

  // Handle SPK selection
  const handleSPKSelect = (spk: SPK) => {
    setSelectedSPK(spk);
    setValue('spk_id', spk.id);
    
    // Auto-calculate material based on BOM
    const fabricMaterial = spk.bomMaterials.find(m => m.materialCode.includes('KOHAIR'));
    if (fabricMaterial && good_output > 0) {
      const estimatedUsage = fabricMaterial.qtyPerUnit * good_output;
      setValue('material_consumption', [{
        material_code: fabricMaterial.materialCode,
        qty_used: estimatedUsage,
        uom: 'YARD'
      }]);
    }
  };

  // Watch good output to update material estimate
  const updateMaterialEstimate = () => {
    if (!selectedSPK || good_output === 0) return;

    const fabricMaterial = selectedSPK.bomMaterials.find(m => m.materialCode.includes('KOHAIR'));
    if (fabricMaterial) {
      const estimatedUsage = fabricMaterial.qtyPerUnit * good_output;
      setValue('material_consumption', [{
        material_code: fabricMaterial.materialCode,
        qty_used: estimatedUsage,
        uom: 'YARD'
      }]);
    }
  };

  // Form submission
  const onSubmit = async (data: CuttingInputData) => {
    try {
      // Check variance tolerance
      if (materialVariance && Math.abs(materialVariance.variance) > 5) {
        if (!data.notes) {
          toast.error('Variance >5% requires justification in notes!');
          setShowVarianceReason(true);
          return;
        }
      }

      const response = await api.production.inputProduction(data);

      toast.success(`Production input successful! ${good_output} pcs transferred to WIP Buffer.`);
      navigate('/production/calendar');
    } catch (error: any) {
      toast.error(error?.message || 'Failed to input production.');
    }
  };

  return (
    <div className="p-6 space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">✂️ Cutting - Daily Production Input</h1>
          <p className="text-gray-600 mt-1">
            Input daily cutting output with material consumption tracking
          </p>
        </div>
        <Button variant="secondary" onClick={() => navigate('/production/calendar')}>
          ← Back to Calendar
        </Button>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
        {/* Step 1: Select SPK */}
        <Card variant="elevated" className="border-2 border-blue-200 bg-blue-50">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <span>1️⃣ Select SPK</span>
              <Badge variant="info">Required</Badge>
            </CardTitle>
          </CardHeader>
          <CardContent>
            {loadingSPKs ? (
              <div className="text-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto"></div>
                <p className="text-gray-600 mt-2">Loading active SPKs...</p>
              </div>
            ) : spks && spks.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {spks.map((spk) => (
                  <button
                    key={spk.id}
                    type="button"
                    onClick={() => handleSPKSelect(spk)}
                    className={cn(
                      'text-left p-4 rounded-lg border-2 transition-all',
                      selectedSPK?.id === spk.id
                        ? 'border-blue-500 bg-blue-100 shadow-lg'
                        : 'border-gray-300 bg-white hover:border-blue-300 hover:shadow-md'
                    )}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="font-semibold text-gray-900">{spk.spkNumber}</div>
                        <div className="text-sm text-gray-600 mt-1">
                          {spk.articleCode} - {spk.articleName}
                        </div>
                        <div className="flex items-center gap-4 mt-2 text-sm">
                          <span className="text-gray-600">
                            Target: <span className="font-semibold">{formatNumber(spk.targetQty)}</span>
                          </span>
                          <span className="text-gray-600">
                            Actual: <span className="font-semibold">{formatNumber(spk.actualQty)}</span>
                          </span>
                          <span className="text-blue-600 font-semibold">
                            Remaining: {formatNumber(spk.remainingQty)}
                          </span>
                        </div>
                      </div>
                      {selectedSPK?.id === spk.id && (
                        <div className="text-blue-500 text-2xl">✓</div>
                      )}
                    </div>
                  </button>
                ))}
              </div>
            ) : (
              <div className="text-center py-8 bg-white rounded-lg">
                <p className="text-gray-600">No active SPKs found for Cutting department.</p>
              </div>
            )}
            {errors.spk_id && (
              <p className="text-red-600 text-sm mt-2">⚠️ {errors.spk_id.message}</p>
            )}
          </CardContent>
        </Card>

        {/* Step 2: Production Details */}
        {selectedSPK && (
          <>
            <Card variant="bordered">
              <CardHeader>
                <CardTitle>2️⃣ Production Details</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  {/* Production Date */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Production Date <span className="text-red-500">*</span>
                    </label>
                    <input
                      type="date"
                      {...register('date')}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                    {errors.date && (
                      <p className="text-red-600 text-sm mt-1">⚠️ {errors.date.message}</p>
                    )}
                  </div>

                  {/* Good Output */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Good Output (pcs) <span className="text-red-500">*</span>
                    </label>
                    <input
                      type="number"
                      {...register('good_output', { valueAsNumber: true, onChange: updateMaterialEstimate })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      min="0"
                      max={selectedSPK.remainingQty}
                      placeholder="0"
                    />
                    <p className="text-xs text-gray-500 mt-1">
                      Max: {formatNumber(selectedSPK.remainingQty)} pcs
                    </p>
                    {errors.good_output && (
                      <p className="text-red-600 text-sm mt-1">⚠️ {errors.good_output.message}</p>
                    )}
                  </div>

                  {/* Defect Qty */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Defect Qty (pcs)
                    </label>
                    <input
                      type="number"
                      {...register('defect_qty', { valueAsNumber: true })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      min="0"
                      placeholder="0"
                    />
                    {errors.defect_qty && (
                      <p className="text-red-600 text-sm mt-1">⚠️ {errors.defect_qty.message}</p>
                    )}
                  </div>
                </div>

                {/* Total Output Display */}
                <div className="mt-4 bg-blue-50 border-l-4 border-blue-500 p-4 rounded-r-lg">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-gray-700">Total Output (Good + Defect):</p>
                      <p className="text-2xl font-bold text-blue-700 mt-1">
                        {formatNumber(good_output + defect_qty)} pcs
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="text-sm text-gray-600">Defect Rate:</p>
                      <p className="text-lg font-semibold text-gray-900">
                        {good_output + defect_qty > 0
                          ? ((defect_qty / (good_output + defect_qty)) * 100).toFixed(2)
                          : 0}%
                      </p>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Step 3: Material Consumption */}
            <Card variant="bordered">
              <CardHeader>
                <CardTitle>3️⃣ Material Consumption (Fabric)</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {/* Material Input */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      KOHAIR Fabric Used (YARD) <span className="text-red-500">*</span>
                    </label>
                    <input
                      type="number"
                      step="0.01"
                      value={materialUsedQty}
                      onChange={(e) => {
                        const qty = parseFloat(e.target.value) || 0;
                        const fabricMaterial = selectedSPK?.bomMaterials.find(m => m.materialCode.includes('KOHAIR'));
                        if (fabricMaterial) {
                          setValue('material_consumption', [{
                            material_code: fabricMaterial.materialCode,
                            qty_used: qty,
                            uom: 'YARD'
                          }]);
                        }
                      }}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="0.00"
                    />
                    {selectedSPK.bomMaterials.find(m => m.materialCode.includes('KOHAIR')) && (
                      <p className="text-xs text-gray-500 mt-1">
                        BOM Standard: {selectedSPK.bomMaterials.find(m => m.materialCode.includes('KOHAIR'))!.qtyPerUnit} YARD/pcs
                      </p>
                    )}
                  </div>

                  {/* Variance Analysis */}
                  {materialVariance && (
                    <div className={cn(
                      'p-4 rounded-lg border-2',
                      Math.abs(materialVariance.variance) <= 3 ? 'bg-green-50 border-green-300' :
                      Math.abs(materialVariance.variance) <= 5 ? 'bg-yellow-50 border-yellow-300' :
                      'bg-red-50 border-red-300'
                    )}>
                      <h4 className="font-semibold text-gray-900 mb-3">Material Variance Analysis</h4>
                      <div className="grid grid-cols-2 gap-4 text-sm">
                        <div>
                          <p className="text-gray-600">BOM Standard:</p>
                          <p className="font-semibold">{materialVariance.bomStandard.toFixed(2)} YARD</p>
                        </div>
                        <div>
                          <p className="text-gray-600">Actual Used:</p>
                          <p className="font-semibold">{materialVariance.actual.toFixed(2)} YARD</p>
                        </div>
                        <div>
                          <p className="text-gray-600">Variance Qty:</p>
                          <p className={cn(
                            'font-semibold',
                            materialVariance.varianceQty > 0 ? 'text-red-700' : 'text-green-700'
                          )}>
                            {materialVariance.varianceQty > 0 ? '+' : ''}
                            {materialVariance.varianceQty.toFixed(2)} YARD
                          </p>
                        </div>
                        <div>
                          <p className="text-gray-600">Variance %:</p>
                          <p className={cn(
                            'font-bold text-lg',
                            Math.abs(materialVariance.variance) <= 3 ? 'text-green-700' :
                            Math.abs(materialVariance.variance) <= 5 ? 'text-yellow-700' :
                            'text-red-700'
                          )}>
                            {materialVariance.variance > 0 ? '+' : ''}
                            {materialVariance.variance.toFixed(2)}%
                          </p>
                        </div>
                      </div>

                      {/* Variance Status */}
                      <div className="mt-3 pt-3 border-t">
                        {Math.abs(materialVariance.variance) <= 3 && (
                          <p className="text-sm text-green-700 font-medium">
                            ✅ Within normal waste tolerance (0-3%). Auto-approved.
                          </p>
                        )}
                        {Math.abs(materialVariance.variance) > 3 && Math.abs(materialVariance.variance) <= 5 && (
                          <p className="text-sm text-yellow-700 font-medium">
                            ⚠️ Above normal waste (3-5%). Supervisor will review.
                          </p>
                        )}
                        {Math.abs(materialVariance.variance) > 5 && (
                          <p className="text-sm text-red-700 font-medium">
                            ❌ High variance (&gt;5%). Justification required below!
                          </p>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>

            {/* Step 4: Notes (Required if high variance) */}
            {(showVarianceReason || (materialVariance && Math.abs(materialVariance.variance) > 5)) && (
              <Card variant="elevated" className="bg-yellow-50 border-2 border-yellow-400">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <span>4️⃣ Justification</span>
                    <Badge variant="error">Required for Variance &gt;5%</Badge>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <textarea
                    {...register('notes')}
                    rows={4}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Explain the reason for high material variance. Example: 'Kain cacat, harus cut ulang beberapa pieces' or 'Marker tidak optimal, sudah report ke SPV'"
                  />
                  {errors.notes && (
                    <p className="text-red-600 text-sm mt-2">⚠️ {errors.notes.message}</p>
                  )}
                </CardContent>
              </Card>
            )}

            {/* Submit Button */}
            <div className="flex items-center justify-end gap-4">
              <Button
                type="button"
                variant="secondary"
                onClick={() => navigate('/production/calendar')}
              >
                Cancel
              </Button>
              <Button
                type="submit"
                variant="primary"
                disabled={isSubmitting || !selectedSPK}
                isLoading={isSubmitting}
              >
                {isSubmitting ? 'Submitting...' : '✅ Submit Production Input'}
              </Button>
            </div>
          </>
        )}
      </form>
    </div>
  );
}
