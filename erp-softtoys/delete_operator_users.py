"""Delete operator-level users from database"""
from app.core.database import SessionLocal
from app.core.models.users import User

db = SessionLocal()

# List of operator usernames to delete
operator_usernames = [
    'operator_cut',
    'operator_embro',
    'operator_sew',
    'operator_finish',
    'operator_pack',
    'qc_inspector',
    'wh_operator',
    'security'
]

print("🗑️ Deleting operator-level users from database...\n")
print("="*80)

deleted_count = 0

for username in operator_usernames:
    user = db.query(User).filter(User.username == username).first()
    
    if user:
        print(f"❌ Deleting: {username:20s} | {user.full_name:30s} | {user.role.value}")
        db.delete(user)
        deleted_count += 1
    else:
        print(f"⚠️  Not found: {username}")

if deleted_count > 0:
    db.commit()
    print("\n" + "="*80)
    print(f"✅ Deleted {deleted_count} operator users")
else:
    print("\n" + "="*80)
    print("ℹ️  No operator users found to delete")

# Show remaining users
print("\n📋 Remaining users in database:")
print("="*80)

remaining_users = db.query(User).order_by(User.role).all()
for user in remaining_users:
    print(f"✅ {user.username:20s} | {user.full_name:30s} | {user.role.value}")

print("\n" + "="*80)
print(f"📊 Total users: {len(remaining_users)}")

db.close()
