import React, { useState, useEffect } from 'react'
import { apiClient } from '@/api'

interface Product {
  id: number
  code: string
  name: string
  type: string
  uom: string
  category_id?: number
  min_stock?: number
  created_at: string
}

interface Category {
  id: number
  name: string
  description?: string
}

const AdminMasterdataPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'products' | 'categories'>('products')
  const [products, setProducts] = useState<Product[]>([])
  const [categories, setCategories] = useState<Category[]>([])
  const [loading, setLoading] = useState(false)
  
  // Modal states
  const [showProductModal, setShowProductModal] = useState(false)
  const [showCategoryModal, setShowCategoryModal] = useState(false)
  const [editingProduct, setEditingProduct] = useState<Product | null>(null)
  const [editingCategory, setEditingCategory] = useState<Category | null>(null)
  
  // Form states
  const [productForm, setProductForm] = useState({
    code: '',
    name: '',
    type: 'Raw Material',
    uom: 'Pcs',
    category_id: '',
    min_stock: '0'
  })
  
  const [categoryForm, setCategoryForm] = useState({
    name: '',
    description: ''
  })

  const productTypes = ['Raw Material', 'WIP', 'Finish Good', 'Service']
  const uomOptions = ['Pcs', 'Meter', 'Yard', 'Kg', 'Roll', 'Box', 'Set']

  useEffect(() => {
    fetchData()
  }, [activeTab])

  const fetchData = async () => {
    setLoading(true)
    try {
      if (activeTab === 'products') {
        // TODO: Implement products endpoint
        // const response = await apiClient.get('/masterdata/products')
        // setProducts(response.data)
        setProducts([]) // Placeholder
      } else {
        // TODO: Implement categories endpoint
        // const response = await apiClient.get('/masterdata/categories')
        // setCategories(response.data)
        setCategories([]) // Placeholder
      }
    } catch (error) {
      console.error('Failed to fetch data:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleCreateProduct = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    try {
      await apiClient.post('/masterdata/product', {
        ...productForm,
        category_id: productForm.category_id ? parseInt(productForm.category_id) : null,
        min_stock: parseFloat(productForm.min_stock)
      })
      
      setShowProductModal(false)
      resetProductForm()
      fetchData()
    } catch (error: any) {
      alert('Failed to create product: ' + error.response?.data?.detail)
    } finally {
      setLoading(false)
    }
  }

  const handleUpdateProduct = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!editingProduct) return
    
    setLoading(true)
    try {
      await apiClient.put(`/masterdata/product/${editingProduct.id}`, {
        ...productForm,
        category_id: productForm.category_id ? parseInt(productForm.category_id) : null,
        min_stock: parseFloat(productForm.min_stock)
      })
      
      setShowProductModal(false)
      setEditingProduct(null)
      resetProductForm()
      fetchData()
    } catch (error: any) {
      alert('Failed to update product: ' + error.response?.data?.detail)
    } finally {
      setLoading(false)
    }
  }

  const handleDeleteProduct = async (productId: number) => {
    if (!confirm('Are you sure you want to delete this product?')) return
    
    setLoading(true)
    try {
      await apiClient.delete(`/masterdata/product/${productId}`)
      fetchData()
    } catch (error: any) {
      alert('Failed to delete product: ' + error.response?.data?.detail)
    } finally {
      setLoading(false)
    }
  }

  const handleCreateCategory = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    try {
      await apiClient.post('/masterdata/category', categoryForm)
      
      setShowCategoryModal(false)
      resetCategoryForm()
      fetchData()
    } catch (error: any) {
      alert('Failed to create category: ' + error.response?.data?.detail)
    } finally {
      setLoading(false)
    }
  }

  const handleUpdateCategory = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!editingCategory) return
    
    setLoading(true)
    try {
      await apiClient.put(`/masterdata/category/${editingCategory.id}`, categoryForm)
      
      setShowCategoryModal(false)
      setEditingCategory(null)
      resetCategoryForm()
      fetchData()
    } catch (error: any) {
      alert('Failed to update category: ' + error.response?.data?.detail)
    } finally {
      setLoading(false)
    }
  }

  const handleDeleteCategory = async (categoryId: number) => {
    if (!confirm('Are you sure you want to delete this category?')) return
    
    setLoading(true)
    try {
      await apiClient.delete(`/masterdata/category/${categoryId}`)
      fetchData()
    } catch (error: any) {
      alert('Failed to delete category: ' + error.response?.data?.detail)
    } finally {
      setLoading(false)
    }
  }

  const openProductCreateModal = () => {
    setEditingProduct(null)
    resetProductForm()
    setShowProductModal(true)
  }

  const openProductEditModal = (product: Product) => {
    setEditingProduct(product)
    setProductForm({
      code: product.code,
      name: product.name,
      type: product.type,
      uom: product.uom,
      category_id: product.category_id?.toString() || '',
      min_stock: product.min_stock?.toString() || '0'
    })
    setShowProductModal(true)
  }

  const openCategoryCreateModal = () => {
    setEditingCategory(null)
    resetCategoryForm()
    setShowCategoryModal(true)
  }

  const openCategoryEditModal = (category: Category) => {
    setEditingCategory(category)
    setCategoryForm({
      name: category.name,
      description: category.description || ''
    })
    setShowCategoryModal(true)
  }

  const resetProductForm = () => {
    setProductForm({
      code: '',
      name: '',
      type: 'Raw Material',
      uom: 'Pcs',
      category_id: '',
      min_stock: '0'
    })
  }

  const resetCategoryForm = () => {
    setCategoryForm({
      name: '',
      description: ''
    })
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Master Data Management</h1>
          <p className="text-gray-600 mt-1">Manage products, categories, and BOMs</p>
        </div>
        {activeTab === 'products' && (
          <button
            onClick={openProductCreateModal}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
          >
            + Create Product
          </button>
        )}
        {activeTab === 'categories' && (
          <button
            onClick={openCategoryCreateModal}
            className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition"
          >
            + Create Category
          </button>
        )}
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          <button
            onClick={() => setActiveTab('products')}
            className={`py-4 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'products'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            Products
          </button>
          <button
            onClick={() => setActiveTab('categories')}
            className={`py-4 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'categories'
                ? 'border-purple-500 text-purple-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            Categories
          </button>
        </nav>
      </div>

      {/* Content */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        {activeTab === 'products' ? (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Code</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">UOM</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Min Stock</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Created</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {products.length === 0 ? (
                  <tr>
                    <td colSpan={7} className="px-6 py-8 text-center text-gray-500">
                      No products found. Create your first product to get started.
                    </td>
                  </tr>
                ) : (
                  products.map((product) => (
                    <tr key={product.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{product.code}</td>
                      <td className="px-6 py-4 text-sm text-gray-900">{product.name}</td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="px-2 py-1 text-xs font-semibold rounded-full bg-blue-100 text-blue-800">
                          {product.type}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{product.uom}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{product.min_stock || 0}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {new Date(product.created_at).toLocaleDateString()}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm">
                        <div className="flex gap-2">
                          <button
                            onClick={() => openProductEditModal(product)}
                            className="text-blue-600 hover:text-blue-800"
                          >
                            Edit
                          </button>
                          <button
                            onClick={() => handleDeleteProduct(product.id)}
                            className="text-red-600 hover:text-red-800"
                          >
                            Delete
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">ID</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Description</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {categories.length === 0 ? (
                  <tr>
                    <td colSpan={4} className="px-6 py-8 text-center text-gray-500">
                      No categories found. Create your first category to get started.
                    </td>
                  </tr>
                ) : (
                  categories.map((category) => (
                    <tr key={category.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{category.id}</td>
                      <td className="px-6 py-4 text-sm font-medium text-gray-900">{category.name}</td>
                      <td className="px-6 py-4 text-sm text-gray-500">{category.description || '-'}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm">
                        <div className="flex gap-2">
                          <button
                            onClick={() => openCategoryEditModal(category)}
                            className="text-blue-600 hover:text-blue-800"
                          >
                            Edit
                          </button>
                          <button
                            onClick={() => handleDeleteCategory(category.id)}
                            className="text-red-600 hover:text-red-800"
                          >
                            Delete
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Product Modal */}
      {showProductModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md max-h-[90vh] overflow-y-auto">
            <h2 className="text-2xl font-bold mb-4">
              {editingProduct ? 'Edit Product' : 'Create Product'}
            </h2>
            <form onSubmit={editingProduct ? handleUpdateProduct : handleCreateProduct} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Product Code *</label>
                <input
                  type="text"
                  value={productForm.code}
                  onChange={(e) => setProductForm({...productForm, code: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                  placeholder="e.g., BLU-SHARK"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Product Name *</label>
                <input
                  type="text"
                  value={productForm.name}
                  onChange={(e) => setProductForm({...productForm, name: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                  placeholder="e.g., Blue Shark Plush"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Type *</label>
                <select
                  value={productForm.type}
                  onChange={(e) => setProductForm({...productForm, type: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  {productTypes.map(type => (
                    <option key={type} value={type}>{type}</option>
                  ))}
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Unit of Measure *</label>
                <select
                  value={productForm.uom}
                  onChange={(e) => setProductForm({...productForm, uom: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  {uomOptions.map(uom => (
                    <option key={uom} value={uom}>{uom}</option>
                  ))}
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Minimum Stock</label>
                <input
                  type="number"
                  step="0.01"
                  value={productForm.min_stock}
                  onChange={(e) => setProductForm({...productForm, min_stock: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="0"
                />
              </div>
              
              <div className="flex justify-end gap-2 mt-6">
                <button
                  type="button"
                  onClick={() => {
                    setShowProductModal(false)
                    setEditingProduct(null)
                    resetProductForm()
                  }}
                  className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={loading}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition disabled:opacity-50"
                >
                  {loading ? 'Saving...' : editingProduct ? 'Update Product' : 'Create Product'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Category Modal */}
      {showCategoryModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h2 className="text-2xl font-bold mb-4">
              {editingCategory ? 'Edit Category' : 'Create Category'}
            </h2>
            <form onSubmit={editingCategory ? handleUpdateCategory : handleCreateCategory} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Category Name *</label>
                <input
                  type="text"
                  value={categoryForm.name}
                  onChange={(e) => setCategoryForm({...categoryForm, name: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
                  required
                  placeholder="e.g., Fabrics"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
                <textarea
                  value={categoryForm.description}
                  onChange={(e) => setCategoryForm({...categoryForm, description: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
                  rows={3}
                  placeholder="Category description..."
                />
              </div>
              
              <div className="flex justify-end gap-2 mt-6">
                <button
                  type="button"
                  onClick={() => {
                    setShowCategoryModal(false)
                    setEditingCategory(null)
                    resetCategoryForm()
                  }}
                  className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={loading}
                  className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition disabled:opacity-50"
                >
                  {loading ? 'Saving...' : editingCategory ? 'Update Category' : 'Create Category'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}

export default AdminMasterdataPage
