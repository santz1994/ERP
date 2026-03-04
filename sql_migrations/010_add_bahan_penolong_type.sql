-- Migration 010: Add 'BAHAN_PENOLONG' to producttype enum
-- Bahan Penolong = Auxiliary / Indirect Material (e.g. chemicals, adhesives, packaging consumables)
-- DB enum name: producttype (consolidated, no underscore)
-- Run: psql -U postgres -d erp_quty_karunia -f sql_migrations/010_add_bahan_penolong_type.sql

ALTER TYPE producttype ADD VALUE IF NOT EXISTS 'BAHAN_PENOLONG';

-- Verify
SELECT unnest(enum_range(NULL::producttype)) AS producttype_values;
