/**
 * Copyright (C) 2026 - PT Quty Karunia / Daniel Rizaldy
 * Date Created: 2026-02-04
 * 
 * MANUFACTURING ORDER (MO) MANAGEMENT - DUAL-STAGE SYSTEM
 * 
 * Specification: Rencana Tampilan.md Lines 853-950
 * 
 * **REVOLUTIONARY CONCEPT**: MO dapat dimulai dengan 2 stages untuk reduce lead time
 * 
 * STAGE 1: MO PARTIAL (PO Kain only)
 * - Status:  PARTIAL
 * - Trigger: PO Kain created + approved
 * - Release: Cutting & Embroidery departments ONLY
 * - Hold: Sewing, Finishing, Packing (waiting PO Label)
 * - Benefit: 3-5 days earlier production start (fabric is longest lead time)
 * 
 * STAGE 2: MO RELEASED (PO Label ready)
 * - Status:  RELEASED
 * - Trigger: PO Label created → Auto-upgrade PARTIAL MO
 * - Auto-inherit: Week & Destination from PO Label (locked after approval)
 * - Release: ALL departments unlocked instantly
 * - Audit: System log PARTIAL → RELEASED upgrade timestamp
 * - Notification: Email to PPIC & Production Admin
 * 
 * **KEY FEATURES**:
 * - Dual-stage workflow (PARTIAL → RELEASED)
 * - Department-level release control
 * - Auto-inherit Week/Destination (zero manual entry error)
 * - Progress tracking per department
 * - SPK summary per MO
 */

