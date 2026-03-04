import React, { useState, useEffect, useCallback } from 'react'
import { apiClient } from '@/api'
import { useAuthStore } from '@/store'

// â”€â”€â”€ Types â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

interface Category {
  id: number; name: string; description?: string
}
interface Product {
  id: number; code: string; name: string; type: string; uom: string
  category_id?: number; category_name?: string; min_stock?: number
  is_active: boolean; created_at: string
}
interface Supplier {
  id: number; name: string; code?: string; contact_person?: string
  phone?: string; email?: string; address?: string
}

const ADMIN_ROLES = ['Admin', 'Superadmin', 'Developer']
const PRODUCT_TYPES = ['Raw Material', 'WIP', 'Finish Good', 'Label', 'Accessories', 'Service']
const UOM_OPTIONS = [
  'Pcs', 'Meter', 'Yard', 'Kg', 'Gram', 'Cm',
  'Roll', 'Box', 'Ctn', 'Set', 'Pack',
  'Sheet', 'Lusin', 'Cone', 'Ball', 'Liter',
]

// â”€â”€â”€ Helpers â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

const useAdmin = () => {
  const { user } = useAuthStore()
  return ADMIN_ROLES.includes(user?.role ?? '')
}

const TypeBadge: React.FC<{ type: string }> = ({ type }) => {
  const colours: Record<string, string> = {
    'Raw Material': 'bg-blue-100 text-blue-800',
    'WIP': 'bg-yellow-100 text-yellow-800',
    'Finish Good': 'bg-green-100 text-green-800',
    'Label': 'bg-purple-100 text-purple-800',
    'Accessories': 'bg-orange-100 text-orange-800',
    'Service': 'bg-gray-100 text-gray-700',
  }
  return <span className={`px-2 py-0.5 text-xs font-semibold rounded-full ${colours[type] ?? 'bg-gray-100 text-gray-700'}`}>{type}</span>
}

// â”€â”€â”€ Modal wrapper â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

const Modal: React.FC<{ title: string; onClose: () => void; children: React.ReactNode }> = ({ title, onClose, children }) => (
  <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
    <div className="bg-white rounded-xl shadow-2xl w-full max-w-lg max-h-[90vh] overflow-y-auto">
      <div className="flex items-center justify-between p-5 border-b">
        <h2 className="text-xl font-bold text-gray-800">{title}</h2>
        <button onClick={onClose} className="text-gray-400 hover:text-gray-600 text-2xl leading-none">&times;</button>
      </div>
      <div className="p-5">{children}</div>
    </div>
  </div>
)

// â”€â”€â”€ Main Page â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

type Tab = 'products' | 'categories' | 'suppliers'

