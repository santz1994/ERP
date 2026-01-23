"""Database Utility Scripts for ERP System
========================================
Useful database inspection and maintenance utilities.

Author: Daniel - IT Developer Senior
Date: 2026-01-22

Usage:
    python scripts/database_utils.py --check-tables
    python scripts/database_utils.py --check-enums
    python scripts/database_utils.py --verify-mvs
    python scripts/database_utils.py --refresh-mvs
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import inspect, text

from app.core.database import SessionLocal


def check_tables():
    """Check all database tables"""
    db = SessionLocal()
    try:
        inspector = inspect(db.bind)
        tables = inspector.get_table_names()

        print("\n=== Database Tables ===")
        print(f"Total tables: {len(tables)}\n")

        for table in sorted(tables):
            print(f"  - {table}")

        return tables
    finally:
        db.close()


def check_enums():
    """Check enum values in key tables"""
    db = SessionLocal()
    try:
        queries = {
            'manufacturing_orders.state': "SELECT DISTINCT state FROM manufacturing_orders ORDER BY state",
            'work_orders.status': "SELECT DISTINCT status FROM work_orders ORDER BY status",
            'qc_inspections.status': "SELECT DISTINCT status FROM qc_inspections ORDER BY status",
            'products.type': "SELECT DISTINCT type FROM products ORDER BY type"
        }

        print("\n=== Enum Values ===")
        for name, query in queries.items():
            try:
                result = db.execute(text(query))
                values = [row[0] for row in result.fetchall()]
                print(f"\n{name}:")
                for val in values:
                    print(f"  - '{val}'")
            except Exception as e:
                print(f"\n{name}: Error - {str(e)[:100]}")

    finally:
        db.close()


def verify_materialized_views():
    """Verify materialized views exist and have data"""
    db = SessionLocal()
    try:
        # Check which views exist
        result = db.execute(text("""
            SELECT matviewname FROM pg_matviews 
            WHERE schemaname = 'public' 
            AND matviewname LIKE 'mv_%'
            ORDER BY matviewname
        """))
        views = [row[0] for row in result.fetchall()]

        print("\n=== Materialized Views ===")
        print(f"Total views: {len(views)}\n")

        for view in views:
            # Check row count
            try:
                count_result = db.execute(text(f"SELECT COUNT(*) FROM {view}"))
                count = count_result.fetchone()[0]
                print(f"OK {view}: {count} rows")
            except Exception as e:
                print(f"ERROR {view}: {str(e)[:100]}")

        return views
    finally:
        db.close()


def refresh_materialized_views():
    """Refresh all materialized views"""
    db = SessionLocal()
    try:
        views = [
            'mv_dashboard_stats',
            'mv_production_dept_status',
            'mv_qc_pass_rate',
            'mv_inventory_status'
        ]

        print("\n=== Refreshing Materialized Views ===")
        for view in views:
            try:
                print(f"Refreshing {view}...")
                db.execute(text(f"REFRESH MATERIALIZED VIEW {view}"))
                db.commit()
                print(f"  OK {view}")
            except Exception as e:
                print(f"  ERROR {view}: {str(e)[:100]}")
                db.rollback()

        print("\nRefresh complete!")
    finally:
        db.close()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Database utility scripts')
    parser.add_argument('--check-tables', action='store_true', help='List all tables')
    parser.add_argument('--check-enums', action='store_true', help='Check enum values')
    parser.add_argument('--verify-mvs', action='store_true', help='Verify materialized views')
    parser.add_argument('--refresh-mvs', action='store_true', help='Refresh materialized views')
    parser.add_argument('--all', action='store_true', help='Run all checks')

    args = parser.parse_args()

    if args.all or args.check_tables:
        check_tables()

    if args.all or args.check_enums:
        check_enums()

    if args.all or args.verify_mvs:
        verify_materialized_views()

    if args.refresh_mvs:
        refresh_materialized_views()

    if not any(vars(args).values()):
        parser.print_help()
