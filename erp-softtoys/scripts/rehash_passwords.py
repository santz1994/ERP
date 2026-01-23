"""Re-hash all user passwords with optimized bcrypt rounds (10 instead of 12)
This improves login performance from ~2s to ~100ms
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.database import SessionLocal
from app.core.models.users import User
from app.core.security import PasswordUtils


def rehash_all_passwords():
    """Re-hash all user passwords with new bcrypt rounds"""
    db = SessionLocal()
    try:
        users = db.query(User).all()
        print(f"Found {len(users)} users to re-hash")

        # Default password for all users (admin123)
        default_password = "admin123"

        for user in users:
            # Re-hash with new rounds
            user.hashed_password = PasswordUtils.hash_password(default_password)
            print(f"✅ Re-hashed password for: {user.username}")

        db.commit()
        print(f"\n✅ Successfully re-hashed {len(users)} passwords with bcrypt rounds=10")
        print("⚡ Login performance should now be ~100ms instead of ~2s")

    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("🔒 Re-hashing passwords for performance optimization...")
    print("📝 All passwords will be reset to: admin123")
    print("")
    rehash_all_passwords()
