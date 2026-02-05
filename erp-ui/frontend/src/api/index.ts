import { apiClient } from './client'
import {
  LoginFormData,
  UserFormData,
  MaterialFormData,
  SupplierFormData,
  ArticleFormData,
  BOMFormData,
  POFormData,
  MOFormData,
  SPKFormData,
  ProductionInputFormData,
  QCCheckpointFormData,
  ReworkInputFormData,
} from '@/lib/schemas'

/**
 * Comprehensive API Service for ERP Quty Karunia
 * All API endpoints organized by module
 */

// ============================================================================
// AUTHENTICATION & USER MANAGEMENT
// ============================================================================

export const authApi = {
  login: (data: LoginFormData) =>
    apiClient.post('/auth/login', data),
  
  logout: () =>
    apiClient.post('/auth/logout'),
  
  getCurrentUser: () =>
    apiClient.get('/auth/me'),
  
  changePassword: (data: { current_password: string; new_password: string }) =>
    apiClient.post('/auth/change-password', data),
  
  refreshToken: () =>
    apiClient.post('/auth/refresh'),
}

export const userApi = {
  getUsers: (params?: { role?: string; department?: string; is_active?: boolean }) =>
    apiClient.get('/users', { params }),
  
  getUserById: (id: number) =>
    apiClient.get(`/users/${id}`),
  
  createUser: (data: UserFormData) =>
    apiClient.post('/users', data),
  
  updateUser: (id: number, data: Partial<UserFormData>) =>
    apiClient.put(`/users/${id}`, data),
  
  deleteUser: (id: number) =>
    apiClient.delete(`/users/${id}`),
  
  getUserActivity: (userId: number, params?: { start_date?: string; end_date?: string }) =>
    apiClient.get(`/users/${userId}/activity`, { params }),
}

// ============================================================================
// DASHBOARD & KPI
// ============================================================================

export const dashboardApi = {
  getKPIs: (role?: string) =>
    apiClient.get('/dashboard/kpi', { params: { role } }),
  
  getProductionChart: (params?: { start_date?: string; end_date?: string; department?: string }) =>
    apiClient.get('/dashboard/production-chart', { params }),
  
  getMaterialAlerts: () =>
    apiClient.get('/dashboard/material-alerts'),
  
  getSPKStatus: () =>
    apiClient.get('/dashboard/spk-status'),
  
  getRealtimeUpdates: () =>
    apiClient.get('/dashboard/realtime'),
}

// ============================================================================
// MASTERDATA MANAGEMENT
// ============================================================================

