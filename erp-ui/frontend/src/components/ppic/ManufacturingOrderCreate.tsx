/**
 * Copyright (C) 2026 - PT Quty Karunia / Daniel Rizaldy
 * Date Created: 2026-02-04
 * 
 * MANUFACTURING ORDER - CREATE MODAL
 * 
 * Specification: Rencana Tampilan.md Lines 853-950
 * 
 * **MO Creation Logic**:
 * - Select Article (with BOM validation)
 * - Set Target Quantity
 * - Link PO Kain (if available) → Status: PARTIAL
 * - Link PO Label (if available) → Status: RELEASED
 * - Auto-inherit Week & Destination from PO Label
 * - Auto-release departments based on status
 */

import React, { useState, useEffect } from 'react'
import { apiClient } from '@/api/client'
import { useUIStore } from '@/stores/uiStore'
import { 
  Package, 
  X, 
  Save, 
  AlertCircle,
  CheckCircle,
  Loader2
} from 'lucide-react'

interface Article {
  id: number
  code: string
  name: string
  bom_available: boolean
}

interface PurchaseOrder {
  id: number
  po_number: string
  po_type: 'KAIN' | 'LABEL' | 'ACCESSORIES'
  article_id: number
  week?: string
  destination?: string
  status: string
}

interface MOFormData {
  article_id: number | null
  target_qty: number
  po_kain_id: number | null
  po_label_id: number | null
  notes?: string
}

interface ManufacturingOrderCreateProps {
  onClose: () => void
  onSuccess: () => void
}

