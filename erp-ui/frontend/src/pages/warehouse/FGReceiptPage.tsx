import React, { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Save, Package, Barcode, Camera, CheckCircle, XCircle, AlertTriangle } from 'lucide-react'
import { api } from '@/api'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Alert } from '@/components/ui/alert'
import { formatNumber, cn } from '@/lib/utils'
import toast from 'react-hot-toast'

const fgReceiptSchema = z.object({
  mo_id: z.number(),
  receipt_date: z.string(),
  cartons_received: z.number().min(1),
  barcode_scanned: z.string().optional(),
  location: z.string(),
  notes: z.string().optional()
})

type FGReceiptForm = z.infer<typeof fgReceiptSchema>

const FGReceiptPage: React.FC = () => {
  const [selectedMO, setSelectedMO] = useState<number | null>(null)
  const [barcodeMode, setBarcodeMode] = useState(false)
  const [scannedBarcodes, setScannedBarcodes] = useState<string[]>([])
  const queryClient = useQueryClient()

  const { data: completedMOs = [] } = useQuery({
    queryKey: ['completed-mos'],
    queryFn: async () => {
      const response = await api.ppic.getMOList({ status: 'COMPLETED', has_fg_receipt: false })
      return response.data
    }
  })

  const { data: moDetail } = useQuery({
    queryKey: ['mo-detail', selectedMO],
    enabled: !!selectedMO,
    queryFn: async () => {
      const response = await api.ppic.getMODetail(selectedMO!)
      return response.data
    }
  })

  const { register, handleSubmit, reset, watch, setValue, formState: { errors } } = useForm<FGReceiptForm>({
    resolver: zodResolver(fgReceiptSchema),
    defaultValues: {
      receipt_date: new Date().toISOString().split('T')[0],
      cartons_received: 0,
      location: 'WH-FG-01'
    }
  })

  const cartonsReceived = watch('cartons_received') || 0

  const submitMutation = useMutation({
    mutationFn: async (data: FGReceiptForm) => {
      return await api.warehouse.createFGReceipt(data)
    },
    onSuccess: () => {
      toast.success('FG receipt created successfully')
      queryClient.invalidateQueries({ queryKey: ['completed-mos'] })
      reset()
      setScannedBarcodes([])
    },
    onError: () => {
      toast.error('Failed to create FG receipt')
    }
  })

  const handleBarcodeInput = (barcode: string) => {
    if (barcode && !scannedBarcodes.includes(barcode)) {
      setScannedBarcodes([...scannedBarcodes, barcode])
      setValue('cartons_received', scannedBarcodes.length + 1)
      toast.success(`Barcode scanned: ${barcode}`)
    }
  }

  const onSubmit = (data: FGReceiptForm) => {
    // Validate against MO target
    if (moDetail) {
      const expectedCartons = Math.ceil(moDetail.target_qty / 60) // 60 pcs per carton
      const variance = Math.abs(cartonsReceived - expectedCartons)
      
      if (variance > expectedCartons * 0.1) {
        toast.error(`Carton count variance too high. Expected: ${expectedCartons}, Received: ${cartonsReceived}`)
        return
      }
    }

    submitMutation.mutate({ ...data, mo_id: selectedMO! })
  }

  // Calculate expected vs actual
  const expectedCartons = moDetail ? Math.ceil(moDetail.target_qty / 60) : 0
  const expectedPcs = moDetail?.target_qty || 0
  const actualPcs = cartonsReceived * 60
  const variance = expectedPcs > 0 ? ((actualPcs - expectedPcs) / expectedPcs) * 100 : 0

  const getVarianceStatus = () => {
    const absVariance = Math.abs(variance)
    if (absVariance <= 5) return { icon: CheckCircle, color: 'text-green-600', label: 'MATCH' }
    if (absVariance <= 10) return { icon: AlertTriangle, color: 'text-yellow-600', label: 'WARNING' }
    return { icon: XCircle, color: 'text-red-600', label: 'MISMATCH' }
  }

  const varianceStatus = getVarianceStatus()
  const VarianceIcon = varianceStatus.icon

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Finished Goods Receipt</h1>
          <p className="text-gray-500 mt-1">Receive packed FG from Production with barcode scanning</p>
        </div>
      </div>

      {/* Barcode Mode Toggle */}
      <Card variant="bordered" className="p-4 bg-purple-50 border-purple-200">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-sm font-semibold text-purple-900">📱 Barcode Scanning Mode</h3>
            <p className="text-xs text-purple-700 mt-1">Use mobile app or handheld scanner for quick receipt</p>
          </div>
          <Button
            variant={barcodeMode ? 'primary' : 'outline'}
            onClick={() => setBarcodeMode(!barcodeMode)}
          >
            {barcodeMode ? (
              <>
                <Camera className="w-4 h-4 mr-2" />
                Scanner Active
              </>
            ) : (
              <>
                <Barcode className="w-4 h-4 mr-2" />
                Enable Scanner
              </>
            )}
          </Button>
        </div>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-1 space-y-4">
          <Card variant="bordered" className="p-4">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Select MO</h3>
            <div className="space-y-2">
              {completedMOs.length === 0 ? (
                <p className="text-sm text-gray-500 text-center py-4">No completed MOs pending FG receipt</p>
              ) : (
                completedMOs.map((mo: any) => (
                  <div
                    key={mo.id}
                    onClick={() => setSelectedMO(mo.id)}
                    className={cn(
                      'p-3 border rounded-lg cursor-pointer transition-all',
                      selectedMO === mo.id ? 'border-blue-500 bg-blue-50' : 'border-gray-200'
                    )}
                  >
                    <div className="flex items-start justify-between">
                      <div>
                        <p className="text-sm font-semibold">{mo.mo_number}</p>
                        <p className="text-xs text-gray-600 mt-1">{mo.article_name}</p>
                        <p className="text-xs text-gray-500 mt-1">Target: {formatNumber(mo.target_qty)} pcs</p>
                        {mo.week && mo.destination && (
                          <div className="flex gap-1 mt-2">
                            <Badge variant="outline" className="text-xs">W{mo.week}</Badge>
                            <Badge variant="outline" className="text-xs">{mo.destination}</Badge>
                          </div>
                        )}
                      </div>
                      {mo.priority === 'URGENT' && (
                        <Badge variant="destructive" className="text-xs">Urgent</Badge>
                      )}
                    </div>
                  </div>
                ))
              )}
            </div>
          </Card>
        </div>

        <div className="lg:col-span-2 space-y-4">
          {!selectedMO ? (
            <Card variant="bordered" className="p-12 text-center">
              <Package className="w-16 h-16 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-gray-900 mb-2">No MO Selected</h3>
            </Card>
          ) : (
            <>
              {/* Barcode Scanner Section */}
              {barcodeMode && (
                <Card variant="bordered" className="p-6 bg-purple-50">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Barcode Scanner</h3>
                  <div className="space-y-4">
                    <Input
                      type="text"
                      placeholder="Scan barcode or enter manually..."
                      onKeyDown={(e) => {
                        if (e.key === 'Enter') {
                          handleBarcodeInput(e.currentTarget.value)
                          e.currentTarget.value = ''
                        }
                      }}
                      autoFocus
                    />
                    <div className="flex flex-wrap gap-2">
                      {scannedBarcodes.map((code, i) => (
                        <Badge key={i} variant="success" className="text-xs">
                          {code}
                        </Badge>
                      ))}
                    </div>
                    <p className="text-sm text-gray-600">
                      Scanned: <strong>{scannedBarcodes.length}</strong> cartons
                    </p>
                  </div>
                </Card>
              )}

              {/* Receipt Form */}
              <Card variant="bordered" className="p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">FG Receipt Entry</h3>

                {/* MO Summary */}
                <div className="p-4 bg-gray-50 rounded-lg mb-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <p className="text-xs text-gray-600">MO Target Qty</p>
                      <p className="text-lg font-semibold text-gray-900">{formatNumber(expectedPcs)} pcs</p>
                    </div>
                    <div>
                      <p className="text-xs text-gray-600">Expected Cartons</p>
                      <p className="text-lg font-semibold text-blue-600">{formatNumber(expectedCartons)} CTN</p>
                    </div>
                  </div>
                </div>

                <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
                  <div>
                    <Label>Receipt Date</Label>
                    <Input type="date" {...register('receipt_date')} />
                  </div>

                  <div>
                    <Label>Cartons Received</Label>
                    <Input
                      type="number"
                      {...register('cartons_received', { valueAsNumber: true })}
                      min="1"
                      placeholder="0"
                      disabled={barcodeMode}
                    />
                    {barcodeMode && (
                      <p className="text-xs text-gray-500 mt-1">Auto-filled from barcode scanning</p>
                    )}
                  </div>

                  {cartonsReceived > 0 && (
                    <Alert variant={Math.abs(variance) > 10 ? 'destructive' : 'default'}>
                      <div className="flex items-start gap-3">
                        <VarianceIcon className={cn('w-5 h-5 mt-0.5', varianceStatus.color)} />
                        <div className="flex-1">
                          <p className="text-sm font-semibold">Validation: {varianceStatus.label}</p>
                          <div className="text-xs mt-2 space-y-1">
                            <p>Expected: {formatNumber(expectedPcs)} pcs ({formatNumber(expectedCartons)} cartons)</p>
                            <p>Actual: {formatNumber(actualPcs)} pcs ({formatNumber(cartonsReceived)} cartons)</p>
                            <p>Variance: {variance.toFixed(2)}%</p>
                          </div>
                        </div>
                      </div>
                    </Alert>
                  )}

                  <div>
                    <Label>Storage Location</Label>
                    <Input {...register('location')} placeholder="e.g., WH-FG-01" />
                  </div>

                  <div>
                    <Label>Notes</Label>
                    <Input {...register('notes')} placeholder="Any remarks..." />
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
                        : 'Confirm FG Receipt'
                    }
                  </Button>
                </form>
              </Card>

              {/* Auto-Display Logic Info */}
              <Card variant="bordered" className="p-4 bg-blue-50">
                <h4 className="text-sm font-semibold text-blue-900 mb-2">💾 Multi-UOM Auto-Display</h4>
                <div className="text-xs text-blue-700 space-y-1">
                  <p><strong>Input:</strong> Cartons received → System calculates pcs (×60)</p>
                  <p><strong>Storage:</strong> Total qty stored in database as pcs</p>
                  <p><strong>Display:</strong> Auto-show Pcs, Cartons, Weight, Pallets</p>
                  <p className="mt-2"><strong>Example:</strong> 8 cartons → Store: 480 pcs → Display: 480 pcs / 8 CTN / 26.8 kg / 1.6 pallets</p>
                </div>
              </Card>
            </>
          )}
        </div>
      </div>
    </div>
  )
}

export default FGReceiptPage