export const materialApi = {
  getMaterials: (params?: { type?: string; search?: string; page?: number; limit?: number }) =>
    apiClient.get('/materials', { params }),
  
  getMaterialById: (id: number) =>
    apiClient.get(`/materials/${id}`),
  
  createMaterial: (data: MaterialFormData) =>
    apiClient.post('/materials', data),
  
  updateMaterial: (id: number, data: Partial<MaterialFormData>) =>
    apiClient.put(`/materials/${id}`, data),
  
  deleteMaterial: (id: number) =>
    apiClient.delete(`/materials/${id}`),
  
  importMaterials: (file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    return apiClient.post('/materials/import', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },
  
  exportMaterials: () =>
    apiClient.get('/materials/export', { responseType: 'blob' }),
}

export const supplierApi = {
  getSuppliers: (params?: { type?: string; search?: string }) =>
    apiClient.get('/suppliers', { params }),
  
  getSupplierById: (id: number) =>
    apiClient.get(`/suppliers/${id}`),
  
  createSupplier: (data: SupplierFormData) =>
    apiClient.post('/suppliers', data),
  
  updateSupplier: (id: number, data: Partial<SupplierFormData>) =>
    apiClient.put(`/suppliers/${id}`, data),
  
  deleteSupplier: (id: number) =>
    apiClient.delete(`/suppliers/${id}`),
  
  getSupplierPerformance: (id: number) =>
    apiClient.get(`/suppliers/${id}/performance`),
}

export const articleApi = {
  getArticles: (params?: { buyer?: string; search?: string; is_active?: boolean }) =>
    apiClient.get('/articles', { params }),
  
  getArticleById: (id: number) =>
    apiClient.get(`/articles/${id}`),
  
  createArticle: (data: ArticleFormData) =>
    apiClient.post('/articles', data),
  
  updateArticle: (id: number, data: Partial<ArticleFormData>) =>
    apiClient.put(`/articles/${id}`, data),
  
  deleteArticle: (id: number) =>
    apiClient.delete(`/articles/${id}`),
}

export const bomApi = {
  getBOMs: (params?: { article_code?: string; department?: string; bom_type?: string }) =>
    apiClient.get('/bom', { params }),
  
  getBOMById: (id: number) =>
    apiClient.get(`/bom/${id}`),
  
  createBOM: (data: BOMFormData) =>
    apiClient.post('/bom', data),
  
  updateBOM: (id: number, data: Partial<BOMFormData>) =>
    apiClient.put(`/bom/${id}`, data),
  
  deleteBOM: (id: number) =>
    apiClient.delete(`/bom/${id}`),
  
  // BOM Explosion for PO Auto mode
  bomExplosion: (article_code: string, qty: number) =>
    apiClient.post('/bom/explosion', { article_code, qty }),
  
  // BOM Cascade Validation
  validateBOMCascade: (article_code: string) =>
    apiClient.get(`/bom/validate-cascade/${article_code}`),
}

// ============================================================================
// PURCHASING MODULE
// ============================================================================

export const purchasingApi = {
  // Purchase Orders
  getPOs: (params?: { 
    po_type?: string
    status?: string
    supplier_id?: number
    search?: string
    page?: number
    limit?: number
  }) =>
    apiClient.get('/purchasing/po', { params }),
  
  getPOById: (id: number) =>
    apiClient.get(`/purchasing/po/${id}`),
  
  createPO: (data: POFormData) =>
    apiClient.post('/purchasing/po', data),
  
  updatePO: (id: number, data: Partial<POFormData>) =>
    apiClient.put(`/purchasing/po/${id}`, data),
  
  deletePO: (id: number) =>
    apiClient.delete(`/purchasing/po/${id}`),
  
  // PO Status management
  sendPO: (id: number) =>
    apiClient.post(`/purchasing/po/${id}/send`),
  
  receivePO: (id: number, materials: Array<{ material_code: string; qty: number }>) =>
    apiClient.post(`/purchasing/po/${id}/receive`, { materials }),
  
  // PO Tracking
  getPOTracking: (id: number) =>
    apiClient.get(`/purchasing/po/${id}/tracking`),
  
  // Export PO
  exportPO: (id: number) =>
    apiClient.get(`/purchasing/po/${id}/export`, { responseType: 'blob' }),
}

// ============================================================================
// PPIC MODULE
// ============================================================================

export const ppicApi = {
  // Manufacturing Orders
  getMOs: (params?: {
    status?: string
    article_code?: string
    week_number?: string
    search?: string
  }) =>
    apiClient.get('/ppic/mo', { params }),
  
  getMOById: (id: number) =>
    apiClient.get(`/ppic/mo/${id}`),
  
  createMO: (data: MOFormData) =>
    apiClient.post('/ppic/mo', data),
  
  updateMO: (id: number, data: Partial<MOFormData>) =>
    apiClient.put(`/ppic/mo/${id}`, data),
  
  deleteMO: (id: number) =>
    apiClient.delete(`/ppic/mo/${id}`),
  
  // MO Status transitions
  releasePartial: (id: number) =>
    apiClient.post(`/ppic/mo/${id}/release-partial`),
  
  releaseFull: (id: number) =>
    apiClient.post(`/ppic/mo/${id}/release-full`),
  
  completeMO: (id: number) =>
    apiClient.post(`/ppic/mo/${id}/complete`),
  
  // SPK Management
  getSPKs: (params?: {
    mo_id?: number
    department?: string
    status?: string
    date_range?: string
  }) =>
    apiClient.get('/ppic/spk', { params }),
  
  getSPKById: (id: number) =>
    apiClient.get(`/ppic/spk/${id}`),
  
  createSPK: (data: SPKFormData) =>
    apiClient.post('/ppic/spk', data),
  
  updateSPK: (id: number, data: Partial<SPKFormData>) =>
    apiClient.put(`/ppic/spk/${id}`, data),
  
  deleteSPK: (id: number) =>
    apiClient.delete(`/ppic/spk/${id}`),
  
  // Auto-generate SPK from MO
  autoGenerateSPK: (mo_id: number) =>
    apiClient.post(`/ppic/mo/${mo_id}/generate-spk`),
  
  // Material Allocation
  getMaterialAllocation: (mo_id: number) =>
    apiClient.get(`/ppic/material-allocation/${mo_id}`),
  
  reserveMaterials: (spk_id: number) =>
    apiClient.post(`/ppic/material-allocation/reserve`, { spk_id }),
  
  releaseMaterials: (spk_id: number) =>
    apiClient.post(`/ppic/material-allocation/release`, { spk_id }),
}

// ============================================================================
// PRODUCTION MODULE
// ============================================================================

export const productionApi = {
  // Daily production input
  inputProduction: (data: ProductionInputFormData) =>
    apiClient.post('/production/input', data),
  
  getProductionHistory: (spk_id: number) =>
    apiClient.get(`/production/history/${spk_id}`),
  
  // Calendar view data
  getProductionCalendar: (params: { 
    department: string
    month: string // YYYY-MM
  }) =>
    apiClient.get('/production/calendar', { params }),
  
  // Real-time WIP Dashboard
  getWIPDashboard: (department?: string) =>
    apiClient.get('/production/wip-dashboard', { params: { department } }),
  
  // Department-specific endpoints
  getCuttingSPKs: () =>
    apiClient.get('/production/cutting/spk'),
  
  getEmbroiderySPKs: () =>
    apiClient.get('/production/embroidery/spk'),
  
  getSewingSPKs: () =>
    apiClient.get('/production/sewing/spk'),
  
  getFinishingSPKs: (stage?: 'STAGE1' | 'STAGE2') =>
    apiClient.get('/production/finishing/spk', { params: { stage } }),
  
  getPackingSPKs: () =>
    apiClient.get('/production/packing/spk'),
  
  // Subcontractor management (Embroidery)
  sendToSubcon: (data: { spk_id: number; subcon_id: number; qty: number }) =>
    apiClient.post('/production/embroidery/send-subcon', data),
  
  receiveFromSubcon: (data: { spk_id: number; subcon_id: number; qty: number }) =>
    apiClient.post('/production/embroidery/receive-subcon', data),
  
  // Barcode generation (Packing)
  generateBarcode: (spk_id: number, carton_id: number) =>
    apiClient.post('/production/packing/generate-barcode', { spk_id, carton_id }),
}

// ============================================================================
// WAREHOUSE & INVENTORY MODULE
// ============================================================================

export const warehouseApi = {
  // Material Stock
  getMaterialStock: (params?: { 
    material_code?: string
    material_type?: string
    low_stock?: boolean
  }) =>
    apiClient.get('/warehouse/material/stock', { params }),
  
  // Material Receipt (GRN)
  materialReceipt: (data: any) =>
    apiClient.post('/warehouse/material/receipt', data),
  
  // Material Issue to Production
  materialIssue: (data: any) =>
    apiClient.post('/warehouse/material/issue', data),
  
  // Stock Adjustment
  stockAdjustment: (data: any) =>
    apiClient.post('/warehouse/material/adjust', data),
  
  // Finishing Warehouse (2-stage)
  getFinishingStock: (stage?: 'SKIN' | 'STUFFED' | 'FINISHED') =>
    apiClient.get('/warehouse/finishing/stock', { params: { stage } }),
  
  transferFinishing: (data: { from_stage: string; to_stage: string; qty: number }) =>
    apiClient.post('/warehouse/finishing/transfer', data),
  
  // Finished Goods
  getFGStock: (params?: { article_code?: string; week?: string; destination?: string }) =>
    apiClient.get('/warehouse/fg/stock', { params }),
  
  fgReceipt: (data: any) =>
    apiClient.post('/warehouse/fg/receipt', data),
  
  fgShipment: (data: { do_number: string; cartons: Array<{ barcode: string; qty: number }> }) =>
    apiClient.post('/warehouse/fg/shipment', data),
  
  // Stock Opname
  createStockOpname: (data: { schedule_date: string; warehouse_type: string }) =>
    apiClient.post('/warehouse/opname', data),
  
  inputStockOpname: (opname_id: number, data: Array<{ material_code: string; physical_count: number }>) =>
    apiClient.post(`/warehouse/opname/${opname_id}/input`, { materials: data }),
  
  getOpnameVariance: (opname_id: number) =>
    apiClient.get(`/warehouse/opname/${opname_id}/variance`),
}

// ============================================================================
// QUALITY CONTROL & REWORK MODULE
// ============================================================================

export const qcApi = {
  // QC Checkpoints
  inputQCCheckpoint: (data: QCCheckpointFormData) =>
    apiClient.post('/qc/checkpoint', data),
  
  getQCHistory: (spk_id: number) =>
    apiClient.get(`/qc/history/${spk_id}`),
  
  // Defect Analysis
  getDefectAnalysis: (params?: { 
    start_date?: string
    end_date?: string
    department?: string
    article_code?: string
  }) =>
    apiClient.get('/qc/defect-analysis', { params }),
  
  // First Pass Yield
  getFPYReport: (params?: { department?: string; date_range?: string }) =>
    apiClient.get('/qc/fpy-report', { params }),
}

export const reworkApi = {
  // Rework Orders
  getReworkOrders: (params?: { 
    status?: string
    department?: string
    priority?: string
  }) =>
    apiClient.get('/rework/orders', { params }),
  
  getReworkOrderById: (id: number) =>
    apiClient.get(`/rework/orders/${id}`),
  
  // Rework Operations
  startRework: (order_id: number) =>
    apiClient.post(`/rework/orders/${order_id}/start`),
  
  completeRework: (order_id: number, data: ReworkInputFormData) =>
    apiClient.post(`/rework/orders/${order_id}/complete`, data),
  
  scrapDefect: (order_id: number, reason: string) =>
    apiClient.post(`/rework/orders/${order_id}/scrap`, { reason }),
  
  // Rework Dashboard
  getReworkDashboard: () =>
    apiClient.get('/rework/dashboard'),
  
  // COPQ (Cost of Poor Quality)
  getCOPQReport: (params?: { start_date?: string; end_date?: string }) =>
    apiClient.get('/rework/copq-report', { params }),
  
  // Recovery Rate
  getRecoveryRate: (params?: { department?: string; period?: string }) =>
    apiClient.get('/rework/recovery-rate', { params }),
}

// ============================================================================
// REPORTING MODULE
// ============================================================================

export const reportApi = {
  // Production Reports
  getDailyProductionReport: (date: string, department?: string) =>
    apiClient.get('/reports/production/daily', { params: { date, department } }),
  
  getWeeklyProductionReport: (week: string) =>
    apiClient.get('/reports/production/weekly', { params: { week } }),
  
  getMonthlyProductionReport: (month: string) =>
    apiClient.get('/reports/production/monthly', { params: { month } }),
  
  // Purchasing Reports
  getPOSummary: (params?: { start_date?: string; end_date?: string; po_type?: string }) =>
    apiClient.get('/reports/purchasing/po-summary', { params }),
  
  getDeliveryPerformance: (params?: { supplier_id?: number; date_range?: string }) =>
    apiClient.get('/reports/purchasing/delivery-performance', { params }),
  
  // Inventory Reports
  getStockMovementReport: (params: { start_date: string; end_date: string; material_code?: string }) =>
    apiClient.get('/reports/inventory/stock-movement', { params }),
  
  getMaterialConsumption: (params: { start_date: string; end_date: string; department?: string }) =>
    apiClient.get('/reports/inventory/material-consumption', { params }),
  
  getABCAnalysis: () =>
    apiClient.get('/reports/inventory/abc-analysis'),
  
  // Material Debt Report
  getMaterialDebtReport: () =>
    apiClient.get('/reports/material-debt'),
  
  // Executive Dashboard
  getExecutiveDashboard: (period: string) =>
    apiClient.get('/reports/executive-dashboard', { params: { period } }),
  
  // Export Reports
  exportReport: (report_type: string, params: any) =>
    apiClient.get(`/reports/export/${report_type}`, { 
      params,
      responseType: 'blob'
    }),
}

// ============================================================================
// NOTIFICATION & AUDIT
// ============================================================================

export const notificationApi = {
  getNotifications: (params?: { read?: boolean; type?: string; limit?: number }) =>
    apiClient.get('/notifications', { params }),
  
  markAsRead: (id: number) =>
    apiClient.post(`/notifications/${id}/read`),
  
  markAllAsRead: () =>
    apiClient.post('/notifications/read-all'),
  
  getUnreadCount: () =>
    apiClient.get('/notifications/unread-count'),
}

export const auditApi = {
  getAuditTrail: (params?: {
    user_id?: number
    action?: string
    module?: string
    start_date?: string
    end_date?: string
    page?: number
    limit?: number
  }) =>
    apiClient.get('/audit/trail', { params }),
  
  getLoginHistory: (user_id?: number) =>
    apiClient.get('/audit/login-history', { params: { user_id } }),
  
  getDataChangeHistory: (table_name: string, record_id: number) =>
    apiClient.get(`/audit/data-changes/${table_name}/${record_id}`),
}

// ============================================================================
// SYSTEM CONFIGURATION
// ============================================================================

export const systemApi = {
  getSystemParameters: () =>
    apiClient.get('/system/parameters'),
  
  updateSystemParameter: (key: string, value: any) =>
    apiClient.put(`/system/parameters/${key}`, { value }),
  
  backupDatabase: () =>
    apiClient.post('/system/backup'),
  
  restoreDatabase: (file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    return apiClient.post('/system/restore', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },
  
  getSystemHealth: () =>
    apiClient.get('/system/health'),
}

// Export all APIs
export const api = {
  auth: authApi,
  user: userApi,
  dashboard: dashboardApi,
  material: materialApi,
  supplier: supplierApi,
  article: articleApi,
  bom: bomApi,
  purchasing: purchasingApi,
  ppic: ppicApi,
  production: productionApi,
  warehouse: warehouseApi,
  qc: qcApi,
  rework: reworkApi,
  report: reportApi,
  notification: notificationApi,
  audit: auditApi,
  system: systemApi,
}

// Export apiClient for direct API calls (custom endpoints, legacy code)
// Prefer using the structured 'api' object above for new code
export { apiClient }

export default api
