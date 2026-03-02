/**
 * BOM Management Page
 * View, add, edit, delete BOM Headers and their component lines.
 */

import React, { useState, useEffect, useCallback } from 'react'
import { apiClient } from '@/api'
import { useAuthStore } from '@/store'
import { ChevronDown, ChevronRight, Plus, Pencil, Trash2, RefreshCw } from 'lucide-react'

// ─── Types ────────────────────────────────────────────────────────────────────

interface BOMDetail {
  id: number
  component_id: number
  component_code: string
  component_name: string
  component_uom: string
  component_type: string
  category_name?: string
  qty_needed: number
  wastage_percent: number
}

interface BOMHeader {
  id: number
  product_id: number
  product_code: string
  product_name: string
  product_type: string
  category_name?: string
  revision: string
  bom_type: string
  qty_output: number
  is_active: boolean
  detail_count: number | null
  revision_reason?: string
  created_at?: string
  details?: BOMDetail[]
}

interface ProductOption { id: number; code: string; name: string; uom: string }

const ADMIN_ROLES = ['Admin', 'Superadmin', 'Developer']
const BOM_TYPES = ['manufacturing', 'subcontract', 'kit']

// ─── Modal ────────────────────────────────────────────────────────────────────

const Modal: React.FC<{ title: string; onClose: () => void; wide?: boolean; children: React.ReactNode }> = ({ title, onClose, wide, children }) => (
  <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
    <div className={`bg-white rounded-xl shadow-2xl w-full ${wide ? 'max-w-3xl' : 'max-w-lg'} max-h-[90vh] overflow-y-auto`}>
      <div className="flex items-center justify-between p-5 border-b sticky top-0 bg-white z-10">
        <h2 className="text-xl font-bold text-gray-800">{title}</h2>
        <button onClick={onClose} className="text-gray-400 hover:text-gray-600 text-2xl leading-none">&times;</button>
      </div>
      <div className="p-5">{children}</div>
    </div>
  </div>
)

// ─── Main Page ────────────────────────────────────────────────────────────────

