"""Add dual-mode PO system with BOM explosion support

Revision ID: 009_dual_mode_po_bom_explosion
Revises: 008_dual_trigger_flexible_target
Create Date: 2026-02-05 10:00:00

Features:
- Dual-mode PO: AUTO_BOM vs MANUAL input
- BOM Explosion from Article
- Supplier per material (flexibility)
- 3-Type PO: KAIN, LABEL, ACCESSORIES
- Week/Destination from PO LABEL
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSON

# revision identifiers
revision = '009_dual_mode_po_bom_explosion'
down_revision = '008_dual_trigger_flexible_target'
branch_labels = None
depends_on = None


def upgrade():
    # 1. Add new columns to purchase_orders table
    op.add_column('purchase_orders', 
        sa.Column('input_mode', sa.String(20), server_default='MANUAL', nullable=False))
    op.add_column('purchase_orders',
        sa.Column('source_article_id', sa.Integer(), nullable=True))
    op.add_column('purchase_orders',
        sa.Column('article_quantity', sa.DECIMAL(15, 3), nullable=True))
    op.add_column('purchase_orders',
        sa.Column('po_type', sa.String(20), server_default='ACCESSORIES', nullable=False))
    op.add_column('purchase_orders',
        sa.Column('linked_mo_id', sa.Integer(), nullable=True))
    op.add_column('purchase_orders',
        sa.Column('extra_metadata', JSON, nullable=True, comment='JSON metadata: BOM explosion, supplier mappings, week/destination'))
    op.add_column('purchase_orders',
        sa.Column('total_amount', sa.DECIMAL(18, 2), server_default='0.00'))
    op.add_column('purchase_orders',
        sa.Column('currency', sa.String(10), server_default='IDR'))
    op.add_column('purchase_orders',
        sa.Column('approved_by', sa.Integer(), nullable=True))
    op.add_column('purchase_orders',
        sa.Column('approved_at', sa.DateTime(timezone=True), nullable=True))
    
    # Foreign keys
    op.create_foreign_key(
        'fk_po_source_article',
        'purchase_orders', 'products',
        ['source_article_id'], ['id'],
        ondelete='SET NULL'
    )
    
    op.create_foreign_key(
        'fk_po_linked_mo',
        'purchase_orders', 'manufacturing_orders',
        ['linked_mo_id'], ['id'],
        ondelete='SET NULL'
    )
    
    op.create_foreign_key(
        'fk_po_approved_by',
        'purchase_orders', 'users',
        ['approved_by'], ['id'],
        ondelete='SET NULL'
    )
    
    # Add check constraint for input_mode
    op.create_check_constraint(
        'check_po_input_mode',
        'purchase_orders',
        "input_mode IN ('AUTO_BOM', 'MANUAL')"
    )
    
    # Add check constraint for po_type
    op.create_check_constraint(
        'check_po_type',
        'purchase_orders',
        "po_type IN ('KAIN', 'LABEL', 'ACCESSORIES')"
    )
    
    # Create index for performance
    op.create_index('idx_po_input_mode', 'purchase_orders', ['input_mode'])
    op.create_index('idx_po_type', 'purchase_orders', ['po_type'])
    op.create_index('idx_po_linked_mo', 'purchase_orders', ['linked_mo_id'])
    
    # 2. Create purchase_order_lines table (for detailed items)
    op.create_table(
        'purchase_order_lines',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('purchase_order_id', sa.Integer(), nullable=False, index=True),
        sa.Column('product_id', sa.Integer(), nullable=False, index=True),
        sa.Column('supplier_id', sa.Integer(), nullable=True, index=True),  # 🔥 KEY: Supplier per material
        sa.Column('quantity', sa.DECIMAL(15, 3), nullable=False),
        sa.Column('unit_price', sa.DECIMAL(18, 2), nullable=False),
        sa.Column('subtotal', sa.DECIMAL(18, 2), nullable=False),
        sa.Column('uom', sa.String(20), nullable=False),
        sa.Column('extra_metadata', JSON, nullable=True, comment='JSON metadata: from_bom, quantity_per_unit, etc'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
        
        # Foreign Keys
        sa.ForeignKeyConstraint(['purchase_order_id'], ['purchase_orders.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['supplier_id'], ['partners.id'], ondelete='SET NULL')
    )
    
    # Indexes for PO Lines
    op.create_index('idx_po_line_po_id', 'purchase_order_lines', ['purchase_order_id'])
    op.create_index('idx_po_line_product_id', 'purchase_order_lines', ['product_id'])
    op.create_index('idx_po_line_supplier_id', 'purchase_order_lines', ['supplier_id'])


def downgrade():
    # Drop tables
    op.drop_table('purchase_order_lines')
    
    # Drop indexes
    op.drop_index('idx_po_input_mode', 'purchase_orders')
    op.drop_index('idx_po_type', 'purchase_orders')
    op.drop_index('idx_po_linked_mo', 'purchase_orders')
    
    # Drop constraints
    op.drop_constraint('check_po_input_mode', 'purchase_orders', type_='check')
    op.drop_constraint('check_po_type', 'purchase_orders', type_='check')
    op.drop_constraint('fk_po_source_article', 'purchase_orders', type_='foreignkey')
    op.drop_constraint('fk_po_linked_mo', 'purchase_orders', type_='foreignkey')
    op.drop_constraint('fk_po_approved_by', 'purchase_orders', type_='foreignkey')
    
    # Drop columns
    op.drop_column('purchase_orders', 'approved_at')
    op.drop_column('purchase_orders', 'approved_by')
    op.drop_column('purchase_orders', 'currency')
    op.drop_column('purchase_orders', 'total_amount')
    op.drop_column('purchase_orders', 'extra_metadata')
    op.drop_column('purchase_orders', 'linked_mo_id')
    op.drop_column('purchase_orders', 'po_type')
    op.drop_column('purchase_orders', 'article_quantity')
    op.drop_column('purchase_orders', 'source_article_id')
    op.drop_column('purchase_orders', 'input_mode')
