/**
 * Copyright (C) 2026 - PT Quty Karunia / Daniel Rizaldy
 * Date Created: 2026-02-04
 * 
 * MANUFACTURING ORDER - DETAIL VIEW
 * 
 * Specification: Rencana Tampilan.md Lines 853-950
 * 
 * **Features**:
 * - View complete MO details
 * - Department-level status tracking
 * - SPK list per department
 * - Progress monitoring
 * - Manual upgrade from PARTIAL → RELEASED (if PO Label added later)
 */

import React, { useState } from 'react'
import { 
  X, 
  CheckCircle, 
  Clock, 
  Lock,
  Calendar,
  MapPin,
  Package,
  TrendingUp,
  FileText,
  AlertCircle,
  Scissors,
  Paintbrush,
  Shirt,
  Package2,
  Box
} from 'lucide-react'
import { apiClient } from '@/api/client'
import { useUIStore } from '@/stores/uiStore'

type MOStatus = 'DRAFT' | 'PARTIAL' | 'RELEASED' | 'IN_PROGRESS' | 'COMPLETED' | 'CANCELLED'
type Department = 'CUTTING' | 'EMBROIDERY' | 'SEWING' | 'FINISHING' | 'PACKING'

interface DepartmentStatus {
  department: Department
  status: 'RELEASED' | 'HOLD' | 'IN_PROGRESS' | 'COMPLETED'
  spk_count: number
  target_qty: number
  actual_qty: number
  can_start: boolean
}

interface ManufacturingOrder {
  id: number
  mo_number: string
  article_id: number
  article_code: string
  article_name: string
  target_qty: number
  status: MOStatus
  po_kain_id: number | null
  po_kain_number: string | null
  po_label_id: number | null
  po_label_number: string | null
  week: string | null
  destination: string | null
  week_locked: boolean
  destination_locked: boolean
  department_statuses: DepartmentStatus[]
  created_at: string
  upgraded_at: string | null
  completed_at: string | null
  notes?: string
}

interface ManufacturingOrderDetailProps {
  mo: ManufacturingOrder
  onClose: () => void
  onUpdate: () => void
}

const DEPT_ICONS: Record<Department, React.ElementType> = {
  CUTTING: Scissors,
  EMBROIDERY: Paintbrush,
  SEWING: Shirt,
  FINISHING: Package2,
  PACKING: Box
}

