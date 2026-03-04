/**
 * PO List & Tracking Page — /purchasing/po
 * Full purchase order list with advanced filters, search, and status tracking.
 */

import { useState, useMemo } from 'react'
import { useQuery } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { format } from 'date-fns'
import {
  ArrowLeft, Search, Filter, RefreshCw,
  FileText, Clock, PackageCheck, CheckCircle, XCircle,
  ShoppingCart, Download, ChevronLeft, ChevronRight,
} from 'lucide-react'
import { apiClient } from '@/api/client'
import { Card } from '@/components/ui/card'
import { formatCurrency, getStatusBadge } from '@/lib/utils'
import PODetailModal from '@/components/purchasing/PODetailModal'

// ── Types ────────────────────────────────────────────────────────────────────

interface PurchaseOrder {
  id: number
  po_number: string
  supplier_id: number
  supplier_name?: string
  order_date: string
  expected_date?: string
  status: string
  total_amount: number
  currency: string
  po_type?: string
  week?: string
  destination?: string
}

const PO_STATUSES = ['Draft', 'Sent', 'Received', 'Done', 'Cancelled']
const PO_TYPES = ['KAIN', 'LABEL', 'ACCESSORIES']
const PAGE_SIZE = 20

// ── Status badge helper ───────────────────────────────────────────────────────

const StatusBadge = ({ status }: { status: string }) => {
  const map: Record<string, string> = {
    Draft:     'bg-gray-100 text-gray-600',
    Sent:      'bg-blue-100 text-blue-700',
    Received:  'bg-orange-100 text-orange-700',
    Done:      'bg-green-100 text-green-700',
    Cancelled: 'bg-red-100 text-red-600',
  }
  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold ${map[status] ?? 'bg-gray-100 text-gray-600'}`}>
      {status}
    </span>
  )
}

const TypeBadge = ({ type }: { type?: string }) => {
  const map: Record<string, string> = {
    KAIN:        'bg-purple-100 text-purple-800',
    LABEL:       'bg-blue-100 text-blue-800',
    ACCESSORIES: 'bg-amber-100 text-amber-800',
  }
  if (!type) return <span className="text-gray-400 text-xs">—</span>
  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold ${map[type] ?? 'bg-gray-100 text-gray-700'}`}>
      {type}
    </span>
  )
}

// ── Main Component ────────────────────────────────────────────────────────────

