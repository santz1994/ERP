/**
 * SPK Create Modal Component
 * Extracted from CreateSPKPage for modal-based UX
 * 
 * Features:
 * - Select MO and Department
 * - Auto-calculate buffer target
 * - BOM explosion with material availability check
 * - Material shortage warning
 */

import React, { useState, useEffect } from 'react';
import { useForm, Controller } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import toast from 'react-hot-toast';
import { 
  X,
  AlertCircle,
  Calculator,
  CheckCircle,
  XCircle
} from 'lucide-react';
import { apiClient } from '@/api';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Input } from '../ui/input';
import { Button } from '../ui/button';
import { Label } from '../ui/label';
import { Textarea } from '../ui/textarea';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '../ui/select';
import { Alert, AlertDescription } from '../ui/alert';

const spkSchema = z.object({
  mo_id: z.number().min(1, 'Please select an MO'),
  department: z.string().min(1, 'Please select a department'),
  target_qty: z.number().min(1, 'Target quantity must be greater than 0'),
  start_date: z.string().min(1, 'Start date is required'),
  target_date: z.string().min(1, 'Target date is required'),
  notes: z.string().optional(),
  materials: z.array(z.object({
    material_id: z.number(),
    material_code: z.string(),
    material_name: z.string(),
    required_qty: z.number(),
    allocated_qty: z.number(),
    unit: z.string(),
  })).optional(),
});

type SPKFormData = z.infer<typeof spkSchema>;

interface MO {
  id: number;
  mo_number: string;
  article_code: string;
  article_name: string;
  target_qty: number;
  status: string;
  po_label_number: string;
}

interface Material {
  id: number;
  material_code: string;
  material_name: string;
  stock_qty: number;
  unit: string;
  required_qty_per_pc: number;
}

const DEPARTMENTS = [
  { value: 'CUTTING', label: 'Cutting', buffer: 10 },
  { value: 'EMBROIDERY', label: 'Embroidery', buffer: 5 },
  { value: 'SEWING', label: 'Sewing', buffer: 15 },
  { value: 'FINISHING', label: 'Finishing', buffer: 10 },
  { value: 'PACKING', label: 'Packing', buffer: 0 },
];

interface SPKCreateModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess?: (spkId: number) => void;
}

