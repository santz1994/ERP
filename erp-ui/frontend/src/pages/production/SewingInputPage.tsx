import React, { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Save, RefreshCw, Package, AlertTriangle } from 'lucide-react'
import { api } from '@/api'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Select } from '@/components/ui/select'
import { formatDate, formatNumber, cn } from '@/lib/utils'
import toast from 'react-hot-toast'

// Form schema
const sewingInputSchema = z.object({
  spk_id: z.number(),
  stream_type: z.enum(['BODY', 'BAJU']),
  date: z.string(),
  good_output: z.number().min(0),
  defect_qty: z.number().min(0),
  thread_consumed_kg: z.number().min(0).optional(),
  operator_name: z.string().optional(),
  line_number: z.string().optional(),
  notes: z.string().optional()
}).refine(data => {
  // Constraint: Sewing Baju cannot exceed Sewing Body
  return true // Will be validated against cumulative data
}, {
  message: 'Sewing Baju output cannot exceed Sewing Body output'
})

type SewingInputForm = z.infer<typeof sewingInputSchema>

const SewingInputPage: React.FC = () => {
  const [selectedSPK, setSelectedSPK] = useState<number | null>(null)
  const [streamType, setStreamType] = useState<'BODY' | 'BAJU'>('BODY')
  const [selectedDate, setSelectedDate] = useState<string>(new Date().toISOString().split('T')[0])
  const queryClient = useQueryClient()

  // Fetch active SPKs
  const { data: spkList = [] } = useQuery({
    queryKey: ['spk-list-sewing'],
    queryFn: async () => {
      const response = await api.ppic.getSPKList({ department: 'SEWING', status: 'IN_PROGRESS' })
      return response.data
    }
  })

  // Fetch SPK detail
  const { data: spkDetail } = useQuery({
    queryKey: ['spk-detail', selectedSPK],
    queryFn: async () => {
      if (!selectedSPK) return null
      const response = await api.ppic.getSPKDetail(selectedSPK)
      return response.data
    },
    enabled: !!selectedSPK
  })

  // Fetch progress by stream
  const { data: bodyProgress = [] } = useQuery({
    queryKey: ['sewing-progress-body', selectedSPK],
    queryFn: async () => {
      if (!selectedSPK) return []
      const response = await api.production.getSewingProgress(selectedSPK, 'BODY')
      return response.data
    },
    enabled: !!selectedSPK
  })

  const { data: bajuProgress = [] } = useQuery({
    queryKey: ['sewing-progress-baju', selectedSPK],
    queryFn: async () => {
      if (!selectedSPK) return []
      const response = await api.production.getSewingProgress(selectedSPK, 'BAJU')
      return response.data
    },
    enabled: !!selectedSPK
  })

  // Form
  const { register, handleSubmit, reset, watch, setValue, formState: { errors } } = useForm<SewingInputForm>({
    resolver: zodResolver(sewingInputSchema),
    defaultValues: {
      stream_type: streamType,
      date: selectedDate,
      good_output: 0,
      defect_qty: 0,
      thread_consumed_kg: 0
    }
  })

  const goodOutput = watch('good_output') || 0
  const defectQty = watch('defect_qty') || 0
  const totalOutput = goodOutput + defectQty

  // Submit mutation
  const submitMutation = useMutation({
    mutationFn: async (data: SewingInputForm) => {
      return await api.production.inputSewing(data)
    },
    onSuccess: () => {
      toast.success(`Sewing ${streamType} input saved successfully`)
      queryClient.invalidateQueries({ queryKey: [`sewing-progress-${streamType.toLowerCase()}`, selectedSPK] })
      reset()
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to save sewing input')
    }
  })

  const onSubmit = (data: SewingInputForm) => {
    // Validate constraint: Baju cannot exceed Body
    if (data.stream_type === 'BAJU') {
      const cumulativeBody = bodyProgress.reduce((sum: number, day: any) => sum + (day.good_output || 0), 0)
      const cumulativeBaju = bajuProgress.reduce((sum: number, day: any) => sum + (day.good_output || 0), 0)
      
      if (cumulativeBaju + data.good_output > cumulativeBody) {
        toast.error('Sewing Baju output cannot exceed Sewing Body output')
        return
      }
    }

    submitMutation.mutate({
      ...data,
      spk_id: selectedSPK!,
      stream_type: streamType
    })
  }

  // Calculate cumulative progress
  const cumulativeBody = bodyProgress.reduce((sum: number, day: any) => sum + (day.good_output || 0), 0)
  const cumulativeBaju = bajuProgress.reduce((sum: number, day: any) => sum + (day.good_output || 0), 0)
  const targetQty = spkDetail?.target_qty || 0
  const bodyPercent = targetQty > 0 ? (cumulativeBody / targetQty) * 100 : 0
  const bajuPercent = targetQty > 0 ? (cumulativeBaju / targetQty) * 100 : 0

  return (
    <div className="space-y-6 p-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Sewing Input</h1>
          <p className="text-gray-500 mt-1">Record daily sewing production (Body & Baju parallel streams)</p>
        </div>
        <Button variant="outline" onClick={() => queryClient.invalidateQueries()}>
          <RefreshCw className="w-4 h-4 mr-2" />
          Refresh
        </Button>
      </div>

      {/* Constraint Alert */}
      <Card variant="bordered" className="p-4 bg-yellow-50 border-yellow-200">
        <div className="flex items-start gap-3">
          <AlertTriangle className="w-5 h-5 text-yellow-600 mt-0.5" />
          <div>
            <p className="text-sm font-semibold text-yellow-900">Important Constraint</p>
            <p className="text-sm text-yellow-700 mt-1">
              Sewing Baju output CANNOT exceed Sewing Body output. System will validate this rule.
            </p>
          </div>
        </div>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Section - SPK Selection */}
        <div className="lg:col-span-1 space-y-4">
          <Card variant="bordered" className="p-4">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Select SPK</h3>
            <div className="space-y-2">
              {spkList.length === 0 ? (
                <p className="text-sm text-gray-500 text-center py-4">No active SPK for Sewing</p>
              ) : (
                spkList.map((spk: any) => (
                  <div
                    key={spk.id}
                    onClick={() => setSelectedSPK(spk.id)}
                    className={cn(
                      'p-3 border rounded-lg cursor-pointer transition-all',
                      selectedSPK === spk.id ? 'border-blue-500 bg-blue-50' : 'border-gray-200 hover:border-gray-300'
                    )}
                  >
                    <p className="text-sm font-semibold text-gray-900">{spk.spk_number}</p>
                    <p className="text-xs text-gray-600 mt-1">{spk.article_name}</p>
                    <p className="text-xs text-gray-500 mt-1">Target: {formatNumber(spk.target_qty)} pcs</p>
                  </div>
                ))
              )}
            </div>
          </Card>

          {/* Stream Selection */}
          {selectedSPK && (
            <Card variant="bordered" className="p-4">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Select Stream</h3>
              <div className="space-y-2">
                <button
                  onClick={() => {
                    setStreamType('BODY')
                    setValue('stream_type', 'BODY')
                  }}
                  className={cn(
                    'w-full p-4 border-2 rounded-lg text-left transition-all',
                    streamType === 'BODY' ? 'border-blue-500 bg-blue-50' : 'border-gray-200 hover:border-gray-300'
                  )}
                >
                  <p className="font-semibold text-gray-900">Sewing Body</p>
                  <p className="text-sm text-gray-600 mt-1">Main body of the soft toy</p>
                  <p className="text-lg font-bold text-blue-600 mt-2">{formatNumber(cumulativeBody)} / {formatNumber(targetQty)}</p>
                  <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
                    <div className="bg-blue-500 h-2 rounded-full" style={{ width: `${Math.min(bodyPercent, 100)}%` }} />
                  </div>
                </button>

                <button
                  onClick={() => {
                    setStreamType('BAJU')
                    setValue('stream_type', 'BAJU')
                  }}
                  className={cn(
                    'w-full p-4 border-2 rounded-lg text-left transition-all',
                    streamType === 'BAJU' ? 'border-purple-500 bg-purple-50' : 'border-gray-200 hover:border-gray-300'
                  )}
                >
                  <p className="font-semibold text-gray-900">Sewing Baju</p>
                  <p className="text-sm text-gray-600 mt-1">Clothing for the soft toy</p>
                  <p className="text-lg font-bold text-purple-600 mt-2">{formatNumber(cumulativeBaju)} / {formatNumber(targetQty)}</p>
                  <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
                    <div className="bg-purple-500 h-2 rounded-full" style={{ width: `${Math.min(bajuPercent, 100)}%` }} />
                  </div>
                  {cumulativeBaju > cumulativeBody && (
                    <div className="mt-2 flex items-center gap-2 text-red-600">
                      <AlertTriangle className="w-4 h-4" />
                      <span className="text-xs font-semibold">Exceeds Body!</span>
                    </div>
                  )}
                </button>
              </div>
            </Card>
          )}
        </div>

        {/* Right Section - Input Form */}
        <div className="lg:col-span-2 space-y-4">
          {!selectedSPK ? (
            <Card variant="bordered" className="p-12 text-center">
              <Package className="w-16 h-16 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-gray-900 mb-2">No SPK Selected</h3>
              <p className="text-gray-500">Please select an SPK from the left panel</p>
            </Card>
          ) : (
            <>
              <Card variant="bordered" className="p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold text-gray-900">
                    Sewing {streamType} Input
                  </h3>
                  <Badge variant={streamType === 'BODY' ? 'default' : 'secondary'}>
                    {streamType}
                  </Badge>
                </div>

                <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
                  <div>
                    <Label>Production Date</Label>
                    <Input
                      type="date"
                      {...register('date')}
                      value={selectedDate}
                      onChange={(e) => {
                        setSelectedDate(e.target.value)
                        setValue('date', e.target.value)
                      }}
                    />
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <Label>Good Output (pcs)</Label>
                      <Input
                        type="number"
                        {...register('good_output', { valueAsNumber: true })}
                        min="0"
                        placeholder="0"
                      />
                    </div>
                    <div>
                      <Label>Defect Qty (pcs)</Label>
                      <Input
                        type="number"
                        {...register('defect_qty', { valueAsNumber: true })}
                        min="0"
                        placeholder="0"
                      />
                    </div>
                  </div>

                  {totalOutput > 0 && (
                    <div className="p-3 bg-blue-50 rounded-lg">
                      <p className="text-sm text-gray-600">Total Output Today</p>
                      <p className="text-2xl font-bold text-blue-600">{formatNumber(totalOutput)} pcs</p>
                    </div>
                  )}

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <Label>Thread Consumed (kg)</Label>
                      <Input
                        type="number"
                        step="0.01"
                        {...register('thread_consumed_kg', { valueAsNumber: true })}
                        min="0"
                        placeholder="0.00"
                      />
                    </div>
                    <div>
                      <Label>Line Number</Label>
                      <Input
                        type="text"
                        {...register('line_number')}
                        placeholder="e.g., Line 1"
                      />
                    </div>
                  </div>

                  <div>
                    <Label>Operator Name</Label>
                    <Input
                      type="text"
                      {...register('operator_name')}
                      placeholder="Operator name"
                    />
                  </div>

                  <div>
                    <Label>Notes (optional)</Label>
                    <Textarea
                      {...register('notes')}
                      placeholder="Any additional notes..."
                      rows={2}
                    />
                  </div>

                  <Button
                    type="submit"
                    variant="primary"
                    className="w-full"
                    disabled={submitMutation.isPending}
                  >
                    <Save className="w-4 h-4 mr-2" />
                    {submitMutation.isPending ? 'Saving...' : `Save Sewing ${streamType} Input`}
                  </Button>
                </form>
              </Card>

              {/* Progress History */}
              <Card variant="bordered" className="p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  {streamType} Progress History
                </h3>
                {(streamType === 'BODY' ? bodyProgress : bajuProgress).length === 0 ? (
                  <p className="text-sm text-gray-500 text-center py-8">No progress recorded</p>
                ) : (
                  <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                      <thead className="bg-gray-50">
                        <tr>
                          <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">Date</th>
                          <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">Good</th>
                          <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">Defect</th>
                          <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">Thread (kg)</th>
                          <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">Line</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-gray-200">
                        {(streamType === 'BODY' ? bodyProgress : bajuProgress).map((day: any, i: number) => (
                          <tr key={i}>
                            <td className="px-4 py-3">{formatDate(day.date)}</td>
                            <td className="px-4 py-3 font-semibold text-green-600">{formatNumber(day.good_output || 0)}</td>
                            <td className="px-4 py-3 text-red-600">{formatNumber(day.defect_qty || 0)}</td>
                            <td className="px-4 py-3">{day.thread_consumed_kg || '-'}</td>
                            <td className="px-4 py-3">{day.line_number || '-'}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </Card>
            </>
          )}
        </div>
      </div>
    </div>
  )
}

export default SewingInputPage
