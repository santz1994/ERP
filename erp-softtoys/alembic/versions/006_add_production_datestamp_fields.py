"""Add production datestamp fields for IKEA compliance

Revision ID: 006_add_datestamp
Revises: 5e9925f3de45
Create Date: 2026-02-04 18:00:00.000000

IKEA Requirements:
- Production date tracking (actual production start date)
- Planned production date (management decision)
- Label date (must match physical label on product)
- Week number (production week)
- Destination (shipping destination)
- Traceability code (batch + date code for recall purposes)

Flow: PO Purchasing (BOM Purchasing) → MO (datestamp) → BOM Explosion → SPK/WO
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '006_add_datestamp'
down_revision = '5e9925f3de45'
branch_labels = None
depends_on = None


def upgrade():
    """Add datestamp fields for production traceability"""
    
    print("\n" + "="*80)
    print("🏭 ADDING IKEA-COMPLIANT DATESTAMP FIELDS")
    print("="*80)
    
    # Get inspector
    from alembic import context
    conn = context.get_bind()
    inspector = sa.inspect(conn)
    
    # ========================================================================
    # 1. MANUFACTURING ORDERS - Add Production Planning Dates
    # ========================================================================
    print("\n📋 Adding datestamp fields to manufacturing_orders...")
    
    existing_mo_columns = [col['name'] for col in inspector.get_columns('manufacturing_orders')]
    
    # Link to PO Purchasing (source of week & destination)
    if 'po_id' not in existing_mo_columns:
        op.add_column('manufacturing_orders', 
            sa.Column('po_id', sa.Integer(), sa.ForeignKey('purchase_orders.id'), nullable=True,
                     comment='Link to PO Purchasing that triggered this MO')
        )
        print("  ✅ Added: po_id (link to PO Purchasing)")
    
    # Planned production date (set by management/PPIC)
    if 'planned_production_date' not in existing_mo_columns:
        op.add_column('manufacturing_orders', 
            sa.Column('planned_production_date', sa.Date(), nullable=True,
                     comment='Target date when production should start (set by PPIC)')
        )
        print("  ✅ Added: planned_production_date")
    
    # Actual production start date (when first WO starts)
    if 'actual_production_start_date' not in existing_mo_columns:
        op.add_column('manufacturing_orders', 
            sa.Column('actual_production_start_date', sa.Date(), nullable=True,
                     comment='Actual date when production started (first WO began)')
        )
        print("  ✅ Added: actual_production_start_date")
    
    # Actual production end date (when last WO completes)
    if 'actual_production_end_date' not in existing_mo_columns:
        op.add_column('manufacturing_orders', 
            sa.Column('actual_production_end_date', sa.Date(), nullable=True,
                     comment='Actual date when production completed (last WO finished)')
        )
        print("  ✅ Added: actual_production_end_date")
    
    # Label production date (date printed on physical label - IKEA requirement)
    if 'label_production_date' not in existing_mo_columns:
        op.add_column('manufacturing_orders', 
            sa.Column('label_production_date', sa.Date(), nullable=True,
                     comment='Date printed on product label (IKEA traceability requirement)')
        )
        print("  ✅ Added: label_production_date")
    
    # Production week (IKEA week format: WW-YYYY)
    if 'production_week' not in existing_mo_columns:
        op.add_column('manufacturing_orders', 
            sa.Column('production_week', sa.String(10), nullable=True, index=True,
                     comment='Production week in IKEA format (e.g., 05-2026)')
        )
        print("  ✅ Added: production_week")
    
    # Destination country (shipping destination)
    if 'destination_country' not in existing_mo_columns:
        op.add_column('manufacturing_orders', 
            sa.Column('destination_country', sa.String(50), nullable=True, index=True,
                     comment='Shipping destination country')
        )
        print("  ✅ Added: destination_country")
    
    # Traceability code (batch + date code for recall)
    if 'traceability_code' not in existing_mo_columns:
        op.add_column('manufacturing_orders', 
            sa.Column('traceability_code', sa.String(50), nullable=True, unique=True, index=True,
                     comment='Unique traceability code (batch + date) for product recall')
        )
        print("  ✅ Added: traceability_code")
    
    # Target shipment date (when product should ship to customer)
    if 'target_shipment_date' not in existing_mo_columns:
        op.add_column('manufacturing_orders', 
            sa.Column('target_shipment_date', sa.Date(), nullable=True,
                     comment='Target date for shipment to customer/IKEA')
        )
        print("  ✅ Added: target_shipment_date")
    
    # ========================================================================
    # 2. WORK ORDERS - Add Department-Level Date Tracking
    # ========================================================================
    print("\n🏭 Adding datestamp fields to work_orders...")
    
    existing_wo_columns = [col['name'] for col in inspector.get_columns('work_orders')]
    
    # Planned start date for this WO
    if 'planned_start_date' not in existing_wo_columns:
        op.add_column('work_orders', 
            sa.Column('planned_start_date', sa.Date(), nullable=True,
                     comment='Planned date when this WO should start')
        )
        print("  ✅ Added: planned_start_date")
    
    # Actual start date
    if 'actual_start_date' not in existing_wo_columns:
        op.add_column('work_orders', 
            sa.Column('actual_start_date', sa.Date(), nullable=True,
                     comment='Actual date when this WO started production')
        )
        print("  ✅ Added: actual_start_date")
    
    # Planned completion date
    if 'planned_completion_date' not in existing_wo_columns:
        op.add_column('work_orders', 
            sa.Column('planned_completion_date', sa.Date(), nullable=True,
                     comment='Planned date when this WO should complete')
        )
        print("  ✅ Added: planned_completion_date")
    
    # Actual completion date
    if 'actual_completion_date' not in existing_wo_columns:
        op.add_column('work_orders', 
            sa.Column('actual_completion_date', sa.Date(), nullable=True,
                     comment='Actual date when this WO was completed')
        )
        print("  ✅ Added: actual_completion_date")
    
    # Production date (date stamped on this department's output)
    if 'production_date_stamp' not in existing_wo_columns:
        op.add_column('work_orders', 
            sa.Column('production_date_stamp', sa.Date(), nullable=True,
                     comment='Date stamp for this department output (for traceability)')
        )
        print("  ✅ Added: production_date_stamp")
    
    # ========================================================================
    # 3. SPKs - Add Date Tracking (Legacy compatibility)
    # ========================================================================
    print("\n📄 Adding datestamp fields to spks...")
    
    existing_spk_columns = [col['name'] for col in inspector.get_columns('spks')]
    
    if 'planned_start_date' not in existing_spk_columns:
        op.add_column('spks', 
            sa.Column('planned_start_date', sa.Date(), nullable=True,
                     comment='Planned production start date')
        )
        print("  ✅ Added: planned_start_date to spks")
    
    if 'actual_start_date' not in existing_spk_columns:
        op.add_column('spks', 
            sa.Column('actual_start_date', sa.Date(), nullable=True,
                     comment='Actual production start date')
        )
        print("  ✅ Added: actual_start_date to spks")
    
    if 'production_date_stamp' not in existing_spk_columns:
        op.add_column('spks', 
            sa.Column('production_date_stamp', sa.Date(), nullable=True,
                     comment='Production date stamp for traceability')
        )
        print("  ✅ Added: production_date_stamp to spks")
    
    # ========================================================================
    # 4. Create Indexes for Performance
    # ========================================================================
    print("\n📑 Creating indexes for date queries...")
    
    existing_mo_indexes = [idx['name'] for idx in inspector.get_indexes('manufacturing_orders')]
    existing_wo_indexes = [idx['name'] for idx in inspector.get_indexes('work_orders')]
    
    if 'idx_mo_production_week' not in existing_mo_indexes:
        op.create_index('idx_mo_production_week', 'manufacturing_orders', ['production_week'])
        print("  ✅ Created index: idx_mo_production_week")
    
    if 'idx_mo_label_date' not in existing_mo_indexes:
        op.create_index('idx_mo_label_date', 'manufacturing_orders', ['label_production_date'])
        print("  ✅ Created index: idx_mo_label_date")
    
    if 'idx_mo_planned_date' not in existing_mo_indexes:
        op.create_index('idx_mo_planned_date', 'manufacturing_orders', ['planned_production_date'])
        print("  ✅ Created index: idx_mo_planned_date")
    
    if 'idx_wo_planned_start' not in existing_wo_indexes:
        op.create_index('idx_wo_planned_start', 'work_orders', ['planned_start_date'])
        print("  ✅ Created index: idx_wo_planned_start")
    
    if 'idx_wo_actual_start' not in existing_wo_indexes:
        op.create_index('idx_wo_actual_start', 'work_orders', ['actual_start_date'])
        print("  ✅ Created index: idx_wo_actual_start")
    
    print("\n✅ Migration completed successfully!")
    print("\n📊 Summary:")
    print("   • 9 fields added to manufacturing_orders (incl. po_id link)")
    print("   • 5 fields added to work_orders")
    print("   • 3 fields added to spks")
    print("   • 5 indexes created for performance")
    print("\n🎯 IKEA Compliance: READY FOR PRODUCTION!")
    print("📦 PO → MO → BOM Explosion → SPK/WO flow enabled!")


def downgrade():
    """Remove datestamp fields"""
    
    print("\n⏪ Rolling back datestamp fields...")
    
    # Drop indexes
    op.drop_index('idx_wo_actual_start', 'work_orders')
    op.drop_index('idx_wo_planned_start', 'work_orders')
    op.drop_index('idx_mo_planned_date', 'manufacturing_orders')
    op.drop_index('idx_mo_label_date', 'manufacturing_orders')
    op.drop_index('idx_mo_production_week', 'manufacturing_orders')
    
    # Drop SPK columns
    op.drop_column('spks', 'production_date_stamp')
    op.drop_column('spks', 'actual_start_date')
    op.drop_column('spks', 'planned_start_date')
    
    # Drop Work Order columns
    op.drop_column('work_orders', 'production_date_stamp')
    op.drop_column('work_orders', 'actual_completion_date')
    op.drop_column('work_orders', 'planned_completion_date')
    op.drop_column('work_orders', 'actual_start_date')
    op.drop_column('work_orders', 'planned_start_date')
    
    # Drop Manufacturing Order columns
    op.drop_column('manufacturing_orders', 'target_shipment_date')
    op.drop_column('manufacturing_orders', 'traceability_code')
    op.drop_column('manufacturing_orders', 'destination_country')
    op.drop_column('manufacturing_orders', 'production_week')
    op.drop_column('manufacturing_orders', 'label_production_date')
    op.drop_column('manufacturing_orders', 'actual_production_end_date')
    op.drop_column('manufacturing_orders', 'actual_production_start_date')
    op.drop_column('manufacturing_orders', 'planned_production_date')
    op.drop_column('manufacturing_orders', 'po_id')
    
    print("✅ Rollback completed!")
