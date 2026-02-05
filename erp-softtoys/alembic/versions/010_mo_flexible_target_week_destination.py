"""Add flexible target system, week, destination to MO

Revision ID: 010_mo_flexible_target
Revises: 009_dual_mode_po_bom_explosion
Create Date: 2026-01-26

🔥 KEY FEATURES:
1. Flexible Target System:
   - target_quantity: Target pcs to produce
   - buffer_quantity: Buffer pcs (e.g., 50 pcs for QC reserve)
   - production_quantity: Actual production = target + buffer
   - auto_calculate: Boolean to auto-recalc buffer

2. MO PARTIAL/RELEASED Logic:
   - week: Week number (e.g., "W01", "W02-W03")
   - destination: Buyer/destination (e.g., "SHEIN_UK", "NIKE_US")
   - week_destination_locked: Boolean to prevent changes after RELEASED

3. Enhanced Metadata:
   - JSON field for BOM explosion, PO tracking, QC results, etc.

Upgrade Logic:
- PO KAIN approved → MO: DRAFT → PARTIAL
- PO LABEL approved → MO: PARTIAL → RELEASED + lock week/destination
"""

revision = '010_mo_flexible_target'
down_revision = '009_dual_mode_po_bom_explosion'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSON


def upgrade():
    """Add flexible target, week, destination to manufacturing_orders table."""
    
    # Add Flexible Target System fields
    op.add_column('manufacturing_orders', 
        sa.Column('target_quantity', sa.DECIMAL(15, 3), nullable=True,
                  comment='Target pcs to produce (final deliverable qty)')
    )
    op.add_column('manufacturing_orders', 
        sa.Column('buffer_quantity', sa.DECIMAL(15, 3), nullable=True,
                  comment='Buffer pcs for QC/rework (e.g., 50 pcs extra)')
    )
    op.add_column('manufacturing_orders', 
        sa.Column('production_quantity', sa.DECIMAL(15, 3), nullable=True,
                  comment='Actual production qty = target + buffer (auto-calculated)')
    )
    op.add_column('manufacturing_orders', 
        sa.Column('auto_calculate_buffer', sa.Boolean(), nullable=True, default=True,
                  comment='If true, system auto-recalculates buffer based on rules')
    )
    
    # Add Week & Destination fields
    op.add_column('manufacturing_orders', 
        sa.Column('week', sa.String(50), nullable=True,
                  comment='Week number (e.g., "W01", "W02-W03")')
    )
    op.add_column('manufacturing_orders', 
        sa.Column('destination', sa.String(100), nullable=True,
                  comment='Buyer/destination (e.g., "SHEIN_UK", "NIKE_US")')
    )
    op.add_column('manufacturing_orders', 
        sa.Column('week_destination_locked', sa.Boolean(), nullable=True, default=False,
                  comment='Lock week/destination after MO RELEASED (from PO LABEL approval)')
    )
    
    # Add enhanced metadata field (if not already exists)
    # Note: Check if column exists first (might be added in previous migration)
    # For safety, we'll use try-except in production
    # RENAMED to 'extra_metadata' to avoid SQLAlchemy reserved name 'metadata'
    try:
        op.add_column('manufacturing_orders', 
            sa.Column('extra_metadata', JSON, nullable=True,
                      comment='JSON metadata: BOM explosion, PO links, QC results, notes')
        )
    except Exception:
        # Column might already exist from previous migration
        pass
    
    # Add indexes for common queries
    op.create_index('idx_mo_week', 'manufacturing_orders', ['week'])
    op.create_index('idx_mo_destination', 'manufacturing_orders', ['destination'])
    op.create_index('idx_mo_week_dest_locked', 'manufacturing_orders', ['week_destination_locked'])
    
    # Update existing rows with default values
    # Use qty_planned (existing column) as default for target_quantity
    op.execute("""
        UPDATE manufacturing_orders
        SET 
            target_quantity = COALESCE(qty_planned, 0),
            buffer_quantity = 0,
            production_quantity = COALESCE(qty_planned, 0),
            auto_calculate_buffer = true,
            week_destination_locked = false
        WHERE target_quantity IS NULL
    """)
    
    # Make fields NOT NULL after setting defaults
    op.alter_column('manufacturing_orders', 'target_quantity', nullable=False)
    op.alter_column('manufacturing_orders', 'buffer_quantity', nullable=False)
    op.alter_column('manufacturing_orders', 'production_quantity', nullable=False)
    op.alter_column('manufacturing_orders', 'auto_calculate_buffer', nullable=False)
    op.alter_column('manufacturing_orders', 'week_destination_locked', nullable=False)


def downgrade():
    """Revert flexible target, week, destination fields."""
    
    # Drop indexes
    op.drop_index('idx_mo_week_dest_locked', 'manufacturing_orders')
    op.drop_index('idx_mo_destination', 'manufacturing_orders')
    op.drop_index('idx_mo_week', 'manufacturing_orders')
    
    # Drop columns
    op.drop_column('manufacturing_orders', 'week_destination_locked')
    op.drop_column('manufacturing_orders', 'destination')
    op.drop_column('manufacturing_orders', 'week')
    op.drop_column('manufacturing_orders', 'auto_calculate_buffer')
    op.drop_column('manufacturing_orders', 'production_quantity')
    op.drop_column('manufacturing_orders', 'buffer_quantity')
    op.drop_column('manufacturing_orders', 'target_quantity')
    
    # Note: We don't drop extra_metadata column as it might be used by other features
