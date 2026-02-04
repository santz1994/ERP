"""Quick script to check admin user"""
from app.core.database import SessionLocal
from app.core.models import User

db = SessionLocal()

admin = db.query(User).filter(User.username == 'admin').first()

if admin:
    print(f'✅ Admin exists: {admin.username}')
    print(f'   Email: {admin.email}')
    print(f'   Role: {admin.role}')
    print(f'   Active: {admin.is_active}')
    print(f'   Hashed: {admin.hashed_password[:50]}...')
else:
    print('❌ Admin user not found')

db.close()
