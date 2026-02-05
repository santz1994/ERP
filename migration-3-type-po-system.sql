-- Copyright (c) 2026 PT Quty Karunia / Daniel Rizaldy - All Rights Reserved
-- Migration: Add 3-Type PO System support to purchase_orders table
-- Date: 2026-01-26
-- Session: 44
-- Purpose: Enable Dual Trigger System (Week 1 CRITICAL)

-- 🆕 Add columns for 3-Type PO System
ALTER TABLE purchase_orders 
ADD COLUMN IF NOT EXISTS po_type VARCHAR(20) DEFAULT 'ACCESSORIES' CHECK (po_type IN ('KAIN', 'LABEL', 'ACCESSORIES'));

ALTER TABLE purchase_orders 
ADD COLUMN IF NOT EXISTS linked_mo_id INTEGER REFERENCES manufacturing_orders(id) ON DELETE SET NULL;

-- 🆕 Add columns for financial tracking (if missing)
ALTER TABLE purchase_orders 
ADD COLUMN IF NOT EXISTS total_amount DECIMAL(15, 2) DEFAULT 0.00;

ALTER TABLE purchase_orders 
ADD COLUMN IF NOT EXISTS currency VARCHAR(10) DEFAULT 'IDR';

-- 🆕 Add columns for approval workflow (if missing)
ALTER TABLE purchase_orders 
ADD COLUMN IF NOT EXISTS approved_by INTEGER REFERENCES users(id) ON DELETE SET NULL;

ALTER TABLE purchase_orders 
ADD COLUMN IF NOT EXISTS approved_at TIMESTAMP WITH TIME ZONE;

-- 🆕 Add columns for receiving workflow (if missing)
ALTER TABLE purchase_orders 
ADD COLUMN IF NOT EXISTS received_by INTEGER REFERENCES users(id) ON DELETE SET NULL;

ALTER TABLE purchase_orders 
ADD COLUMN IF NOT EXISTS received_at TIMESTAMP WITH TIME ZONE;

-- 🆕 Add metadata column for flexible data storage (if missing)
ALTER TABLE purchase_orders 
ADD COLUMN IF NOT EXISTS metadata JSONB;

-- 🆕 Add indices for performance
CREATE INDEX IF NOT EXISTS idx_po_type ON purchase_orders(po_type);
CREATE INDEX IF NOT EXISTS idx_po_linked_mo ON purchase_orders(linked_mo_id);
CREATE INDEX IF NOT EXISTS idx_po_status_type ON purchase_orders(status, po_type);

-- 🆕 Add comment for documentation
COMMENT ON COLUMN purchase_orders.po_type IS '3-Type PO System: KAIN (Trigger 1 - Early Start), LABEL (Trigger 2 - Full Release), ACCESSORIES (No Trigger)';
COMMENT ON COLUMN purchase_orders.linked_mo_id IS 'Manufacturing Order linked to this PO (required for KAIN/LABEL types to enable Dual Trigger System)';

-- ✅ Verify migration
SELECT 
    column_name, 
    data_type, 
    is_nullable, 
    column_default
FROM information_schema.columns
WHERE table_name = 'purchase_orders' 
  AND column_name IN ('po_type', 'linked_mo_id', 'total_amount', 'currency', 'approved_by', 'approved_at', 'received_by', 'received_at', 'metadata')
ORDER BY column_name;

-- 📊 Show current PO type distribution (should be all ACCESSORIES initially)
SELECT 
    po_type, 
    COUNT(*) as count,
    CASE 
        WHEN po_type = 'KAIN' THEN '🧵 TRIGGER 1: Early Start'
        WHEN po_type = 'LABEL' THEN '🏷️ TRIGGER 2: Full Release'
        WHEN po_type = 'ACCESSORIES' THEN '📦 No Trigger'
        ELSE 'Unknown'
    END as description
FROM purchase_orders
GROUP BY po_type
ORDER BY po_type;
