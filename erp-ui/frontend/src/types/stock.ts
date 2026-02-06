/**
 * Copyright (c) 2026 PT Quty Karunia - All Rights Reserved
 * File: stock.ts | Date: 2026-02-06
 * Purpose: Shared Stock/Inventory Types (Phase 3 - Code Duplication Elimination)
 * Usage: Import from '@/types/stock' instead of defining inline
 */

/**
 * Stock Item - Warehouse inventory entity
 * Tracks material, WIP, and finished goods quantities
 */
export interface StockItem {
  id: number
  product_id: number
  product_name: string
  product_code: string
  warehouse_id: number
  warehouse_name: string
  location_code: string
  quantity: number
  uom: string
  unit_price?: number
  total_value?: number
  last_movement_date: string
  status: 'Available' | 'Reserved' | 'Blocked' | 'Quarantine'
}

/**
 * Stock Quant - Detailed stock tracking with lot/batch
 */
export interface StockQuant {
  id: number
  product_id: number
  product_name: string
  product_code: string
  warehouse_id: number
  location_id: number
  lot_number?: string
  batch_number?: string
  quantity: number
  reserved_qty: number
  available_qty: number
  uom: string
  manufacture_date?: string
  expiry_date?: string
  status: 'Available' | 'Reserved' | 'Blocked' | 'Quarantine'
  created_at: string
  updated_at: string
}

/**
 * Stock Movement - Inventory transaction record
 */
export interface StockMovement {
  id: number
  product_id: number
  product_name: string
  product_code: string
  movement_type: StockMovementType
  quantity: number
  uom: string
  source_location: string
  destination_location: string
  reference_document?: string
  reference_id?: number
  notes?: string
  performed_by: number
  performed_by_name?: string
  performed_at: string
  status: 'Pending' | 'Completed' | 'Cancelled'
}

/**
 * Stock Movement Type - Transaction categories
 */
export type StockMovementType =
  | 'Purchase Receipt'    // From PO
  | 'Production Input'    // Material consumption
  | 'Production Output'   // WIP/FG production
  | 'Internal Transfer'   // Between warehouses
  | 'Stock Adjustment'    // Inventory correction
  | 'Sales Delivery'      // To customer
  | 'Rework'              // QC reject to rework
  | 'Scrap'               // Write-off

/**
 * Stock Deduction - Material consumption tracking
 */
export interface StockDeduction {
  id: number
  mo_id: number
  wo_id: number
  product_id: number
  product_name: string
  quantity_required: number
  quantity_deducted: number
  quantity_remaining: number
  uom: string
  warehouse_id: number
  deducted_at: string
  deducted_by: number
  notes?: string
}

/**
 * Stock Aging - For aging analysis report
 */
export interface StockAgingItem {
  product_id: number
  product_name: string
  product_code: string
  warehouse_name: string
  quantity: number
  uom: string
  days_in_stock: number
  aging_category: '0-30 days' | '31-60 days' | '61-90 days' | '91-180 days' | '180+ days'
  last_movement_date: string
  unit_price: number
  total_value: number
}

/**
 * Stock Status - For dashboard widgets
 */
export interface StockStatusItem {
  warehouse_name: string
  category: string
  total_items: number
  total_quantity: number
  total_value: number
  low_stock_items: number
  out_of_stock_items: number
}

/**
 * Stock Level Alert - For low stock monitoring
 */
export interface StockLevelAlert {
  product_id: number
  product_name: string
  product_code: string
  current_qty: number
  min_qty: number
  max_qty: number
  reorder_point: number
  uom: string
  warehouse_name: string
  alert_level: 'Critical' | 'Warning' | 'Normal'
  recommended_po_qty?: number
}

/**
 * Stock Movement Day - For dashboard timeline
 */
export interface StockMovementDay {
  date: string
  receipts: number
  issues: number
  transfers: number
  net_movement: number
}

/**
 * Stock Valuation - For inventory valuation report
 */
export interface StockValuation {
  product_id: number
  product_name: string
  product_code: string
  category: string
  quantity: number
  uom: string
  unit_cost: number
  total_cost: number
  valuation_method: 'FIFO' | 'Average' | 'Standard'
  last_purchase_price?: number
  last_purchase_date?: string
}

/**
 * Warehouse - Storage location entity
 */
export interface Warehouse {
  id: number
  warehouse_code: string
  warehouse_name: string
  warehouse_type: 'Raw Material' | 'WIP' | 'Finished Goods' | 'Rejection' | 'Rework' | 'General'
  location_address?: string
  capacity?: number
  current_utilization?: number
  manager_id?: number
  manager_name?: string
  is_active: boolean
  created_at: string
}

/**
 * Warehouse Location - Sub-location within warehouse
 */
export interface WarehouseLocation {
  id: number
  warehouse_id: number
  location_code: string
  location_name: string
  location_type: 'Rack' | 'Bin' | 'Zone' | 'Area'
  parent_location_id?: number
  capacity?: number
  is_active: boolean
}
