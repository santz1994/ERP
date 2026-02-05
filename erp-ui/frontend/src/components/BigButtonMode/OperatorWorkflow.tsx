import React, { useState } from 'react';
import { BigButton } from './BigButton';

export interface WorkflowStep {
  id: string;
  title: string;
  description?: string;
  action: () => Promise<void> | void;
  icon?: string;
  confirmMessage?: string;
}

export interface OperatorWorkflowProps {
  steps: WorkflowStep[];
  onComplete?: () => void;
  onCancel?: () => void;
}

export const OperatorWorkflow: React.FC<OperatorWorkflowProps> = ({
  steps,
  onComplete,
  onCancel,
}) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const step = steps[currentStep];
  const isLastStep = currentStep === steps.length - 1;

  const handleAction = async () => {
    try {
      setLoading(true);
      setError(null);
      await step.action();
      
      if (isLastStep) {
        onComplete?.();
      } else {
        setCurrentStep(currentStep + 1);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
      setLoading(false);
    }
  };

  const handleBack = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
      setError(null);
    } else {
      onCancel?.();
    }
  };

  return (
    <div className="w-full h-screen bg-gray-50 flex flex-col">
      {/* Progress Bar */}
      <div className="bg-gray-200 h-3">
        <div
          className="bg-blue-600 h-full transition-all duration-300"
          style={{
            width: `${((currentStep + 1) / steps.length) * 100}%`,
          }}
        />
      </div>

      {/* Content */}
      <div className="flex-1 flex flex-col items-center justify-center p-8">
        {/* Step Counter */}
        <div className="text-2xl font-bold text-gray-600 mb-8">
          Step {currentStep + 1} of {steps.length}
        </div>

        {/* Step Icon */}
        {step.icon && (
          <div className="text-8xl mb-8 animate-bounce">{step.icon}</div>
        )}

        {/* Step Title */}
        <h1 className="text-4xl font-bold text-center mb-4 text-gray-900">
          {step.title}
        </h1>

        {/* Step Description */}
        {step.description && (
          <p className="text-2xl text-gray-600 text-center mb-8 max-w-2xl">
            {step.description}
          </p>
        )}

        {/* Confirm Message */}
        {step.confirmMessage && (
          <div className="bg-yellow-50 border-4 border-yellow-300 rounded-lg p-6 mb-8 w-full max-w-2xl">
            <p className="text-xl text-yellow-700">{step.confirmMessage}</p>
          </div>
        )}

        {/* Error Message */}
        {error && (
          <div className="bg-red-50 border-4 border-red-300 rounded-lg p-6 mb-8 w-full max-w-2xl">
            <p className="text-lg text-red-700 font-bold">Error:</p>
            <p className="text-lg text-red-700">{error}</p>
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex gap-4 w-full max-w-2xl">
          <BigButton
            variant="secondary"
            onClick={handleBack}
            disabled={loading}
          >
            ← BACK
          </BigButton>
          <BigButton
            variant="primary"
            onClick={handleAction}
            disabled={loading}
          >
            {loading ? '⏳ PROCESSING...' : '→ NEXT'}
          </BigButton>
        </div>

        {/* Cancel Button */}
        <button
          onClick={onCancel}
          disabled={loading}
          className="mt-8 text-xl font-semibold text-gray-600 hover:text-gray-800 underline disabled:opacity-50"
        >
          Cancel Workflow
        </button>
      </div>
    </div>
  );
};
