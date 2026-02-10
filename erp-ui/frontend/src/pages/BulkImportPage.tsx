/**
 * Bulk Import Page - Session 49 Phase 8
 * Template-based bulk import for masterdata (Suppliers, Materials, Articles, BOM)
 * 
 * Features:
 * - Drag & drop Excel files
 * - Download templates with sample data
 * - Real-time validation feedback
 * - Import history  table
 * - Transaction-safe error handling
 */
import React, { useState } from 'react'
import { Upload, Download, CheckCircle, XCircle, AlertCircle, FileSpreadsheet, Users, Package, List } from 'lucide-react'
import { toast } from 'react-hot-toast'
import { importsApi } from '@/api'

interface ImportResult {
  success: boolean
  imported_count: number
  updated_count: number
  errors: string[]
  execution_time_ms: number
}

const BulkImportPage: React.FC = () => {
  const [activeImportType, setActiveImportType] = useState<'suppliers' | 'materials' | 'articles' | 'bom'>('suppliers')
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [isDragging, setIsDragging] = useState<boolean>(false)
  const [isUploading, setIsUploading] = useState<boolean>(false)
  const [importResult, setImportResult] = useState<ImportResult | null>(null)

  const importTypes = [
    {
      id: 'suppliers' as const,
      name: 'Suppliers',
      icon: Users,
      color: 'blue',
      description: 'Import supplier/partner masterdata',
    },
    {
      id: 'materials' as const,
      name: 'Materials',
      icon: Package,
      color: 'green',
      description: 'Import raw materials, fabric, thread, etc.',
    },
    {
      id: 'articles' as const,
      name: 'Articles',
      icon: FileSpreadsheet,
      color: 'yellow',
      description: 'Import finished goods articles',
    },
    {
      id: 'bom' as const,
      name: 'BOM',
      icon: List,
      color: 'red',
      description: 'Import Bill of Materials structures',
    },
  ]

  // ====================== FILE HANDLING ======================

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      validateAndSetFile(file)
    }
  }

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(true)
  }

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)

    const file = e.dataTransfer.files[0]
    if (file) {
      validateAndSetFile(file)
    }
  }

  const validateAndSetFile = (file: File) => {
    // Validate file extension
    if (!file.name.endsWith('.xlsx') && !file.name.endsWith('.xls')) {
      toast.error('❌ Invalid file format. Please upload Excel file (.xlsx or .xls)')
      return
    }

    // Validate file size (max 10MB)
    if (file.size > 10 * 1024 * 1024) {
      toast.error('❌ File too large. Maximum size is 10MB.')
      return
    }

    setSelectedFile(file)
    setImportResult(null)
    toast.success(`✅ File selected: ${file.name} (${(file.size / 1024).toFixed(2)} KB)`)
  }

  // ====================== IMPORT EXECUTION ======================

  const handleImport = async () => {
    if (!selectedFile) {
      toast.error('❌ Please select a file first')
      return
    }

    setIsUploading(true)
    setImportResult(null)

    try {
      let response

      // Call appropriate API based on import type
      switch (activeImportType) {
        case 'suppliers':
          response = await importsApi.importSuppliers(selectedFile)
          break
        case 'materials':
          response = await importsApi.importMaterials(selectedFile)
          break
        case 'articles':
          response = await importsApi.importArticles(selectedFile)
          break
        case 'bom':
          response = await importsApi.importBOM(selectedFile)
          break
      }

      const result = (response.data || { success: false, imported_count: 0, updated_count: 0, execution_time_ms: 0, errors: [] }) as ImportResult

      setImportResult(result)

      if (result.success) {
        toast.success(
          `✅ Import completed!\n` +
          `   Imported: ${result.imported_count}\n` +
          `   Updated: ${result.updated_count}\n` +
          `   Time: ${result.execution_time_ms}ms`
        )
        setSelectedFile(null)
      } else {
        toast.error('❌ Import failed. See errors below.')
      }
    } catch (error: any) {
      const errorDetail = error.response?.data?.detail
      
      if (errorDetail && typeof errorDetail === 'object') {
        // Detailed error from backend
        setImportResult({
          success: false,
          imported_count: errorDetail.imported_count || 0,
          updated_count: errorDetail.updated_count || 0,
          errors: errorDetail.errors || [errorDetail.message || 'Unknown error'],
          execution_time_ms: 0
        })
        toast.error(`❌ ${errorDetail.message || 'Import failed'}`)
      } else {
        toast.error(`❌ Import failed: ${error.message}`)
        setImportResult({
          success: false,
          imported_count: 0,
          updated_count: 0,
          errors: [error.message],
          execution_time_ms: 0
        })
      }
    } finally {
      setIsUploading(false)
    }
  }

  // ====================== TEMPLATE DOWNLOAD ======================

  const handleDownloadTemplate = async () => {
    try {
      toast.loading(`⏳ Generating ${activeImportType} template...`)

      const response = await importsApi.downloadTemplate(activeImportType)

      // Create download link
      const blob = new Blob([response.data])
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `${activeImportType}_template_${new Date().toISOString().split('T')[0]}.xlsx`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)

      toast.dismiss()
      toast.success(`✅ Template downloaded: ${link.download}`)
    } catch (error: any) {
      toast.dismiss()
      toast.error(`❌ Failed to download template: ${error.message}`)
    }
  }

  // ====================== RENDER ======================

  const activeType = importTypes.find((t) => t.id === activeImportType)
  const ColorIcon = activeType?.icon || FileSpreadsheet

  return (
    <div className="p-6 max-w-7xl mx-auto bg-gray-50 min-h-screen">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-800 mb-2">📦 Masterdata Bulk Import</h1>
        <p className="text-gray-600">
          Import suppliers, materials, articles, and BOM structures from Excel templates. 
          Safe, validated, transaction-based imports with detailed error reporting.
        </p>
      </div>

      {/* Import Type Tabs */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        {importTypes.map((type) => {
          const Icon = type.icon
          const isActive = activeImportType === type.id
          return (
            <button
              key={type.id}
              onClick={() => {
                setActiveImportType(type.id)
                setSelectedFile(null)
                setImportResult(null)
              }}
              className={`
                p-4 rounded-lg border-2 transition-all
                ${isActive 
                  ? `border-${type.color}-500 bg-${type.color}-50 shadow-md` 
                  : 'border-gray-300 bg-white hover:border-gray-400'
                }
              `}
            >
              <Icon 
                className={`w-8 h-8 mx-auto mb-2 ${isActive ? `text-${type.color}-600` : 'text-gray-400'}`} 
              />
              <div className={`font-semibold ${isActive ? `text-${type.color}-700` : 'text-gray-700'}`}>
                {type.name}
              </div>
              <div className="text-xs text-gray-500 mt-1">{type.description}</div>
            </button>
          )
        })}
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        
        {/* Left Column: Upload Zone */}
        <div className="space-y-6">
          
          {/* Template Download Card */}
          <div className="bg-white p-6 rounded-lg shadow-md border border-gray-200">
            <div className="flex items-center mb-4">
              <Download className="w-5 h-5 text-blue-600 mr-2" />
              <h2 className="text-xl font-semibold text-gray-800">Step 1: Download Template</h2>
            </div>
            <p className="text-gray-600 mb-4">
              Download the Excel template with sample data and column headers.
              Fill in your data starting from row 3 (row 1 = headers, row 2 = sample).
            </p>
            <button
              onClick={handleDownloadTemplate}
              className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-4 rounded-lg transition-colors flex items-center justify-center"
            >
              <Download className="w-5 h-5 mr-2" />
              Download {activeType?.name} Template
            </button>
          </div>

          {/* Upload Zone Card */}
          <div className="bg-white p-6 rounded-lg shadow-md border border-gray-200">
            <div className="flex items-center mb-4">
              <Upload className="w-5 h-5 text-green-600 mr-2" />
              <h2 className="text-xl font-semibold text-gray-800">Step 2: Upload Filled Template</h2>
            </div>
            
            {/* Drag & Drop Zone */}
            <div
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
              className={`
                border-2 border-dashed rounded-lg p-8 text-center transition-all
                ${isDragging 
                  ? 'border-blue-500 bg-blue-50' 
                  : 'border-gray-300 bg-gray-50 hover:bg-gray-100'
                }
              `}
            >
              <FileSpreadsheet className="w-16 h-16 text-gray-400 mx-auto mb-4" />
              
              {selectedFile ? (
                <div className="space-y-2">
                  <p className="font-semibold text-gray-800">{selectedFile.name}</p>
                  <p className="text-sm text-gray-500">
                    {(selectedFile.size / 1024).toFixed(2)} KB
                  </p>
                  <button
                    onClick={() => setSelectedFile(null)}
                    className="text-red-500 hover:text-red-700 text-sm underline"
                  >
                    Remove file
                  </button>
                </div>
              ) : (
                <>
                  <p className="text-gray-600 mb-2">
                    Drag & drop your Excel file here, or
                  </p>
                  <label className="inline-block bg-gray-200 hover:bg-gray-300 text-gray-800 font-semibold py-2 px-4 rounded-lg cursor-pointer transition-colors">
                    Browse Files
                    <input
                      type="file"
                      accept=".xlsx,.xls"
                      onChange={handleFileSelect}
                      className="hidden"
                    />
                  </label>
                  <p className="text-xs text-gray-500 mt-2">
                    Accepted: .xlsx, .xls (Max 10MB)
                  </p>
                </>
              )}
            </div>

            {/* Import Button */}
            <button
              onClick={handleImport}
              disabled={!selectedFile || isUploading}
              className={`
                w-full mt-4 font-semibold py-3 px-4 rounded-lg transition-colors flex items-center justify-center
                ${selectedFile && !isUploading
                  ? 'bg-green-600 hover:bg-green-700 text-white'
                  : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                }
              `}
            >
              {isUploading ? (
                <>
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                  Uploading & Validating...
                </>
              ) : (
                <>
                  <Upload className="w-5 h-5 mr-2" />
                  Import {activeType?.name}
                </>
              )}
            </button>
          </div>

        </div>

        {/* Right Column: Results & History */}
        <div className="space-y-6">
          
          {/* Import Result Card */}
          {importResult && (
            <div className={`
              p-6 rounded-lg shadow-md border-2
              ${importResult.success 
                ? 'bg-green-50 border-green-500' 
                : 'bg-red-50 border-red-500'
              }
            `}>
              <div className="flex items-center mb-4">
                {importResult.success ? (
                  <CheckCircle className="w-6 h-6 text-green-600 mr-2" />
                ) : (
                  <XCircle className="w-6 h-6 text-red-600 mr-2" />
                )}
                <h2 className={`text-xl font-semibold ${importResult.success ? 'text-green-800' : 'text-red-800'}`}>
                  {importResult.success ? 'Import Successful' : 'Import Failed'}
                </h2>
              </div>

              {/* Success Stats */}
              {importResult.success && (
                <div className="grid grid-cols-3 gap-4 mb-4">
                  <div className="text-center">
                    <div className="text-2xl font-bold text-green-700">{importResult.imported_count}</div>
                    <div className="text-xs text-gray-600">New Records</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-blue-700">{importResult.updated_count}</div>
                    <div className="text-xs text-gray-600">Updated</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-gray-700">{importResult.execution_time_ms}ms</div>
                    <div className="text-xs text-gray-600">Execution Time</div>
                  </div>
                </div>
              )}

              {/* Error List */}
              {importResult.errors.length > 0 && (
                <div className="mt-4">
                  <div className="flex items-center mb-2">
                    <AlertCircle className="w-5 h-5 text-red-600 mr-2" />
                    <h3 className="font-semibold text-red-800">Errors ({importResult.errors.length})</h3>
                  </div>
                  <div className="bg-white p-4 rounded-lg max-h-64 overflow-y-auto">
                    {importResult.errors.map((error, idx) => (
                      <div key={idx} className="text-sm text-red-700 mb-2 border-l-4 border-red-500 pl-3">
                        {error}
                      </div>
                    ))}
                  </div>
                  <p className="text-xs text-red-600 mt-2">
                    ⚠️ Transaction rolled back. No data was imported. Fix errors and try again.
                  </p>
                </div>
              )}
            </div>
          )}

          {/* Instructions Card */}
          <div className="bg-blue-50 p-6 rounded-lg border border-blue-200">
            <div className="flex items-center mb-3">
              <AlertCircle className="w-5 h-5 text-blue-600 mr-2" />
              <h3 className="font-semibold text-blue-900">Import Instructions</h3>
            </div>
            <div className="text-sm text-blue-800 space-y-2">
              <p>✅ <strong>Row 1:</strong> Column headers (mandatory, do not modify)</p>
              <p>✅ <strong>Row 2:</strong> Sample data (for reference, can be deleted)</p>
              <p>✅ <strong>Row 3+:</strong> Your actual data to import</p>
              <hr className="border-blue-300 my-3" />
              <p>🔒 <strong>Transaction Safe:</strong> All inserts are atomic. If ANY error occurs, entire import is rolled back (zero records imported).</p>
              <p>🔄 <strong>UPDATE Mode:</strong> Existing records (matched by code) will be UPDATED, not duplicated.</p>
              <p>⚡ <strong>Validation:</strong> File format, column names, data types, business rules, foreign keys, unique constraints are all checked before insertion.</p>
            </div>
          </div>

          {/* Import Order Guide */}
          <div className="bg-yellow-50 p-6 rounded-lg border border-yellow-200">
            <div className="flex items-center mb-3">
              <AlertCircle className="w-5 h-5 text-yellow-600 mr-2" />
              <h3 className="font-semibold text-yellow-900">⚠️ Import Sequence (IMPORTANT)</h3>
            </div>
            <div className="text-sm text-yellow-800 space-y-2">
              <p><strong>Phase 1 (Foundation Data):</strong></p>
              <ol className="list-decimal list-inside ml-4 space-y-1">
                <li>Suppliers (no dependencies)</li>
                <li>Materials (requires categories to exist)</li>
                <li>Articles (requires categories to exist)</li>
              </ol>
              <p className="mt-3"><strong>Phase 2 (Relationships):</strong></p>
              <ol className="list-decimal list-inside ml-4 space-y-1" start={4}>
                <li>BOM (requires articles + materials from Phase 1)</li>
              </ol>
              <p className="mt-3 font-semibold text-red-600">
                ❌ DO NOT import BOM before materials/articles! Foreign key validation will fail.
              </p>
            </div>
          </div>

        </div>
      </div>
    </div>
  )
}

export default BulkImportPage