import React, { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { 
  Package, 
  Plus, 
  Search, 
  Filter, 
  Calendar,
  MapPin,
  CheckCircle,
  Clock,
  Lock,
  AlertCircle,
  Eye,
  Scissors,
  Shirt,
  Paintbrush,
  Package2,
  Box,
  ChevronRight,
  TrendingUp,
  XCircle
} from 'lucide-react'
import { apiClient } from '@/api/client'
import { useUIStore } from '@/stores/uiStore'
import { ManufacturingOrderCreate } from './ManufacturingOrderCreate'
import { ManufacturingOrderDetail } from './ManufacturingOrderDetail'

// MO Status Types
type MOStatus = 
  | 'DRAFT'           // Not yet released (data entry)
  | 'PARTIAL'         // PO Kain ready, Cutting/Embroidery can start (Lines 871-906)
  | 'RELEASED'        // PO Label ready, ALL departments unlocked (Lines 908-950)
  | 'IN_PROGRESS'     // Production ongoing
  | 'COMPLETED'       // All departments finished
  | 'CANCELLED'       // Cancelled

// Department Types
type Department = 'CUTTING' | 'EMBROIDERY' | 'SEWING' | 'FINISHING' | 'PACKING'

// Department Release Status (Lines 890-900)
interface DepartmentStatus {
  department: Department
  status: 'RELEASED' | 'HOLD' | 'IN_PROGRESS' | 'COMPLETED'
  spk_count: number
  target_qty: number
  actual_qty: number
  can_start: boolean  // Based on MO status (PARTIAL = Cutting/Embroidery only, RELEASED = all)
}

// Manufacturing Order Interface
interface ManufacturingOrder {
  id: number
  mo_number: string
  article_id: number
  article_code: string
  article_name: string
  target_qty: number
  status: MOStatus
  
  // PO References (Lines 882-887)
  po_kain_id: number | null
  po_kain_number: string | null
  po_label_id: number | null
  po_label_number: string | null
  
  // Week & Destination (Lines 888-889, 918-919)
  week: string | null              // Inherited from PO Label
  destination: string | null        // Inherited from PO Label
  week_locked: boolean             // Locked after PO Label approval
  destination_locked: boolean      // Locked after PO Label approval
  
  // Department Release Status (Lines 890-900)
  department_statuses: DepartmentStatus[]
  
  // Timestamps
  created_at: string
  upgraded_at: string | null       // When PARTIAL → RELEASED
  completed_at: string | null
}

// Department Icons Mapping
const DEPT_ICONS: Record<Department, React.ElementType> = {
  CUTTING: Scissors,
  EMBROIDERY: Paintbrush,
  SEWING: Shirt,
  FINISHING: Package2,
  PACKING: Box
}

// Status Badge Component
const MOStatusBadge: React.FC<{ status: MOStatus }> = ({ status }) => {
  const statusConfig = {
    DRAFT: { color: 'bg-gray-100 text-gray-700 border-gray-300', icon: AlertCircle, label: 'DRAFT' },
    PARTIAL: { color: 'bg-yellow-100 text-yellow-700 border-yellow-300', icon: Clock, label: 'PARTIAL' },
    RELEASED: { color: 'bg-green-100 text-green-700 border-green-300', icon: CheckCircle, label: 'RELEASED' },
    IN_PROGRESS: { color: 'bg-blue-100 text-blue-700 border-blue-300', icon: TrendingUp, label: 'IN PROGRESS' },
    COMPLETED: { color: 'bg-emerald-100 text-emerald-700 border-emerald-300', icon: CheckCircle, label: 'COMPLETED' },
    CANCELLED: { color: 'bg-red-100 text-red-700 border-red-300', icon: XCircle, label: 'CANCELLED' }
  }

  const config = statusConfig[status]
  const Icon = config.icon

  return (
    <span className={`px-3 py-1 rounded-full text-xs font-semibold border ${config.color} flex items-center gap-1`}>
      <Icon className="w-3 h-3" />
      {config.label}
    </span>
  )
}

// Department Status Badge Component (Lines 890-900)
const DepartmentStatusBadge: React.FC<{ dept: DepartmentStatus; moStatus: MOStatus }> = ({ dept, moStatus }) => {
  const Icon = DEPT_ICONS[dept.department]
  
  // Determine status based on MO status (PARTIAL = only Cutting/Embroidery released)
  let statusDisplay = dept.status
  let colorClass = ''
  let statusText = ''

  if (moStatus === 'PARTIAL' && !['CUTTING', 'EMBROIDERY'].includes(dept.department)) {
    // Sewing, Finishing, Packing HOLD in PARTIAL mode (Lines 895-897)
    colorClass = 'bg-gray-100 text-gray-600 border-gray-300'
    statusText = '[Hold] HOLD'
  } else if (dept.status === 'RELEASED' || dept.can_start) {
    colorClass = 'bg-green-100 text-green-700 border-green-300'
    statusText = 'RELEASED'
  } else if (dept.status === 'IN_PROGRESS') {
    colorClass = 'bg-blue-100 text-blue-700 border-blue-300'
    statusText = `${dept.actual_qty}/${dept.target_qty} pcs`
  } else if (dept.status === 'COMPLETED') {
    colorClass = 'bg-emerald-100 text-emerald-700 border-emerald-300'
    statusText = 'COMPLETED'
  } else {
    colorClass = 'bg-gray-100 text-gray-600 border-gray-300'
    statusText = '[Hold] HOLD'
  }

  return (
    <div className={`flex items-center gap-2 px-3 py-2 rounded-lg border ${colorClass}`}>
      <Icon className="w-4 h-4" />
      <div className="flex-1">
        <div className="text-xs font-semibold">{dept.department}</div>
        <div className="text-xs">{statusText}</div>
      </div>
    </div>
  )
}

// Main Component
export const ManufacturingOrderList: React.FC = () => {
  const { addNotification } = useUIStore()
  
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [selectedMO, setSelectedMO] = useState<ManufacturingOrder | null>(null)
  const [filterStatus, setFilterStatus] = useState<MOStatus | 'ALL'>('ALL')
  const [searchQuery, setSearchQuery] = useState('')

  // Fetch MO List
  const { data: moList = [], isLoading, refetch } = useQuery({
    queryKey: ['manufacturing-orders', filterStatus, searchQuery],
    queryFn: async () => {
      const params: any = {}
      if (filterStatus !== 'ALL') params.status = filterStatus
      if (searchQuery) params.search = searchQuery

      const response = await apiClient.get('/ppic/manufacturing-orders', { params })
      return response.data as ManufacturingOrder[]
    }
  })

  const handleCreateSuccess = () => {
    refetch()
    setShowCreateModal(false)
    addNotification({ type: 'success', message: 'Manufacturing Order created successfully' })
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-800 flex items-center gap-3">
            <Package className="w-8 h-8 text-blue-600" />
            Manufacturing Order Management
          </h1>
          <p className="text-gray-600 mt-1">
            [Launch] Dual-Stage System: PARTIAL (Kain only) → RELEASED (Full production)
          </p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="flex items-center gap-2 px-5 py-2.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors shadow-lg"
        >
          <Plus className="w-5 h-5" />
          Create MO
        </button>
      </div>

      {/* Filters & Search */}
      <div className="bg-white rounded-xl shadow-sm p-4 space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Search */}
          <div className="relative">
            <Search className="w-5 h-5 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search by MO Number, Article Code, Article Name..."
              className="w-full pl-10 pr-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          {/* Status Filter */}
          <div className="relative">
            <Filter className="w-5 h-5 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value as MOStatus | 'ALL')}
              className="w-full pl-10 pr-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="ALL">All Status</option>
              <option value="DRAFT">DRAFT</option>
              <option value="PARTIAL">PARTIAL (PO Kain Only)</option>
              <option value="RELEASED">RELEASED (Full Production)</option>
              <option value="IN_PROGRESS">IN PROGRESS</option>
              <option value="COMPLETED">COMPLETED</option>
              <option value="CANCELLED">CANCELLED</option>
            </select>
          </div>
        </div>
      </div>

      {/* MO Cards */}
      {isLoading ? (
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="text-gray-600 mt-4">Loading Manufacturing Orders...</p>
        </div>
      ) : moList.length === 0 ? (
        <div className="bg-white rounded-xl shadow-sm p-12 text-center">
          <Package className="w-16 h-16 text-gray-300 mx-auto mb-4" />
          <p className="text-gray-600 text-lg">No Manufacturing Orders found</p>
          <p className="text-gray-500 text-sm mt-2">Create your first MO to start production planning</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-4">
          {moList.map((mo) => (
            <div
              key={mo.id}
              className="bg-white rounded-xl shadow-sm hover:shadow-md transition-shadow border border-gray-200"
            >
              {/* Card Header (Lines 871-878) */}
              <div className="p-5 border-b border-gray-200">
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <div className="flex items-center gap-3">
                      <h3 className="text-xl font-bold text-gray-800">{mo.mo_number}</h3>
                      <MOStatusBadge status={mo.status} />
                    </div>
                    <p className="text-gray-600 mt-1">
                      [{mo.article_code}] {mo.article_name}
                    </p>
                    <p className="text-sm text-gray-500 mt-1">
                      Target: <span className="font-semibold">{mo.target_qty} pcs</span>
                    </p>
                  </div>
                  <button
                    onClick={() => setSelectedMO(mo)}
                    className="flex items-center gap-2 px-4 py-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                  >
                    <Eye className="w-4 h-4" />
                    View Details
                    <ChevronRight className="w-4 h-4" />
                  </button>
                </div>
              </div>

              {/* Card Body */}
              <div className="p-5 space-y-4">
                {/* PO References (Lines 882-887) */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="bg-gray-50 rounded-lg p-3">
                    <p className="text-xs text-gray-600 mb-1">PO Kain:</p>
                    {mo.po_kain_number ? (
                      <div className="flex items-center gap-2">
                        <CheckCircle className="w-4 h-4 text-green-600" />
                        <span className="font-semibold text-gray-800">{mo.po_kain_number}</span>
                      </div>
                    ) : (
                      <div className="flex items-center gap-2 text-amber-600">
                        <Clock className="w-4 h-4" />
                        <span className="text-sm">⏳ Waiting...</span>
                      </div>
                    )}
                  </div>

                  <div className="bg-gray-50 rounded-lg p-3">
                    <p className="text-xs text-gray-600 mb-1">PO Label:</p>
                    {mo.po_label_number ? (
                      <div className="flex items-center gap-2">
                        <CheckCircle className="w-4 h-4 text-green-600" />
                        <span className="font-semibold text-gray-800">{mo.po_label_number}</span>
                      </div>
                    ) : (
                      <div className="flex items-center gap-2 text-amber-600">
                        <Clock className="w-4 h-4" />
                        <span className="text-sm">⏳ Waiting...</span>
                      </div>
                    )}
                  </div>
                </div>

                {/* Week & Destination (Lines 888-889, 918-919) */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="flex items-center gap-2">
                    <Calendar className="w-4 h-4 text-gray-500" />
                    <span className="text-sm text-gray-600">Week:</span>
                    {mo.week ? (
                      <span className="font-semibold text-gray-800">
                        {mo.week} {mo.week_locked && ''}
                      </span>
                    ) : (
                      <span className="text-gray-400 text-sm">[Waiting PO Label]</span>
                    )}
                  </div>

                  <div className="flex items-center gap-2">
                    <MapPin className="w-4 h-4 text-gray-500" />
                    <span className="text-sm text-gray-600">Destination:</span>
                    {mo.destination ? (
                      <span className="font-semibold text-gray-800">
                        {mo.destination} {mo.destination_locked && ''}
                      </span>
                    ) : (
                      <span className="text-gray-400 text-sm">[Waiting PO Label]</span>
                    )}
                  </div>
                </div>

                {/* Department Release Status (Lines 890-900) */}
                <div>
                  <h4 className="text-sm font-semibold text-gray-700 mb-2">
                    [Status] Department Release Status:
                  </h4>
                  <div className="grid grid-cols-2 md:grid-cols-5 gap-2">
                    {mo.department_statuses.map((dept) => (
                      <DepartmentStatusBadge 
                        key={dept.department} 
                        dept={dept} 
                        moStatus={mo.status} 
                      />
                    ))}
                  </div>
                </div>

                {/* Status Explanation (Lines 871-906) */}
                {mo.status === 'PARTIAL' && (
                  <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3">
                    <div className="flex items-start gap-2">
                      <AlertCircle className="w-4 h-4 text-yellow-600 mt-0.5" />
                      <div className="text-sm text-gray-700">
                        <p className="font-semibold text-yellow-800 mb-1">
                          PARTIAL Status (PO Kain Ready)
                        </p>
                        <p>
                          • Cutting & Embroidery can start <span className="font-semibold">(3-5 days earlier!)</span><br />
                          • Sewing, Finishing, Packing: HOLD (waiting PO Label)<br />
                          • Week & Destination will auto-inherit when PO Label created
                        </p>
                      </div>
                    </div>
                  </div>
                )}

                {mo.status === 'RELEASED' && mo.upgraded_at && (
                  <div className="bg-green-50 border border-green-200 rounded-lg p-3">
                    <div className="flex items-start gap-2">
                      <CheckCircle className="w-4 h-4 text-green-600 mt-0.5" />
                      <div className="text-sm text-gray-700">
                        <p className="font-semibold text-green-800 mb-1">
                          RELEASED Status (Full Production Ready)
                        </p>
                        <p>
                          • All departments unlocked instantly<br />
                          • Week & Destination auto-inherited from PO Label <br />
                          • Upgraded at: {new Date(mo.upgraded_at).toLocaleString('id-ID')}
                        </p>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Create Modal */}
      {showCreateModal && (
        <ManufacturingOrderCreate 
          onClose={() => setShowCreateModal(false)}
          onSuccess={handleCreateSuccess}
        />
      )}

      {/* Detail Modal */}
      {selectedMO && (
        <ManufacturingOrderDetail
          mo={selectedMO}
          onClose={() => setSelectedMO(null)}
          onUpdate={refetch}
        />
      )}
    </div>
  )
}
