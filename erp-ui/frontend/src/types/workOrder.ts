/**
 * Copyright (c) 2026 PT Quty Karunia - All Rights Reserved
 * File: workOrder.ts | Date: 2026-02-06
 * Purpose: Shared Work Order Types (Phase 3 - Code Duplication Elimination)
 * Usage: Import from '@/types/workOrder' instead of defining inline
 */

/**
 * Work Order - Core production tracking entity
 * Used across all production departments (Cutting, Sewing, Finishing, Packing, Embroidery)
 */
export interface WorkOrder {
  id: number
  mo_id: number
  department: string
  status: 'Pending' | 'Running' | 'Finished' | 'Cancelled'
  input_qty: number
  output_qty: number
  reject_qty: number
  start_time: string | null
  end_time: string | null
  created_at?: string
  updated_at?: string
  line_number?: number
  operator_id?: number
  notes?: string
  defect_summary?: Record<string, number>  // For QC defect tracking (Sewing, Finishing)
  cartons_packed?: number  // For Packing
}

/**
 * Work Order with extended properties for specific departments
 */
export interface WorkOrderExtended extends WorkOrder {
  // Sewing-specific
  body_output_qty?: number
  baju_output_qty?: number
  thread_consumption_meter?: number
  
  // Finishing-specific
  stuffed_qty?: number
  closed_qty?: number
  filling_consumption_gram?: number
  
  // Packing-specific
  cartons_packed?: number
  week_assignment?: number
  fg_barcode?: string
  
  // Embroidery-specific
  design_code?: string
  thread_colors_used?: number
}

/**
 * Work Order Status - For filtering and status transitions
 */
export type WorkOrderStatus = 'Pending' | 'Running' | 'Finished' | 'Cancelled'

/**
 * Department-specific stats interfaces
 */
export interface CuttingStats {
  today_output: number
  efficiency_rate: number
  defect_rate: number
  active_wos: number
  completed_today: number
}

export interface SewingStats {
  today_output: number
  inline_qc_rate: number
  defect_rate: number
  active_lines?: number  // Optional - may use active_wos instead
  completed_today: number
  active_wos: number     // Primary property
  body_output?: number
  baju_output?: number
}

export interface FinishingStats {
  today_stuffed: number
  today_closed: number
  active_wos: number
  filling_consumption_kg: number
}

export interface PackingStats {
  today_packed: number
  cartons_completed: number
  active_wos: number
  fg_ready_ship: number
}

export interface EmbroideryStats {
  today_output: number
  designs_completed: number
  active_machines: number
  thread_consumption_meter: number
}
