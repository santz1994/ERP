"""extend product code length

Revision ID: 004_extend_code
Revises: 003_wip_routing
Create Date: 2026-02-03 15:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '004_extend_code'
down_revision = '003_wip_routing'
branch_labels = None
depends_on = None


def upgrade():
    """Extend products.code from VARCHAR(50) to VARCHAR(255)"""
    # Alter column type
    op.alter_column('products', 'code',
                    existing_type=sa.VARCHAR(50),
                    type_=sa.VARCHAR(255),
                    existing_nullable=False)


def downgrade():
    """Revert products.code back to VARCHAR(50)"""
    op.alter_column('products', 'code',
                    existing_type=sa.VARCHAR(255),
                    type_=sa.VARCHAR(50),
                    existing_nullable=False)
