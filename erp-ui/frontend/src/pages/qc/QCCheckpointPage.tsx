import React, { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { api } from '@/api'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select } from '@/components/ui/select'
import { Textarea } from '@/components/ui/textarea'
import { Badge } from '@/components/ui/badge'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { toast } from 'sonner'
import {
  ClipboardCheck,
  CheckCircle,
  XCircle,
  AlertTriangle,
  FileText,
  TrendingUp,
  TrendingDown
} from 'lucide-react'
import { formatNumber, formatDate, cn } from '@/lib/utils'

// QC Checkpoint Schema
const qcCheckpointSchema = z.object({
  spk_id: z.number().min(1, 'SPK is required'),
  checkpoint: z.enum(['AFTER_CUTTING', 'AFTER_SEWING', 'AFTER_FINISHING', 'PRE_PACKING']),
  inspection_date: z.string(),
  inspected_qty: z.number().min(1, 'Inspected quantity must be at least 1'),
  pass_qty: z.number().min(0),
  fail_qty: z.number().min(0),
  defect_type: z.string().optional(),
  defect_description: z.string().optional(),
  inspector_name: z.string().min(1, 'Inspector name is required'),
  notes: z.string().optional()
}).refine(data => data.pass_qty + data.fail_qty === data.inspected_qty, {
  message: 'Pass + Fail must equal Inspected Quantity',
  path: ['inspected_qty']
})

type QCCheckpointForm = z.infer<typeof qcCheckpointSchema>

