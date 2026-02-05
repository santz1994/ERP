"""Create Warehouse Finishing tables - Phase 2A

Revision ID: 011
Revises: 010
Create Date: 2026-02-05

Warehouse finishing (2-stage process):
- warehouse_finishing_stocks: Track inventory at each finishing stage
- finishing_material_consumptions: Track material consumption (filling/thread)
- finishing_inputs_outputs: Daily input/output with yield tracking
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "011_warehouse_finishing_2stage"
down_revision = "010_mo_flexible_target"
branch_labels = None
depends_on = None


def upgrade():
    """Create warehouse finishing tables"""

    # Create warehouse_finishing_stocks table
    op.create_table(
        "warehouse_finishing_stocks",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("stage", sa.String(20), nullable=False),  # STAGE_1 or STAGE_2
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("good_qty", sa.Numeric(10, 2), nullable=False, server_default="0"),
        sa.Column("defect_qty", sa.Numeric(10, 2), nullable=False, server_default="0"),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
        ),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "stage", "product_id", name="uq_stage_product"
        ),  # One stock per stage per product
    )

    # Create finishing_material_consumptions table
    op.create_table(
        "finishing_material_consumptions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("spk_id", sa.Integer(), nullable=False),
        sa.Column("stage", sa.String(20), nullable=False),  # STAGE_1 or STAGE_2
        sa.Column("material_id", sa.Integer(), nullable=False),
        sa.Column("qty_planned", sa.Numeric(10, 2), nullable=False),
        sa.Column("qty_actual", sa.Numeric(10, 2), nullable=True),
        sa.Column("uom", sa.String(10), nullable=False),  # KG, METER, etc.
        sa.Column("lot_id", sa.Integer(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
        ),
        sa.ForeignKeyConstraint(["spk_id"], ["spks.id"]),
        sa.ForeignKeyConstraint(["material_id"], ["products.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.Index(
            "ix_finishing_material_consumptions_spk_id", "spk_id"
        ),  # For quick SPK lookup
    )

    # Create finishing_inputs_outputs table
    op.create_table(
        "finishing_inputs_outputs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("spk_id", sa.Integer(), nullable=False),
        sa.Column("stage", sa.String(20), nullable=False),  # STAGE_1 or STAGE_2
        sa.Column("production_date", sa.Date(), nullable=False),
        sa.Column("input_qty", sa.Numeric(10, 2), nullable=False),
        sa.Column("good_qty", sa.Numeric(10, 2), nullable=False),
        sa.Column("defect_qty", sa.Numeric(10, 2), nullable=False),
        sa.Column("rework_qty", sa.Numeric(10, 2), nullable=False, server_default="0"),
        sa.Column(
            "yield_rate", sa.Numeric(5, 2), nullable=False
        ),  # Percentage: 0-100
        sa.Column("operator_id", sa.Integer(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
        ),
        sa.ForeignKeyConstraint(["spk_id"], ["spks.id"]),
        sa.ForeignKeyConstraint(["operator_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.Index(
            "ix_finishing_inputs_outputs_spk_id", "spk_id"
        ),  # For quick SPK lookup
        sa.Index(
            "ix_finishing_inputs_outputs_production_date", "production_date"
        ),  # For date range queries
    )


def downgrade():
    """Drop warehouse finishing tables"""
    op.drop_table("finishing_inputs_outputs")
    op.drop_table("finishing_material_consumptions")
    op.drop_table("warehouse_finishing_stocks")
