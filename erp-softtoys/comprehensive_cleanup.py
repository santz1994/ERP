"""
Comprehensive Database Cleanup Script
Removes ALL dummy/test data except users and system tables

User Request: "Kita tidak membuat baju, hapus semua database dummy, kecuali user, user roles, atau yang berhubungan dengan user"

Tables to CLEAN (DELETE all rows):
- products (1450 rows) - Dummy IKEA articles and materials
- bom_headers (1299 rows) - Dummy BOMs
- bom_details (1340 rows) - Cascades from bom_headers
- manufacturing_orders (5 rows)
- work_orders (15 rows)
- partners (0 rows - already empty)
- All production transaction tables

Tables to KEEP:
- users (15 rows) - User accounts
- categories (8 rows) - Product categories (reusable)
- System tables (alembic_version, etc.)
"""

import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from sqlalchemy.orm import Session
from sqlalchemy import text
from app.core.database import SessionLocal


def comprehensive_cleanup(db: Session):
    """Remove ALL dummy data except users and system tables."""
    
    print("=" * 80)
    print("COMPREHENSIVE DATABASE CLEANUP")
    print("=" * 80)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Tables to clean with estimated current counts
    cleanup_plan = [
        ("work_orders", "Work Orders (WO/SPK)"),
        ("spk_daily_production", "SPK Daily Production Records"),
        ("spk_material_allocation", "SPK Material Allocations"),
        ("spk_material_allocations", "SPK Material Allocations (alt table)"),
        ("spk_material_allocation_old", "SPK Material Allocations (old)"),
        ("spk_production_completion", "SPK Production Completions"),
        ("spk_edit_history", "SPK Edit History"),
        ("spk_modifications", "SPK Modifications"),
        ("spks", "SPKs (Production Orders)"),
        ("manufacturing_orders", "Manufacturing Orders (MO)"),
        ("mo_material_consumption", "MO Material Consumption"),
        ("bom_details", "BOM Details (cascades from headers)"),
        ("bom_wip_routing", "BOM WIP Routing"),
        ("bom_variants", "BOM Variants"),
        ("bom_headers", "BOM Headers"),
        ("products", "Products (Articles + Materials)"),
        ("partners", "Partners (Suppliers/Customers/Subcons)"),
        ("purchase_order_lines", "Purchase Order Lines"),
        ("purchase_orders", "Purchase Orders"),
        ("sales_order_lines", "Sales Order Lines"),
        ("sales_orders", "Sales Orders"),
        ("stock_moves", "Stock Movements"),
        ("stock_quants", "Stock Quantities"),
        ("stock_lots", "Stock Lots"),
        ("material_debt", "Material Debt Records"),
        ("material_debt_settlement", "Material Debt Settlements"),
        ("material_requests", "Material Requests"),
        ("qc_inspections", "QC Inspections"),
        ("qc_lab_tests", "QC Lab Tests"),
        ("rework_requests", "Rework Requests"),
        ("rework_materials", "Rework Materials"),
        ("finishing_inputs_outputs", "Finishing Inputs/Outputs"),
        ("finishing_material_consumptions", "Finishing Material Consumptions"),
        ("warehouse_finishing_stocks", "Warehouse Finishing Stocks"),
        ("wip_transfer_logs", "WIP Transfer Logs"),
        ("transfer_logs", "Transfer Logs"),
        ("pallet_barcodes", "Pallet Barcodes"),
        ("kanban_cards", "Kanban Cards"),
        ("kanban_boards", "Kanban Boards"),
        ("kanban_rules", "Kanban Rules"),
        ("line_occupancy", "Line Occupancy"),
        ("segregasi_acknowledgement", "Segregasi Acknowledgements"),
        ("defect_categories", "Defect Categories"),
        ("approval_requests", "Approval Requests"),
        ("approval_steps", "Approval Steps"),
    ]
    
    print("📋 CLEANUP PLAN:")
    print("-" * 80)
    print(f"Total tables to clean: {len(cleanup_plan)}")
    print()
    
    # Count current rows
    print("📊 CURRENT DATA (Before Cleanup):")
    print("-" * 80)
    total_rows_before = 0
    for table, description in cleanup_plan:
        try:
            result = db.execute(text(f"SELECT COUNT(*) FROM {table}"))
            count = result.scalar()
            if count > 0:
                indicator = "🔴" if count > 100 else "🟡" if count > 0 else "⚪"
                print(f"{indicator} {table:<40} {count:>6} rows - {description}")
                total_rows_before += count
        except Exception as e:
            print(f"⚠️  {table:<40} Error: {str(e)}")
    
    print("-" * 80)
    print(f"📊 TOTAL ROWS TO DELETE: {total_rows_before}")
    print()
    
    # Confirmation
    print("⚠️  WARNING: This action is IRREVERSIBLE!")
    print("    All production data will be deleted permanently.")
    print("    Only users and system tables will remain.")
    print()
    response = input("❓ Type 'DELETE ALL' to confirm: ")
    
    if response.strip() != "DELETE ALL":
        print("\n❌ Cleanup cancelled by user.")
        return False
    
    print()
    print("=" * 80)
    print("🗑️  DELETING DATA...")
    print("=" * 80)
    
    # Execute cleanup in correct order (respect foreign keys)
    deleted_total = 0
    for table, description in cleanup_plan:
        try:
            result = db.execute(text(f"DELETE FROM {table}"))
            deleted = result.rowcount
            if deleted > 0:
                print(f"✅ Deleted {deleted:>6} rows from {table}")
                deleted_total += deleted
            db.commit()
        except Exception as e:
            print(f"❌ Error deleting from {table}: {str(e)}")
            db.rollback()
            continue
    
    print()
    print("=" * 80)
    print("✅ CLEANUP COMPLETE!")
    print("=" * 80)
    print(f"📊 Total rows deleted: {deleted_total}")
    print()
    
    # Verify remaining data
    print("📊 REMAINING DATA (After Cleanup):")
    print("-" * 80)
    
    verify_tables = [
        ("users", "User Accounts"),
        ("categories", "Product Categories"),
        ("products", "Products"),
        ("bom_headers", "BOM Headers"),
        ("manufacturing_orders", "Manufacturing Orders"),
        ("work_orders", "Work Orders"),
    ]
    
    for table, description in verify_tables:
        try:
            result = db.execute(text(f"SELECT COUNT(*) FROM {table}"))
            count = result.scalar()
            indicator = "✅" if table in ["users", "categories"] else "⚪"
            print(f"{indicator} {table:<30} {count:>6} rows - {description}")
        except Exception as e:
            print(f"⚠️  {table:<30} Error")
    
    print("-" * 80)
    print()
    print("✅ Database is now clean and ready for masterdata import!")
    print("📦 Next step: Import masterdata from docs/Masterdata/*.xlsx")
    print()
    
    return True


def main():
    """Main execution."""
    db = SessionLocal()
    try:
        success = comprehensive_cleanup(db)
        if success:
            print("=" * 80)
            print("✅ SUCCESS: Database cleaned successfully!")
            print("=" * 80)
    except KeyboardInterrupt:
        print("\n\n❌ Cleanup interrupted by user.")
        db.rollback()
    except Exception as e:
        print(f"\n❌ FATAL ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    main()
