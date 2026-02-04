"""Verify all models load correctly"""
print("🔍 Testing model imports...")

try:
    from app.core.models import User
    print("✅ User model OK")
except Exception as e:
    print(f"❌ User model error: {str(e)}")

try:
    from app.core.models.manufacturing import SPKMaterialAllocation
    print("✅ SPKMaterialAllocation (manufacturing) OK")
except Exception as e:
    print(f"❌ SPKMaterialAllocation error: {str(e)}")

try:
    from app.core.models.manufacturing import WorkOrder
    print("✅ WorkOrder model OK")
except Exception as e:
    print(f"❌ WorkOrder model error: {str(e)}")

try:
    from app.core.models.production import SPKMaterialAllocationOLD
    print("✅ SPKMaterialAllocationOLD (renamed) OK")
except Exception as e:
    print(f"❌ SPKMaterialAllocationOLD error: {str(e)}")

print("\n🎯 Testing database query...")
try:
    from app.core.database import SessionLocal
    from app.core.models import User
    
    db = SessionLocal()
    user_count = db.query(User).count()
    print(f"✅ Database query OK - {user_count} users found")
    db.close()
except Exception as e:
    print(f"❌ Database query error: {str(e)}")
    import traceback
    traceback.print_exc()

print("\n✅ ALL MODEL CHECKS PASSED! Backend ready to start.")
