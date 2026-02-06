"""add PO Reference System - parent-child relationship for traceability

Revision ID: 014_po_reference_system
Revises: 013_material_debt_tracking
Create Date: 2026-02-06 20:00:00.000000

This migration adds support for PO Reference Chain:
- PO KAIN (Master) → TRIGGER 1 for cutting/embroidery
- PO LABEL (Child) → TRIGGER 2 for full production release
- PO ACCESSORIES (Child) → Optional reference to PO KAIN

Adds 7 columns:
1. po_type (ENUM: KAIN, LABEL, ACCESSORIES)
2. source_po_kain_id (FK → purchase_orders.id)
3. article_id (FK → products.id)
4. article_qty (INTEGER)
5. week (VARCHAR(20))
6. destination (VARCHAR(100))
7. linked_mo_id (FK → manufacturing_orders.id)

Enforces 4 business rules via constraints:
1. PO LABEL must reference PO KAIN
2. PO LABEL must have week & destination
3. PO KAIN cannot self-reference
4. PO KAIN/LABEL must have article_id

Creates 4 indexes for performance:
1. idx_po_source_po_kain
2. idx_po_article
3. idx_po_type_status
4. idx_po_week
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import func


# revision identifiers, used by Alembic.
revision = '014_po_reference_system'
down_revision = '013_material_debt_tracking'
branch_labels = None
depends_on = None


def upgrade():
    """Add PO Reference System columns, constraints, and indexes"""
    
    # Step 1: Create po_type ENUM type
    op.execute("""
        CREATE TYPE po_type_enum AS ENUM ('KAIN', 'LABEL', 'ACCESSORIES')
    """)
    
    # Step 2: Add 7 new columns
    # Column 1: po_type (nullable temporarily for data migration)
    op.add_column('purchase_orders', 
        sa.Column('po_type', 
                  sa.Enum('KAIN', 'LABEL', 'ACCESSORIES', name='po_type_enum'),
                  nullable=True,
                  comment='PO Type: KAIN (Fabric-TRIGGER 1), LABEL (TRIGGER 2), ACCESSORIES'
        )
    )
    
    # Column 2: source_po_kain_id (parent-child relationship)
    op.add_column('purchase_orders',
        sa.Column('source_po_kain_id',
                  sa.Integer(),
                  nullable=True,
                  comment='Reference to parent PO KAIN (required for PO LABEL/ACC)'
        )
    )
    
    # Column 3: article_id (product/article reference)
    op.add_column('purchase_orders',
        sa.Column('article_id',
                  sa.Integer(),
                  nullable=True,
                  comment='Article/Product reference (required for PO KAIN/LABEL)'
        )
    )
    
    # Column 4: article_qty (quantity of article)
    op.add_column('purchase_orders',
        sa.Column('article_qty',
                  sa.Integer(),
                  nullable=True,
                  comment='Article quantity (pcs)'
        )
    )
    
    # Column 5: week (production week)
    op.add_column('purchase_orders',
        sa.Column('week',
                  sa.String(20),
                  nullable=True,
                  comment='Production week (e.g., W5, W12) - required for PO LABEL'
        )
    )
    
    # Column 6: destination (delivery destination)
    op.add_column('purchase_orders',
        sa.Column('destination',
                  sa.String(100),
                  nullable=True,
                  comment='Delivery destination - required for PO LABEL'
        )
    )
    
    # Column 7: linked_mo_id (link to Manufacturing Order)
    op.add_column('purchase_orders',
        sa.Column('linked_mo_id',
                  sa.Integer(),
                  nullable=True,
                  comment='Linked Manufacturing Order (MO) for production tracking'
        )
    )
    
    # Step 3: Set default po_type for existing records
    # Existing POs are assumed to be ACCESSORIES (generic type)
    op.execute("""
        UPDATE purchase_orders 
        SET po_type = 'ACCESSORIES' 
        WHERE po_type IS NULL
    """)
    
    # Step 4: Make po_type NOT NULL after setting defaults
    op.alter_column('purchase_orders', 'po_type', nullable=False)
    
    # Step 5: Add foreign keys
    op.create_foreign_key(
        'fk_po_source_po_kain',
        'purchase_orders', 'purchase_orders',
        ['source_po_kain_id'], ['id'],
        ondelete='RESTRICT'  # Cannot delete master PO if child exists
    )
    
    op.create_foreign_key(
        'fk_po_article',
        'purchase_orders', 'products',
        ['article_id'], ['id'],
        ondelete='RESTRICT'  # Cannot delete product if PO references it
    )
    
    op.create_foreign_key(
        'fk_po_linked_mo',
        'purchase_orders', 'manufacturing_orders',
        ['linked_mo_id'], ['id'],
        ondelete='SET NULL'  # If MO deleted, PO remains but link removed
    )
    
    # Step 6: Create indexes for performance
    op.create_index(
        'idx_po_source_po_kain',
        'purchase_orders',
        ['source_po_kain_id']
    )
    
    op.create_index(
        'idx_po_article',
        'purchase_orders',
        ['article_id']
    )
    
    op.create_index(
        'idx_po_type_status',
        'purchase_orders',
        ['po_type', 'status']  # Composite index for filtering
    )
    
    op.create_index(
        'idx_po_week',
        'purchase_orders',
        ['week']
    )
    
    # Step 7: Add business rule constraints
    
    # Constraint 1: PO LABEL must have source_po_kain_id
    op.execute("""
        ALTER TABLE purchase_orders
        ADD CONSTRAINT chk_po_label_requires_kain
        CHECK (
            (po_type = 'LABEL' AND source_po_kain_id IS NOT NULL) OR
            (po_type != 'LABEL')
        )
    """)
    
    # Constraint 2: PO LABEL must have week AND destination
    op.execute("""
        ALTER TABLE purchase_orders
        ADD CONSTRAINT chk_po_label_week_destination
        CHECK (
            (po_type = 'LABEL' AND week IS NOT NULL AND destination IS NOT NULL) OR
            (po_type != 'LABEL')
        )
    """)
    
    # Constraint 3: PO KAIN cannot self-reference
    op.execute("""
        ALTER TABLE purchase_orders
        ADD CONSTRAINT chk_po_kain_no_self_reference
        CHECK (
            (po_type = 'KAIN' AND source_po_kain_id IS NULL) OR
            (po_type != 'KAIN')
        )
    """)
    
    # Constraint 4: PO KAIN/LABEL must have article_id
    op.execute("""
        ALTER TABLE purchase_orders
        ADD CONSTRAINT chk_po_article_required_for_kain_label
        CHECK (
            ((po_type IN ('KAIN', 'LABEL')) AND article_id IS NOT NULL) OR
            (po_type = 'ACCESSORIES')
        )
    """)
    
    print("✅ PO Reference System migration completed:")
    print("   - 7 columns added")
    print("   - 4 business rule constraints enforced")
    print("   - 4 indexes created for performance")
    print("   - Parent-child relationship enabled")


def downgrade():
    """Remove PO Reference System (rollback migration)"""
    
    # Step 1: Drop business rule constraints
    op.drop_constraint('chk_po_article_required_for_kain_label', 'purchase_orders')
    op.drop_constraint('chk_po_kain_no_self_reference', 'purchase_orders')
    op.drop_constraint('chk_po_label_week_destination', 'purchase_orders')
    op.drop_constraint('chk_po_label_requires_kain', 'purchase_orders')
    
    # Step 2: Drop indexes
    op.drop_index('idx_po_week', 'purchase_orders')
    op.drop_index('idx_po_type_status', 'purchase_orders')
    op.drop_index('idx_po_article', 'purchase_orders')
    op.drop_index('idx_po_source_po_kain', 'purchase_orders')
    
    # Step 3: Drop foreign keys
    op.drop_constraint('fk_po_linked_mo', 'purchase_orders')
    op.drop_constraint('fk_po_article', 'purchase_orders')
    op.drop_constraint('fk_po_source_po_kain', 'purchase_orders')
    
    # Step 4: Drop columns
    op.drop_column('purchase_orders', 'linked_mo_id')
    op.drop_column('purchase_orders', 'destination')
    op.drop_column('purchase_orders', 'week')
    op.drop_column('purchase_orders', 'article_qty')
    op.drop_column('purchase_orders', 'article_id')
    op.drop_column('purchase_orders', 'source_po_kain_id')
    op.drop_column('purchase_orders', 'po_type')
    
    # Step 5: Drop ENUM type
    op.execute("DROP TYPE po_type_enum")
    
    print("✅ PO Reference System migration rolled back successfully")
