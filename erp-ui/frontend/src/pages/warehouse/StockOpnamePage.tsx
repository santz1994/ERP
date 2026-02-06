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
import { Badge } from '@/components/ui/badge'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { toast } from 'sonner'
import {
  ClipboardCheck,
  Search,
  AlertTriangle,
  CheckCircle,
  XCircle,
  TrendingUp,
  TrendingDown,
  FileText,
  Calendar
} from 'lucide-react'
import { formatNumber, formatDate, formatCurrency, cn } from '@/lib/utils'

// Stock Opname Schema
const stockOpnameSchema = z.object({
  material_id: z.number().min(1, 'Material is required'),
  opname_date: z.string(),
  system_qty: z.number(),
  physical_qty: z.number().min(0, 'Physical quantity cannot be negative'),
  variance_qty: z.number(),
  variance_percentage: z.number(),
  variance_reason: z.string().optional(),
  counted_by: z.string().min(1, 'Counted by is required'),
  notes: z.string().optional()
})

type StockOpnameForm = z.infer<typeof stockOpnameSchema>

const StockOpnamePage: React.FC = () => {
  const [selectedMaterial, setSelectedMaterial] = useState<number | null>(null)
  const [searchTerm, setSearchTerm] = useState('')
  const [filterCategory, setFilterCategory] = useState<string>('ALL')
  
  const queryClient = useQueryClient()

  // Fetch Material Stock
  const { data: materialStock = [] } = useQuery({
    queryKey: ['material-stock'],
    queryFn: () => api.warehouse.getMaterialStock()
  })

  // Fetch Stock Opname History
  const { data: opnameHistory = [] } = useQuery({
    queryKey: ['stock-opname-history'],
    queryFn: () => api.warehouse.getStockOpnameHistory()
  })

  // Fetch Pending Approvals
  const { data: pendingApprovals = [] } = useQuery({
    queryKey: ['stock-opname-pending'],
    queryFn: () => api.warehouse.getStockOpnamePending()
  })

  const {
    register,
    handleSubmit,
    watch,
    setValue,
    reset,
    formState: { errors }
  } = useForm<StockOpnameForm>({
    resolver: zodResolver(stockOpnameSchema),
    defaultValues: {
      opname_date: new Date().toISOString().split('T')[0]
    }
  })

  const watchSystemQty = watch('system_qty')
  const watchPhysicalQty = watch('physical_qty')

  // Calculate variance automatically
  React.useEffect(() => {
    if (watchSystemQty !== undefined && watchPhysicalQty !== undefined) {
      const variance = watchPhysicalQty - watchSystemQty
      const variancePercentage = watchSystemQty === 0 
        ? 0 
        : (variance / watchSystemQty) * 100

      setValue('variance_qty', variance)
      setValue('variance_percentage', parseFloat(variancePercentage.toFixed(2)))
    }
  }, [watchSystemQty, watchPhysicalQty, setValue])

  // Determine variance status
  const varianceStatus = React.useMemo(() => {
    const variancePct = watch('variance_percentage') || 0
    const absVariance = Math.abs(variancePct)

    if (absVariance === 0) return { status: 'EXACT', color: 'green', icon: CheckCircle }
    if (absVariance <= 2) return { status: 'ACCEPTABLE', color: 'blue', icon: CheckCircle }
    if (absVariance <= 5) return { status: 'REVIEW', color: 'yellow', icon: AlertTriangle }
    return { status: 'CRITICAL', color: 'red', icon: XCircle }
  }, [watch('variance_percentage')])

  // Stock Opname Mutation
  const opnameMutation = useMutation({
    mutationFn: (data: StockOpnameForm) => api.warehouse.recordStockOpname(data as any),
    onSuccess: () => {
      toast.success('Stock opname recorded successfully')
      queryClient.invalidateQueries({ queryKey: ['stock-opname-history'] })
      queryClient.invalidateQueries({ queryKey: ['stock-opname-pending'] })
      queryClient.invalidateQueries({ queryKey: ['material-stock'] })
      reset({
        opname_date: new Date().toISOString().split('T')[0]
      })
      setSelectedMaterial(null)
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to record stock opname')
    }
  })

  // Approval Mutation
  const approvalMutation = useMutation({
    mutationFn: ({ id, action, notes }: { id: number; action: 'APPROVE' | 'REJECT'; notes?: string }) => 
      api.warehouse.approveStockOpname(id, action, notes),
    onSuccess: (_, variables) => {
      toast.success(`Stock opname ${variables.action.toLowerCase()}d`)
      queryClient.invalidateQueries({ queryKey: ['stock-opname-pending'] })
      queryClient.invalidateQueries({ queryKey: ['stock-opname-history'] })
      queryClient.invalidateQueries({ queryKey: ['material-stock'] })
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to process approval')
    }
  })

  const onSubmit = (data: StockOpnameForm) => {
    opnameMutation.mutate(data)
  }

  const handleMaterialSelect = (material: any) => {
    setSelectedMaterial(material.id)
    setValue('material_id', material.id)
    setValue('system_qty', material.available_qty)
    setValue('physical_qty', material.available_qty) // Default to system qty
  }

  const handleApproval = (id: number, action: 'APPROVE' | 'REJECT') => {
    const notes = action === 'REJECT'
      ? prompt('Enter rejection reason:')
      : undefined

    if (action === 'REJECT' && !notes) {
      toast.error('Rejection reason is required')
      return
    }

    approvalMutation.mutate({ id, action, notes: notes ?? undefined })
  }

  // Filter materials
  const filteredMaterials = React.useMemo(() => {
    let filtered = materialStock

    if (filterCategory !== 'ALL') {
      filtered = filtered.filter((m: any) => m.category === filterCategory)
    }

    if (searchTerm) {
      const searchLower = searchTerm.toLowerCase()
      filtered = filtered.filter((m: any) => 
        m.material_code?.toLowerCase().includes(searchLower) ||
        m.material_name?.toLowerCase().includes(searchLower)
      )
    }

    return filtered
  }, [materialStock, filterCategory, searchTerm])

  // Get unique categories
  const categories = React.useMemo<string[]>(() => {
    const uniqueCategories = new Set(materialStock.map((m: any) => m.category as string))
    return ['ALL', ...Array.from(uniqueCategories)] as string[]
  }, [materialStock])

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Stock Opname (Cycle Count)</h1>
          <p className="text-gray-500 mt-1">Physical count & variance adjustment with approval workflow</p>
        </div>
        <div className="flex items-center gap-3">
          <Badge variant="warning" className="text-lg px-4 py-2">
            <AlertTriangle className="w-5 h-5 mr-2" />
            {pendingApprovals.length} Pending
          </Badge>
          <Badge variant="outline" className="text-lg px-4 py-2">
            <ClipboardCheck className="w-5 h-5 mr-2" />
            {opnameHistory.length} Completed
          </Badge>
        </div>
      </div>

      {/* Info Card */}
      <Alert className="bg-blue-50 border-blue-200">
        <AlertTriangle className="w-5 h-5 text-blue-600" />
        <AlertDescription>
          <p className="font-semibold text-blue-900 mb-2">
            📋 Stock Opname Process
          </p>
          <div className="text-blue-800 text-sm space-y-1">
            <p><strong>1. Physical Count:</strong> Count actual stock in warehouse</p>
            <p><strong>2. Record Variance:</strong> System will auto-calculate difference</p>
            <p><strong>3. Approval Workflow:</strong> Variance &gt;5% requires Manager approval</p>
            <p><strong>4. Auto Adjustment:</strong> After approval, stock will be adjusted automatically</p>
          </div>
        </AlertDescription>
      </Alert>

      {/* Tabs */}
      <div className="flex items-center gap-4 border-b border-gray-200">
        <button
          className="px-6 py-3 font-semibold border-b-2 border-blue-500 text-blue-600"
        >
          New Opname
        </button>
        <button
          className="px-6 py-3 font-semibold text-gray-600 hover:text-gray-900"
        >
          History
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left: Material Selection */}
        <div className="lg:col-span-1">
          <Card className="p-6">
            <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
              <Search className="w-5 h-5" />
              Select Material
            </h2>
            
            {/* Filter & Search */}
            <div className="space-y-3 mb-4">
              <div>
                <Label htmlFor="category-filter">Category Filter</Label>
                <select
                  id="category-filter"
                  value={filterCategory}
                  onChange={(e: React.ChangeEvent<HTMLSelectElement>) => setFilterCategory(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  {categories.map((cat: string) => (
                    <option key={cat} value={cat}>{cat}</option>
                  ))}
                </select>
              </div>
              
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                <Input
                  type="text"
                  placeholder="Search material..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
            
            <div className="space-y-2 max-h-[500px] overflow-y-auto">
              {filteredMaterials.length === 0 ? (
                <p className="text-gray-500 text-sm text-center py-4">
                  {searchTerm ? 'No materials match your search' : 'No materials available'}
                </p>
              ) : (
                filteredMaterials.map((material: any) => (
                  <button
                    key={material.id}
                    onClick={() => handleMaterialSelect(material)}
                    className={cn(
                      'w-full text-left p-4 rounded-lg border-2 transition-all',
                      selectedMaterial === material.id
                        ? 'border-blue-500 bg-blue-50'
                        : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                    )}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <p className="font-semibold text-gray-900 text-sm">
                          [{material.material_code}]
                        </p>
                        <p className="text-xs text-gray-600 mt-1">{material.material_name}</p>
                        <div className="flex items-center gap-2 mt-2">
                          <Badge variant="outline" className="text-xs">
                            {material.category}
                          </Badge>
                          <span className="text-xs text-gray-600">
                            {formatNumber(material.available_qty)} {material.uom}
                          </span>
                        </div>
                      </div>
                      {selectedMaterial === material.id && (
                        <CheckCircle className="w-5 h-5 text-blue-500 flex-shrink-0" />
                      )}
                    </div>
                  </button>
                ))
              )}
            </div>
          </Card>
        </div>

        {/* Right: Opname Form */}
        <div className="lg:col-span-2">
          {!selectedMaterial ? (
            <Card className="p-12 text-center">
              <ClipboardCheck className="w-16 h-16 text-gray-300 mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-gray-900 mb-2">
                Select Material to Count
              </h3>
              <p className="text-gray-500">
                Choose a material from the list to record physical count
              </p>
            </Card>
          ) : (
            <div className="space-y-6">
              {/* Stock Opname Form */}
              <Card className="p-6">
                <h3 className="text-lg font-semibold mb-4">Record Physical Count</h3>
                
                <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="opname_date">Opname Date</Label>
                      <Input
                        id="opname_date"
                        type="date"
                        {...register('opname_date')}
                        className={errors.opname_date ? 'border-red-500' : ''}
                      />
                      {errors.opname_date && (
                        <p className="text-sm text-red-500 mt-1">{errors.opname_date.message}</p>
                      )}
                    </div>

                    <div>
                      <Label htmlFor="counted_by">Counted By</Label>
                      <Input
                        id="counted_by"
                        {...register('counted_by')}
                        placeholder="Enter your name..."
                        className={errors.counted_by ? 'border-red-500' : ''}
                      />
                      {errors.counted_by && (
                        <p className="text-sm text-red-500 mt-1">{errors.counted_by.message}</p>
                      )}
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="system_qty">System Quantity</Label>
                      <Input
                        id="system_qty"
                        type="number"
                        step="0.01"
                        {...register('system_qty', { valueAsNumber: true })}
                        disabled
                        className="bg-gray-100"
                      />
                      <p className="text-xs text-gray-500 mt-1">Current system stock</p>
                    </div>

                    <div>
                      <Label htmlFor="physical_qty">Physical Count</Label>
                      <Input
                        id="physical_qty"
                        type="number"
                        step="0.01"
                        {...register('physical_qty', { valueAsNumber: true })}
                        className={errors.physical_qty ? 'border-red-500' : ''}
                        placeholder="Enter counted quantity..."
                      />
                      {errors.physical_qty && (
                        <p className="text-sm text-red-500 mt-1">{errors.physical_qty.message}</p>
                      )}
                    </div>
                  </div>

                  <div>
                    <Label htmlFor="variance_reason">Variance Reason (Optional)</Label>
                    <Input
                      id="variance_reason"
                      {...register('variance_reason')}
                      placeholder="Explain variance if any..."
                    />
                  </div>

                  <div>
                    <Label htmlFor="notes">Notes (Optional)</Label>
                    <Input
                      id="notes"
                      {...register('notes')}
                      placeholder="Additional notes..."
                    />
                  </div>

                  {/* Variance Display */}
                  {watchPhysicalQty !== undefined && (
                    <Alert className={cn(
                      varianceStatus.color === 'green' && 'bg-green-50 border-green-200',
                      varianceStatus.color === 'blue' && 'bg-blue-50 border-blue-200',
                      varianceStatus.color === 'yellow' && 'bg-yellow-50 border-yellow-200',
                      varianceStatus.color === 'red' && 'bg-red-50 border-red-200'
                    )}>
                      <div className="flex items-start gap-3">
                        <varianceStatus.icon className={cn(
                          'w-5 h-5 flex-shrink-0 mt-0.5',
                          varianceStatus.color === 'green' && 'text-green-600',
                          varianceStatus.color === 'blue' && 'text-blue-600',
                          varianceStatus.color === 'yellow' && 'text-yellow-600',
                          varianceStatus.color === 'red' && 'text-red-600'
                        )} />
                        <div className="flex-1">
                          <h4 className={cn(
                            'font-semibold mb-2',
                            varianceStatus.color === 'green' && 'text-green-900',
                            varianceStatus.color === 'blue' && 'text-blue-900',
                            varianceStatus.color === 'yellow' && 'text-yellow-900',
                            varianceStatus.color === 'red' && 'text-red-900'
                          )}>
                            Variance Status: {varianceStatus.status}
                          </h4>
                          <div className="grid grid-cols-3 gap-4 text-sm">
                            <div>
                              <p className="text-gray-600">Variance Qty</p>
                              <p className={cn(
                                'font-semibold flex items-center gap-1',
                                watch('variance_qty') > 0 ? 'text-green-600' : 
                                watch('variance_qty') < 0 ? 'text-red-600' : 'text-gray-900'
                              )}>
                                {watch('variance_qty') > 0 && <TrendingUp className="w-4 h-4" />}
                                {watch('variance_qty') < 0 && <TrendingDown className="w-4 h-4" />}
                                {formatNumber(Math.abs(watch('variance_qty') || 0))}
                              </p>
                            </div>
                            <div>
                              <p className="text-gray-600">Variance %</p>
                              <p className="font-semibold text-gray-900">
                                {Math.abs(watch('variance_percentage') || 0).toFixed(2)}%
                              </p>
                            </div>
                            <div>
                              <p className="text-gray-600">Approval</p>
                              <p className="font-semibold text-gray-900">
                                {Math.abs(watch('variance_percentage') || 0) > 5 ? 'Required' : 'Auto'}
                              </p>
                            </div>
                          </div>
                          {Math.abs(watch('variance_percentage') || 0) > 5 && (
                            <p className="text-xs mt-2 text-yellow-800">
                              ⚠️ Variance &gt;5% will require Manager approval before adjustment
                            </p>
                          )}
                        </div>
                      </div>
                    </Alert>
                  )}

                  <Button
                    type="submit"
                    disabled={opnameMutation.isPending}
                    className="w-full bg-blue-600 hover:bg-blue-700"
                  >
                    {opnameMutation.isPending ? (
                      'Recording...'
                    ) : (
                      <>
                        <ClipboardCheck className="w-4 h-4 mr-2" />
                        Record Stock Opname
                      </>
                    )}
                  </Button>
                </form>
              </Card>

              {/* Pending Approvals */}
              {pendingApprovals.length > 0 && (
                <Card className="p-6">
                  <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                    <AlertTriangle className="w-5 h-5 text-yellow-600" />
                    Pending Approvals ({pendingApprovals.length})
                  </h3>
                  <div className="space-y-3">
                    {pendingApprovals.map((opname: any) => (
                      <div key={opname.id} className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                        <div className="flex items-start justify-between mb-2">
                          <div className="flex-1">
                            <p className="font-semibold text-gray-900">
                              [{opname.material_code}] {opname.material_name}
                            </p>
                            <p className="text-sm text-gray-600 mt-1">
                              Counted by: {opname.counted_by} • {formatDate(opname.opname_date)}
                            </p>
                          </div>
                          <Badge variant="warning">
                            {Math.abs(opname.variance_percentage).toFixed(2)}% Variance
                          </Badge>
                        </div>
                        <div className="grid grid-cols-3 gap-4 text-sm mb-3">
                          <div>
                            <p className="text-gray-600">System</p>
                            <p className="font-semibold">{formatNumber(opname.system_qty)}</p>
                          </div>
                          <div>
                            <p className="text-gray-600">Physical</p>
                            <p className="font-semibold">{formatNumber(opname.physical_qty)}</p>
                          </div>
                          <div>
                            <p className="text-gray-600">Variance</p>
                            <p className={cn(
                              'font-semibold',
                              opname.variance_qty > 0 ? 'text-green-600' : 'text-red-600'
                            )}>
                              {opname.variance_qty > 0 ? '+' : ''}{formatNumber(opname.variance_qty)}
                            </p>
                          </div>
                        </div>
                        {opname.variance_reason && (
                          <p className="text-sm text-gray-700 mb-3 italic">
                            Reason: {opname.variance_reason}
                          </p>
                        )}
                        <div className="flex items-center gap-2">
                          <Button
                            size="sm"
                            onClick={() => handleApproval(opname.id, 'APPROVE')}
                            disabled={approvalMutation.isPending}
                            className="bg-green-600 hover:bg-green-700"
                          >
                            <CheckCircle className="w-4 h-4 mr-1" />
                            Approve
                          </Button>
                          <Button
                            size="sm"
                            variant="danger"
                            onClick={() => handleApproval(opname.id, 'REJECT')}
                            disabled={approvalMutation.isPending}
                          >
                            <XCircle className="w-4 h-4 mr-1" />
                            Reject
                          </Button>
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

export default StockOpnamePage
