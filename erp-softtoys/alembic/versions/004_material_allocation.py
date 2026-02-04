"""
Add SPK Material Allocation table - Week 4 Implementation

Revision ID: 004_material_allocation
Revises: 003_wip_routing
Create Date: 2026-02-04

Purpose:
- Track material allocation per Work Order
- Enable soft reservation and hard consumption
- Support material debt system
- FIFO stock tracking integration
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '004_material_allocation'
down_revision = '003_wip_routing'
branch_labels = None
depends_on = None


def upgrade():
    """Upgrade database schema"""
    
    # ========================================================================
    # 1. Create spk_material_allocations table
    # ========================================================================
    op.create_table(
        'spk_material_allocations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('wo_id', sa.Integer(), nullable=False, comment='Work Order ID'),
        sa.Column('material_id', sa.Integer(), nullable=False, comment='Material Product ID'),
        sa.Column('qty_allocated', sa.DECIMAL(precision=12, scale=3), nullable=False, comment='Quantity allocated (soft reservation)'),
        sa.Column('qty_consumed', sa.DECIMAL(precision=12, scale=3), nullable=False, default=0, comment='Quantity actually consumed'),
        sa.Column('uom_id', sa.Integer(), nullable=True, comment='Unit of Measure'),
        sa.Column('is_reserved', sa.Boolean(), nullable=False, default=True, comment='Is material reserved?'),
        sa.Column('is_consumed', sa.Boolean(), nullable=False, default=False, comment='Is material consumed?'),
        sa.Column('allocated_at', sa.DateTime(), nullable=True, comment='When allocated'),
        sa.Column('consumed_at', sa.DateTime(), nullable=True, comment='When consumed'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=True, onupdate=sa.text('CURRENT_TIMESTAMP')),
        
        # Primary Key
        sa.PrimaryKeyConstraint('id'),
        
        # Foreign Keys
        sa.ForeignKeyConstraint(['wo_id'], ['work_orders.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['material_id'], ['products.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['uom_id'], ['uoms.id'], ondelete='SET NULL'),
        
        # Indexes for performance
        sa.Index('idx_spk_mat_alloc_wo', 'wo_id'),
        sa.Index('idx_spk_mat_alloc_material', 'material_id'),
        sa.Index('idx_spk_mat_alloc_reserved', 'is_reserved'),
        sa.Index('idx_spk_mat_alloc_consumed', 'is_consumed'),
        
        comment='Material allocation tracking per Work Order'
    )
    
    # ========================================================================
    # 2. Add material_debt_logs table (if not exists)
    # ========================================================================
    # This table tracks negative inventory approvals
    op.create_table(
        'material_debt_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('wo_id', sa.Integer(), nullable=False, comment='Work Order with debt'),
        sa.Column('material_id', sa.Integer(), nullable=False, comment='Material in debt'),
        sa.Column('debt_qty', sa.DECIMAL(precision=12, scale=3), nullable=False, comment='Debt quantity'),
        sa.Column('reason', sa.String(500), nullable=True, comment='Reason for debt'),
        sa.Column('status', sa.String(50), nullable=False, default='PENDING', comment='PENDING/APPROVED/REJECTED'),
        sa.Column('requested_by_id', sa.Integer(), nullable=False, comment='Who requested'),
        sa.Column('approved_by_id', sa.Integer(), nullable=True, comment='Who approved'),
        sa.Column('requested_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('approved_at', sa.DateTime(), nullable=True),
        sa.Column('resolved_at', sa.DateTime(), nullable=True, comment='When debt was cleared'),
        
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['wo_id'], ['work_orders.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['material_id'], ['products.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['requested_by_id'], ['users.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['approved_by_id'], ['users.id'], ondelete='SET NULL'),
        
        sa.Index('idx_mat_debt_wo', 'wo_id'),
        sa.Index('idx_mat_debt_material', 'material_id'),
        sa.Index('idx_mat_debt_status', 'status'),
        
        comment='Material debt (negative inventory) tracking'
    )
    
    # ========================================================================
    # 3. Add columns to stock_quants for better tracking
    # ========================================================================
    op.add_column('stock_quants', 
        sa.Column('reserved_qty', sa.DECIMAL(precision=12, scale=3), nullable=False, default=0, 
                  comment='Quantity reserved for WOs (soft reservation)')
    )
    
    op.add_column('stock_quants',
        sa.Column('available_qty', sa.DECIMAL(precision=12, scale=3), nullable=True,
                  comment='Available = quantity - reserved_qty (computed)')
    )
    
    # ========================================================================
    # 4. Add columns to work_orders for material status
    # ========================================================================
    op.add_column('work_orders',
        sa.Column('materials_allocated', sa.Boolean(), nullable=False, default=False,
                  comment='Are materials allocated for this WO?')
    )
    
    op.add_column('work_orders',
        sa.Column('materials_consumed', sa.Boolean(), nullable=False, default=False,
                  comment='Are materials fully consumed?')
    )
    
    op.add_column('work_orders',
        sa.Column('has_material_shortage', sa.Boolean(), nullable=False, default=False,
                  comment='Does this WO have material shortage?')
    )
    
    op.add_column('work_orders',
        sa.Column('shortage_alert_sent', sa.Boolean(), nullable=False, default=False,
                  comment='Has shortage alert been sent?')
    )
    
    # ========================================================================
    # 5. Create material_shortage_alerts table
    # ========================================================================
    op.create_table(
        'material_shortage_alerts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('wo_id', sa.Integer(), nullable=False),
        sa.Column('material_id', sa.Integer(), nullable=False),
        sa.Column('required_qty', sa.DECIMAL(precision=12, scale=3), nullable=False),
        sa.Column('available_qty', sa.DECIMAL(precision=12, scale=3), nullable=False),
        sa.Column('shortage_qty', sa.DECIMAL(precision=12, scale=3), nullable=False),
        sa.Column('severity', sa.String(20), nullable=False, comment='CRITICAL/HIGH/MEDIUM/LOW'),
        sa.Column('status', sa.String(20), nullable=False, default='OPEN', comment='OPEN/RESOLVED/IGNORED'),
        sa.Column('alert_sent_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('resolved_at', sa.DateTime(), nullable=True),
        sa.Column('resolved_by_id', sa.Integer(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['wo_id'], ['work_orders.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['material_id'], ['products.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['resolved_by_id'], ['users.id'], ondelete='SET NULL'),
        
        sa.Index('idx_shortage_alert_wo', 'wo_id'),
        sa.Index('idx_shortage_alert_material', 'material_id'),
        sa.Index('idx_shortage_alert_severity', 'severity'),
        sa.Index('idx_shortage_alert_status', 'status'),
        
        comment='Material shortage alert tracking'
    )
    
    print("✅ Migration 004: Material allocation tables created successfully!")


def downgrade():
    """Downgrade database schema"""
    
    # Drop tables in reverse order (due to foreign keys)
    op.drop_table('material_shortage_alerts')
    
    op.drop_column('work_orders', 'shortage_alert_sent')
    op.drop_column('work_orders', 'has_material_shortage')
    op.drop_column('work_orders', 'materials_consumed')
    op.drop_column('work_orders', 'materials_allocated')
    
    op.drop_column('stock_quants', 'available_qty')
    op.drop_column('stock_quants', 'reserved_qty')
    
    op.drop_table('material_debt_logs')
    op.drop_table('spk_material_allocations')
    
    print("✅ Migration 004: Downgrade completed!")
