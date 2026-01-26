/**
 * BOM Builder Component - Session 24
 * Create and edit Bill of Materials with multi-material variant support
 */

import React, { useState } from 'react'
import { useQuery, useMutation } from '@tanstack/react-query'
import { apiClient } from '@/api/client'
import { Plus, Trash2, Edit2, Save, X, AlertCircle } from 'lucide-react'
import BOMEditor from './BOMEditor'
import { useUIStore } from '@/store'

export interface BOMDetail {
  id: number
  component_id: number
  qty_needed: number
  wastage_percent: number
  has_variants: boolean
}

export interface BOM {
  id: number
  product_id: number
  bom_type: string
  qty_output: number
  is_active: boolean
  revision: string
  supports_multi_material: boolean
  details: BOMDetail[]
}

export interface BOMBuilderProps {
  productId: number
  onSave?: (bom: BOM) => void
}

export const BOMBuilder: React.FC<BOMBuilderProps> = ({ productId, onSave }) => {
  const { addNotification } = useUIStore()
  const [showNewDetail, setShowNewDetail] = useState(false)
  const [editingDetailId, setEditingDetailId] = useState<number | null>(null)

  const [newDetail, setNewDetail] = useState({
    component_id: 0,
    qty_needed: 0,
    wastage_percent: 0,
    has_variants: false,
  })

  // Fetch BOM for product
  const { data: bom, isLoading, refetch } = useQuery({
    queryKey: ['bom', productId],
    queryFn: async () => {
      try {
        const response = await apiClient.get(`/bom/product/${productId}`)
        return response.data as BOM
      } catch (error: any) {
        if (error.response?.status === 404) {
          return null // No BOM exists yet
        }
        throw error
      }
    },
  })

  // Create BOM mutation
  const createBOMMutation = useMutation({
    mutationFn: async (bom_type: string) => {
      return await apiClient.post('/bom', {
        product_id: productId,
        bom_type: bom_type,
        qty_output: 1.0,
        supports_multi_material: true,
      })
    },
    onSuccess: (data) => {
      addNotification('success', 'BOM created successfully')
      refetch()
    },
    onError: (error: any) => {
      addNotification('error', error.response?.data?.detail || 'Failed to create BOM')
    },
  })

  // Add detail mutation
  const addDetailMutation = useMutation({
    mutationFn: async (detail: typeof newDetail) => {
      if (!bom) throw new Error('No BOM selected')
      return await apiClient.post(`/bom/${bom.id}/details`, {
        component_id: detail.component_id,
        qty_needed: parseFloat(detail.qty_needed as any),
        wastage_percent: parseFloat(detail.wastage_percent as any),
        has_variants: detail.has_variants,
      })
    },
    onSuccess: () => {
      addNotification('success', 'BOM detail added')
      setNewDetail({
        component_id: 0,
        qty_needed: 0,
        wastage_percent: 0,
        has_variants: false,
      })
      setShowNewDetail(false)
      refetch()
    },
    onError: (error: any) => {
      addNotification('error', error.response?.data?.detail || 'Failed to add detail')
    },
  })

  // Delete detail mutation
  const deleteDetailMutation = useMutation({
    mutationFn: async (detailId: number) => {
      return await apiClient.delete(`/bom/details/${detailId}`)
    },
    onSuccess: () => {
      addNotification('success', 'BOM detail removed')
      refetch()
    },
    onError: (error: any) => {
      addNotification('error', 'Failed to remove detail')
    },
  })

  if (isLoading) {
    return (
      <div className="p-6 text-center">
        <div className="inline-block h-8 w-8 border-4 border-blue-500 border-t-transparent rounded-full animate-spin" />
        <p className="mt-2 text-gray-600">Loading BOM...</p>
      </div>
    )
  }

  // No BOM exists yet
  if (!bom) {
    return (
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <div className="text-center mb-6">
          <AlertCircle className="w-12 h-12 text-yellow-600 mx-auto mb-3" />
          <h3 className="text-lg font-semibold text-gray-900">No BOM Found</h3>
          <p className="text-gray-600 mt-1">Create a new Bill of Materials for this product</p>
        </div>

        <div className="space-y-3 max-w-sm mx-auto">
          <button
            onClick={() => createBOMMutation.mutate('Manufacturing')}
            disabled={createBOMMutation.isPending}
            className="w-full px-4 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors disabled:opacity-50 flex items-center justify-center gap-2"
          >
            <Plus className="w-5 h-5" />
            Create Manufacturing BOM
          </button>
          <button
            onClick={() => createBOMMutation.mutate('Kit/Phantom')}
            disabled={createBOMMutation.isPending}
            className="w-full px-4 py-3 bg-purple-600 hover:bg-purple-700 text-white rounded-lg font-medium transition-colors disabled:opacity-50 flex items-center justify-center gap-2"
          >
            <Plus className="w-5 h-5" />
            Create Kit/Phantom BOM
          </button>
        </div>
      </div>
    )
  }

  // BOM exists - show details
  return (
    <div className="space-y-6">
      {/* BOM Header */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <div className="flex justify-between items-start mb-4">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">
              BOM - Product ID {bom.product_id}
            </h2>
            <p className="text-gray-600 mt-1">
              Type: <span className="font-medium">{bom.bom_type}</span> | Revision:{' '}
              <span className="font-medium">{bom.revision}</span>
            </p>
          </div>
          <div className="flex gap-2">
            <button
              className={`px-3 py-1 rounded text-sm font-medium ${
                bom.is_active
                  ? 'bg-green-100 text-green-700'
                  : 'bg-gray-100 text-gray-700'
              }`}
            >
              {bom.is_active ? '✓ Active' : '⊘ Inactive'}
            </button>
            <button
              className={`px-3 py-1 rounded text-sm font-medium ${
                bom.supports_multi_material
                  ? 'bg-blue-100 text-blue-700'
                  : 'bg-gray-100 text-gray-700'
              }`}
            >
              {bom.supports_multi_material ? 'Multi-Material ✓' : 'Single Material'}
            </button>
          </div>
        </div>
      </div>

      {/* BOM Details List */}
      <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
        <div className="p-4 bg-gray-50 border-b flex justify-between items-center">
          <h3 className="font-semibold text-gray-900">
            BOM Details ({bom.details.length})
          </h3>
          <button
            onClick={() => setShowNewDetail(!showNewDetail)}
            className="px-3 py-1 bg-blue-600 hover:bg-blue-700 text-white rounded text-sm font-medium flex items-center gap-1"
          >
            <Plus className="w-4 h-4" />
            Add Line Item
          </button>
        </div>

        {/* New Detail Form */}
        {showNewDetail && (
          <div className="p-4 bg-blue-50 border-b space-y-3">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-2">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Component ID
                </label>
                <input
                  type="number"
                  value={newDetail.component_id}
                  onChange={(e) =>
                    setNewDetail({ ...newDetail, component_id: parseInt(e.target.value) || 0 })
                  }
                  className="w-full px-2 py-1 border border-gray-300 rounded text-sm"
                  placeholder="Material ID"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Quantity Needed
                </label>
                <input
                  type="number"
                  step="0.01"
                  value={newDetail.qty_needed}
                  onChange={(e) =>
                    setNewDetail({ ...newDetail, qty_needed: e.target.value as any })
                  }
                  className="w-full px-2 py-1 border border-gray-300 rounded text-sm"
                  placeholder="0.00"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Wastage %
                </label>
                <input
                  type="number"
                  step="0.01"
                  value={newDetail.wastage_percent}
                  onChange={(e) =>
                    setNewDetail({ ...newDetail, wastage_percent: e.target.value as any })
                  }
                  className="w-full px-2 py-1 border border-gray-300 rounded text-sm"
                  placeholder="0.00"
                />
              </div>
              <div className="flex items-end">
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={newDetail.has_variants}
                    onChange={(e) =>
                      setNewDetail({ ...newDetail, has_variants: e.target.checked })
                    }
                    className="w-4 h-4"
                  />
                  <span className="text-sm font-medium text-gray-700">Multi-Material</span>
                </label>
              </div>
            </div>

            <div className="flex gap-2">
              <button
                onClick={() => addDetailMutation.mutate(newDetail)}
                disabled={addDetailMutation.isPending || !newDetail.component_id}
                className="flex-1 px-3 py-2 bg-green-600 hover:bg-green-700 text-white rounded text-sm font-medium disabled:opacity-50"
              >
                {addDetailMutation.isPending ? 'Adding...' : 'Add Detail'}
              </button>
              <button
                onClick={() => setShowNewDetail(false)}
                className="flex-1 px-3 py-2 bg-gray-300 hover:bg-gray-400 text-gray-700 rounded text-sm font-medium"
              >
                Cancel
              </button>
            </div>
          </div>
        )}

        {/* Details Table */}
        {bom.details.length > 0 ? (
          <div className="divide-y">
            {bom.details.map((detail) => (
              <div key={detail.id} className="p-4 hover:bg-gray-50">
                <div className="flex justify-between items-start mb-3">
                  <div>
                    <h4 className="font-medium text-gray-900">
                      Component ID: {detail.component_id}
                    </h4>
                    <p className="text-sm text-gray-600">
                      Qty: {detail.qty_needed} | Wastage: {detail.wastage_percent}%
                    </p>
                    {detail.has_variants && (
                      <span className="inline-block mt-2 px-2 py-1 bg-blue-100 text-blue-700 text-xs font-medium rounded">
                        Multi-Material ✓
                      </span>
                    )}
                  </div>

                  <div className="flex gap-2">
                    <button
                      onClick={() => setEditingDetailId(detail.id)}
                      className="p-2 hover:bg-blue-100 text-blue-600 rounded"
                    >
                      <Edit2 className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => deleteDetailMutation.mutate(detail.id)}
                      className="p-2 hover:bg-red-100 text-red-600 rounded"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>

                {/* Inline Editor */}
                {editingDetailId === detail.id && (
                  <div className="mt-3 p-3 bg-blue-50 border border-blue-200 rounded">
                    <BOMEditor
                      bomDetailId={detail.id}
                      onUpdate={() => {
                        setEditingDetailId(null)
                        refetch()
                      }}
                    />
                  </div>
                )}
              </div>
            ))}
          </div>
        ) : (
          <div className="p-6 text-center text-gray-500">
            No BOM details yet. Add line items to get started.
          </div>
        )}
      </div>

      {/* Action Buttons */}
      <div className="flex gap-3">
        <button
          onClick={() => onSave?.(bom)}
          className="flex-1 px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg font-medium transition-colors flex items-center justify-center gap-2"
        >
          <Save className="w-4 h-4" />
          Save BOM
        </button>
        <button className="flex-1 px-4 py-2 bg-gray-300 hover:bg-gray-400 text-gray-700 rounded-lg font-medium transition-colors">
          Cancel
        </button>
      </div>
    </div>
  )
}

export default BOMBuilder
