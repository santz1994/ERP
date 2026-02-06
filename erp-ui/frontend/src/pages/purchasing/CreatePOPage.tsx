import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useForm, useFieldArray } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { toast } from 'sonner'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { poSchema, POFormData } from '@/lib/schemas'
import api from '@/api'
import { cn, formatCurrency, formatDate } from '@/lib/utils'

/**
 * Enhanced Purchase Order Creation - DUAL MODE SYSTEM + PO REFERENCE
 * 
 * MODE 1: AUTO - BOM Explosion from Article
 * MODE 2: MANUAL - Line by line material entry
 * 
 * 🆕 PO REFERENCE SYSTEM (Phase 3 - Feb 6, 2026):
 * - PO KAIN (Master) → TRIGGER 1 for early production start
 * - PO LABEL (Child) → TRIGGER 2 for full MO release (auto-inherits article, week, destination)
 * - PO ACCESSORIES → Optional reference to PO KAIN
 * 
 * Critical Features:
 * - Supplier per material (different suppliers for each material)
 * - Week & Destination inheritance for PO Label
 * - Material Debt tracking
 * - Variance validation
 * - 🆕 Reference PO KAIN dropdown (for PO LABEL)
 * - 🆕 Auto-inherited article display (read-only from PO KAIN)
 */

interface POMaterialLine {
  id?: string
  material_code: string
  material_name: string
  material_type: 'RAW' | 'BAHAN_PENOLONG' | 'WIP'
  supplier_id?: number
  supplier_name?: string
  quantity: number
  uom: string
  unit_price: number
  total_price: number
  description?: string
  is_auto_generated?: boolean // Track if from BOM explosion
}

interface AvailablePoKain {
  id: number
  po_number: string
  article_id: number
  article_code: string
  article_name: string
  article_qty: number
  order_date: string
  status: string
  supplier_name: string
}

interface Article {
  id: number
  code: string
  name: string
  description?: string
}

