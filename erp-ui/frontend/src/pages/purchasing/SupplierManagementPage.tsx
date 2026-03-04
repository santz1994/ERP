/**
 * Supplier Management Page — /purchasing/suppliers
 * View, create, edit, and search suppliers.
 * Uses /masterdata/suppliers CRUD endpoints.
 */

import { useState, useCallback } from 'react'
import { useQuery } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import {
  ArrowLeft, Search, Plus, RefreshCw,
  Users, Phone, Mail, MapPin, User, Edit, Trash2,
  Building2,
} from 'lucide-react'
import { apiClient } from '@/api/client'
import { Card } from '@/components/ui/card'
import { useAuthStore } from '@/store'

// ── Types ────────────────────────────────────────────────────────────────────

interface Supplier {
  id: number
  name: string
  code?: string
  contact_person?: string
  phone?: string
  email?: string
  address?: string
}

interface SupplierForm {
  name: string
  code: string
  contact_person: string
  phone: string
  email: string
  address: string
}

const EMPTY_FORM: SupplierForm = { name: '', code: '', contact_person: '', phone: '', email: '', address: '' }

const ADMIN_ROLES = ['Admin', 'Superadmin', 'Developer', 'Purchasing Head', 'Manager']

// ── Modal ────────────────────────────────────────────────────────────────────

