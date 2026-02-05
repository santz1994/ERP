import React, { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Save, RefreshCw, Package, Layers } from 'lucide-react'
import { api } from '@/api'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { formatDate, formatNumber, cn } from '@/lib/utils'
import toast from 'react-hot-toast'

const finishingInputSchema = z.object({
  spk_id: z.number(),
  stage: z.enum(['STUFFING', 'CLOSING']),
  date: z.string(),
  good_output: z.number().min(0),
  defect_qty: z.number().min(0),
  filling_consumed_kg: z.number().min(0).optional(),
  notes: z.string().optional()
})

type FinishingInputForm = z.infer<typeof finishingInputSchema>

const FinishingInputPage: React.FC = () => {
  const [selectedSPK, setSelectedSPK] = useState<number | null>(null)
  const [stage, setStage] = useState<'STUFFING' | 'CLOSING'>('STUFFING')
  const [selectedDate, setSelectedDate] = useState<string>(new Date().toISOString().split('T')[0])
  const queryClient = useQueryClient()

  const { data: spkList = [] } = useQuery({
    queryKey: ['spk-list-finishing'],
    queryFn: async () => {
      const response = await api.ppic.getSPKList({ department: 'FINISHING', status: 'IN_PROGRESS' })
      return response.data
    }
  })

  const { data: spkDetail } = useQuery({
    queryKey: ['spk-detail', selectedSPK],
    enabled: !!selectedSPK,
    queryFn: async () => {
      const response = await api.ppic.getSPKDetail(selectedSPK!)
      return response.data
    }
  })

  const { data: stuffingProgress = [] } = useQuery({
    queryKey: ['finishing-stuffing', selectedSPK],
    enabled: !!selectedSPK,
    queryFn: async () => {
      const response = await api.production.getFinishingProgress(selectedSPK!, 'STUFFING')
      return response.data
    }
  })

  const { data: closingProgress = [] } = useQuery({
    queryKey: ['finishing-closing', selectedSPK],
    enabled: !!selectedSPK,
    queryFn: async () => {
      const response = await api.production.getFinishingProgress(selectedSPK!, 'CLOSING')
      return response.data
    }
  })

  const { register, handleSubmit, reset, watch, setValue, formState: { errors } } = useForm<FinishingInputForm>({
    resolver: zodResolver(finishingInputSchema),
    defaultValues: {
      stage,
      date: selectedDate,
      good_output: 0,
      defect_qty: 0,
      filling_consumed_kg: 0
    }
  })

  const goodOutput = watch('good_output') || 0
  const defectQty = watch('defect_qty') || 0

  const submitMutation = useMutation({
    mutationFn: async (data: FinishingInputForm) => {
      return await api.production.inputFinishing(data)
    },
    onSuccess: () => {
      toast.success(`${stage} input saved successfully`)
      queryClient.invalidateQueries({ queryKey: [`finishing-${stage.toLowerCase()}`, selectedSPK] })
      reset()
    },
    onError: () => {
      toast.error('Failed to save finishing input')
    }
  })

  const onSubmit = (data: FinishingInputForm) => {
    submitMutation.mutate({ ...data, spk_id: selectedSPK!, stage })
  }

  const cumulativeStuffing = stuffingProgress.reduce((sum: number, d: any) => sum + (d.good_output || 0), 0)
  const cumulativeClosing = closingProgress.reduce((sum: number, d: any) => sum + (d.good_output || 0), 0)
  const targetQty = spkDetail?.target_qty || 0

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Finishing Input (2-Stage Process)</h1>
          <p className="text-gray-500 mt-1">Stage 1: Stuffing | Stage 2: Closing</p>
        </div>
        <Button variant="outline" onClick={() => queryClient.invalidateQueries()}>
          <RefreshCw className="w-4 h-4 mr-2" />
          Refresh
        </Button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-1 space-y-4">
          <Card variant="bordered" className="p-4">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Select SPK</h3>
            <div className="space-y-2">
              {spkList.length === 0 ? (
                <p className="text-sm text-gray-500 text-center py-4">No active SPK</p>
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
                    <p className="text-sm font-semibold">{spk.spk_number}</p>
                    <p className="text-xs text-gray-600 mt-1">{spk.article_name}</p>
                    <p className="text-xs text-gray-500 mt-1">Target: {formatNumber(spk.target_qty)} pcs</p>
                  </div>
                ))
              )}
            </div>
          </Card>

          {selectedSPK && (
            <Card variant="bordered" className="p-4">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Select Stage</h3>
              <div className="space-y-2">
                <button
                  onClick={() => {
                    setStage('STUFFING')
                    setValue('stage', 'STUFFING')
                  }}
                  className={cn(
                    'w-full p-4 border-2 rounded-lg text-left',
                    stage === 'STUFFING' ? 'border-green-500 bg-green-50' : 'border-gray-200'
                  )}
                >
                  <div className="flex items-center gap-2">
                    <Layers className="w-5 h-5 text-green-600" />
                    <p className="font-semibold">Stage 1: Stuffing</p>
                  </div>
                  <p className="text-sm text-gray-600 mt-1">Isi kapas + Close stitch</p>
                  <p className="text-lg font-bold text-green-600 mt-2">
                    {formatNumber(cumulativeStuffing)} / {formatNumber(targetQty)}
                  </p>
                </button>

                <button
                  onClick={() => {
                    setStage('CLOSING')
                    setValue('stage', 'CLOSING')
                  }}
                  className={cn(
                    'w-full p-4 border-2 rounded-lg text-left',
                    stage === 'CLOSING' ? 'border-blue-500 bg-blue-50' : 'border-gray-200'
                  )}
                >
                  <div className="flex items-center gap-2">
                    <Package className="w-5 h-5 text-blue-600" />
                    <p className="font-semibold">Stage 2: Closing</p>
                  </div>
                  <p className="text-sm text-gray-600 mt-1">Hang Tag + Final Touch</p>
                  <p className="text-lg font-bold text-blue-600 mt-2">
                    {formatNumber(cumulativeClosing)} / {formatNumber(targetQty)}
                  </p>
                </button>
              </div>
            </Card>
          )}
        </div>

        <div className="lg:col-span-2 space-y-4">
          {!selectedSPK ? (
            <Card variant="bordered" className="p-12 text-center">
              <Package className="w-16 h-16 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-gray-900 mb-2">No SPK Selected</h3>
              <p className="text-gray-500">Select SPK to start input</p>
            </Card>
          ) : (
            <>
              <Card variant="bordered" className="p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">{stage} Input</h3>
                <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
                  <div>
                    <Label>Date</Label>
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
                      <Input type="number" {...register('good_output', { valueAsNumber: true })} min="0" />
                    </div>
                    <div>
                      <Label>Defect Qty (pcs)</Label>
                      <Input type="number" {...register('defect_qty', { valueAsNumber: true })} min="0" />
                    </div>
                  </div>

                  {stage === 'STUFFING' && (
                    <div>
                      <Label>Filling Consumed (kg)</Label>
                      <Input
                        type="number"
                        step="0.01"
                        {...register('filling_consumed_kg', { valueAsNumber: true })}
                        min="0"
                        placeholder="0.00"
                      />
                    </div>
                  )}

                  <div>
                    <Label>Notes</Label>
                    <Textarea {...register('notes')} rows={2} />
                  </div>

                  <Button type="submit" variant="primary" className="w-full" disabled={submitMutation.isPending}>
                    <Save className="w-4 h-4 mr-2" />
                    {submitMutation.isPending ? 'Saving...' : `Save ${stage} Input`}
                  </Button>
                </form>
              </Card>

              <Card variant="bordered" className="p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">{stage} History</h3>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-4 py-2 text-left">Date</th>
                        <th className="px-4 py-2 text-left">Good</th>
                        <th className="px-4 py-2 text-left">Defect</th>
                        {stage === 'STUFFING' && <th className="px-4 py-2 text-left">Filling (kg)</th>}
                      </tr>
                    </thead>
                    <tbody className="divide-y">
                      {(stage === 'STUFFING' ? stuffingProgress : closingProgress).map((d: any, i: number) => (
                        <tr key={i}>
                          <td className="px-4 py-3">{formatDate(d.date)}</td>
                          <td className="px-4 py-3 text-green-600 font-semibold">{formatNumber(d.good_output || 0)}</td>
                          <td className="px-4 py-3 text-red-600">{formatNumber(d.defect_qty || 0)}</td>
                          {stage === 'STUFFING' && <td className="px-4 py-3">{d.filling_consumed_kg || '-'}</td>}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </Card>
            </>
          )}
        </div>
      </div>
    </div>
  )
}

export default FinishingInputPage
