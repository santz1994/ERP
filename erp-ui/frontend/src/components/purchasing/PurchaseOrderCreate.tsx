/**
 * Copyright (c) 2026 PT Quty Karunia / Daniel Rizaldy - All Rights Reserved
 * File: PurchaseOrderCreate.tsx | Date: 2026-02-05
 * Specification: Rencana Tampilan.md Lines 620-850
 * 
 * DUAL-MODE PURCHASE ORDER SYSTEM:
 * MODE 1: AUTO from ARTICLE (BOM Explosion) - 80% time savings
 * MODE 2: MANUAL INPUT - Full flexibility
 */

import React, { useState, useEffect } from 'react'
import { 
  Bot, 
  Edit3, 
  Package, 
  AlertCircle, 
  CheckCircle, 
  Loader2,
  X,
  Plus,
  Trash2,
  Search,
  TrendingUp
} from 'lucide-react'
import { apiClient } from '@/api/client'
import { useUIStore } from '@/store'

type POMode = 'AUTO_BOM' | 'MANUAL'
type POType = 'KAIN' | 'LABEL' | 'ACCESSORIES'

interface Article {
  id: number
  code: string
  name: string
  bom_available: boolean
}

interface BOMExplosionResult {
  article_id: number
  article_code: string
  article_name: string
  quantity: number
  materials: BOMExplosionMaterial[]
  total_estimated_cost: number
}

interface BOMExplosionMaterial {
  id: number
  material_code: string
  material_name: string
  material_type: 'RAW' | 'BAHAN_PENOLONG' | 'WIP'
  quantity: number
  uom: string
  suggested_supplier_id?: number
  suggested_supplier_name?: string
}

interface Supplier {
  id: number
  name: string
  material_specialization?: string[]
}

interface POFormData {
  po_number_ikea?: string
  po_type: POType
  order_date: string
  expected_date: string
  week?: string
  destination?: string
  mode: POMode
  article_id?: number
  article_quantity?: number
  materials: MaterialItem[]
}

interface MaterialItem {
  id: string
  material_code: string
  material_name: string
  material_type: string
  supplier_id: number | null
  description?: string
  quantity: number
  uom: string
  unit_price: number
  is_auto_generated: boolean
}

interface PurchaseOrderCreateProps {
  onClose: () => void
  onSuccess: () => void
}

