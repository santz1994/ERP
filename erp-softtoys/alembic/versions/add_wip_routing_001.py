"""Add WIP routing and multi-level BOM support

Revision ID: 003_wip_routing
Revises: 002
Create Date: 2026-02-03

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '003_wip_routing'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade():
    """Upgrade database schema for WIP routing and multi-level BOM"""
    
    # Get inspector for checking existing schema
    from alembic import context
    conn = context.get_bind()
    inspector = sa.inspect(conn)
    existing_tables = inspector.get_table_names()
    
    # 1. Add product_type column to products table
    print("Adding product_type column to products table...")
    existing_product_columns = [col['name'] for col in inspector.get_columns('products')]
    
    if 'product_type' not in existing_product_columns:
        op.add_column('products', sa.Column('product_type', sa.String(20), nullable=True))
        
        # Set default values for existing products based on actual enum values
        # Database uses: RAW_MATERIAL, WIP, FINISH_GOOD, SERVICE
        op.execute("""
            UPDATE products 
            SET product_type = CASE 
                WHEN type = 'WIP' THEN 'wip'
                WHEN type = 'FINISH_GOOD' THEN 'finished_good'
                WHEN type = 'RAW_MATERIAL' THEN 'raw_material'
                WHEN type = 'SERVICE' THEN 'service'
                ELSE 'raw_material'
            END
            WHERE product_type IS NULL
        """)
    else:
        print("  product_type column already exists, skipping")
    
    # 2. Add department column to BOM headers
    print("Adding routing_department to bom_headers...")
    
    # Check existing columns in bom_headers
    existing_bom_columns = [col['name'] for col in inspector.get_columns('bom_headers')]
    
    if 'routing_department' not in existing_bom_columns:
        op.add_column('bom_headers', sa.Column('routing_department', sa.String(50), nullable=True))
    
    if 'routing_sequence' not in existing_bom_columns:
        op.add_column('bom_headers', sa.Column('routing_sequence', sa.Integer, nullable=True))
    
    # 3. Create BOM WIP Routing table (tracks department sequence)
    print("Creating bom_wip_routing table...")
    
    if 'bom_wip_routing' not in existing_tables:
        op.create_table(
            'bom_wip_routing',
            sa.Column('id', sa.Integer(), primary_key=True),
            sa.Column('bom_header_id', sa.Integer(), sa.ForeignKey('bom_headers.id'), nullable=False),
            sa.Column('department', sa.String(50), nullable=False),
            sa.Column('sequence', sa.Integer(), nullable=False),
            sa.Column('input_wip_product_id', sa.Integer(), sa.ForeignKey('products.id'), nullable=True),
            sa.Column('output_wip_product_id', sa.Integer(), sa.ForeignKey('products.id'), nullable=False),
            sa.Column('is_optional', sa.Boolean(), default=False),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
            sa.Index('idx_bom_wip_routing_bom_header', 'bom_header_id'),
            sa.Index('idx_bom_wip_routing_department', 'department'),
        )
    else:
        print("  bom_wip_routing table already exists, skipping")
    
    # 4. Update work_orders table to support WIP input/output
    print("Updating work_orders table...")
    
    # Use batch_alter_table for conditional column additions
    from alembic import context
    conn = context.get_bind()
    
    # Check which columns already exist
    inspector = sa.inspect(conn)
    existing_columns = [col['name'] for col in inspector.get_columns('work_orders')]
    
    if 'input_wip_product_id' not in existing_columns:
        op.add_column('work_orders', sa.Column('input_wip_product_id', sa.Integer(), sa.ForeignKey('products.id'), nullable=True))
    
    if 'output_wip_product_id' not in existing_columns:
        op.add_column('work_orders', sa.Column('output_wip_product_id', sa.Integer(), sa.ForeignKey('products.id'), nullable=True))
    
    if 'sequence' not in existing_columns:
        op.add_column('work_orders', sa.Column('sequence', sa.Integer(), nullable=True))
    
    if 'status' not in existing_columns:
        op.add_column('work_orders', sa.Column('status', sa.String(20), nullable=True, server_default='WAITING'))
    
    # Add indexes if they don't exist
    existing_indexes = [idx['name'] for idx in inspector.get_indexes('work_orders')]
    
    if 'idx_work_orders_status' not in existing_indexes:
        op.create_index('idx_work_orders_status', 'work_orders', ['status'])
    
    if 'idx_work_orders_sequence' not in existing_indexes:
        op.create_index('idx_work_orders_sequence', 'work_orders', ['mo_id', 'sequence'])
    
    # 5. Create WIP Transfer Logs table (track WIP movement between departments)
    print("Creating wip_transfer_logs table...")
    
    # Check if table exists
    existing_tables = inspector.get_table_names()
    
    if 'wip_transfer_logs' not in existing_tables:
        op.create_table(
            'wip_transfer_logs',
            sa.Column('id', sa.Integer(), primary_key=True),
            sa.Column('wo_id', sa.Integer(), sa.ForeignKey('work_orders.id'), nullable=False),
            sa.Column('wip_product_id', sa.Integer(), sa.ForeignKey('products.id'), nullable=False),
            sa.Column('from_department', sa.String(50), nullable=False),
            sa.Column('to_department', sa.String(50), nullable=False),
            sa.Column('qty_transferred', sa.DECIMAL(10, 2), nullable=False),
            sa.Column('transfer_date', sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column('transferred_by', sa.Integer(), sa.ForeignKey('users.id'), nullable=True),
            sa.Column('notes', sa.TEXT(), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Index('idx_wip_transfer_wo', 'wo_id'),
            sa.Index('idx_wip_transfer_product', 'wip_product_id'),
            sa.Index('idx_wip_transfer_date', 'transfer_date'),
        )
    else:
        print("  wip_transfer_logs table already exists, skipping")
    
    # 6. Update manufacturing_orders table
    print("Updating manufacturing_orders table...")
    
    existing_mo_columns = [col['name'] for col in inspector.get_columns('manufacturing_orders')]
    
    if 'finished_good_product_id' not in existing_mo_columns:
        op.add_column('manufacturing_orders', sa.Column('finished_good_product_id', sa.Integer(), sa.ForeignKey('products.id'), nullable=True))
    
    if 'bom_explosion_complete' not in existing_mo_columns:
        op.add_column('manufacturing_orders', sa.Column('bom_explosion_complete', sa.Boolean(), default=False))
    
    if 'total_departments' not in existing_mo_columns:
        op.add_column('manufacturing_orders', sa.Column('total_departments', sa.Integer(), default=0))
    
    # Add index if not exists
    existing_mo_indexes = [idx['name'] for idx in inspector.get_indexes('manufacturing_orders')]
    if 'idx_mo_fg_product' not in existing_mo_indexes:
        op.create_index('idx_mo_fg_product', 'manufacturing_orders', ['finished_good_product_id'])
    
    print("✅ Migration completed successfully!")


def downgrade():
    """Downgrade database schema"""
    
    print("Rolling back WIP routing changes...")
    
    # Drop tables in reverse order
    op.drop_table('wip_transfer_logs')
    op.drop_table('bom_wip_routing')
    
    # Drop indexes
    op.drop_index('idx_mo_fg_product', 'manufacturing_orders')
    op.drop_index('idx_work_orders_sequence', 'work_orders')
    op.drop_index('idx_work_orders_status', 'work_orders')
    
    # Drop columns from manufacturing_orders
    op.drop_column('manufacturing_orders', 'total_departments')
    op.drop_column('manufacturing_orders', 'bom_explosion_complete')
    op.drop_column('manufacturing_orders', 'finished_good_product_id')
    
    # Drop columns from work_orders
    op.drop_column('work_orders', 'status')
    op.drop_column('work_orders', 'sequence')
    op.drop_column('work_orders', 'output_wip_product_id')
    op.drop_column('work_orders', 'input_wip_product_id')
    
    # Drop columns from bom_headers
    op.drop_column('bom_headers', 'routing_sequence')
    op.drop_column('bom_headers', 'routing_department')
    
    # Drop column from products
    op.drop_column('products', 'product_type')
    
    print("✅ Rollback completed!")