export default function SPKCreateModal({ isOpen, onClose, onSuccess }: SPKCreateModalProps) {
  const queryClient = useQueryClient();
  const [selectedMO, setSelectedMO] = useState<MO | null>(null);
  const [materials, setMaterials] = useState<Material[]>([]);

  const {
    control,
    register,
    handleSubmit,
    watch,
    setValue,
    reset,
    formState: { errors },
  } = useForm<SPKFormData>({
    resolver: zodResolver(spkSchema),
    defaultValues: {
      target_qty: 0,
      notes: '',
      materials: [],
    },
  });

  const watchMOId = watch('mo_id');
  const watchDepartment = watch('department');
  const watchTargetQty = watch('target_qty');

  // Fetch active MOs
  const { data: mos = [] } = useQuery<MO[]>({
    queryKey: ['mos-active'],
    queryFn: async () => {
      const response = await apiClient.get('/production/mo?status=RELEASED');
      return response.data;
    },
    enabled: isOpen,
  });

  // Fetch materials for selected MO
  const { data: bomMaterials = [] } = useQuery<Material[]>({
    queryKey: ['bom-materials', watchMOId],
    queryFn: async () => {
      const response = await apiClient.get(`/bom/materials/${watchMOId}`);
      return response.data;
    },
    enabled: !!watchMOId && isOpen,
  });

  // Calculate materials when MO or target qty changes
  useEffect(() => {
    if (bomMaterials.length > 0 && watchTargetQty > 0) {
      const calculatedMaterials = bomMaterials.map(material => ({
        material_id: material.id,
        material_code: material.material_code,
        material_name: material.material_name,
        required_qty: material.required_qty_per_pc * watchTargetQty,
        allocated_qty: Math.min(
          material.required_qty_per_pc * watchTargetQty,
          material.stock_qty
        ),
        unit: material.unit,
      }));
      setMaterials(calculatedMaterials as any);
      setValue('materials', calculatedMaterials);
    }
  }, [bomMaterials, watchTargetQty, setValue]);

  // Auto-calculate buffer target
  useEffect(() => {
    if (watchDepartment && selectedMO) {
      const dept = DEPARTMENTS.find(d => d.value === watchDepartment);
      if (dept) {
        const bufferQty = Math.ceil(selectedMO.target_qty * (1 + dept.buffer / 100));
        setValue('target_qty', bufferQty);
      }
    }
  }, [watchDepartment, selectedMO, setValue]);

  // Reset form when modal closes
  useEffect(() => {
    if (!isOpen) {
      reset();
      setSelectedMO(null);
      setMaterials([]);
    }
  }, [isOpen, reset]);

  // Create SPK mutation
  const createSPKMutation = useMutation({
    mutationFn: async (data: SPKFormData) => {
      const response = await apiClient.post('/production/spk', data);
      return response.data;
    },
    onSuccess: (data) => {
      toast.success(`SPK ${data.spk_number || 'created'} successfully!`);
      queryClient.invalidateQueries({ queryKey: ['spks'] });
      reset();
      setSelectedMO(null);
      onSuccess?.(data.id);
      onClose();
    },
    onError: () => {
      toast.error('Failed to create SPK. Please try again.');
    },
  });

  const handleMOChange = (moId: string) => {
    const mo = mos.find(m => m.id === parseInt(moId));
    if (mo) {
      setSelectedMO(mo);
      setValue('mo_id', mo.id);
    }
  };

  const onSubmit = (data: SPKFormData) => {
    createSPKMutation.mutate(data);
  };

  const getMaterialStatus = (material: Material) => {
    const requiredQty = material.required_qty_per_pc * (watchTargetQty || 0);
    const availability = (material.stock_qty / requiredQty) * 100;

    if (availability >= 100) return { color: 'text-green-600', label: 'Available', icon: CheckCircle };
    if (availability >= 70) return { color: 'text-yellow-600', label: 'Low Stock', icon: AlertCircle };
   return { color: 'text-red-600', label: 'Insufficient', icon: XCircle };
  };

  const canSubmit = materials.length > 0 && materials.every(m => {
    const requiredQty = m.required_qty_per_pc * (watchTargetQty || 0);
    return m.stock_qty >= requiredQty;
  });

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-[9999] p-4 overflow-y-auto">
      <div className="bg-white rounded-lg shadow-2xl w-full max-w-6xl my-8">
        {/* Modal Header */}
        <div className="flex items-center justify-between p-6 border-b sticky top-0 bg-white rounded-t-lg z-10">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Create SPK (Work Order)</h2>
            <p className="text-gray-600 text-sm mt-1">
              Generate work order with BOM explosion and material allocation
            </p>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Modal Body */}
        <form onSubmit={handleSubmit(onSubmit)} className="p-6 space-y-6 max-h-[calc(100vh-200px)] overflow-y-auto">
          {/* Basic Information */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Basic Information</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="mo_id">Manufacturing Order *</Label>
                  <Controller
                    name="mo_id"
                    control={control}
                    render={({ field }) => (
                      <Select
                        onValueChange={(value) => {
                          handleMOChange(value);
                          field.onChange(parseInt(value));
                        }}
                        value={field.value?.toString()}
                      >
                        <SelectTrigger>
                          <SelectValue placeholder="Select MO" />
                        </SelectTrigger>
                        <SelectContent>
                          {mos.map((mo) => (
                            <SelectItem key={mo.id} value={mo.id.toString()}>
                              {mo.mo_number} - {mo.article_code} ({mo.target_qty} pcs)
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    )}
                  />
                  {errors.mo_id && (
                    <p className="text-sm text-red-600 mt-1">{errors.mo_id.message}</p>
                  )}
                </div>

                <div>
                  <Label htmlFor="department">Department *</Label>
                  <Controller
                    name="department"
                    control={control}
                    render={({ field }) => (
                      <Select
                        onValueChange={field.onChange}
                        value={field.value}
                      >
                        <SelectTrigger>
                          <SelectValue placeholder="Select Department" />
                        </SelectTrigger>
                        <SelectContent>
                          {DEPARTMENTS.map((dept) => (
                            <SelectItem key={dept.value} value={dept.value}>
                              {dept.label} (+{dept.buffer}% buffer)
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    )}
                  />
                  {errors.department && (
                    <p className="text-sm text-red-600 mt-1">{errors.department.message}</p>
                  )}
                </div>
              </div>

              {selectedMO && (
                <Alert>
                  <AlertCircle className="h-4 w-4" />
                  <AlertDescription>
                    <div className="grid grid-cols-2 gap-2 text-xs">
                      <div>Article: <strong>{selectedMO.article_code}</strong></div>
                      <div>MO Target: <strong>{selectedMO.target_qty.toLocaleString()}</strong> pcs</div>
                    </div>
                  </AlertDescription>
                </Alert>
              )}

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <Label htmlFor="target_qty">Target Qty (pcs) *</Label>
                  <div className="relative">
                    <Input
                      id="target_qty"
                      type="number"
                      {...register('target_qty', { valueAsNumber: true })}
                    />
                    <Calculator className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                  </div>
                  {errors.target_qty && (
                    <p className="text-sm text-red-600 mt-1">{errors.target_qty.message}</p>
                  )}
                </div>

                <div>
                  <Label htmlFor="start_date">Start Date *</Label>
                  <Input
                    id="start_date"
                    type="date"
                    {...register('start_date')}
                  />
                  {errors.start_date && (
                    <p className="text-sm text-red-600 mt-1">{errors.start_date.message}</p>
                  )}
                </div>

                <div>
                  <Label htmlFor="target_date">Target Date *</Label>
                  <Input
                    id="target_date"
                    type="date"
                    {...register('target_date')}
                  />
                  {errors.target_date && (
                    <p className="text-sm text-red-600 mt-1">{errors.target_date.message}</p>
                  )}
                </div>
              </div>

              <div>
                <Label htmlFor="notes">Notes (Optional)</Label>
                <Textarea
                  id="notes"
                  {...register('notes')}
                  placeholder="Special instructions..."
                  rows={2}
                />
              </div>
            </CardContent>
          </Card>

          {/* Material Allocation */}
          {materials.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Material Allocation (BOM Explosion)</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead className="bg-gray-50 border-b">
                      <tr>
                        <th className="px-3 py-2 text-left text-xs font-medium text-gray-500">Code</th>
                        <th className="px-3 py-2 text-left text-xs font-medium text-gray-500">Material</th>
                        <th className="px-3 py-2 text-right text-xs font-medium text-gray-500">Required</th>
                        <th className="px-3 py-2 text-right text-xs font-medium text-gray-500">Available</th>
                        <th className="px-3 py-2 text-center text-xs font-medium text-gray-500">Status</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y">
                      {materials.map((material) => {
                        const status = getMaterialStatus(material);
                        const requiredQty = material.required_qty_per_pc * (watchTargetQty || 0);
                        const StatusIcon = status.icon;
                        
                        return (
                          <tr key={material.id}>
                            <td className="px-3 py-2 font-medium">{material.material_code}</td>
                            <td className="px-3 py-2 text-gray-700">{material.material_name}</td>
                            <td className="px-3 py-2 text-right font-medium">
                              {requiredQty.toLocaleString()} {material.unit}
                            </td>
                            <td className="px-3 py-2 text-right">
                              {material.stock_qty.toLocaleString()} {material.unit}
                            </td>
                            <td className="px-3 py-2 text-center">
                              <span className={`flex items-center justify-center gap-1 font-medium ${status.color}`}>
                                <StatusIcon className="w-4 h-4" />
                                {status.label}
                              </span>
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>

                {!canSubmit && (
                  <Alert className="mt-4" variant="destructive">
                    <AlertCircle className="h-4 w-4" />
                    <AlertDescription>
                      Insufficient materials. Please ensure stock availability before creating SPK.
                    </AlertDescription>
                  </Alert>
                )}
              </CardContent>
            </Card>
          )}
        </form>

        {/* Modal Footer */}
        <div className="flex items-center justify-end gap-3 p-6 border-t bg-gray-50 rounded-b-lg sticky bottom-0">
          <Button
            type="button"
            variant="secondary"
            onClick={onClose}
            disabled={createSPKMutation.isPending}
          >
            Cancel
          </Button>
          <Button
            type="submit"
            variant="primary"
            onClick={handleSubmit(onSubmit)}
            disabled={!canSubmit || createSPKMutation.isPending}
            isLoading={createSPKMutation.isPending}
          >
            {createSPKMutation.isPending ? 'Creating...' : 'Create SPK'}
          </Button>
        </div>
      </div>
    </div>
  );
}
