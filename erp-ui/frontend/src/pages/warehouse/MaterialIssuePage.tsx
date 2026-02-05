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
  Package, 
  AlertTriangle, 
  CheckCircle, 
  XCircle, 
  Search,
  FileText,
  TrendingDown,
  ArrowRight
} from 'lucide-react'
import { formatNumber, formatDate, cn } from '@/lib/utils'

// Material Issue Schema
const materialIssueSchema = z.object({
  spk_id: z.number().min(1, 'SPK is required'),
  material_id: z.number().min(1, 'Material is required'),
  issue_date: z.string(),
  quantity_issued: z.number().min(0.01, 'Quantity must be greater than 0'),
  notes: z.string().optional()
})

type MaterialIssueForm = z.infer<typeof materialIssueSchema>

const MaterialIssuePage: React.FC = () => {
  const [selectedSPK, setSelectedSPK] = useState<number | null>(null)
  const [searchMaterial, setSearchMaterial] = useState('')
  const [showDebtWarning, setShowDebtWarning] = useState(false)
  
  const queryClient = useQueryClient()

  // Fetch SPK List (APPROVED status only)
  const { data: spkList = [] } = useQuery({
    queryKey: ['spk-list', 'APPROVED'],
    queryFn: () => api.ppic.getSPKList({ status: 'APPROVED' })
  })

  // Fetch SPK Detail with Material Allocation
  const { data: spkDetail } = useQuery({
    queryKey: ['spk-detail', selectedSPK],
    queryFn: () => api.ppic.getSPKDetail(selectedSPK!),
    enabled: !!selectedSPK
  })

  // Fetch Material Stock (Real-time)
  const { data: materialStock = [] } = useQuery({
    queryKey: ['material-stock'],
    queryFn: () => api.warehouse.getMaterialStock()
  })

  // Fetch Material Issue History
  const { data: issueHistory = [] } = useQuery({
    queryKey: ['material-issue-history', selectedSPK],
    queryFn: () => api.warehouse.getMaterialIssueHistory(selectedSPK!),
    enabled: !!selectedSPK
  })

  const {
    register,
    handleSubmit,
    watch,
    setValue,
    reset,
    formState: { errors }
  } = useForm<MaterialIssueForm>({
    resolver: zodResolver(materialIssueSchema),
    defaultValues: {
      issue_date: new Date().toISOString().split('T')[0]
    }
  })

  const selectedMaterialId = watch('material_id')
  const quantityToIssue = watch('quantity_issued')

  // Get current stock for selected material
  const currentStock = React.useMemo(() => {
    if (!selectedMaterialId) return null
    const material = materialStock.find((m: any) => m.material_id === selectedMaterialId)
    return material || null
  }, [selectedMaterialId, materialStock])

  // Calculate if this will create debt
  const willCreateDebt = React.useMemo(() => {
    if (!currentStock || !quantityToIssue) return false
    return quantityToIssue > currentStock.available_qty
  }, [currentStock, quantityToIssue])

  // Debt amount
  const debtAmount = React.useMemo(() => {
    if (!willCreateDebt || !currentStock || !quantityToIssue) return 0
    return quantityToIssue - currentStock.available_qty
  }, [willCreateDebt, currentStock, quantityToIssue])

  // Material Issue Mutation
  const issueMutation = useMutation({
    mutationFn: (data: MaterialIssueForm) => api.warehouse.issueMaterial(data),
    onSuccess: () => {
      toast.success('Material issued successfully')
      queryClient.invalidateQueries({ queryKey: ['material-stock'] })
      queryClient.invalidateQueries({ queryKey: ['material-issue-history'] })
      queryClient.invalidateQueries({ queryKey: ['spk-detail'] })
      reset()
      setShowDebtWarning(false)
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to issue material')
    }
  })

  const onSubmit = (data: MaterialIssueForm) => {
    // Show debt warning confirmation if creating debt
    if (willCreateDebt && !showDebtWarning) {
      setShowDebtWarning(true)
      return
    }

    issueMutation.mutate(data)
  }

  const handleSPKSelect = (spkId: number) => {
    setSelectedSPK(spkId)
    setValue('spk_id', spkId)
    reset({
      spk_id: spkId,
      issue_date: new Date().toISOString().split('T')[0]
    })
    setShowDebtWarning(false)
  }

  const handleMaterialSelect = (materialId: number) => {
    setValue('material_id', materialId)
  }

  // Filter materials by search
  const filteredMaterials = React.useMemo(() => {
    if (!spkDetail?.materials) return []
    
    return spkDetail.materials.filter((m: any) => {
      const searchLower = searchMaterial.toLowerCase()
      return (
        m.material_code?.toLowerCase().includes(searchLower) ||
        m.material_name?.toLowerCase().includes(searchLower)
      )
    })
  }, [spkDetail, searchMaterial])

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Material Issue</h1>
          <p className="text-gray-500 mt-1">Issue materials to production with debt tracking</p>
        </div>
        <Badge variant="outline" className="text-lg px-4 py-2">
          <Package className="w-5 h-5 mr-2" />
          {issueHistory.length} Issues Today
        </Badge>
      </div>

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
                <p className="text-gray-500 text-sm">No approved SPK available</p>
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

        {/* Right: Material Issue Form */}
        <div className="lg:col-span-2">
          {!selectedSPK ? (
            <Card className="p-12 text-center">
              <Package className="w-16 h-16 text-gray-300 mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-gray-900 mb-2">
                Select SPK to Issue Material
              </h3>
              <p className="text-gray-500">
                Choose an approved SPK from the list to start issuing materials
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

              {/* Material Selection */}
              <Card className="p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold">Select Material to Issue</h3>
                  <div className="relative w-64">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                    <Input
                      type="text"
                      placeholder="Search material..."
                      value={searchMaterial}
                      onChange={(e) => setSearchMaterial(e.target.value)}
                      className="pl-10"
                    />
                  </div>
                </div>

                <div className="space-y-3 max-h-[300px] overflow-y-auto">
                  {filteredMaterials.length === 0 ? (
                    <p className="text-gray-500 text-center py-4">
                      {searchMaterial ? 'No materials match your search' : 'No materials allocated for this SPK'}
                    </p>
                  ) : (
                    filteredMaterials.map((material: any) => {
                      const stockInfo = materialStock.find((s: any) => s.material_id === material.material_id)
                      const availableQty = stockInfo?.available_qty || 0
                      const isLowStock = availableQty < material.allocated_qty
                      const isDebt = availableQty < 0

                      return (
                        <button
                          key={material.material_id}
                          onClick={() => handleMaterialSelect(material.material_id)}
                          className={cn(
                            'w-full text-left p-4 rounded-lg border-2 transition-all',
                            selectedMaterialId === material.material_id
                              ? 'border-blue-500 bg-blue-50'
                              : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                          )}
                        >
                          <div className="flex items-start justify-between">
                            <div className="flex-1">
                              <div className="flex items-center gap-2">
                                <p className="font-semibold text-gray-900">
                                  [{material.material_code}]
                                </p>
                                {isDebt && (
                                  <Badge variant="destructive" className="text-xs">
                                    DEBT
                                  </Badge>
                                )}
                                {!isDebt && isLowStock && (
                                  <Badge variant="warning" className="text-xs">
                                    LOW STOCK
                                  </Badge>
                                )}
                              </div>
                              <p className="text-sm text-gray-600 mt-1">{material.material_name}</p>
                              <div className="flex items-center gap-4 mt-2 text-sm">
                                <span className="text-gray-600">
                                  Required: <strong>{formatNumber(material.allocated_qty)} {material.uom}</strong>
                                </span>
                                <span className={cn(
                                  'font-semibold',
                                  isDebt ? 'text-red-600' : isLowStock ? 'text-yellow-600' : 'text-green-600'
                                )}>
                                  Stock: {formatNumber(availableQty)} {material.uom}
                                </span>
                              </div>
                            </div>
                            {selectedMaterialId === material.material_id && (
                              <CheckCircle className="w-5 h-5 text-blue-500 flex-shrink-0" />
                            )}
                          </div>
                        </button>
                      )
                    })
                  )}
                </div>
              </Card>

              {/* Issue Form */}
              {selectedMaterialId && (
                <Card className="p-6">
                  <h3 className="text-lg font-semibold mb-4">Issue Details</h3>
                  
                  <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <Label htmlFor="issue_date">Issue Date</Label>
                        <Input
                          id="issue_date"
                          type="date"
                          {...register('issue_date')}
                          className={errors.issue_date ? 'border-red-500' : ''}
                        />
                        {errors.issue_date && (
                          <p className="text-sm text-red-500 mt-1">{errors.issue_date.message}</p>
                        )}
                      </div>

                      <div>
                        <Label htmlFor="quantity_issued">Quantity to Issue</Label>
                        <div className="flex items-center gap-2">
                          <Input
                            id="quantity_issued"
                            type="number"
                            step="0.01"
                            {...register('quantity_issued', { valueAsNumber: true })}
                            className={errors.quantity_issued ? 'border-red-500' : ''}
                          />
                          <span className="text-sm text-gray-600 whitespace-nowrap">
                            {currentStock?.uom || 'UOM'}
                          </span>
                        </div>
                        {errors.quantity_issued && (
                          <p className="text-sm text-red-500 mt-1">{errors.quantity_issued.message}</p>
                        )}
                      </div>
                    </div>

                    <div>
                      <Label htmlFor="notes">Notes (Optional)</Label>
                      <Input
                        id="notes"
                        {...register('notes')}
                        placeholder="Enter any notes..."
                      />
                    </div>

                    {/* Stock Status Alert */}
                    {currentStock && (
                      <Alert className={cn(
                        willCreateDebt ? 'bg-red-50 border-red-200' : 'bg-blue-50 border-blue-200'
                      )}>
                        <div className="flex items-start gap-3">
                          {willCreateDebt ? (
                            <AlertTriangle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
                          ) : (
                            <CheckCircle className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
                          )}
                          <div className="flex-1">
                            <h4 className={cn(
                              'font-semibold mb-2',
                              willCreateDebt ? 'text-red-900' : 'text-blue-900'
                            )}>
                              {willCreateDebt ? 'WARNING: This will create Material Debt' : 'Stock Status'}
                            </h4>
                            <div className="grid grid-cols-3 gap-4 text-sm">
                              <div>
                                <p className="text-gray-600">Current Stock</p>
                                <p className="font-semibold text-gray-900">
                                  {formatNumber(currentStock.available_qty)} {currentStock.uom}
                                </p>
                              </div>
                              <div>
                                <p className="text-gray-600">To Issue</p>
                                <p className="font-semibold text-gray-900">
                                  {formatNumber(quantityToIssue || 0)} {currentStock.uom}
                                </p>
                              </div>
                              <div>
                                <p className="text-gray-600">After Issue</p>
                                <p className={cn(
                                  'font-semibold',
                                  willCreateDebt ? 'text-red-600' : 'text-green-600'
                                )}>
                                  {formatNumber((currentStock.available_qty || 0) - (quantityToIssue || 0))} {currentStock.uom}
                                  {willCreateDebt && (
                                    <span className="ml-2 text-red-700">
                                      (Debt: {formatNumber(debtAmount)})
                                    </span>
                                  )}
                                </p>
                              </div>
                            </div>
                          </div>
                        </div>
                      </Alert>
                    )}

                    {/* Debt Confirmation */}
                    {showDebtWarning && (
                      <Alert className="bg-yellow-50 border-yellow-200">
                        <AlertTriangle className="w-5 h-5 text-yellow-600" />
                        <AlertDescription>
                          <p className="font-semibold text-yellow-900 mb-2">
                            Confirm Material Debt Creation
                          </p>
                          <p className="text-yellow-800 text-sm">
                            You are about to create a debt of <strong>{formatNumber(debtAmount)} {currentStock?.uom}</strong>.
                            This means production will run with negative stock. Are you sure you want to proceed?
                          </p>
                        </AlertDescription>
                      </Alert>
                    )}

                    <div className="flex items-center gap-3 pt-4">
                      <Button
                        type="submit"
                        disabled={issueMutation.isPending}
                        className={cn(
                          'flex-1',
                          willCreateDebt ? 'bg-red-600 hover:bg-red-700' : 'bg-blue-600 hover:bg-blue-700'
                        )}
                      >
                        {issueMutation.isPending ? (
                          'Issuing...'
                        ) : willCreateDebt && showDebtWarning ? (
                          <>
                            <TrendingDown className="w-4 h-4 mr-2" />
                            Confirm Issue with Debt
                          </>
                        ) : (
                          <>
                            <ArrowRight className="w-4 h-4 mr-2" />
                            Issue Material
                          </>
                        )}
                      </Button>
                      {showDebtWarning && (
                        <Button
                          type="button"
                          variant="outline"
                          onClick={() => setShowDebtWarning(false)}
                        >
                          Cancel
                        </Button>
                      )}
                    </div>
                  </form>
                </Card>
              )}

              {/* Issue History */}
              {issueHistory.length > 0 && (
                <Card className="p-6">
                  <h3 className="text-lg font-semibold mb-4">Issue History for This SPK</h3>
                  <div className="space-y-3">
                    {issueHistory.map((issue: any) => (
                      <div key={issue.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                        <div className="flex-1">
                          <p className="font-medium text-gray-900">
                            [{issue.material_code}] {issue.material_name}
                          </p>
                          <p className="text-sm text-gray-600 mt-1">
                            {formatNumber(issue.quantity_issued)} {issue.uom} • {formatDate(issue.issue_date)}
                          </p>
                        </div>
                        {issue.created_debt && (
                          <Badge variant="destructive">
                            <TrendingDown className="w-3 h-3 mr-1" />
                            Debt Created
                          </Badge>
                        )}
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

export default MaterialIssuePage