export const PurchaseOrderCreate: React.FC<PurchaseOrderCreateProps> = ({ onClose, onSuccess }) => {
  const { addNotification } = useUIStore()
  
  // Form state
  const [mode, setMode] = useState<POMode>('AUTO_BOM')
  const [formData, setFormData] = useState<POFormData>({
    po_type: 'KAIN',
    order_date: new Date().toISOString().split('T')[0],
    expected_date: '',
    mode: 'AUTO_BOM',
    materials: []
  })
  
  // Data fetching state
  const [articles, setArticles] = useState<Article[]>([])
  const [suppliers, setSuppliers] = useState<Supplier[]>([])
  const [loadingArticles, setLoadingArticles] = useState(false)
  const [loadingBOM, setLoadingBOM] = useState(false)
  const [bomExplosion, setBomExplosion] = useState<BOMExplosionResult | null>(null)
  const [submitting, setSubmitting] = useState(false)

  // Load articles and suppliers on mount
  useEffect(() => {
    fetchArticles()
    fetchSuppliers()
  }, [])

  const fetchArticles = async () => {
    try {
      setLoadingArticles(true)
      const response = await apiClient.get('/articles')
      setArticles(response.data)
    } catch (error) {
      console.error('Failed to fetch articles:', error)
      addNotification({ type: 'error', message: 'Failed to load articles' })
    } finally {
      setLoadingArticles(false)
    }
  }

  const fetchSuppliers = async () => {
    try {
      const response = await apiClient.get('/suppliers')
      setSuppliers(response.data)
    } catch (error) {
      console.error('Failed to fetch suppliers:', error)
    }
  }

  const handleModeSwitch = (newMode: POMode) => {
    setMode(newMode)
    setFormData(prev => ({ ...prev, mode: newMode, materials: [] }))
    setBomExplosion(null)
  }

  const handleArticleSelect = async (articleId: number) => {
    if (!formData.article_quantity || formData.article_quantity <= 0) {
      addNotification({ type: 'warning', message: 'Please enter article quantity first' })
      return
    }

    try {
      setLoadingBOM(true)
      const response = await apiClient.get(`/bom-explosion/${articleId}`, {
        params: { quantity: formData.article_quantity }
      })
      
      const explosion: BOMExplosionResult = response.data
      setBomExplosion(explosion)
      
      // Convert BOM materials to material items
      const materials: MaterialItem[] = explosion.materials.map(mat => ({
        id: `auto-${mat.id}-${Date.now()}`,
        material_code: mat.material_code,
        material_name: mat.material_name,
        material_type: mat.material_type,
        supplier_id: mat.suggested_supplier_id || null,
        quantity: mat.quantity,
        uom: mat.uom,
        unit_price: 0,
        is_auto_generated: true
      }))
      
      setFormData(prev => ({ ...prev, materials }))
      
      addNotification({ 
        type: 'success', 
        message: `BOM Explosion successful! ${explosion.materials.length} materials generated` 
      })
    } catch (error: any) {
      console.error('BOM Explosion failed:', error)
      addNotification({ 
        type: 'error', 
        message: error.response?.data?.detail || 'BOM Explosion failed' 
      })
    } finally {
      setLoadingBOM(false)
    }
  }

  const addManualMaterial = () => {
    const newMaterial: MaterialItem = {
      id: `manual-${Date.now()}`,
      material_code: '',
      material_name: '',
      material_type: 'RAW',
      supplier_id: null,
      quantity: 0,
      uom: 'PCS',
      unit_price: 0,
      is_auto_generated: false
    }
    setFormData(prev => ({ ...prev, materials: [...prev.materials, newMaterial] }))
  }

  const removeMaterial = (id: string) => {
    setFormData(prev => ({
      ...prev,
      materials: prev.materials.filter(m => m.id !== id)
    }))
  }

  const updateMaterial = (id: string, field: keyof MaterialItem, value: any) => {
    setFormData(prev => ({
      ...prev,
      materials: prev.materials.map(m => 
        m.id === id ? { ...m, [field]: value } : m
      )
    }))
  }

  const validateForm = (): string | null => {
    if (!formData.order_date) return 'Order date is required'
    if (!formData.expected_date) return 'Expected delivery date is required'
    if (formData.materials.length === 0) return 'At least one material is required'
    
    // Validate each material
    for (const material of formData.materials) {
      if (!material.material_name) return `Material name is required`
      if (!material.supplier_id) return `Supplier is required for ${material.material_name}`
      if (material.quantity <= 0) return `Quantity must be > 0 for ${material.material_name}`
      if (material.unit_price <= 0) return `Unit price is required for ${material.material_name}`
    }
    
    // PO Label specific validation
    if (formData.po_type === 'LABEL') {
      if (!formData.week) return 'Week assignment is required for PO Label'
      if (!formData.destination) return 'Destination is required for PO Label'
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
      
      const payload = {
        po_number_ikea: formData.po_number_ikea,
        po_type: formData.po_type,
        order_date: formData.order_date,
        expected_date: formData.expected_date,
        week: formData.week,
        destination: formData.destination,
        mode: formData.mode,
        article_id: formData.article_id,
        article_quantity: formData.article_quantity,
        materials: formData.materials.map(m => ({
          material_code: m.material_code,
          material_name: m.material_name,
          material_type: m.material_type,
          supplier_id: m.supplier_id,
          description: m.description,
          quantity: m.quantity,
          uom: m.uom,
          unit_price: m.unit_price
        }))
      }

      await apiClient.post('/purchasing/purchase-orders', payload)
      
      addNotification({ 
        type: 'success', 
        message: `Purchase Order created successfully (${formData.mode} mode)` 
      })
      onSuccess()
      onClose()
    } catch (error: any) {
      console.error('Failed to create PO:', error)
      addNotification({ 
        type: 'error', 
        message: error.response?.data?.detail || 'Failed to create Purchase Order' 
      })
    } finally {
      setSubmitting(false)
    }
  }

  const totalPOValue = formData.materials.reduce((sum, m) => sum + (m.quantity * m.unit_price), 0)

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl shadow-2xl max-w-6xl w-full max-h-[95vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="bg-gradient-to-r from-blue-600 to-indigo-700 text-white px-6 py-4 flex justify-between items-center">
          <div>
            <h2 className="text-2xl font-bold">Create Purchase Order</h2>
            <p className="text-sm text-blue-100 mt-1">
              {mode === 'AUTO_BOM' ? 'AUTO Mode: BOM Explosion' : 'MANUAL Mode: Custom Entry'}
            </p>
          </div>
          <button onClick={onClose} className="text-white hover:bg-white/20 p-2 rounded-lg transition-colors">
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Body */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {/* Header Information */}
          <div className="bg-gray-50 rounded-lg p-5 space-y-4">
            <h3 className="font-semibold text-gray-800 flex items-center gap-2">
              <Package className="w-5 h-5 text-blue-600" />
              Header Information
            </h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  No PO IKEA (ECIS) <span className="text-gray-400">(Optional)</span>
                </label>
                <input
                  type="text"
                  value={formData.po_number_ikea || ''}
                  onChange={(e) => setFormData(prev => ({ ...prev, po_number_ikea: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="e.g. IKEA-2026-001"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  PO Type <span className="text-red-500">*</span>
                </label>
                <select
                  value={formData.po_type}
                  onChange={(e) => setFormData(prev => ({ ...prev, po_type: e.target.value as POType }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="KAIN">KAIN (Fabric)</option>
                  <option value="LABEL">LABEL</option>
                  <option value="ACCESSORIES">ACCESSORIES</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Order Date <span className="text-red-500">*</span>
                </label>
                <input
                  type="date"
                  value={formData.order_date}
                  onChange={(e) => setFormData(prev => ({ ...prev, order_date: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Expected Delivery <span className="text-red-500">*</span>
                </label>
                <input
                  type="date"
                  value={formData.expected_date}
                  onChange={(e) => setFormData(prev => ({ ...prev, expected_date: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>

              {/* PO Label Specific Fields (Lines 822-828) */}
              {formData.po_type === 'LABEL' && (
                <>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Week Assignment <span className="text-red-500">*</span>
                    </label>
                    <input
                      type="text"
                      value={formData.week || ''}
                      onChange={(e) => setFormData(prev => ({ ...prev, week: e.target.value }))}
                      placeholder="e.g. W05, W06"
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                    <p className="text-xs text-gray-500 mt-1">Inherited to MO (locked after approval)</p>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Destination <span className="text-red-500">*</span>
                    </label>
                    <input
                      type="text"
                      value={formData.destination || ''}
                      onChange={(e) => setFormData(prev => ({ ...prev, destination: e.target.value }))}
                      placeholder="e.g. IKEA DC, IKEA Store"
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                    <p className="text-xs text-gray-500 mt-1">Inherited to MO (locked after approval)</p>
                  </div>
                </>
              )}
            </div>
          </div>

          {/* Mode Selection (Lines 640-655) */}
          <div className="bg-white border-2 border-gray-200 rounded-lg p-4">
            <h3 className="font-semibold text-gray-800 mb-3">Input Mode Selection</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <button
                onClick={() => handleModeSwitch('AUTO_BOM')}
                className={`p-4 rounded-lg border-2 transition-all ${
                  mode === 'AUTO_BOM'
                    ? 'border-purple-500 bg-purple-50 shadow-md'
                    : 'border-gray-200 hover:border-purple-300'
                }`}
              >
                <div className="flex items-center gap-3 mb-2">
                  <Bot className={`w-6 h-6 ${mode === 'AUTO_BOM' ? 'text-purple-600' : 'text-gray-400'}`} />
                  <span className="font-semibold text-gray-800">AUTO from ARTICLE</span>
                </div>
                <p className="text-sm text-gray-600">BOM Explosion: 30+ materials auto-generated</p>
                {mode === 'AUTO_BOM' && (
                  <div className="mt-2 px-2 py-1 bg-purple-100 text-purple-700 text-xs font-semibold rounded">
                    SELECTED
                  </div>
                )}
              </button>

              <button
                onClick={() => handleModeSwitch('MANUAL')}
                className={`p-4 rounded-lg border-2 transition-all ${
                  mode === 'MANUAL'
                    ? 'border-blue-500 bg-blue-50 shadow-md'
                    : 'border-gray-200 hover:border-blue-300'
                }`}
              >
                <div className="flex items-center gap-3 mb-2">
                  <Edit3 className={`w-6 h-6 ${mode === 'MANUAL' ? 'text-blue-600' : 'text-gray-400'}`} />
                  <span className="font-semibold text-gray-800">MANUAL INPUT</span>
                </div>
                <p className="text-sm text-gray-600">Add materials one by one (custom orders)</p>
                {mode === 'MANUAL' && (
                  <div className="mt-2 px-2 py-1 bg-blue-100 text-blue-700 text-xs font-semibold rounded">
                    SELECTED
                  </div>
                )}
              </button>
            </div>
          </div>

          {/* AUTO MODE: Article Selection & BOM Explosion (Lines 656-720) */}
          {mode === 'AUTO_BOM' && (
            <div className="bg-purple-50 border-2 border-purple-200 rounded-lg p-5 space-y-4">
              <h3 className="font-semibold text-purple-800 flex items-center gap-2">
                <Bot className="w-5 h-5" />
                Article Selection (BOM Explosion Trigger)
              </h3>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="md:col-span-2">
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    No/Kode Article <span className="text-red-500">*</span>
                  </label>
                  <select
                    value={formData.article_id || ''}
                    onChange={(e) => {
                      const articleId = parseInt(e.target.value)
                      const article = articles.find(a => a.id === articleId)
                      setFormData(prev => ({ 
                        ...prev, 
                        article_id: articleId,
                      }))
                    }}
                    disabled={loadingArticles}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  >
                    <option value="">Select Article...</option>
                    {articles.map(article => (
                      <option key={article.id} value={article.id}>
                        {article.code} - {article.name} {article.bom_available ? '[BOM Available]' : '[No BOM]'}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Qty Article (pcs) <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="number"
                    min="1"
                    value={formData.article_quantity || ''}
                    onChange={(e) => setFormData(prev => ({ ...prev, article_quantity: parseInt(e.target.value) || 0 }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    placeholder="e.g. 1000"
                  />
                </div>
              </div>

              <button
                onClick={() => formData.article_id && handleArticleSelect(formData.article_id)}
                disabled={!formData.article_id || !formData.article_quantity || loadingBOM}
                className="flex items-center gap-2 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {loadingBOM ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    Processing BOM Explosion...
                  </>
                ) : (
                  <>
                    <TrendingUp className="w-5 h-5" />
                    Trigger BOM Explosion
                  </>
                )}
              </button>

              {bomExplosion && (
                <div className="bg-green-50 border border-green-200 rounded-lg p-3">
                  <div className="flex items-center gap-2 text-green-700 font-semibold">
                    <CheckCircle className="w-5 h-5" />
                    BOM Explosion successful! {bomExplosion.materials.length} materials generated
                  </div>
                  <p className="text-sm text-gray-600 mt-1">
                    Silakan cek dan update harga/supplier per material.
                  </p>
                </div>
              )}
            </div>
          )}

          {/* Material List */}
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <h3 className="font-semibold text-gray-800">
                Material List ({formData.materials.length} items)
              </h3>
              {mode === 'MANUAL' && (
                <button
                  onClick={addManualMaterial}
                  className="flex items-center gap-2 px-3 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm"
                >
                  <Plus className="w-4 h-4" />
                  Add Material
                </button>
              )}
            </div>

            {formData.materials.length === 0 ? (
              <div className="text-center py-12 bg-gray-50 rounded-lg border-2 border-dashed border-gray-300">
                <Package className="w-12 h-12 text-gray-400 mx-auto mb-3" />
                <p className="text-gray-600">
                  {mode === 'AUTO_BOM' 
                    ? 'Select an article and trigger BOM explosion to generate materials'
                    : 'Click "Add Material" to start adding materials manually'
                  }
                </p>
              </div>
            ) : (
              <div className="space-y-3">
                {formData.materials.map((material, index) => (
                  <div
                    key={material.id}
                    className={`p-4 rounded-lg border-2 ${
                      material.is_auto_generated
                        ? 'bg-purple-50 border-purple-200'
                        : 'bg-blue-50 border-blue-200'
                    }`}
                  >
                    <div className="flex justify-between items-start mb-3">
                      <div className="flex items-center gap-2">
                        <span className="font-semibold text-gray-700">MATERIAL #{index + 1}</span>
                        {material.is_auto_generated && (
                          <span className="px-2 py-0.5 bg-purple-100 text-purple-700 text-xs font-semibold rounded">
                            Auto-generated from BOM
                          </span>
                        )}
                      </div>
                      {!material.is_auto_generated && (
                        <button
                          onClick={() => removeMaterial(material.id)}
                          className="text-red-600 hover:bg-red-100 p-1 rounded transition-colors"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      )}
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                      <div>
                        <label className="block text-xs font-medium text-gray-600 mb-1">
                          Material Name <span className="text-red-500">*</span>
                        </label>
                        <input
                          type="text"
                          value={material.material_name}
                          onChange={(e) => updateMaterial(material.id, 'material_name', e.target.value)}
                          disabled={material.is_auto_generated}
                          className="w-full px-2 py-1.5 text-sm border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100"
                        />
                      </div>

                      <div>
                        <label className="block text-xs font-medium text-gray-600 mb-1">
                          Material Code
                        </label>
                        <input
                          type="text"
                          value={material.material_code}
                          onChange={(e) => updateMaterial(material.id, 'material_code', e.target.value)}
                          disabled={material.is_auto_generated}
                          className="w-full px-2 py-1.5 text-sm border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100"
                        />
                      </div>

                      <div>
                        <label className="block text-xs font-medium text-gray-600 mb-1">
                          Supplier <span className="text-red-500">*</span>
                        </label>
                        <select
                          value={material.supplier_id || ''}
                          onChange={(e) => updateMaterial(material.id, 'supplier_id', parseInt(e.target.value))}
                          className="w-full px-2 py-1.5 text-sm border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        >
                          <option value="">Select Supplier...</option>
                          {suppliers.map(supplier => (
                            <option key={supplier.id} value={supplier.id}>
                              {supplier.name}
                            </option>
                          ))}
                        </select>
                      </div>

                      <div>
                        <label className="block text-xs font-medium text-gray-600 mb-1">
                          Quantity <span className="text-red-500">*</span>
                        </label>
                        <div className="flex gap-2">
                          <input
                            type="number"
                            step="0.01"
                            value={material.quantity}
                            onChange={(e) => updateMaterial(material.id, 'quantity', parseFloat(e.target.value) || 0)}
                            className="flex-1 px-2 py-1.5 text-sm border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                          />
                          <input
                            type="text"
                            value={material.uom}
                            onChange={(e) => updateMaterial(material.id, 'uom', e.target.value)}
                            disabled={material.is_auto_generated}
                            className="w-20 px-2 py-1.5 text-sm border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100"
                            placeholder="UOM"
                          />
                        </div>
                      </div>

                      <div>
                        <label className="block text-xs font-medium text-gray-600 mb-1">
                          Unit Price (Rp) <span className="text-red-500">*</span>
                        </label>
                        <input
                          type="number"
                          step="0.01"
                          value={material.unit_price}
                          onChange={(e) => updateMaterial(material.id, 'unit_price', parseFloat(e.target.value) || 0)}
                          className="w-full px-2 py-1.5 text-sm border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        />
                      </div>

                      <div>
                        <label className="block text-xs font-medium text-gray-600 mb-1">
                          Total Price
                        </label>
                        <div className="px-2 py-1.5 text-sm bg-gray-100 border border-gray-300 rounded font-semibold text-gray-700">
                          Rp {(material.quantity * material.unit_price).toLocaleString('id-ID')}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Total PO Value */}
          {formData.materials.length > 0 && (
            <div className="bg-gradient-to-r from-emerald-50 to-green-50 border-2 border-emerald-200 rounded-lg p-4">
              <div className="flex justify-between items-center">
                <span className="text-lg font-semibold text-gray-800">TOTAL PO VALUE</span>
                <span className="text-2xl font-bold text-emerald-700">
                  Rp {totalPOValue.toLocaleString('id-ID')}
                </span>
              </div>
              <p className="text-sm text-gray-600 mt-1">
                {formData.materials.length} materials • {mode === 'AUTO_BOM' ? 'AUTO Mode' : 'MANUAL Mode'}
              </p>
            </div>
          )}

          {/* Validation Note */}
          {mode === 'AUTO_BOM' && (
            <div className="bg-amber-50 border border-amber-200 rounded-lg p-4">
              <div className="flex gap-3">
                <AlertCircle className="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" />
                <div className="text-sm text-gray-700">
                  <p className="font-semibold text-amber-800 mb-1">NOTE (AUTO Mode):</p>
                  <ul className="space-y-1 list-disc list-inside">
                    <li>Material names & codes CANNOT be edited (from BOM)</li>
                    <li>You MUST fill: Supplier & Unit Price for each material</li>
                    <li>Quantities are calculated from BOM × Article Qty</li>
                    <li>Each material can have DIFFERENT supplier</li>
                  </ul>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="bg-gray-50 px-6 py-4 border-t border-gray-200 flex justify-between items-center">
          <button
            onClick={onClose}
            className="px-6 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-100 transition-colors"
          >
            Cancel
          </button>
          <div className="flex gap-3">
            <button
              onClick={handleSubmit}
              disabled={submitting || formData.materials.length === 0}
              className="px-8 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2 font-semibold"
            >
              {submitting ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  Submitting...
                </>
              ) : (
                <>
                  <CheckCircle className="w-5 h-5" />
                  Submit PO
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
