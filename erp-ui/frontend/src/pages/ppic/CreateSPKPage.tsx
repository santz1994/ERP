import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useForm, Controller } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useMutation, useQuery } from '@tanstack/react-query';
import { 
  FileText, 
  ArrowLeft, 
  Save, 
  AlertCircle,
  Calculator,
  Plus,
  Trash2
} from 'lucide-react';
import { apiClient } from '@/api';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Alert, AlertDescription } from '@/components/ui/alert';

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

const CreateSPKPage: React.FC = () => {
  const navigate = useNavigate();
  const [selectedMO, setSelectedMO] = useState<MO | null>(null);
  const [materials, setMaterials] = useState<Material[]>([]);

  const {
    control,
    register,
    handleSubmit,
    watch,
    setValue,
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
  });

  // Fetch MO details and BOM when MO is selected
  const { data: moDetails } = useQuery({
    queryKey: ['mo-details', watchMOId],
    queryFn: async () => {
      const response = await apiClient.get(`/production/mo/${watchMOId}`);
      return response.data;
    },
    enabled: !!watchMOId,
  });

  // Fetch materials for selected MO
  const { data: bomMaterials = [] } = useQuery<Material[]>({
    queryKey: ['bom-materials', watchMOId],
    queryFn: async () => {
      const response = await apiClient.get(`/bom/materials/${watchMOId}`);
      return response.data;
    },
    enabled: !!watchMOId,
  });

  // Calculate materials when MO or target qty changes
  React.useEffect(() => {
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

  // Auto-calculate buffer target when department changes
  React.useEffect(() => {
    if (watchDepartment && selectedMO) {
      const dept = DEPARTMENTS.find(d => d.value === watchDepartment);
      if (dept) {
        const bufferQty = Math.ceil(selectedMO.target_qty * (1 + dept.buffer / 100));
        setValue('target_qty', bufferQty);
      }
    }
  }, [watchDepartment, selectedMO, setValue]);

  // Handle MO selection
  const handleMOChange = (moId: string) => {
    const mo = mos.find(m => m.id === parseInt(moId));
    if (mo) {
      setSelectedMO(mo);
      setValue('mo_id', mo.id);
    }
  };

  // Create SPK mutation
  const createSPKMutation = useMutation({
    mutationFn: async (data: SPKFormData) => {
      const response = await apiClient.post('/production/spk', data);
      return response.data;
    },
    onSuccess: (data) => {
      navigate(`/ppic/spk/${data.id}`);
    },
  });

  const onSubmit = (data: SPKFormData) => {
    createSPKMutation.mutate(data);
  };

  const getMaterialStatus = (material: Material) => {
    const requiredQty = material.required_qty_per_pc * watchTargetQty;
    const availability = (material.stock_qty / requiredQty) * 100;

    if (availability >= 100) return { color: 'text-green-600', label: 'Available' };
    if (availability >= 70) return { color: 'text-yellow-600', label: 'Low Stock' };
    if (availability >= 30) return { color: 'text-orange-600', label: 'Critical' };
    return { color: 'text-red-600', label: 'Insufficient' };
  };

  const canSubmit = materials.length > 0 && materials.every(m => {
    const requiredQty = m.required_qty_per_pc * watchTargetQty;
    return m.stock_qty >= requiredQty;
  });

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center gap-4">
        <Button
          variant="outline"
          onClick={() => navigate('/ppic/spk')}
        >
          <ArrowLeft className="w-4 h-4 mr-2" />
          Back
        </Button>
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Create SPK</h1>
          <p className="text-gray-500 mt-1">Generate work order for production department</p>
        </div>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
        {/* Basic Information */}
        <Card>
          <CardHeader>
            <CardTitle>Basic Information</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* MO Selection */}
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

              {/* Department Selection */}
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

            {/* MO Details */}
            {selectedMO && (
              <Alert>
                <AlertCircle className="h-4 w-4" />
                <AlertDescription>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-sm">
                    <div>
                      <span className="font-medium">Article:</span> {selectedMO.article_code}
                    </div>
                    <div>
                      <span className="font-medium">MO Target:</span> {selectedMO.target_qty.toLocaleString()} pcs
                    </div>
                    <div>
                      <span className="font-medium">PO Label:</span> {selectedMO.po_label_number}
                    </div>
                    <div>
                      <span className="font-medium">Status:</span> {selectedMO.status}
                    </div>
                  </div>
                </AlertDescription>
              </Alert>
            )}

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Target Quantity */}
              <div>
                <Label htmlFor="target_qty">Target Quantity (pcs) *</Label>
                <div className="relative">
                  <Input
                    id="target_qty"
                    type="number"
                    {...register('target_qty', { valueAsNumber: true })}
                    placeholder="Enter target quantity"
                  />
                  <Calculator className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                </div>
                {errors.target_qty && (
                  <p className="text-sm text-red-600 mt-1">{errors.target_qty.message}</p>
                )}
                {selectedMO && watchTargetQty > selectedMO.target_qty * 1.15 && (
                  <p className="text-sm text-orange-600 mt-1">
                    ⚠️ Buffer exceeds 15% - requires approval
                  </p>
                )}
              </div>

              {/* Start Date */}
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

              {/* Target Date */}
              <div>
                <Label htmlFor="target_date">Target Completion Date *</Label>
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

            {/* Notes */}
            <div>
              <Label htmlFor="notes">Notes (Optional)</Label>
              <Textarea
                id="notes"
                {...register('notes')}
                placeholder="Add any special instructions or notes..."
                rows={3}
              />
            </div>
          </CardContent>
        </Card>

        {/* Material Allocation */}
        {materials.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle>Material Allocation (BOM Explosion)</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-gray-50 border-b">
                    <tr>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Material Code</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Material Name</th>
                      <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Per Piece</th>
                      <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Required</th>
                      <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Available</th>
                      <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase">Status</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200">
                    {materials.map((material, index) => {
                      const status = getMaterialStatus(material);
                      const requiredQty = material.required_qty_per_pc * watchTargetQty;
                      
                      return (
                        <tr key={material.id}>
                          <td className="px-4 py-3 font-medium text-gray-900">
                            {material.material_code}
                          </td>
                          <td className="px-4 py-3 text-gray-700">
                            {material.material_name}
                          </td>
                          <td className="px-4 py-3 text-right text-gray-700">
                            {material.required_qty_per_pc} {material.unit}
                          </td>
                          <td className="px-4 py-3 text-right font-medium text-gray-900">
                            {requiredQty.toLocaleString()} {material.unit}
                          </td>
                          <td className="px-4 py-3 text-right text-gray-700">
                            {material.stock_qty.toLocaleString()} {material.unit}
                          </td>
                          <td className="px-4 py-3 text-center">
                            <span className={`font-medium ${status.color}`}>
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
                    Insufficient materials available. Please ensure all materials are in stock before creating SPK.
                  </AlertDescription>
                </Alert>
              )}
            </CardContent>
          </Card>
        )}

        {/* Actions */}
        <Card>
          <CardContent className="pt-6">
            <div className="flex justify-end gap-4">
              <Button
                type="button"
                variant="outline"
                onClick={() => navigate('/ppic/spk')}
              >
                Cancel
              </Button>
              <Button
                type="submit"
                disabled={createSPKMutation.isPending || !canSubmit}
                className="gap-2"
              >
                {createSPKMutation.isPending ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                    Creating...
                  </>
                ) : (
                  <>
                    <Save className="w-4 h-4" />
                    Create SPK
                  </>
                )}
              </Button>
            </div>
          </CardContent>
        </Card>

        {createSPKMutation.isError && (
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>
              Failed to create SPK. Please try again.
            </AlertDescription>
          </Alert>
        )}
      </form>
    </div>
  );
};

export default CreateSPKPage;
