/**
 * Document Templates Settings Page (ADMIN only)
 * Customize document templates and forms
 */

import React, { useState, useEffect } from 'react'
import { FileText, Save, Plus } from 'lucide-react'
import { useUIStore } from '@/store'

interface Template {
  id: string
  name: string
  type: 'invoice' | 'purchase_order' | 'delivery_note' | 'report'
  header: string
  footer: string
  includeQRCode: boolean
}

export const DocumentTemplatesSettings: React.FC = () => {
  const { addNotification } = useUIStore()
  const [loading, setLoading] = useState(false)
  const [templates, setTemplates] = useState<Template[]>([
    { id: '1', name: 'Standard Invoice', type: 'invoice', header: 'INVOICE', footer: 'Thank you for your business', includeQRCode: true },
    { id: '2', name: 'Purchase Order', type: 'purchase_order', header: 'PURCHASE ORDER', footer: '', includeQRCode: false },
  ])
  const [editingId, setEditingId] = useState<string | null>(null)
  const [editingTemplate, setEditingTemplate] = useState<Template | null>(null)

  useEffect(() => {
    const saved = localStorage.getItem('documentTemplates')
    if (saved) setTemplates(JSON.parse(saved))
  }, [])

  const handleSave = async () => {
    try {
      setLoading(true)
      localStorage.setItem('documentTemplates', JSON.stringify(templates))
      addNotification('success', 'Document templates saved!')
    } catch (error) {
      addNotification('error', 'Failed to save templates')
    } finally {
      setLoading(false)
    }
  }

  const handleEditStart = (template: Template) => {
    setEditingId(template.id)
    setEditingTemplate({ ...template })
  }

  const handleEditEnd = () => {
    if (editingTemplate) {
      setTemplates(prev => prev.map(t => t.id === editingTemplate.id ? editingTemplate : t))
    }
    setEditingId(null)
    setEditingTemplate(null)
  }

  const handleAddTemplate = () => {
    const newId = (Math.max(...templates.map(t => parseInt(t.id)), 0) + 1).toString()
    const newTemplate: Template = {
      id: newId,
      name: 'New Template',
      type: 'invoice',
      header: '',
      footer: '',
      includeQRCode: false,
    }
    setTemplates([...templates, newTemplate])
  }

  const handleDeleteTemplate = (id: string) => {
    setTemplates(prev => prev.filter(t => t.id !== id))
    addNotification('success', 'Template deleted')
  }

  return (
    <div className="p-6 max-w-4xl">
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3 mb-2">
            <FileText className="w-8 h-8 text-green-600" />
            <h1 className="text-3xl font-bold text-gray-900">Document Templates</h1>
          </div>
          <button 
            onClick={handleAddTemplate}
            className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg flex items-center gap-2"
          >
            <Plus size={18} /> New Template
          </button>
        </div>
        <p className="text-gray-600">Customize document templates and forms used in the system</p>
      </div>

      <div className="space-y-4">
        {templates.map(template => (
          <div key={template.id} className="bg-white rounded-lg shadow-md p-6">
            {editingId === template.id && editingTemplate ? (
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Template Name</label>
                    <input 
                      type="text" 
                      value={editingTemplate.name}
                      onChange={(e) => setEditingTemplate(prev => prev ? { ...prev, name: e.target.value } : null)}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Document Type</label>
                    <select 
                      value={editingTemplate.type}
                      onChange={(e) => setEditingTemplate(prev => prev ? { ...prev, type: e.target.value as any } : null)}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="invoice">Invoice</option>
                      <option value="purchase_order">Purchase Order</option>
                      <option value="delivery_note">Delivery Note</option>
                      <option value="report">Report</option>
                    </select>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Header Text</label>
                  <input 
                    type="text" 
                    value={editingTemplate.header}
                    onChange={(e) => setEditingTemplate(prev => prev ? { ...prev, header: e.target.value } : null)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Footer Text</label>
                  <textarea 
                    value={editingTemplate.footer}
                    onChange={(e) => setEditingTemplate(prev => prev ? { ...prev, footer: e.target.value } : null)}
                    rows={3}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>

                <label className="flex items-center gap-2 cursor-pointer">
                  <input 
                    type="checkbox" 
                    checked={editingTemplate.includeQRCode}
                    onChange={() => setEditingTemplate(prev => prev ? { ...prev, includeQRCode: !prev.includeQRCode } : null)}
                    className="w-4 h-4"
                  />
                  <span className="text-sm font-medium text-gray-700">Include QR Code</span>
                </label>

                <div className="flex gap-2">
                  <button 
                    onClick={handleEditEnd}
                    className="flex-1 bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-lg"
                  >
                    Done Editing
                  </button>
                  <button 
                    onClick={() => handleDeleteTemplate(template.id)}
                    className="flex-1 bg-red-600 hover:bg-red-700 text-white font-medium py-2 px-4 rounded-lg"
                  >
                    Delete
                  </button>
                </div>
              </div>
            ) : (
              <div className="flex justify-between items-start">
                <div>
                  <h3 className="font-bold text-lg text-gray-900">{template.name}</h3>
                  <p className="text-sm text-gray-600 mt-1">Type: <span className="font-medium">{template.type.replace('_', ' ')}</span></p>
                  <p className="text-sm text-gray-600">QR Code: {template.includeQRCode ? '✓ Enabled' : '✗ Disabled'}</p>
                </div>
                <button 
                  onClick={() => handleEditStart(template)}
                  className="bg-blue-100 hover:bg-blue-200 text-blue-700 px-4 py-2 rounded-lg font-medium"
                >
                  Edit
                </button>
              </div>
            )}
          </div>
        ))}
      </div>

      <button 
        onClick={handleSave} 
        disabled={loading} 
        className="w-full mt-6 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-medium py-2 px-4 rounded-lg flex items-center justify-center gap-2 transition"
      >
        <Save size={18} /> {loading ? 'Saving...' : 'Save All Templates'}
      </button>
    </div>
  )
}
