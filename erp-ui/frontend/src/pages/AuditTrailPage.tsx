import { useState, useEffect } from 'react';
import { api } from '@/api/client';
import { useAuthStore } from '@/store/index';  // Fix: changed from authStore to index

interface AuditLog {
  id: number;
  timestamp: string;
  username: string;
  user_role: string | null;
  ip_address: string | null;
  action: string;
  module: string;
  entity_type: string | null;
  entity_id: number | null;
  description: string;
  old_values: any;
  new_values: any;
  request_method: string | null;
  request_path: string | null;
}

interface AuditSummary {
  total_events: number;
  events_last_24h: number;
  events_last_7d: number;
  top_users: Array<{ username: string; event_count: number }>;
  top_modules: Array<{ module: string; event_count: number }>;
  recent_critical_events: Array<any>;
}

export default function AuditTrailPage() {
  const { user } = useAuthStore();
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [summary, setSummary] = useState<AuditSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedLog, setSelectedLog] = useState<AuditLog | null>(null);
  
  // Filters
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [filters, setFilters] = useState({
    username: '',
    action: '',
    module: '',
    search: '',
    start_date: '',
    end_date: ''
  });

  useEffect(() => {
    fetchAuditLogs();
    fetchSummary();
  }, [page, filters]);

  const fetchAuditLogs = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams({
        page: page.toString(),
        page_size: '20',
        ...Object.fromEntries(
          Object.entries(filters).filter(([_, v]) => v !== '')
        )
      });
      
      const response = await api.get(`/api/audit/logs?${params}`);
      setLogs(response.data.data);
      setTotalPages(response.data.total_pages);
    } catch (error) {
      console.error('Failed to fetch audit logs:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchSummary = async () => {
    try {
      const response = await api.get('/api/audit/summary');
      setSummary(response.data);
    } catch (error) {
      console.error('Failed to fetch summary:', error);
    }
  };

  const handleExportCSV = async () => {
    try {
      const params = new URLSearchParams({
        ...Object.fromEntries(
          Object.entries(filters).filter(([_, v]) => v !== '')
        )
      });
      
      window.open(`/api/audit/export/csv?${params}`, '_blank');
    } catch (error) {
      console.error('Failed to export:', error);
    }
  };

  const getActionBadgeColor = (action: string) => {
    const colors: Record<string, string> = {
      CREATE: 'bg-green-100 text-green-800',
      UPDATE: 'bg-blue-100 text-blue-800',
      DELETE: 'bg-red-100 text-red-800',
      APPROVE: 'bg-purple-100 text-purple-800',
      LOGIN: 'bg-gray-100 text-gray-800',
      TRANSFER: 'bg-yellow-100 text-yellow-800',
      EXPORT: 'bg-orange-100 text-orange-800'
    };
    return colors[action] || 'bg-gray-100 text-gray-800';
  };

  if (!['DEVELOPER', 'SUPERADMIN', 'MANAGER'].includes(user?.role || '')) {
    return (
      <div className="p-6">
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-800">Access Denied: Audit Trail requires DEVELOPER, SUPERADMIN, or MANAGER role</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Audit Trail</h1>
        <p className="text-sm text-gray-600 mt-1">
          ISO 27001 A.12.4.1 Event Logging | SOX 404 Compliance
        </p>
      </div>

      {/* Summary Cards */}
      {summary && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div className="bg-white rounded-lg shadow p-4">
            <div className="text-sm text-gray-600">Total Events</div>
            <div className="text-2xl font-bold text-gray-900">{summary.total_events.toLocaleString()}</div>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <div className="text-sm text-gray-600">Last 24 Hours</div>
            <div className="text-2xl font-bold text-blue-600">{summary.events_last_24h.toLocaleString()}</div>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <div className="text-sm text-gray-600">Last 7 Days</div>
            <div className="text-2xl font-bold text-green-600">{summary.events_last_7d.toLocaleString()}</div>
          </div>
        </div>
      )}

      {/* Filters */}
      <div className="bg-white rounded-lg shadow p-4 mb-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <input
            type="text"
            placeholder="Search username..."
            value={filters.username}
            onChange={(e) => setFilters({ ...filters, username: e.target.value })}
            className="border border-gray-300 rounded px-3 py-2"
          />
          
          <select
            value={filters.action}
            onChange={(e) => setFilters({ ...filters, action: e.target.value })}
            className="border border-gray-300 rounded px-3 py-2"
          >
            <option value="">All Actions</option>
            <option value="CREATE">CREATE</option>
            <option value="UPDATE">UPDATE</option>
            <option value="DELETE">DELETE</option>
            <option value="APPROVE">APPROVE</option>
            <option value="LOGIN">LOGIN</option>
            <option value="TRANSFER">TRANSFER</option>
            <option value="EXPORT">EXPORT</option>
          </select>
          
          <select
            value={filters.module}
            onChange={(e) => setFilters({ ...filters, module: e.target.value })}
            className="border border-gray-300 rounded px-3 py-2"
          >
            <option value="">All Modules</option>
            <option value="Authentication">Authentication</option>
            <option value="PPIC">PPIC</option>
            <option value="Warehouse">Warehouse</option>
            <option value="Cutting">Cutting</option>
            <option value="Embroidery">Embroidery</option>
            <option value="Sewing">Sewing</option>
            <option value="Quality Control">Quality Control</option>
            <option value="Reports">Reports</option>
          </select>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4">
          <input
            type="text"
            placeholder="Search description..."
            value={filters.search}
            onChange={(e) => setFilters({ ...filters, search: e.target.value })}
            className="border border-gray-300 rounded px-3 py-2"
          />
          
          <input
            type="datetime-local"
            value={filters.start_date}
            onChange={(e) => setFilters({ ...filters, start_date: e.target.value })}
            className="border border-gray-300 rounded px-3 py-2"
          />
          
          <input
            type="datetime-local"
            value={filters.end_date}
            onChange={(e) => setFilters({ ...filters, end_date: e.target.value })}
            className="border border-gray-300 rounded px-3 py-2"
          />
        </div>
        
        <div className="flex justify-between items-center mt-4">
          <button
            onClick={() => setFilters({
              username: '',
              action: '',
              module: '',
              search: '',
              start_date: '',
              end_date: ''
            })}
            className="text-sm text-blue-600 hover:text-blue-800"
          >
            Clear Filters
          </button>
          
          <button
            onClick={handleExportCSV}
            className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700"
          >
            Export CSV
          </button>
        </div>
      </div>

      {/* Audit Logs Table */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Timestamp</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">User</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Action</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Module</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Description</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">IP Address</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {loading ? (
                <tr>
                  <td colSpan={7} className="px-4 py-8 text-center text-gray-500">
                    Loading audit logs...
                  </td>
                </tr>
              ) : logs.length === 0 ? (
                <tr>
                  <td colSpan={7} className="px-4 py-8 text-center text-gray-500">
                    No audit logs found
                  </td>
                </tr>
              ) : (
                logs.map((log) => (
                  <tr key={log.id} className="hover:bg-gray-50">
                    <td className="px-4 py-3 text-sm text-gray-900">
                      {new Date(log.timestamp).toLocaleString()}
                    </td>
                    <td className="px-4 py-3 text-sm">
                      <div className="font-medium text-gray-900">{log.username}</div>
                      <div className="text-xs text-gray-500">{log.user_role}</div>
                    </td>
                    <td className="px-4 py-3 text-sm">
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${getActionBadgeColor(log.action)}`}>
                        {log.action}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-900">{log.module}</td>
                    <td className="px-4 py-3 text-sm text-gray-700 max-w-md truncate">{log.description}</td>
                    <td className="px-4 py-3 text-sm text-gray-500">{log.ip_address || 'N/A'}</td>
                    <td className="px-4 py-3 text-sm">
                      <button
                        onClick={() => setSelectedLog(log)}
                        className="text-blue-600 hover:text-blue-800"
                      >
                        Details
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
        
        {/* Pagination */}
        <div className="bg-gray-50 px-4 py-3 flex items-center justify-between border-t border-gray-200">
          <div className="text-sm text-gray-700">
            Page {page} of {totalPages}
          </div>
          <div className="flex space-x-2">
            <button
              onClick={() => setPage(Math.max(1, page - 1))}
              disabled={page === 1}
              className="px-3 py-1 border border-gray-300 rounded text-sm disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-100"
            >
              Previous
            </button>
            <button
              onClick={() => setPage(Math.min(totalPages, page + 1))}
              disabled={page === totalPages}
              className="px-3 py-1 border border-gray-300 rounded text-sm disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-100"
            >
              Next
            </button>
          </div>
        </div>
      </div>

      {/* Detail Modal */}
      {selectedLog && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-3xl w-full max-h-[90vh] overflow-y-auto m-4">
            <div className="p-6">
              <div className="flex justify-between items-start mb-4">
                <h2 className="text-xl font-bold text-gray-900">Audit Log Details</h2>
                <button
                  onClick={() => setSelectedLog(null)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
              
              <div className="space-y-3">
                <div>
                  <span className="text-sm font-medium text-gray-500">Timestamp:</span>
                  <p className="text-sm text-gray-900">{new Date(selectedLog.timestamp).toLocaleString()}</p>
                </div>
                
                <div>
                  <span className="text-sm font-medium text-gray-500">User:</span>
                  <p className="text-sm text-gray-900">{selectedLog.username} ({selectedLog.user_role})</p>
                </div>
                
                <div>
                  <span className="text-sm font-medium text-gray-500">IP Address:</span>
                  <p className="text-sm text-gray-900">{selectedLog.ip_address || 'N/A'}</p>
                </div>
                
                <div>
                  <span className="text-sm font-medium text-gray-500">Action:</span>
                  <p className="text-sm text-gray-900">{selectedLog.action}</p>
                </div>
                
                <div>
                  <span className="text-sm font-medium text-gray-500">Module:</span>
                  <p className="text-sm text-gray-900">{selectedLog.module}</p>
                </div>
                
                {selectedLog.entity_type && (
                  <div>
                    <span className="text-sm font-medium text-gray-500">Entity:</span>
                    <p className="text-sm text-gray-900">{selectedLog.entity_type} #{selectedLog.entity_id}</p>
                  </div>
                )}
                
                <div>
                  <span className="text-sm font-medium text-gray-500">Description:</span>
                  <p className="text-sm text-gray-900">{selectedLog.description}</p>
                </div>
                
                {selectedLog.old_values && (
                  <div>
                    <span className="text-sm font-medium text-gray-500">Old Values:</span>
                    <pre className="mt-1 text-xs bg-gray-50 p-2 rounded overflow-x-auto">
                      {JSON.stringify(selectedLog.old_values, null, 2)}
                    </pre>
                  </div>
                )}
                
                {selectedLog.new_values && (
                  <div>
                    <span className="text-sm font-medium text-gray-500">New Values:</span>
                    <pre className="mt-1 text-xs bg-gray-50 p-2 rounded overflow-x-auto">
                      {JSON.stringify(selectedLog.new_values, null, 2)}
                    </pre>
                  </div>
                )}
                
                {selectedLog.request_method && (
                  <div>
                    <span className="text-sm font-medium text-gray-500">Request:</span>
                    <p className="text-sm text-gray-900">{selectedLog.request_method} {selectedLog.request_path}</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