const BOMManagementPage: React.FC = () => {
  const { user } = useAuthStore()
  const isAdmin = ADMIN_ROLES.includes(user?.role ?? '')

  const [headers, setHeaders] = useState<BOMHeader[]>([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [activeOnly, setActiveOnly] = useState(false)
  const [loading, setLoading] = useState(false)

  // Expanded rows → load details on expand
  const [expanded, setExpanded] = useState<Set<number>>(new Set())
  const [detailsMap, setDetailsMap] = useState<Record<number, BOMDetail[]>>({})
  const [detailsLoading, setDetailsLoading] = useState<Set<number>>(new Set())

  // Product options for dropdowns
  const [productOptions, setProductOptions] = useState<ProductOption[]>([])

  // Header modal
  const [showHeaderModal, setShowHeaderModal] = useState(false)
  const [editingHeader, setEditingHeader] = useState<BOMHeader | null>(null)
  const [headerForm, setHeaderForm] = useState({ product_id: '', revision: 'Rev 1.0', bom_type: 'manufacturing', qty_output: '1', is_active: true, revision_reason: '' })

  // Detail modal
  const [showDetailModal, setShowDetailModal] = useState(false)
  const [detailModalHeaderId, setDetailModalHeaderId] = useState<number | null>(null)
  const [editingDetail, setEditingDetail] = useState<BOMDetail | null>(null)
  const [detailForm, setDetailForm] = useState({ component_id: '', qty_needed: '1', wastage_percent: '0' })

  // ── Fetch functions ──────────────────────────────────────────────────────────

  const fetchHeaders = useCallback(async () => {
    setLoading(true)
    try {
      const params = new URLSearchParams({ page: String(page), page_size: '50' })
      if (search) params.set('search', search)
      if (activeOnly) params.set('active_only', 'true')
      const res = await apiClient.get(`/bom-management/headers?${params}`)
      setHeaders(res.data.items)
      setTotal(res.data.total)
    } catch (e) { console.error(e) } finally { setLoading(false) }
  }, [page, search, activeOnly])

  const fetchProductOptions = useCallback(async () => {
    try {
      const res = await apiClient.get('/masterdata/products?page_size=500')
      setProductOptions(res.data.items.map((p: any) => ({ id: p.id, code: p.code, name: p.name, uom: p.uom })))
    } catch (e) { console.error(e) }
  }, [])

  useEffect(() => { fetchHeaders() }, [fetchHeaders])
  useEffect(() => { fetchProductOptions() }, [fetchProductOptions])

  // ── Expand / load details ────────────────────────────────────────────────────

  const toggleExpand = async (headerId: number) => {
    const next = new Set(expanded)
    if (next.has(headerId)) { next.delete(headerId); setExpanded(next); return }
    next.add(headerId); setExpanded(next)
    if (detailsMap[headerId]) return  // already loaded
    setDetailsLoading(prev => new Set(prev).add(headerId))
    try {
      const res = await apiClient.get(`/bom-management/headers/${headerId}`)
      setDetailsMap(prev => ({ ...prev, [headerId]: res.data.details ?? [] }))
    } catch (e) { console.error(e) }
    setDetailsLoading(prev => { const s = new Set(prev); s.delete(headerId); return s })
  }

  // ── Header CRUD ──────────────────────────────────────────────────────────────

  const handleSaveHeader = async (e: React.FormEvent) => {
    e.preventDefault()
    const payload = { ...headerForm, product_id: Number(headerForm.product_id), qty_output: parseFloat(headerForm.qty_output) }
    try {
      if (editingHeader) {
        await apiClient.put(`/bom-management/headers/${editingHeader.id}`, payload)
        // Invalidate cached details for this header
        setDetailsMap(prev => { const m = { ...prev }; delete m[editingHeader.id]; return m })
      } else {
        await apiClient.post('/bom-management/headers', payload)
      }
      setShowHeaderModal(false)
      fetchHeaders()
    } catch (e: any) { alert(e.response?.data?.detail ?? 'Error saving BOM header') }
  }

  const handleDeleteHeader = async (h: BOMHeader) => {
    if (!confirm(`Delete BOM "${h.product_code}" rev "${h.revision}" and all its lines?`)) return
    try {
      await apiClient.delete(`/bom-management/headers/${h.id}`)
      setDetailsMap(prev => { const m = { ...prev }; delete m[h.id]; return m })
      fetchHeaders()
    } catch (e: any) { alert(e.response?.data?.detail ?? 'Error') }
  }

  const openHeaderModal = (h?: BOMHeader) => {
    setEditingHeader(h ?? null)
    setHeaderForm(h ? {
      product_id: String(h.product_id),
      revision: h.revision,
      bom_type: h.bom_type ?? 'manufacturing',
      qty_output: String(h.qty_output),
      is_active: h.is_active,
      revision_reason: h.revision_reason ?? '',
    } : { product_id: '', revision: 'Rev 1.0', bom_type: 'manufacturing', qty_output: '1', is_active: true, revision_reason: '' })
    setShowHeaderModal(true)
  }

  // ── Detail CRUD ──────────────────────────────────────────────────────────────

  const handleSaveDetail = async (e: React.FormEvent) => {
    e.preventDefault()
    const payload = { ...detailForm, component_id: Number(detailForm.component_id), qty_needed: parseFloat(detailForm.qty_needed), wastage_percent: parseFloat(detailForm.wastage_percent) }
    try {
      if (editingDetail) {
        await apiClient.put(`/bom-management/details/${editingDetail.id}`, payload)
      } else if (detailModalHeaderId) {
        await apiClient.post(`/bom-management/headers/${detailModalHeaderId}/details`, payload)
      }
      setShowDetailModal(false)
      // Reload details
      if (detailModalHeaderId) {
        const res = await apiClient.get(`/bom-management/headers/${detailModalHeaderId}`)
        setDetailsMap(prev => ({ ...prev, [detailModalHeaderId]: res.data.details ?? [] }))
        // Update detail_count in header list
        setHeaders(prev => prev.map(h => h.id === detailModalHeaderId ? { ...h, detail_count: res.data.details?.length } : h))
      }
    } catch (e: any) { alert(e.response?.data?.detail ?? 'Error saving detail') }
  }

  const handleDeleteDetail = async (headerId: number, d: BOMDetail) => {
    if (!confirm(`Remove "${d.component_name}" from BOM?`)) return
    try {
      await apiClient.delete(`/bom-management/details/${d.id}`)
      const res = await apiClient.get(`/bom-management/headers/${headerId}`)
      setDetailsMap(prev => ({ ...prev, [headerId]: res.data.details ?? [] }))
      setHeaders(prev => prev.map(h => h.id === headerId ? { ...h, detail_count: res.data.details?.length } : h))
    } catch (e: any) { alert(e.response?.data?.detail ?? 'Error') }
  }

  const openDetailModal = (headerId: number, d?: BOMDetail) => {
    setDetailModalHeaderId(headerId)
    setEditingDetail(d ?? null)
    setDetailForm(d ? { component_id: String(d.component_id), qty_needed: String(d.qty_needed), wastage_percent: String(d.wastage_percent) } : { component_id: '', qty_needed: '1', wastage_percent: '0' })
    setShowDetailModal(true)
  }

  // ─────────────────────────────────────────────────────────────────────────────

  return (
    <div className="p-6 space-y-5">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">BOM Management</h1>
          <p className="text-gray-500 text-sm mt-0.5">Bill of Materials — view, add, edit, delete</p>
        </div>
        {isAdmin && (
          <button onClick={() => openHeaderModal()} className="flex items-center gap-1.5 px-4 py-2 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700">
            <Plus size={15} /> New BOM
          </button>
        )}
      </div>

      {/* Filters */}
      <div className="flex gap-3 flex-wrap items-center">
        <input value={search} onChange={e => { setSearch(e.target.value); setPage(1) }} onKeyDown={e => e.key === 'Enter' && fetchHeaders()} placeholder="Search article code / name…" className="border rounded-lg px-3 py-2 text-sm flex-1 min-w-52" />
        <label className="flex items-center gap-2 text-sm text-gray-600">
          <input type="checkbox" checked={activeOnly} onChange={e => setActiveOnly(e.target.checked)} />
          Active only
        </label>
        <button onClick={fetchHeaders} className="flex items-center gap-1 px-3 py-2 text-sm bg-gray-100 hover:bg-gray-200 rounded-lg">
          <RefreshCw size={14} /> Refresh
        </button>
      </div>

      {/* Table */}
      <div className="bg-white rounded-xl border shadow-sm overflow-hidden">
        <table className="min-w-full divide-y divide-gray-100">
          <thead className="bg-gray-50 text-xs font-semibold text-gray-500 uppercase">
            <tr>
              <th className="w-8" />
              <th className="px-4 py-3 text-left">Article</th>
              <th className="px-4 py-3 text-left">Revision</th>
              <th className="px-4 py-3 text-left">Type</th>
              <th className="px-4 py-3 text-left">Qty Output</th>
              <th className="px-4 py-3 text-left">Lines</th>
              <th className="px-4 py-3 text-left">Status</th>
              {isAdmin && <th className="px-4 py-3 text-left">Actions</th>}
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-50 text-sm">
            {loading ? (
              <tr><td colSpan={8} className="py-10 text-center text-gray-400">Loading…</td></tr>
            ) : headers.length === 0 ? (
              <tr><td colSpan={8} className="py-10 text-center text-gray-400">No BOM headers found.</td></tr>
            ) : headers.map(h => (
              <React.Fragment key={h.id}>
                {/* Header row */}
                <tr className="hover:bg-gray-50">
                  <td className="pl-3">
                    <button onClick={() => toggleExpand(h.id)} className="text-gray-400 hover:text-gray-700 p-1">
                      {expanded.has(h.id) ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
                    </button>
                  </td>
                  <td className="px-4 py-3">
                    <div className="font-semibold text-gray-800">{h.product_code}</div>
                    <div className="text-xs text-gray-500 mt-0.5">{h.product_name}</div>
                  </td>
                  <td className="px-4 py-3 text-gray-700 font-mono text-xs">{h.revision}</td>
                  <td className="px-4 py-3 text-gray-600 capitalize">{h.bom_type}</td>
                  <td className="px-4 py-3 text-gray-600">{h.qty_output} pcs</td>
                  <td className="px-4 py-3 text-gray-600">{h.detail_count ?? '—'} components</td>
                  <td className="px-4 py-3">
                    <span className={`px-2 py-0.5 rounded-full text-xs font-semibold ${h.is_active ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-600'}`}>
                      {h.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </td>
                  {isAdmin && (
                    <td className="px-4 py-3">
                      <div className="flex gap-2 items-center">
                        <button onClick={() => openHeaderModal(h)} title="Edit" className="text-blue-500 hover:text-blue-700"><Pencil size={14} /></button>
                        <button onClick={() => handleDeleteHeader(h)} title="Delete" className="text-red-400 hover:text-red-600"><Trash2 size={14} /></button>
                        <button onClick={() => openDetailModal(h.id)} title="Add component" className="text-green-500 hover:text-green-700 ml-1 text-xs font-medium">+ Line</button>
                      </div>
                    </td>
                  )}
                </tr>

                {/* Expanded detail rows */}
                {expanded.has(h.id) && (
                  <tr>
                    <td colSpan={isAdmin ? 8 : 7} className="bg-blue-50/40 px-6 pb-4 pt-2">
                      {detailsLoading.has(h.id) ? (
                        <div className="text-sm text-gray-400 py-2">Loading components…</div>
                      ) : !detailsMap[h.id] || detailsMap[h.id].length === 0 ? (
                        <div className="text-sm text-gray-400 italic py-2">No components yet. {isAdmin && 'Use "+ Line" to add.'}</div>
                      ) : (
                        <table className="w-full text-xs">
                          <thead>
                            <tr className="text-gray-500 border-b border-blue-100">
                              <th className="text-left py-1.5 pr-4">Component Code</th>
                              <th className="text-left py-1.5 pr-4">Name</th>
                              <th className="text-left py-1.5 pr-4">Type</th>
                              <th className="text-left py-1.5 pr-4">Qty Needed</th>
                              <th className="text-left py-1.5 pr-4">UOM</th>
                              <th className="text-left py-1.5 pr-4">Wastage %</th>
                              {isAdmin && <th className="text-left py-1.5">Actions</th>}
                            </tr>
                          </thead>
                          <tbody>
                            {detailsMap[h.id].map(d => (
                              <tr key={d.id} className="border-b border-blue-50 last:border-0">
                                <td className="py-1.5 pr-4 font-mono font-semibold text-gray-700">{d.component_code}</td>
                                <td className="py-1.5 pr-4 text-gray-600">{d.component_name}</td>
                                <td className="py-1.5 pr-4 text-gray-500">{d.component_type}</td>
                                <td className="py-1.5 pr-4 font-semibold text-gray-800">{d.qty_needed}</td>
                                <td className="py-1.5 pr-4 text-gray-500">{d.component_uom}</td>
                                <td className="py-1.5 pr-4 text-gray-500">{d.wastage_percent > 0 ? `${d.wastage_percent}%` : '—'}</td>
                                {isAdmin && (
                                  <td className="py-1.5 flex gap-2">
                                    <button onClick={() => openDetailModal(h.id, d)} className="text-blue-500 hover:text-blue-700"><Pencil size={12} /></button>
                                    <button onClick={() => handleDeleteDetail(h.id, d)} className="text-red-400 hover:text-red-600"><Trash2 size={12} /></button>
                                  </td>
                                )}
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      )}
                    </td>
                  </tr>
                )}
              </React.Fragment>
            ))}
          </tbody>
        </table>

        {total > 50 && (
          <div className="px-4 py-3 border-t flex items-center justify-between text-sm text-gray-500">
            <span>Showing {headers.length} of {total}</span>
            <div className="flex gap-2">
              <button disabled={page === 1} onClick={() => setPage(p => p - 1)} className="px-3 py-1 border rounded disabled:opacity-40">Prev</button>
              <button disabled={page * 50 >= total} onClick={() => setPage(p => p + 1)} className="px-3 py-1 border rounded disabled:opacity-40">Next</button>
            </div>
          </div>
        )}
      </div>

      {/* ─── BOM Header Modal ────────────────────────────────────────────────── */}
      {showHeaderModal && (
        <Modal title={editingHeader ? 'Edit BOM Header' : 'New BOM Header'} onClose={() => setShowHeaderModal(false)}>
          <form onSubmit={handleSaveHeader} className="space-y-4">
            <label className="block">
              <span className="text-sm font-medium text-gray-700">Article / Product *</span>
              <select required className="mt-1 w-full border rounded-lg px-3 py-2 text-sm"
                value={headerForm.product_id} onChange={e => setHeaderForm(f => ({ ...f, product_id: e.target.value }))}>
                <option value="">-- select product --</option>
                {productOptions.map(p => <option key={p.id} value={p.id}>{p.code} — {p.name}</option>)}
              </select>
            </label>

            <div className="grid grid-cols-2 gap-4">
              <label className="block">
                <span className="text-sm font-medium text-gray-700">Revision *</span>
                <input className="mt-1 w-full border rounded-lg px-3 py-2 text-sm" required value={headerForm.revision}
                  onChange={e => setHeaderForm(f => ({ ...f, revision: e.target.value }))} />
              </label>
              <label className="block">
                <span className="text-sm font-medium text-gray-700">BOM Type</span>
                <select className="mt-1 w-full border rounded-lg px-3 py-2 text-sm"
                  value={headerForm.bom_type} onChange={e => setHeaderForm(f => ({ ...f, bom_type: e.target.value }))}>
                  {BOM_TYPES.map(t => <option key={t} value={t}>{t.charAt(0).toUpperCase() + t.slice(1)}</option>)}
                </select>
              </label>
            </div>

            <label className="block">
              <span className="text-sm font-medium text-gray-700">Qty Output</span>
              <input type="number" step="0.01" className="mt-1 w-full border rounded-lg px-3 py-2 text-sm"
                value={headerForm.qty_output} onChange={e => setHeaderForm(f => ({ ...f, qty_output: e.target.value }))} />
            </label>

            <label className="block">
              <span className="text-sm font-medium text-gray-700">Revision Reason</span>
              <input className="mt-1 w-full border rounded-lg px-3 py-2 text-sm" placeholder="Optional…"
                value={headerForm.revision_reason} onChange={e => setHeaderForm(f => ({ ...f, revision_reason: e.target.value }))} />
            </label>

            <label className="flex items-center gap-2 text-sm">
              <input type="checkbox" checked={headerForm.is_active} onChange={e => setHeaderForm(f => ({ ...f, is_active: e.target.checked }))} />
              <span className="font-medium text-gray-700">Active</span>
            </label>

            <div className="flex justify-end gap-2 pt-2">
              <button type="button" onClick={() => setShowHeaderModal(false)} className="px-4 py-2 border rounded-lg text-sm">Cancel</button>
              <button type="submit" className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700">Save</button>
            </div>
          </form>
        </Modal>
      )}

      {/* ─── BOM Detail Modal ─────────────────────────────────────────────────── */}
      {showDetailModal && (
        <Modal title={editingDetail ? 'Edit Component' : 'Add Component'} onClose={() => setShowDetailModal(false)}>
          <form onSubmit={handleSaveDetail} className="space-y-4">
            {!editingDetail && (
              <label className="block">
                <span className="text-sm font-medium text-gray-700">Component / Material *</span>
                <select required className="mt-1 w-full border rounded-lg px-3 py-2 text-sm"
                  value={detailForm.component_id} onChange={e => setDetailForm(f => ({ ...f, component_id: e.target.value }))}>
                  <option value="">-- select material --</option>
                  {productOptions.map(p => <option key={p.id} value={p.id}>{p.code} — {p.name} ({p.uom})</option>)}
                </select>
              </label>
            )}
            {editingDetail && (
              <div className="bg-gray-50 rounded-lg px-4 py-3 text-sm text-gray-700">
                <span className="font-semibold">{editingDetail.component_code}</span> — {editingDetail.component_name}
              </div>
            )}

            <div className="grid grid-cols-2 gap-4">
              <label className="block">
                <span className="text-sm font-medium text-gray-700">Qty Needed *</span>
                <input type="number" step="0.0001" required className="mt-1 w-full border rounded-lg px-3 py-2 text-sm"
                  value={detailForm.qty_needed} onChange={e => setDetailForm(f => ({ ...f, qty_needed: e.target.value }))} />
              </label>
              <label className="block">
                <span className="text-sm font-medium text-gray-700">Wastage %</span>
                <input type="number" step="0.01" min="0" max="100" className="mt-1 w-full border rounded-lg px-3 py-2 text-sm"
                  value={detailForm.wastage_percent} onChange={e => setDetailForm(f => ({ ...f, wastage_percent: e.target.value }))} />
              </label>
            </div>

            <div className="flex justify-end gap-2 pt-2">
              <button type="button" onClick={() => setShowDetailModal(false)} className="px-4 py-2 border rounded-lg text-sm">Cancel</button>
              <button type="submit" className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700">Save</button>
            </div>
          </form>
        </Modal>
      )}
    </div>
  )
}

export default BOMManagementPage
