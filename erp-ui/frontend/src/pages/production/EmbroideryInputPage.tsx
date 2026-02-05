import React, { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Calendar, Save, RefreshCw, Package, TrendingUp, AlertCircle } from 'lucide-react'
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
const embroideryInputSchema = z.object({
  spk_id: z.number(),
  date: z.string(),
  good_output: z.number().min(0),
  defect_qty: z.number().min(0),
  subcon_name: z.string().optional(),
  subcon_send_qty: z.number().min(0).optional(),
  subcon_receive_qty: z.number().min(0).optional(),
  notes: z.string().optional()
})

type EmbroideryInputForm = z.infer<typeof embroideryInputSchema>

const EmbroideryInputPage: React.FC = () => {
  const [selectedSPK, setSelectedSPK] = useState<number | null>(null)
  const [selectedDate, setSelectedDate] = useState<string>(new Date().toISOString().split('T')[0])
  const queryClient = useQueryClient()

  // Fetch active SPKs
  const { data: spkList = [] } = useQuery({
    queryKey: ['spk-list-embroidery'],
    queryFn: async () => {
      const response = await api.ppic.getSPKList({ department: 'EMBROIDERY', status: 'IN_PROGRESS' })
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

  // Fetch daily progress
  const { data: dailyProgress = [] } = useQuery({
    queryKey: ['daily-progress-embroidery', selectedSPK],
    queryFn: async () => {
      if (!selectedSPK) return []
      const response = await api.production.getDailyProgress(selectedSPK)
      return response.data
    },
    enabled: !!selectedSPK
  })

  // Form
  const { register, handleSubmit, reset, watch, setValue, formState: { errors } } = useForm<EmbroideryInputForm>({
    resolver: zodResolver(embroideryInputSchema),
    defaultValues: {
      date: selectedDate,
      good_output: 0,
      defect_qty: 0,
      subcon_send_qty: 0,
      subcon_receive_qty: 0
    }
  })

  const goodOutput = watch('good_output') || 0
  const defectQty = watch('defect_qty') || 0
  const totalOutput = goodOutput + defectQty

  // Submit mutation
  const submitMutation = useMutation({
    mutationFn: async (data: EmbroideryInputForm) => {
      return await api.production.inputEmbroidery(data)
    },
    onSuccess: () => {
      toast.success('Embroidery input saved successfully')
      queryClient.invalidateQueries({ queryKey: ['daily-progress-embroidery', selectedSPK] })
      reset()
    },
    onError: () => {
      toast.error('Failed to save embroidery input')
    }
  })

  const onSubmit = (data: EmbroideryInputForm) => {
    submitMutation.mutate({
      ...data,
      spk_id: selectedSPK!
    })
  }

  // Calculate cumulative progress
  const cumulativeGood = dailyProgress.reduce((sum: number, day: any) => sum + (day.good_output || 0), 0)
  const cumulativeDefect = dailyProgress.reduce((sum: number, day: any) => sum + (day.defect_qty || 0), 0)
  const cumulativeTotal = cumulativeGood + cumulativeDefect
  const targetQty = spkDetail?.target_qty || 0
  const progressPercent = targetQty > 0 ? (cumulativeGood / targetQty) * 100 : 0
  const yield_rate = cumulativeTotal > 0 ? (cumulativeGood / cumulativeTotal) * 100 : 0

  return (
    <div className="space-y-6 p-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Embroidery Input</h1>
          <p className="text-gray-500 mt-1">Record daily embroidery production with subcontractor management</p>
        </div>
        <Button variant="outline" onClick={() => queryClient.invalidateQueries()}>
          <RefreshCw className="w-4 h-4 mr-2" />
          Refresh
        </Button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Section - SPK Selection & Progress */}
        <div className="lg:col-span-1 space-y-4">
          {/* SPK Selection */}
          <Card variant="bordered" className="p-4">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Select SPK</h3>
            <div className="space-y-2">
              {spkList.length === 0 ? (
                <p className="text-sm text-gray-500 text-center py-4">No active SPK for Embroidery</p>
              ) : (
                spkList.map((spk: any) => (
                  <div
                    key={spk.id}
                    onClick={() => setSelectedSPK(spk.id)}
                    className={cn(
                      'p-3 border rounded-lg cursor-pointer transition-all',
                      selectedSPK === spk.id
                        ? 'border-blue-500 bg-blue-50'
                        : 'border-gray-200 hover:border-gray-300'
                    )}
                  >
                    <div className="flex items-start justify-between">
                      <div>
                        <p className="text-sm font-semibold text-gray-900">{spk.spk_number}</p>
                        <p className="text-xs text-gray-600 mt-1">{spk.article_name}</p>
                        <p className="text-xs text-gray-500 mt-1">Target: {formatNumber(spk.target_qty)} pcs</p>
                      </div>
                      {spk.priority === 'URGENT' && (
                        <Badge variant="destructive" className="text-xs">
                          Urgent
                        </Badge>
                      )}
                    </div>
                  </div>
                ))
              )}
            </div>
          </Card>

          {/* Progress Summary */}
          {selectedSPK && spkDetail && (
            <Card variant="bordered" className="p-4">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Progress Summary</h3>
              <div className="space-y-4">
                {/* Progress Bar */}
                <div>
                  <div className="flex justify-between text-sm mb-2">
                    <span className="text-gray-600">Overall Progress</span>
                    <span className="font-semibold text-gray-900">{progressPercent.toFixed(1)}%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-3">
                    <div
                      className={cn(
                        'h-3 rounded-full transition-all',
                        progressPercent >= 100 ? 'bg-green-500' : 'bg-blue-500'
                      )}
                      style={{ width: `${Math.min(progressPercent, 100)}%` }}
                    />
                  </div>
                </div>

                {/* Stats */}
                <div className="grid grid-cols-2 gap-3">
                  <div className="p-3 bg-green-50 rounded-lg">
                    <p className="text-xs text-gray-600">Good Output</p>
                    <p className="text-lg font-bold text-green-600">{formatNumber(cumulativeGood)}</p>
                  </div>
                  <div className="p-3 bg-red-50 rounded-lg">
                    <p className="text-xs text-gray-600">Defect</p>
                    <p className="text-lg font-bold text-red-600">{formatNumber(cumulativeDefect)}</p>
                  </div>
                  <div className="p-3 bg-blue-50 rounded-lg">
                    <p className="text-xs text-gray-600">Target</p>
                    <p className="text-lg font-bold text-blue-600">{formatNumber(targetQty)}</p>
                  </div>
                  <div className="p-3 bg-purple-50 rounded-lg">
                    <p className="text-xs text-gray-600">Yield Rate</p>
                    <p className="text-lg font-bold text-purple-600">{yield_rate.toFixed(1)}%</p>
                  </div>
                </div>

                {/* Remaining */}
                <div className="p-3 bg-gray-50 rounded-lg">
                  <p className="text-xs text-gray-600">Remaining</p>
                  <p className="text-xl font-bold text-gray-900">
                    {formatNumber(Math.max(0, targetQty - cumulativeGood))} pcs
                  </p>
                  {cumulativeGood >= targetQty && (
                    <Badge variant="success" className="mt-2">
                      Target Achieved!
                    </Badge>
                  )}
                </div>
              </div>
            </Card>
          )}
        </div>

        {/* Right Section - Input Form & Calendar */}
        <div className="lg:col-span-2 space-y-4">
          {!selectedSPK ? (
            <Card variant="bordered" className="p-12 text-center">
              <Package className="w-16 h-16 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-gray-900 mb-2">No SPK Selected</h3>
              <p className="text-gray-500">Please select an SPK from the left panel to start input</p>
            </Card>
          ) : (
            <>
              {/* Input Form */}
              <Card variant="bordered" className="p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Daily Embroidery Input</h3>
                <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
                  {/* Date */}
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
                    {errors.date && <p className="text-xs text-red-600 mt-1">{errors.date.message}</p>}
                  </div>

                  {/* Production Output */}
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <Label>Good Output (pcs)</Label>
                      <Input
                        type="number"
                        {...register('good_output', { valueAsNumber: true })}
                        min="0"
                        placeholder="0"
                      />
                      {errors.good_output && <p className="text-xs text-red-600 mt-1">{errors.good_output.message}</p>}
                    </div>
                    <div>
                      <Label>Defect Qty (pcs)</Label>
                      <Input
                        type="number"
                        {...register('defect_qty', { valueAsNumber: true })}
                        min="0"
                        placeholder="0"
                      />
                      {errors.defect_qty && <p className="text-xs text-red-600 mt-1">{errors.defect_qty.message}</p>}
                    </div>
                  </div>

                  {/* Total Output Display */}
                  {totalOutput > 0 && (
                    <div className="p-3 bg-blue-50 rounded-lg">
                      <p className="text-sm text-gray-600">Total Output Today</p>
                      <p className="text-2xl font-bold text-blue-600">
                        {formatNumber(totalOutput)} pcs
                      </p>
                      <p className="text-xs text-gray-500 mt-1">
                        Yield: {totalOutput > 0 ? ((goodOutput / totalOutput) * 100).toFixed(1) : 0}%
                      </p>
                    </div>
                  )}

                  {/* Subcontractor Section */}
                  <div className="border-t pt-4 mt-4">
                    <h4 className="text-md font-semibold text-gray-900 mb-3">Subcontractor Management</h4>
                    <div className="space-y-4">
                      <div>
                        <Label>Subcontractor Name</Label>
                        <Input
                          type="text"
                          {...register('subcon_name')}
                          placeholder="e.g., CV Embroidery Partner"
                        />
                      </div>
                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <Label>Send to Subcon (pcs)</Label>
                          <Input
                            type="number"
                            {...register('subcon_send_qty', { valueAsNumber: true })}
                            min="0"
                            placeholder="0"
                          />
                        </div>
                        <div>
                          <Label>Receive from Subcon (pcs)</Label>
                          <Input
                            type="number"
                            {...register('subcon_receive_qty', { valueAsNumber: true })}
                            min="0"
                            placeholder="0"
                          />
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Notes */}
                  <div>
                    <Label>Notes (optional)</Label>
                    <Textarea
                      {...register('notes')}
                      placeholder="Any additional notes or remarks..."
                      rows={3}
                    />
                  </div>

                  {/* Submit Button */}
                  <Button
                    type="submit"
                    variant="primary"
                    className="w-full"
                    disabled={submitMutation.isPending}
                  >
                    <Save className="w-4 h-4 mr-2" />
                    {submitMutation.isPending ? 'Saving...' : 'Save Embroidery Input'}
                  </Button>
                </form>
              </Card>

              {/* Daily Progress Calendar */}
              <Card variant="bordered" className="p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Daily Progress History</h3>
                {dailyProgress.length === 0 ? (
                  <p className="text-sm text-gray-500 text-center py-8">No progress recorded yet</p>
                ) : (
                  <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                      <thead className="bg-gray-50">
                        <tr>
                          <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">Date</th>
                          <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">Good Output</th>
                          <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">Defect</th>
                          <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">Total</th>
                          <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">Yield</th>
                          <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">Subcon</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-gray-200">
                        {dailyProgress.map((day: any, index: number) => {
                          const dayTotal = (day.good_output || 0) + (day.defect_qty || 0)
                          const dayYield = dayTotal > 0 ? ((day.good_output || 0) / dayTotal) * 100 : 0
                          
                          return (
                            <tr key={index} className="hover:bg-gray-50">
                              <td className="px-4 py-3 whitespace-nowrap">{formatDate(day.date)}</td>
                              <td className="px-4 py-3 whitespace-nowrap font-semibold text-green-600">
                                {formatNumber(day.good_output || 0)}
                              </td>
                              <td className="px-4 py-3 whitespace-nowrap text-red-600">
                                {formatNumber(day.defect_qty || 0)}
                              </td>
                              <td className="px-4 py-3 whitespace-nowrap font-semibold">
                                {formatNumber(dayTotal)}
                              </td>
                              <td className="px-4 py-3 whitespace-nowrap">
                                <Badge variant={dayYield >= 95 ? 'success' : 'warning'} className="text-xs">
                                  {dayYield.toFixed(1)}%
                                </Badge>
                              </td>
                              <td className="px-4 py-3 text-xs text-gray-600">
                                {day.subcon_name || '-'}
                              </td>
                            </tr>
                          )
                        })}
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

export default EmbroideryInputPage
