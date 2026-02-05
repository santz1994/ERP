import React, { useState, useEffect } from 'react';
import { AlertCircle, CheckCircle, Clock, TrendingUp, Plus, Filter, RefreshCw, Eye, Edit2 } from 'lucide-react';
import { apiClient } from '../api/client';
import { usePermission } from '../hooks/usePermission';
import { useAuthStore } from '../store';
import { UserRole } from '../types';

interface MaterialDebt {
  id: number;
  spk_id: string;
  material_id: number;
  material_name: string;
  qty_owed: number;
  qty_settled: number;
  qty_unit: string;
  department: string;
  approval_status: string;
  debt_status: string;
  created_at: string;
  due_date: string;
  created_by: string;
  approved_by?: string;
  approved_at?: string;
  reason: string;
}

interface Settlement {
  id: number;
  settlement_date: string;
  qty_received: number;
  qty_settled: number;
  adjustment_notes: string;
  recorded_by: string;
}

interface DebtDetailData extends MaterialDebt {
  settlement_history: Settlement[];
  remaining_debt: number;
  excess_qty: number;
}

const MaterialDebtPage: React.FC = () => {
  const hasPermission = (permission: string) => usePermission(permission);
  const [debts, setDebts] = useState<MaterialDebt[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedDebt, setSelectedDebt] = useState<DebtDetailData | null>(null);
  const [showDetailModal, setShowDetailModal] = useState(false);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showAdjustmentModal, setShowAdjustmentModal] = useState(false);
  const [filterStatus, setFilterStatus] = useState<string>('all');
  const [filterDept, setFilterDept] = useState<string>('all');
  const [onlyPendingApproval, setOnlyPendingApproval] = useState(false);
  const [stats, setStats] = useState({
    total_outstanding: 0,
    total_qty: 0,
    pending_approval: 0,
    approved: 0
  });

  const fetchDebts = async () => {
    setLoading(true);
    try {
      const response = await apiClient.get('/api/v1/warehouse/material-debt/outstanding', {
        params: {
          only_pending_approval: onlyPendingApproval
        }
      });
      setDebts(response.data.debts || []);
      setStats({
        total_outstanding: response.data.total_outstanding_value || 0,
        total_qty: response.data.total_outstanding_qty || 0,
        pending_approval: response.data.debts?.filter((d: any) => d.approval_status === 'PENDING_APPROVAL').length || 0,
        approved: response.data.debts?.filter((d: any) => d.approval_status === 'APPROVED').length || 0
      });
    } catch (error) {
      console.error('Error fetching debts:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDebts();
  }, [onlyPendingApproval]);

  const fetchDebtDetail = async (debtId: number) => {
    try {
      const response = await apiClient.get(`/api/v1/warehouse/material-debt/${debtId}`);
      setSelectedDebt(response.data);
      setShowDetailModal(true);
    } catch (error) {
      console.error('Error fetching debt detail:', error);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'PENDING_APPROVAL': return 'bg-yellow-100 text-yellow-800';
      case 'SPV_APPROVED': return 'bg-blue-100 text-blue-800';
      case 'MANAGER_APPROVED': return 'bg-blue-100 text-blue-800';
      case 'APPROVED': return 'bg-green-100 text-green-800';
      case 'REJECTED': return 'bg-red-100 text-red-800';
      case 'FULLY_RESOLVED': return 'bg-green-100 text-green-800';
      case 'PARTIAL_RESOLVED': return 'bg-orange-100 text-orange-800';
      case 'EXCESS': return 'bg-purple-100 text-purple-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'PENDING_APPROVAL': return <Clock className="w-4 h-4" />;
      case 'APPROVED': return <CheckCircle className="w-4 h-4" />;
      case 'REJECTED': return <AlertCircle className="w-4 h-4" />;
      case 'FULLY_RESOLVED': return <CheckCircle className="w-4 h-4" />;
      default: return <TrendingUp className="w-4 h-4" />;
    }
  };

  const filteredDebts = debts.filter(debt => {
    if (filterStatus !== 'all' && debt.approval_status !== filterStatus) return false;
    if (filterDept !== 'all' && debt.department !== filterDept) return false;
    return true;
  });

  const departments = Array.from(new Set(debts.map(d => d.department)));

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">Material Debt Management</h1>
          <p className="text-gray-600">Manage negative inventory and material debt approvals</p>
        </div>

        {/* Statistics Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow-md p-6 border-l-4 border-orange-500">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-500 text-sm font-medium">Total Outstanding Qty</p>
                <p className="text-2xl font-bold text-orange-600">{stats.total_qty.toLocaleString()}</p>
              </div>
              <TrendingUp className="w-10 h-10 text-orange-200" />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6 border-l-4 border-yellow-500">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-500 text-sm font-medium">Pending Approval</p>
                <p className="text-2xl font-bold text-yellow-600">{stats.pending_approval}</p>
              </div>
              <Clock className="w-10 h-10 text-yellow-200" />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6 border-l-4 border-green-500">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-500 text-sm font-medium">Approved Debts</p>
                <p className="text-2xl font-bold text-green-600">{stats.approved}</p>
              </div>
              <CheckCircle className="w-10 h-10 text-green-200" />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6 border-l-4 border-blue-500">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-500 text-sm font-medium">Total Value (Rp)</p>
                <p className="text-2xl font-bold text-blue-600">
                  {(stats.total_outstanding / 1000000000).toFixed(1)}B
                </p>
              </div>
              <AlertCircle className="w-10 h-10 text-blue-200" />
            </div>
          </div>
        </div>

        {/* Controls */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-8">
          <div className="flex flex-col md:flex-row gap-4 items-start md:items-center justify-between">
            <div className="flex flex-col md:flex-row gap-4 items-start md:items-center flex-1">
              <div className="flex items-center gap-2">
                <Filter className="w-5 h-5 text-gray-600" />
                <select
                  value={filterStatus}
                  onChange={(e) => setFilterStatus(e.target.value)}
                  className="px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="all">All Status</option>
                  <option value="PENDING_APPROVAL">Pending Approval</option>
                  <option value="APPROVED">Approved</option>
                  <option value="FULLY_RESOLVED">Fully Resolved</option>
                  <option value="PARTIAL_RESOLVED">Partial Resolved</option>
                </select>
              </div>

              <select
                value={filterDept}
                onChange={(e) => setFilterDept(e.target.value)}
                className="px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="all">All Departments</option>
                {departments.map(dept => (
                  <option key={dept} value={dept}>{dept}</option>
                ))}
              </select>

              <label className="flex items-center gap-2 text-sm cursor-pointer">
                <input
                  type="checkbox"
                  checked={onlyPendingApproval}
                  onChange={(e) => setOnlyPendingApproval(e.target.checked)}
                  className="w-4 h-4 text-blue-500 rounded"
                />
                <span className="text-gray-700">Only Pending Approval</span>
              </label>
            </div>

            <div className="flex gap-2">
              <button
                onClick={fetchDebts}
                className="p-2 bg-gray-100 hover:bg-gray-200 rounded-md transition"
                title="Refresh"
              >
                <RefreshCw className="w-5 h-5 text-gray-600" />
              </button>
              
              {hasPermission('warehouse.write_debt') && (
                <button
                  onClick={() => setShowCreateModal(true)}
                  className="flex items-center gap-2 px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 transition"
                >
                  <Plus className="w-5 h-5" />
                  Create Debt
                </button>
              )}
            </div>
          </div>
        </div>

        {/* Debts Table */}
        <div className="bg-white rounded-lg shadow-md overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b bg-gray-50">
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase">SPK</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase">Material</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase">Department</th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-700 uppercase">Qty Owned</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase">Approval Status</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase">Debt Status</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase">Due Date</th>
                  <th className="px-6 py-3 text-center text-xs font-medium text-gray-700 uppercase">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {loading ? (
                  <tr>
                    <td colSpan={8} className="px-6 py-4 text-center text-gray-500">
                      Loading debts...
                    </td>
                  </tr>
                ) : filteredDebts.length === 0 ? (
                  <tr>
                    <td colSpan={8} className="px-6 py-4 text-center text-gray-500">
                      No material debts found
                    </td>
                  </tr>
                ) : (
                  filteredDebts.map(debt => (
                    <tr key={debt.id} className="hover:bg-gray-50 transition">
                      <td className="px-6 py-4 text-sm font-medium text-gray-900">{debt.spk_id}</td>
                      <td className="px-6 py-4 text-sm text-gray-700">{debt.material_name}</td>
                      <td className="px-6 py-4 text-sm text-gray-700">{debt.department}</td>
                      <td className="px-6 py-4 text-sm text-right font-semibold text-gray-900">
                        {debt.qty_owed.toLocaleString()} {debt.qty_unit}
                      </td>
                      <td className="px-6 py-4 text-sm">
                        <span className={`inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-medium ${getStatusColor(debt.approval_status)}`}>
                          {getStatusIcon(debt.approval_status)}
                          {debt.approval_status.replace(/_/g, ' ')}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-sm">
                        <span className={`inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-medium ${getStatusColor(debt.debt_status)}`}>
                          {debt.debt_status.replace(/_/g, ' ')}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-700">
                        {new Date(debt.due_date).toLocaleDateString('id-ID')}
                      </td>
                      <td className="px-6 py-4 text-sm text-center">
                        <div className="flex items-center justify-center gap-2">
                          <button
                            onClick={() => fetchDebtDetail(debt.id)}
                            className="p-1 text-blue-600 hover:bg-blue-50 rounded transition"
                            title="View Details"
                          >
                            <Eye className="w-5 h-5" />
                          </button>
                          {hasPermission('warehouse.write_debt') && debt.approval_status === 'APPROVED' && (
                            <button
                              onClick={() => {
                                setSelectedDebt(debt as any);
                                setShowAdjustmentModal(true);
                              }}
                              className="p-1 text-green-600 hover:bg-green-50 rounded transition"
                              title="Record Settlement"
                            >
                              <Edit2 className="w-5 h-5" />
                            </button>
                          )}
                        </div>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* Detail Modal */}
        {showDetailModal && selectedDebt && (
          <DebtDetailModal
            debt={selectedDebt}
            onClose={() => {
              setShowDetailModal(false);
              setSelectedDebt(null);
            }}
            onApprove={() => {
              fetchDebts();
              setShowDetailModal(false);
              setSelectedDebt(null);
            }}
          />
        )}

        {/* Create Debt Modal */}
        {showCreateModal && (
          <CreateDebtModal
            onClose={() => setShowCreateModal(false)}
            onSuccess={() => {
              fetchDebts();
              setShowCreateModal(false);
            }}
          />
        )}

        {/* Adjustment Modal */}
        {showAdjustmentModal && selectedDebt && (
          <AdjustmentModal
            debt={selectedDebt}
            onClose={() => {
              setShowAdjustmentModal(false);
              setSelectedDebt(null);
            }}
            onSuccess={() => {
              fetchDebts();
              setShowAdjustmentModal(false);
              setSelectedDebt(null);
            }}
          />
        )}
      </div>
    </div>
  );
};

// DebtDetailModal Component
const DebtDetailModal: React.FC<{
  debt: DebtDetailData;
  onClose: () => void;
  onApprove: () => void;
}> = ({ debt, onClose, onApprove }) => {
  const user = useAuthStore(state => state.user);
  const canApproveDebt = usePermission('warehouse.approve_debt');
  const [loading, setLoading] = useState(false);
  const [approvalNotes, setApprovalNotes] = useState('');
  const [approvalDecision, setApprovalDecision] = useState('APPROVE');

  const handleApproval = async (decision: string) => {
    setLoading(true);
    try {
      const approverRole = user?.role === UserRole.MANAGER || user?.role === UserRole.FINANCE_MANAGER ? 'MANAGER' : 'SPV';
      await apiClient.post(`/api/v1/warehouse/material-debt/${debt.id}/approve`, {
        approval_decision: decision,
        approver_role: approverRole,
        notes: approvalNotes
      });
      onApprove();
    } catch (error) {
      console.error('Error submitting approval:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div className="sticky top-0 bg-gradient-to-r from-blue-600 to-blue-700 p-6 text-white flex justify-between items-center">
          <h2 className="text-xl font-bold">Material Debt Details</h2>
          <button onClick={onClose} className="text-white hover:bg-white hover:bg-opacity-20 rounded p-1">
            
          </button>
        </div>

        <div className="p-6 space-y-6">
          {/* Basic Info */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="text-gray-500 text-sm">SPK ID</p>
              <p className="text-gray-900 font-semibold">{debt.spk_id}</p>
            </div>
            <div>
              <p className="text-gray-500 text-sm">Material</p>
              <p className="text-gray-900 font-semibold">{debt.material_name}</p>
            </div>
            <div>
              <p className="text-gray-500 text-sm">Department</p>
              <p className="text-gray-900 font-semibold">{debt.department}</p>
            </div>
            <div>
              <p className="text-gray-500 text-sm">Created By</p>
              <p className="text-gray-900 font-semibold">{debt.created_by}</p>
            </div>
          </div>

          {/* Debt Status */}
          <div className="border-t pt-4">
            <h3 className="font-semibold text-gray-900 mb-3">Debt Status</h3>
            <div className="grid grid-cols-2 gap-4">
              <div className="bg-orange-50 p-4 rounded-lg">
                <p className="text-gray-500 text-sm">Quantity Owed</p>
                <p className="text-2xl font-bold text-orange-600">
                  {debt.qty_owed.toLocaleString()} {debt.qty_unit}
                </p>
              </div>
              <div className="bg-green-50 p-4 rounded-lg">
                <p className="text-gray-500 text-sm">Quantity Settled</p>
                <p className="text-2xl font-bold text-green-600">
                  {debt.qty_settled.toLocaleString()} {debt.qty_unit}
                </p>
              </div>
              <div className="bg-blue-50 p-4 rounded-lg">
                <p className="text-gray-500 text-sm">Remaining Debt</p>
                <p className="text-2xl font-bold text-blue-600">
                  {debt.remaining_debt.toLocaleString()} {debt.qty_unit}
                </p>
              </div>
              <div className="bg-purple-50 p-4 rounded-lg">
                <p className="text-gray-500 text-sm">Excess Qty</p>
                <p className="text-2xl font-bold text-purple-600">
                  {debt.excess_qty.toLocaleString()} {debt.qty_unit}
                </p>
              </div>
            </div>
          </div>

          {/* Reason & Notes */}
          <div className="border-t pt-4">
            <h3 className="font-semibold text-gray-900 mb-3">Details</h3>
            <div>
              <p className="text-gray-500 text-sm">Reason for Debt</p>
              <p className="text-gray-900 font-medium bg-gray-50 p-3 rounded-lg">{debt.reason}</p>
            </div>
          </div>

          {/* Settlement History */}
          {debt.settlement_history.length > 0 && (
            <div className="border-t pt-4">
              <h3 className="font-semibold text-gray-900 mb-3">Settlement History</h3>
              <div className="space-y-3">
                {debt.settlement_history.map((settlement, idx) => (
                  <div key={idx} className="bg-gray-50 p-4 rounded-lg">
                    <div className="flex justify-between items-start mb-2">
                      <p className="text-gray-900 font-semibold">
                        Settlement #{idx + 1}
                      </p>
                      <p className="text-gray-500 text-sm">
                        {new Date(settlement.settlement_date).toLocaleDateString('id-ID')}
                      </p>
                    </div>
                    <p className="text-sm text-gray-700">
                      Received: {settlement.qty_received} {debt.qty_unit} | Settled: {settlement.qty_settled} {debt.qty_unit}
                    </p>
                    <p className="text-sm text-gray-600 mt-1">
                      Notes: {settlement.adjustment_notes}
                    </p>
                    <p className="text-xs text-gray-500 mt-1">
                      By: {settlement.recorded_by}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Approval Section */}
          {debt.approval_status === 'PENDING_APPROVAL' && canApproveDebt && (
            <div className="border-t pt-4 bg-yellow-50 p-4 rounded-lg">
              <h3 className="font-semibold text-gray-900 mb-3">Pending Your Approval</h3>
              <textarea
                value={approvalNotes}
                onChange={(e) => setApprovalNotes(e.target.value)}
                placeholder="Add approval notes (optional)"
                className="w-full p-3 border border-gray-300 rounded-lg mb-3 focus:outline-none focus:ring-2 focus:ring-blue-500"
                rows={3}
              />
              <div className="flex gap-2">
                <button
                  onClick={() => handleApproval('APPROVE')}
                  disabled={loading}
                  className="flex-1 px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 disabled:opacity-50 transition"
                >
                  Approve
                </button>
                <button
                  onClick={() => handleApproval('REJECT')}
                  disabled={loading}
                  className="flex-1 px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 disabled:opacity-50 transition"
                >
                  Reject
                </button>
              </div>
            </div>
          )}

          {debt.approved_by && (
            <div className="border-t pt-4 bg-green-50 p-4 rounded-lg">
              <p className="text-sm text-gray-700">
                <span className="font-semibold">Approved by:</span> {debt.approved_by}
              </p>
              <p className="text-sm text-gray-600 mt-1">
                {new Date(debt.approved_at || '').toLocaleDateString('id-ID')}
              </p>
            </div>
          )}
        </div>

        <div className="border-t bg-gray-50 p-4 flex justify-end gap-2">
          <button
            onClick={onClose}
            className="px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};

// CreateDebtModal Component
const CreateDebtModal: React.FC<{
  onClose: () => void;
  onSuccess: () => void;
}> = ({ onClose, onSuccess }) => {
  const [formData, setFormData] = useState({
    spk_id: '',
    material_id: '',
    qty_owed: '',
    reason: '',
    department: '',
    due_date: '',
    allow_production: true
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      await apiClient.post('/api/v1/warehouse/material-debt/create', {
        ...formData,
        qty_owed: parseFloat(formData.qty_owed)
      });
      onSuccess();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create debt');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-lg w-full">
        <div className="bg-gradient-to-r from-blue-600 to-blue-700 p-6 text-white flex justify-between items-center">
          <h2 className="text-xl font-bold">Create Material Debt</h2>
          <button onClick={onClose} className="text-white hover:bg-white hover:bg-opacity-20 rounded p-1">
            
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 p-3 rounded-lg text-sm">
              {error}
            </div>
          )}

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">SPK ID *</label>
            <input
              type="text"
              required
              value={formData.spk_id}
              onChange={(e) => setFormData({ ...formData, spk_id: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="SPK-2026-00123"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Material ID *</label>
            <input
              type="number"
              required
              value={formData.material_id}
              onChange={(e) => setFormData({ ...formData, material_id: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Material ID"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Quantity Owed *</label>
            <input
              type="number"
              required
              step="0.01"
              value={formData.qty_owed}
              onChange={(e) => setFormData({ ...formData, qty_owed: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="0.00"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Department *</label>
            <select
              required
              value={formData.department}
              onChange={(e) => setFormData({ ...formData, department: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Select Department</option>
              <option value="Cutting">Cutting</option>
              <option value="Sewing">Sewing</option>
              <option value="Finishing">Finishing</option>
              <option value="Packing">Packing</option>
              <option value="Warehouse">Warehouse</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Reason *</label>
            <textarea
              required
              value={formData.reason}
              onChange={(e) => setFormData({ ...formData, reason: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Why is material needed before it arrives?"
              rows={3}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Due Date *</label>
            <input
              type="date"
              required
              value={formData.due_date}
              onChange={(e) => setFormData({ ...formData, due_date: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="checkbox"
              checked={formData.allow_production}
              onChange={(e) => setFormData({ ...formData, allow_production: e.target.checked })}
              className="w-4 h-4 text-blue-500 rounded"
            />
            <span className="text-sm text-gray-700">Allow production to start while pending approval</span>
          </label>

          <div className="flex gap-2 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="flex-1 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50 transition"
            >
              {loading ? 'Creating...' : 'Create Debt'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

// AdjustmentModal Component
const AdjustmentModal: React.FC<{
  debt: DebtDetailData;
  onClose: () => void;
  onSuccess: () => void;
}> = ({ debt, onClose, onSuccess }) => {
  const [formData, setFormData] = useState({
    actual_received_qty: '',
    adjustment_notes: '',
    received_date: new Date().toISOString().split('T')[0]
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      await apiClient.post(`/api/v1/warehouse/material-debt/${debt.id}/adjust`, {
        actual_received_qty: parseFloat(formData.actual_received_qty),
        adjustment_notes: formData.adjustment_notes,
        received_date: formData.received_date
      });
      onSuccess();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to record settlement');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-lg w-full">
        <div className="bg-gradient-to-r from-green-600 to-green-700 p-6 text-white flex justify-between items-center">
          <h2 className="text-xl font-bold">Record Material Settlement</h2>
          <button onClick={onClose} className="text-white hover:bg-white hover:bg-opacity-20 rounded p-1">
            
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 p-3 rounded-lg text-sm">
              {error}
            </div>
          )}

          <div className="bg-blue-50 p-4 rounded-lg">
            <p className="text-sm text-gray-600">SPK: <span className="font-semibold">{debt.spk_id}</span></p>
            <p className="text-sm text-gray-600">Material: <span className="font-semibold">{debt.material_name}</span></p>
            <p className="text-sm text-gray-600">
              Remaining Debt: <span className="font-semibold text-red-600">{debt.remaining_debt} {debt.qty_unit}</span>
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Actual Quantity Received *</label>
            <input
              type="number"
              required
              step="0.01"
              value={formData.actual_received_qty}
              onChange={(e) => setFormData({ ...formData, actual_received_qty: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
              placeholder={`Enter qty (max: ${debt.remaining_debt})`}
            />
            <p className="text-xs text-gray-500 mt-1">
              If less than owed: Partial resolution | If equal: Fully resolved | If more: Excess qty recorded
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Received Date *</label>
            <input
              type="date"
              required
              value={formData.received_date}
              onChange={(e) => setFormData({ ...formData, received_date: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Notes</label>
            <textarea
              value={formData.adjustment_notes}
              onChange={(e) => setFormData({ ...formData, adjustment_notes: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
              placeholder="Any notes about this settlement (optional)"
              rows={3}
            />
          </div>

          <div className="flex gap-2 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="flex-1 px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 disabled:opacity-50 transition"
            >
              {loading ? 'Recording...' : 'Record Settlement'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default MaterialDebtPage;
