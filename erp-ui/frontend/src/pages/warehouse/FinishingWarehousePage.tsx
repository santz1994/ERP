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
import { Badge } from '@/components/ui/badge'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { toast } from 'sonner'
import {
  Package,
  ArrowRight,
  CheckCircle,
  AlertCircle,
  TrendingUp,
  Box,
  Layers
} from 'lucide-react'
import { formatNumber, formatDate, cn } from '@/lib/utils'

// Finishing Warehouse Schema
const finishingWarehouseSchema = z.object({
  mo_id: z.number().min(1, 'MO is required'),
  stage: z.enum(['STUFFING', 'CLOSING']),
  transaction_date: z.string(),
  quantity: z.number().min(1, 'Quantity must be at least 1'),
  filling_consumed_kg: z.number().min(0).optional(),
  notes: z.string().optional()
})

type FinishingWarehouseForm = z.infer<typeof finishingWarehouseSchema>

const FinishingWarehousePage: React.FC = () => {
  const [selectedMO, setSelectedMO] = useState<number | null>(null)
  const [selectedStage, setSelectedStage] = useState<'STUFFING' | 'CLOSING'>('STUFFING')
  
  const queryClient = useQueryClient()

  // Fetch MO List (Active Finishing MOs)
  const { data: moList = [] } = useQuery({
    queryKey: ['mo-list-finishing'],
    queryFn: () => api.ppic.getMOList({ 
      status: 'RELEASED',
      has_finishing: true 
    })
  })

  // Fetch MO Detail
  const { data: moDetail } = useQuery({
    queryKey: ['mo-detail', selectedMO],
    queryFn: () => api.ppic.getMODetail(selectedMO!),
    enabled: !!selectedMO
  })

  // Fetch Finishing Warehouse Stock for selected MO
  const { data: warehouseStock } = useQuery({
    queryKey: ['finishing-warehouse-stock', selectedMO],
    queryFn: () => api.warehouse.getFinishingWarehouseStock(selectedMO!),
    enabled: !!selectedMO
  })

  // Fetch Transaction History
  const { data: transactionHistory = [] } = useQuery({
    queryKey: ['finishing-warehouse-history', selectedMO],
    queryFn: () => api.warehouse.getFinishingWarehouseHistory(selectedMO!),
    enabled: !!selectedMO
  })

  const {
    register,
    handleSubmit,
    watch,
    setValue,
    reset,
    formState: { errors }
  } = useForm<FinishingWarehouseForm>({
    resolver: zodResolver(finishingWarehouseSchema),
    defaultValues: {
      stage: 'STUFFING',
      transaction_date: new Date().toISOString().split('T')[0]
    }
  })

  const watchQuantity = watch('quantity')

  // Calculate available stock for selected stage
  const availableStock = React.useMemo(() => {
    if (!warehouseStock) return { skin: 0, stuffed_body: 0 }
    
    return {
      skin: warehouseStock.skin_stock || 0,
      stuffed_body: warehouseStock.stuffed_body_stock || 0
    }
  }, [warehouseStock])

  // Validate if transaction is possible
  const canProcess = React.useMemo(() => {
    if (!watchQuantity) return false
    
    if (selectedStage === 'STUFFING') {
      // Need Skin stock
      return availableStock.skin >= watchQuantity
    } else {
      // Need Stuffed Body stock
      return availableStock.stuffed_body >= watchQuantity
    }
  }, [selectedStage, watchQuantity, availableStock])

  // Transaction Mutation
  const transactionMutation = useMutation({
    mutationFn: (data: FinishingWarehouseForm) => 
      api.warehouse.createFinishingWarehouseTransaction(data),
    onSuccess: () => {
      toast.success(`${selectedStage} transaction recorded successfully`)
      queryClient.invalidateQueries({ queryKey: ['finishing-warehouse-stock'] })
      queryClient.invalidateQueries({ queryKey: ['finishing-warehouse-history'] })
      reset({
        mo_id: selectedMO!,
        stage: selectedStage,
        transaction_date: new Date().toISOString().split('T')[0]
      })
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to record transaction')
    }
  })

  const onSubmit = (data: FinishingWarehouseForm) => {
    if (!canProcess) {
      toast.error('Insufficient stock for this transaction')
      return
    }

    transactionMutation.mutate(data)
  }

  const handleMOSelect = (moId: number) => {
    setSelectedMO(moId)
    setValue('mo_id', moId)
    reset({
      mo_id: moId,
      stage: selectedStage,
      transaction_date: new Date().toISOString().split('T')[0]
    })
  }

  const handleStageChange = (stage: 'STUFFING' | 'CLOSING') => {
    setSelectedStage(stage)
    setValue('stage', stage)
    reset({
      mo_id: selectedMO!,
      stage: stage,
      transaction_date: new Date().toISOString().split('T')[0]
    })
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Finishing Warehouse (2-Stage)</h1>
          <p className="text-gray-500 mt-1">
            Internal conversion tracking: Skin → Stuffed Body → Finished Doll
          </p>
        </div>
        <Badge variant="outline" className="text-lg px-4 py-2">
          <Layers className="w-5 h-5 mr-2" />
          {transactionHistory.length} Transactions
        </Badge>
      </div>

      {/* Info Card */}
      <Alert className="bg-blue-50 border-blue-200">
        <AlertCircle className="w-5 h-5 text-blue-600" />
        <AlertDescription>
          <p className="font-semibold text-blue-900 mb-2">
            🔄 2-Stage Process (Demand-Driven)
          </p>
          <div className="text-blue-800 text-sm space-y-1">
            <p><strong>Stage 1 - STUFFING:</strong> Skin + Filling → Stuffed Body (Internal conversion, no surat jalan)</p>
            <p><strong>Stage 2 - CLOSING:</strong> Stuffed Body → Finished Doll (Sent to Packing)</p>
            <p><strong>Target:</strong> Adjust based on Packing demand (bukan rigid MO target)</p>
          </div>
        </AlertDescription>
      </Alert>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left: MO Selection */}
        <div className="lg:col-span-1">
          <Card className="p-6">
            <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
              <Box className="w-5 h-5" />
              Select MO
            </h2>
            
            <div className="space-y-2 max-h-[600px] overflow-y-auto">
              {moList.length === 0 ? (
                <p className="text-gray-500 text-sm">No active MO for finishing</p>
              ) : (
                moList.map((mo: any) => (
                  <button
                    key={mo.id}
                    onClick={() => handleMOSelect(mo.id)}
                    className={cn(
                      'w-full text-left p-4 rounded-lg border-2 transition-all',
                      selectedMO === mo.id
                        ? 'border-purple-500 bg-purple-50'
                        : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                    )}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <p className="font-semibold text-gray-900">{mo.mo_number}</p>
                        <p className="text-sm text-gray-600 mt-1">{mo.article_name}</p>
                        <div className="flex items-center gap-2 mt-2">
                          <Badge variant="outline" className="text-xs">
                            Week {mo.week}
                          </Badge>
                          <Badge variant="outline" className="text-xs">
                            {mo.destination}
                          </Badge>
                        </div>
                        <p className="text-xs text-gray-500 mt-2">
                          Target: {formatNumber(mo.target_qty)} pcs
                        </p>
                      </div>
                      {selectedMO === mo.id && (
                        <CheckCircle className="w-5 h-5 text-purple-500 flex-shrink-0" />
                      )}
                    </div>
                  </button>
                ))
              )}
            </div>
          </Card>
        </div>

        {/* Right: 2-Stage Management */}
        <div className="lg:col-span-2">
          {!selectedMO ? (
            <Card className="p-12 text-center">
              <Layers className="w-16 h-16 text-gray-300 mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-gray-900 mb-2">
                Select MO to Manage Finishing Warehouse
              </h3>
              <p className="text-gray-500">
                Choose an MO to track internal 2-stage conversion
              </p>
            </Card>
          ) : (
            <div className="space-y-6">
              {/* MO Info Card */}
              <Card className="p-6 bg-purple-50 border-purple-200">
                <div className="flex items-start justify-between">
                  <div>
                    <h3 className="text-lg font-semibold text-purple-900">
                      {moDetail?.mo_number}
                    </h3>
                    <p className="text-purple-700 mt-1">{moDetail?.article_name}</p>
                    <div className="flex items-center gap-3 mt-3">
                      <Badge className="bg-purple-600 text-white">
                        Week {moDetail?.week}
                      </Badge>
                      <Badge className="bg-purple-600 text-white">
                        {moDetail?.destination}
                      </Badge>
                      <span className="text-sm text-purple-800">
                        Target: {formatNumber(moDetail?.target_qty)} pcs
                      </span>
                    </div>
                  </div>
                </div>
              </Card>

              {/* Stock Status Cards */}
              <div className="grid grid-cols-2 gap-4">
                {/* Skin Stock */}
                <Card className="p-6 bg-gradient-to-br from-yellow-50 to-orange-50 border-yellow-200">
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="text-sm font-medium text-yellow-900">Skin Stock</h4>
                    <Package className="w-5 h-5 text-yellow-600" />
                  </div>
                  <p className="text-3xl font-bold text-yellow-900">
                    {formatNumber(availableStock.skin)}
                  </p>
                  <p className="text-sm text-yellow-700 mt-1">pcs available</p>
                  <Badge variant="outline" className="mt-3 text-xs border-yellow-300 text-yellow-800">
                    Stage 1 Input
                  </Badge>
                </Card>

                {/* Stuffed Body Stock */}
                <Card className="p-6 bg-gradient-to-br from-green-50 to-emerald-50 border-green-200">
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="text-sm font-medium text-green-900">Stuffed Body Stock</h4>
                    <Box className="w-5 h-5 text-green-600" />
                  </div>
                  <p className="text-3xl font-bold text-green-900">
                    {formatNumber(availableStock.stuffed_body)}
                  </p>
                  <p className="text-sm text-green-700 mt-1">pcs available</p>
                  <Badge variant="outline" className="mt-3 text-xs border-green-300 text-green-800">
                    Stage 2 Input
                  </Badge>
                </Card>
              </div>

              {/* Stage Selection */}
              <Card className="p-6">
                <h3 className="text-lg font-semibold mb-4">Select Process Stage</h3>
                <div className="grid grid-cols-2 gap-4">
                  <button
                    onClick={() => handleStageChange('STUFFING')}
                    className={cn(
                      'p-6 rounded-lg border-2 transition-all text-left',
                      selectedStage === 'STUFFING'
                        ? 'border-yellow-500 bg-yellow-50'
                        : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                    )}
                  >
                    <div className="flex items-center justify-between mb-3">
                      <Package className={cn(
                        'w-6 h-6',
                        selectedStage === 'STUFFING' ? 'text-yellow-600' : 'text-gray-400'
                      )} />
                      {selectedStage === 'STUFFING' && (
                        <CheckCircle className="w-5 h-5 text-yellow-500" />
                      )}
                    </div>
                    <h4 className="font-semibold text-gray-900 mb-2">Stage 1: STUFFING</h4>
                    <p className="text-sm text-gray-600 mb-3">
                      Convert Skin + Filling → Stuffed Body
                    </p>
                    <div className="flex items-center gap-2 text-xs">
                      <Badge variant="outline">Input: Skin</Badge>
                      <ArrowRight className="w-3 h-3" />
                      <Badge variant="outline">Output: Stuffed Body</Badge>
                    </div>
                  </button>

                  <button
                    onClick={() => handleStageChange('CLOSING')}
                    className={cn(
                      'p-6 rounded-lg border-2 transition-all text-left',
                      selectedStage === 'CLOSING'
                        ? 'border-green-500 bg-green-50'
                        : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                    )}
                  >
                    <div className="flex items-center justify-between mb-3">
                      <Box className={cn(
                        'w-6 h-6',
                        selectedStage === 'CLOSING' ? 'text-green-600' : 'text-gray-400'
                      )} />
                      {selectedStage === 'CLOSING' && (
                        <CheckCircle className="w-5 h-5 text-green-500" />
                      )}
                    </div>
                    <h4 className="font-semibold text-gray-900 mb-2">Stage 2: CLOSING</h4>
                    <p className="text-sm text-gray-600 mb-3">
                      Convert Stuffed Body → Finished Doll
                    </p>
                    <div className="flex items-center gap-2 text-xs">
                      <Badge variant="outline">Input: Stuffed Body</Badge>
                      <ArrowRight className="w-3 h-3" />
                      <Badge variant="outline">Output: Finished Doll</Badge>
                    </div>
                  </button>
                </div>
              </Card>

              {/* Transaction Form */}
              <Card className="p-6">
                <h3 className="text-lg font-semibold mb-4">
                  Record {selectedStage === 'STUFFING' ? 'Stuffing' : 'Closing'} Transaction
                </h3>
                
                <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="transaction_date">Transaction Date</Label>
                      <Input
                        id="transaction_date"
                        type="date"
                        {...register('transaction_date')}
                        className={errors.transaction_date ? 'border-red-500' : ''}
                      />
                      {errors.transaction_date && (
                        <p className="text-sm text-red-500 mt-1">{errors.transaction_date.message}</p>
                      )}
                    </div>

                    <div>
                      <Label htmlFor="quantity">
                        Quantity {selectedStage === 'STUFFING' ? 'to Stuff' : 'to Close'}
                      </Label>
                      <div className="flex items-center gap-2">
                        <Input
                          id="quantity"
                          type="number"
                          min="1"
                          {...register('quantity', { valueAsNumber: true })}
                          className={errors.quantity ? 'border-red-500' : ''}
                        />
                        <span className="text-sm text-gray-600 whitespace-nowrap">pcs</span>
                      </div>
                      {errors.quantity && (
                        <p className="text-sm text-red-500 mt-1">{errors.quantity.message}</p>
                      )}
                    </div>
                  </div>

                  {/* Filling Consumption (STUFFING only) */}
                  {selectedStage === 'STUFFING' && (
                    <div>
                      <Label htmlFor="filling_consumed_kg">Filling Consumed (Optional)</Label>
                      <div className="flex items-center gap-2">
                        <Input
                          id="filling_consumed_kg"
                          type="number"
                          step="0.01"
                          placeholder="Enter filling weight..."
                          {...register('filling_consumed_kg', { valueAsNumber: true })}
                        />
                        <span className="text-sm text-gray-600 whitespace-nowrap">kg</span>
                      </div>
                      <p className="text-xs text-gray-500 mt-1">
                        Track filling/dacron consumption for this batch
                      </p>
                    </div>
                  )}

                  <div>
                    <Label htmlFor="notes">Notes (Optional)</Label>
                    <Input
                      id="notes"
                      {...register('notes')}
                      placeholder="Enter any notes..."
                    />
                  </div>

                  {/* Stock Validation Alert */}
                  <Alert className={cn(
                    canProcess ? 'bg-green-50 border-green-200' : 'bg-red-50 border-red-200'
                  )}>
                    <div className="flex items-start gap-3">
                      {canProcess ? (
                        <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
                      ) : (
                        <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
                      )}
                      <div className="flex-1">
                        <h4 className={cn(
                          'font-semibold mb-2',
                          canProcess ? 'text-green-900' : 'text-red-900'
                        )}>
                          {canProcess ? 'Stock Available' : 'Insufficient Stock'}
                        </h4>
                        <div className="grid grid-cols-3 gap-4 text-sm">
                          <div>
                            <p className="text-gray-600">Required Stock</p>
                            <p className="font-semibold text-gray-900">
                              {selectedStage === 'STUFFING' ? 'Skin' : 'Stuffed Body'}
                            </p>
                          </div>
                          <div>
                            <p className="text-gray-600">Available</p>
                            <p className="font-semibold text-gray-900">
                              {formatNumber(
                                selectedStage === 'STUFFING' 
                                  ? availableStock.skin 
                                  : availableStock.stuffed_body
                              )} pcs
                            </p>
                          </div>
                          <div>
                            <p className="text-gray-600">To Process</p>
                            <p className={cn(
                              'font-semibold',
                              canProcess ? 'text-green-600' : 'text-red-600'
                            )}>
                              {formatNumber(watchQuantity || 0)} pcs
                            </p>
                          </div>
                        </div>
                      </div>
                    </div>
                  </Alert>

                  <Button
                    type="submit"
                    disabled={!canProcess || transactionMutation.isPending}
                    className={cn(
                      'w-full',
                      selectedStage === 'STUFFING' 
                        ? 'bg-yellow-600 hover:bg-yellow-700' 
                        : 'bg-green-600 hover:bg-green-700'
                    )}
                  >
                    {transactionMutation.isPending ? (
                      'Recording...'
                    ) : (
                      <>
                        <TrendingUp className="w-4 h-4 mr-2" />
                        Record {selectedStage === 'STUFFING' ? 'Stuffing' : 'Closing'} Transaction
                      </>
                    )}
                  </Button>
                </form>
              </Card>

              {/* Transaction History */}
              {transactionHistory.length > 0 && (
                <Card className="p-6">
                  <h3 className="text-lg font-semibold mb-4">Transaction History</h3>
                  <div className="space-y-3">
                    {transactionHistory.map((transaction: any) => (
                      <div 
                        key={transaction.id} 
                        className={cn(
                          'flex items-center justify-between p-4 rounded-lg',
                          transaction.stage === 'STUFFING' 
                            ? 'bg-yellow-50 border border-yellow-200'
                            : 'bg-green-50 border border-green-200'
                        )}
                      >
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-1">
                            <Badge className={cn(
                              transaction.stage === 'STUFFING'
                                ? 'bg-yellow-600 text-white'
                                : 'bg-green-600 text-white'
                            )}>
                              {transaction.stage}
                            </Badge>
                            <p className="text-sm text-gray-600">
                              {formatDate(transaction.transaction_date)}
                            </p>
                          </div>
                          <p className="font-semibold text-gray-900">
                            {formatNumber(transaction.quantity)} pcs
                          </p>
                          {transaction.filling_consumed_kg && (
                            <p className="text-sm text-gray-600 mt-1">
                              Filling: {formatNumber(transaction.filling_consumed_kg)} kg
                            </p>
                          )}
                          {transaction.notes && (
                            <p className="text-xs text-gray-500 mt-1 italic">
                              {transaction.notes}
                            </p>
                          )}
                        </div>
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

export default FinishingWarehousePage
