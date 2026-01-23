"""Test User Seeding Script
Phase 16 Week 4 - Day 4
Purpose: Create test users with various roles for PBAC testing

Usage:
    python seed_test_users.py

Creates 9 test users:
    - admin_test (ADMIN) - All permissions
    - manager_test (MANAGER) - View-only
    - cutting_op_test (OPERATOR) - Cutting department
    - cutting_spv_test (SPV_CUTTING) - Cutting supervisor
    - sewing_op_test (OPERATOR_SEWING) - Sewing operator
    - sewing_spv_test (SPV_SEWING) - Sewing supervisor
    - qc_inspector_test (QC_INSPECTOR) - QC specific
    - ppic_manager_test (PPIC_MANAGER) - PPIC manager
    - no_perms_test (CUSTOM_ROLE) - Zero permissions
"""

import asyncio
import os
import sys
from datetime import datetime

from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.config import settings
from app.models import User

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Test users configuration
TEST_USERS = [
    {
        "username": "admin_test",
        "email": "admin@test.com",
        "password": "Admin123!",
        "role": "ADMIN",
        "department": "Admin",
        "full_name": "Test Administrator",
        "description": "Full system access - all 36 permissions"
    },
    {
        "username": "manager_test",
        "email": "manager@test.com",
        "password": "Manager123!",
        "role": "MANAGER",
        "department": "PPIC",
        "full_name": "Test Manager",
        "description": "View-only permissions for testing read-only access"
    },
    {
        "username": "cutting_op_test",
        "email": "cutting_op@test.com",
        "password": "Cutting123!",
        "role": "OPERATOR",
        "department": "Cutting",
        "full_name": "Test Cutting Operator",
        "description": "Cutting department permissions only (6 perms)"
    },
    {
        "username": "cutting_spv_test",
        "email": "cutting_spv@test.com",
        "password": "CuttingSPV123!",
        "role": "SPV_CUTTING",
        "department": "Cutting",
        "full_name": "Test Cutting Supervisor",
        "description": "Cutting supervisor - inherits operator permissions + SPV perms"
    },
    {
        "username": "sewing_op_test",
        "email": "sewing_op@test.com",
        "password": "Sewing123!",
        "role": "OPERATOR_SEWING",
        "department": "Sewing",
        "full_name": "Test Sewing Operator",
        "description": "Sewing department permissions (6 perms)"
    },
    {
        "username": "sewing_spv_test",
        "email": "sewing_spv@test.com",
        "password": "SewingSPV123!",
        "role": "SPV_SEWING",
        "department": "Sewing",
        "full_name": "Test Sewing Supervisor",
        "description": "Sewing supervisor - inherits operator permissions"
    },
    {
        "username": "qc_inspector_test",
        "email": "qc@test.com",
        "password": "QC123!",
        "role": "QC_INSPECTOR",
        "department": "QC",
        "full_name": "Test QC Inspector",
        "description": "QC-specific permissions including sewing.inline_qc"
    },
    {
        "username": "ppic_manager_test",
        "email": "ppic_mgr@test.com",
        "password": "PPIC123!",
        "role": "PPIC_MANAGER",
        "department": "PPIC",
        "full_name": "Test PPIC Manager",
        "description": "PPIC permissions including ppic.approve_mo"
    },
    {
        "username": "no_perms_test",
        "email": "none@test.com",
        "password": "None123!",
        "role": "CUSTOM_ROLE",
        "department": "Test",
        "full_name": "Test No Permissions",
        "description": "Zero permissions - for testing access denial"
    }
]


async def seed_test_users():
    """Create test users for PBAC testing"""
    # Create async engine
    engine = create_async_engine(
        settings.DATABASE_URL.replace('postgresql://', 'postgresql+asyncpg://'),
        echo=False
    )

    # Create async session
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        print("🧪 Creating test users for PBAC testing...")
        print("=" * 70)

        created_count = 0
        skipped_count = 0

        for user_data in TEST_USERS:
            # Check if user exists
            from sqlalchemy import select
            result = await session.execute(
                select(User).where(User.username == user_data["username"])
            )
            existing_user = result.scalar_one_or_none()

            if existing_user:
                print(f"⏭️  SKIP: {user_data['username']} (already exists)")
                skipped_count += 1
                continue

            # Create new user
            hashed_password = pwd_context.hash(user_data["password"])

            new_user = User(
                username=user_data["username"],
                email=user_data["email"],
                password_hash=hashed_password,
                role=user_data["role"],
                department=user_data["department"],
                full_name=user_data.get("full_name", user_data["username"]),
                is_active=True,
                created_at=datetime.utcnow()
            )

            session.add(new_user)
            created_count += 1

            print(f"✅ CREATE: {user_data['username']}")
            print(f"   Email: {user_data['email']}")
            print(f"   Password: {user_data['password']}")
            print(f"   Role: {user_data['role']}")
            print(f"   Department: {user_data['department']}")
            print(f"   Purpose: {user_data['description']}")
            print()

        # Commit all users
        await session.commit()

        print("=" * 70)
        print("📊 Summary:")
        print(f"   Created: {created_count} users")
        print(f"   Skipped: {skipped_count} users (already exist)")
        print(f"   Total: {created_count + skipped_count} users")
        print()

        # Print login credentials
        if created_count > 0:
            print("🔑 Test User Credentials:")
            print("-" * 70)
            for user_data in TEST_USERS:
                print(f"Username: {user_data['username']:<20} Password: {user_data['password']}")
            print()

            print("📝 Quick Test Commands:")
            print("-" * 70)
            print("# Login as admin")
            print("POST /auth/login")
            print('  {"username": "admin_test", "password": "Admin123!"}')
            print()
            print("# Login as operator")
            print("POST /auth/login")
            print('  {"username": "cutting_op_test", "password": "Cutting123!"}')
            print()

            print("✅ Test users ready for PBAC testing!")
        else:
            print("ℹ️  All test users already exist. No new users created.")

    await engine.dispose()


async def delete_test_users():
    """Delete all test users (cleanup)"""
    engine = create_async_engine(
        settings.DATABASE_URL.replace('postgresql://', 'postgresql+asyncpg://'),
        echo=False
    )

    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        print("🗑️  Deleting test users...")

        deleted_count = 0

        for user_data in TEST_USERS:
            from sqlalchemy import select

            # Find user
            result = await session.execute(
                select(User).where(User.username == user_data["username"])
            )
            user = result.scalar_one_or_none()

            if user:
                await session.delete(user)
                deleted_count += 1
                print(f"❌ DELETE: {user_data['username']}")

        await session.commit()

        print(f"📊 Deleted {deleted_count} test users")

    await engine.dispose()


async def main():
    """Main entry point"""
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--delete":
        print("⚠️  DELETING ALL TEST USERS")
        confirm = input("Are you sure? (yes/no): ")
        if confirm.lower() == "yes":
            await delete_test_users()
        else:
            print("❌ Cancelled")
    else:
        await seed_test_users()


if __name__ == "__main__":
    asyncio.run(main())