function SupplierModal({
  supplier,
  onClose,
  onSaved,
}: {
  supplier: Supplier | null
  onClose: () => void
  onSaved: () => void
}) {
  const [form, setForm] = useState<SupplierForm>(
    supplier
      ? { name: supplier.name, code: supplier.code ?? '', contact_person: supplier.contact_person ?? '', phone: supplier.phone ?? '', email: supplier.email ?? '', address: supplier.address ?? '' }
      : EMPTY_FORM
  )
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')

  const set = (k: keyof SupplierForm) => (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) =>
    setForm(f => ({ ...f, [k]: e.target.value }))

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!form.name.trim()) { setError('Supplier name is required'); return }
    setSaving(true); setError('')
    try {
      if (supplier) {
        await apiClient.put(`/masterdata/suppliers/${supplier.id}`, form)
      } else {
        await apiClient.post('/masterdata/suppliers', form)
      }
      onSaved()
      onClose()
    } catch (err: any) {
      setError(err?.response?.data?.detail ?? 'Error saving supplier')
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl shadow-2xl w-full max-w-lg max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between p-5 border-b">
          <h2 className="text-xl font-bold text-gray-800">{supplier ? 'Edit Supplier' : 'New Supplier'}</h2>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600 text-2xl leading-none">&times;</button>
        </div>
        <form onSubmit={handleSubmit} className="p-5 space-y-4">
          {error && <div className="text-sm text-red-600 bg-red-50 rounded-lg p-3">{error}</div>}
          <div className="grid grid-cols-2 gap-4">
            <div className="col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-1">Supplier Name *</label>
              <input value={form.name} onChange={set('name')} placeholder="PT. Example Supplier" className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Supplier Code</label>
              <input value={form.code} onChange={set('code')} placeholder="SUP-001" className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Contact Person</label>
              <input value={form.contact_person} onChange={set('contact_person')} placeholder="Budi Santoso" className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Phone</label>
              <input value={form.phone} onChange={set('phone')} placeholder="0812-3456-7890" className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
              <input type="email" value={form.email} onChange={set('email')} placeholder="supplier@example.com" className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
            </div>
            <div className="col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-1">Address</label>
              <textarea value={form.address} onChange={set('address')} rows={2} placeholder="Jl. Industri No. 1, Bandung" className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none" />
            </div>
          </div>
          <div className="flex justify-end gap-3 pt-2">
            <button type="button" onClick={onClose} className="px-4 py-2 text-sm text-gray-600 border rounded-lg hover:bg-gray-50">Cancel</button>
            <button type="submit" disabled={saving} className="px-4 py-2 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50">
              {saving ? 'Saving…' : supplier ? 'Save Changes' : 'Add Supplier'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

// ── Main Page ─────────────────────────────────────────────────────────────────

export default function SupplierManagementPage() {
  const navigate = useNavigate()
  const { user } = useAuthStore()
  const isAdmin = ADMIN_ROLES.includes(user?.role ?? '')

  const [search, setSearch] = useState('')
  const [showModal, setShowModal] = useState(false)
  const [editing, setEditing] = useState<Supplier | null>(null)

  const fetchSuppliers = useCallback(
    () => apiClient.get(`/masterdata/suppliers${search ? `?search=${encodeURIComponent(search)}` : ''}`),
    [search]
  )

  const { data: suppliers = [], isLoading, refetch } = useQuery<Supplier[]>({
    queryKey: ['suppliers-mgmt', search],
    queryFn: fetchSuppliers,
  })

  const handleDelete = async (s: Supplier) => {
    if (!confirm(`Delete supplier "${s.name}"? This cannot be undone.`)) return
    try {
      await apiClient.delete(`/masterdata/suppliers/${s.id}`)
      refetch()
    } catch (err: any) {
      alert(err?.response?.data?.detail ?? 'Cannot delete this supplier')
    }
  }

  const openCreate = () => { setEditing(null); setShowModal(true) }
  const openEdit   = (s: Supplier) => { setEditing(s); setShowModal(true) }

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
              <Users className="w-7 h-7 text-green-600" />
              Supplier Management
            </h1>
            <p className="text-sm text-gray-500 mt-0.5">
              {isLoading ? 'Loading…' : `${suppliers.length} supplier${suppliers.length !== 1 ? 's' : ''}`}
            </p>
          </div>
        </div>
        <div className="flex gap-2">
          <button onClick={() => refetch()} className="flex items-center gap-1.5 px-3 py-2 text-sm bg-white border rounded-lg hover:bg-gray-50">
            <RefreshCw className="w-4 h-4" /> Refresh
          </button>
          {isAdmin && (
            <button onClick={openCreate} className="flex items-center gap-1.5 px-4 py-2 text-sm bg-green-600 text-white rounded-lg hover:bg-green-700">
              <Plus className="w-4 h-4" /> New Supplier
            </button>
          )}
        </div>
      </div>

      {/* Search */}
      <Card className="bg-white shadow-sm mb-5">
        <div className="p-4 flex gap-3">
          <div className="relative flex-1">
            <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
            <input
              value={search}
              onChange={e => setSearch(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && refetch()}
              placeholder="Search by name or code…"
              className="w-full pl-9 pr-3 py-2 text-sm border rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
            />
          </div>
          <button onClick={() => refetch()} className="px-4 py-2 text-sm bg-gray-100 hover:bg-gray-200 rounded-lg">Search</button>
        </div>
      </Card>

      {/* Grid */}
      {isLoading ? (
        <div className="flex justify-center py-20">
          <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-green-600" />
        </div>
      ) : suppliers.length === 0 ? (
        <Card className="bg-white shadow-sm">
          <div className="py-20 text-center">
            <Building2 className="w-12 h-12 text-gray-300 mx-auto mb-3" />
            <p className="text-gray-500">{search ? 'No suppliers match your search' : 'No suppliers yet'}</p>
            {isAdmin && !search && (
              <button onClick={openCreate} className="mt-4 text-green-600 hover:text-green-700 text-sm font-medium">
                Add first supplier →
              </button>
            )}
          </div>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          {suppliers.map(s => (
            <Card key={s.id} className="bg-white shadow-sm hover:shadow-md transition-shadow">
              <div className="p-5">
                {/* Header row */}
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-xl bg-green-100 flex items-center justify-center flex-shrink-0">
                      <Building2 className="w-5 h-5 text-green-600" />
                    </div>
                    <div>
                      <h3 className="font-semibold text-gray-900 text-sm leading-tight">{s.name}</h3>
                      {s.code && <span className="text-xs text-gray-400 font-mono">{s.code}</span>}
                    </div>
                  </div>
                  {isAdmin && (
                    <div className="flex gap-1 flex-shrink-0">
                      <button onClick={() => openEdit(s)} className="p-1.5 text-blue-500 hover:text-blue-700 hover:bg-blue-50 rounded-lg transition-colors">
                        <Edit className="w-3.5 h-3.5" />
                      </button>
                      <button onClick={() => handleDelete(s)} className="p-1.5 text-red-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors">
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  )}
                </div>

                {/* Contact info */}
                <div className="space-y-1.5">
                  {s.contact_person && (
                    <div className="flex items-center gap-2 text-sm text-gray-600">
                      <User className="w-3.5 h-3.5 text-gray-400 flex-shrink-0" />
                      <span className="truncate">{s.contact_person}</span>
                    </div>
                  )}
                  {s.phone && (
                    <div className="flex items-center gap-2 text-sm text-gray-600">
                      <Phone className="w-3.5 h-3.5 text-gray-400 flex-shrink-0" />
                      <a href={`tel:${s.phone}`} onClick={e => e.stopPropagation()} className="hover:text-green-600">{s.phone}</a>
                    </div>
                  )}
                  {s.email && (
                    <div className="flex items-center gap-2 text-sm text-gray-600">
                      <Mail className="w-3.5 h-3.5 text-gray-400 flex-shrink-0" />
                      <a href={`mailto:${s.email}`} onClick={e => e.stopPropagation()} className="truncate hover:text-green-600">{s.email}</a>
                    </div>
                  )}
                  {s.address && (
                    <div className="flex items-start gap-2 text-sm text-gray-500">
                      <MapPin className="w-3.5 h-3.5 text-gray-400 flex-shrink-0 mt-0.5" />
                      <span className="line-clamp-2">{s.address}</span>
                    </div>
                  )}
                  {!s.contact_person && !s.phone && !s.email && !s.address && (
                    <p className="text-xs text-gray-400 italic">No contact info</p>
                  )}
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}

      {/* Modal */}
      {showModal && (
        <SupplierModal
          supplier={editing}
          onClose={() => setShowModal(false)}
          onSaved={() => refetch()}
        />
      )}
    </div>
  )
}
