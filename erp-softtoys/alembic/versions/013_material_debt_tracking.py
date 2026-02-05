"""create material debt tables

Revision ID: 013_material_debt_tracking
Revises: 012_rework_qc_tables
Create Date: 2026-02-05 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import func


# revision identifiers, used by Alembic.
revision = '013_material_debt_tracking'
down_revision = '012_rework_qc_tables'
branch_labels = None
depends_on = None


def upgrade():
    """Create material debt tracking tables"""

    # Create MaterialDebtStatus enum
    op.execute("""
        CREATE TYPE materialDebtstatus AS ENUM (
            'ACTIVE',
            'PARTIAL_PAID',
            'FULLY_PAID',
            'WRITTEN_OFF'
        )
    """)

    # Create material_debts table
    op.create_table(
        'material_debts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False,
                  comment='Material in debt'),
        sa.Column('uom', sa.String(length=10), nullable=False,
                  comment='Unit: YARD, KG, PCS, etc.'),
        sa.Column('total_debt_qty', sa.DECIMAL(15, 3), nullable=False,
                  comment='Total debt incurred (absolute value)'),
        sa.Column('settled_qty', sa.DECIMAL(15, 3), nullable=False,
                  server_default='0',
                  comment='Quantity already settled'),
        sa.Column('balance_qty', sa.DECIMAL(15, 3), nullable=False,
                  comment='Remaining debt (total - settled)'),
        sa.Column('status', sa.Enum('ACTIVE', 'PARTIAL_PAID',
                                     'FULLY_PAID', 'WRITTEN_OFF',
                                     name='materialDebtstatus'),
                  nullable=False, server_default='ACTIVE'),
        sa.Column('spk_id', sa.Integer(), nullable=True,
                  comment='SPK that caused debt'),
        sa.Column('reference_doc', sa.String(length=100), nullable=False,
                  comment='SPK number or transaction ref'),
        sa.Column('estimated_cost', sa.DECIMAL(15, 2), nullable=True,
                  comment='Estimated material cost (debt × avg price)'),
        sa.Column('rush_order_cost', sa.DECIMAL(15, 2), nullable=False,
                  server_default='0',
                  comment='Additional cost for rush PO'),
        sa.Column('total_cost_impact', sa.DECIMAL(15, 2), nullable=True,
                  comment='Total financial impact (estimated + rush)'),
        sa.Column('risk_level', sa.String(length=20), nullable=False,
                  server_default='MEDIUM',
                  comment='LOW/MEDIUM/HIGH/CRITICAL'),
        sa.Column('impact_notes', sa.TEXT(), nullable=True,
                  comment='Production impact description'),
        sa.Column('created_by_id', sa.Integer(), nullable=True,
                  comment='User who recorded debt'),
        sa.Column('resolved_by_id', sa.Integer(), nullable=True,
                  comment='User who settled debt'),
        sa.Column('resolved_at', sa.DateTime(timezone=True), nullable=True,
                  comment='When debt fully settled'),
        sa.Column('created_at', sa.DateTime(timezone=True),
                  nullable=False, server_default=func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True),
                  nullable=True, server_default=func.now(),
                  onupdate=func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ),
        sa.ForeignKeyConstraint(['spk_id'], ['work_orders.id'], ),
        sa.ForeignKeyConstraint(['created_by_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['resolved_by_id'], ['users.id'], ),
    )

    # Create indexes for material_debts
    op.create_index('ix_material_debts_product_id',
                    'material_debts', ['product_id'])
    op.create_index('ix_material_debts_status',
                    'material_debts', ['status'])
    op.create_index('ix_material_debts_created_at',
                    'material_debts', ['created_at'])

    # Create material_debt_settlements table
    op.create_table(
        'material_debt_settlements',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('debt_id', sa.Integer(), nullable=False,
                  comment='Debt being settled'),
        sa.Column('settlement_qty', sa.DECIMAL(15, 3), nullable=False,
                  comment='Quantity applied to debt'),
        sa.Column('settlement_cost', sa.DECIMAL(15, 2), nullable=True,
                  comment='Actual cost of settled qty'),
        sa.Column('po_id', sa.Integer(), nullable=True,
                  comment='PO that settled debt'),
        sa.Column('po_line_id', sa.Integer(), nullable=True,
                  comment='Specific PO line'),
        sa.Column('grn_number', sa.String(length=50), nullable=True,
                  comment='GRN reference number'),
        sa.Column('settlement_date', sa.DateTime(timezone=True),
                  nullable=False, server_default=func.now(),
                  comment='When settlement applied'),
        sa.Column('settled_by_id', sa.Integer(), nullable=True,
                  comment='User who processed settlement'),
        sa.Column('notes', sa.TEXT(), nullable=True,
                  comment='Settlement notes'),
        sa.Column('auto_settled', sa.Boolean(), nullable=False,
                  server_default='false',
                  comment='True if auto-applied from GRN'),
        sa.Column('created_at', sa.DateTime(timezone=True),
                  nullable=False, server_default=func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['debt_id'], ['material_debts.id'], ),
        sa.ForeignKeyConstraint(['po_id'], ['purchase_orders.id'], ),
        sa.ForeignKeyConstraint(['po_line_id'],
                                ['purchase_order_lines.id'], ),
        sa.ForeignKeyConstraint(['settled_by_id'], ['users.id'], ),
    )

    # Create indexes for material_debt_settlements
    op.create_index('ix_material_debt_settlements_debt_id',
                    'material_debt_settlements', ['debt_id'])
    op.create_index('ix_material_debt_settlements_po_id',
                    'material_debt_settlements', ['po_id'])


def downgrade():
    """Drop material debt tracking tables"""

    # Drop tables
    op.drop_index('ix_material_debt_settlements_po_id',
                  table_name='material_debt_settlements')
    op.drop_index('ix_material_debt_settlements_debt_id',
                  table_name='material_debt_settlements')
    op.drop_table('material_debt_settlements')

    op.drop_index('ix_material_debts_created_at',
                  table_name='material_debts')
    op.drop_index('ix_material_debts_status',
                  table_name='material_debts')
    op.drop_index('ix_material_debts_product_id',
                  table_name='material_debts')
    op.drop_table('material_debts')

    # Drop enum
    op.execute('DROP TYPE materialDebtstatus')
