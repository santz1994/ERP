/**
 * Form Field Component with Validation
 * ERP Quty Karunia - UI Standardization
 * Date: 4 Februari 2026
 */

import React from 'react';
import { AlertCircle, CheckCircle, Info } from 'lucide-react';

interface FormFieldProps {
  label: string;
  error?: string;
  success?: string;
  info?: string;
  required?: boolean;
  children: React.ReactNode;
  className?: string;
  labelClassName?: string;
}

/**
 * FormField - Standardized form field wrapper with validation feedback
 * 
 * @param label - Field label
 * @param error - Error message (shows red alert)
 * @param success - Success message (shows green checkmark)
 * @param info - Info message (shows blue info icon)
 * @param required - Whether field is required (adds red asterisk)
 * @param children - Input element
 * @param className - Additional wrapper classes
 * @param labelClassName - Additional label classes
 * 
 * @example
 * <FormField 
 *   label="Product Name" 
 *   required 
 *   error={errors.product_name}
 * >
 *   <input 
 *     type="text" 
 *     value={form.product_name}
 *     onChange={(e) => setForm({...form, product_name: e.target.value})}
 *     className="w-full px-3 py-2 border rounded-md"
 *   />
 * </FormField>
 */
export const FormField: React.FC<FormFieldProps> = ({
  label,
  error,
  success,
  info,
  required,
  children,
  className = '',
  labelClassName = '',
}) => {
  return (
    <div className={`space-y-2 ${className}`}>
      <label className={`block text-sm font-medium text-gray-700 ${labelClassName}`}>
        {label}
        {required && <span className="text-red-500 ml-1">*</span>}
      </label>
      
      {children}
      
      {error && (
        <div className="flex items-start gap-2 text-sm text-red-600 bg-red-50 border border-red-200 rounded-md p-2">
          <AlertCircle className="w-4 h-4 mt-0.5 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}
      
      {success && !error && (
        <div className="flex items-start gap-2 text-sm text-green-600 bg-green-50 border border-green-200 rounded-md p-2">
          <CheckCircle className="w-4 h-4 mt-0.5 flex-shrink-0" />
          <span>{success}</span>
        </div>
      )}
      
      {info && !error && !success && (
        <div className="flex items-start gap-2 text-sm text-blue-600 bg-blue-50 border border-blue-200 rounded-md p-2">
          <Info className="w-4 h-4 mt-0.5 flex-shrink-0" />
          <span>{info}</span>
        </div>
      )}
    </div>
  );
};

interface FormSectionProps {
  title: string;
  description?: string;
  children: React.ReactNode;
  className?: string;
}

/**
 * FormSection - Groups related form fields with header
 * 
 * @example
 * <FormSection title="Product Information" description="Basic product details">
 *   <FormField label="Name">{/* ... *}/</FormField>
 *   <FormField label="Category">{/* ... *}/</FormField>
 * </FormSection>
 */
export const FormSection: React.FC<FormSectionProps> = ({
  title,
  description,
  children,
  className = '',
}) => {
  return (
    <div className={`space-y-4 ${className}`}>
      <div className="border-b border-gray-200 pb-3">
        <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
        {description && (
          <p className="text-sm text-gray-600 mt-1">{description}</p>
        )}
      </div>
      <div className="space-y-4">
        {children}
      </div>
    </div>
  );
};

interface FormActionsProps {
  onCancel?: () => void;
  onSubmit?: () => void;
  cancelText?: string;
  submitText?: string;
  isSubmitting?: boolean;
  submitDisabled?: boolean;
  className?: string;
}

/**
 * FormActions - Standardized form action buttons (Cancel/Submit)
 * 
 * @example
 * <FormActions
 *   onCancel={() => setShowModal(false)}
 *   onSubmit={handleSubmit}
 *   submitText="Create Order"
 *   isSubmitting={createMutation.isLoading}
 * />
 */
export const FormActions: React.FC<FormActionsProps> = ({
  onCancel,
  onSubmit,
  cancelText = 'Cancel',
  submitText = 'Submit',
  isSubmitting = false,
  submitDisabled = false,
  className = '',
}) => {
  return (
    <div className={`flex items-center justify-end gap-3 pt-4 border-t border-gray-200 ${className}`}>
      {onCancel && (
        <button
          type="button"
          onClick={onCancel}
          disabled={isSubmitting}
          className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {cancelText}
        </button>
      )}
      
      {onSubmit && (
        <button
          type="button"
          onClick={onSubmit}
          disabled={isSubmitting || submitDisabled}
          className="px-4 py-2 bg-brand-600 text-white rounded-md hover:bg-brand-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
        >
          {isSubmitting && (
            <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
            </svg>
          )}
          {submitText}
        </button>
      )}
    </div>
  );
};

interface SelectFieldOption {
  value: string | number;
  label: string;
  disabled?: boolean;
}

interface SelectFieldProps {
  label: string;
  options: SelectFieldOption[];
  value: string | number;
  onChange: (value: string) => void;
  required?: boolean;
  error?: string;
  placeholder?: string;
  className?: string;
}

/**
 * SelectField - Standardized select dropdown
 * 
 * @example
 * <SelectField
 *   label="Department"
 *   options={[
 *     { value: 'cutting', label: 'Cutting' },
 *     { value: 'sewing', label: 'Sewing' }
 *   ]}
 *   value={form.department}
 *   onChange={(val) => setForm({...form, department: val})}
 *   required
 * />
 */
export const SelectField: React.FC<SelectFieldProps> = ({
  label,
  options,
  value,
  onChange,
  required,
  error,
  placeholder = 'Select...',
  className = '',
}) => {
  return (
    <FormField label={label} required={required} error={error} className={className}>
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className={`w-full px-3 py-2 border rounded-md focus:ring-2 focus:ring-brand-500 focus:border-brand-500 ${
          error ? 'border-red-300' : 'border-gray-300'
        }`}
      >
        <option value="">{placeholder}</option>
        {options.map((opt) => (
          <option key={opt.value} value={opt.value} disabled={opt.disabled}>
            {opt.label}
          </option>
        ))}
      </select>
    </FormField>
  );
};

interface TextFieldProps {
  label: string;
  value: string;
  onChange: (value: string) => void;
  type?: 'text' | 'email' | 'password' | 'number' | 'tel' | 'url';
  placeholder?: string;
  required?: boolean;
  error?: string;
  success?: string;
  info?: string;
  disabled?: boolean;
  maxLength?: number;
  minLength?: number;
  pattern?: string;
  className?: string;
}

/**
 * TextField - Standardized text input
 * 
 * @example
 * <TextField
 *   label="Batch Number"
 *   value={form.batch_number}
 *   onChange={(val) => setForm({...form, batch_number: val})}
 *   placeholder="BATCH-2026-001"
 *   required
 *   maxLength={20}
 * />
 */
export const TextField: React.FC<TextFieldProps> = ({
  label,
  value,
  onChange,
  type = 'text',
  placeholder,
  required,
  error,
  success,
  info,
  disabled,
  maxLength,
  minLength,
  pattern,
  className = '',
}) => {
  return (
    <FormField 
      label={label} 
      required={required} 
      error={error}
      success={success}
      info={info}
      className={className}
    >
      <input
        type={type}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        disabled={disabled}
        maxLength={maxLength}
        minLength={minLength}
        pattern={pattern}
        className={`w-full px-3 py-2 border rounded-md focus:ring-2 focus:ring-brand-500 focus:border-brand-500 disabled:bg-gray-100 disabled:cursor-not-allowed ${
          error ? 'border-red-300' : 'border-gray-300'
        }`}
      />
    </FormField>
  );
};

interface TextAreaFieldProps {
  label: string;
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  required?: boolean;
  error?: string;
  rows?: number;
  maxLength?: number;
  className?: string;
}

/**
 * TextAreaField - Standardized textarea input
 * 
 * @example
 * <TextAreaField
 *   label="Notes"
 *   value={form.notes}
 *   onChange={(val) => setForm({...form, notes: val})}
 *   rows={4}
 *   maxLength={500}
 * />
 */
export const TextAreaField: React.FC<TextAreaFieldProps> = ({
  label,
  value,
  onChange,
  placeholder,
  required,
  error,
  rows = 3,
  maxLength,
  className = '',
}) => {
  return (
    <FormField label={label} required={required} error={error} className={className}>
      <textarea
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        rows={rows}
        maxLength={maxLength}
        className={`w-full px-3 py-2 border rounded-md focus:ring-2 focus:ring-brand-500 focus:border-brand-500 resize-none ${
          error ? 'border-red-300' : 'border-gray-300'
        }`}
      />
      {maxLength && (
        <div className="text-xs text-gray-500 text-right">
          {value.length}/{maxLength}
        </div>
      )}
    </FormField>
  );
};
