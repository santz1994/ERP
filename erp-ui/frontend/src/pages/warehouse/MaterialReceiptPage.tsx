import React, { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Save, Package, AlertTriangle, CheckCircle, XCircle } from 'lucide-react'
import { api } from '@/api'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Select } from '@/components/ui/select'
import { Alert } from '@/components/ui/alert'
import { formatNumber, cn } from '@/lib/utils'
import toast from 'react-hot-toast'

const materialReceiptSchema = z.object({
  po_id: z.number(),
  material_id: z.number(),
  receipt_date: z.string(),
  received_qty: z.number().min(0),
  uom: z.string(),
  supplier_name: z.string(),
  notes: z.string().optional()
})

type MaterialReceiptForm = z.infer<typeof materialReceiptSchema>

const MaterialReceiptPage: React.FC = () => {
  const [selectedPO, setSelectedPO] = useState<number | null>(null)
  const queryClient = useQueryClient()

  const { data: pendingPOs = [] } = useQuery({
    queryKey: ['pending-pos'],
    queryFn: async () => {
      const response = await api.purchasing.getPOList({ status: 'APPROVED' })
      return response.data
    }
  })

  const { data: poDetail } = useQuery({
    queryKey: ['po-detail', selectedPO],
    enabled: !!selectedPO,
    queryFn: async () => {
      const response = await api.purchasing.getPODetail(selectedPO!)
      return response.data
    }
  })

  const { register, handleSubmit, reset, watch, setValue, formState: { errors } } = useForm<MaterialReceiptForm>({
    resolver: zodResolver(materialReceiptSchema),
    defaultValues: {
      receipt_date: new Date().toISOString().split('T')[0],
      received_qty: 0
    }
  })

  const receivedQty = watch('received_qty') || 0
  const [selectedMaterial, setSelectedMaterial] = useState<any>(null)

  const submitMutation = useMutation({
    mutationFn: async (data: MaterialReceiptForm) => {
      return await api.warehouse.createMaterialReceipt(data)
    },
    onSuccess: () => {
      toast.success('Material receipt created successfully')
      queryClient.invalidateQueries({ queryKey: ['pending-pos'] })
      reset()
    },
    onError: () => {
      toast.error('Failed to create material receipt')
    }
  })

  const onSubmit = (data: MaterialReceiptForm) => {
    submitMutation.mutate({ ...data, po_id: selectedPO! })
  }

  // Calculate variance
  const variance = selectedMaterial 
    ? ((receivedQty - selectedMaterial.ordered_qty) / selectedMaterial.ordered_qty) * 100 
    : 0

  const getVarianceStatus = () => {
    const absVariance = Math.abs(variance)
    if (absVariance <= 5) return { level: 'ACCEPTABLE', color: 'text-green-600', icon: CheckCircle, action: 'Auto-Accept' }
    if (absVariance <= 10) return { level: 'WARNING', color: 'text-yellow-600', icon: AlertTriangle, action: 'Require Approval' }
    return { level: 'CRITICAL', color: 'text-red-600', icon: XCircle, action: 'Block Receipt' }
  }

  const varianceStatus = getVarianceStatus()
  const VarianceIcon = varianceStatus.icon

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Material Receipt</h1>
          <p className="text-gray-500 mt-1">Record incoming materials with 3-step variance validation</p>
        </div>
      </div>

      {/* Variance Guide */}
      <Card variant="bordered" className="p-4 bg-blue-50 border-blue-200">
        <h3 className="text-sm font-semibold text-blue-900 mb-2">Variance Validation Rules</h3>
        <div className="grid grid-cols-3 gap-4 text-xs">
          <div className="flex items-center gap-2">
            <CheckCircle className="w-4 h-4 text-green-600" />
            <span className="text-green-700">≤5%: Auto-Accept</span>
          </div>
          <div className="flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 text-yellow-600" />
            <span className="text-yellow-700">5-10%: Require Approval</span>
          </div>
          <div className="flex items-center gap-2">
            <XCircle className="w-4 h-4 text-red-600" />
            <span className="text-red-700">&gt;10%: Block Receipt</span>
          </div>
        </div>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-1 space-y-4">
          <Card variant="bordered" className="p-4">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Select PO</h3>
            <div className="space-y-2">
              {pendingPOs.length === 0 ? (
                <p className="text-sm text-gray-500 text-center py-4">No pending POs</p>
              ) : (
                pendingPOs.map((po: any) => (
                  <div
                    key={po.id}
                    onClick={() => setSelectedPO(po.id)}
                    className={cn(
                      'p-3 border rounded-lg cursor-pointer transition-all',
                      selectedPO === po.id ? 'border-blue-500 bg-blue-50' : 'border-gray-200'
                    )}
                  >
                    <p className="text-sm font-semibold">{po.po_number}</p>
                    <p className="text-xs text-gray-600 mt-1">{po.supplier_name}</p>
                    <Badge variant="outline" className="text-xs mt-2">{po.po_type}</Badge>
                  </div>
                ))
              )}
            </div>
          </Card>
        </div>

        <div className="lg:col-span-2 space-y-4">
          {!selectedPO ? (
            <Card variant="bordered" className="p-12 text-center">
              <Package className="w-16 h-16 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-gray-900 mb-2">No PO Selected</h3>
            </Card>
          ) : (
            <>
              <Card variant="bordered" className="p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Material Receipt Entry</h3>
                <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
                  <div>
                    <Label>Receipt Date</Label>
                    <Input
                      type="date"
                      {...register('receipt_date')}
                    />
                  </div>

                  <div>
                    <Label>Select Material</Label>
                    <Select
                      value={selectedMaterial?.id || ''}
                      onValueChange={(value) => {
                        const material = poDetail?.lines.find((l: any) => l.id == value)
                        setSelectedMaterial(material)
                        setValue('material_id', parseInt(value))
                        setValue('uom', material?.uom)
                        setValue('supplier_name', poDetail?.supplier_name)
                      }}
                    >
                      <option value="">Select material...</option>
                      {poDetail?.lines?.map((line: any) => (
                        <option key={line.id} value={line.id}>
                          {line.material_code} - {line.material_name} ({line.ordered_qty} {line.uom})
                        </option>
                      ))}
                    </Select>
                  </div>

                  {selectedMaterial && (
                    <>
                      <div className="p-4 bg-gray-50 rounded-lg">
                        <div className="grid grid-cols-2 gap-4">
                          <div>
                            <p className="text-xs text-gray-600">Ordered Qty</p>
                            <p className="text-lg font-semibold text-gray-900">
                              {formatNumber(selectedMaterial.ordered_qty)} {selectedMaterial.uom}
                            </p>
                          </div>
                          <div>
                            <p className="text-xs text-gray-600">Supplier</p>
                            <p className="text-sm font-medium text-gray-900">{poDetail?.supplier_name}</p>
                          </div>
                        </div>
                      </div>

                      <div>
                        <Label>Received Quantity</Label>
                        <Input
                          type="number"
                          step="0.01"
                          {...register('received_qty', { valueAsNumber: true })}
                          min="0"
                          placeholder="0"
                        />
                      </div>

                      {receivedQty > 0 && (
                        <Alert variant={variance > 10 || variance < -10 ? 'destructive' : 'default'}>
                          <div className="flex items-start gap-3">
                            <VarianceIcon className={cn('w-5 h-5 mt-0.5', varianceStatus.color)} />
                            <div className="flex-1">
                              <p className="text-sm font-semibold">Variance: {variance.toFixed(2)}%</p>
                              <p className="text-xs mt-1">
                                {variance > 0 ? 'Over Receipt' : 'Under Receipt'} by {Math.abs(receivedQty - selectedMaterial.ordered_qty).toFixed(2)} {selectedMaterial.uom}
                              </p>
                              <p className="text-xs mt-2 font-semibold">{varianceStatus.action}</p>
                            </div>
                          </div>
                        </Alert>
                      )}

                      <div>
                        <Label>Notes</Label>
                        <Textarea {...register('notes')} rows={2} placeholder="Any remarks..." />
                      </div>

                      <Button
                        type="submit"
                        variant="primary"
                        className="w-full"
                        disabled={submitMutation.isPending || Math.abs(variance) > 10}
                      >
                        <Save className="w-4 h-4 mr-2" />
                        {Math.abs(variance) > 10 
                          ? 'Receipt Blocked (Variance >10%)' 
                          : submitMutation.isPending 
                            ? 'Saving...' 
                            : 'Confirm Receipt'
                        }
                      </Button>
                    </>
                  )}
                </form>
              </Card>
            </>
          )}
        </div>
      </div>
    </div>
  )
}

export default MaterialReceiptPage
