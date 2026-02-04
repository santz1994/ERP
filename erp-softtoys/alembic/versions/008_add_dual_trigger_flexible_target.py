"""Add dual trigger system and flexible target system

Revision ID: 008_dual_trigger_flexible_target
Revises: 004_material_allocation
Create Date: 2026-02-04 14:30:00.000000

Changes:
1. Manufacturing Orders: Add dual trigger fields (po_fabric_id, po_label_id, trigger_mode)
2. SPK: Add flexible target fields (buffer_percentage, good_qty, defect_qty, rework_qty)
3. Work Orders: Already has output_qty/reject_qty, add computed properties in model

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '008_dual_trigger_flexible_target'
down_revision = '004_material_allocation'  # ✅ Merge with existing head
branch_labels = None
depends_on = None


def upgrade():
    """Apply changes to database."""
    
    # ========================================================================
    # 1. MANUFACTURING ORDERS - Dual Trigger System
    # ========================================================================
    print("✅ Adding dual trigger fields to manufacturing_orders...")
    
    # Add PO Fabric reference (TRIGGER 1)
    op.add_column('manufacturing_orders', 
                  sa.Column('po_fabric_id', sa.Integer(), nullable=True, 
                           comment='PO for fabric materials (TRIGGER 1: enables Cutting/Embroidery)'))
    op.create_index('ix_manufacturing_orders_po_fabric_id', 'manufacturing_orders', ['po_fabric_id'])
    op.create_foreign_key('fk_mo_po_fabric', 'manufacturing_orders', 'purchase_orders', 
                         ['po_fabric_id'], ['id'])
    
    # Add PO Label reference (TRIGGER 2)
    op.add_column('manufacturing_orders', 
                  sa.Column('po_label_id', sa.Integer(), nullable=True,
                           comment='PO for labels/tags (TRIGGER 2: enables all departments)'))
    op.create_index('ix_manufacturing_orders_po_label_id', 'manufacturing_orders', ['po_label_id'])
    op.create_foreign_key('fk_mo_po_label', 'manufacturing_orders', 'purchase_orders', 
                         ['po_label_id'], ['id'])
    
    # Add trigger mode
    op.add_column('manufacturing_orders', 
                  sa.Column('trigger_mode', sa.String(20), nullable=False, 
                           server_default='PARTIAL',
                           comment='Production release mode: PARTIAL (fabric only) or RELEASED (fabric+label)'))
    op.create_index('ix_manufacturing_orders_trigger_mode', 'manufacturing_orders', ['trigger_mode'])
    
    print("   ✓ Dual trigger system added to manufacturing_orders")
    
    # ========================================================================
    # 2. SPK - Flexible Target System
    # ========================================================================
    print("✅ Adding flexible target fields to spks...")
    
    # Add buffer percentage
    op.add_column('spks', 
                  sa.Column('buffer_percentage', sa.DECIMAL(5, 2), nullable=False, 
                           server_default='0',
                           comment='Department buffer % (10% Cutting, 6.7% Sewing, etc.)'))
    
    # Add quality tracking fields
    op.add_column('spks', 
                  sa.Column('good_qty', sa.Integer(), nullable=False, 
                           server_default='0',
                           comment='Good output produced'))
    
    op.add_column('spks', 
                  sa.Column('defect_qty', sa.Integer(), nullable=False, 
                           server_default='0',
                           comment='Defect/reject output'))
    
    op.add_column('spks', 
                  sa.Column('rework_qty', sa.Integer(), nullable=False, 
                           server_default='0',
                           comment='Sent to rework'))
    
    # Update column comments for clarity
    op.alter_column('spks', 'original_qty',
                   existing_type=sa.Integer(),
                   comment='Base quantity from MO')
    
    op.alter_column('spks', 'target_qty',
                   existing_type=sa.Integer(),
                   comment='Target with buffer (original × buffer)')
    
    op.alter_column('spks', 'produced_qty',
                   existing_type=sa.Integer(),
                   comment='Total produced (good + defect)')
    
    print("   ✓ Flexible target system added to spks")
    
    # ========================================================================
    # 3. WORK ORDERS - Update comments only (computed properties in model)
    # ========================================================================
    print("✅ Updating work_orders column comments...")
    
    op.alter_column('work_orders', 'input_qty',
                   existing_type=sa.DECIMAL(10, 2),
                   comment='Material received as input')
    
    op.alter_column('work_orders', 'output_qty',
                   existing_type=sa.DECIMAL(10, 2),
                   comment='Good output produced (also aliased as good_qty, actual_qty)')
    
    op.alter_column('work_orders', 'reject_qty',
                   existing_type=sa.DECIMAL(10, 2),
                   comment='Defective/rejected units (also aliased as defect_qty)')
    
    print("   ✓ Work orders comments updated")
    
    print("\n🎉 Migration complete! Database schema updated with:")
    print("   - Dual Trigger System (ManufacturingOrder)")
    print("   - Flexible Target System (SPK)")
    print("   - Backward Compatible Aliases (WorkOrder)")


def downgrade():
    """Revert changes."""
    
    print("⚠️  Rolling back dual trigger and flexible target changes...")
    
    # Remove SPK flexible target fields
    op.drop_column('spks', 'rework_qty')
    op.drop_column('spks', 'defect_qty')
    op.drop_column('spks', 'good_qty')
    op.drop_column('spks', 'buffer_percentage')
    
    # Remove MO dual trigger fields
    op.drop_index('ix_manufacturing_orders_trigger_mode', 'manufacturing_orders')
    op.drop_column('manufacturing_orders', 'trigger_mode')
    
    op.drop_constraint('fk_mo_po_label', 'manufacturing_orders', type_='foreignkey')
    op.drop_index('ix_manufacturing_orders_po_label_id', 'manufacturing_orders')
    op.drop_column('manufacturing_orders', 'po_label_id')
    
    op.drop_constraint('fk_mo_po_fabric', 'manufacturing_orders', type_='foreignkey')
    op.drop_index('ix_manufacturing_orders_po_fabric_id', 'manufacturing_orders')
    op.drop_column('manufacturing_orders', 'po_fabric_id')
    
    print("✅ Rollback complete")