export const CreatePOPage: React.FC = () => {
  const navigate = useNavigate()
  const [inputMode, setInputMode] = useState<'AUTO' | 'MANUAL'>('AUTO')
  const [isExploding, setIsExploding] = useState(false)
  const [bomExplosionSuccess, setBomExplosionSuccess] = useState(false)
  
  // 🆕 PO Reference System State
  const [availablePoKain, setAvailablePoKain] = useState<AvailablePoKain[]>([])
  const [selectedPoKain, setSelectedPoKain] = useState<AvailablePoKain | null>(null)
  const [isLoadingPoKain, setIsLoadingPoKain] = useState(false)
  
  // 🆕 SESSION 49 PHASE 9: Article Dropdown State (Feb 6, 2026)
  const [articles, setArticles] = useState<Article[]>([])
  const [selectedArticle, setSelectedArticle] = useState<Article | null>(null)
  const [isLoadingArticles, setIsLoadingArticles] = useState(false)

  const {
    register,
    control,
    handleSubmit,
    watch,
    setValue,
    formState: { errors, isSubmitting },
  } = useForm<POFormData>({
    resolver: zodResolver(poSchema),
    defaultValues: {
      input_mode: 'AUTO',
      po_type: 'KAIN',
      materials: [],
    },
  })

  const { fields, append, remove, replace } = useFieldArray({
    control,
    name: 'materials',
  })

  const poType = watch('po_type')
  const articleCode = watch('article_code')
  const articleQty = watch('article_qty')
  const sourcePoKainId = watch('source_po_kain_id')

  // 🆕 SESSION 49 PHASE 9: Fetch articles on component mount (Feb 6, 2026)
  useEffect(() => {
    const fetchArticles = async () => {
      setIsLoadingArticles(true)
      try {
        const response = await api.purchasing.getArticles()
        setArticles(response.data || [])
        console.log(`✅ Loaded ${response.data.length} articles for dropdown`)
      } catch (error: any) {
        console.error('❌ Failed to fetch articles:', error)
        toast.error('Failed to load articles')
        setArticles([])
      } finally {
        setIsLoadingArticles(false)
      }
    }

    fetchArticles()
  }, []) // Run once on mount

  // 🆕 Fetch available PO KAIN when PO type changes to LABEL or ACCESSORIES
  useEffect(() => {
    const fetchAvailablePoKain = async () => {
      if (poType === 'LABEL' || poType === 'ACCESSORIES') {
        setIsLoadingPoKain(true)
        try {
          const response = await api.purchasing.getAvailablePoKain()
          setAvailablePoKain(response.data.data || [])
          
          if (response.data.count === 0) {
            toast.warning('⚠️ No active PO KAIN available. Create PO KAIN first.')
          }
        } catch (error: any) {
          toast.error('Failed to fetch available PO KAIN')
          setAvailablePoKain([])
        } finally {
          setIsLoadingPoKain(false)
        }
      } else {
        // Clear PO KAIN selection if switching to KAIN type
        setAvailablePoKain([])
        setSelectedPoKain(null)
        setValue('source_po_kain_id', undefined)
      }
    }

    fetchAvailablePoKain()
  }, [poType, setValue])

  // 🆕 Handle PO KAIN selection (auto-inherit article info)
  const handlePoKainSelection = (poKainId: number) => {
    const selected = availablePoKain.find((pk) => pk.id === poKainId)
    
    if (selected) {
      setSelectedPoKain(selected)
      setValue('source_po_kain_id', selected.id)
      setValue('article_id', selected.article_id)
      setValue('article_code', selected.article_code)
      setValue('article_qty', selected.article_qty)
      
      toast.success(
        `✅ Referenced PO KAIN: ${selected.po_number}\n📦 Article: ${selected.article_code} - ${selected.article_name} (${selected.article_qty} pcs)`
      )
    }
  }

  // 🆕 SESSION 49 PHASE 9: Handle Article Selection + Auto-BOM Explosion (Feb 6, 2026)
  const handleArticleSelection = async (articleId: number) => {
    const selected = articles.find((art) => art.id === articleId)
    
    if (!selected) return
    
    setSelectedArticle(selected)
    setValue('article_id', selected.id)
    setValue('article_code', selected.code)
    
    toast.success(`✅ Selected: ${selected.code} - ${selected.name}`)
    
    // Auto-trigger BOM explosion if quantity is set
    const currentQty = articleQty || 1
    if (currentQty > 0) {
      await handleBOMExplosionWithFilter(selected.id, currentQty)
    }
  }
  
  // 🆕 SESSION 49 PHASE 9: BOM Explosion with Material Type Filter (Feb 6, 2026)
  const handleBOMExplosionWithFilter = async (articleId?: number, quantity?: number) => {
    const targetArticleId = articleId || selectedArticle?.id
    const targetQty = quantity || articleQty
    
    if (!targetArticleId || !targetQty) {
      toast.error('Please select article and enter quantity')
      return
    }

    setIsExploding(true)
    setBomExplosionSuccess(false)
    
    try {
      // Determine material filter based on PO type
      let materialTypeFilter: 'FABRIC' | 'LABEL' | 'ACCESSORIES' | undefined = undefined
      
      if (poType === 'KAIN') {
        materialTypeFilter = 'FABRIC' // Only fabric materials for PO KAIN
      } else if (poType === 'LABEL') {
        materialTypeFilter = 'LABEL' // Only label materials for PO LABEL
      } else if (poType === 'ACCESSORIES') {
        materialTypeFilter = 'ACCESSORIES' // Non-fabric, non-label materials
      }

      const response = await api.purchasing.getBOMMaterials(targetArticleId, {
        quantity: targetQty,
        material_type_filter: materialTypeFilter
      })
      
      const bomData = response.data
      const materials = bomData.materials || []

      if (materials.length === 0) {
        toast.warning(
          `⚠️ No ${materialTypeFilter ? materialTypeFilter.toLowerCase() : ''} materials found in BOM. You can add materials manually.`
        )
        replace([])
      } else {
        // Replace materials array with BOM explosion result
        replace(
          materials.map((material: any) => ({
            material_code: material.material_code,
            material_name: material.material_name,
            material_type: material.material_type,
            quantity: material.total_qty_needed,
            uom: material.uom || 'PCS',
            unit_price: 0, // User must fill
            total_price: 0,
            supplier_id: undefined, // User must select
            description: material.description,
            is_auto_generated: true,
          }))
        )

        setBomExplosionSuccess(true)
        const filterMsg = materialTypeFilter ? ` (filtered: ${materialTypeFilter})` : ''
        toast.success(
          `✅ BOM Explosion successful! ${materials.length} materials generated${filterMsg}`
        )
      }
    } catch (error: any) {
      console.error('❌ BOM Explosion failed:', error)
      toast.error(error.response?.data?.detail || 'BOM Explosion failed')
      setBomExplosionSuccess(false)
      replace([])
    } finally {
      setIsExploding(false)
    }
  }

  // Legacy BOM Explosion Handler (kept for backward compatibility)
  const handleBOMExplosion = async () => {
    await handleBOMExplosionWithFilter()
  }
  
  // 🆕 Trigger BOM explosion when article quantity changes (if article already selected)
  useEffect(() => {
    if (selectedArticle && articleQty && articleQty > 0 && inputMode === 'AUTO') {
      const timer = setTimeout(() => {
        handleBOMExplosionWithFilter(selectedArticle.id, articleQty)
      }, 500) // Debounce 500ms
      
      return () => clearTimeout(timer)
    }
  }, [articleQty]) // React to quantity changes

  // Calculate total price for each line
  const calculateLineTotal = (index: number) => {
    const material = fields[index]
    const total = material.quantity * material.unit_price
    setValue(`materials.${index}.total_price`, total)
  }

  // Toggle between AUTO and MANUAL mode
  const switchMode = (mode: 'AUTO' | 'MANUAL') => {
    if (fields.length > 0) {
      const confirmed = window.confirm(
        'Switching mode will clear all materials. Continue?'
      )
      if (!confirmed) return
    }

    setInputMode(mode)
    setValue('input_mode', mode)
    replace([])
    setBomExplosionSuccess(false)
  }

  // Add empty material line (MANUAL mode)
  const addMaterialLine = () => {
    append({
      material_code: '',
      material_name: '',
      material_type: 'RAW',
      quantity: 0,
      uom: 'PCS',
      unit_price: 0,
      total_price: 0,
      is_auto_generated: false,
    })
  }

  // Submit PO
  const onSubmit = async (data: POFormData) => {
    // Validation
    if (data.materials.length === 0) {
      toast.error('Please add at least one material')
      return
    }

    // Check if all materials have supplier and price
    const missingData = data.materials.some(
      (m) => !m.supplier_id || m.unit_price <= 0
    )
    if (missingData) {
      toast.error('All materials must have supplier and unit price')
      return
    }

    try {
      const response = await api.purchasing.createPO(data)
      toast.success('✅ Purchase Order created successfully!')
      navigate(`/purchasing/po/${response.data.id}`)
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to create PO')
    }
  }

  // Calculate grand total
  const grandTotal = fields.reduce((sum, field) => sum + (field.total_price || 0), 0)

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">
          Create Purchase Order - {poType}
        </h1>
        <p className="text-gray-500 mt-1">
          Dual-Mode PO Creation System: AUTO (BOM Explosion) or MANUAL (Line Entry)
        </p>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
        {/* PO Header Information */}
        <Card>
          <CardHeader>
            <CardTitle>📋 Header Information</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* PO IKEA Number */}
              <div>
                <label className="block text-sm font-medium mb-2">
                  No PO IKEA (ECIS) <span className="text-gray-500">(Optional)</span>
                </label>
                <input
                  {...register('po_ikea_number')}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
                  placeholder="e.g., ECIS-2026-001234"
                />
              </div>

              {/* PO Type */}
              <div>
                <label className="block text-sm font-medium mb-2">
                  PO Type <span className="text-red-500">*</span>
                </label>
                <select
                  {...register('po_type')}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
                >
                  <option value="KAIN">KAIN (Fabric) - TRIGGER 1 🔑</option>
                  <option value="LABEL">LABEL - TRIGGER 2 🔑</option>
                  <option value="ACCESSORIES">ACCESSORIES</option>
                </select>
                {poType === 'KAIN' && (
                  <p className="text-xs text-blue-600 mt-1">
                    🔑 TRIGGER 1: Enables Cutting & Embroidery (MO PARTIAL)
                  </p>
                )}
                {poType === 'LABEL' && (
                  <p className="text-xs text-purple-600 mt-1">
                    🔑 TRIGGER 2: Full MO Release + Week/Destination inherited
                  </p>
                )}
              </div>

              {/* 🆕 Reference PO KAIN (PO Label & Accessories) */}
              {(poType === 'LABEL' || poType === 'ACCESSORIES') && (
                <div className="md:col-span-2">
                  <label className="block text-sm font-medium mb-2">
                    Reference PO KAIN {poType === 'LABEL' && <span className="text-red-500">*</span>}
                    {poType === 'ACCESSORIES' && <span className="text-gray-500">(Optional)</span>}
                    <span className={`ml-2 text-xs ${poType === 'LABEL' ? 'text-purple-600' : 'text-green-600'}`}>
                      {poType === 'LABEL' ? '(Parent-child relationship - MANDATORY)' : '(Optional reference for tracking)'}
                    </span>
                  </label>
                  <select
                    value={sourcePoKainId || ''}
                    onChange={(e) => handlePoKainSelection(Number(e.target.value))}
                    className="w-full px-3 py-2 border border-purple-300 rounded-md focus:ring-2 focus:ring-purple-500 bg-purple-50"
                    disabled={isLoadingPoKain}
                  >
                    <option value="">
                      {isLoadingPoKain
                        ? 'Loading PO KAIN...'
                        : availablePoKain.length === 0
                        ? 'No active PO KAIN available'
                        : '-- Select PO KAIN --'}
                    </option>
                    {availablePoKain.map((pk) => (
                      <option key={pk.id} value={pk.id}>
                        {pk.po_number} | {pk.article_code} - {pk.article_name} ({pk.article_qty} pcs) | {pk.supplier_name} | Status: {pk.status}
                      </option>
                    ))}
                  </select>
                  {errors.source_po_kain_id && (
                    <p className="text-red-500 text-xs mt-1">
                      {errors.source_po_kain_id.message}
                    </p>
                  )}
                  
                  {/* 🆕 Auto-Inherited Article Display */}
                  {selectedPoKain && (
                    <div className="mt-3 p-3 bg-purple-50 border border-purple-200 rounded-md">
                      <p className="text-xs font-semibold text-purple-700 mb-2">
                        ✅ Auto-Inherited from PO KAIN:
                      </p>
                      <div className="grid grid-cols-3 gap-2 text-xs">
                        <div>
                          <span className="text-gray-600">Article Code:</span>
                          <p className="font-mono font-bold">{selectedPoKain.article_code}</p>
                        </div>
                        <div>
                          <span className="text-gray-600">Article Name:</span>
                          <p className="font-semibold">{selectedPoKain.article_name}</p>
                        </div>
                        <div>
                          <span className="text-gray-600">Quantity:</span>
                          <p className="font-bold">{selectedPoKain.article_qty} pcs</p>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* PO Date */}
              <div>
                <label className="block text-sm font-medium mb-2">
                  PO Date <span className="text-red-500">*</span>
                </label>
                <input
                  type="date"
                  {...register('po_date')}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
                  defaultValue={new Date().toISOString().split('T')[0]}
                />
                {errors.po_date && (
                  <p className="text-red-500 text-xs mt-1">{errors.po_date.message}</p>
                )}
              </div>

              {/* Expected Delivery */}
              <div>
                <label className="block text-sm font-medium mb-2">
                  Expected Delivery <span className="text-red-500">*</span>
                </label>
                <input
                  type="date"
                  {...register('expected_delivery_date')}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
                />
                {errors.expected_delivery_date && (
                  <p className="text-red-500 text-xs mt-1">
                    {errors.expected_delivery_date.message}
                  </p>
                )}
              </div>

              {/* Week & Destination (PO Label only) */}
              {poType === 'LABEL' && (
                <>
                  <div>
                    <label className="block text-sm font-medium mb-2">
                      Week Number <span className="text-red-500">*</span>
                      <span className="ml-2 text-purple-600 text-xs">
                        (Auto-inherited to MO)
                      </span>
                    </label>
                    <input
                      {...register('week_number')}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-purple-500"
                      placeholder="e.g., W05-2026"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-2">
                      Destination <span className="text-red-500">*</span>
                      <span className="ml-2 text-purple-600 text-xs">
                        (Auto-inherited to MO)
                      </span>
                    </label>
                    <input
                      {...register('destination')}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-purple-500"
                      placeholder="e.g., IKEA DC Belgium"
                    />
                  </div>
                </>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Input Mode Selection - CRITICAL FEATURE */}
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-center space-x-4 mb-6">
              <button
                type="button"
                onClick={() => switchMode('AUTO')}
                className={cn(
                  'flex-1 p-6 rounded-lg border-2 transition-all',
                  inputMode === 'AUTO'
                    ? 'border-purple-500 bg-purple-50'
                    : 'border-gray-300 bg-white hover:bg-gray-50'
                )}
              >
                <div className="text-center">
                  <span className="text-4xl mb-2 block">🤖</span>
                  <h3 className="font-bold text-lg">AUTO from ARTICLE</h3>
                  <p className="text-sm text-gray-600 mt-1">
                    BOM Explosion - Auto-generate material list
                  </p>
                  {inputMode === 'AUTO' && (
                    <Badge variant="secondary" className="mt-2">
                      SELECTED
                    </Badge>
                  )}
                </div>
              </button>

              <button
                type="button"
                onClick={() => switchMode('MANUAL')}
                className={cn(
                  'flex-1 p-6 rounded-lg border-2 transition-all',
                  inputMode === 'MANUAL'
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-300 bg-white hover:bg-gray-50'
                )}
              >
                <div className="text-center">
                  <span className="text-4xl mb-2 block">✍️</span>
                  <h3 className="font-bold text-lg">MANUAL INPUT</h3>
                  <p className="text-sm text-gray-600 mt-1">
                    Add materials one by one manually
                  </p>
                  {inputMode === 'MANUAL' && (
                    <Badge variant="info" className="mt-2">
                      SELECTED
                    </Badge>
                  )}
                </div>
              </button>
            </div>

            {/* AUTO Mode - Article Selection & BOM Explosion */}
            {inputMode === 'AUTO' && (
              <div className="bg-purple-50 border border-purple-200 rounded-lg p-6">
                <h4 className="font-semibold mb-4 text-purple-900">
                  📦 Article Selection (BOM Explosion Trigger)
                </h4>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="md:col-span-2">
                    <label className="block text-sm font-medium mb-2">
                      Select Article <span className="text-red-500">*</span>
                      <span className="ml-2 text-xs text-purple-600">
                        (🆕 {poType === 'KAIN' ? 'Will show FABRIC materials only' : poType === 'LABEL' ? 'Will show LABEL materials only' : 'Will show all materials'})
                      </span>
                    </label>
                    <select
                      value={selectedArticle?.id || ''}
                      onChange={(e) => handleArticleSelection(Number(e.target.value))}
                      className="w-full px-3 py-2 border border-purple-300 rounded-md focus:ring-2 focus:ring-purple-500 bg-white"
                      disabled={isLoadingArticles}
                    >
                      <option value="">
                        {isLoadingArticles
                          ? 'Loading articles...'
                          : articles.length === 0
                          ? 'No articles available'
                          : '-- Select Article --'}
                      </option>
                      {articles.map((art) => (
                        <option key={art.id} value={art.id}>
                          {art.code} - {art.name}
                        </option>
                      ))}
                    </select>
                    {selectedArticle && (
                      <p className="text-xs text-purple-700 mt-1">
                        ✅ Selected: {selectedArticle.code} - {selectedArticle.name}
                      </p>
                    )}
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-2">
                      Quantity (pcs) <span className="text-red-500">*</span>
                    </label>
                    <input
                      type="number"
                      {...register('article_qty', { valueAsNumber: true })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md"
                      placeholder="e.g., 1000"
                      min="1"
                      onChange={(e) => {
                        // Manually update form value
                        setValue('article_qty', Number(e.target.value))
                      }}
                    />
                  </div>
                </div>

                {isExploding && (
                  <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-md">
                    <p className="text-blue-800 text-sm flex items-center">
                      <span className="animate-spin mr-2">⏳</span>
                      Exploding BOM for {selectedArticle?.code}...
                    </p>
                  </div>
                )}

                {bomExplosionSuccess && (
                  <div className="mt-4 p-3 bg-green-50 border border-green-200 rounded-md">
                    <p className="text-green-800 text-sm">
                      ✅ BOM Explosion successful! {fields.length} materials generated
                      {poType === 'KAIN' && ' (FABRIC only)'}.
                      <br />
                      Please update supplier and unit price for each material below.
                    </p>
                  </div>
                )}
              </div>
            )}

            {/* MANUAL Mode - Add Material Button */}
            {inputMode === 'MANUAL' && (
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <Button
                  type="button"
                  onClick={addMaterialLine}
                  variant="primary"
                  leftIcon={<span>➕</span>}
                >
                  Add Material Line
                </Button>
                <p className="text-sm text-gray-600 mt-2">
                  Click to add materials one by one. You can add as many as needed.
                </p>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Material List */}
        {fields.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle>
                📋 Material List ({fields.length} items)
                {inputMode === 'AUTO' && (
                  <Badge variant="secondary" className="ml-2">
                    🤖 Auto-generated from BOM
                  </Badge>
                )}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {fields.map((field, index) => (
                  <div
                    key={field.id}
                    className={cn(
                      'p-4 border rounded-lg',
                      field.is_auto_generated
                        ? 'bg-purple-50 border-purple-200'
                        : 'bg-blue-50 border-blue-200'
                    )}
                  >
                    <div className="flex items-center justify-between mb-3">
                      <h5 className="font-semibold">
                        Material #{index + 1}
                        {field.is_auto_generated && (
                          <Badge variant="secondary" size="sm" className="ml-2">
                            🤖 Auto
                          </Badge>
                        )}
                      </h5>
                      {inputMode === 'MANUAL' && (
                        <button
                          type="button"
                          onClick={() => remove(index)}
                          className="text-red-600 hover:text-red-800 text-sm"
                        >
                          🗑️ Remove
                        </button>
                      )}
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                      {/* Material Code */}
                      <div>
                        <label className="block text-xs font-medium mb-1">
                          Material Code <span className="text-red-500">*</span>
                        </label>
                        <input
                          {...register(`materials.${index}.material_code`)}
                          className="w-full px-2 py-1 text-sm border rounded"
                          readOnly={field.is_auto_generated}
                          placeholder="e.g., IKHR504"
                        />
                      </div>

                      {/* Material Name */}
                      <div className="md:col-span-2">
                        <label className="block text-xs font-medium mb-1">
                          Material Name <span className="text-red-500">*</span>
                        </label>
                        <input
                          {...register(`materials.${index}.material_name`)}
                          className="w-full px-2 py-1 text-sm border rounded"
                          readOnly={field.is_auto_generated}
                          placeholder="e.g., KOHAIR 7MM D.BROWN"
                        />
                      </div>

                      {/* Material Type */}
                      <div>
                        <label className="block text-xs font-medium mb-1">Type</label>
                        <select
                          {...register(`materials.${index}.material_type`)}
                          className="w-full px-2 py-1 text-sm border rounded"
                          disabled={field.is_auto_generated}
                        >
                          <option value="RAW">RAW</option>
                          <option value="BAHAN_PENOLONG">BAHAN PENOLONG</option>
                          <option value="WIP">WIP</option>
                        </select>
                      </div>

                      {/* Supplier - CRITICAL: Per material supplier */}
                      <div className="md:col-span-2">
                        <label className="block text-xs font-medium mb-1 text-red-600">
                          🏭 Supplier <span className="text-red-500">* (PER MATERIAL)</span>
                        </label>
                        <select
                          {...register(`materials.${index}.supplier_id`, {
                            valueAsNumber: true,
                          })}
                          className="w-full px-2 py-1 text-sm border border-red-300 rounded focus:ring-2 focus:ring-red-500"
                        >
                          <option value="">-- Select Supplier --</option>
                          <option value={1}>PT Supplier A</option>
                          <option value={2}>CV Supplier B</option>
                          <option value={3}>UD Supplier C</option>
                        </select>
                        <p className="text-xs text-gray-600 mt-1">
                          ℹ️ Each material can have different supplier
                        </p>
                      </div>

                      {/* Quantity */}
                      <div>
                        <label className="block text-xs font-medium mb-1">
                          Quantity <span className="text-red-500">*</span>
                        </label>
                        <input
                          type="number"
                          {...register(`materials.${index}.quantity`, {
                            valueAsNumber: true,
                            onChange: () => calculateLineTotal(index),
                          })}
                          className="w-full px-2 py-1 text-sm border rounded"
                          step="0.01"
                          min="0"
                        />
                      </div>

                      {/* UOM */}
                      <div>
                        <label className="block text-xs font-medium mb-1">UOM</label>
                        <select
                          {...register(`materials.${index}.uom`)}
                          className="w-full px-2 py-1 text-sm border rounded"
                          disabled={field.is_auto_generated}
                        >
                          <option value="YD">YARD</option>
                          <option value="METER">METER</option>
                          <option value="KG">KG</option>
                          <option value="PCS">PCS</option>
                          <option value="CM">CM</option>
                        </select>
                      </div>

                      {/* Unit Price */}
                      <div>
                        <label className="block text-xs font-medium mb-1 text-red-600">
                          Unit Price <span className="text-red-500">*</span>
                        </label>
                        <input
                          type="number"
                          {...register(`materials.${index}.unit_price`, {
                            valueAsNumber: true,
                            onChange: () => calculateLineTotal(index),
                          })}
                          className="w-full px-2 py-1 text-sm border border-red-300 rounded focus:ring-2 focus:ring-red-500"
                          step="0.01"
                          min="0"
                          placeholder="0.00"
                        />
                      </div>

                      {/* Total Price */}
                      <div>
                        <label className="block text-xs font-medium mb-1">Total Price</label>
                        <input
                          type="number"
                          {...register(`materials.${index}.total_price`)}
                          className="w-full px-2 py-1 text-sm border rounded bg-gray-100"
                          readOnly
                        />
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              {/* Grand Total */}
              <div className="mt-6 p-4 bg-gray-50 rounded-lg border-2 border-gray-300">
                <div className="flex items-center justify-between">
                  <span className="text-lg font-semibold">💰 Grand Total:</span>
                  <span className="text-2xl font-bold text-blue-600">
                    {formatCurrency(grandTotal)}
                  </span>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Notes */}
        <Card>
          <CardHeader>
            <CardTitle>📝 Notes (Optional)</CardTitle>
          </CardHeader>
          <CardContent>
            <textarea
              {...register('notes')}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
              rows={3}
              placeholder="Additional notes or special instructions..."
            />
          </CardContent>
        </Card>

        {/* Submit Buttons */}
        <div className="flex items-center justify-end space-x-4">
          <Button
            type="button"
            variant="ghost"
            onClick={() => navigate('/purchasing/po')}
          >
            Cancel
          </Button>
          <Button
            type="submit"
            variant="primary"
            isLoading={isSubmitting}
            disabled={fields.length === 0}
          >
            {isSubmitting ? 'Saving...' : '✅ Submit Purchase Order'}
          </Button>
        </div>
      </form>

      {/* Help Text */}
      <Card className="mt-6 bg-blue-50 border-blue-200">
        <CardContent className="pt-6">
          <h4 className="font-semibold text-blue-900 mb-2">ℹ️ How to Use:</h4>
          <ul className="text-sm text-blue-800 space-y-1 list-disc list-inside">
            <li>
              <strong>AUTO Mode:</strong> Select article + qty → Click "Explode BOM" → System
              generates all materials automatically
            </li>
            <li>
              <strong>MANUAL Mode:</strong> Click "Add Material Line" → Fill each material
              manually
            </li>
            <li>
              <strong>Supplier:</strong> Each material can have DIFFERENT supplier (flexibility!)
            </li>
            <li>
              <strong>PO Label:</strong> Week & Destination will auto-inherit to MO (TRIGGER 2
              system)
            </li>
            <li>
              <strong>Validation:</strong> All materials MUST have Supplier + Unit Price filled
            </li>
          </ul>
        </CardContent>
      </Card>
    </div>
  )
}

export default CreatePOPage
