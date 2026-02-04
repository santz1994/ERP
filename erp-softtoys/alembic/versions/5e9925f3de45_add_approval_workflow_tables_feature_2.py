"""Add approval workflow tables - Feature #2

Revision ID: 5e9925f3de45
Revises: 005_add_wip_routing
Create Date: 2026-02-04 06:44:55.940008

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '5e9925f3de45'
down_revision: Union[str, Sequence[str], None] = '005_add_wip_routing'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - Add approval workflow tables."""
    # Create approval_requests table
    op.create_table('approval_requests',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('entity_type', sa.String(length=50), nullable=False),
    sa.Column('entity_id', sa.UUID(), nullable=False),
    sa.Column('submitted_by', sa.UUID(), nullable=False),
    sa.Column('changes', sa.JSON(), nullable=False),
    sa.Column('reason', sa.Text(), nullable=False),
    sa.Column('status', sa.String(length=20), nullable=False),
    sa.Column('current_step', sa.Integer(), nullable=False),
    sa.Column('approval_chain', sa.JSON(), nullable=False),
    sa.Column('approvals', sa.JSON(), nullable=True),
    sa.Column('rejection_reason', sa.Text(), nullable=True),
    sa.Column('rejected_by', sa.UUID(), nullable=True),
    sa.Column('rejected_at', sa.DateTime(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['rejected_by'], ['users.id'], ),
    sa.ForeignKeyConstraint(['submitted_by'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_approval_requests_created', 'approval_requests', ['created_at'], unique=False)
    op.create_index('idx_approval_requests_entity', 'approval_requests', ['entity_type', 'entity_id'], unique=False)
    op.create_index('idx_approval_requests_status', 'approval_requests', ['status'], unique=False)
    op.create_index(op.f('ix_approval_requests_entity_id'), 'approval_requests', ['entity_id'], unique=False)
    op.create_index(op.f('ix_approval_requests_entity_type'), 'approval_requests', ['entity_type'], unique=False)
    op.create_index(op.f('ix_approval_requests_status'), 'approval_requests', ['status'], unique=False)
    
    # Create approval_steps table
    op.create_table('approval_steps',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('approval_request_id', sa.UUID(), nullable=False),
    sa.Column('step_number', sa.Integer(), nullable=False),
    sa.Column('approver_role', sa.String(length=50), nullable=False),
    sa.Column('status', sa.String(length=20), nullable=False),
    sa.Column('approved_by', sa.UUID(), nullable=True),
    sa.Column('approved_at', sa.DateTime(), nullable=True),
    sa.Column('notes', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['approval_request_id'], ['approval_requests.id'], ),
    sa.ForeignKeyConstraint(['approved_by'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_approval_steps_request', 'approval_steps', ['approval_request_id'], unique=False)
    op.create_index('idx_approval_steps_status', 'approval_steps', ['status'], unique=False)
    op.create_index(op.f('ix_approval_steps_approval_request_id'), 'approval_steps', ['approval_request_id'], unique=False)
    op.create_index(op.f('ix_approval_steps_status'), 'approval_steps', ['status'], unique=False)
    
    # Commented out cleanup operations - run manually if needed
    # op.drop_index(op.f('idx_bom_wip_routing_bom_header'), table_name='bom_wip_routing')
    # op.drop_index(op.f('idx_bom_wip_routing_department'), table_name='bom_wip_routing')
    # op.drop_table('bom_wip_routing')
    # op.drop_index(op.f('idx_wip_transfer_date'), table_name='wip_transfer_logs')
    # op.drop_index(op.f('idx_wip_transfer_product'), table_name='wip_transfer_logs')
    # op.drop_index(op.f('idx_wip_transfer_wo'), table_name='wip_transfer_logs')
    # op.drop_table('wip_transfer_logs')
    # op.drop_column('bom_headers', 'routing_department')
    # op.drop_column('bom_headers', 'routing_sequence')
    # op.drop_index(op.f('idx_mo_fg_product'), table_name='manufacturing_orders')
    # op.drop_constraint(op.f('manufacturing_orders_finished_good_product_id_fkey'), 'manufacturing_orders', type_='foreignkey')
    # op.drop_column('manufacturing_orders', 'total_departments')
    # op.drop_column('manufacturing_orders', 'finished_good_product_id')
    # op.drop_column('manufacturing_orders', 'bom_explosion_complete')
    # op.alter_column('products', 'code', existing_type=sa.VARCHAR(length=255), type_=sa.String(length=50), existing_nullable=False)
    # op.drop_column('products', 'product_type')
    # op.drop_index(op.f('idx_work_orders_sequence'), table_name='work_orders')
    # op.drop_index(op.f('idx_work_orders_status'), table_name='work_orders')
    # op.drop_constraint(op.f('fk_wo_input_wip_product'), 'work_orders', type_='foreignkey')
    # op.drop_constraint(op.f('fk_wo_output_wip_product'), 'work_orders', type_='foreignkey')


def downgrade() -> None:
    """Downgrade schema - Remove approval workflow tables."""
    # Drop approval tables
    op.drop_index(op.f('ix_approval_steps_status'), table_name='approval_steps')
    op.drop_index(op.f('ix_approval_steps_approval_request_id'), table_name='approval_steps')
    op.drop_index('idx_approval_steps_status', table_name='approval_steps')
    op.drop_index('idx_approval_steps_request', table_name='approval_steps')
    op.drop_table('approval_steps')
    
    op.drop_index(op.f('ix_approval_requests_status'), table_name='approval_requests')
    op.drop_index(op.f('ix_approval_requests_entity_type'), table_name='approval_requests')
    op.drop_index(op.f('ix_approval_requests_entity_id'), table_name='approval_requests')
    op.drop_index('idx_approval_requests_status', table_name='approval_requests')
    op.drop_index('idx_approval_requests_entity', table_name='approval_requests')
    op.drop_index('idx_approval_requests_created', table_name='approval_requests')
    op.drop_table('approval_requests')
    op.add_column('products', sa.Column('product_type', sa.VARCHAR(length=20), autoincrement=False, nullable=True))
    op.alter_column('products', 'code',
               existing_type=sa.String(length=50),
               type_=sa.VARCHAR(length=255),
               existing_nullable=False)
    op.add_column('manufacturing_orders', sa.Column('bom_explosion_complete', sa.BOOLEAN(), autoincrement=False, nullable=True))
    op.add_column('manufacturing_orders', sa.Column('finished_good_product_id', sa.INTEGER(), autoincrement=False, nullable=True))
    op.add_column('manufacturing_orders', sa.Column('total_departments', sa.INTEGER(), autoincrement=False, nullable=True))
    op.create_foreign_key(op.f('manufacturing_orders_finished_good_product_id_fkey'), 'manufacturing_orders', 'products', ['finished_good_product_id'], ['id'])
    op.create_index(op.f('idx_mo_fg_product'), 'manufacturing_orders', ['finished_good_product_id'], unique=False)
    op.add_column('bom_headers', sa.Column('routing_sequence', sa.INTEGER(), autoincrement=False, nullable=True))
    op.add_column('bom_headers', sa.Column('routing_department', sa.VARCHAR(length=50), autoincrement=False, nullable=True))
    op.create_table('wip_transfer_logs',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('wo_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('wip_product_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('from_department', sa.VARCHAR(length=50), autoincrement=False, nullable=False),
    sa.Column('to_department', sa.VARCHAR(length=50), autoincrement=False, nullable=False),
    sa.Column('qty_transferred', sa.NUMERIC(precision=10, scale=2), autoincrement=False, nullable=False),
    sa.Column('transfer_date', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), autoincrement=False, nullable=True),
    sa.Column('transferred_by', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('notes', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['transferred_by'], ['users.id'], name=op.f('wip_transfer_logs_transferred_by_fkey')),
    sa.ForeignKeyConstraint(['wip_product_id'], ['products.id'], name=op.f('wip_transfer_logs_wip_product_id_fkey')),
    sa.ForeignKeyConstraint(['wo_id'], ['work_orders.id'], name=op.f('wip_transfer_logs_wo_id_fkey')),
    sa.PrimaryKeyConstraint('id', name=op.f('wip_transfer_logs_pkey'))
    )
    op.create_index(op.f('idx_wip_transfer_wo'), 'wip_transfer_logs', ['wo_id'], unique=False)
    op.create_index(op.f('idx_wip_transfer_product'), 'wip_transfer_logs', ['wip_product_id'], unique=False)
    op.create_index(op.f('idx_wip_transfer_date'), 'wip_transfer_logs', ['transfer_date'], unique=False)
    op.create_table('bom_wip_routing',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('bom_header_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('department', sa.VARCHAR(length=50), autoincrement=False, nullable=False),
    sa.Column('sequence', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('input_wip_product_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('output_wip_product_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('is_optional', sa.BOOLEAN(), autoincrement=False, nullable=True),
    sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), autoincrement=False, nullable=True),
    sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['bom_header_id'], ['bom_headers.id'], name=op.f('bom_wip_routing_bom_header_id_fkey')),
    sa.ForeignKeyConstraint(['input_wip_product_id'], ['products.id'], name=op.f('bom_wip_routing_input_wip_product_id_fkey')),
    sa.ForeignKeyConstraint(['output_wip_product_id'], ['products.id'], name=op.f('bom_wip_routing_output_wip_product_id_fkey')),
    sa.PrimaryKeyConstraint('id', name=op.f('bom_wip_routing_pkey'))
    )
    op.create_index(op.f('idx_bom_wip_routing_department'), 'bom_wip_routing', ['department'], unique=False)
    op.create_index(op.f('idx_bom_wip_routing_bom_header'), 'bom_wip_routing', ['bom_header_id'], unique=False)
    op.drop_index(op.f('ix_approval_steps_status'), table_name='approval_steps')
    op.drop_index(op.f('ix_approval_steps_approval_request_id'), table_name='approval_steps')
    op.drop_index('idx_approval_steps_status', table_name='approval_steps')
    op.drop_index('idx_approval_steps_request', table_name='approval_steps')
    op.drop_table('approval_steps')
    op.drop_index(op.f('ix_approval_requests_status'), table_name='approval_requests')
    op.drop_index(op.f('ix_approval_requests_entity_type'), table_name='approval_requests')
    op.drop_index(op.f('ix_approval_requests_entity_id'), table_name='approval_requests')
    op.drop_index('idx_approval_requests_status', table_name='approval_requests')
    op.drop_index('idx_approval_requests_entity', table_name='approval_requests')
    op.drop_index('idx_approval_requests_created', table_name='approval_requests')
    op.drop_table('approval_requests')
    # ### end Alembic commands ###
