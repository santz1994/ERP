"""Create Rework & QC System tables - Phase 2B

Revision ID: 012_rework_qc_system
Revises: 011_warehouse_finishing_2stage
Create Date: 2026-02-05

Rework & QC system (quality control and defect management):
- defect_categories: Categorization of defects (STITCHING, MATERIAL, etc.)
- rework_requests: Track requests to rework defective units with approval workflow
- rework_materials: Track materials consumed during rework for cost analysis
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "012_rework_qc_system"
down_revision = "011_warehouse_finishing_2stage"
branch_labels = None
depends_on = None


def upgrade():
    """Create rework & QC tables"""

    # Create defect_categories table
    op.create_table(
        "defect_categories",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(50), nullable=False, unique=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("defect_type", sa.String(20), nullable=False),  # STITCHING, MATERIAL, etc.
        sa.Column("description", sa.String(500)),
        sa.Column("severity", sa.String(20), nullable=False),  # MINOR, MAJOR, CRITICAL
        sa.Column("default_rework_hours", sa.Integer(), default=1),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
    )

    # Create rework_requests table
    op.create_table(
        "rework_requests",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("spk_id", sa.Integer(), nullable=False),
        sa.Column("defect_qty", sa.Numeric(10, 2), nullable=False),
        sa.Column("defect_category_id", sa.Integer(), nullable=False),
        sa.Column("defect_notes", sa.String(500)),
        sa.Column("status", sa.String(20), default="PENDING", nullable=False),
        sa.Column("qc_reviewed_by_id", sa.Integer()),
        sa.Column("qc_reviewed_at", sa.DateTime(timezone=True)),
        sa.Column("qc_approval_notes", sa.String(500)),
        sa.Column("rework_started_at", sa.DateTime(timezone=True)),
        sa.Column("rework_completed_at", sa.DateTime(timezone=True)),
        sa.Column("rework_operator_id", sa.Integer()),
        sa.Column("rework_notes", sa.String(500)),
        sa.Column("verified_by_id", sa.Integer()),
        sa.Column("verified_at", sa.DateTime(timezone=True)),
        sa.Column("verified_good_qty", sa.Numeric(10, 2), default=0),
        sa.Column("verified_failed_qty", sa.Numeric(10, 2), default=0),
        sa.Column("material_cost", sa.Numeric(12, 2), default=0),
        sa.Column("labor_cost", sa.Numeric(12, 2), default=0),
        sa.Column("total_cost", sa.Numeric(12, 2), default=0),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column("requested_by_id", sa.Integer(), nullable=False),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
        ),
        sa.ForeignKeyConstraint(["spk_id"], ["spks.id"]),
        sa.ForeignKeyConstraint(["defect_category_id"], ["defect_categories.id"]),
        sa.ForeignKeyConstraint(["qc_reviewed_by_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["rework_operator_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["verified_by_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["requested_by_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.Index("ix_rework_requests_spk_id", "spk_id"),
        sa.Index("ix_rework_requests_status", "status"),
    )

    # Create rework_materials table
    op.create_table(
        "rework_materials",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("rework_request_id", sa.Integer(), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("qty_used", sa.Numeric(10, 2), nullable=False),
        sa.Column("uom", sa.String(10), nullable=False),
        sa.Column("unit_cost", sa.Numeric(12, 2), nullable=False),
        sa.Column("total_cost", sa.Numeric(12, 2), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.ForeignKeyConstraint(["rework_request_id"], ["rework_requests.id"]),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.Index("ix_rework_materials_rework_id", "rework_request_id"),
    )


def downgrade():
    """Drop rework & QC tables"""
    op.drop_table("rework_materials")
    op.drop_table("rework_requests")
    op.drop_table("defect_categories")
