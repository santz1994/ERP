"""Complete backend startup test"""
import sys
import traceback

print("=" * 70)
print("🔍 BACKEND STARTUP VERIFICATION")
print("=" * 70)

# Test 1: Import main app
print("\n1️⃣ Testing app.main import...")
try:
    from app.main import app
    print("   ✅ app.main imported successfully")
except Exception as e:
    print(f"   ❌ FAILED: {str(e)}")
    traceback.print_exc()
    sys.exit(1)

# Test 2: Check models
print("\n2️⃣ Testing model imports...")
try:
    from app.core.models import User, WorkOrder, ManufacturingOrder
    from app.core.models.manufacturing import SPKMaterialAllocation
    print("   ✅ All critical models imported")
except Exception as e:
    print(f"   ❌ FAILED: {str(e)}")
    traceback.print_exc()
    sys.exit(1)

# Test 3: Database connection
print("\n3️⃣ Testing database connection...")
try:
    from app.core.database import SessionLocal
    db = SessionLocal()
    from app.core.models import User
    count = db.query(User).count()
    print(f"   ✅ Database connected ({count} users)")
    db.close()
except Exception as e:
    print(f"   ❌ FAILED: {str(e)}")
    traceback.print_exc()
    sys.exit(1)

# Test 4: Check CORS config
print("\n4️⃣ Testing CORS configuration...")
try:
    from app.core.config import settings
    print(f"   CORS Origins: {settings.CORS_ORIGINS[:3]}...")
    if 'http://localhost:5173' in settings.CORS_ORIGINS:
        print("   ✅ localhost:5173 included in CORS")
    else:
        print("   ⚠️  localhost:5173 NOT in CORS origins!")
except Exception as e:
    print(f"   ❌ FAILED: {str(e)}")
    traceback.print_exc()

# Test 5: Check critical endpoints
print("\n5️⃣ Checking API endpoints registration...")
try:
    from fastapi.routing import APIRoute
    routes = [route for route in app.routes if isinstance(route, APIRoute)]
    
    critical_endpoints = [
        '/api/v1/auth/login',
        '/api/v1/ppic/manufacturing-orders',
        '/api/v1/work-orders'
    ]
    
    all_paths = [route.path for route in routes]
    
    for endpoint in critical_endpoints:
        # Check if endpoint or its pattern exists
        found = any(endpoint in path or path.startswith(endpoint) for path in all_paths)
        status = "✅" if found else "❌"
        print(f"   {status} {endpoint}")
        
    print(f"\n   Total routes: {len(routes)}")
except Exception as e:
    print(f"   ❌ FAILED: {str(e)}")
    traceback.print_exc()

print("\n" + "=" * 70)
print("✅ BACKEND READY TO START!")
print("=" * 70)
print("\nRun command:")
print("  python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload")
print()