export const ManufacturingOrderCreate: React.FC<ManufacturingOrderCreateProps> = ({ onClose, onSuccess }) => {
  const { addNotification } = useUIStore()
  
  const [formData, setFormData] = useState<MOFormData>({
    article_id: null,
    target_qty: 0,
    po_kain_id: null,
    po_label_id: null
  })

  const [articles, setArticles] = useState<Article[]>([])
  const [poKainList, setPoKainList] = useState<PurchaseOrder[]>([])
  const [poLabelList, setPoLabelList] = useState<PurchaseOrder[]>([])
  const [loading, setLoading] = useState(false)
  const [submitting, setSubmitting] = useState(false)

  // Selected PO Label (for auto-inherit)
  const [selectedPoLabel, setSelectedPoLabel] = useState<PurchaseOrder | null>(null)

  // Fetch articles and POs on mount
  useEffect(() => {
    fetchArticles()
    fetchPurchaseOrders()
  }, [])

  // Fetch POs for selected article
  useEffect(() => {
    if (formData.article_id) {
      fetchPurchaseOrdersForArticle(formData.article_id)
    }
  }, [formData.article_id])

  // Update selected PO Label
  useEffect(() => {
    if (formData.po_label_id) {
      const poLabel = poLabelList.find(po => po.id === formData.po_label_id)
      setSelectedPoLabel(poLabel || null)
    } else {
      setSelectedPoLabel(null)
    }
  }, [formData.po_label_id, poLabelList])

  const fetchArticles = async () => {
    try {
      const response = await apiClient.get('/articles')
      setArticles(response.data)
    } catch (error) {
      addNotification({ type: 'error', message: 'Failed to load articles' })
    }
  }

  const fetchPurchaseOrders = async () => {
    try {
      const [kainRes, labelRes] = await Promise.all([
        apiClient.get('/purchasing/purchase-orders', { params: { po_type: 'KAIN', status: 'APPROVED' } }),
        apiClient.get('/purchasing/purchase-orders', { params: { po_type: 'LABEL', status: 'APPROVED' } })
      ])
      setPoKainList(kainRes.data)
      setPoLabelList(labelRes.data)
    } catch (error) {
      addNotification({ type: 'error', message: 'Failed to load purchase orders' })
    }
  }

  const fetchPurchaseOrdersForArticle = async (articleId: number) => {
    try {
      setLoading(true)
      const [kainRes, labelRes] = await Promise.all([
        apiClient.get('/purchasing/purchase-orders', { 
          params: { po_type: 'KAIN', article_id: articleId, status: 'APPROVED' } 
        }),
        apiClient.get('/purchasing/purchase-orders', { 
          params: { po_type: 'LABEL', article_id: articleId, status: 'APPROVED' } 
        })
      ])
      setPoKainList(kainRes.data)
      setPoLabelList(labelRes.data)
    } catch (error) {
      addNotification({ type: 'error', message: 'Failed to load purchase orders for article' })
    } finally {
      setLoading(false)
    }
  }

  const validateForm = (): string | null => {
    if (!formData.article_id) return 'Article is required'
    if (formData.target_qty <= 0) return 'Target quantity must be > 0'
    
    // Must have at least PO Kain to create MO
    if (!formData.po_kain_id) {
      return 'PO Kain is required to create MO (minimum for PARTIAL status)'
    }

    return null
  }

  const handleSubmit = async () => {
    const validationError = validateForm()
    if (validationError) {
      addNotification({ type: 'error', message: validationError })
      return
    }

    try {
      setSubmitting(true)

      // Determine initial status
      // - If PO Label linked → RELEASED (all departments unlocked)
      // - If only PO Kain → PARTIAL (Cutting/Embroidery only)
      const initialStatus = formData.po_label_id ? 'RELEASED' : 'PARTIAL'

      const payload = {
        article_id: formData.article_id,
        target_qty: formData.target_qty,
        po_kain_id: formData.po_kain_id,
        po_label_id: formData.po_label_id,
        status: initialStatus,
        week: selectedPoLabel?.week || null,              // Auto-inherit from PO Label
        destination: selectedPoLabel?.destination || null, // Auto-inherit from PO Label
        notes: formData.notes
      }

      await apiClient.post('/ppic/manufacturing-orders', payload)

      addNotification({ 
        type: 'success', 
        message: `✅ MO created successfully with status: ${initialStatus === 'PARTIAL' ? '🟡 PARTIAL' : '🟢 RELEASED'}` 
      })
      onSuccess()
      onClose()
    } catch (error: any) {
      addNotification({ 
        type: 'error', 
        message: error.response?.data?.detail || 'Failed to create Manufacturing Order' 
      })
    } finally {
      setSubmitting(false)
    }
  }

  // Determine MO status based on linked POs
  const determineMOStatus = () => {
    if (formData.po_label_id) return '🟢 RELEASED (Full Production)'
    if (formData.po_kain_id) return '🟡 PARTIAL (Cutting/Embroidery Only)'
    return 'DRAFT'
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl shadow-2xl max-w-3xl w-full max-h-[95vh] overflow-hidden flex flex-col">
        
        {/* Header */}
        <div className="bg-gradient-to-r from-blue-600 to-indigo-700 text-white px-6 py-4 flex justify-between items-center">
          <div>
            <h2 className="text-2xl font-bold">Create Manufacturing Order</h2>
            <p className="text-sm text-blue-100 mt-1">
              🚀 Dual-Stage System: PARTIAL → RELEASED
            </p>
          </div>
          <button onClick={onClose} className="text-white hover:bg-white/20 p-2 rounded-lg transition-colors">
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Body */}
        <div className="flex-1 overflow-y-auto p-6 space-y-5">
          
          {/* Article Selection */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              Article <span className="text-red-500">*</span>
            </label>
            <select
              value={formData.article_id || ''}
              onChange={(e) => {
                const articleId = parseInt(e.target.value)
                setFormData(prev => ({ 
                  ...prev, 
                  article_id: articleId,
                  po_kain_id: null,  // Reset POs when article changes
                  po_label_id: null
                }))
              }}
              className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">Select Article...</option>
              {articles.map(article => (
                <option key={article.id} value={article.id}>
                  [{article.code}] {article.name} {article.bom_available ? '✅' : '⚠️ No BOM'}
                </option>
              ))}
            </select>
          </div>

          {/* Target Quantity */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              Target Quantity (pcs) <span className="text-red-500">*</span>
            </label>
            <input
              type="number"
              min="1"
              value={formData.target_qty || ''}
              onChange={(e) => setFormData(prev => ({ ...prev, target_qty: parseInt(e.target.value) || 0 }))}
              placeholder="e.g. 450"
              className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          {/* PO Linking Section */}
          {formData.article_id && (
            <div className="space-y-4 bg-gray-50 rounded-lg p-5 border border-gray-200">
              <h3 className="font-semibold text-gray-800 flex items-center gap-2">
                <Package className="w-5 h-5 text-blue-600" />
                Link Purchase Orders (Determines MO Status)
              </h3>

              {/* PO Kain */}
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  PO Kain <span className="text-red-500">*</span> (Required for PARTIAL status)
                </label>
                {loading ? (
                  <div className="flex items-center gap-2 text-gray-600">
                    <Loader2 className="w-4 h-4 animate-spin" />
                    Loading PO Kain...
                  </div>
                ) : poKainList.length === 0 ? (
                  <div className="bg-amber-50 border border-amber-200 rounded-lg p-3 text-sm text-gray-700">
                    <AlertCircle className="w-4 h-4 text-amber-600 inline mr-2" />
                    No approved PO Kain found for this article. Create PO Kain first.
                  </div>
                ) : (
                  <select
                    value={formData.po_kain_id || ''}
                    onChange={(e) => setFormData(prev => ({ ...prev, po_kain_id: parseInt(e.target.value) || null }))}
                    className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="">Select PO Kain...</option>
                    {poKainList.map(po => (
                      <option key={po.id} value={po.id}>
                        {po.po_number} (Status: {po.status})
                      </option>
                    ))}
                  </select>
                )}
              </div>

              {/* PO Label */}
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  PO Label (Optional - Upgrades to RELEASED if linked)
                </label>
                {loading ? (
                  <div className="flex items-center gap-2 text-gray-600">
                    <Loader2 className="w-4 h-4 animate-spin" />
                    Loading PO Label...
                  </div>
                ) : poLabelList.length === 0 ? (
                  <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 text-sm text-gray-700">
                    <AlertCircle className="w-4 h-4 text-blue-600 inline mr-2" />
                    No approved PO Label found. MO will be created with PARTIAL status.
                  </div>
                ) : (
                  <select
                    value={formData.po_label_id || ''}
                    onChange={(e) => setFormData(prev => ({ ...prev, po_label_id: parseInt(e.target.value) || null }))}
                    className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="">No PO Label (Create as PARTIAL)</option>
                    {poLabelList.map(po => (
                      <option key={po.id} value={po.id}>
                        {po.po_number} | Week: {po.week || 'N/A'} | Dest: {po.destination || 'N/A'}
                      </option>
                    ))}
                  </select>
                )}
              </div>

              {/* Auto-inherit Preview (Lines 918-919) */}
              {selectedPoLabel && (
                <div className="bg-green-50 border border-green-200 rounded-lg p-4 space-y-2">
                  <div className="flex items-center gap-2 text-green-700 font-semibold">
                    <CheckCircle className="w-5 h-5" />
                    Auto-inherit from PO Label (Locked after creation):
                  </div>
                  <div className="grid grid-cols-2 gap-3 text-sm">
                    <div>
                      <span className="text-gray-600">Week:</span>
                      <span className="ml-2 font-semibold">{selectedPoLabel.week || 'N/A'} 🔒</span>
                    </div>
                    <div>
                      <span className="text-gray-600">Destination:</span>
                      <span className="ml-2 font-semibold">{selectedPoLabel.destination || 'N/A'} 🔒</span>
                    </div>
                  </div>
                  <p className="text-xs text-gray-600">
                    ℹ️ Week & Destination will be locked and cannot be edited after MO creation
                  </p>
                </div>
              )}
            </div>
          )}

          {/* MO Status Preview */}
          {formData.article_id && formData.po_kain_id && (
            <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border-2 border-blue-200 rounded-lg p-4">
              <div className="flex items-center gap-3">
                <Package className="w-6 h-6 text-blue-600" />
                <div className="flex-1">
                  <p className="text-sm text-gray-600">Initial MO Status:</p>
                  <p className="text-lg font-bold text-gray-800">{determineMOStatus()}</p>
                </div>
              </div>

              {/* Department Release Preview (Lines 890-900) */}
              <div className="mt-3 space-y-1 text-sm text-gray-700">
                {formData.po_label_id ? (
                  <>
                    <p className="font-semibold text-green-700">✅ All Departments RELEASED:</p>
                    <p>• Cutting, Embroidery, Sewing, Finishing, Packing can start</p>
                  </>
                ) : (
                  <>
                    <p className="font-semibold text-yellow-700">🟡 Partial Release:</p>
                    <p>• ✅ Cutting & Embroidery can start (3-5 days earlier!)</p>
                    <p>• 🔒 Sewing, Finishing, Packing: HOLD (waiting PO Label)</p>
                  </>
                )}
              </div>
            </div>
          )}

          {/* Notes */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              Notes (Optional)
            </label>
            <textarea
              value={formData.notes || ''}
              onChange={(e) => setFormData(prev => ({ ...prev, notes: e.target.value }))}
              placeholder="Additional notes for this MO..."
              rows={3}
              className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
            />
          </div>

        </div>

        {/* Footer */}
        <div className="bg-gray-50 px-6 py-4 border-t border-gray-200 flex justify-between">
          <button 
            onClick={onClose} 
            className="px-6 py-2 border border-gray-300 rounded-lg hover:bg-gray-100 transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={handleSubmit}
            disabled={submitting || !formData.article_id || !formData.po_kain_id || formData.target_qty <= 0}
            className="flex items-center gap-2 px-8 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {submitting ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                Creating MO...
              </>
            ) : (
              <>
                <Save className="w-5 h-5" />
                Create MO
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  )
}
