"""Add SPK Material Allocation Table - Week 4 Implementation

Revision ID: 007_spk_material_allocation
Revises: 006_add_production_datestamp_fields
Create Date: 2026-02-04 10:00:00.000000

Description:
This migration adds the spk_material_allocation table to track material
allocation and consumption per Work Order. This is the core of Week 3-4
implementation for material integration with WO system.

Features:
1. Material reservation (soft allocation)
2. Material deduction tracking (hard consumption)
3. Variance tracking (planned vs actual)
4. FIFO stock allocation support
5. Material shortage alerts

Author: IT Developer Expert
Motto: "Kegagalan adalah kesuksesan yang tertunda!"
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB
from datetime import datetime


# revision identifiers, used by Alembic.
revision = '007_spk_material_allocation'
down_revision = '006_add_datestamp'  # Fixed: matches actual revision ID from 006 file
branch_labels = None
depends_on = None


def upgrade():
    """Add spk_material_allocation table"""
    
    print("\n" + "="*80)
    print("📦 ADDING SPK MATERIAL ALLOCATION TABLE")
    print("="*80)
    
    # Get inspector to check existing tables
    from alembic import context
    conn = context.get_bind()
    inspector = sa.inspect(conn)
    
    existing_tables = inspector.get_table_names()
    
    # ========================================================================
    # 1. CREATE spk_material_allocation TABLE
    # ========================================================================
    
    if 'spk_material_allocation' not in existing_tables:
        print("\n📋 Creating spk_material_allocation table...")
        
        op.create_table(
            'spk_material_allocation',
            
            # Primary Key
            sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
            
            # Foreign Keys
            sa.Column('wo_id', sa.Integer(), sa.ForeignKey('work_orders.id', ondelete='CASCADE'),
                     nullable=False, index=True,
                     comment='Work Order yang menggunakan material ini'),
            sa.Column('material_id', sa.Integer(), sa.ForeignKey('products.id', ondelete='RESTRICT'),
                     nullable=False, index=True,
                     comment='Material/Raw Material yang dialokasikan'),
            
            # Planned Allocation (from BOM)
            sa.Column('planned_qty', sa.DECIMAL(10, 4), nullable=False,
                     comment='Jumlah material yang direncanakan (dari BOM)'),
            sa.Column('planned_uom', sa.String(20), nullable=False, default='PCS',
                     comment='Unit of Measure (YD, KG, PCS, CM, etc.)'),
            
            # Reserved (Soft Allocation)
            sa.Column('reserved_qty', sa.DECIMAL(10, 4), nullable=True,
                     comment='Jumlah yang di-reserve dari warehouse (soft lock)'),
            sa.Column('reserved_at', sa.DateTime(), nullable=True,
                     comment='Timestamp kapan material di-reserve'),
            sa.Column('reserved_by', sa.Integer(), sa.ForeignKey('users.id'), nullable=True,
                     comment='User yang melakukan reservation (biasanya PPIC)'),
            
            # Consumed (Hard Deduction)
            sa.Column('consumed_qty', sa.DECIMAL(10, 4), nullable=True, default=0,
                     comment='Jumlah yang sudah benar-benar digunakan (hard deduction)'),
            sa.Column('consumed_at', sa.DateTime(), nullable=True,
                     comment='Timestamp kapan material digunakan (WO started)'),
            sa.Column('consumed_by', sa.Integer(), sa.ForeignKey('users.id'), nullable=True,
                     comment='User yang memulai WO (biasanya department admin)'),
            
            # Variance Tracking
            sa.Column('variance_qty', sa.DECIMAL(10, 4), nullable=True,
                     comment='Selisih planned vs consumed (positive = over, negative = under)'),
            sa.Column('variance_pct', sa.DECIMAL(5, 2), nullable=True,
                     comment='Persentase variance'),
            sa.Column('variance_reason', sa.Text(), nullable=True,
                     comment='Alasan jika ada variance signifikan (>10%)'),
            
            # Stock Allocation Details (FIFO tracking)
            sa.Column('stock_allocation_details', JSONB, nullable=True,
                     comment='JSON array of stock lots used (FIFO tracking)'),
            # Example JSON:
            # [
            #   {"lot_id": 123, "qty": 50, "location": "WH-A-01"},
            #   {"lot_id": 124, "qty": 20, "location": "WH-A-02"}
            # ]
            
            # Status
            sa.Column('status', sa.String(20), nullable=False, default='PLANNED',
                     comment='Status: PLANNED, RESERVED, CONSUMED, VARIANCE_PENDING'),
            
            # Metadata
            sa.Column('notes', sa.Text(), nullable=True,
                     comment='Catatan tambahan (optional)'),
            sa.Column('created_at', sa.DateTime(), default=datetime.utcnow, nullable=False),
            sa.Column('updated_at', sa.DateTime(), default=datetime.utcnow, 
                     onupdate=datetime.utcnow, nullable=False),
            
            # Constraints
            sa.CheckConstraint('planned_qty >= 0', name='check_planned_qty_positive'),
            sa.CheckConstraint('reserved_qty >= 0', name='check_reserved_qty_positive'),
            sa.CheckConstraint('consumed_qty >= 0', name='check_consumed_qty_positive'),
            sa.UniqueConstraint('wo_id', 'material_id', name='uq_wo_material')
        )
        
        print("  ✅ Table created: spk_material_allocation")
        
        # Create indexes for performance
        print("\n📑 Creating indexes...")
        op.create_index('idx_spk_mat_alloc_wo', 'spk_material_allocation', ['wo_id'])
        op.create_index('idx_spk_mat_alloc_material', 'spk_material_allocation', ['material_id'])
        op.create_index('idx_spk_mat_alloc_status', 'spk_material_allocation', ['status'])
        op.create_index('idx_spk_mat_alloc_consumed_at', 'spk_material_allocation', ['consumed_at'])
        print("  ✅ Created 4 indexes")
        
    else:
        print("⚠️ Table spk_material_allocation already exists, skipping...")
    
    # ========================================================================
    # 2. ADD MATERIAL SHORTAGE LOG TABLE (for alerts)
    # ========================================================================
    
    if 'material_shortage_logs' not in existing_tables:
        print("\n⚠️ Creating material_shortage_logs table...")
        
        op.create_table(
            'material_shortage_logs',
            
            sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column('wo_id', sa.Integer(), sa.ForeignKey('work_orders.id'), nullable=False, index=True),
            sa.Column('material_id', sa.Integer(), sa.ForeignKey('products.id'), nullable=False, index=True),
            
            sa.Column('required_qty', sa.DECIMAL(10, 4), nullable=False,
                     comment='Jumlah material yang dibutuhkan'),
            sa.Column('available_qty', sa.DECIMAL(10, 4), nullable=False,
                     comment='Jumlah material yang tersedia di warehouse'),
            sa.Column('shortage_qty', sa.DECIMAL(10, 4), nullable=False,
                     comment='Selisih (required - available)'),
            sa.Column('shortage_pct', sa.DECIMAL(5, 2), nullable=False,
                     comment='Persentase shortage'),
            
            sa.Column('severity', sa.String(20), nullable=False, default='MEDIUM',
                     comment='CRITICAL, HIGH, MEDIUM, LOW'),
            sa.Column('status', sa.String(20), nullable=False, default='OPEN',
                     comment='OPEN, RESOLVED, CANCELLED'),
            
            sa.Column('detected_at', sa.DateTime(), default=datetime.utcnow, nullable=False,
                     comment='Kapan shortage detected'),
            sa.Column('resolved_at', sa.DateTime(), nullable=True,
                     comment='Kapan shortage resolved'),
            sa.Column('resolved_by', sa.Integer(), sa.ForeignKey('users.id'), nullable=True),
            
            sa.Column('notes', sa.Text(), nullable=True),
            sa.Column('created_at', sa.DateTime(), default=datetime.utcnow, nullable=False)
        )
        
        print("  ✅ Table created: material_shortage_logs")
        
        # Indexes
        op.create_index('idx_shortage_wo', 'material_shortage_logs', ['wo_id'])
        op.create_index('idx_shortage_material', 'material_shortage_logs', ['material_id'])
        op.create_index('idx_shortage_status', 'material_shortage_logs', ['status'])
        op.create_index('idx_shortage_severity', 'material_shortage_logs', ['severity'])
        print("  ✅ Created 4 indexes")
        
    else:
        print("⚠️ Table material_shortage_logs already exists, skipping...")
    
    print("\n" + "="*80)
    print("✅ MIGRATION 007 COMPLETE!")
    print("="*80)
    print("\nNext Steps:")
    print("1. ✅ Run integration service (material_allocation_service.py)")
    print("2. ✅ Test auto-allocation when WO is created")
    print("3. ✅ Test auto-deduction when WO starts")
    print("4. ✅ Test shortage alerts")
    print("\n")


def downgrade():
    """Revert changes"""
    
    print("\n" + "="*80)
    print("⚠️ REVERTING MIGRATION 007")
    print("="*80)
    
    # Drop tables (reverse order)
    op.drop_table('material_shortage_logs')
    print("  ✅ Dropped: material_shortage_logs")
    
    op.drop_table('spk_material_allocation')
    print("  ✅ Dropped: spk_material_allocation")
    
    print("\n✅ Migration 007 reverted successfully\n")
