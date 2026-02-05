/**
 * Copyright (c) 2026 PT Quty Karunia / Daniel Rizaldy - All Rights Reserved
 * File: DailyProgressModal.tsx | Author: Daniel Rizaldy | Date: 2026-02-04
 * Modal for Daily Production Input
 */

import { useState, useEffect } from 'react';
import { format } from 'date-fns';
import { X, Save, AlertCircle } from 'lucide-react';

interface DailyProgressModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSave: (data: DailyProgressData) => Promise<void>;
  date: Date;
  workOrderId: number;
  existingData?: DailyProgressData;
  defectOptions?: string[];
  departmentName: string;
}

export interface DailyProgressData {
  date: string; // YYYY-MM-DD
  production_qty: number;
  good_qty: number;
  defect_qty: number;
  defect_reasons?: Record<string, number>;
  notes?: string;
}

export const DailyProgressModal: React.FC<DailyProgressModalProps> = ({
  isOpen,
  onClose,
  onSave,
  date,
  workOrderId,
  existingData,
  defectOptions = [
    'Broken Stitch',
    'Skip Stitch',
    'Wrong Thread Color',
    'Dirty/Stained',
    'Uneven Seam',
    'Missing Component',
    'Wrong Size',
    'Measurement Error',
    'Material Defect',
    'Other'
  ],
  departmentName
}) => {
  const [productionQty, setProductionQty] = useState(0);
  const [goodQty, setGoodQty] = useState(0);
  const [defectQty, setDefectQty] = useState(0);
  const [notes, setNotes] = useState('');
  const [defectReasons, setDefectReasons] = useState<Record<string, number>>({});
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (existingData) {
      setProductionQty(existingData.production_qty);
      setGoodQty(existingData.good_qty);
      setDefectQty(existingData.defect_qty);
      setNotes(existingData.notes || '');
      setDefectReasons(existingData.defect_reasons || {});
    } else {
      // Reset form
      setProductionQty(0);
      setGoodQty(0);
      setDefectQty(0);
      setNotes('');
      setDefectReasons({});
    }
    setError('');
  }, [existingData, isOpen]);

  // Auto-calculate defect qty
  useEffect(() => {
    const calculatedDefect = productionQty - goodQty;
    if (calculatedDefect >= 0 && calculatedDefect !== defectQty) {
      setDefectQty(calculatedDefect);
    }
  }, [productionQty, goodQty]);

  const handleDefectReasonChange = (reason: string, qty: number) => {
    setDefectReasons(prev => {
      const updated = { ...prev };
      if (qty > 0) {
        updated[reason] = qty;
      } else {
        delete updated[reason];
      }
      return updated;
    });
  };

  const totalDefectReasons = Object.values(defectReasons).reduce((sum, qty) => sum + qty, 0);

  const handleSave = async () => {
    // Validation
    if (productionQty <= 0) {
      setError('Production quantity must be greater than 0');
      return;
    }

    if (goodQty > productionQty) {
      setError('Good output cannot exceed total production');
      return;
    }

    if (defectQty > 0 && totalDefectReasons !== defectQty) {
      setError(`Defect reasons total (${totalDefectReasons}) must equal defect quantity (${defectQty})`);
      return;
    }

    setIsSaving(true);
    setError('');

    try {
      await onSave({
        date: format(date, 'yyyy-MM-dd'),
        production_qty: productionQty,
        good_qty: goodQty,
        defect_qty: defectQty,
        defect_reasons: defectReasons,
        notes: notes.trim()
      });
      onClose();
    } catch (err: any) {
      setError(err.message || 'Failed to save daily progress');
    } finally {
      setIsSaving(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200 bg-gradient-to-r from-blue-50 to-blue-100">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">
              Input Daily Progress
            </h2>
            <p className="text-sm text-gray-600 mt-1">
              {departmentName} - {format(date, 'EEEE, dd MMMM yyyy')}
            </p>
          </div>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700 transition-colors"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Body */}
        <div className="p-6 space-y-6">
          {error && (
            <div className="bg-red-50 border-l-4 border-red-500 p-4 flex items-start gap-3">
              <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
              <div className="text-sm text-red-700">{error}</div>
            </div>
          )}

          {/* Production Quantity */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              Total Production Quantity <span className="text-red-500">*</span>
            </label>
            <input
              type="number"
              min="0"
              value={productionQty || ''}
              onChange={(e) => setProductionQty(parseInt(e.target.value) || 0)}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-lg font-semibold"
              placeholder="Enter total pieces produced today"
            />
            <p className="text-xs text-gray-500 mt-1">Total pieces processed in this department today</p>
          </div>

          {/* Good Output */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              Good Output (Quality Passed) <span className="text-red-500">*</span>
            </label>
            <input
              type="number"
              min="0"
              max={productionQty}
              value={goodQty || ''}
              onChange={(e) => setGoodQty(parseInt(e.target.value) || 0)}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent text-lg font-semibold"
              placeholder="Enter good pieces"
            />
            <p className="text-xs text-gray-500 mt-1">Pieces that passed quality inspection</p>
          </div>

          {/* Defect Quantity (Auto-calculated) */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              Defect Found
            </label>
            <div className="px-4 py-3 bg-gray-100 border border-gray-300 rounded-lg text-lg font-semibold text-gray-900">
              {defectQty} pcs
            </div>
            <p className="text-xs text-gray-500 mt-1">Auto-calculated: Production - Good Output</p>
          </div>

          {/* Defect Reasons (if defects exist) */}
          {defectQty > 0 && (
            <div className="border-t pt-4">
              <label className="block text-sm font-semibold text-gray-700 mb-3">
                Defect Classification <span className="text-red-500">*</span>
                <span className="text-xs font-normal text-gray-500 ml-2">
                  (Total: {totalDefectReasons}/{defectQty})
                </span>
              </label>
              <div className="grid grid-cols-2 gap-3">
                {defectOptions.map(reason => (
                  <div key={reason} className="flex items-center gap-2">
                    <input
                      type="number"
                      min="0"
                      max={defectQty}
                      value={defectReasons[reason] || ''}
                      onChange={(e) => handleDefectReasonChange(reason, parseInt(e.target.value) || 0)}
                      className="w-20 px-2 py-1 border border-gray-300 rounded text-sm"
                      placeholder="0"
                    />
                    <label className="text-sm text-gray-700">{reason}</label>
                  </div>
                ))}
              </div>
              {totalDefectReasons !== defectQty && (
                <div className="mt-2 text-xs text-orange-600 flex items-center gap-1">
                  <AlertCircle className="w-3 h-3" />
                  Please allocate all {defectQty} defects to specific reasons
                </div>
              )}
            </div>
          )}

          {/* Notes */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              Notes (Optional)
            </label>
            <textarea
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              rows={3}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Any issues, machine downtime, or special notes for today..."
            />
            <p className="text-xs text-gray-500 mt-1">Example: Machine #3 maintenance 1 hour, Rush order completed</p>
          </div>

          {/* Summary */}
          <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
            <h4 className="font-semibold text-gray-900 mb-2">Summary</h4>
            <div className="grid grid-cols-3 gap-4 text-sm">
              <div>
                <div className="text-gray-600">Total Production</div>
                <div className="text-xl font-bold text-gray-900">{productionQty} pcs</div>
              </div>
              <div>
                <div className="text-gray-600">Good Output</div>
                <div className="text-xl font-bold text-green-600">{goodQty} pcs</div>
              </div>
              <div>
                <div className="text-gray-600">Defect Rate</div>
                <div className="text-xl font-bold text-red-600">
                  {productionQty > 0 ? ((defectQty / productionQty) * 100).toFixed(1) : 0}%
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-end gap-3 p-6 border-t border-gray-200 bg-gray-50">
          <button
            onClick={onClose}
            disabled={isSaving}
            className="px-6 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-100 transition-colors disabled:opacity-50"
          >
            Cancel
          </button>
          <button
            onClick={handleSave}
            disabled={isSaving || productionQty <= 0 || (defectQty > 0 && totalDefectReasons !== defectQty)}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
          >
            <Save className="w-4 h-4" />
            {isSaving ? 'Saving...' : 'Save Progress'}
          </button>
        </div>
      </div>
    </div>
  );
};
