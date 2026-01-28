"""
ApprovalModal - Modal for approving or rejecting requests
Shows request details and captures approver notes/reason
"""

import React, { useState } from 'react';
import { X, CheckCircle, XCircle, Loader } from 'lucide-react';

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

interface ApprovalModalProps {
  approval: PendingApproval;
  actionType: 'approve' | 'reject' | null;
  onClose: () => void;
  onSuccess: () => void;
}

export const ApprovalModal: React.FC<ApprovalModalProps> = ({
  approval,
  actionType,
  onClose,
  onSuccess,
}) => {
  const [notes, setNotes] = useState('');
  const [reason, setReason] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async () => {
    try {
      setLoading(true);
      setError(null);

      const url = actionType === 'approve'
        ? `/api/v1/approvals/${approval.approval_request_id}/approve`
        : `/api/v1/approvals/${approval.approval_request_id}/reject`;

      const payload = actionType === 'approve'
        ? { notes }
        : { reason };

      const response = await fetch(url, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || `Failed to ${actionType} approval`);
      }

      // Show success message
      alert(
        actionType === 'approve'
          ? 'Approval submitted successfully'
          : 'Request rejected successfully'
      );

      onSuccess();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const isFormValid = actionType === 'approve' ? true : reason.trim().length > 0;

  return (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black bg-opacity-50 z-40 transition-opacity"
        onClick={onClose}
      />

      {/* Modal */}
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
        <div className="bg-white rounded-lg shadow-xl max-w-lg w-full max-h-[90vh] overflow-y-auto">
          {/* Header */}
          <div className={`sticky top-0 flex items-center justify-between p-6 border-b
            ${actionType === 'approve' ? 'bg-green-50 border-green-200' : 'bg-red-50 border-red-200'}
          `}>
            <div className="flex items-center gap-3">
              {actionType === 'approve' ? (
                <CheckCircle className="w-6 h-6 text-green-600" />
              ) : (
                <XCircle className="w-6 h-6 text-red-600" />
              )}
              <h2 className={`text-xl font-bold
                ${actionType === 'approve' ? 'text-green-900' : 'text-red-900'}
              `}>
                {actionType === 'approve' ? 'Setujui Permintaan' : 'Tolak Permintaan'}
              </h2>
            </div>
            <button
              onClick={onClose}
              className="p-1 hover:bg-gray-200 rounded-lg transition-colors"
              disabled={loading}
            >
              <X className="w-6 h-6" />
            </button>
          </div>

          {/* Content */}
          <div className="p-6 space-y-6">
            {/* Request Details */}
            <div className="bg-gray-50 rounded-lg p-4 space-y-3">
              <div>
                <p className="text-sm text-gray-600">Tipe Request</p>
                <p className="font-semibold text-gray-900">{approval.entity_type}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">ID Entity</p>
                <p className="font-mono text-sm text-gray-900">{approval.entity_id}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Alasan Perubahan</p>
                <p className="text-gray-900">{approval.reason}</p>
              </div>

              {/* Changes */}
              {approval.changes && Object.keys(approval.changes).length > 0 && (
                <div>
                  <p className="text-sm text-gray-600 mb-2">Perubahan yang Diusulkan</p>
                  <div className="bg-white rounded p-2 border border-gray-200">
                    {Object.entries(approval.changes).map(([key, value]) => (
                      <div key={key} className="flex justify-between text-sm py-1 border-b border-gray-100 last:border-0">
                        <span className="text-gray-700 font-medium">{key}:</span>
                        <span className="text-gray-900">{JSON.stringify(value)}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Error Message */}
            {error && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                <p className="text-sm text-red-800">{error}</p>
              </div>
            )}

            {/* Action-Specific Content */}
            {actionType === 'approve' ? (
              <div>
                <label className="block text-sm font-medium text-gray-900 mb-2">
                  Catatan Persetujuan (Opsional)
                </label>
                <textarea
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  placeholder="Tambahkan catatan untuk submitter..."
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent resize-none"
                  rows={4}
                  disabled={loading}
                />
              </div>
            ) : (
              <div>
                <label className="block text-sm font-medium text-gray-900 mb-2">
                  Alasan Penolakan <span className="text-red-500">*</span>
                </label>
                <textarea
                  value={reason}
                  onChange={(e) => setReason(e.target.value)}
                  placeholder="Jelaskan mengapa Anda menolak permintaan ini..."
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent resize-none"
                  rows={4}
                  disabled={loading}
                />
              </div>
            )}
          </div>

          {/* Footer */}
          <div className="sticky bottom-0 flex gap-3 p-6 border-t bg-gray-50">
            <button
              onClick={onClose}
              className="flex-1 px-4 py-2 rounded-lg border-2 border-gray-300 text-gray-900 font-medium hover:bg-gray-100 transition-colors disabled:opacity-50"
              disabled={loading}
            >
              Batal
            </button>
            <button
              onClick={handleSubmit}
              disabled={loading || !isFormValid}
              className={`flex-1 px-4 py-2 rounded-lg text-white font-medium transition-colors flex items-center justify-center gap-2 disabled:opacity-50
                ${actionType === 'approve'
                  ? 'bg-green-600 hover:bg-green-700'
                  : 'bg-red-600 hover:bg-red-700'
                }
              `}
            >
              {loading && <Loader className="w-4 h-4 animate-spin" />}
              {actionType === 'approve' ? 'Setujui' : 'Tolak'}
            </button>
          </div>
        </div>
      </div>
    </>
  );
};

export default ApprovalModal;
