// Auth Types
export interface User {
  id: number
  username: string
  email: string
  full_name: string
  role: UserRole
  department?: string
  is_active: boolean
  is_verified: boolean
  created_at: string
}

export enum UserRole {
  ADMIN = 'Admin',
  PPIC = 'PPIC',
  OPERATOR_CUTTING = 'Operator_Cutting',
  OPERATOR_SEWING = 'Operator_Sewing',
  OPERATOR_FINISHING = 'Operator_Finishing',
  OPERATOR_PACKING = 'Operator_Packing',
  SPV_CUTTING = 'SPV_Cutting',
  SPV_SEWING = 'SPV_Sewing',
  SPV_FINISHING = 'SPV_Finishing',
  QC_INSPECTOR = 'QC_Inspector',
  WAREHOUSE_ADMIN = 'Warehouse_Admin',
}

export interface AuthResponse {
  access_token: string
  token_type: string
  user: User
}

// Manufacturing Types
export interface ManufacturingOrder {
  id: number
  so_line_id: number
  product_id: number
  qty_planned: number
  qty_produced: number
  routing_type: string
  batch_number: string
  state: 'Draft' | 'In Progress' | 'Done' | 'Cancel'
  created_at: string
}

export interface WorkOrder {
  id: number
  mo_id: number
  department: string
  status: 'Pending' | 'Running' | 'Finished'
  input_qty: number
  output_qty: number
  reject_qty: number
  start_time?: string
  end_time?: string
}

export interface Product {
  id: number
  code: string
  name: string
  type: 'Raw Material' | 'WIP' | 'Finish Good'
  uom: string
  category_id: number
  min_stock: number
}

export interface TransferLog {
  id: number
  from_dept: string
  to_dept: string
  article_code: string
  qty_sent: number
  qty_received: number
  is_line_clear: boolean
  timestamp_start: string
  timestamp_end?: string
}

// Quality Types
export interface QCLabTest {
  id: number
  batch_number: string
  test_type: 'Drop Test' | 'Stability 10' | 'Stability 27' | 'Seam Strength'
  test_result: 'Pass' | 'Fail'
  measured_value?: number
  measured_unit?: string
  inspector_id: number
  created_at: string
}

export interface QCInspection {
  id: number
  work_order_id: number
  type: 'Incoming' | 'Inline Sewing' | 'Final Metal Detector'
  status: 'Pass' | 'Fail'
  defect_reason?: string
  inspected_by: number
  created_at: string
}

// Stock/Warehouse Types
export interface StockQuant {
  id: number
  product_id: number
  location_id: number
  qty_available: number
  qty_reserved: number
}

export interface StockLot {
  id: number
  product_id: number
  lot_number: string
  qty: number
  received_date: string
  expiry_date?: string
}
