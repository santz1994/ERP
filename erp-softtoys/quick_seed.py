"""Quick seeder with simple passwords for testing"""
import bcrypt

from app.core.database import SessionLocal
from app.core.models.users import User, UserRole


def hash_simple(password: str) -> str:
    """Simple bcrypt hash"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

db = SessionLocal()

# Create admin only
admin = User(
    username="admin",
    email="admin@qutykarunia.com",
    hashed_password=hash_simple("Admin@123"),
    full_name="System Administrator",
    role=UserRole.ADMIN,
    is_active=True,
    is_verified=True
)

db.add(admin)
db.commit()
print("✅ Admin created: admin / Admin@123")
db.close()
