#!/usr/bin/env python
"""List all test users for RBAC/PBAC/UAC testing"""

from app.core.database import SessionLocal
from app.core.models.users import User

db = SessionLocal()
users = db.query(User).order_by(User.username).all()

print('\n' + '='*70)
print('ALL TEST USERS AVAILABLE FOR RBAC/PBAC/UAC TESTING')
print('='*70)
print(f'{"Username":<20} | {"Role":<15} | {"Active":<10} | {"Email"}')
print('-'*70)

for u in users:
    status = '✅ YES' if u.is_active else '❌ NO'
    print(f'{u.username:<20} | {u.role.value:<15} | {status:<10} | {u.email}')

print('-'*70)
print(f'Total: {len(users)} users ready for testing')
print('\nDefault Password: password123')
print('='*70 + '\n')
