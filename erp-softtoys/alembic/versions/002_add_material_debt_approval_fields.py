"""Add Material Debt Approval Fields

Revision ID: 002
Revises: 001
Create Date: 2026-01-28 17:45:00.000000

Feature #4: Material Debt System - Approval Workflow Integration
Extends material_debt table with approval status and workflow fields
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add approval workflow fields to material_debt table"""
    
    # Create ENUM type for debt approval status
    approval_status_enum = sa.String(50)  # Use String instead of ENUM for flexibility
    
    # Add columns to material_debt table if they don't exist
    # Note: These fields are defined in the model, migration ensures DB consistency
    
    # Check if columns exist before adding (for idempotency)
    inspector = sa.inspect(op.get_bind())
    columns = [c['name'] for c in inspector.get_columns('material_debt')]
    
    # Add missing columns
    if 'approval_status' not in columns:
        op.add_column(
            'material_debt',
            sa.Column('approval_status', sa.String(50), server_default='PENDING_APPROVAL', nullable=False)
        )
    
    # Create index on approval_status
    try:
        op.create_index('ix_material_debt_approval_status', 'material_debt', ['approval_status'])
    except:
        pass  # Index might already exist


def downgrade() -> None:
    """Downgrade: Remove approval fields (if needed)"""
    
    # Drop index
    try:
        op.drop_index('ix_material_debt_approval_status', 'material_debt')
    except:
        pass
    
    # Drop columns
    try:
        op.drop_column('material_debt', 'approval_status')
    except:
        pass
