"""
ApprovalFlow - Timeline visualization component for approval status
Shows multi-step approval process with current status and timestamps
"""

import React from 'react';
import { format } from 'date-fns';
import { CheckCircle, Clock, XCircle, Eye } from 'lucide-react';

interface ApprovalStep {
  step: string;
  status: 'pending' | 'approved' | 'rejected';
  approver_role: string;
  approver_name?: string;
  approved_at?: string;
  notes?: string;
  is_current?: boolean;
}

interface ApprovalFlowProps {
  steps: ApprovalStep[];
  current_step: number;
  approval_chain: string[];
  status: string;
}

export const ApprovalFlow: React.FC<ApprovalFlowProps> = ({
  steps,
  current_step,
  approval_chain,
  status,
}) => {
  const getStatusIcon = (step: ApprovalStep, index: number) => {
    if (step.status === 'approved') {
      return <CheckCircle className="w-8 h-8 text-green-500" />;
    } else if (step.status === 'rejected') {
      return <XCircle className="w-8 h-8 text-red-500" />;
    } else if (index === current_step && status === 'PENDING') {
      return <Clock className="w-8 h-8 text-yellow-500 animate-pulse" />;
    } else {
      return <Clock className="w-8 h-8 text-gray-300" />;
    }
  };

  const getStatusColor = (step: ApprovalStep, index: number) => {
    if (step.status === 'approved') return 'bg-green-50 border-green-200';
    if (step.status === 'rejected') return 'bg-red-50 border-red-200';
    if (index === current_step && status === 'PENDING') return 'bg-yellow-50 border-yellow-200';
    return 'bg-gray-50 border-gray-200';
  };

  const getStatusBadge = (step: ApprovalStep) => {
    if (step.status === 'approved') {
      return <span className="inline-block px-3 py-1 text-xs font-semibold text-green-800 bg-green-100 rounded-full">Approved</span>;
    } else if (step.status === 'rejected') {
      return <span className="inline-block px-3 py-1 text-xs font-semibold text-red-800 bg-red-100 rounded-full">Rejected</span>;
    }
    return <span className="inline-block px-3 py-1 text-xs font-semibold text-gray-800 bg-gray-100 rounded-full">Pending</span>;
  };

  return (
    <div className="w-full bg-white rounded-lg shadow-md p-6">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-semibold text-gray-900">Approval Status</h3>
        <div className="text-sm text-gray-500">
          Step {current_step + 1} of {approval_chain.length}
        </div>
      </div>

      <div className="space-y-4">
        {steps && steps.map((step, index) => (
          <div key={index} className={`border rounded-lg p-4 ${getStatusColor(step, index)}`}>
            <div className="flex items-start justify-between">
              <div className="flex items-start gap-4 flex-1">
                <div className="flex-shrink-0 mt-1">
                  {getStatusIcon(step, index)}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <h4 className="font-semibold text-gray-900">
                      {step.approver_role}
                      {step.is_current && index === current_step && (
                        <span className="ml-2 text-xs font-normal text-yellow-600">(Awaiting)</span>
                      )}
                    </h4>
                    {getStatusBadge(step)}
                  </div>

                  {step.approver_name && (
                    <p className="text-sm text-gray-600 mt-1">
                      Approver: {step.approver_name}
                    </p>
                  )}

                  {step.approved_at && (
                    <p className="text-sm text-gray-500 mt-1">
                      {format(new Date(step.approved_at), 'PPpp')}
                    </p>
                  )}

                  {step.notes && (
                    <p className="text-sm text-gray-700 mt-2 italic">
                      "{step.notes}"
                    </p>
                  )}
                </div>
              </div>
            </div>

            {/* Connector line to next step */}
            {index < steps.length - 1 && (
              <div className="ml-4 mt-3 pl-4 border-l-2 border-gray-300 h-4" />
            )}
          </div>
        ))}
      </div>

      {/* Overall Status Summary */}
      <div className="mt-6 pt-6 border-t border-gray-200">
        <div className="flex items-center gap-2">
          <span className="text-sm font-semibold text-gray-700">Overall Status:</span>
          <span className={`text-sm font-semibold px-3 py-1 rounded-full
            ${status === 'APPROVED' ? 'bg-green-100 text-green-800' : ''}
            ${status === 'REJECTED' ? 'bg-red-100 text-red-800' : ''}
            ${status === 'PENDING' ? 'bg-yellow-100 text-yellow-800' : ''}
          `}>
            {status}
          </span>
        </div>
      </div>
    </div>
  );
};

export default ApprovalFlow;