const QCCheckpointPage: React.FC = () => {
  const [selectedSPK, setSelectedSPK] = useState<number | null>(null)
  const [selectedCheckpoint, setSelectedCheckpoint] = useState<'AFTER_CUTTING' | 'AFTER_SEWING' | 'AFTER_FINISHING' | 'PRE_PACKING'>('AFTER_CUTTING')
  
  const queryClient = useQueryClient()

  // Fetch SPK List (Active SPKs)
  const { data: spkList = [] } = useQuery({
    queryKey: ['spk-list-active'],
    queryFn: () => api.ppic.getSPKList({ status: 'ACTIVE' })
  })

  // Fetch SPK Detail
  const { data: spkDetail } = useQuery({
    queryKey: ['spk-detail', selectedSPK],
    queryFn: () => api.ppic.getSPKDetail(selectedSPK!),
    enabled: !!selectedSPK
  })

  // Fetch QC History for selected SPK & Checkpoint
  const { data: qcHistory = [] } = useQuery({
    queryKey: ['qc-checkpoint-history', selectedSPK, selectedCheckpoint],
    queryFn: () => api.qc.getQCCheckpointHistory(selectedSPK!, selectedCheckpoint),
    enabled: !!selectedSPK
  })

  // Fetch QC Statistics
  const { data: qcStats } = useQuery({
    queryKey: ['qc-statistics', selectedSPK],
    queryFn: () => api.qc.getQCStatistics(selectedSPK!),
    enabled: !!selectedSPK
  })

  const {
    register,
    handleSubmit,
    watch,
    setValue,
    reset,
    formState: { errors }
  } = useForm<QCCheckpointForm>({
    resolver: zodResolver(qcCheckpointSchema),
    defaultValues: {
      checkpoint: 'AFTER_CUTTING',
      inspection_date: new Date().toISOString().split('T')[0]
    }
  })

  const watchInspectedQty = watch('inspected_qty')
  const watchPassQty = watch('pass_qty')
  const watchFailQty = watch('fail_qty')

  // Calculate First Pass Yield (FPY)
  const firstPassYield = React.useMemo(() => {
    if (!watchInspectedQty || watchInspectedQty === 0) return 0
    return ((watchPassQty || 0) / watchInspectedQty) * 100
  }, [watchInspectedQty, watchPassQty])

  // Auto-calculate fail qty
  React.useEffect(() => {
    if (watchInspectedQty !== undefined && watchPassQty !== undefined) {
      const calculatedFail = watchInspectedQty - watchPassQty
      setValue('fail_qty', Math.max(0, calculatedFail))
    }
  }, [watchInspectedQty, watchPassQty, setValue])

  // QC Checkpoint Mutation
  const qcMutation = useMutation({
    mutationFn: (data: QCCheckpointForm) => api.qc.createQCCheckpoint(data),
    onSuccess: () => {
      toast.success('QC inspection recorded successfully')
      queryClient.invalidateQueries({ queryKey: ['qc-checkpoint-history'] })
      queryClient.invalidateQueries({ queryKey: ['qc-statistics'] })
      queryClient.invalidateQueries({ queryKey: ['spk-detail'] })
      reset({
        spk_id: selectedSPK!,
        checkpoint: selectedCheckpoint,
        inspection_date: new Date().toISOString().split('T')[0]
      })
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to record QC inspection')
    }
  })

  const onSubmit = (data: QCCheckpointForm) => {
    qcMutation.mutate(data)
  }

  const handleSPKSelect = (spkId: number) => {
    setSelectedSPK(spkId)
    setValue('spk_id', spkId)
    reset({
      spk_id: spkId,
      checkpoint: selectedCheckpoint,
      inspection_date: new Date().toISOString().split('T')[0]
    })
  }

  const handleCheckpointChange = (checkpoint: typeof selectedCheckpoint) => {
    setSelectedCheckpoint(checkpoint)
    setValue('checkpoint', checkpoint)
    reset({
      spk_id: selectedSPK!,
      checkpoint: checkpoint,
      inspection_date: new Date().toISOString().split('T')[0]
    })
  }

  // Checkpoint colors
  const getCheckpointColor = (checkpoint: string) => {
    const colors: Record<string, string> = {
      AFTER_CUTTING: 'blue',
      AFTER_SEWING: 'green',
      AFTER_FINISHING: 'yellow',
      PRE_PACKING: 'red'
    }
    return colors[checkpoint] || 'gray'
  }

  // Defect types by checkpoint
  const defectTypes = {
    AFTER_CUTTING: ['Measurement Error', 'Fabric Damage', 'Wrong Pattern', 'Incomplete Cut'],
    AFTER_SEWING: ['Loose Thread', 'Broken Seam', 'Uneven Stitch', 'Wrong Attachment'],
    AFTER_FINISHING: ['Stuffing Insufficient', 'Closing Defect', 'Tag Missing', 'Shape Deformed'],
    PRE_PACKING: ['Label Missing', 'Barcode Error', 'Box Damage', 'Incomplete Set']
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">QC 4-Checkpoint System</h1>
          <p className="text-gray-500 mt-1">Quality inspection at each production stage</p>
        </div>
        <Badge variant="outline" className="text-lg px-4 py-2">
          <ClipboardCheck className="w-5 h-5 mr-2" />
          {qcHistory.length} Inspections
        </Badge>
      </div>

      {/* Info Card */}
      <Alert className="bg-blue-50 border-blue-200">
        <AlertTriangle className="w-5 h-5 text-blue-600" />
        <AlertDescription>
          <p className="font-semibold text-blue-900 mb-2">
            ✅ 4-Checkpoint Quality Control System
          </p>
          <div className="text-blue-800 text-sm space-y-1">
            <p><strong>Checkpoint 1 - CUTTING:</strong> Check fabric cut accuracy, measurement, pattern alignment</p>
            <p><strong>Checkpoint 2 - EMBROIDERY:</strong> Inspect embroidery quality, thread breaks, design accuracy</p>
            <p><strong>Checkpoint 3 - SEWING:</strong> Verify seam quality, stitching, attachments</p>
            <p><strong>Checkpoint 4 - FINISHING:</strong> Check stuffing quality, closing, tag attachment</p>
            <p><strong>Checkpoint 5 - PACKING:</strong> Final inspection before shipment (label, barcode, completeness)</p>
          </div>
        </AlertDescription>
      </Alert>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left: SPK Selection */}
        <div className="lg:col-span-1">
          <Card className="p-6">
            <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
              <FileText className="w-5 h-5" />
              Select SPK
            </h2>
            
            <div className="space-y-2 max-h-[600px] overflow-y-auto">
              {spkList.length === 0 ? (
                <p className="text-gray-500 text-sm">No active SPK available</p>
              ) : (
                spkList.map((spk: any) => (
                  <button
                    key={spk.id}
                    onClick={() => handleSPKSelect(spk.id)}
                    className={cn(
                      'w-full text-left p-4 rounded-lg border-2 transition-all',
                      selectedSPK === spk.id
                        ? 'border-blue-500 bg-blue-50'
                        : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                    )}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <p className="font-semibold text-gray-900">{spk.spk_number}</p>
                        <p className="text-sm text-gray-600 mt-1">{spk.article_name}</p>
                        <div className="flex items-center gap-2 mt-2">
                          <Badge variant="outline" className="text-xs">
                            {spk.department}
                          </Badge>
                          <Badge variant="outline" className="text-xs">
                            Week {spk.week}
                          </Badge>
                        </div>
                      </div>
                      {selectedSPK === spk.id && (
                        <CheckCircle className="w-5 h-5 text-blue-500 flex-shrink-0" />
                      )}
                    </div>
                  </button>
                ))
              )}
            </div>
          </Card>
        </div>

        {/* Right: QC Inspection Form */}
        <div className="lg:col-span-2">
          {!selectedSPK ? (
            <Card className="p-12 text-center">
              <ClipboardCheck className="w-16 h-16 text-gray-300 mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-gray-900 mb-2">
                Select SPK to Start QC Inspection
              </h3>
              <p className="text-gray-500">
                Choose an SPK from the list to record quality inspection
              </p>
            </Card>
          ) : (
            <div className="space-y-6">
              {/* SPK Info Card */}
              <Card className="p-6 bg-blue-50 border-blue-200">
                <div className="flex items-start justify-between">
                  <div>
                    <h3 className="text-lg font-semibold text-blue-900">
                      {spkDetail?.spk_number}
                    </h3>
                    <p className="text-blue-700 mt-1">{spkDetail?.article_name}</p>
                    <div className="flex items-center gap-3 mt-3">
                      <Badge className="bg-blue-600 text-white">
                        {spkDetail?.department}
                      </Badge>
                      <span className="text-sm text-blue-800">
                        Target: {formatNumber(spkDetail?.target_qty)} pcs
                      </span>
                    </div>
                  </div>
                </div>
              </Card>

              {/* QC Statistics */}
              {qcStats && (
                <div className="grid grid-cols-4 gap-4">
                  <Card className="p-4 bg-gradient-to-br from-green-50 to-emerald-50 border-green-200">
                    <div className="flex items-center justify-between mb-2">
                      <h4 className="text-sm font-medium text-green-900">Total Inspected</h4>
                      <CheckCircle className="w-5 h-5 text-green-600" />
                    </div>
                    <p className="text-2xl font-bold text-green-900">
                      {formatNumber(qcStats.total_inspected)}
                    </p>
                    <p className="text-xs text-green-700 mt-1">pcs</p>
                  </Card>

                  <Card className="p-4 bg-gradient-to-br from-blue-50 to-cyan-50 border-blue-200">
                    <div className="flex items-center justify-between mb-2">
                      <h4 className="text-sm font-medium text-blue-900">Pass</h4>
                      <TrendingUp className="w-5 h-5 text-blue-600" />
                    </div>
                    <p className="text-2xl font-bold text-blue-900">
                      {formatNumber(qcStats.total_pass)}
                    </p>
                    <p className="text-xs text-blue-700 mt-1">
                      {qcStats.pass_percentage?.toFixed(1)}% FPY
                    </p>
                  </Card>

                  <Card className="p-4 bg-gradient-to-br from-red-50 to-rose-50 border-red-200">
                    <div className="flex items-center justify-between mb-2">
                      <h4 className="text-sm font-medium text-red-900">Fail</h4>
                      <TrendingDown className="w-5 h-5 text-red-600" />
                    </div>
                    <p className="text-2xl font-bold text-red-900">
                      {formatNumber(qcStats.total_fail)}
                    </p>
                    <p className="text-xs text-red-700 mt-1">
                      {qcStats.fail_percentage?.toFixed(1)}% Defect
                    </p>
                  </Card>

                  <Card className="p-4 bg-gradient-to-br from-yellow-50 to-amber-50 border-yellow-200">
                    <div className="flex items-center justify-between mb-2">
                      <h4 className="text-sm font-medium text-yellow-900">Yield Rate</h4>
                      <ClipboardCheck className="w-5 h-5 text-yellow-600" />
                    </div>
                    <p className="text-2xl font-bold text-yellow-900">
                      {qcStats.yield_rate?.toFixed(1)}%
                    </p>
                    <p className="text-xs text-yellow-700 mt-1">Overall</p>
                  </Card>
                </div>
              )}

              {/* Checkpoint Selection */}
              <Card className="p-6">
                <h3 className="text-lg font-semibold mb-4">Select Checkpoint</h3>
                <div className="grid grid-cols-4 gap-3">
                  {['AFTER_CUTTING', 'AFTER_SEWING', 'AFTER_FINISHING', 'PRE_PACKING'].map((checkpoint) => (
                    <button
                      key={checkpoint}
                      onClick={() => handleCheckpointChange(checkpoint as typeof selectedCheckpoint)}
                      className={cn(
                        'p-4 rounded-lg border-2 transition-all text-center',
                        selectedCheckpoint === checkpoint
                          ? `border-${getCheckpointColor(checkpoint)}-500 bg-${getCheckpointColor(checkpoint)}-50`
                          : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                      )}
                    >
                      <ClipboardCheck className={cn(
                        'w-6 h-6 mx-auto mb-2',
                        selectedCheckpoint === checkpoint 
                          ? `text-${getCheckpointColor(checkpoint)}-600`
                          : 'text-gray-400'
                      )} />
                      <p className="text-sm font-semibold">{checkpoint.replace('_', ' ')}</p>
                    </button>
                  ))}
                </div>
              </Card>

              {/* Inspection Form */}
              <Card className="p-6">
                <h3 className="text-lg font-semibold mb-4">
                  Record Inspection - {selectedCheckpoint}
                </h3>
                
                <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="inspection_date">Inspection Date</Label>
                      <Input
                        id="inspection_date"
                        type="date"
                        {...register('inspection_date')}
                        className={errors.inspection_date ? 'border-red-500' : ''}
                      />
                      {errors.inspection_date && (
                        <p className="text-sm text-red-500 mt-1">{errors.inspection_date.message}</p>
                      )}
                    </div>

                    <div>
                      <Label htmlFor="inspector_name">Inspector Name</Label>
                      <Input
                        id="inspector_name"
                        {...register('inspector_name')}
                        placeholder="Enter inspector name..."
                        className={errors.inspector_name ? 'border-red-500' : ''}
                      />
                      {errors.inspector_name && (
                        <p className="text-sm text-red-500 mt-1">{errors.inspector_name.message}</p>
                      )}
                    </div>
                  </div>

                  <div className="grid grid-cols-3 gap-4">
                    <div>
                      <Label htmlFor="inspected_qty">Inspected Qty</Label>
                      <Input
                        id="inspected_qty"
                        type="number"
                        min="1"
                        {...register('inspected_qty', { valueAsNumber: true })}
                        className={errors.inspected_qty ? 'border-red-500' : ''}
                      />
                      {errors.inspected_qty && (
                        <p className="text-sm text-red-500 mt-1">{errors.inspected_qty.message}</p>
                      )}
                    </div>

                    <div>
                      <Label htmlFor="pass_qty">Pass Qty</Label>
                      <Input
                        id="pass_qty"
                        type="number"
                        min="0"
                        {...register('pass_qty', { valueAsNumber: true })}
                        className={errors.pass_qty ? 'border-red-500' : ''}
                      />
                      {errors.pass_qty && (
                        <p className="text-sm text-red-500 mt-1">{errors.pass_qty.message}</p>
                      )}
                    </div>

                    <div>
                      <Label htmlFor="fail_qty">Fail Qty (Auto)</Label>
                      <Input
                        id="fail_qty"
                        type="number"
                        {...register('fail_qty', { valueAsNumber: true })}
                        disabled
                        className="bg-gray-100"
                      />
                    </div>
                  </div>

                  {/* Defect Details (shown if fail_qty > 0) */}
                  {watchFailQty > 0 && (
                    <>
                      <div>
                        <Label htmlFor="defect_type">Defect Type</Label>
                        <select
                          id="defect_type"
                          {...register('defect_type')}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        >
                          <option value="">Select defect type...</option>
                          {defectTypes[selectedCheckpoint].map(type => (
                            <option key={type} value={type}>{type}</option>
                          ))}
                        </select>
                      </div>

                      <div>
                        <Label htmlFor="defect_description">Defect Description</Label>
                        <Textarea
                          id="defect_description"
                          {...register('defect_description')}
                          placeholder="Describe the defects in detail..."
                          rows={3}
                        />
                      </div>
                    </>
                  )}

                  <div>
                    <Label htmlFor="notes">Notes (Optional)</Label>
                    <Input
                      id="notes"
                      {...register('notes')}
                      placeholder="Additional notes..."
                    />
                  </div>

                  {/* First Pass Yield Display */}
                  {watchInspectedQty > 0 && (
                    <Alert className={cn(
                      firstPassYield >= 95 ? 'bg-green-50 border-green-200' :
                      firstPassYield >= 90 ? 'bg-blue-50 border-blue-200' :
                      firstPassYield >= 85 ? 'bg-yellow-50 border-yellow-200' :
                      'bg-red-50 border-red-200'
                    )}>
                      <div className="flex items-start gap-3">
                        {firstPassYield >= 95 ? <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" /> :
                         firstPassYield >= 90 ? <CheckCircle className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" /> :
                         firstPassYield >= 85 ? <AlertTriangle className="w-5 h-5 text-yellow-600 flex-shrink-0 mt-0.5" /> :
                         <XCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />}
                        <div className="flex-1">
                          <h4 className={cn(
                            'font-semibold mb-2',
                            firstPassYield >= 95 ? 'text-green-900' :
                            firstPassYield >= 90 ? 'text-blue-900' :
                            firstPassYield >= 85 ? 'text-yellow-900' :
                            'text-red-900'
                          )}>
                            First Pass Yield (FPY): {firstPassYield.toFixed(1)}%
                          </h4>
                          <div className="grid grid-cols-3 gap-4 text-sm">
                            <div>
                              <p className="text-gray-600">Inspected</p>
                              <p className="font-semibold text-gray-900">
                                {formatNumber(watchInspectedQty)} pcs
                              </p>
                            </div>
                            <div>
                              <p className="text-gray-600">Pass</p>
                              <p className="font-semibold text-green-600">
                                {formatNumber(watchPassQty || 0)} pcs
                              </p>
                            </div>
                            <div>
                              <p className="text-gray-600">Fail</p>
                              <p className="font-semibold text-red-600">
                                {formatNumber(watchFailQty || 0)} pcs
                              </p>
                            </div>
                          </div>
                        </div>
                      </div>
                    </Alert>
                  )}

                  <Button
                    type="submit"
                    disabled={qcMutation.isPending}
                    className="w-full bg-blue-600 hover:bg-blue-700"
                  >
                    {qcMutation.isPending ? (
                      'Recording...'
                    ) : (
                      <>
                        <ClipboardCheck className="w-4 h-4 mr-2" />
                        Record QC Inspection
                      </>
                    )}
                  </Button>
                </form>
              </Card>

              {/* Inspection History */}
              {qcHistory.length > 0 && (
                <Card className="p-6">
                  <h3 className="text-lg font-semibold mb-4">
                    Inspection History - {selectedCheckpoint}
                  </h3>
                  <div className="space-y-3">
                    {qcHistory.map((inspection: any) => (
                      <div key={inspection.id} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-1">
                            <p className="text-sm font-semibold text-gray-900">
                              {formatDate(inspection.inspection_date)}
                            </p>
                            <span className="text-sm text-gray-600">by {inspection.inspector_name}</span>
                          </div>
                          <div className="flex items-center gap-4 text-sm">
                            <span>Inspected: <strong>{formatNumber(inspection.inspected_qty)}</strong></span>
                            <span className="text-green-600">Pass: <strong>{formatNumber(inspection.pass_qty)}</strong></span>
                            <span className="text-red-600">Fail: <strong>{formatNumber(inspection.fail_qty)}</strong></span>
                          </div>
                          {inspection.defect_type && (
                            <p className="text-xs text-gray-500 mt-1">
                              Defect: {inspection.defect_type}
                            </p>
                          )}
                        </div>
                        <Badge className={cn(
                          inspection.first_pass_yield >= 95 ? 'bg-green-600' :
                          inspection.first_pass_yield >= 90 ? 'bg-blue-600' :
                          inspection.first_pass_yield >= 85 ? 'bg-yellow-600' :
                          'bg-red-600'
                        )}>
                          FPY: {inspection.first_pass_yield.toFixed(1)}%
                        </Badge>
                      </div>
                    ))}
                  </div>
                </Card>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default QCCheckpointPage
