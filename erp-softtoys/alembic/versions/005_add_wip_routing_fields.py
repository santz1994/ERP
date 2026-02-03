"""add_wip_routing_fields

Revision ID: 005_add_wip_routing
Revises: 004_extend_code
Create Date: 2026-02-03 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '005_add_wip_routing'
down_revision = '004_extend_code'
branch_labels = None
depends_on = None


def upgrade():
    """Add WIP routing fields and new tables"""
    
    print("\n🔄 Adding WIP routing fields to existing tables...")
    
    # Get connection to check existing columns
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    
    # 1. Add product_type column to products table (if not exists)
    products_columns = [col['name'] for col in inspector.get_columns('products')]
    if 'product_type' not in products_columns:
        print("  ✅ Adding product_type column to products table...")
        op.add_column('products', 
            sa.Column('product_type', sa.String(50), nullable=True)
        )
        
        # Set default values for existing products based on type column
        op.execute("""
            UPDATE products 
            SET product_type = CASE 
                WHEN type = 'Raw Material' THEN 'raw_material'
                WHEN type = 'WIP' THEN 'wip'
                WHEN type = 'Finish Good' THEN 'finished_good'
                WHEN type = 'Service' THEN 'service'
                ELSE 'raw_material'
            END
        """)
    else:
        print("  ⏭️  product_type column already exists, skipping...")
    
    # 2. Add routing fields to bom_headers
    bom_columns = [col['name'] for col in inspector.get_columns('bom_headers')]
    if 'routing_department' not in bom_columns:
        print("  ✅ Adding routing_department and routing_sequence to bom_headers...")
        op.add_column('bom_headers', 
            sa.Column('routing_department', sa.String(50), nullable=True)
        )
        op.add_column('bom_headers',
            sa.Column('routing_sequence', sa.Integer, nullable=True)
        )
    else:
        print("  ⏭️  routing fields already exist in bom_headers, skipping...")
    
    # 3. Add WIP tracking fields to work_orders
    wo_columns = [col['name'] for col in inspector.get_columns('work_orders')]
    if 'wo_number' not in wo_columns:
        print("  ✅ Adding WIP tracking fields to work_orders...")
        op.add_column('work_orders',
            sa.Column('wo_number', sa.String(100), nullable=True)
        )
        op.add_column('work_orders',
            sa.Column('sequence', sa.Integer, nullable=True)
        )
        op.add_column('work_orders',
            sa.Column('input_wip_product_id', sa.Integer, nullable=True)
        )
        op.add_column('work_orders',
            sa.Column('output_wip_product_id', sa.Integer, nullable=True)
        )
        op.add_column('work_orders',
            sa.Column('target_qty', sa.DECIMAL(10, 2), nullable=True)
        )
        op.add_column('work_orders',
            sa.Column('notes', sa.TEXT, nullable=True)
        )
        
        # Add foreign keys
        op.create_foreign_key(
            'fk_wo_input_wip_product',
            'work_orders', 'products',
            ['input_wip_product_id'], ['id'],
            ondelete='SET NULL'
        )
        op.create_foreign_key(
            'fk_wo_output_wip_product',
            'work_orders', 'products',
            ['output_wip_product_id'], ['id'],
            ondelete='SET NULL'
        )
    else:
        print("  ⏭️  WIP tracking fields already exist in work_orders, skipping...")
    
    # 4. Add BOM explosion tracking to manufacturing_orders
    mo_columns = [col['name'] for col in inspector.get_columns('manufacturing_orders')]
    if 'finished_good_product_id' not in mo_columns:
        print("  ✅ Adding BOM explosion tracking to manufacturing_orders...")
        op.add_column('manufacturing_orders',
            sa.Column('finished_good_product_id', sa.Integer, nullable=True)
        )
        op.add_column('manufacturing_orders',
            sa.Column('bom_explosion_complete', sa.Boolean, default=False)
        )
        op.add_column('manufacturing_orders',
            sa.Column('total_departments', sa.Integer, default=0)
        )
        
        op.create_foreign_key(
            'fk_mo_finished_good',
            'manufacturing_orders', 'products',
            ['finished_good_product_id'], ['id'],
            ondelete='SET NULL'
        )
    else:
        print("  ⏭️  BOM explosion fields already exist in manufacturing_orders, skipping...")
    
    # 5. Create bom_wip_routing table (if not exists)
    existing_tables = inspector.get_table_names()
    if 'bom_wip_routing' not in existing_tables:
        print("  ✅ Creating bom_wip_routing table...")
        op.create_table(
            'bom_wip_routing',
            sa.Column('id', sa.Integer, primary_key=True, index=True),
            sa.Column('bom_header_id', sa.Integer, sa.ForeignKey('bom_headers.id'), nullable=False),
            sa.Column('department', sa.String(50), nullable=False),
            sa.Column('sequence', sa.Integer, nullable=False),
            sa.Column('input_wip_product_id', sa.Integer, sa.ForeignKey('products.id'), nullable=True),
            sa.Column('output_wip_product_id', sa.Integer, sa.ForeignKey('products.id'), nullable=True),
            sa.Column('is_optional', sa.Boolean, default=False),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now())
        )
    else:
        print("  ⏭️  bom_wip_routing table already exists, skipping...")
    
    # 6. Create wip_transfer_logs table (if not exists)
    if 'wip_transfer_logs' not in existing_tables:
        print("  ✅ Creating wip_transfer_logs table...")
        op.create_table(
            'wip_transfer_logs',
            sa.Column('id', sa.Integer, primary_key=True, index=True),
            sa.Column('wo_id', sa.Integer, sa.ForeignKey('work_orders.id'), nullable=False),
            sa.Column('wip_product_id', sa.Integer, sa.ForeignKey('products.id'), nullable=False),
            sa.Column('from_department', sa.String(50), nullable=False),
            sa.Column('to_department', sa.String(50), nullable=False),
            sa.Column('qty_transferred', sa.DECIMAL(10, 2), nullable=False),
            sa.Column('transfer_date', sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column('notes', sa.TEXT, nullable=True)
        )
    else:
        print("  ⏭️  wip_transfer_logs table already exists, skipping...")
    
    print("\n✅ Migration 005 completed successfully!")


def downgrade():
    """Remove WIP routing fields and tables"""
    
    print("\n🔄 Rolling back WIP routing changes...")
    
    # Drop tables
    op.drop_table('wip_transfer_logs')
    op.drop_table('bom_wip_routing')
    
    # Remove columns from manufacturing_orders
    op.drop_constraint('fk_mo_finished_good', 'manufacturing_orders', type_='foreignkey')
    op.drop_column('manufacturing_orders', 'total_departments')
    op.drop_column('manufacturing_orders', 'bom_explosion_complete')
    op.drop_column('manufacturing_orders', 'finished_good_product_id')
    
    # Remove columns from work_orders
    op.drop_constraint('fk_wo_output_wip_product', 'work_orders', type_='foreignkey')
    op.drop_constraint('fk_wo_input_wip_product', 'work_orders', type_='foreignkey')
    op.drop_column('work_orders', 'notes')
    op.drop_column('work_orders', 'target_qty')
    op.drop_column('work_orders', 'output_wip_product_id')
    op.drop_column('work_orders', 'input_wip_product_id')
    op.drop_column('work_orders', 'sequence')
    op.drop_column('work_orders', 'wo_number')
    
    # Remove columns from bom_headers
    op.drop_column('bom_headers', 'routing_sequence')
    op.drop_column('bom_headers', 'routing_department')
    
    # Remove product_type from products
    op.drop_column('products', 'product_type')
    
    print("\n✅ Rollback completed!")
