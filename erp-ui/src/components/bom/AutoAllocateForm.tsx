"""
AutoAllocateForm Component - BOM Material Allocation Preview & Confirmation
Feature #1: BOM Manufacturing Auto-Allocate
Path: src/components/bom/AutoAllocateForm.tsx
"""

import React, { useState, useEffect } from 'react';
import { AlertCircle, CheckCircle, AlertTriangle, Loader, Info } from 'lucide-react';

interface MaterialAllocation {
  material_id: number;
  material_name: string;
  qty_needed: number;
  qty_allocated: number;
  warehouse_location: string;
  status: 'ALLOCATED' | 'RESERVED' | 'PENDING_DEBT';
}

interface DebtItem {
  material_id: number;
  material_name: string;
  qty_shortage: number;
  material_debt_id?: number;
  debt_status: string;
}

interface AllocationSummary {
  total_materials: number;
  fully_allocated: number;
  partially_allocated: number;
  shortage_count: number;
}

interface AutoAllocateFormProps {
  article_id: number;
  quantity: number;
  onConfirm: (result: any) => void;
  onCancel: () => void;
  loading?: boolean;
}

export const AutoAllocateForm: React.FC<AutoAllocateFormProps> = ({
  article_id,
  quantity,
  onConfirm,
  onCancel,
  loading = false,
}) => {
  const [allocations, setAllocations] = useState<MaterialAllocation[]>([]);
  const [debts, setDebts] = useState<DebtItem[]>([]);
  const [summary, setSummary] = useState<AllocationSummary | null>(null);
  const [previewLoading, setPreviewLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [allowNegative, setAllowNegative] = useState(false);
  const [confirming, setConfirming] = useState(false);

  // Fetch allocation preview
  useEffect(() => {
    const fetchPreview = async () => {
      try {
        setPreviewLoading(true);
        setError(null);

        const params = new URLSearchParams({
          article_id: String(article_id),
          quantity: String(quantity),
          allow_negative: String(allowNegative),
        });

        const response = await fetch(`/api/v1/production/bom/allocation-preview?${params}`);
        
        if (!response.ok) {
          const data = await response.json();
          throw new Error(data.detail || 'Failed to fetch allocation preview');
        }

        const data = await response.json();
        setAllocations(data.allocated_materials || []);
        setDebts(data.debt_materials || []);
        setSummary(data.summary);

      } catch (err) {
        setError(err instanceof Error ? err.message : 'An error occurred');
      } finally {
        setPreviewLoading(false);
      }
    };

    fetchPreview();
  }, [article_id, quantity, allowNegative]);

  const handleConfirm = async () => {
    if (!summary || (summary.shortage_count > 0 && !allowNegative)) {
      setError('Cannot proceed: Material shortages exist and negative inventory is not allowed');
      return;
    }

    try {
      setConfirming(true);
      onConfirm({
        article_id,
        quantity,
        allow_negative: allowNegative,
        allocations,
        debts,
        summary,
      });
    } finally {
      setConfirming(false);
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'ALLOCATED':
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'RESERVED':
        return <AlertTriangle className="w-5 h-5 text-yellow-500" />;
      case 'PENDING_DEBT':
        return <AlertCircle className="w-5 h-5 text-orange-500" />;
      default:
        return <AlertCircle className="w-5 h-5 text-gray-400" />;
    }
  };

  const getStatusBadge = (status: string) => {
    const badges = {
      ALLOCATED: 'bg-green-100 text-green-800',
      RESERVED: 'bg-yellow-100 text-yellow-800',
      PENDING_DEBT: 'bg-orange-100 text-orange-800',
    };
    return badges[status as keyof typeof badges] || 'bg-gray-100 text-gray-800';
  };

  const canProceed = summary && (summary.shortage_count === 0 || allowNegative);
  const hasShortages = (summary?.shortage_count || 0) > 0;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg p-6 border border-blue-200">
        <h3 className="text-lg font-semibold text-gray-900 mb-2">Material Allocation Preview</h3>
        <p className="text-sm text-gray-600">
          Article: <span className="font-mono font-semibold">{article_id}</span> | 
          Quantity: <span className="font-semibold ml-1">{quantity.toLocaleString()} units</span>
        </p>
      </div>

      {/* Loading State */}
      {previewLoading && (
        <div className="flex items-center justify-center py-12">
          <Loader className="w-6 h-6 animate-spin text-blue-600 mr-3" />
          <span className="text-gray-600">Generating allocation preview...</span>
        </div>
      )}

      {/* Error State */}
      {error && !previewLoading && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
          <div>
            <h4 className="font-semibold text-red-900">Error</h4>
            <p className="text-sm text-red-800 mt-1">{error}</p>
          </div>
        </div>
      )}

      {/* Summary Stats */}
      {summary && !previewLoading && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-white border border-gray-200 rounded-lg p-4">
            <p className="text-sm text-gray-600">Total Materials</p>
            <p className="text-2xl font-bold text-gray-900">{summary.total_materials}</p>
          </div>
          <div className="bg-white border border-gray-200 rounded-lg p-4">
            <p className="text-sm text-gray-600">Fully Allocated</p>
            <p className="text-2xl font-bold text-green-600">{summary.fully_allocated}</p>
          </div>
          <div className="bg-white border border-gray-200 rounded-lg p-4">
            <p className="text-sm text-gray-600">Partial/Debt</p>
            <p className="text-2xl font-bold text-yellow-600">{summary.partially_allocated}</p>
          </div>
          <div className="bg-white border border-gray-200 rounded-lg p-4">
            <p className="text-sm text-gray-600">Shortages</p>
            <p className={`text-2xl font-bold ${summary.shortage_count > 0 ? 'text-red-600' : 'text-green-600'}`}>
              {summary.shortage_count}
            </p>
          </div>
        </div>
      )}

      {/* Allocated Materials */}
      {allocations.length > 0 && !previewLoading && (
        <div className="space-y-3">
          <h4 className="font-semibold text-gray-900 flex items-center gap-2">
            <CheckCircle className="w-5 h-5 text-blue-600" />
            Allocated Materials
          </h4>
          <div className="space-y-2 max-h-64 overflow-y-auto">
            {allocations.map((alloc, idx) => (
              <div key={idx} className={`border rounded-lg p-4 ${getStatusBadge(alloc.status)} bg-white`}>
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      {getStatusIcon(alloc.status)}
                      <div>
                        <p className="font-medium text-gray-900">{alloc.material_name}</p>
                        <p className="text-sm text-gray-600">ID: {alloc.material_id}</p>
                      </div>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="font-semibold text-gray-900">{alloc.qty_allocated.toFixed(2)}</p>
                    <p className="text-xs text-gray-600">of {alloc.qty_needed.toFixed(2)}</p>
                  </div>
                </div>
                <div className="mt-2 pt-2 border-t border-gray-200">
                  <p className="text-xs text-gray-600">Location: <span className="font-mono">{alloc.warehouse_location}</span></p>
                  <div className="w-full bg-gray-200 rounded-full h-2 mt-1">
                    <div
                      className={`h-full rounded-full ${
                        alloc.qty_allocated >= alloc.qty_needed ? 'bg-green-500' : 'bg-yellow-500'
                      }`}
                      style={{ width: `${Math.min((alloc.qty_allocated / alloc.qty_needed) * 100, 100)}%` }}
                    />
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Material Debts (Shortages) */}
      {debts.length > 0 && !previewLoading && (
        <div className="space-y-3">
          <h4 className="font-semibold text-gray-900 flex items-center gap-2">
            <AlertTriangle className="w-5 h-5 text-orange-600" />
            Material Shortages (Debt)
          </h4>
          <div className="bg-orange-50 border border-orange-200 rounded-lg p-4 space-y-3">
            <div className="space-y-2 max-h-40 overflow-y-auto">
              {debts.map((debt, idx) => (
                <div key={idx} className="border border-orange-300 rounded p-3 bg-white">
                  <div className="flex items-start justify-between">
                    <div>
                      <p className="font-medium text-gray-900">{debt.material_name}</p>
                      <p className="text-sm text-gray-600">ID: {debt.material_id}</p>
                    </div>
                    <div className="text-right">
                      <p className="font-bold text-orange-600">{debt.qty_shortage.toFixed(2)}</p>
                      <p className="text-xs text-gray-600">shortage</p>
                    </div>
                  </div>
                  <div className="mt-2">
                    <span className="inline-block px-2 py-1 bg-orange-100 text-orange-800 text-xs font-semibold rounded">
                      {debt.debt_status}
                    </span>
                  </div>
                </div>
              ))}
            </div>

            {/* Negative Inventory Warning & Checkbox */}
            {hasShortages && (
              <div className="border-t border-orange-200 pt-4 mt-4">
                <label className="flex items-start gap-3 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={allowNegative}
                    onChange={(e) => setAllowNegative(e.target.checked)}
                    className="w-4 h-4 mt-1 text-orange-600 rounded focus:ring-orange-500"
                    disabled={confirming}
                  />
                  <div>
                    <p className="font-medium text-gray-900">Allow Production with Material Debt</p>
                    <p className="text-sm text-gray-600">
                      Check this to proceed with production. Material debt will require approval before inventory adjustment.
                    </p>
                  </div>
                </label>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Info Banner */}
      {summary && !previewLoading && (
        <div className={`border rounded-lg p-4 flex items-start gap-3 ${
          canProceed ? 'bg-green-50 border-green-200' : 'bg-blue-50 border-blue-200'
        }`}>
          <Info className={`w-5 h-5 flex-shrink-0 mt-0.5 ${
            canProceed ? 'text-green-600' : 'text-blue-600'
          }`} />
          <div>
            <p className="font-medium text-gray-900">
              {canProceed 
                ? '✅ Ready to proceed' 
                : '⏸️ Cannot proceed yet'}
            </p>
            <p className="text-sm text-gray-600 mt-1">
              {canProceed
                ? 'All materials are available. You can create the SPK.'
                : 'Material shortages detected. You must allow negative inventory or wait for stock to arrive.'}
            </p>
          </div>
        </div>
      )}

      {/* Action Buttons */}
      {!previewLoading && (
        <div className="flex gap-3 pt-4 border-t">
          <button
            onClick={onCancel}
            disabled={confirming}
            className="flex-1 px-4 py-2 border-2 border-gray-300 rounded-lg text-gray-900 font-medium hover:bg-gray-50 transition-colors disabled:opacity-50"
          >
            Cancel
          </button>
          <button
            onClick={handleConfirm}
            disabled={!canProceed || confirming || !summary}
            className={`flex-1 px-4 py-2 rounded-lg text-white font-medium transition-colors flex items-center justify-center gap-2 ${
              canProceed
                ? 'bg-blue-600 hover:bg-blue-700'
                : 'bg-gray-400 cursor-not-allowed'
            } disabled:opacity-50`}
          >
            {confirming && <Loader className="w-4 h-4 animate-spin" />}
            {confirming ? 'Creating SPK...' : 'Create SPK'}
          </button>
        </div>
      )}
    </div>
  );
};

export default AutoAllocateForm;
