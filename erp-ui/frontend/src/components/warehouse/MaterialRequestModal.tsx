/**
 * Material Request Modal Component
 * Handles creation of manual material requests in the warehouse
 * Supports workflow: PENDING → APPROVED → COMPLETED
 */

import React, { useState } from 'react'
import { AlertCircle, Package, MapPin, CheckCircle, X } from 'lucide-react'
import { useUIStore } from '@/store'

export interface MaterialRequestModalProps {
  isOpen: boolean
  onClose: () => void
  onSubmit: (data: MaterialRequestFormData) => Promise<void>
  loading?: boolean
  error?: string | null
}

export interface MaterialRequestFormData {
  product_id: number
  location_id: number
  qty_requested: number
  uom: 'Pcs' | 'Meter' | 'Kg' | 'Roll' | 'Box' | 'Dozen'
  purpose: string
}

export const MaterialRequestModal: React.FC<MaterialRequestModalProps> = ({
  isOpen,
  onClose,
  onSubmit,
  loading = false,
  error = null,
}) => {
  const { addNotification } = useUIStore()
  
  const [formData, setFormData] = useState<MaterialRequestFormData>({
    product_id: 0,
    location_id: 0,
    qty_requested: 0,
    uom: 'Pcs',
    purpose: '',
  })

  const [validationErrors, setValidationErrors] = useState<Record<string, string>>({})

  if (!isOpen) return null

  const validateForm = (): boolean => {
    const errors: Record<string, string> = {}

    if (!formData.product_id || formData.product_id === 0) {
      errors.product_id = 'Product is required'
    }

    if (!formData.location_id || formData.location_id === 0) {
      errors.location_id = 'Location is required'
    }

    if (!formData.qty_requested || formData.qty_requested <= 0) {
      errors.qty_requested = 'Quantity must be greater than 0'
    }

    if (!formData.purpose || formData.purpose.trim().length === 0) {
      errors.purpose = 'Purpose is required'
    }

    if (formData.purpose.length > 500) {
      errors.purpose = 'Purpose cannot exceed 500 characters'
    }

    setValidationErrors(errors)
    return Object.keys(errors).length === 0
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!validateForm()) {
      addNotification('error', 'Please fix the errors below')
      return
    }

    try {
      await onSubmit(formData)
      setFormData({
        product_id: 0,
        location_id: 0,
        qty_requested: 0,
        uom: 'Pcs',
        purpose: '',
      })
      setValidationErrors({})
      onClose()
    } catch (err) {
      console.error('Failed to submit material request:', err)
    }
  }

  const handleClose = () => {
    setFormData({
      product_id: 0,
      location_id: 0,
      qty_requested: 0,
      uom: 'Pcs',
      purpose: '',
    })
    setValidationErrors({})
    onClose()
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-[9999]">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div className="flex items-center gap-2">
            <Package className="w-5 h-5 text-blue-600" />
            <h2 className="text-lg font-bold text-gray-900">Request Material</h2>
          </div>
          <button
            onClick={handleClose}
            className="text-gray-400 hover:text-gray-600"
            disabled={loading}
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Error Alert */}
        {error && (
          <div className="mx-6 mt-4 p-4 bg-red-50 border border-red-200 rounded-lg flex gap-3">
            <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
            <div>
              <p className="text-sm font-medium text-red-900">Error</p>
              <p className="text-sm text-red-800">{error}</p>
            </div>
          </div>
        )}

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          {/* Product ID */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Product ID <span className="text-red-500">*</span>
            </label>
            <input
              type="number"
              value={formData.product_id || ''}
              onChange={(e) =>
                setFormData({ ...formData, product_id: parseInt(e.target.value) || 0 })
              }
              className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                validationErrors.product_id ? 'border-red-500' : 'border-gray-300'
              }`}
              placeholder="Enter product ID"
              disabled={loading}
            />
            {validationErrors.product_id && (
              <p className="text-sm text-red-500 mt-1">{validationErrors.product_id}</p>
            )}
          </div>

          {/* Location ID */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              <MapPin className="w-4 h-4 inline mr-1" />
              Location ID <span className="text-red-500">*</span>
            </label>
            <input
              type="number"
              value={formData.location_id || ''}
              onChange={(e) =>
                setFormData({ ...formData, location_id: parseInt(e.target.value) || 0 })
              }
              className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                validationErrors.location_id ? 'border-red-500' : 'border-gray-300'
              }`}
              placeholder="Enter location ID"
              disabled={loading}
            />
            {validationErrors.location_id && (
              <p className="text-sm text-red-500 mt-1">{validationErrors.location_id}</p>
            )}
          </div>

          {/* Quantity */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Quantity <span className="text-red-500">*</span>
            </label>
            <div className="flex gap-2">
              <input
                type="number"
                step="0.01"
                min="0"
                value={formData.qty_requested || ''}
                onChange={(e) =>
                  setFormData({ ...formData, qty_requested: parseFloat(e.target.value) || 0 })
                }
                className={`flex-1 px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                  validationErrors.qty_requested ? 'border-red-500' : 'border-gray-300'
                }`}
                placeholder="0.00"
                disabled={loading}
              />
              <select
                value={formData.uom}
                onChange={(e) =>
                  setFormData({ ...formData, uom: e.target.value as MaterialRequestFormData['uom'] })
                }
                className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white"
                disabled={loading}
              >
                <option value="Pcs">Pcs</option>
                <option value="Meter">Meter</option>
                <option value="Kg">Kg</option>
                <option value="Roll">Roll</option>
                <option value="Box">Box</option>
                <option value="Dozen">Dozen</option>
              </select>
            </div>
            {validationErrors.qty_requested && (
              <p className="text-sm text-red-500 mt-1">{validationErrors.qty_requested}</p>
            )}
          </div>

          {/* Purpose */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Purpose <span className="text-red-500">*</span>
            </label>
            <textarea
              value={formData.purpose}
              onChange={(e) => setFormData({ ...formData, purpose: e.target.value })}
              maxLength={500}
              rows={3}
              className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none ${
                validationErrors.purpose ? 'border-red-500' : 'border-gray-300'
              }`}
              placeholder="Describe why this material is needed..."
              disabled={loading}
            />
            <div className="flex justify-between mt-1">
              <p className="text-xs text-gray-500">
                {validationErrors.purpose && (
                  <span className="text-red-500">{validationErrors.purpose}</span>
                )}
              </p>
              <p className="text-xs text-gray-400">
                {formData.purpose.length}/500
              </p>
            </div>
          </div>

          {/* Info Box */}
          <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg">
            <p className="text-xs text-blue-800">
              <CheckCircle className="w-4 h-4 inline mr-1" />
              Your request will be pending approval from warehouse supervisor.
            </p>
          </div>

          {/* Buttons */}
          <div className="flex gap-3 pt-4">
            <button
              type="button"
              onClick={handleClose}
              className="flex-1 px-4 py-2 text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg font-medium transition-colors disabled:opacity-50"
              disabled={loading}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="flex-1 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors disabled:opacity-50 flex items-center justify-center gap-2"
              disabled={loading}
            >
              {loading ? (
                <>
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  Submitting...
                </>
              ) : (
                <>
                  <CheckCircle className="w-4 h-4" />
                  Submit Request
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default MaterialRequestModal
