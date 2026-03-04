-- Migration 008: Expand UOM enum with additional units
-- Run ONCE against PostgreSQL. Each ADD VALUE is idempotent (IF NOT EXISTS).
-- Date: 2026-03-04
--
-- NOTE: PostgreSQL native enum stores the Python enum MEMBER NAMES (uppercase).
-- The human-readable labels ('Ctn', 'Meter') come from the Python UOM.value.
-- PostgreSQL requires enum values to be added outside any table DML transaction.

ALTER TYPE uom ADD VALUE IF NOT EXISTS 'CTN';    -- UOM.CTN   → .value 'Ctn'  (Carton / karton)
ALTER TYPE uom ADD VALUE IF NOT EXISTS 'BOX';    -- UOM.BOX   → .value 'Box'  (Box / kotak)
ALTER TYPE uom ADD VALUE IF NOT EXISTS 'CONE';   -- UOM.CONE  → .value 'Cone' (Thread cone)
ALTER TYPE uom ADD VALUE IF NOT EXISTS 'PACK';   -- UOM.PACK  → .value 'Pack' (Pack / paket)
ALTER TYPE uom ADD VALUE IF NOT EXISTS 'LITER';  -- UOM.LITER → .value 'Liter'(Liquid / lem)
ALTER TYPE uom ADD VALUE IF NOT EXISTS 'SET';    -- UOM.SET   → .value 'Set'  (Set)
ALTER TYPE uom ADD VALUE IF NOT EXISTS 'SHEET';  -- UOM.SHEET → .value 'Sheet'(Sheet / lembar)
ALTER TYPE uom ADD VALUE IF NOT EXISTS 'LUSIN';  -- UOM.LUSIN → .value 'Lusin'(Dozen Indonesian)
ALTER TYPE uom ADD VALUE IF NOT EXISTS 'BALL';   -- UOM.BALL  → .value 'Ball' (Ball of thread)