export default function POListPage() {
  const navigate = useNavigate()

  // Filter state
  const [search, setSearch] = useState('')
  const [filterStatus, setFilterStatus] = useState('')
  const [filterType, setFilterType] = useState('')
  const [filterDateFrom, setFilterDateFrom] = useState('')
  const [filterDateTo, setFilterDateTo] = useState('')
  const [page, setPage] = useState(1)
  const [selectedPOId, setSelectedPOId] = useState<number | null>(null)

  // Fetch all POs (backend returns array)
  const { data: allPOs = [], isLoading, refetch } = useQuery<PurchaseOrder[]>({
    queryKey: ['po-list-all'],
    queryFn: () => apiClient.get('/purchasing/purchase-orders'),
    refetchInterval: 60_000,
  })

  // Client-side filter + paginate
  const filtered = useMemo(() => {
    let result = allPOs
    if (search) {
      const q = search.toLowerCase()
      result = result.filter(po =>
        po.po_number?.toLowerCase().includes(q) ||
        (po.supplier_name ?? '').toLowerCase().includes(q) ||
        (po.week ?? '').toLowerCase().includes(q) ||
        (po.destination ?? '').toLowerCase().includes(q)
      )
    }
    if (filterStatus) result = result.filter(po => po.status === filterStatus)
    if (filterType)   result = result.filter(po => po.po_type === filterType)
    if (filterDateFrom) result = result.filter(po => po.order_date >= filterDateFrom)
    if (filterDateTo)   result = result.filter(po => po.order_date <= filterDateTo)
    return result
  }, [allPOs, search, filterStatus, filterType, filterDateFrom, filterDateTo])

  const totalPages = Math.max(1, Math.ceil(filtered.length / PAGE_SIZE))
  const paginated = filtered.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE)

  // Stats from filtered result
  const stats = {
    total:    filtered.length,
    draft:    filtered.filter(p => p.status === 'Draft').length,
    sent:     filtered.filter(p => p.status === 'Sent').length,
    received: filtered.filter(p => p.status === 'Received').length,
    done:     filtered.filter(p => p.status === 'Done').length,
  }

  const clearFilters = () => {
    setSearch(''); setFilterStatus(''); setFilterType('')
    setFilterDateFrom(''); setFilterDateTo(''); setPage(1)
  }
  const hasFilters = !!(search || filterStatus || filterType || filterDateFrom || filterDateTo)

  // CSV export
  const exportCSV = () => {
    const header = 'PO Number,Type,Supplier,Date,Expected,Status,Amount'
    const rows = filtered.map(po =>
      [po.po_number, po.po_type ?? '', po.supplier_name ?? po.supplier_id,
       po.order_date, po.expected_date ?? '', po.status, po.total_amount].join(',')
    )
    const blob = new Blob([header + '\n' + rows.join('\n')], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a'); a.href = url
    a.download = `PO_List_${format(new Date(), 'yyyy-MM-dd')}.csv`; a.click()
    URL.revokeObjectURL(url)
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      {/* Header */}
      <div className="mb-6 flex items-center justify-between flex-wrap gap-3">
        <div className="flex items-center gap-3">
          <button onClick={() => navigate('/purchasing')} className="p-2 rounded-lg hover:bg-gray-200 transition-colors">
            <ArrowLeft className="w-5 h-5 text-gray-600" />
          </button>
          <div>
            <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
              <ShoppingCart className="w-7 h-7 text-blue-600" />
              PO List & Tracking
            </h1>
            <p className="text-sm text-gray-500 mt-0.5">
              {isLoading ? 'Loading…' : `${allPOs.length} total purchase orders`}
            </p>
          </div>
        </div>
        <div className="flex gap-2">
          <button onClick={() => refetch()} className="flex items-center gap-1.5 px-3 py-2 text-sm bg-white border rounded-lg hover:bg-gray-50">
            <RefreshCw className="w-4 h-4" /> Refresh
          </button>
          <button onClick={exportCSV} className="flex items-center gap-1.5 px-3 py-2 text-sm bg-white border rounded-lg hover:bg-gray-50">
            <Download className="w-4 h-4" /> Export CSV
          </button>
        </div>
      </div>

      {/* Status KPI strip */}
      <div className="grid grid-cols-2 sm:grid-cols-5 gap-3 mb-6">
        {[
          { label: 'All',      count: stats.total,    icon: FileText,     color: 'text-gray-700',   bg: 'bg-gray-50',    f: '' },
          { label: 'Draft',    count: stats.draft,    icon: FileText,     color: 'text-gray-500',   bg: 'bg-gray-50',    f: 'Draft' },
          { label: 'Sent',     count: stats.sent,     icon: Clock,        color: 'text-blue-600',   bg: 'bg-blue-50',    f: 'Sent' },
          { label: 'Received', count: stats.received, icon: PackageCheck, color: 'text-orange-600', bg: 'bg-orange-50',  f: 'Received' },
          { label: 'Done',     count: stats.done,     icon: CheckCircle,  color: 'text-green-600',  bg: 'bg-green-50',   f: 'Done' },
        ].map(({ label, count, icon: Icon, color, bg, f }) => (
          <button
            key={label}
            onClick={() => { setFilterStatus(f); setPage(1) }}
            className={`${bg} rounded-xl p-4 text-left border transition-all ${filterStatus === f ? 'ring-2 ring-blue-400 border-blue-300' : 'border-gray-200 hover:border-gray-300'}`}
          >
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-500">{label}</span>
              <Icon className={`w-4 h-4 ${color}`} />
            </div>
            <p className={`text-2xl font-bold mt-1 ${color}`}>{count}</p>
          </button>
        ))}
      </div>

      {/* Filters */}
      <Card className="bg-white shadow-sm mb-5">
        <div className="p-4 flex flex-wrap gap-3 items-end">
          {/* Search */}
          <div className="relative flex-1 min-w-48">
            <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
            <input
              value={search}
              onChange={e => { setSearch(e.target.value); setPage(1) }}
              placeholder="Search PO number, supplier, week…"
              className="w-full pl-9 pr-3 py-2 text-sm border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          {/* Status */}
          <select value={filterStatus} onChange={e => { setFilterStatus(e.target.value); setPage(1) }} className="border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
            <option value="">All Status</option>
            {PO_STATUSES.map(s => <option key={s} value={s}>{s}</option>)}
          </select>
          {/* Type */}
          <select value={filterType} onChange={e => { setFilterType(e.target.value); setPage(1) }} className="border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
            <option value="">All Types</option>
            {PO_TYPES.map(t => <option key={t} value={t}>{t}</option>)}
          </select>
          {/* Date range */}
          <div className="flex items-center gap-2">
            <input type="date" value={filterDateFrom} onChange={e => { setFilterDateFrom(e.target.value); setPage(1) }} className="border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
            <span className="text-gray-400 text-sm">→</span>
            <input type="date" value={filterDateTo} onChange={e => { setFilterDateTo(e.target.value); setPage(1) }} className="border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
          </div>
          {hasFilters && (
            <button onClick={clearFilters} className="flex items-center gap-1.5 px-3 py-2 text-sm text-red-600 border border-red-200 rounded-lg hover:bg-red-50">
              <XCircle className="w-4 h-4" /> Clear
            </button>
          )}
        </div>
      </Card>

      {/* Table */}
      <Card className="bg-white shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-100">
            <thead className="bg-gray-50">
              <tr>
                {['PO Number', 'Type', 'Supplier', 'Week', 'Destination', 'Order Date', 'Amount', 'Status', ''].map(h => (
                  <th key={h} className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wide">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-50">
              {isLoading ? (
                <tr><td colSpan={9} className="py-16 text-center">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto" />
                </td></tr>
              ) : paginated.length === 0 ? (
                <tr><td colSpan={9} className="py-16 text-center">
                  <ShoppingCart className="w-10 h-10 text-gray-300 mx-auto mb-2" />
                  <p className="text-gray-500 text-sm">{hasFilters ? 'No POs match your filters' : 'No purchase orders yet'}</p>
                </td></tr>
              ) : paginated.map(po => (
                <tr
                  key={po.id}
                  className="hover:bg-blue-50 cursor-pointer transition-colors"
                  onClick={() => setSelectedPOId(po.id)}
                >
                  <td className="px-4 py-3">
                    <span className="font-mono font-semibold text-sm text-gray-900">{po.po_number}</span>
                  </td>
                  <td className="px-4 py-3"><TypeBadge type={po.po_type} /></td>
                  <td className="px-4 py-3 text-sm text-gray-700">{po.supplier_name ?? `Supplier #${po.supplier_id}`}</td>
                  <td className="px-4 py-3 text-sm text-gray-500">{po.week ?? '—'}</td>
                  <td className="px-4 py-3 text-sm text-gray-500">{po.destination ?? '—'}</td>
                  <td className="px-4 py-3 text-sm text-gray-500">
                    {po.order_date ? format(new Date(po.order_date), 'dd MMM yyyy') : '—'}
                  </td>
                  <td className="px-4 py-3 text-sm font-medium text-gray-900">{formatCurrency(po.total_amount)}</td>
                  <td className="px-4 py-3"><StatusBadge status={po.status} /></td>
                  <td className="px-4 py-3 text-xs text-blue-600 font-medium">View →</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        {filtered.length > PAGE_SIZE && (
          <div className="px-4 py-3 border-t bg-gray-50 flex items-center justify-between text-sm text-gray-500">
            <span>Showing {(page - 1) * PAGE_SIZE + 1}–{Math.min(page * PAGE_SIZE, filtered.length)} of {filtered.length}</span>
            <div className="flex items-center gap-1">
              <button disabled={page === 1} onClick={() => setPage(p => p - 1)} className="p-1.5 rounded border disabled:opacity-40 hover:bg-gray-100">
                <ChevronLeft className="w-4 h-4" />
              </button>
              {Array.from({ length: Math.min(totalPages, 7) }, (_, i) => {
                const pg = totalPages <= 7 ? i + 1 : page <= 4 ? i + 1 : page + i - 3
                if (pg < 1 || pg > totalPages) return null
                return (
                  <button key={pg} onClick={() => setPage(pg)}
                    className={`w-8 h-8 rounded border text-xs font-medium ${page === pg ? 'bg-blue-600 text-white border-blue-600' : 'hover:bg-gray-100'}`}>
                    {pg}
                  </button>
                )
              })}
              <button disabled={page === totalPages} onClick={() => setPage(p => p + 1)} className="p-1.5 rounded border disabled:opacity-40 hover:bg-gray-100">
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        )}
      </Card>

      {/* Detail Modal */}
      <PODetailModal
        poId={selectedPOId}
        isOpen={selectedPOId !== null}
        onClose={() => setSelectedPOId(null)}
        onStatusChanged={() => { setSelectedPOId(null); refetch() }}
      />
    </div>
  )
}
