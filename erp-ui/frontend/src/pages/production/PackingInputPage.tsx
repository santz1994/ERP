import React, { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Save, RefreshCw, Package, Barcode, Printer, AlertTriangle } from 'lucide-react'
import { api } from '@/api'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { formatDate, formatNumber, cn } from '@/lib/utils'
import toast from 'react-hot-toast'

const packingInputSchema = z.object({
  spk_id: z.number(),
  date: z.string(),
  packed_sets: z.number().min(0),
  cartons_packed: z.number().min(0),
  barcode_generated: z.boolean().optional().default(false),
  pallet_id: z.string().optional(),
  notes: z.string().optional()
}).refine(data => data.packed_sets > 0 || data.cartons_packed > 0, {
  message: 'Either packed sets or cartons must be greater than 0'
})

type PackingInputForm = z.infer<typeof packingInputSchema>

const PackingInputPage: React.FC = () => {
  const [selectedSPK, setSelectedSPK] = useState<number | null>(null)
  const [selectedDate, setSelectedDate] = useState<string>(new Date().toISOString().split('T')[0])
  const queryClient = useQueryClient()

  const { data: spkList = [] } = useQuery({
    queryKey: ['spk-list-packing'],
    queryFn: async () => {
      const response = await api.ppic.getSPKList({ department: 'PACKING', status: 'IN_PROGRESS' })
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

  const { data: packingProgress = [] } = useQuery({
    queryKey: ['packing-progress', selectedSPK],
    enabled: !!selectedSPK,
    queryFn: async () => {
      const response = await api.production.getPackingProgress(selectedSPK!)
      return response.data
    }
  })

  // Check Doll + Baju availability
  const { data: wipStatus } = useQuery({
    queryKey: ['wip-status', spkDetail?.mo_id],
    enabled: !!spkDetail?.mo_id,
    queryFn: async () => {
      const response = await api.production.getWIPStatus(spkDetail.mo_id)
      return response.data
    }
  })

  const { register, handleSubmit, reset, watch, setValue, formState: { errors } } = useForm<PackingInputForm>({
    resolver: zodResolver(packingInputSchema) as any,
    defaultValues: {
      date: selectedDate,
      packed_sets: 0,
      cartons_packed: 0,
      barcode_generated: false
    }
  })

  const packedSets = watch('packed_sets') || 0
  const cartonsPacked = watch('cartons_packed') || 0

  const submitMutation = useMutation({
    mutationFn: async (data: PackingInputForm) => {
      return await api.production.inputPacking(data)
    },
    onSuccess: () => {
      toast.success('Packing input saved successfully')
      queryClient.invalidateQueries({ queryKey: ['packing-progress', selectedSPK] })
      reset()
    },
    onError: () => {
      toast.error('Failed to save packing input')
    }
  })

  const handleGenerateBarcode = async () => {
    if (!selectedSPK) return
    try {
      const response = await api.production.generateBarcode(selectedSPK, packedSets)
      toast.success(`Barcode generated for ${packedSets} sets`)
      setValue('barcode_generated', true)
    } catch {
      toast.error('Failed to generate barcode')
    }
  }

  const onSubmit = (data: PackingInputForm) => {
    // Validate Doll + Baju constraint
    if (wipStatus) {
      const dollAvailable = wipStatus.finished_doll || 0
      const bajuAvailable = wipStatus.baju_ready || 0
      
      if (data.packed_sets > dollAvailable || data.packed_sets > bajuAvailable) {
        toast.error('Insufficient Doll or Baju for packing')
        return
      }
    }

    submitMutation.mutate({ ...data, spk_id: selectedSPK! })
  }

  const cumulativePacked = packingProgress.reduce((sum: number, d: any) => sum + (d.packed_sets || 0), 0)
  const cumulativeCartons = packingProgress.reduce((sum: number, d: any) => sum + (d.cartons_packed || 0), 0)
  const targetQty = spkDetail?.target_qty || 0

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Packing Input</h1>
          <p className="text-gray-500 mt-1">Pack complete sets (Doll + Baju) with barcode generation</p>
        </div>
        <Button variant="outline" onClick={() => queryClient.invalidateQueries()}>
          <RefreshCw className="w-4 h-4 mr-2" />
          Refresh
        </Button>
      </div>

      {/* Constraint Alert */}
      <Card variant="bordered" className="p-4 bg-blue-50 border-blue-200">
        <div className="flex items-start gap-3">
          <AlertTriangle className="w-5 h-5 text-blue-600 mt-0.5" />
          <div>
            <p className="text-sm font-semibold text-blue-900">Packing Constraint</p>
            <p className="text-sm text-blue-700 mt-1">
              Can only pack complete sets: Requires BOTH Finished Doll AND Baju available
            </p>
          </div>
        </div>
      </Card>

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
                      selectedSPK === spk.id ? 'border-blue-500 bg-blue-50' : 'border-gray-200'
                    )}
                  >
                    <div className="flex items-start justify-between">
                      <div>
                        <p className="text-sm font-semibold">{spk.spk_number}</p>
                        <p className="text-xs text-gray-600 mt-1">{spk.article_name}</p>
                        {spk.week && spk.destination && (
                          <div className="flex gap-2 mt-2">
                            <Badge variant="outline" className="text-xs">Week {spk.week}</Badge>
                            <Badge variant="outline" className="text-xs">{spk.destination}</Badge>
                          </div>
                        )}
                      </div>
                      {spk.priority === 'URGENT' && (
                        <Badge variant="destructive" className="text-xs">Urgent</Badge>
                      )}
                    </div>
                  </div>
                ))
              )}
            </div>
          </Card>

          {selectedSPK && wipStatus && (
            <Card variant="bordered" className="p-4">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">WIP Status</h3>
              <div className="space-y-3">
                <div className="p-3 bg-green-50 rounded-lg">
                  <p className="text-xs text-gray-600">Finished Doll Available</p>
                  <p className="text-xl font-bold text-green-600">{formatNumber(wipStatus.finished_doll || 0)}</p>
                </div>
                <div className="p-3 bg-purple-50 rounded-lg">
                  <p className="text-xs text-gray-600">Baju Ready</p>
                  <p className="text-xl font-bold text-purple-600">{formatNumber(wipStatus.baju_ready || 0)}</p>
                </div>
                <div className="p-3 bg-blue-50 rounded-lg">
                  <p className="text-xs text-gray-600">Can Pack (min of both)</p>
                  <p className="text-xl font-bold text-blue-600">
                    {formatNumber(Math.min(wipStatus.finished_doll || 0, wipStatus.baju_ready || 0))}
                  </p>
                </div>
              </div>
            </Card>
          )}
        </div>

        <div className="lg:col-span-2 space-y-4">
          {!selectedSPK ? (
            <Card variant="bordered" className="p-12 text-center">
              <Package className="w-16 h-16 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-gray-900 mb-2">No SPK Selected</h3>
            </Card>
          ) : (
            <>
              <Card variant="bordered" className="p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Packing Input</h3>
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
                      <Label>Packed Sets (Doll+Baju)</Label>
                      <Input type="number" {...register('packed_sets', { valueAsNumber: true })} min="0" />
                    </div>
                    <div>
                      <Label>Cartons Packed</Label>
                      <Input type="number" {...register('cartons_packed', { valueAsNumber: true })} min="0" />
                    </div>
                  </div>

                  <div className="p-4 border-2 border-dashed border-gray-300 rounded-lg">
                    <div className="flex items-center justify-between mb-3">
                      <Label>Barcode Generation</Label>
                      <Barcode className="w-5 h-5 text-gray-400" />
                    </div>
                    <Button
                      type="button"
                      variant="outline"
                      className="w-full"
                      onClick={handleGenerateBarcode}
                      disabled={packedSets === 0}
                    >
                      <Printer className="w-4 h-4 mr-2" />
                      Generate Barcode for {packedSets} Sets
                    </Button>
                  </div>

                  <div>
                    <Label>Pallet ID (optional)</Label>
                    <Input {...register('pallet_id')} placeholder="PALLET-001" />
                  </div>

                  <div>
                    <Label>Notes</Label>
                    <Textarea {...register('notes')} rows={2} />
                  </div>

                  <Button type="submit" variant="primary" className="w-full" disabled={submitMutation.isPending}>
                    <Save className="w-4 h-4 mr-2" />
                    {submitMutation.isPending ? 'Saving...' : 'Save Packing Input'}
                  </Button>
                </form>
              </Card>

              <Card variant="bordered" className="p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold text-gray-900">Progress Summary</h3>
                  <Badge variant="default" className="text-sm">
                    {((cumulativePacked / targetQty) * 100).toFixed(1)}%
                  </Badge>
                </div>
                <div className="grid grid-cols-3 gap-4 mb-4">
                  <div className="p-3 bg-blue-50 rounded-lg">
                    <p className="text-xs text-gray-600">Packed Sets</p>
                    <p className="text-xl font-bold text-blue-600">{formatNumber(cumulativePacked)}</p>
                  </div>
                  <div className="p-3 bg-green-50 rounded-lg">
                    <p className="text-xs text-gray-600">Total Cartons</p>
                    <p className="text-xl font-bold text-green-600">{formatNumber(cumulativeCartons)}</p>
                  </div>
                  <div className="p-3 bg-gray-50 rounded-lg">
                    <p className="text-xs text-gray-600">Remaining</p>
                    <p className="text-xl font-bold text-gray-900">{formatNumber(Math.max(0, targetQty - cumulativePacked))}</p>
                  </div>
                </div>

                <h4 className="text-md font-semibold text-gray-900 mb-3">Packing History</h4>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-4 py-2 text-left">Date</th>
                        <th className="px-4 py-2 text-left">Sets</th>
                        <th className="px-4 py-2 text-left">Cartons</th>
                        <th className="px-4 py-2 text-left">Pallet</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y">
                      {packingProgress.map((d: any, i: number) => (
                        <tr key={i}>
                          <td className="px-4 py-3">{formatDate(d.date)}</td>
                          <td className="px-4 py-3 font-semibold">{formatNumber(d.packed_sets || 0)}</td>
                          <td className="px-4 py-3">{formatNumber(d.cartons_packed || 0)}</td>
                          <td className="px-4 py-3">{d.pallet_id || '-'}</td>
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

export default PackingInputPage
