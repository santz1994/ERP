import React, { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Search, Package, AlertTriangle, CheckCircle, XCircle, RefreshCw } from 'lucide-react'
import { api } from '@/api'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Select } from '@/components/ui/select'
import { formatNumber, cn } from '@/lib/utils'

interface MaterialAllocation {
  id: number
  spk_id: number
  spk_number: string
  material_id: number
  material_code: string
  material_name: string
  required_qty: number
  allocated_qty: number
  available_stock: number
  uom: string
  status: 'ALLOCATED' | 'PARTIAL' | 'INSUFFICIENT' | 'RELEASED'
  allocation_date?: string
  release_date?: string
}

const MaterialAllocationPage: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState<string>('ALL')
  const [departmentFilter, setDepartmentFilter] = useState<string>('ALL')

  // Fetch material allocations
  const { data: allocations = [], isLoading, refetch } = useQuery({
    queryKey: ['material-allocations', statusFilter, departmentFilter],
    queryFn: async () => {
      const params: any = {}
      if (statusFilter !== 'ALL') params.status = statusFilter
      if (departmentFilter !== 'ALL') params.department = departmentFilter
      
      const response = await api.ppic.getMaterialAllocations(params)
      return response.data as MaterialAllocation[]
    }
  })

  // Filter by search term
  const filteredAllocations = allocations.filter(alloc => 
    alloc.spk_number.toLowerCase().includes(searchTerm.toLowerCase()) ||
    alloc.material_code.toLowerCase().includes(searchTerm.toLowerCase()) ||
    alloc.material_name.toLowerCase().includes(searchTerm.toLowerCase())
  )

  // Calculate KPIs
  const kpis = {
    total: allocations.length,
    allocated: allocations.filter(a => a.status === 'ALLOCATED').length,
    partial: allocations.filter(a => a.status === 'PARTIAL').length,
    insufficient: allocations.filter(a => a.status === 'INSUFFICIENT').length,
    released: allocations.filter(a => a.status === 'RELEASED').length
  }

  // Group by material
  const materialSummary = allocations.reduce((acc, alloc) => {
    const key = alloc.material_code
    if (!acc[key]) {
      acc[key] = {
        material_code: alloc.material_code,
        material_name: alloc.material_name,
        total_required: 0,
        total_allocated: 0,
        available_stock: alloc.available_stock,
        uom: alloc.uom,
        allocations: []
      }
    }
    acc[key].total_required += alloc.required_qty
    acc[key].total_allocated += alloc.allocated_qty
    acc[key].allocations.push(alloc)
    return acc
  }, {} as Record<string, any>)

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'ALLOCATED':
        return 'bg-green-100 text-green-800'
      case 'PARTIAL':
        return 'bg-yellow-100 text-yellow-800'
      case 'INSUFFICIENT':
        return 'bg-red-100 text-red-800'
      case 'RELEASED':
        return 'bg-gray-100 text-gray-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  const getStockStatus = (available: number, required: number) => {
    const ratio = (available / required) * 100
    if (ratio >= 100) return { icon: CheckCircle, color: 'text-green-600', label: 'Sufficient' }
    if (ratio >= 50) return { icon: AlertTriangle, color: 'text-yellow-600', label: 'Partial' }
    return { icon: XCircle, color: 'text-red-600', label: 'Insufficient' }
  }

  return (
    <div className="space-y-6 p-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Material Allocation</h1>
          <p className="text-gray-500 mt-1">Monitor material reservations and availability</p>
        </div>
        <div className="flex gap-3">
          <Button variant="outline" onClick={() => refetch()}>
            <RefreshCw className="w-4 h-4 mr-2" />
            Refresh
          </Button>
          <Button variant="primary">
            <Package className="w-4 h-4 mr-2" />
            Allocate Materials
          </Button>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
        <Card variant="default" className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Total Allocations</p>
              <p className="text-2xl font-bold text-gray-900">{kpis.total}</p>
            </div>
            <Package className="w-8 h-8 text-blue-500" />
          </div>
        </Card>
        
        <Card variant="default" className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Fully Allocated</p>
              <p className="text-2xl font-bold text-green-600">{kpis.allocated}</p>
            </div>
            <CheckCircle className="w-8 h-8 text-green-500" />
          </div>
        </Card>

        <Card variant="default" className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Partial</p>
              <p className="text-2xl font-bold text-yellow-600">{kpis.partial}</p>
            </div>
            <AlertTriangle className="w-8 h-8 text-yellow-500" />
          </div>
        </Card>

        <Card variant="default" className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Insufficient</p>
              <p className="text-2xl font-bold text-red-600">{kpis.insufficient}</p>
            </div>
            <XCircle className="w-8 h-8 text-red-500" />
          </div>
        </Card>

        <Card variant="default" className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Released</p>
              <p className="text-2xl font-bold text-gray-600">{kpis.released}</p>
            </div>
            <Package className="w-8 h-8 text-gray-500" />
          </div>
        </Card>
      </div>

      {/* Filters */}
      <Card variant="bordered" className="p-4">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
            <Input
              type="text"
              placeholder="Search SPK, Material..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10"
            />
          </div>

          <Select
            value={statusFilter}
            onValueChange={setStatusFilter}
          >
            <option value="ALL">All Status</option>
            <option value="ALLOCATED">Fully Allocated</option>
            <option value="PARTIAL">Partial</option>
            <option value="INSUFFICIENT">Insufficient</option>
            <option value="RELEASED">Released</option>
          </Select>

          <Select
            value={departmentFilter}
            onValueChange={setDepartmentFilter}
          >
            <option value="ALL">All Departments</option>
            <option value="CUTTING">Cutting</option>
            <option value="EMBROIDERY">Embroidery</option>
            <option value="SEWING">Sewing</option>
            <option value="FINISHING">Finishing</option>
            <option value="PACKING">Packing</option>
          </Select>
        </div>
      </Card>

      {/* Material Summary by Material Code */}
      <div className="space-y-4">
        <h2 className="text-xl font-semibold text-gray-900">Material Summary</h2>
        {Object.values(materialSummary).map((material: any) => {
          const stockStatus = getStockStatus(material.available_stock, material.total_required)
          const StatusIcon = stockStatus.icon
          
          return (
            <Card key={material.material_code} variant="bordered" className="p-4">
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <div className="flex items-center gap-3">
                    <h3 className="text-lg font-semibold text-gray-900">{material.material_code}</h3>
                    <Badge className={cn('text-xs', stockStatus.color)}>
                      {stockStatus.label}
                    </Badge>
                  </div>
                  <p className="text-sm text-gray-600 mt-1">{material.material_name}</p>
                </div>
                <StatusIcon className={cn('w-6 h-6', stockStatus.color)} />
              </div>

              {/* Stock Overview */}
              <div className="grid grid-cols-3 gap-4 mb-4 p-4 bg-gray-50 rounded-lg">
                <div>
                  <p className="text-xs text-gray-500">Available Stock</p>
                  <p className="text-lg font-semibold text-gray-900">
                    {formatNumber(material.available_stock)} {material.uom}
                  </p>
                </div>
                <div>
                  <p className="text-xs text-gray-500">Total Required</p>
                  <p className="text-lg font-semibold text-blue-600">
                    {formatNumber(material.total_required)} {material.uom}
                  </p>
                </div>
                <div>
                  <p className="text-xs text-gray-500">Total Allocated</p>
                  <p className="text-lg font-semibold text-green-600">
                    {formatNumber(material.total_allocated)} {material.uom}
                  </p>
                </div>
              </div>

              {/* Progress Bar */}
              <div className="mb-4">
                <div className="flex justify-between text-xs text-gray-600 mb-1">
                  <span>Allocation Progress</span>
                  <span>{((material.total_allocated / material.total_required) * 100).toFixed(1)}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className={cn(
                      'h-2 rounded-full transition-all',
                      material.total_allocated >= material.total_required ? 'bg-green-500' : 'bg-yellow-500'
                    )}
                    style={{ width: `${Math.min((material.total_allocated / material.total_required) * 100, 100)}%` }}
                  />
                </div>
              </div>

              {/* Allocation Details */}
              <div className="space-y-2">
                <p className="text-sm font-medium text-gray-700">Allocated to SPKs:</p>
                <div className="overflow-x-auto">
                  <table className="min-w-full text-sm">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-3 py-2 text-left text-xs font-medium text-gray-500">SPK Number</th>
                        <th className="px-3 py-2 text-left text-xs font-medium text-gray-500">Required</th>
                        <th className="px-3 py-2 text-left text-xs font-medium text-gray-500">Allocated</th>
                        <th className="px-3 py-2 text-left text-xs font-medium text-gray-500">Status</th>
                        <th className="px-3 py-2 text-left text-xs font-medium text-gray-500">Action</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-200">
                      {material.allocations.map((alloc: MaterialAllocation) => (
                        <tr key={alloc.id}>
                          <td className="px-3 py-2 whitespace-nowrap">
                            <span className="text-blue-600 hover:underline cursor-pointer">
                              {alloc.spk_number}
                            </span>
                          </td>
                          <td className="px-3 py-2 whitespace-nowrap">
                            {formatNumber(alloc.required_qty)} {alloc.uom}
                          </td>
                          <td className="px-3 py-2 whitespace-nowrap font-semibold">
                            {formatNumber(alloc.allocated_qty)} {alloc.uom}
                          </td>
                          <td className="px-3 py-2 whitespace-nowrap">
                            <Badge className={cn('text-xs', getStatusColor(alloc.status))}>
                              {alloc.status}
                            </Badge>
                          </td>
                          <td className="px-3 py-2 whitespace-nowrap">
                            {alloc.status === 'ALLOCATED' && !alloc.release_date ? (
                              <Button variant="outline" size="sm">
                                Release
                              </Button>
                            ) : alloc.status === 'RELEASED' ? (
                              <span className="text-xs text-gray-500">Released</span>
                            ) : (
                              <Button variant="outline" size="sm">
                                Re-allocate
                              </Button>
                            )}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </Card>
          )
        })}
      </div>

      {/* Empty State */}
      {!isLoading && Object.keys(materialSummary).length === 0 && (
        <Card variant="bordered" className="p-12 text-center">
          <Package className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-900 mb-2">No material allocations found</h3>
          <p className="text-gray-500">Create SPKs to allocate materials</p>
        </Card>
      )}
    </div>
  )
}

export default MaterialAllocationPage
