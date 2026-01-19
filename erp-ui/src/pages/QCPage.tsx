import React, { useState, useEffect } from 'react'
import { apiClient } from '@/api/client'

interface QCInspection {
  id: number
  work_order_id: number
  type: string
  status: string
  defect_reason?: string
  inspected_by: number
  inspector_name?: string
  created_at: string
}

interface QCLabTest {
  id: number
  batch_number: string
  test_type: string
  test_result: string
  measured_value?: number
  inspector_id: number
  inspector_name?: string
  evidence_photo?: string
  created_at: string
}

interface QCStats {
  total_inspections: number
  passed: number
  failed: number
  pass_rate: number
  today_inspections: number
}

const QCPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'inspections' | 'lab-tests'>('inspections')
  const [inspections, setInspections] = useState<QCInspection[]>([])
  const [labTests, setLabTests] = useState<QCLabTest[]>([])
  const [stats, setStats] = useState<QCStats | null>(null)
  const [loading, setLoading] = useState(false)
  
  // Modal states
  const [showInspectionModal, setShowInspectionModal] = useState(false)
  const [showLabTestModal, setShowLabTestModal] = useState(false)
  
  // Form states
  const [inspectionForm, setInspectionForm] = useState({
    work_order_id: '',
    type: 'Inline Sewing',
    status: 'Pass',
    defect_reason: ''
  })
  
  const [labTestForm, setLabTestForm] = useState({
    batch_number: '',
    test_type: 'Drop Test',
    test_result: 'Pass',
    measured_value: ''
  })

  useEffect(() => {
    fetchData()
    const interval = setInterval(fetchData, 5000) // Poll every 5 seconds
    return () => clearInterval(interval)
  }, [activeTab])

  const fetchData = async () => {
    setLoading(true)
    try {
      // Fetch QC stats
      const statsRes = await apiClient.get('/quality/stats')
      setStats(statsRes.data)
      
      if (activeTab === 'inspections') {
        // Fetch inspections
        const inspRes = await apiClient.get('/quality/inspections')
        setInspections(inspRes.data)
      } else {
        // Fetch lab tests
        const labRes = await apiClient.get('/quality/lab-tests')
        setLabTests(labRes.data)
      }
    } catch (error) {
      console.error('Failed to fetch QC data:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleCreateInspection = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    try {
      await apiClient.post('/quality/inspection', {
        work_order_id: parseInt(inspectionForm.work_order_id),
        type: inspectionForm.type,
        status: inspectionForm.status,
        defect_reason: inspectionForm.status === 'Fail' ? inspectionForm.defect_reason : null
      })
      
      setShowInspectionModal(false)
      setInspectionForm({
        work_order_id: '',
        type: 'Inline Sewing',
        status: 'Pass',
        defect_reason: ''
      })
      fetchData()
    } catch (error: any) {
      alert('Failed to create inspection: ' + error.response?.data?.detail)
    } finally {
      setLoading(false)
    }
  }

  const handleCreateLabTest = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    try {
      await apiClient.post('/quality/lab-test', {
        batch_number: labTestForm.batch_number,
        test_type: labTestForm.test_type,
        test_result: labTestForm.test_result,
        measured_value: labTestForm.measured_value ? parseFloat(labTestForm.measured_value) : null
      })
      
      setShowLabTestModal(false)
      setLabTestForm({
        batch_number: '',
        test_type: 'Drop Test',
        test_result: 'Pass',
        measured_value: ''
      })
      fetchData()
    } catch (error: any) {
      alert('Failed to create lab test: ' + error.response?.data?.detail)
    } finally {
      setLoading(false)
    }
  }

  const getStatusBadgeClass = (status: string) => {
    return status === 'Pass' 
      ? 'bg-green-100 text-green-800'
      : 'bg-red-100 text-red-800'
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-900">Quality Control</h1>
        <div className="flex gap-2">
          {activeTab === 'inspections' && (
            <button
              onClick={() => setShowInspectionModal(true)}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
            >
              + New Inspection
            </button>
          )}
          {activeTab === 'lab-tests' && (
            <button
              onClick={() => setShowLabTestModal(true)}
              className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition"
            >
              + New Lab Test
            </button>
          )}
        </div>
      </div>

      {/* Statistics Cards */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl p-6 text-white shadow-lg">
            <div className="text-sm opacity-90">Total Inspections</div>
            <div className="text-3xl font-bold mt-2">{stats.total_inspections}</div>
          </div>
          <div className="bg-gradient-to-br from-green-500 to-green-600 rounded-xl p-6 text-white shadow-lg">
            <div className="text-sm opacity-90">Passed</div>
            <div className="text-3xl font-bold mt-2">{stats.passed}</div>
          </div>
          <div className="bg-gradient-to-br from-red-500 to-red-600 rounded-xl p-6 text-white shadow-lg">
            <div className="text-sm opacity-90">Failed</div>
            <div className="text-3xl font-bold mt-2">{stats.failed}</div>
          </div>
          <div className="bg-gradient-to-br from-purple-500 to-purple-600 rounded-xl p-6 text-white shadow-lg">
            <div className="text-sm opacity-90">Pass Rate</div>
            <div className="text-3xl font-bold mt-2">{stats.pass_rate.toFixed(1)}%</div>
          </div>
        </div>
      )}

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          <button
            onClick={() => setActiveTab('inspections')}
            className={`py-4 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'inspections'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            Inspections
          </button>
          <button
            onClick={() => setActiveTab('lab-tests')}
            className={`py-4 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'lab-tests'
                ? 'border-purple-500 text-purple-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            Lab Tests
          </button>
        </nav>
      </div>

      {/* Content */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        {activeTab === 'inspections' ? (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">ID</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">WO ID</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Defect Reason</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Inspector</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {inspections.length === 0 ? (
                  <tr>
                    <td colSpan={7} className="px-6 py-8 text-center text-gray-500">
                      No inspections found. Create your first inspection to get started.
                    </td>
                  </tr>
                ) : (
                  inspections.map((inspection) => (
                    <tr key={inspection.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{inspection.id}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{inspection.work_order_id}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{inspection.type}</td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`px-2 py-1 text-xs font-semibold rounded-full ${getStatusBadgeClass(inspection.status)}`}>
                          {inspection.status}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-900">{inspection.defect_reason || '-'}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {inspection.inspector_name || `ID: ${inspection.inspected_by}`}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {new Date(inspection.created_at).toLocaleDateString()}
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
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Batch</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Test Type</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Result</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Measured Value</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Inspector</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {labTests.length === 0 ? (
                  <tr>
                    <td colSpan={7} className="px-6 py-8 text-center text-gray-500">
                      No lab tests found. Create your first lab test to get started.
                    </td>
                  </tr>
                ) : (
                  labTests.map((test) => (
                    <tr key={test.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{test.id}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{test.batch_number}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{test.test_type}</td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`px-2 py-1 text-xs font-semibold rounded-full ${getStatusBadgeClass(test.test_result)}`}>
                          {test.test_result}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {test.measured_value ? test.measured_value.toFixed(2) : '-'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {test.inspector_name || `ID: ${test.inspector_id}`}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {new Date(test.created_at).toLocaleDateString()}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Inspection Modal */}
      {showInspectionModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h2 className="text-2xl font-bold mb-4">New Inspection</h2>
            <form onSubmit={handleCreateInspection} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Work Order ID</label>
                <input
                  type="number"
                  value={inspectionForm.work_order_id}
                  onChange={(e) => setInspectionForm({...inspectionForm, work_order_id: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Type</label>
                <select
                  value={inspectionForm.type}
                  onChange={(e) => setInspectionForm({...inspectionForm, type: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option>Inline Sewing</option>
                  <option>Final Metal Detector</option>
                  <option>Incoming</option>
                  <option>Fabric Inspection</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Status</label>
                <select
                  value={inspectionForm.status}
                  onChange={(e) => setInspectionForm({...inspectionForm, status: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option>Pass</option>
                  <option>Fail</option>
                </select>
              </div>
              
              {inspectionForm.status === 'Fail' && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Defect Reason</label>
                  <textarea
                    value={inspectionForm.defect_reason}
                    onChange={(e) => setInspectionForm({...inspectionForm, defect_reason: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    rows={3}
                    required
                  />
                </div>
              )}
              
              <div className="flex justify-end gap-2 mt-6">
                <button
                  type="button"
                  onClick={() => setShowInspectionModal(false)}
                  className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={loading}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition disabled:opacity-50"
                >
                  {loading ? 'Creating...' : 'Create Inspection'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Lab Test Modal */}
      {showLabTestModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h2 className="text-2xl font-bold mb-4">New Lab Test</h2>
            <form onSubmit={handleCreateLabTest} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Batch Number</label>
                <input
                  type="text"
                  value={labTestForm.batch_number}
                  onChange={(e) => setLabTestForm({...labTestForm, batch_number: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
                  required
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Test Type</label>
                <select
                  value={labTestForm.test_type}
                  onChange={(e) => setLabTestForm({...labTestForm, test_type: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
                >
                  <option>Drop Test</option>
                  <option>Stability 10</option>
                  <option>Stability 27</option>
                  <option>Seam Strength</option>
                  <option>Color Fastness</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Test Result</label>
                <select
                  value={labTestForm.test_result}
                  onChange={(e) => setLabTestForm({...labTestForm, test_result: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
                >
                  <option>Pass</option>
                  <option>Fail</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Measured Value (Optional)</label>
                <input
                  type="number"
                  step="0.01"
                  value={labTestForm.measured_value}
                  onChange={(e) => setLabTestForm({...labTestForm, measured_value: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
                  placeholder="e.g., 12.5"
                />
              </div>
              
              <div className="flex justify-end gap-2 mt-6">
                <button
                  type="button"
                  onClick={() => setShowLabTestModal(false)}
                  className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={loading}
                  className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition disabled:opacity-50"
                >
                  {loading ? 'Creating...' : 'Create Lab Test'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}

export default QCPage
