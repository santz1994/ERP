"""Reset admin user password"""
from app.core.database import SessionLocal
from app.core.models import User
from app.core.models.users import UserRole
from app.core.security import PasswordUtils

db = SessionLocal()

# Find or create admin
admin = db.query(User).filter(User.username == 'admin').first()

# Generate proper hash for "admin123"
correct_hash = PasswordUtils.hash_password("admin123")
print(f'✅ Generated new hash:')
print(f'   Length: {len(correct_hash)} chars')
print(f'   Hash: {correct_hash}')

if admin:
    print(f'\n🔄 Updating existing admin user...')
    admin.hashed_password = correct_hash
    admin.is_active = True
    admin.login_attempts = 0
    admin.locked_until = None
else:
    print(f'\n✨ Creating new admin user...')
    admin = User(
        username='admin',
        email='admin@qutykarunia.com',
        full_name='System Administrator',
        hashed_password=correct_hash,
        role=UserRole.ADMIN,
        is_active=True,
        is_verified=True,
        login_attempts=0
    )
    db.add(admin)

try:
    db.commit()
    print(f'✅ Admin user ready!')
    print(f'   Username: admin')
    print(f'   Password: admin123')
    print(f'   Role: {admin.role}')
except Exception as e:
    print(f'❌ Error: {str(e)}')
    db.rollback()
finally:
    db.close()
