-- Migration 010: Add 'Bahan Penolong' to product_type enum
-- Bahan Penolong = Auxiliary / Indirect Material (e.g. chemicals, adhesives, packaging consumables)
-- Run: psql -U postgres -d erp_quty_karunia -f sql_migrations/010_add_bahan_penolong_type.sql

ALTER TYPE product_type ADD VALUE IF NOT EXISTS 'Bahan Penolong';

-- Verify
SELECT unnest(enum_range(NULL::product_type)) AS product_type_values;
