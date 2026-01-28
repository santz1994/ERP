"""Add SPK Material Allocation table

Revision ID: 001_add_spk_material_allocation
Revises: 
Create Date: 2026-01-28 17:30:00.000000

Feature #1: BOM Manufacturing Auto-Allocate Material
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '001_add_spk_material_allocation'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create spk_material_allocations table"""
    
    # Create ENUM type for allocation status
    allocation_status_enum = postgresql.ENUM(
        'ALLOCATED',
        'RESERVED', 
        'PENDING_DEBT',
        'DEBT_APPROVED',
        'COMPLETED',
        name='spk_material_allocation_status'
    )
    allocation_status_enum.create(op.get_bind(), checkfirst=True)
    
    # Create table
    op.create_table(
        'spk_material_allocations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('spk_id', sa.Integer(), nullable=False),
        sa.Column('material_id', sa.Integer(), nullable=False),
        sa.Column('mo_id', sa.Integer(), nullable=False),
        sa.Column('qty_needed', sa.DECIMAL(precision=10, scale=2), nullable=False),
        sa.Column('qty_allocated', sa.DECIMAL(precision=10, scale=2), nullable=False),
        sa.Column('qty_from_debt', sa.DECIMAL(precision=10, scale=2), server_default='0'),
        sa.Column('warehouse_location_id', sa.Integer(), nullable=True),
        sa.Column('allocation_status', allocation_status_enum, server_default='ALLOCATED', nullable=False),
        sa.Column('has_material_debt', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('material_debt_id', sa.Integer(), nullable=True),
        sa.Column('debt_created_at', sa.DateTime(), nullable=True),
        sa.Column('allocated_by_id', sa.Integer(), nullable=False),
        sa.Column('allocated_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('notes', sa.String(length=500), nullable=True),
        sa.Column('bom_line_id', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index('ix_spk_material_allocations_spk_id', 'spk_material_allocations', ['spk_id'])
    op.create_index('ix_spk_material_allocations_material_id', 'spk_material_allocations', ['material_id'])
    op.create_index('ix_spk_material_allocations_mo_id', 'spk_material_allocations', ['mo_id'])
    op.create_index('ix_spk_material_allocations_allocation_status', 'spk_material_allocations', ['allocation_status'])
    
    # Create foreign keys
    op.create_foreign_key(
        'fk_spk_material_allocations_spk_id',
        'spk_material_allocations', 'spks',
        ['spk_id'], ['id']
    )
    op.create_foreign_key(
        'fk_spk_material_allocations_material_id',
        'spk_material_allocations', 'products',
        ['material_id'], ['id']
    )
    op.create_foreign_key(
        'fk_spk_material_allocations_mo_id',
        'spk_material_allocations', 'manufacturing_orders',
        ['mo_id'], ['id']
    )
    op.create_foreign_key(
        'fk_spk_material_allocations_material_debt_id',
        'spk_material_allocations', 'material_debts',
        ['material_debt_id'], ['id']
    )
    op.create_foreign_key(
        'fk_spk_material_allocations_allocated_by_id',
        'spk_material_allocations', 'users',
        ['allocated_by_id'], ['id']
    )


def downgrade() -> None:
    """Drop spk_material_allocations table"""
    
    # Drop table
    op.drop_table('spk_material_allocations')
    
    # Drop ENUM type
    allocation_status_enum = postgresql.ENUM(
        'ALLOCATED',
        'RESERVED', 
        'PENDING_DEBT',
        'DEBT_APPROVED',
        'COMPLETED',
        name='spk_material_allocation_status'
    )
    allocation_status_enum.drop(op.get_bind(), checkfirst=True)