export const ManufacturingOrderDetail: React.FC<ManufacturingOrderDetailProps> = ({ mo, onClose, onUpdate }) => {
  const { addNotification } = useUIStore()
  const [upgrading, setUpgrading] = useState(false)

  const handleUpgradeToReleased = async () => {
    if (!confirm('Upgrade this MO to RELEASED status? This will unlock all departments.')) return

    try {
      setUpgrading(true)
      await apiClient.post(`/ppic/manufacturing-orders/${mo.id}/upgrade-to-released`)
      
      addNotification({ 
        type: 'success', 
        message: 'MO upgraded to RELEASED successfully! All departments unlocked.' 
      })
      onUpdate()
      onClose()
    } catch (error: any) {
      addNotification({ 
        type: 'error', 
        message: error.response?.data?.detail || 'Failed to upgrade MO' 
      })
    } finally {
      setUpgrading(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl shadow-2xl max-w-5xl w-full max-h-[95vh] overflow-hidden flex flex-col">
        
        {/* Header */}
        <div className="bg-gradient-to-r from-blue-600 to-indigo-700 text-white px-6 py-4 flex justify-between items-center">
          <div>
            <h2 className="text-2xl font-bold">{mo.mo_number}</h2>
            <p className="text-sm text-blue-100 mt-1">
              [{mo.article_code}] {mo.article_name}
            </p>
          </div>
          <button onClick={onClose} className="text-white hover:bg-white/20 p-2 rounded-lg transition-colors">
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Body */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          
          {/* Status & Basic Info */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Status Badge */}
            <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg p-5 border border-blue-200">
              <p className="text-sm text-gray-600 mb-2">MO Status:</p>
              <div className="flex items-center gap-2">
                {mo.status === 'PARTIAL' && (
                  <span className="px-4 py-2 bg-yellow-100 text-yellow-700 border border-yellow-300 rounded-full text-lg font-semibold">
                    PARTIAL
                  </span>
                )}
                {mo.status === 'RELEASED' && (
                  <span className="px-4 py-2 bg-green-100 text-green-700 border border-green-300 rounded-full text-lg font-semibold">
                    RELEASED
                  </span>
                )}
                {mo.status === 'IN_PROGRESS' && (
                  <span className="px-4 py-2 bg-blue-100 text-blue-700 border border-blue-300 rounded-full text-lg font-semibold">
                    IN PROGRESS
                  </span>
                )}
                {mo.status === 'COMPLETED' && (
                  <span className="px-4 py-2 bg-emerald-100 text-emerald-700 border border-emerald-300 rounded-full text-lg font-semibold">
                    COMPLETED
                  </span>
                )}
              </div>
            </div>

            {/* Target Quantity */}
            <div className="bg-gray-50 rounded-lg p-5 border border-gray-200">
              <p className="text-sm text-gray-600 mb-2">Target Quantity:</p>
              <p className="text-3xl font-bold text-gray-800">{mo.target_qty} <span className="text-lg text-gray-600">pcs</span></p>
            </div>
          </div>

          {/* PO References (Lines 882-887) */}
          <div className="bg-white border-2 border-gray-200 rounded-lg p-5">
            <h3 className="font-semibold text-gray-800 mb-3 flex items-center gap-2">
              <Package className="w-5 h-5 text-blue-600" />
              Purchase Order References
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="bg-gray-50 rounded-lg p-4">
                <p className="text-xs text-gray-600 mb-2">PO Kain:</p>
                {mo.po_kain_number ? (
                  <div className="flex items-center gap-2">
                    <CheckCircle className="w-5 h-5 text-green-600" />
                    <span className="font-semibold text-gray-800">{mo.po_kain_number}</span>
                  </div>
                ) : (
                  <div className="flex items-center gap-2 text-amber-600">
                    <Clock className="w-5 h-5" />
                    <span>⏳ Waiting...</span>
                  </div>
                )}
              </div>

              <div className="bg-gray-50 rounded-lg p-4">
                <p className="text-xs text-gray-600 mb-2">PO Label:</p>
                {mo.po_label_number ? (
                  <div className="flex items-center gap-2">
                    <CheckCircle className="w-5 h-5 text-green-600" />
                    <span className="font-semibold text-gray-800">{mo.po_label_number}</span>
                  </div>
                ) : (
                  <div className="flex items-center gap-2 text-amber-600">
                    <Clock className="w-5 h-5" />
                    <span>⏳ Waiting...</span>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Week & Destination (Lines 888-889, 918-919) */}
          <div className="bg-white border-2 border-gray-200 rounded-lg p-5">
            <h3 className="font-semibold text-gray-800 mb-3">Shipping Information</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="flex items-center gap-3 bg-gray-50 rounded-lg p-4">
                <Calendar className="w-6 h-6 text-blue-600" />
                <div className="flex-1">
                  <p className="text-xs text-gray-600">Week Assignment:</p>
                  {mo.week ? (
                    <p className="font-semibold text-gray-800 flex items-center gap-2">
                      {mo.week} 
                      {mo.week_locked && <Lock className="w-4 h-4 text-gray-500" />}
                    </p>
                  ) : (
                    <p className="text-gray-400">[Waiting PO Label]</p>
                  )}
                </div>
              </div>

              <div className="flex items-center gap-3 bg-gray-50 rounded-lg p-4">
                <MapPin className="w-6 h-6 text-blue-600" />
                <div className="flex-1">
                  <p className="text-xs text-gray-600">Destination:</p>
                  {mo.destination ? (
                    <p className="font-semibold text-gray-800 flex items-center gap-2">
                      {mo.destination} 
                      {mo.destination_locked && <Lock className="w-4 h-4 text-gray-500" />}
                    </p>
                  ) : (
                    <p className="text-gray-400">[Waiting PO Label]</p>
                  )}
                </div>
              </div>
            </div>
            
            {mo.week_locked && mo.destination_locked && (
              <div className="mt-3 bg-blue-50 border border-blue-200 rounded-lg p-3 text-sm text-gray-700">
                <AlertCircle className="w-4 h-4 text-blue-600 inline mr-2" />
                Week & Destination are locked (auto-inherited from PO Label). Cannot be edited.
              </div>
            )}
          </div>

          {/* Department Release Status (Lines 890-900) */}
          <div className="bg-white border-2 border-gray-200 rounded-lg p-5">
            <h3 className="font-semibold text-gray-800 mb-4 flex items-center gap-2">
              <TrendingUp className="w-5 h-5 text-blue-600" />
              [Status] Department Release Status
            </h3>

            <div className="space-y-3">
              {mo.department_statuses.map((dept) => {
                const Icon = DEPT_ICONS[dept.department]
                const isHold = mo.status === 'PARTIAL' && !['CUTTING', 'EMBROIDERY'].includes(dept.department)

                return (
                  <div
                    key={dept.department}
                    className={`flex items-center justify-between p-4 rounded-lg border-2 ${
                      isHold 
                        ? 'bg-gray-50 border-gray-300' 
                        : dept.status === 'COMPLETED'
                        ? 'bg-emerald-50 border-emerald-300'
                        : dept.status === 'IN_PROGRESS'
                        ? 'bg-blue-50 border-blue-300'
                        : dept.can_start
                        ? 'bg-green-50 border-green-300'
                        : 'bg-gray-50 border-gray-300'
                    }`}
                  >
                    <div className="flex items-center gap-3">
                      <Icon className={`w-6 h-6 ${isHold ? 'text-gray-400' : 'text-blue-600'}`} />
                      <div>
                        <p className="font-semibold text-gray-800">{dept.department}</p>
                        <p className="text-sm text-gray-600">
                          {dept.spk_count > 0 ? `${dept.spk_count} SPK Active` : 'No SPK'}
                        </p>
                      </div>
                    </div>

                    <div className="text-right">
                      {isHold ? (
                        <span className="px-3 py-1 bg-gray-200 text-gray-600 rounded-full text-sm font-semibold flex items-center gap-1">
                          <Lock className="w-3 h-3" />
                          HOLD
                        </span>
                      ) : dept.status === 'COMPLETED' ? (
                        <span className="px-3 py-1 bg-emerald-200 text-emerald-700 rounded-full text-sm font-semibold flex items-center gap-1">
                          <CheckCircle className="w-3 h-3" />
                          COMPLETED
                        </span>
                      ) : dept.status === 'IN_PROGRESS' ? (
                        <div>
                          <span className="px-3 py-1 bg-blue-200 text-blue-700 rounded-full text-sm font-semibold">
                            {dept.actual_qty}/{dept.target_qty} pcs
                          </span>
                          <p className="text-xs text-gray-600 mt-1">In Progress</p>
                        </div>
                      ) : dept.can_start ? (
                        <span className="px-3 py-1 bg-green-200 text-green-700 rounded-full text-sm font-semibold flex items-center gap-1">
                          <CheckCircle className="w-3 h-3" />
                          RELEASED
                        </span>
                      ) : (
                        <span className="px-3 py-1 bg-gray-200 text-gray-600 rounded-full text-sm font-semibold">
                          Pending
                        </span>
                      )}
                    </div>
                  </div>
                )
              })}
            </div>
          </div>

          {/* Status Explanation */}
          {mo.status === 'PARTIAL' && (
            <div className="bg-yellow-50 border-2 border-yellow-200 rounded-lg p-5">
              <div className="flex items-start gap-3">
                <AlertCircle className="w-6 h-6 text-yellow-600 flex-shrink-0 mt-0.5" />
                <div>
                  <h4 className="font-semibold text-yellow-800 mb-2">PARTIAL Status Explanation (Lines 871-906)</h4>
                  <ul className="space-y-1 text-sm text-gray-700">
                    <li>• PO Kain is ready</li>
                    <li>• Cutting & Embroidery can start production <span className="font-semibold text-yellow-800">(3-5 days earlier!)</span></li>
                    <li>• Sewing, Finishing, Packing are HOLD (waiting for PO Label)</li>
                    <li>• Week & Destination will auto-inherit when PO Label is created</li>
                    <li>• MO will auto-upgrade to RELEASED when PO Label is linked</li>
                  </ul>
                </div>
              </div>
            </div>
          )}

          {mo.status === 'RELEASED' && mo.upgraded_at && (
            <div className="bg-green-50 border-2 border-green-200 rounded-lg p-5">
              <div className="flex items-start gap-3">
                <CheckCircle className="w-6 h-6 text-green-600 flex-shrink-0 mt-0.5" />
                <div>
                  <h4 className="font-semibold text-green-800 mb-2">RELEASED Status (Full Production Ready)</h4>
                  <ul className="space-y-1 text-sm text-gray-700">
                    <li>• All departments are now RELEASED</li>
                    <li>• Week & Destination auto-inherited from PO Label</li>
                    <li>• Full production can proceed without delays</li>
                    <li>• Upgraded at: <span className="font-semibold">{new Date(mo.upgraded_at).toLocaleString('id-ID')}</span></li>
                  </ul>
                </div>
              </div>
            </div>
          )}

          {/* Notes */}
          {mo.notes && (
            <div className="bg-white border-2 border-gray-200 rounded-lg p-5">
              <h3 className="font-semibold text-gray-800 mb-2 flex items-center gap-2">
                <FileText className="w-5 h-5 text-blue-600" />
                Notes
              </h3>
              <p className="text-gray-700 text-sm whitespace-pre-wrap">{mo.notes}</p>
            </div>
          )}

          {/* Manual Upgrade Button (if PARTIAL and no PO Label) */}
          {mo.status === 'PARTIAL' && !mo.po_label_id && (
            <div className="bg-blue-50 border-2 border-blue-200 rounded-lg p-5">
              <h4 className="font-semibold text-blue-800 mb-2">Manual Upgrade to RELEASED</h4>
              <p className="text-sm text-gray-700 mb-3">
                If PO Label has been created but not linked, you can manually upgrade this MO to RELEASED status.
                This will unlock all departments (Sewing, Finishing, Packing).
              </p>
              <button
                onClick={handleUpgradeToReleased}
                disabled={upgrading}
                className="flex items-center gap-2 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors"
              >
                {upgrading ? 'Upgrading...' : 'Upgrade to RELEASED'}
              </button>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="bg-gray-50 px-6 py-4 border-t border-gray-200 flex justify-end">
          <button 
            onClick={onClose} 
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  )
}
