-- Add missing pallet tracking columns to work_orders table
-- Run this ASAP to fix backend errors

-- Add columns
ALTER TABLE work_orders 
ADD COLUMN IF NOT EXISTS cartons_packed INTEGER DEFAULT 0;

ALTER TABLE work_orders 
ADD COLUMN IF NOT EXISTS pallets_formed INTEGER DEFAULT 0;

ALTER TABLE work_orders 
ADD COLUMN IF NOT EXISTS packing_validated BOOLEAN DEFAULT FALSE;

-- Add comments
COMMENT ON COLUMN work_orders.cartons_packed IS 'Number of cartons packed (must be multiple of article.cartons_per_pallet)';
COMMENT ON COLUMN work_orders.pallets_formed IS 'Number of pallets formed: cartons_packed / article.cartons_per_pallet';
COMMENT ON COLUMN work_orders.packing_validated IS 'TRUE if packing quantities validated (no partial cartons/pallets)';

-- Verify
SELECT column_name, data_type, column_default 
FROM information_schema.columns 
WHERE table_name = 'work_orders' 
  AND column_name IN ('cartons_packed', 'pallets_formed', 'packing_validated');
