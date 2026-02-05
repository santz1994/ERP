import React, { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Search, Package, Barcode, QrCode, RefreshCw } from 'lucide-react'
import { api } from '@/api'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Select } from '@/components/ui/select'
import { formatNumber, formatDate, cn } from '@/lib/utils'

interface FGStock {
  id: number
  article_code: string
  article_name: string
  mo_number: string
  total_qty: number
  pcs: number
  cartons: number
  weight_kg: number
  pallets: number
  week?: string
  destination?: string
  location: string
  last_receipt_date: string
}

const FGStockPage: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('')
  const [weekFilter, setWeekFilter] = useState<string>('ALL')
  const [destinationFilter, setDestinationFilter] = useState<string>('ALL')

  const { data: fgStock = [], isLoading, refetch } = useQuery({
    queryKey: ['fg-stock', weekFilter, destinationFilter],
    queryFn: async () => {
      const params: any = {}
      if (weekFilter !== 'ALL') params.week = weekFilter
      if (destinationFilter !== 'ALL') params.destination = destinationFilter
      
      const response = await api.warehouse.getFGStock(params)
      return response.data as FGStock[]
    }
  })

  const filteredStock = fgStock.filter(item =>
    item.article_code.toLowerCase().includes(searchTerm.toLowerCase()) ||
    item.article_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    item.mo_number.toLowerCase().includes(searchTerm.toLowerCase())
  )

  const kpis = {
    totalArticles: fgStock.length,
    totalPcs: fgStock.reduce((sum, item) => sum + item.pcs, 0),
    totalCartons: fgStock.reduce((sum, item) => sum + item.cartons, 0),
    totalPallets: fgStock.reduce((sum, item) => sum + item.pallets, 0)
  }

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Finished Goods Stock</h1>
          <p className="text-gray-500 mt-1">Monitor FG inventory with multi-UOM display (Pcs, Cartons, Weight, Pallets)</p>
        </div>
        <Button variant="outline" onClick={() => refetch()}>
          <RefreshCw className="w-4 h-4 mr-2" />
          Refresh
        </Button>
      </div>

      {/* Info Card - Multi-UOM Logic */}
      <Card variant="bordered" className="p-4 bg-blue-50 border-blue-200">
        <h3 className="text-sm font-semibold text-blue-900 mb-2">🎯 FG Data Recording Logic</h3>
        <div className="text-xs text-blue-700 space-y-1">
          <p>• <strong>Input:</strong> System records qty from MO (single value in pcs)</p>
          <p>• <strong>Display:</strong> Auto-calculated multi-UOM: Pcs, Cartons (÷60), Weight (×article weight), Pallets (÷pallet capacity)</p>
          <p>• <strong>Validation:</strong> FG Receipt qty must match MO Target qty</p>
        </div>
      </Card>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card variant="default" className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Total Articles</p>
              <p className="text-2xl font-bold text-gray-900">{kpis.totalArticles}</p>
            </div>
            <Package className="w-8 h-8 text-blue-500" />
          </div>
        </Card>
        
        <Card variant="default" className="p-4 bg-green-50">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-green-700">Total Pieces</p>
              <p className="text-2xl font-bold text-green-700">{formatNumber(kpis.totalPcs)}</p>
            </div>
            <Package className="w-8 h-8 text-green-600" />
          </div>
        </Card>

        <Card variant="default" className="p-4 bg-purple-50">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-purple-700">Total Cartons</p>
              <p className="text-2xl font-bold text-purple-700">{formatNumber(kpis.totalCartons)}</p>
            </div>
            <Package className="w-8 h-8 text-purple-600" />
          </div>
        </Card>

        <Card variant="default" className="p-4 bg-orange-50">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-orange-700">Total Pallets</p>
              <p className="text-2xl font-bold text-orange-700">{formatNumber(kpis.totalPallets)}</p>
            </div>
            <Package className="w-8 h-8 text-orange-600" />
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
              placeholder="Search article, MO..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10"
            />
          </div>

          <Select value={weekFilter} onValueChange={setWeekFilter}>
            <option value="ALL">All Weeks</option>
            <option value="W01">Week 01</option>
            <option value="W02">Week 02</option>
            <option value="W03">Week 03</option>
            <option value="W04">Week 04</option>
          </Select>

          <Select value={destinationFilter} onValueChange={setDestinationFilter}>
            <option value="ALL">All Destinations</option>
            <option value="SWEDEN">Sweden</option>
            <option value="GERMANY">Germany</option>
            <option value="USA">USA</option>
          </Select>
        </div>
      </Card>

      {/* FG Stock Table */}
      <Card variant="bordered">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50 border-b">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Article</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">MO Number</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Pieces</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Cartons</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Weight (kg)</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Pallets</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Week/Dest</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Location</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Last Receipt</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {isLoading ? (
                <tr>
                  <td colSpan={9} className="px-6 py-12 text-center text-gray-500">Loading...</td>
                </tr>
              ) : filteredStock.length === 0 ? (
                <tr>
                  <td colSpan={9} className="px-6 py-12 text-center text-gray-500">No FG stock found</td>
                </tr>
              ) : (
                filteredStock.map((item) => (
                  <tr key={item.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4">
                      <div className="flex flex-col">
                        <span className="text-sm font-medium text-gray-900">{item.article_code}</span>
                        <span className="text-xs text-gray-500">{item.article_name}</span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="text-sm text-blue-600 hover:underline cursor-pointer">{item.mo_number}</span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="text-sm font-semibold text-gray-900">{formatNumber(item.pcs)}</span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center gap-2">
                        <Package className="w-4 h-4 text-gray-400" />
                        <span className="text-sm font-semibold text-purple-600">{formatNumber(item.cartons)}</span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="text-sm text-gray-900">{formatNumber(item.weight_kg, 2)} kg</span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="text-sm font-semibold text-orange-600">{formatNumber(item.pallets)}</span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {item.week && item.destination ? (
                        <div className="flex flex-col gap-1">
                          <Badge variant="outline" className="text-xs w-fit">Week {item.week}</Badge>
                          <span className="text-xs text-gray-600">{item.destination}</span>
                        </div>
                      ) : (
                        <span className="text-xs text-gray-400">-</span>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="text-xs text-gray-600">{item.location}</span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="text-xs text-gray-500">{formatDate(item.last_receipt_date)}</span>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </Card>

      {/* System Display Logic Note */}
      <Card variant="bordered" className="p-4 bg-gray-50">
        <h4 className="text-sm font-semibold text-gray-900 mb-2">💾 SYSTEM RECORDS vs DISPLAY</h4>
        <div className="text-xs text-gray-700 space-y-1">
          <p><strong>Database Stores:</strong> Total qty in pcs only (from MO target)</p>
          <p><strong>UI Auto-Displays:</strong></p>
          <ul className="list-disc ml-6 mt-1">
            <li>Cartons = qty ÷ 60 (pcs per carton)</li>
            <li>Weight = qty × article_weight</li>
            <li>Pallets = qty ÷ pallet_capacity</li>
          </ul>
          <p className="mt-2"><strong>Example:</strong> MO qty 450 pcs → Display: 450 pcs / 7.5 cartons / 25.2 kg / 1.2 pallets</p>
        </div>
      </Card>
    </div>
  )
}

export default FGStockPage
