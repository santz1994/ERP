-- Migration: Add Daily Production Input Tracking Tables
-- Created: January 26, 2026
-- Purpose: Support daily production input tracking with cumulative progress
-- Tables: spk_daily_production, spk_production_completion, Enhanced SPK columns

-- ============================================================================
-- TABLE 1: spk_daily_production
-- Description: Track daily production input per SPK with cumulative totals
-- ============================================================================
CREATE TABLE IF NOT EXISTS spk_daily_production (
    id SERIAL PRIMARY KEY,
    spk_id INTEGER NOT NULL REFERENCES spks(id) ON DELETE CASCADE,
    production_date DATE NOT NULL,
    input_qty INTEGER DEFAULT 0 CHECK (input_qty >= 0),
    cumulative_qty INTEGER,                    -- Running total of all daily inputs
    input_by_id INTEGER NOT NULL REFERENCES users(id),
    status VARCHAR(50) DEFAULT 'DRAFT',        -- DRAFT, CONFIRMED, COMPLETED
    notes VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- Indexes for performance
    INDEX idx_spk_id (spk_id),
    INDEX idx_production_date (production_date),
    INDEX idx_status (status),
    
    -- Unique constraint: only one entry per SPK per day
    UNIQUE KEY uk_spk_date (spk_id, production_date)
);

-- ============================================================================
-- TABLE 2: spk_production_completion
-- Description: Track SPK completion milestone (when target qty reached)
-- ============================================================================
CREATE TABLE IF NOT EXISTS spk_production_completion (
    id SERIAL PRIMARY KEY,
    spk_id INTEGER NOT NULL REFERENCES spks(id) ON DELETE CASCADE,
    target_qty INTEGER NOT NULL,
    actual_qty INTEGER NOT NULL,
    completed_date DATE NOT NULL,
    confirmed_by_id INTEGER NOT NULL REFERENCES users(id),
    confirmation_notes VARCHAR(255),
    confirmed_at TIMESTAMP NOT NULL,
    is_completed BOOLEAN DEFAULT FALSE,
    
    -- Indexes
    INDEX idx_spk_id (spk_id),
    INDEX idx_completed_date (completed_date),
    INDEX idx_confirmed_by (confirmed_by_id)
);

-- ============================================================================
-- TABLE 3: spk_modifications
-- Description: Audit trail for SPK edits (quantity, dates, etc)
-- ============================================================================
CREATE TABLE IF NOT EXISTS spk_modifications (
    id SERIAL PRIMARY KEY,
    spk_id INTEGER NOT NULL REFERENCES spks(id) ON DELETE CASCADE,
    field_name VARCHAR(50) NOT NULL,           -- 'qty', 'start_date', 'due_date', etc
    old_value VARCHAR(255),
    new_value VARCHAR(255),
    modified_by_id INTEGER NOT NULL REFERENCES users(id),
    modification_reason VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Indexes
    INDEX idx_spk_id (spk_id),
    INDEX idx_modified_at (created_at),
    INDEX idx_modified_by (modified_by_id)
);

-- ============================================================================
-- TABLE 4: material_debt
-- Description: Track negative inventory (material debt) when production starts without materials
-- ============================================================================
CREATE TABLE IF NOT EXISTS material_debt (
    id SERIAL PRIMARY KEY,
    spk_id INTEGER NOT NULL REFERENCES spks(id) ON DELETE CASCADE,
    material_id INTEGER NOT NULL REFERENCES materials(id),
    qty_owed INTEGER NOT NULL CHECK (qty_owed > 0),    -- Amount of material owed
    qty_settled INTEGER DEFAULT 0,                      -- Amount received & settled
    approval_status VARCHAR(50) DEFAULT 'PENDING',     -- PENDING, APPROVED, REJECTED, SETTLED
    created_by_id INTEGER NOT NULL REFERENCES users(id),
    approved_by_id INTEGER,                             -- Who approved the debt
    approved_at TIMESTAMP,
    approval_reason VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- Indexes
    INDEX idx_spk_id (spk_id),
    INDEX idx_material_id (material_id),
    INDEX idx_approval_status (approval_status),
    INDEX idx_created_by (created_by_id)
);

-- ============================================================================
-- TABLE 5: material_debt_settlement
-- Description: Track settlement records when material arrives to pay off debt
-- ============================================================================
CREATE TABLE IF NOT EXISTS material_debt_settlement (
    id SERIAL PRIMARY KEY,
    material_debt_id INTEGER NOT NULL REFERENCES material_debt(id) ON DELETE CASCADE,
    qty_settled INTEGER NOT NULL CHECK (qty_settled > 0),  -- Qty received this settlement
    settlement_date DATE NOT NULL,
    received_by_id INTEGER NOT NULL REFERENCES users(id),
    settled_by_id INTEGER NOT NULL REFERENCES users(id),  -- Who confirmed settlement
    settlement_notes VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Indexes
    INDEX idx_material_debt_id (material_debt_id),
    INDEX idx_settlement_date (settlement_date),
    INDEX idx_received_by (received_by_id),
    INDEX idx_settled_by (settled_by_id)
);

-- ============================================================================
-- TABLE MODIFICATIONS: Enhanced SPK table
-- Description: Add new columns to existing SPK table to support daily production
-- ============================================================================
ALTER TABLE spks ADD COLUMN IF NOT EXISTS (
    original_qty INT DEFAULT 0,                         -- Original target qty
    modified_qty INT,                                    -- Modified target qty (if edited)
    modification_reason VARCHAR(255),                   -- Why was it modified?
    modified_by_id INT REFERENCES users(id),            -- Who modified it
    modified_at TIMESTAMP,                              -- When was it modified?
    allow_negative_inventory BOOLEAN DEFAULT FALSE,     -- Allow production without materials?
    negative_approval_status VARCHAR(50),               -- PENDING, APPROVED, REJECTED for negative inventory
    negative_approved_by_id INT REFERENCES users(id),   -- Who approved negative inventory
    negative_approved_at TIMESTAMP,                     -- When was it approved?
    production_status VARCHAR(50) DEFAULT 'NOT_STARTED',-- NOT_STARTED, IN_PROGRESS, COMPLETED
    completion_date DATE,                               -- When was production completed?
    daily_progress_start_date DATE                      -- When did daily tracking start?
);

-- ============================================================================
-- INDEXES for performance optimization
-- ============================================================================

-- Index for SPK daily tracking queries
CREATE INDEX IF NOT EXISTS idx_spk_production_status ON spks(production_status);
CREATE INDEX IF NOT EXISTS idx_spk_daily_progress_start ON spks(daily_progress_start_date);
CREATE INDEX IF NOT EXISTS idx_spk_allow_negative ON spks(allow_negative_inventory);

-- Index for material_debt queries
CREATE INDEX IF NOT EXISTS idx_material_debt_settlement_status 
    ON material_debt(approval_status) WHERE approval_status != 'SETTLED';

-- ============================================================================
-- AUDIT LOGGING - Add entries for all modifications
-- ============================================================================
-- This will be handled by the application code through AuditLog model
-- All changes to spk_daily_production, spk_modifications, material_debt, etc.
-- will be logged to audit_logs table with:
-- - action: 'DAILY_PRODUCTION_INPUT', 'SPK_MODIFIED', 'MATERIAL_DEBT_APPROVED', etc.
-- - resource_type: 'SPK', 'MATERIAL_DEBT', etc.
-- - user_id: Who made the change
-- - details: JSON with specific details

-- ============================================================================
-- MIGRATION END
-- ============================================================================