const AdminMasterdataPage: React.FC = () => {
  const isAdmin = useAdmin()
  const [activeTab, setActiveTab] = useState<Tab>('products')

  // â”€â”€ Products â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
  const [products, setProducts] = useState<Product[]>([])
  const [productTotal, setProductTotal] = useState(0)
  const [productPage, setProductPage] = useState(1)
  const [productSearch, setProductSearch] = useState('')
  const [productTypeFilter, setProductTypeFilter] = useState('')
  const [products_loading, setProdLoad] = useState(false)

  const [showProductModal, setShowProductModal] = useState(false)
  const [editingProduct, setEditingProduct] = useState<Product | null>(null)
  const [productForm, setProductForm] = useState({ code: '', name: '', type: 'Raw Material', uom: 'Pcs', category_id: '', min_stock: '0', is_active: true })

  // â”€â”€ Categories â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
  const [categories, setCategories] = useState<Category[]>([])
  const [cats_loading, setCatLoad] = useState(false)
  const [showCatModal, setShowCatModal] = useState(false)
  const [editingCat, setEditingCat] = useState<Category | null>(null)
  const [catForm, setCatForm] = useState({ name: '', description: '' })

  // â”€â”€ Suppliers â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
  const [suppliers, setSuppliers] = useState<Supplier[]>([])
  const [supplierSearch, setSupplierSearch] = useState('')
  const [sup_loading, setSupLoad] = useState(false)
  const [showSupModal, setShowSupModal] = useState(false)
  const [editingSup, setEditingSup] = useState<Supplier | null>(null)
  const [supForm, setSupForm] = useState({ name: '', code: '', contact_person: '', phone: '', email: '', address: '' })

  // â”€â”€ Load Data â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

  const fetchProducts = useCallback(async () => {
    setProdLoad(true)
    try {
      const params = new URLSearchParams({ page: String(productPage), page_size: '50' })
      if (productSearch) params.set('search', productSearch)
      if (productTypeFilter) params.set('product_type', productTypeFilter)
      const res = await apiClient.get(`/masterdata/products?${params}`)
      setProducts(res.items)
      setProductTotal(res.total)
    } catch (e) { console.error(e) } finally { setProdLoad(false) }
  }, [productPage, productSearch, productTypeFilter])

  const fetchCategories = useCallback(async () => {
    setCatLoad(true)
    try {
      const res = await apiClient.get('/masterdata/categories')
      setCategories(res)
    } catch (e) { console.error(e) } finally { setCatLoad(false) }
  }, [])

  const fetchSuppliers = useCallback(async () => {
    setSupLoad(true)
    try {
      const params = supplierSearch ? `?search=${supplierSearch}` : ''
      const res = await apiClient.get(`/masterdata/suppliers${params}`)
      setSuppliers(res)
    } catch (e) { console.error(e) } finally { setSupLoad(false) }
  }, [supplierSearch])

  useEffect(() => { if (activeTab === 'products') fetchProducts() }, [activeTab, fetchProducts])
  useEffect(() => { if (activeTab === 'categories') fetchCategories() }, [activeTab, fetchCategories])
  useEffect(() => { if (activeTab === 'suppliers') fetchSuppliers() }, [activeTab, fetchSuppliers])

  // â”€â”€ Product CRUD â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

  const handleSaveProduct = async (e: React.FormEvent) => {
    e.preventDefault()
    const payload = { ...productForm, category_id: productForm.category_id ? Number(productForm.category_id) : null, min_stock: parseFloat(productForm.min_stock) }
    try {
      if (editingProduct) {
        await apiClient.put(`/masterdata/products/${editingProduct.id}`, payload)
      } else {
        await apiClient.post('/masterdata/products', payload)
      }
      setShowProductModal(false); fetchProducts()
    } catch (e: any) { alert(e.response?.data?.detail ?? 'Error saving product') }
  }

  const handleDeleteProduct = async (p: Product) => {
    if (!confirm(`Deactivate product "${p.name}"?`)) return
    try { await apiClient.delete(`/masterdata/products/${p.id}`); fetchProducts() }
    catch (e: any) { alert(e.response?.data?.detail ?? 'Error') }
  }

  const openProductModal = (p?: Product) => {
    setEditingProduct(p ?? null)
    setProductForm(p ? { code: p.code, name: p.name, type: p.type, uom: p.uom, category_id: p.category_id?.toString() ?? '', min_stock: String(p.min_stock ?? 0), is_active: p.is_active } : { code: '', name: '', type: 'Raw Material', uom: 'Pcs', category_id: '', min_stock: '0', is_active: true })
    setShowProductModal(true)
  }

  // â”€â”€ Category CRUD â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

  const handleSeedCategories = async () => {
    if (!confirm('Seed default material categories (Fabric, Benang, Label, Accessories, etc.)? Existing names will be skipped.')) return
    try {
      const res = await apiClient.post('/masterdata/categories/seed-defaults', {})
      alert(res.message ?? 'Seeded successfully')
      fetchCategories()
    } catch (e: any) { alert(e.response?.data?.detail ?? 'Seed failed') }
  }

  const handleSaveCat = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      if (editingCat) { await apiClient.put(`/masterdata/categories/${editingCat.id}`, catForm) }
      else { await apiClient.post('/masterdata/categories', catForm) }
      setShowCatModal(false); fetchCategories()
    } catch (e: any) { alert(e.response?.data?.detail ?? 'Error') }
  }

  const handleDeleteCat = async (c: Category) => {
    if (!confirm(`Delete category "${c.name}"?`)) return
    try { await apiClient.delete(`/masterdata/categories/${c.id}`); fetchCategories() }
    catch (e: any) { alert(e.response?.data?.detail ?? 'Error') }
  }

  // â”€â”€ Supplier CRUD â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

  const handleSaveSup = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      if (editingSup) { await apiClient.put(`/masterdata/suppliers/${editingSup.id}`, supForm) }
      else { await apiClient.post('/masterdata/suppliers', supForm) }
      setShowSupModal(false); fetchSuppliers()
    } catch (e: any) { alert(e.response?.data?.detail ?? 'Error') }
  }

  const handleDeleteSup = async (s: Supplier) => {
    if (!confirm(`Delete supplier "${s.name}"?`)) return
    try { await apiClient.delete(`/masterdata/suppliers/${s.id}`); fetchSuppliers() }
    catch (e: any) { alert(e.response?.data?.detail ?? 'Error') }
  }

  const openSupModal = (s?: Supplier) => {
    setEditingSup(s ?? null)
    setSupForm(s ? { name: s.name, code: s.code ?? '', contact_person: s.contact_person ?? '', phone: s.phone ?? '', email: s.email ?? '', address: s.address ?? '' } : { name: '', code: '', contact_person: '', phone: '', email: '', address: '' })
    setShowSupModal(true)
  }

  // â”€â”€ Render â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

  const tabs: { key: Tab; label: string; color: string }[] = [
    { key: 'products', label: 'Products', color: 'blue' },
    { key: 'categories', label: 'Categories', color: 'purple' },
    { key: 'suppliers', label: 'Suppliers', color: 'green' },
  ]

  return (
    <div className="p-6 space-y-5">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Masterdata Management</h1>
          <p className="text-gray-500 text-sm mt-0.5">Products Â· Categories Â· Suppliers</p>
        </div>
        {isAdmin && activeTab === 'products' && <button onClick={() => openProductModal()} className="px-4 py-2 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700">+ New Product</button>}
        {isAdmin && activeTab === 'categories' && (
          <div className="flex gap-2">
            <button onClick={handleSeedCategories} className="px-4 py-2 bg-emerald-600 text-white text-sm rounded-lg hover:bg-emerald-700">Seed Default Categories</button>
            <button onClick={() => { setEditingCat(null); setCatForm({ name: '', description: '' }); setShowCatModal(true) }} className="px-4 py-2 bg-purple-600 text-white text-sm rounded-lg hover:bg-purple-700">+ New Category</button>
          </div>
        )}
        {isAdmin && activeTab === 'suppliers' && <button onClick={() => openSupModal()} className="px-4 py-2 bg-green-600 text-white text-sm rounded-lg hover:bg-green-700">+ New Supplier</button>}
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-6">
          {tabs.map(t => (
            <button key={t.key} onClick={() => setActiveTab(t.key)}
              className={`py-3 px-1 border-b-2 font-medium text-sm transition ${activeTab === t.key ? `border-${t.color}-500 text-${t.color}-600` : 'border-transparent text-gray-500 hover:text-gray-700'}`}>
              {t.label}
            </button>
          ))}
        </nav>
      </div>

      {/* â”€â”€ PRODUCTS TAB â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€ */}
      {activeTab === 'products' && (
        <div className="space-y-3">
          <div className="flex gap-3 flex-wrap">
            <input value={productSearch} onChange={e => { setProductSearch(e.target.value); setProductPage(1) }} placeholder="Search code / nameâ€¦" className="border rounded-lg px-3 py-2 text-sm flex-1 min-w-48" />
            <select value={productTypeFilter} onChange={e => { setProductTypeFilter(e.target.value); setProductPage(1) }} className="border rounded-lg px-3 py-2 text-sm">
              <option value="">All Types</option>
              {PRODUCT_TYPES.map(t => <option key={t} value={t}>{t}</option>)}
            </select>
            <button onClick={fetchProducts} className="px-3 py-2 text-sm bg-gray-100 hover:bg-gray-200 rounded-lg">Refresh</button>
          </div>
          <div className="bg-white rounded-xl border overflow-hidden shadow-sm">
            <table className="min-w-full divide-y divide-gray-100">
              <thead className="bg-gray-50 text-xs font-semibold text-gray-500 uppercase">
                <tr>
                  {['Code', 'Name', 'Type', 'UOM', 'Category', 'Status', 'Actions'].map(h => (
                    <th key={h} className="px-4 py-3 text-left">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-50 text-sm">
                {products_loading ? (
                  <tr><td colSpan={7} className="py-10 text-center text-gray-400">Loadingâ€¦</td></tr>
                ) : products.length === 0 ? (
                  <tr><td colSpan={7} className="py-10 text-center text-gray-400">No products found.</td></tr>
                ) : products.map(p => (
                  <tr key={p.id} className="hover:bg-gray-50">
                    <td className="px-4 py-3 font-mono font-semibold text-gray-800">{p.code}</td>
                    <td className="px-4 py-3 text-gray-700">{p.name}</td>
                    <td className="px-4 py-3"><TypeBadge type={p.type} /></td>
                    <td className="px-4 py-3 text-gray-600">{p.uom}</td>
                    <td className="px-4 py-3 text-gray-500">{p.category_name ?? '-'}</td>
                    <td className="px-4 py-3">
                      <span className={`px-2 py-0.5 rounded-full text-xs font-semibold ${p.is_active ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-600'}`}>{p.is_active ? 'Active' : 'Inactive'}</span>
                    </td>
                    <td className="px-4 py-3">
                      {isAdmin && (
                        <div className="flex gap-3">
                          <button onClick={() => openProductModal(p)} className="text-blue-600 hover:text-blue-800 text-xs font-medium">Edit</button>
                          <button onClick={() => handleDeleteProduct(p)} className="text-red-500 hover:text-red-700 text-xs font-medium">Deactivate</button>
                        </div>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            {productTotal > 50 && (
              <div className="px-4 py-3 border-t flex items-center justify-between text-sm text-gray-500">
                <span>Showing {products.length} of {productTotal}</span>
                <div className="flex gap-2">
                  <button disabled={productPage === 1} onClick={() => setProductPage(p => p - 1)} className="px-3 py-1 border rounded disabled:opacity-40">Prev</button>
                  <button disabled={productPage * 50 >= productTotal} onClick={() => setProductPage(p => p + 1)} className="px-3 py-1 border rounded disabled:opacity-40">Next</button>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* â”€â”€ CATEGORIES TAB â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€ */}
      {activeTab === 'categories' && (
        <div className="bg-white rounded-xl border shadow-sm overflow-hidden">
          <table className="min-w-full divide-y divide-gray-100">
            <thead className="bg-gray-50 text-xs font-semibold text-gray-500 uppercase">
              <tr>
                {['ID', 'Name', 'Description', 'Actions'].map(h => <th key={h} className="px-4 py-3 text-left">{h}</th>)}
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-50 text-sm">
              {cats_loading ? (
                <tr><td colSpan={4} className="py-10 text-center text-gray-400">Loadingâ€¦</td></tr>
              ) : categories.length === 0 ? (
                <tr><td colSpan={4} className="py-10 text-center text-gray-400">No categories yet.</td></tr>
              ) : categories.map(c => (
                <tr key={c.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3 text-gray-400 text-xs">{c.id}</td>
                  <td className="px-4 py-3 font-medium text-gray-800">{c.name}</td>
                  <td className="px-4 py-3 text-gray-500">{c.description ?? '-'}</td>
                  <td className="px-4 py-3">
                    {isAdmin && (
                      <div className="flex gap-3">
                        <button onClick={() => { setEditingCat(c); setCatForm({ name: c.name, description: c.description ?? '' }); setShowCatModal(true) }} className="text-blue-600 hover:text-blue-800 text-xs font-medium">Edit</button>
                        <button onClick={() => handleDeleteCat(c)} className="text-red-500 hover:text-red-700 text-xs font-medium">Delete</button>
                      </div>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* â”€â”€ SUPPLIERS TAB â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€ */}
      {activeTab === 'suppliers' && (
        <div className="space-y-3">
          <div className="flex gap-3">
            <input value={supplierSearch} onChange={e => setSupplierSearch(e.target.value)} onKeyDown={e => e.key === 'Enter' && fetchSuppliers()} placeholder="Search supplier nameâ€¦" className="border rounded-lg px-3 py-2 text-sm flex-1" />
            <button onClick={fetchSuppliers} className="px-3 py-2 text-sm bg-gray-100 hover:bg-gray-200 rounded-lg">Search</button>
          </div>
          <div className="bg-white rounded-xl border shadow-sm overflow-hidden">
            <table className="min-w-full divide-y divide-gray-100">
              <thead className="bg-gray-50 text-xs font-semibold text-gray-500 uppercase">
                <tr>
                  {['Code', 'Name', 'Contact', 'Phone', 'Email', 'Actions'].map(h => <th key={h} className="px-4 py-3 text-left">{h}</th>)}
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-50 text-sm">
                {sup_loading ? (
                  <tr><td colSpan={6} className="py-10 text-center text-gray-400">Loadingâ€¦</td></tr>
                ) : suppliers.length === 0 ? (
                  <tr><td colSpan={6} className="py-10 text-center text-gray-400">No suppliers found.</td></tr>
                ) : suppliers.map(s => (
                  <tr key={s.id} className="hover:bg-gray-50">
                    <td className="px-4 py-3 font-mono text-xs text-gray-500">{s.code ?? '-'}</td>
                    <td className="px-4 py-3 font-medium text-gray-800">{s.name}</td>
                    <td className="px-4 py-3 text-gray-600">{s.contact_person ?? '-'}</td>
                    <td className="px-4 py-3 text-gray-600">{s.phone ?? '-'}</td>
                    <td className="px-4 py-3 text-gray-600">{s.email ?? '-'}</td>
                    <td className="px-4 py-3">
                      {isAdmin && (
                        <div className="flex gap-3">
                          <button onClick={() => openSupModal(s)} className="text-blue-600 hover:text-blue-800 text-xs font-medium">Edit</button>
                          <button onClick={() => handleDeleteSup(s)} className="text-red-500 hover:text-red-700 text-xs font-medium">Delete</button>
                        </div>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* â”€â”€ PRODUCT MODAL â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€ */}
      {showProductModal && (
        <Modal title={editingProduct ? 'Edit Product' : 'New Product'} onClose={() => setShowProductModal(false)}>
          <form onSubmit={handleSaveProduct} className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <label className="block">
                <span className="text-sm font-medium text-gray-700">Code *</span>
                <input className="mt-1 w-full border rounded-lg px-3 py-2 text-sm" required value={productForm.code} onChange={e => setProductForm(f => ({ ...f, code: e.target.value }))} />
              </label>
              <label className="block">
                <span className="text-sm font-medium text-gray-700">UOM *</span>
                <select className="mt-1 w-full border rounded-lg px-3 py-2 text-sm" value={productForm.uom} onChange={e => setProductForm(f => ({ ...f, uom: e.target.value }))}>
                  {UOM_OPTIONS.map(u => <option key={u} value={u}>{u}</option>)}
                </select>
              </label>
            </div>
            <label className="block">
              <span className="text-sm font-medium text-gray-700">Name *</span>
              <input className="mt-1 w-full border rounded-lg px-3 py-2 text-sm" required value={productForm.name} onChange={e => setProductForm(f => ({ ...f, name: e.target.value }))} />
            </label>
            <div className="grid grid-cols-2 gap-4">
              <label className="block">
                <span className="text-sm font-medium text-gray-700">Type *</span>
                <select className="mt-1 w-full border rounded-lg px-3 py-2 text-sm" value={productForm.type} onChange={e => setProductForm(f => ({ ...f, type: e.target.value }))}>
                  {PRODUCT_TYPES.map(t => <option key={t} value={t}>{t}</option>)}
                </select>
              </label>
              <label className="block">
                <span className="text-sm font-medium text-gray-700">Category</span>
                <select className="mt-1 w-full border rounded-lg px-3 py-2 text-sm" value={productForm.category_id} onChange={e => setProductForm(f => ({ ...f, category_id: e.target.value }))}>
                  <option value="">-- None --</option>
                  {categories.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
                </select>
              </label>
            </div>
            <label className="block">
              <span className="text-sm font-medium text-gray-700">Min Stock</span>
              <input type="number" step="0.01" className="mt-1 w-full border rounded-lg px-3 py-2 text-sm" value={productForm.min_stock} onChange={e => setProductForm(f => ({ ...f, min_stock: e.target.value }))} />
            </label>
            <label className="flex items-center gap-2 text-sm">
              <input type="checkbox" checked={productForm.is_active} onChange={e => setProductForm(f => ({ ...f, is_active: e.target.checked }))} />
              <span className="font-medium text-gray-700">Active</span>
            </label>
            <div className="flex justify-end gap-2 pt-2">
              <button type="button" onClick={() => setShowProductModal(false)} className="px-4 py-2 border rounded-lg text-sm">Cancel</button>
              <button type="submit" className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700">Save</button>
            </div>
          </form>
        </Modal>
      )}

      {/* â”€â”€ CATEGORY MODAL â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€ */}
      {showCatModal && (
        <Modal title={editingCat ? 'Edit Category' : 'New Category'} onClose={() => setShowCatModal(false)}>
          <form onSubmit={handleSaveCat} className="space-y-4">
            <label className="block">
              <span className="text-sm font-medium text-gray-700">Name *</span>
              <input required className="mt-1 w-full border rounded-lg px-3 py-2 text-sm" value={catForm.name} onChange={e => setCatForm(f => ({ ...f, name: e.target.value }))} />
            </label>
            <label className="block">
              <span className="text-sm font-medium text-gray-700">Description</span>
              <textarea className="mt-1 w-full border rounded-lg px-3 py-2 text-sm" rows={3} value={catForm.description} onChange={e => setCatForm(f => ({ ...f, description: e.target.value }))} />
            </label>
            <div className="flex justify-end gap-2 pt-2">
              <button type="button" onClick={() => setShowCatModal(false)} className="px-4 py-2 border rounded-lg text-sm">Cancel</button>
              <button type="submit" className="px-4 py-2 bg-purple-600 text-white rounded-lg text-sm hover:bg-purple-700">Save</button>
            </div>
          </form>
        </Modal>
      )}

      {/* â”€â”€ SUPPLIER MODAL â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€ */}
      {showSupModal && (
        <Modal title={editingSup ? 'Edit Supplier' : 'New Supplier'} onClose={() => setShowSupModal(false)}>
          <form onSubmit={handleSaveSup} className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <label className="block">
                <span className="text-sm font-medium text-gray-700">Supplier Name *</span>
                <input required className="mt-1 w-full border rounded-lg px-3 py-2 text-sm" value={supForm.name} onChange={e => setSupForm(f => ({ ...f, name: e.target.value }))} />
              </label>
              <label className="block">
                <span className="text-sm font-medium text-gray-700">Code</span>
                <input className="mt-1 w-full border rounded-lg px-3 py-2 text-sm" value={supForm.code} onChange={e => setSupForm(f => ({ ...f, code: e.target.value }))} />
              </label>
            </div>
            <label className="block">
              <span className="text-sm font-medium text-gray-700">Contact Person</span>
              <input className="mt-1 w-full border rounded-lg px-3 py-2 text-sm" value={supForm.contact_person} onChange={e => setSupForm(f => ({ ...f, contact_person: e.target.value }))} />
            </label>
            <div className="grid grid-cols-2 gap-4">
              <label className="block">
                <span className="text-sm font-medium text-gray-700">Phone</span>
                <input className="mt-1 w-full border rounded-lg px-3 py-2 text-sm" value={supForm.phone} onChange={e => setSupForm(f => ({ ...f, phone: e.target.value }))} />
              </label>
              <label className="block">
                <span className="text-sm font-medium text-gray-700">Email</span>
                <input type="email" className="mt-1 w-full border rounded-lg px-3 py-2 text-sm" value={supForm.email} onChange={e => setSupForm(f => ({ ...f, email: e.target.value }))} />
              </label>
            </div>
            <label className="block">
              <span className="text-sm font-medium text-gray-700">Address</span>
              <textarea className="mt-1 w-full border rounded-lg px-3 py-2 text-sm" rows={2} value={supForm.address} onChange={e => setSupForm(f => ({ ...f, address: e.target.value }))} />
            </label>
            <div className="flex justify-end gap-2 pt-2">
              <button type="button" onClick={() => setShowSupModal(false)} className="px-4 py-2 border rounded-lg text-sm">Cancel</button>
              <button type="submit" className="px-4 py-2 bg-green-600 text-white rounded-lg text-sm hover:bg-green-700">Save</button>
            </div>
          </form>
        </Modal>
      )}
    </div>
  )
}

export default AdminMasterdataPage
