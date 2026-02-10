/**
 * PO Create Modal Component (Simplified Version)
 * Essential features from CreatePOPage adapted for modal UX
 * 
 * Features Included:
 * - Basic PO information (IKEA number, type, dates)
 * - MANUAL material entry mode
 * - Supplier per material
 * - Price calculation
 * 
 * Features for Future Enhancement:
 * - AUTO mode with BOM explosion
 * - PO Reference system (PO KAIN → LABEL)
 * - Material type filtering
 * - Week & Destination for PO LABEL
 */

import React, { useEffect } from 'react';
import { useForm, useFieldArray, Controller } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import toast from 'react-hot-toast';
import { X, Plus, Trash2, Package, Calculator } from 'lucide-react';
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

// Simplified Schema
const poMaterialSchema = z.object({
  material_code: z.string().min(1, 'Material code required'),
  material_name: z.string().min(1, 'Material name required'),
  material_type: z.enum(['RAW', 'BAHAN_PENOLONG', 'WIP']),
  supplier_id: z.number().min(1, 'Supplier required'),
  quantity: z.number().min(1, 'Quantity must be > 0'),
  uom: z.string().min(1, 'UOM required'),
  unit_price: z.number().min(0, 'Price must be >= 0'),
  total_price: z.number(),
  description: z.string().optional(),
});

const poSchema = z.object({
  po_ikea_number: z.string().optional(),
  po_type: z.enum(['KAIN', 'LABEL', 'ACCESSORIES']),
  po_date: z.string().min(1, 'PO date required'),
  expected_delivery_date: z.string().min(1, 'Delivery date required'),
  notes: z.string().optional(),
  materials: z.array(poMaterialSchema).min(1, 'Add at least one material'),
});

type POFormData = z.infer<typeof poSchema>;

interface Supplier {
  id: number;
  name: string;
  code: string;
}

interface POCreateModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess?: (poId: number) => void;
}

