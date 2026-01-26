"""Comprehensive User Seeder - Creates demo users for all 22 roles
Usage: python seed_all_users.py
"""
from app.core.database import SessionLocal
from app.core.models.users import User, UserRole
from app.core.security import PasswordUtils

# Default password for all users (TESTING ONLY)
DEFAULT_PASSWORD = "password123"

# User data for all 22 roles
USERS_DATA = [
    # Level 0: System Development
    {"username": "developer", "email": "developer@qutykarunia.com", "full_name": "System Developer", "role": UserRole.DEVELOPER},

    # Level 1: System Administration
    {"username": "superadmin", "email": "superadmin@qutykarunia.com", "full_name": "Super Administrator", "role": UserRole.SUPERADMIN},

    # Level 2: Top Management
    {"username": "manager", "email": "manager@qutykarunia.com", "full_name": "General Manager", "role": UserRole.MANAGER},
    {"username": "finance_mgr", "email": "finance.manager@qutykarunia.com", "full_name": "Finance Manager", "role": UserRole.FINANCE_MANAGER},

    # Level 3: System Admin
    {"username": "admin", "email": "admin@qutykarunia.com", "full_name": "System Administrator", "role": UserRole.ADMIN},

    # Level 4: Department Management
    {"username": "ppic_mgr", "email": "ppic.manager@qutykarunia.com", "full_name": "PPIC Manager", "role": UserRole.PPIC_MANAGER},
    {"username": "ppic_admin", "email": "ppic.admin@qutykarunia.com", "full_name": "PPIC Admin", "role": UserRole.PPIC_ADMIN},
    {"username": "spv_cutting", "email": "spv.cutting@qutykarunia.com", "full_name": "Supervisor Cutting", "role": UserRole.SPV_CUTTING},
    {"username": "spv_sewing", "email": "spv.sewing@qutykarunia.com", "full_name": "Supervisor Sewing", "role": UserRole.SPV_SEWING},
    {"username": "spv_finishing", "email": "spv.finishing@qutykarunia.com", "full_name": "Supervisor Finishing", "role": UserRole.SPV_FINISHING},
    {"username": "wh_admin", "email": "warehouse.admin@qutykarunia.com", "full_name": "Warehouse Admin", "role": UserRole.WAREHOUSE_ADMIN},
    {"username": "qc_lab", "email": "qc.lab@qutykarunia.com", "full_name": "QC Laboratory", "role": UserRole.QC_LAB},
    {"username": "purchasing_head", "email": "purchasing.head@qutykarunia.com", "full_name": "Purchasing Head", "role": UserRole.PURCHASING_HEAD},
    {"username": "purchasing", "email": "purchasing@qutykarunia.com", "full_name": "Purchasing Officer", "role": UserRole.PURCHASING},

    # Level 5: Operations
    {"username": "operator_cut", "email": "operator.cutting@qutykarunia.com", "full_name": "Operator Cutting", "role": UserRole.OPERATOR_CUT},
    {"username": "operator_embro", "email": "operator.embroidery@qutykarunia.com", "full_name": "Operator Embroidery", "role": UserRole.OPERATOR_EMBRO},
    {"username": "operator_sew", "email": "operator.sewing@qutykarunia.com", "full_name": "Operator Sewing", "role": UserRole.OPERATOR_SEW},
    {"username": "operator_finish", "email": "operator.finishing@qutykarunia.com", "full_name": "Operator Finishing", "role": UserRole.OPERATOR_FINISH},
    {"username": "operator_pack", "email": "operator.packing@qutykarunia.com", "full_name": "Operator Packing", "role": UserRole.OPERATOR_PACK},
    {"username": "qc_inspector", "email": "qc.inspector@qutykarunia.com", "full_name": "QC Inspector", "role": UserRole.QC_INSPECTOR},
    {"username": "wh_operator", "email": "warehouse.operator@qutykarunia.com", "full_name": "Warehouse Operator", "role": UserRole.WAREHOUSE_OP},
    {"username": "security", "email": "security@qutykarunia.com", "full_name": "Security Guard", "role": UserRole.SECURITY},
]


def seed_all_users():
    """Create all demo users for testing"""
    db = SessionLocal()
    created_count = 0
    existing_count = 0

    try:
        print("\n" + "="*70)
        print("SEEDING ALL USERS (22 ROLES)")
        print("="*70 + "\n")

        for user_data in USERS_DATA:
            # Check if user exists
            existing_user = db.query(User).filter(
                User.username == user_data["username"]
            ).first()

            if existing_user:
                print(f"⏭️  {user_data['username']:20} - Already exists (skipped)")
                existing_count += 1
                continue

            # Create new user
            # Truncate password to 72 bytes (bcrypt limit)
            truncated_password = DEFAULT_PASSWORD[:72]
            hashed_password = PasswordUtils.hash_password(truncated_password)
            new_user = User(
                username=user_data["username"],
                email=user_data["email"],
                hashed_password=hashed_password,
                full_name=user_data["full_name"],
                role=user_data["role"],
                is_active=True,
                is_verified=True
            )

            db.add(new_user)
            db.commit()
            db.refresh(new_user)

            print(f"✅ {user_data['username']:20} - Created ({user_data['role'].value})")
            created_count += 1

        print("\n" + "="*70)
        print("SUMMARY:")
        print(f"  ✅ Created: {created_count} users")
        print(f"  ⏭️  Skipped: {existing_count} users (already exist)")
        print(f"  📊 Total:   {created_count + existing_count} users")
        print("="*70 + "\n")

        if created_count > 0:
            print("🔐 DEFAULT CREDENTIALS (ALL USERS):")
            print("-" * 70)
            print(f"Password for ALL users: {DEFAULT_PASSWORD}")
            print("-" * 70)
            print(f"{'Role':<25} {'Username':<20}")
            print("-" * 70)
            print(f"{'Admin (Full Access)':<25} {'admin':<20}")
            print(f"{'PPIC Manager':<25} {'ppic_mgr':<20}")
            print(f"{'Warehouse Admin':<25} {'wh_admin':<20}")
            print(f"{'Supervisor Cutting':<25} {'spv_cutting':<20}")
            print(f"{'Operator Cutting':<25} {'operator_cut':<20}")
            print(f"{'Operator Embroidery':<25} {'operator_embro':<20}")
            print(f"{'QC Inspector':<25} {'qc_inspector':<20}")
            print("-" * 70)
            print("\n⚠️  SECURITY WARNING:")
            print(f"   Default password '{DEFAULT_PASSWORD}' for ALL users!")
            print("   Change these passwords in production!")
            print("   These are DEMO credentials for testing only.\n")

    except Exception as e:
        db.rollback()
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    seed_all_users()
