/**
 * Copyright (c) 2026 PT Quty Karunia - All Rights Reserved
 * File: manufacturingOrder.ts | Date: 2026-02-06
 * Purpose: Shared Manufacturing Order Types (Phase 3 - Code Duplication Elimination)
 * Usage: Import from '@/types/manufacturingOrder' instead of defining inline
 */

/**
 * Manufacturing Order (MO) - Master production document
 * Created by PPIC based on PO requirements
 */
export interface ManufacturingOrder {
  id: number
  mo_number: string
  po_id: number
  po_number?: string
  product_id: number
  product_name?: string
  product_code?: string
  quantity: number
  target_date: string
  status: MOStatus
  priority: 'Low' | 'Medium' | 'High' | 'Urgent'
  week_assignment: number
  notes?: string
  created_at: string
  updated_at: string
  created_by?: number
  approved_by?: number
  approved_at?: string
}

/**
 * MO Status - Lifecycle stages
 */
export type MOStatus = 
  | 'Draft'           // Initial creation
  | 'Confirmed'       // Approved by PPIC
  | 'In Production'   // WOs started
  | 'Completed'       // All WOs finished
  | 'Cancelled'       // Cancelled before completion

/**
 * MO Detail - Expanded view with related data
 */
export interface MODetail extends ManufacturingOrder {
  // Related entities
  work_orders: WorkOrderSummary[]
  bom_items: BOMItem[]
  stock_allocations: StockAllocation[]
  
  // Progress tracking
  total_wos: number
  completed_wos: number
  pending_wos: number
  progress_percentage: number
  
  // Material tracking
  total_material_required: number
  total_material_allocated: number
  material_shortage: number
  
  // Production tracking
  total_output: number
  total_reject: number
  efficiency_rate: number
}

/**
 * Work Order Summary (for MO Detail view)
 */
export interface WorkOrderSummary {
  id: number
  department: string
  status: string
  input_qty: number
  output_qty: number
  reject_qty: number
  start_time: string | null
  end_time: string | null
}

/**
 * BOM Item - Bill of Materials line item
 */
export interface BOMItem {
  id: number
  product_id: number
  material_id: number
  material_name: string
  material_code: string
  quantity_per_unit: number
  uom: string
  notes?: string
}

/**
 * Stock Allocation - Material reserved for MO
 */
export interface StockAllocation {
  id: number
  mo_id: number
  material_id: number
  material_name: string
  allocated_qty: number
  consumed_qty: number
  remaining_qty: number
  warehouse_location: string
  allocated_at: string
}

/**
 * MO Filter - For list page filtering
 */
export interface MOFilter {
  status?: MOStatus[]
  priority?: string[]
  week_assignment?: number[]
  product_id?: number
  date_from?: string
  date_to?: string
  search?: string
}

/**
 * MO Form Data - For create/edit forms
 */
export interface MOFormData {
  po_id: number
  product_id: number
  quantity: number
  target_date: string
  priority: 'Low' | 'Medium' | 'High' | 'Urgent'
  week_assignment: number
  notes?: string
}

/**
 * MO Status Count - For dashboard widgets
 */
export interface MOStatusCount {
  draft: number
  confirmed: number
  in_production: number
  completed: number
  cancelled: number
  total: number
}

/**
 * MO Aggregate Data - For aggregate view
 */
export interface MOAggregateData {
  week_number: number
  total_mos: number
  total_quantity: number
  completed_quantity: number
  pending_quantity: number
  progress_percentage: number
  products: MOProductSummary[]
}

/**
 * MO Product Summary - For aggregate view product breakdown
 */
export interface MOProductSummary {
  product_id: number
  product_name: string
  product_code: string
  total_quantity: number
  completed_quantity: number
  pending_mos: number
}
