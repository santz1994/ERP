import React, { useState } from 'react'
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
 * Enhanced Purchase Order Creation - DUAL MODE SYSTEM
 * 
 * MODE 1: AUTO - BOM Explosion from Article
 * MODE 2: MANUAL - Line by line material entry
 * 
 * Critical Features:
 * - Supplier per material (different suppliers for each material)
 * - Week & Destination inheritance for PO Label
 * - Material Debt tracking
 * - Variance validation
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

export const CreatePOPage: React.FC = () => {
  const navigate = useNavigate()
  const [inputMode, setInputMode] = useState<'AUTO' | 'MANUAL'>('AUTO')
  const [isExploding, setIsExploding] = useState(false)
  const [bomExplosionSuccess, setBomExplosionSuccess] = useState(false)

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

  // BOM Explosion Handler (AUTO Mode)
  const handleBOMExplosion = async () => {
    if (!articleCode || !articleQty) {
      toast.error('Please select article and enter quantity')
      return
    }

    setIsExploding(true)
    try {
      const response = await api.bom.bomExplosion(articleCode, articleQty)
      const explodedMaterials = response.data.materials

      // Replace materials array with BOM explosion result
      replace(
        explodedMaterials.map((material: any) => ({
          material_code: material.code,
          material_name: material.name,
          material_type: material.type,
          quantity: material.qty_required,
          uom: material.uom,
          unit_price: 0, // User must fill
          total_price: 0,
          supplier_id: undefined, // User must select
          is_auto_generated: true,
        }))
      )

      setBomExplosionSuccess(true)
      toast.success(`✅ BOM Explosion successful! ${explodedMaterials.length} materials generated`)
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'BOM Explosion failed')
      setBomExplosionSuccess(false)
    } finally {
      setIsExploding(false)
    }
  }

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
                  <div>
                    <label className="block text-sm font-medium mb-2">
                      Article Code <span className="text-red-500">*</span>
                    </label>
                    <input
                      {...register('article_code')}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md"
                      placeholder="e.g., 40551542"
                    />
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
                    />
                  </div>

                  <div className="flex items-end">
                    <Button
                      type="button"
                      onClick={handleBOMExplosion}
                      variant="secondary"
                      className="w-full"
                      isLoading={isExploding}
                      disabled={!articleCode || !articleQty}
                    >
                      {isExploding ? 'Exploding BOM...' : '🚀 Explode BOM'}
                    </Button>
                  </div>
                </div>

                {bomExplosionSuccess && (
                  <div className="mt-4 p-3 bg-green-50 border border-green-200 rounded-md">
                    <p className="text-green-800 text-sm">
                      ✅ BOM Explosion successful! {fields.length} materials generated.
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
