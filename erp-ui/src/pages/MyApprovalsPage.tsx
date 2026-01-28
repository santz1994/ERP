"""
MyApprovalsPage - Page component showing all pending approvals for current user
Shows list of items waiting for approval with filters and action buttons
"""

import React, { useState, useEffect } from 'react';
import { format } from 'date-fns';
import { CheckCircle, XCircle, Clock, Filter } from 'lucide-react';
import ApprovalFlow from '../components/ApprovalFlow';
import ApprovalModal from '../components/ApprovalModal';

interface PendingApproval {
  approval_request_id: string;
  entity_type: string;
  entity_id: string;
  submitted_by: string;
  submitted_at: string;
  reason: string;
  changes: Record<string, any>;
  current_approver_role: string;
  status: string;
}

export const MyApprovalsPage: React.FC = () => {
  const [approvals, setApprovals] = useState<PendingApproval[]>([]);
  const [filteredApprovals, setFilteredApprovals] = useState<PendingApproval[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedApproval, setSelectedApproval] = useState<PendingApproval | null>(null);
  const [showModal, setShowModal] = useState(false);
  const [selectedFilter, setSelectedFilter] = useState<string>('ALL');
  const [actionType, setActionType] = useState<'approve' | 'reject' | null>(null);

  // Fetch pending approvals
  useEffect(() => {
    const fetchApprovals = async () => {
      try {
        setLoading(true);
        const params = new URLSearchParams();
        if (selectedFilter !== 'ALL') {
          params.append('entity_type', selectedFilter);
        }
        params.append('limit', '50');

        const response = await fetch(`/api/v1/approvals/my-pending?${params.toString()}`);
        if (!response.ok) throw new Error('Failed to fetch approvals');

        const data = await response.json();
        setApprovals(data);
        filterApprovals(data, selectedFilter);
      } catch (error) {
        console.error('Error fetching approvals:', error);
        // Show error toast
      } finally {
        setLoading(false);
      }
    };

    fetchApprovals();
  }, [selectedFilter]);

  const filterApprovals = (items: PendingApproval[], filter: string) => {
    if (filter === 'ALL') {
      setFilteredApprovals(items);
    } else {
      setFilteredApprovals(items.filter(a => a.entity_type === filter));
    }
  };

  const handleApproveClick = (approval: PendingApproval) => {
    setSelectedApproval(approval);
    setActionType('approve');
    setShowModal(true);
  };

  const handleRejectClick = (approval: PendingApproval) => {
    setSelectedApproval(approval);
    setActionType('reject');
    setShowModal(true);
  };

  const handleModalClose = () => {
    setShowModal(false);
    setSelectedApproval(null);
    setActionType(null);
  };

  const handleActionSuccess = () => {
    // Refresh approvals after action
    setApprovals(approvals.filter(a => a.approval_request_id !== selectedApproval?.approval_request_id));
    handleModalClose();
  };

  const entityTypeLabels: Record<string, string> = {
    SPK_CREATE: 'Buat SPK',
    SPK_EDIT_QUANTITY: 'Edit Qty SPK',
    SPK_EDIT_DEADLINE: 'Edit Deadline SPK',
    MO_EDIT: 'Edit MO',
    MATERIAL_DEBT: 'Material Debt',
    STOCK_ADJUSTMENT: 'Adjustment Stok',
  };

  const getEntityTypeColor = (entityType: string) => {
    const colors: Record<string, string> = {
      SPK_CREATE: 'bg-blue-100 text-blue-800',
      SPK_EDIT_QUANTITY: 'bg-purple-100 text-purple-800',
      SPK_EDIT_DEADLINE: 'bg-orange-100 text-orange-800',
      MO_EDIT: 'bg-green-100 text-green-800',
      MATERIAL_DEBT: 'bg-red-100 text-red-800',
      STOCK_ADJUSTMENT: 'bg-yellow-100 text-yellow-800',
    };
    return colors[entityType] || 'bg-gray-100 text-gray-800';
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Persetujuan Saya</h1>
          <p className="text-gray-600">
            Total menunggu: <span className="font-semibold">{filteredApprovals.length}</span>
          </p>
        </div>

        {/* Filter Section */}
        <div className="bg-white rounded-lg shadow-md p-4 mb-6">
          <div className="flex items-center gap-2 mb-4">
            <Filter className="w-5 h-5 text-gray-600" />
            <h3 className="font-semibold text-gray-900">Filter</h3>
          </div>
          <div className="flex flex-wrap gap-2">
            {['ALL', 'SPK_CREATE', 'SPK_EDIT_QUANTITY', 'MO_EDIT', 'MATERIAL_DEBT'].map((filter) => (
              <button
                key={filter}
                onClick={() => setSelectedFilter(filter)}
                className={`px-4 py-2 rounded-lg font-medium transition-colors
                  ${selectedFilter === filter
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-200 text-gray-800 hover:bg-gray-300'
                  }
                `}
              >
                {filter === 'ALL' ? 'Semua' : entityTypeLabels[filter] || filter}
              </button>
            ))}
          </div>
        </div>

        {/* Loading State */}
        {loading && (
          <div className="text-center py-12">
            <Clock className="w-12 h-12 text-gray-400 mx-auto mb-4 animate-spin" />
            <p className="text-gray-600">Memuat persetujuan...</p>
          </div>
        )}

        {/* Empty State */}
        {!loading && filteredApprovals.length === 0 && (
          <div className="text-center py-12 bg-white rounded-lg shadow-md">
            <CheckCircle className="w-12 h-12 text-green-500 mx-auto mb-4" />
            <p className="text-gray-600 font-medium">Tidak ada persetujuan menunggu</p>
            <p className="text-gray-500 text-sm">Anda semua siap!</p>
          </div>
        )}

        {/* Approvals List */}
        {!loading && filteredApprovals.length > 0 && (
          <div className="space-y-4">
            {filteredApprovals.map((approval) => (
              <div
                key={approval.approval_request_id}
                className="bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow p-6"
              >
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <div className="flex items-center gap-2 mb-2">
                      <span className={`inline-block px-3 py-1 rounded-full text-xs font-semibold ${getEntityTypeColor(approval.entity_type)}`}>
                        {entityTypeLabels[approval.entity_type] || approval.entity_type}
                      </span>
                      <span className="text-xs text-gray-500">
                        ID: {approval.entity_id.substring(0, 8)}...
                      </span>
                    </div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-1">
                      {entityTypeLabels[approval.entity_type] || approval.entity_type}
                    </h3>
                  </div>
                  <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full bg-yellow-100 text-yellow-800 text-sm font-medium">
                    <Clock className="w-4 h-4" />
                    Menunggu
                  </span>
                </div>

                {/* Submission Info */}
                <div className="mb-4 pb-4 border-b border-gray-200 text-sm text-gray-600">
                  <p>Diajukan: {format(new Date(approval.submitted_at), 'PPpp')}</p>
                  <p className="mt-1">Alasan: {approval.reason}</p>
                  {approval.current_approver_role && (
                    <p className="mt-1 font-medium text-gray-900">
                      Menunggu persetujuan dari: <span className="text-blue-600">{approval.current_approver_role}</span>
                    </p>
                  )}
                </div>

                {/* Changes Preview */}
                {approval.changes && Object.keys(approval.changes).length > 0 && (
                  <div className="mb-4 bg-gray-50 rounded-lg p-3">
                    <p className="text-sm font-semibold text-gray-900 mb-2">Perubahan yang diusulkan:</p>
                    <ul className="text-sm text-gray-600 space-y-1">
                      {Object.entries(approval.changes).map(([key, value]) => (
                        <li key={key}>
                          <strong>{key}:</strong> {JSON.stringify(value)}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Action Buttons */}
                <div className="flex gap-3 justify-end">
                  <button
                    onClick={() => handleRejectClick(approval)}
                    className="px-4 py-2 rounded-lg border-2 border-red-300 text-red-600 font-medium hover:bg-red-50 transition-colors"
                  >
                    <XCircle className="w-4 h-4 inline-block mr-2" />
                    Tolak
                  </button>
                  <button
                    onClick={() => handleApproveClick(approval)}
                    className="px-4 py-2 rounded-lg bg-green-600 text-white font-medium hover:bg-green-700 transition-colors"
                  >
                    <CheckCircle className="w-4 h-4 inline-block mr-2" />
                    Setujui
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Approval Modal */}
      {showModal && selectedApproval && (
        <ApprovalModal
          approval={selectedApproval}
          actionType={actionType}
          onClose={handleModalClose}
          onSuccess={handleActionSuccess}
        />
      )}
    </div>
  );
};

export default MyApprovalsPage;