export default function POCreateModal({ isOpen, onClose, onSuccess }: POCreateModalProps) {
  const queryClient = useQueryClient();

  const {
    control,
    register,
    handleSubmit,
    watch,
    setValue,
    reset,
    formState: { errors },
  } = useForm<POFormData>({
    resolver: zodResolver(poSchema),
    defaultValues: {
      po_type: 'KAIN',
      po_date: new Date().toISOString().split('T')[0],
      materials: [],
    },
  });

  const { fields, append, remove } = useFieldArray({
    control,
    name: 'materials',
  });

  const watchMaterials = watch('materials');
  const watchPOType = watch('po_type');

  // Fetch suppliers
  const { data: suppliers = [] } = useQuery<Supplier[]>({
    queryKey: ['suppliers'],
    queryFn: async () => {
      const response = await apiClient.get('/purchasing/suppliers');
      return response.data;
    },
    enabled: isOpen,
  });

  // Calculate line total when quantity or price changes
  useEffect(() => {
    watchMaterials?.forEach((material, index) => {
      const total = (material.quantity || 0) * (material.unit_price || 0);
      if (material.total_price !== total) {
        setValue(`materials.${index}.total_price`, total);
      }
    });
  }, [watchMaterials, setValue]);

  // Reset form when modal closes
  useEffect(() => {
    if (!isOpen) {
      reset();
    }
  }, [isOpen, reset]);

  // Create PO mutation
  const createPOMutation = useMutation({
    mutationFn: async (data: POFormData) => {
      const response = await apiClient.post('/purchasing/po', data);
      return response.data;
    },
    onSuccess: (data) => {
      toast.success(`PO ${data.po_number || 'created'} successfully!`);
      queryClient.invalidateQueries({ queryKey: ['purchase-orders'] });
      reset();
      onSuccess?.(data.id);
      onClose();
    },
    onError: () => {
      toast.error('Failed to create PO. Please try again.');
    },
  });

  const addMaterialLine = () => {
    append({
      material_code: '',
      material_name: '',
      material_type: 'RAW',
      supplier_id: 0,
      quantity: 0,
      uom: 'PCS',
      unit_price: 0,
      total_price: 0,
      description: '',
    });
  };

  const onSubmit = (data: POFormData) => {
    createPOMutation.mutate(data);
  };

  // Calculate grand total
  const grandTotal = watchMaterials?.reduce(
    (sum, material) => sum + (material.total_price || 0),
    0
  ) || 0;

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-[9999] p-4 overflow-y-auto">
      <div className="bg-white rounded-lg shadow-2xl w-full max-w-7xl my-8">
        {/* Modal Header */}
        <div className="flex items-center justify-between p-6 border-b sticky top-0 bg-white rounded-t-lg z-10">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Create Purchase Order</h2>
            <p className="text-gray-600 text-sm mt-1">
              Add materials and suppliers for procurement
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
          {/* Header Information */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg flex items-center gap-2">
                <Package className="w-5 h-5" />
                Header Information
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="po_ikea_number">No PO IKEA (ECIS) <span className="text-gray-500">(Optional)</span></Label>
                  <Input
                    id="po_ikea_number"
                    {...register('po_ikea_number')}
                    placeholder="e.g., ECIS-2026-001234"
                  />
                </div>

                <div>
                  <Label htmlFor="po_type">PO Type *</Label>
                  <Controller
                    name="po_type"
                    control={control}
                    render={({ field }) => (
                      <Select onValueChange={field.onChange} value={field.value}>
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="KAIN">KAIN (Fabric) - TRIGGER 1 🔑</SelectItem>
                          <SelectItem value="LABEL">LABEL - TRIGGER 2 🔑</SelectItem>
                          <SelectItem value="ACCESSORIES">ACCESSORIES</SelectItem>
                        </SelectContent>
                      </Select>
                    )}
                  />
                  {watchPOType === 'KAIN' && (
                    <p className="text-xs text-blue-600 mt-1">
                      🔑 TRIGGER 1: Enables Cutting & Embroidery
                    </p>
                  )}
                  {watchPOType === 'LABEL' && (
                    <p className="text-xs text-purple-600 mt-1">
                      🔑 TRIGGER 2: Full MO Release
                    </p>
                  )}
                </div>

                <div>
                  <Label htmlFor="po_date">PO Date *</Label>
                  <Input
                    id="po_date"
                    type="date"
                    {...register('po_date')}
                  />
                  {errors.po_date && (
                    <p className="text-sm text-red-600 mt-1">{errors.po_date.message}</p>
                  )}
                </div>

                <div>
                  <Label htmlFor="expected_delivery_date">Expected Delivery *</Label>
                  <Input
                    id="expected_delivery_date"
                    type="date"
                    {...register('expected_delivery_date')}
                  />
                  {errors.expected_delivery_date && (
                    <p className="text-sm text-red-600 mt-1">{errors.expected_delivery_date.message}</p>
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

          {/* Material List */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg flex items-center justify-between">
                <span>Material List ({fields.length} items)</span>
                <Button
                  type="button"
                  onClick={addMaterialLine}
                  size="sm"
                  variant="primary"
                >
                  <Plus className="w-4 h-4 mr-1" />
                  Add Material
                </Button>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {fields.length === 0 && (
                <div className="text-center py-8 text-gray-500">
                  <Package className="w-12 h-12 mx-auto mb-2 opacity-50" />
                  <p>No materials added yet. Click "Add Material" to start.</p>
                </div>
              )}

              {fields.map((field, index) => (
                <div
                  key={field.id}
                  className="p-4 border border-gray-200 rounded-lg bg-gray-50 space-y-3"
                >
                  <div className="flex items-center justify-between mb-2">
                    <h5 className="font-semibold text-gray-700">Material #{index + 1}</h5>
                    <button
                      type="button"
                      onClick={() => remove(index)}
                      className="text-red-600 hover:text-red-800"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
                    <div>
                      <Label className="text-xs">Material Code *</Label>
                      <Input
                        {...register(`materials.${index}.material_code`)}
                        placeholder="e.g., IKHR504"
                        className="text-sm"
                      />
                      {errors.materials?.[index]?.material_code && (
                        <p className="text-xs text-red-600 mt-1">
                          {errors.materials[index]?.material_code?.message}
                        </p>
                      )}
                    </div>

                    <div className="md:col-span-2">
                      <Label className="text-xs">Material Name *</Label>
                      <Input
                        {...register(`materials.${index}.material_name`)}
                        placeholder="e.g., KOHAIR 7MM D.BROWN"
                        className="text-sm"
                      />
                    </div>

                    <div>
                      <Label className="text-xs">Type</Label>
                      <Controller
                        name={`materials.${index}.material_type`}
                        control={control}
                        render={({ field }) => (
                          <Select onValueChange={field.onChange} value={field.value}>
                            <SelectTrigger className="text-sm">
                              <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="RAW">RAW</SelectItem>
                              <SelectItem value="BAHAN_PENOLONG">BAHAN PENOLONG</SelectItem>
                              <SelectItem value="WIP">WIP</SelectItem>
                            </SelectContent>
                          </Select>
                        )}
                      />
                    </div>

                    <div className="md:col-span-2">
                      <Label className="text-xs text-red-600">Supplier * (Per Material)</Label>
                      <Controller
                        name={`materials.${index}.supplier_id`}
                        control={control}
                        render={({ field }) => (
                          <Select
                            onValueChange={(value) => field.onChange(parseInt(value))}
                            value={field.value?.toString()}
                          >
                            <SelectTrigger className="text-sm">
                              <SelectValue placeholder="Select supplier" />
                            </SelectTrigger>
                            <SelectContent>
                              {suppliers.map((supplier) => (
                                <SelectItem key={supplier.id} value={supplier.id.toString()}>
                                  {supplier.name}
                                </SelectItem>
                              ))}
                            </SelectContent>
                          </Select>
                        )}
                      />
                    </div>

                    <div>
                      <Label className="text-xs">Quantity *</Label>
                      <Input
                        type="number"
                        {...register(`materials.${index}.quantity`, { valueAsNumber: true })}
                        className="text-sm"
                        min="0"
                      />
                    </div>

                    <div>
                      <Label className="text-xs">UOM *</Label>
                      <Input
                        {...register(`materials.${index}.uom`)}
                        placeholder="PCS/KG/M"
                        className="text-sm"
                      />
                    </div>

                    <div>
                      <Label className="text-xs">Unit Price *</Label>
                      <Input
                        type="number"
                        {...register(`materials.${index}.unit_price`, { valueAsNumber: true })}
                        className="text-sm"
                        min="0"
                        step="0.01"
                      />
                    </div>

                    <div>
                      <Label className="text-xs">Total Price</Label>
                      <div className="flex items-center h-9 px-3 bg-gray-100 border rounded-md text-sm font-medium">
                        {watchMaterials?.[index]?.total_price?.toLocaleString('id-ID', {
                          style: 'currency',
                          currency: 'IDR',
                        }) || 'Rp 0'}
                      </div>
                    </div>
                  </div>

                  <div>
                    <Label className="text-xs">Description (Optional)</Label>
                    <Input
                      {...register(`materials.${index}.description`)}
                      placeholder="Notes about this material..."
                      className="text-sm"
                    />
                  </div>
                </div>
              ))}

              {fields.length > 0 && (
                <div className="flex items-center justify-between pt-4 border-t">
                  <span className="text-lg font-semibold flex items-center gap-2">
                    <Calculator className="w-5 h-5" />
                    Grand Total:
                  </span>
                  <span className="text-2xl font-bold text-green-600">
                    {grandTotal.toLocaleString('id-ID', {
                      style: 'currency',
                      currency: 'IDR',
                    })}
                  </span>
                </div>
              )}

              {errors.materials && typeof errors.materials === 'object' && !Array.isArray(errors.materials) && (
                <p className="text-sm text-red-600 mt-2">{errors.materials.message}</p>
              )}
            </CardContent>
          </Card>
        </form>

        {/* Modal Footer */}
        <div className="flex items-center justify-end gap-3 p-6 border-t bg-gray-50 rounded-b-lg sticky bottom-0">
          <Button
            type="button"
            variant="secondary"
            onClick={onClose}
            disabled={createPOMutation.isPending}
          >
            Cancel
          </Button>
          <Button
            type="submit"
            variant="primary"
            onClick={handleSubmit(onSubmit)}
            disabled={fields.length === 0 || createPOMutation.isPending}
            isLoading={createPOMutation.isPending}
          >
            {createPOMutation.isPending ? 'Creating...' : 'Create PO'}
          </Button>
        </div>
      </div>
    </div>
  );
}
