"""
Simple script to create admin user
"""
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.core.security import PasswordUtils
from app.core.models.users import User, UserRole


def create_admin_user():
    """Create admin user if not exists"""
    db = SessionLocal()
    try:
        # Check if admin exists
        existing_admin = db.query(User).filter(User.username == "admin").first()
        if existing_admin:
            print("✅ Admin user already exists")
            return
        
        # Create admin user
        hashed_password = PasswordUtils.hash_password("Admin@123456")
        admin_user = User(
            username="admin",
            email="admin@qutykarunia.com",
            hashed_password=hashed_password,
            full_name="System Administrator",
            role=UserRole.ADMIN,
            is_active=True,
            is_verified=True
        )
        
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        
        print("✅ Admin user created successfully!")
        print(f"   Username: admin")
        print(f"   Password: Admin@123456")
        print(f"   Email: admin@qutykarunia.com")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error creating admin user: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    print("\n" + "="*50)
    print("CREATING ADMIN USER")
    print("="*50 + "\n")
    create_admin_user()
