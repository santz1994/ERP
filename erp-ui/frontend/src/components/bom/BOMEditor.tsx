/**
 * BOM Editor Component - Session 24
 * Edit BOM details with multi-material variant support
 */

import React, { useState } from 'react'
import { useQuery, useMutation } from '@tanstack/react-query'
import { apiClient } from '@/api/client'
import { Trash2, Plus, Edit2, CheckCircle, AlertCircle, Loader } from 'lucide-react'
import { useUIStore } from '@/store'

export interface BOMVariant {
  id: number
  material_id: number
  variant_type: 'Primary' | 'Alternative' | 'Optional'
  sequence: number
  qty_variance?: number
  qty_variance_percent?: number
  weight: number
  selection_probability: number
  cost_variance: number
  is_active: boolean
  approval_status: string
}

export interface BOMDetail {
  id: number
  component_id: number
  qty_needed: number
  wastage_percent: number
  has_variants: boolean
  variant_selection_mode: string
  variants: BOMVariant[]
}

export interface BOMEditorProps {
  bomDetailId: number
  onUpdate?: () => void
}

export const BOMEditor: React.FC<BOMEditorProps> = ({ bomDetailId, onUpdate }) => {
  const { addNotification } = useUIStore()
  const [expandedVariants, setExpandedVariants] = useState(false)
  const [newVariantMode, setNewVariantMode] = useState(false)
  const [editingVariantId, setEditingVariantId] = useState<number | null>(null)

  const [newVariant, setNewVariant] = useState({
    material_id: 0,
    variant_type: 'Alternative',
    sequence: 1,
    qty_variance: '',
    qty_variance_percent: '',
    weight: 1.0,
    cost_variance: 0,
    notes: '',
  })

  // Fetch BOM detail
  const { data: bomDetail, isLoading } = useQuery({
    queryKey: ['bom-detail', bomDetailId],
    queryFn: async () => {
      const response = await apiClient.get(`/bom/details/${bomDetailId}`)
      return response.data as BOMDetail
    },
  })

  // Add variant mutation
  const addVariantMutation = useMutation({
    mutationFn: async (variant: typeof newVariant) => {
      return await apiClient.post(`/bom/details/${bomDetailId}/variants`, {
        material_id: parseInt(variant.material_id as any),
        variant_type: variant.variant_type,
        sequence: variant.sequence,
        qty_variance: variant.qty_variance ? parseFloat(variant.qty_variance) : null,
        qty_variance_percent: variant.qty_variance_percent ? parseFloat(variant.qty_variance_percent) : null,
        weight: variant.weight,
        cost_variance: parseFloat(variant.cost_variance as any),
        notes: variant.notes || null,
      })
    },
    onSuccess: () => {
      addNotification('success', 'Variant added successfully')
      setNewVariant({
        material_id: 0,
        variant_type: 'Alternative',
        sequence: 1,
        qty_variance: '',
        qty_variance_percent: '',
        weight: 1.0,
        cost_variance: 0,
        notes: '',
      })
      setNewVariantMode(false)
      onUpdate?.()
    },
    onError: (error: any) => {
      addNotification('error', error.response?.data?.detail || 'Failed to add variant')
    },
  })

  // Delete variant mutation
  const deleteVariantMutation = useMutation({
    mutationFn: async (variantId: number) => {
      return await apiClient.delete(`/bom/variants/${variantId}`)
    },
    onSuccess: () => {
      addNotification('success', 'Variant deleted')
      onUpdate?.()
    },
    onError: (error: any) => {
      addNotification('error', 'Failed to delete variant')
    },
  })

  // Toggle multi-material support
  const toggleMultiMaterialMutation = useMutation({
    mutationFn: async (enabled: boolean) => {
      return await apiClient.patch(`/bom/details/${bomDetailId}/multi-material`, {
        has_variants: enabled,
      })
    },
    onSuccess: () => {
      addNotification('success', 'Multi-material support updated')
      onUpdate?.()
    },
  })

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-6">
        <Loader className="w-5 h-5 text-blue-600 animate-spin mr-2" />
        <span>Loading BOM details...</span>
      </div>
    )
  }

  if (!bomDetail) {
    return (
      <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
        <AlertCircle className="w-5 h-5 text-yellow-600 inline mr-2" />
        BOM detail not found
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {/* BOM Detail Header */}
      <div className="bg-white rounded-lg border border-gray-200 p-4">
        <div className="flex justify-between items-start mb-4">
          <div>
            <h3 className="font-semibold text-gray-900">
              Component ID: {bomDetail.component_id}
            </h3>
            <p className="text-sm text-gray-600">
              Quantity: {bomDetail.qty_needed} | Wastage: {bomDetail.wastage_percent}%
            </p>
          </div>
          <button
            onClick={() =>
              toggleMultiMaterialMutation.mutate(!bomDetail.has_variants)
            }
            disabled={toggleMultiMaterialMutation.isPending}
            className={`px-3 py-1 rounded text-sm font-medium transition-colors ${
              bomDetail.has_variants
                ? 'bg-blue-100 text-blue-700 hover:bg-blue-200'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            {bomDetail.has_variants ? 'Multi-Material' : 'Single Material'}
          </button>
        </div>

        {/* Multi-material Info */}
        {bomDetail.has_variants && (
          <div className="p-3 bg-blue-50 border border-blue-200 rounded text-sm text-blue-800">
            <CheckCircle className="w-4 h-4 inline mr-1" />
            Multi-material variants enabled (Mode: {bomDetail.variant_selection_mode})
          </div>
        )}
      </div>

      {/* Variants List */}
      {bomDetail.has_variants && (
        <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
          <div className="p-4 bg-gray-50 border-b flex justify-between items-center">
            <h4 className="font-semibold text-gray-900">
              Variants ({bomDetail.variants.length})
            </h4>
            <button
              onClick={() => setNewVariantMode(!newVariantMode)}
              className="px-3 py-1 bg-blue-600 hover:bg-blue-700 text-white rounded text-sm font-medium flex items-center gap-1"
            >
              <Plus className="w-4 h-4" />
              Add Variant
            </button>
          </div>

          {/* New Variant Form */}
          {newVariantMode && (
            <div className="p-4 bg-blue-50 border-b space-y-3">
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Material ID
                  </label>
                  <input
                    type="number"
                    value={newVariant.material_id}
                    onChange={(e) =>
                      setNewVariant({ ...newVariant, material_id: parseInt(e.target.value) || 0 })
                    }
                    className="w-full px-2 py-1 border border-gray-300 rounded text-sm"
                    placeholder="Material ID"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Type
                  </label>
                  <select
                    value={newVariant.variant_type}
                    onChange={(e) =>
                      setNewVariant({ ...newVariant, variant_type: e.target.value })
                    }
                    className="w-full px-2 py-1 border border-gray-300 rounded text-sm"
                  >
                    <option>Primary</option>
                    <option>Alternative</option>
                    <option>Optional</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Qty Override
                  </label>
                  <input
                    type="number"
                    step="0.01"
                    value={newVariant.qty_variance}
                    onChange={(e) =>
                      setNewVariant({ ...newVariant, qty_variance: e.target.value })
                    }
                    className="w-full px-2 py-1 border border-gray-300 rounded text-sm"
                    placeholder="Leave blank if same"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Weight
                  </label>
                  <input
                    type="number"
                    step="0.1"
                    value={newVariant.weight}
                    onChange={(e) =>
                      setNewVariant({
                        ...newVariant,
                        weight: parseFloat(e.target.value) || 1.0,
                      })
                    }
                    className="w-full px-2 py-1 border border-gray-300 rounded text-sm"
                  />
                </div>
              </div>

              <div className="flex gap-2">
                <button
                  onClick={() => addVariantMutation.mutate(newVariant)}
                  disabled={addVariantMutation.isPending || !newVariant.material_id}
                  className="flex-1 px-3 py-2 bg-green-600 hover:bg-green-700 text-white rounded text-sm font-medium disabled:opacity-50"
                >
                  {addVariantMutation.isPending ? 'Adding...' : 'Add Variant'}
                </button>
                <button
                  onClick={() => setNewVariantMode(false)}
                  className="flex-1 px-3 py-2 bg-gray-300 hover:bg-gray-400 text-gray-700 rounded text-sm font-medium"
                >
                  Cancel
                </button>
              </div>
            </div>
          )}

          {/* Variants Rows */}
          <div className="divide-y">
            {bomDetail.variants.map((variant) => (
              <div key={variant.id} className="p-4 hover:bg-gray-50">
                <div className="flex justify-between items-start mb-2">
                  <div>
                    <span className="inline-block px-2 py-1 bg-gray-200 text-xs font-medium rounded mr-2">
                      {variant.variant_type}
                    </span>
                    <span className="text-sm text-gray-600">
                      Material ID: {variant.material_id} (Seq: {variant.sequence})
                    </span>
                  </div>
                  <button
                    onClick={() => deleteVariantMutation.mutate(variant.id)}
                    disabled={deleteVariantMutation.isPending}
                    className="text-red-600 hover:text-red-800"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
                <div className="grid grid-cols-4 gap-2 text-xs text-gray-600">
                  <div>Weight: {variant.weight}</div>
                  <div>
                    Probability:{' '}
                    {typeof variant.selection_probability === 'number'
                      ? `${variant.selection_probability.toFixed(1)}%`
                      : 'N/A'}
                  </div>
                  <div>Cost Δ: {variant.cost_variance}</div>
                  <div>
                    Status:{' '}
                    <span className={`font-medium ${
                      variant.approval_status === 'approved'
                        ? 'text-green-600'
                        : variant.approval_status === 'rejected'
                        ? 'text-red-600'
                        : 'text-yellow-600'
                    }`}>
                      {variant.approval_status}
                    </span>
                  </div>
                </div>
              </div>
            ))}
            {bomDetail.variants.length === 0 && (
              <div className="p-4 text-center text-gray-500">
                No variants added yet
              </div>
            )}
          </div>
        </div>
      )}

      {/* Info: Single Material */}
      {!bomDetail.has_variants && (
        <div className="p-4 bg-gray-50 border border-gray-200 rounded-lg text-sm text-gray-600">
          <AlertCircle className="w-4 h-4 inline mr-2" />
          This BOM line uses a single material. Enable multi-material support to add alternatives.
        </div>
      )}
    </div>
  )
}

export default BOMEditor
