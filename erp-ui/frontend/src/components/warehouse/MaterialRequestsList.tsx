/**
 * Material Requests List Component
 * Display and manage material requests with approval workflow
 */

import React, { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { apiClient } from '@/api/client'
import { Clock, CheckCircle, XCircle, AlertCircle, Loader } from 'lucide-react'
import { useUIStore } from '@/store'

export interface MaterialRequest {
  id: number
  product_id: number
  location_id: number
  qty_requested: number
  uom: string
  purpose: string
  status: 'PENDING' | 'APPROVED' | 'REJECTED' | 'COMPLETED'
  requested_by_id: number
  requested_by_name?: string
  approved_by_id?: number | null
  approved_by_name?: string | null
  approved_at?: string | null
  rejection_reason?: string | null
  received_by_id?: number | null
  received_at?: string | null
  requested_at: string
}

export interface MaterialRequestsListProps {
  statusFilter?: 'PENDING' | 'APPROVED' | 'REJECTED' | 'COMPLETED' | 'ALL'
  onApprovalChange?: () => void
}

const statusConfig = {
  PENDING: {
    color: 'bg-yellow-50',
    badge: 'bg-yellow-100 text-yellow-800',
    icon: Clock,
    label: 'Pending Approval',
  },
  APPROVED: {
    color: 'bg-blue-50',
    badge: 'bg-blue-100 text-blue-800',
    icon: CheckCircle,
    label: 'Approved',
  },
  REJECTED: {
    color: 'bg-red-50',
    badge: 'bg-red-100 text-red-800',
    icon: XCircle,
    label: 'Rejected',
  },
  COMPLETED: {
    color: 'bg-green-50',
    badge: 'bg-green-100 text-green-800',
    icon: CheckCircle,
    label: 'Completed',
  },
}

export const MaterialRequestsList: React.FC<MaterialRequestsListProps> = ({
  statusFilter = 'ALL',
  onApprovalChange,
}) => {
  const { addNotification } = useUIStore()
  const [approvingId, setApprovingId] = useState<number | null>(null)
  const [rejectionReason, setRejectionReason] = useState('')
  const [rejectingId, setRejectingId] = useState<number | null>(null)

  const { data: requests, isLoading, refetch } = useQuery({
    queryKey: ['material-requests', statusFilter],
    queryFn: async () => {
      const query = statusFilter !== 'ALL' ? `?status_filter=${statusFilter}` : ''
      const response = await apiClient.get(`/warehouse/material-requests${query}`)
      return response.data as MaterialRequest[]
    },
    refetchInterval: 10000,
  })

  const handleApprove = async (requestId: number) => {
    try {
      setApprovingId(requestId)
      await apiClient.post(`/warehouse/material-requests/${requestId}/approve`, {
        approved: true,
      })
      addNotification('success', 'Material request approved')
      refetch()
      onApprovalChange?.()
    } catch (error) {
      console.error('Failed to approve request:', error)
      addNotification('error', 'Failed to approve request')
    } finally {
      setApprovingId(null)
    }
  }

  const handleReject = async (requestId: number, reason: string) => {
    if (!reason.trim()) {
      addNotification('error', 'Please provide a rejection reason')
      return
    }

    try {
      setRejectingId(requestId)
      await apiClient.post(`/warehouse/material-requests/${requestId}/approve`, {
        approved: false,
        rejection_reason: reason,
      })
      addNotification('success', 'Material request rejected')
      setRejectionReason('')
      refetch()
      onApprovalChange?.()
    } catch (error) {
      console.error('Failed to reject request:', error)
      addNotification('error', 'Failed to reject request')
    } finally {
      setRejectingId(null)
    }
  }

  const handleComplete = async (requestId: number) => {
    try {
      setApprovingId(requestId)
      await apiClient.post(`/warehouse/material-requests/${requestId}/complete`)
      addNotification('success', 'Material request marked as completed')
      refetch()
      onApprovalChange?.()
    } catch (error) {
      console.error('Failed to complete request:', error)
      addNotification('error', 'Failed to complete request')
    } finally {
      setApprovingId(null)
    }
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader className="w-6 h-6 text-blue-600 animate-spin" />
      </div>
    )
  }

  if (!requests || requests.length === 0) {
    return (
      <div className="text-center py-12 bg-gray-50 rounded-lg border border-gray-200">
        <AlertCircle className="w-12 h-12 text-gray-400 mx-auto mb-3" />
        <p className="text-gray-600">No material requests found</p>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {requests.map((request) => {
        const config = statusConfig[request.status]
        const StatusIcon = config.icon

        return (
          <div key={request.id} className={`${config.color} border border-gray-200 rounded-lg p-4`}>
            <div className="flex items-start justify-between mb-3">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-2">
                  <h3 className="font-semibold text-gray-900">
                    Product ID: {request.product_id}
                  </h3>
                  <span className={`px-2 py-1 rounded text-xs font-medium flex items-center gap-1 ${config.badge}`}>
                    <StatusIcon className="w-3 h-3" />
                    {config.label}
                  </span>
                </div>
                <p className="text-sm text-gray-600 mb-2">
                  <strong>Quantity:</strong> {request.qty_requested} {request.uom} at Location {request.location_id}
                </p>
                <p className="text-sm text-gray-600 mb-2">
                  <strong>Purpose:</strong> {request.purpose}
                </p>
                <p className="text-xs text-gray-500">
                  Requested by: {request.requested_by_name || `User ${request.requested_by_id}`} on{' '}
                  {new Date(request.requested_at).toLocaleDateString()}
                </p>
              </div>
            </div>

            {/* Rejection Reason (if rejected) */}
            {request.status === 'REJECTED' && request.rejection_reason && (
              <div className="mb-3 p-2 bg-red-100 border border-red-300 rounded text-sm text-red-800">
                <strong>Rejection Reason:</strong> {request.rejection_reason}
              </div>
            )}

            {/* Actions */}
            {request.status === 'PENDING' && (
              <div className="flex gap-2 pt-3 border-t border-gray-300">
                <button
                  onClick={() => handleApprove(request.id)}
                  disabled={approvingId === request.id}
                  className="flex-1 px-3 py-2 bg-green-600 hover:bg-green-700 text-white rounded text-sm font-medium transition-colors disabled:opacity-50 flex items-center justify-center gap-1"
                >
                  {approvingId === request.id ? (
                    <>
                      <Loader className="w-4 h-4 animate-spin" />
                      Approving...
                    </>
                  ) : (
                    <>
                      <CheckCircle className="w-4 h-4" />
                      Approve
                    </>
                  )}
                </button>
                <div className="flex-1 flex gap-1">
                  <input
                    type="text"
                    placeholder="Reject reason..."
                    value={rejectingId === request.id ? rejectionReason : ''}
                    onChange={(e) => setRejectionReason(e.target.value)}
                    maxLength={100}
                    className="flex-1 px-2 py-2 border border-gray-300 rounded text-sm"
                    disabled={rejectingId !== request.id}
                  />
                  <button
                    onClick={() => handleReject(request.id, rejectionReason)}
                    disabled={rejectingId === request.id}
                    className="px-3 py-2 bg-red-600 hover:bg-red-700 text-white rounded text-sm font-medium transition-colors disabled:opacity-50 flex items-center gap-1"
                  >
                    {rejectingId === request.id ? (
                      <Loader className="w-4 h-4 animate-spin" />
                    ) : (
                      <XCircle className="w-4 h-4" />
                    )}
                  </button>
                </div>
              </div>
            )}

            {/* Complete Action (if approved) */}
            {request.status === 'APPROVED' && (
              <div className="pt-3 border-t border-gray-300">
                <button
                  onClick={() => handleComplete(request.id)}
                  disabled={approvingId === request.id}
                  className="w-full px-3 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded text-sm font-medium transition-colors disabled:opacity-50 flex items-center justify-center gap-1"
                >
                  {approvingId === request.id ? (
                    <>
                      <Loader className="w-4 h-4 animate-spin" />
                      Completing...
                    </>
                  ) : (
                    <>
                      <CheckCircle className="w-4 h-4" />
                      Mark as Received
                    </>
                  )}
                </button>
              </div>
            )}

            {/* Completion Info (if completed) */}
            {request.status === 'COMPLETED' && request.received_at && (
              <p className="text-xs text-gray-500 pt-3 border-t border-gray-300">
                Received by: {request.received_by_name || `User ${request.received_by_id}`} on{' '}
                {new Date(request.received_at).toLocaleDateString()}
              </p>
            )}
          </div>
        )
      })}
    </div>
  )
}

export default MaterialRequestsList
