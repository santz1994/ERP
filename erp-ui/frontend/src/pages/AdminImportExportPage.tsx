import React, { useState } from 'react'
import { apiClient } from '@/api'

const AdminImportExportPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'import' | 'export'>('import')
  const [loading, setLoading] = useState(false)
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [importType, setImportType] = useState('products')
  const [exportType, setExportType] = useState('products')
  const [exportFormat, setExportFormat] = useState('csv')
  const [results, setResults] = useState<any>(null)

  const importTypes = [
    { value: 'products', label: 'Products' },
    { value: 'users', label: 'Users' },
    { value: 'bom', label: 'Bill of Materials' },
    { value: 'stock', label: 'Stock Data' },
    { value: 'manufacturing_orders', label: 'Manufacturing Orders' }
  ]

  const exportTypes = [
    { value: 'products', label: 'Products' },
    { value: 'users', label: 'Users' },
    { value: 'bom', label: 'Bill of Materials' },
    { value: 'stock', label: 'Stock Data' },
    { value: 'work_orders', label: 'Work Orders' },
    { value: 'qc_inspections', label: 'QC Inspections' },
    { value: 'production_report', label: 'Production Report' },
    { value: 'inventory_report', label: 'Inventory Report' }
  ]

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0])
    }
  }

  const handleImport = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!selectedFile) {
      alert('Please select a file to import')
      return
    }

    setLoading(true)
    setResults(null)

    try {
      const formData = new FormData()
      formData.append('file', selectedFile)

      const response = await apiClient.post(`/import-export/import/${importType}`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })

      setResults({
        success: true,
        message: 'Import completed successfully',
        data: response.data
      })
      setSelectedFile(null)
      
      // Reset file input
      const fileInput = document.getElementById('fileInput') as HTMLInputElement
      if (fileInput) fileInput.value = ''
    } catch (error: any) {
      setResults({
        success: false,
        message: 'Import failed',
        error: error.response?.data?.detail || error.message
      })
    } finally {
      setLoading(false)
    }
  }

  const handleExport = async () => {
    setLoading(true)
    setResults(null)

    try {
      const response = await apiClient.get(`/import-export/export/${exportType}`, {
        params: { format: exportFormat },
        responseType: 'blob'
      })

      // Create download link
      const blob = new Blob([response.data])
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `${exportType}_${new Date().toISOString().split('T')[0]}.${exportFormat}`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)

      setResults({
        success: true,
        message: 'Export completed successfully'
      })
    } catch (error: any) {
      setResults({
        success: false,
        message: 'Export failed',
        error: error.response?.data?.detail || error.message
      })
    } finally {
      setLoading(false)
    }
  }

  const downloadTemplate = async (type: string) => {
    try {
      const response = await apiClient.get(`/import-export/template/${type}`, {
        responseType: 'blob'
      })

      const blob = new Blob([response.data])
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `template_${type}.csv`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)
    } catch (error: any) {
      alert('Failed to download template: ' + error.message)
    }
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Import / Export</h1>
        <p className="text-gray-600 mt-1">Bulk data import and export operations</p>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          <button
            onClick={() => setActiveTab('import')}
            className={`py-4 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'import'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            Import Data
          </button>
          <button
            onClick={() => setActiveTab('export')}
            className={`py-4 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'export'
                ? 'border-green-500 text-green-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            Export Data
          </button>
        </nav>
      </div>

      {/* Content */}
      {activeTab === 'import' ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Import Form */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-xl font-bold mb-4">Import Data from CSV/Excel</h2>
            
            <form onSubmit={handleImport} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Data Type *
                </label>
                <select
                  value={importType}
                  onChange={(e) => setImportType(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  {importTypes.map(type => (
                    <option key={type.value} value={type.value}>{type.label}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Select File *
                </label>
                <input
                  id="fileInput"
                  type="file"
                  accept=".csv,.xlsx,.xls"
                  onChange={handleFileSelect}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                {selectedFile && (
                  <p className="text-sm text-gray-600 mt-2">
                    Selected: {selectedFile.name} ({(selectedFile.size / 1024).toFixed(2)} KB)
                  </p>
                )}
              </div>

              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <h3 className="font-medium text-blue-900 mb-2">Template Available</h3>
                <p className="text-sm text-blue-700 mb-3">
                  Download the template file to see the required format for importing {importType}
                </p>
                <button
                  type="button"
                  onClick={() => downloadTemplate(importType)}
                  className="text-sm text-blue-600 hover:text-blue-800 underline"
                >
                  Download Template
                </button>
              </div>

              <button
                type="submit"
                disabled={loading || !selectedFile}
                className="w-full px-4 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition disabled:opacity-50 disabled:cursor-not-allowed font-medium"
              >
                {loading ? 'Importing...' : 'Import Data'}
              </button>
            </form>
          </div>

          {/* Import Instructions */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-xl font-bold mb-4">Import Instructions</h2>
            
            <div className="space-y-4">
              <div>
                <h3 className="font-medium text-gray-900 mb-2">Step 1: Download Template</h3>
                <p className="text-sm text-gray-600">
                  Download the CSV template for the data type you want to import. The template contains the required columns and sample data.
                </p>
              </div>

              <div>
                <h3 className="font-medium text-gray-900 mb-2">Step 2: Fill in Your Data</h3>
                <p className="text-sm text-gray-600">
                  Open the template in Excel or any spreadsheet software. Fill in your data following the format shown in the sample rows.
                </p>
              </div>

              <div>
                <h3 className="font-medium text-gray-900 mb-2">Step 3: Save as CSV</h3>
                <p className="text-sm text-gray-600">
                  Save your file as CSV format. Excel (.xlsx) files are also supported but CSV is recommended.
                </p>
              </div>

              <div>
                <h3 className="font-medium text-gray-900 mb-2">Step 4: Upload and Import</h3>
                <p className="text-sm text-gray-600">
                  Select your data type, upload the file, and click Import. The system will validate and import your data.
                </p>
              </div>

              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                <h3 className="font-medium text-yellow-900 mb-2">Important Notes</h3>
                <ul className="text-sm text-yellow-700 space-y-1 list-disc list-inside">
                  <li>Column names must match the template exactly</li>
                  <li>Required fields cannot be empty</li>
                  <li>Duplicate entries will be skipped or updated</li>
                  <li>Invalid data will cause the import to fail</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Export Form */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-xl font-bold mb-4">Export Data</h2>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Data Type *
                </label>
                <select
                  value={exportType}
                  onChange={(e) => setExportType(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
                >
                  {exportTypes.map(type => (
                    <option key={type.value} value={type.value}>{type.label}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Export Format *
                </label>
                <select
                  value={exportFormat}
                  onChange={(e) => setExportFormat(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
                >
                  <option value="csv">CSV</option>
                  <option value="xlsx">Excel (.xlsx)</option>
                  <option value="pdf">PDF Report</option>
                </select>
              </div>

              <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                <h3 className="font-medium text-green-900 mb-2">Export Info</h3>
                <p className="text-sm text-green-700">
                  Export will include all data for the selected type. Large exports may take a few seconds to generate.
                </p>
              </div>

              <button
                onClick={handleExport}
                disabled={loading}
                className="w-full px-4 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition disabled:opacity-50 disabled:cursor-not-allowed font-medium"
              >
                {loading ? 'Exporting...' : 'Export Data'}
              </button>
            </div>
          </div>

          {/* Export Options */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-xl font-bold mb-4">Available Exports</h2>
            
            <div className="space-y-3">
              {exportTypes.map(type => (
                <div key={type.value} className="border border-gray-200 rounded-lg p-4 hover:border-green-500 transition">
                  <h3 className="font-medium text-gray-900">{type.label}</h3>
                  <p className="text-sm text-gray-600 mt-1">
                    Export all {type.label.toLowerCase()} data with full details
                  </p>
                </div>
              ))}
            </div>

            <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
              <h3 className="font-medium text-blue-900 mb-2">[Tip] Export Tips</h3>
              <ul className="text-sm text-blue-700 space-y-1 list-disc list-inside">
                <li>CSV format is best for re-importing</li>
                <li>Excel format preserves formatting</li>
                <li>PDF format is best for reports</li>
                <li>Exports are timestamped automatically</li>
              </ul>
            </div>
          </div>
        </div>
      )}

      {/* Results Display */}
      {results && (
        <div className={`rounded-lg p-6 ${
          results.success 
            ? 'bg-green-50 border border-green-200' 
            : 'bg-red-50 border border-red-200'
        }`}>
          <h3 className={`font-bold text-lg mb-2 ${
            results.success ? 'text-green-900' : 'text-red-900'
          }`}>
            {results.success ? 'Success' : 'Error'}
          </h3>
          <p className={`text-sm ${results.success ? 'text-green-700' : 'text-red-700'}`}>
            {results.message}
          </p>
          {results.data && (
            <div className="mt-4 bg-white rounded p-4">
              <pre className="text-xs text-gray-700 overflow-x-auto">
                {JSON.stringify(results.data, null, 2)}
              </pre>
            </div>
          )}
          {results.error && (
            <div className="mt-4 bg-white rounded p-4">
              <pre className="text-xs text-red-600 overflow-x-auto">
                {results.error}
              </pre>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default AdminImportExportPage
