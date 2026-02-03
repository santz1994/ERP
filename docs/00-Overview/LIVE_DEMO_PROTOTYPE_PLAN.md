# 🚀 LIVE DEMO PROTOTYPE - COMPREHENSIVE DEVELOPMENT PLAN
**ERP Quty Karunia - From Scratch to Live Deployment**

**Prepared for**: Management PT Quty Karunia  
**Prepared by**: IT Developer Expert Team  
**Date**: 3 Februari 2026  
**Target**: Functional Live Demo in 4-6 Weeks  
**AI Assistant**: Claude Sonnet 4.5

---

## 📋 EXECUTIVE SUMMARY

### ✅ FEASIBILITY ASSESSMENT

**Apakah bisa dibuat?** → **YA, SANGAT BISA!** ✅

**Kondisi Existing**:
- ✅ Backend FastAPI sudah ada (struktur lengkap, 27 database models)
- ✅ Frontend React+Vite sudah ada (struktur lengkap)
- ✅ Database schema sudah defined (27 tables dengan relationships)
- ✅ Docker setup sudah ada (docker-compose.yml)
- ✅ Dokumentasi lengkap (200+ pages technical spec)
- ⚠️ **Yang kurang**: Implementation detail & testing

**Assessment**: Infrastruktur 70% siap, butuh development 30% untuk prototype working

---

## 🎯 PROTOTYPE SCOPE

### What We Will Build

#### ✅ Core Features (MVP - Minimum Viable Product)
1. **Authentication & Authorization**
   - Login/Logout
   - JWT Token management
   - Role-based access (3 roles: Admin, PPIC, Production)

2. **Manufacturing Order (MO) Management**
   - Create MO dari PPIC
   - View MO list & detail
   - Dual Trigger System (PARTIAL → RELEASED)

3. **SPK (Work Order) System**
   - Auto-generate SPK dari MO
   - View SPK per department
   - SPK status tracking

4. **Production Input (Simplified)**
   - Daily production input (Cutting only)
   - Good/Defect/Rework tracking
   - Real-time progress update

5. **Dashboard (Basic)**
   - MO overview
   - Production progress
   - Material status

#### 🔄 Out of Scope (Phase 2+)
- Mobile Android app
- QC Lab tests
- Material debt system
- Warehouse finishing 2-stage
- PDF/Excel reports
- Barcode scanner
- Email notifications

---

## 🗓️ DEVELOPMENT TIMELINE

### Phase 1: Foundation Setup (Week 1-2) - 10 days
**Goal**: Environment ready, database seeded, basic auth working

| Day | Task | Output |
|-----|------|--------|
| 1-2 | Setup development environment | Docker running, DB migrated |
| 3-4 | Implement authentication system | Login working, JWT tokens |
| 5-6 | Seed master data | Users, products, categories |
| 7-8 | Build basic UI shell | Dashboard layout, routing |
| 9-10 | Integration testing | Auth flow end-to-end |

### Phase 2: Core Features (Week 3-4) - 14 days
**Goal**: MO → SPK → Production flow working

| Day | Task | Output |
|-----|------|--------|
| 11-12 | MO creation API + UI | PPIC dapat create MO |
| 13-14 | SPK auto-generation | MO trigger SPK creation |
| 15-16 | SPK listing & detail | Department view SPK |
| 17-18 | Daily production input | Cutting admin input data |
| 19-20 | Dashboard metrics | Real-time progress display |
| 21-22 | Material allocation (basic) | BOM consumption tracking |
| 23-24 | Integration testing | Full flow MO → SPK → Input |

### Phase 3: Testing & Deployment (Week 5-6) - 12 days
**Goal**: Bug-free, deployed to staging, ready for trial

| Day | Task | Output |
|-----|------|--------|
| 25-27 | End-to-end testing | All scenarios tested |
| 28-29 | Bug fixing & polish | No critical bugs |
| 30-31 | User acceptance testing | Stakeholder feedback |
| 32-33 | Deploy to staging server | Accessible via URL |
| 34-35 | Documentation & training | User manual ready |
| 36 | GO LIVE Demo | Trial with real users |

**Total**: 36 working days = **~6 weeks**

---

## 🏗️ TECHNICAL ARCHITECTURE

### Stack Confirmation (No Changes)

```
┌─────────────────────────────────────────────────────┐
│  LIVE DEMO PROTOTYPE ARCHITECTURE                   │
└─────────────────────────────────────────────────────┘

CLIENT LAYER
├─ React 18 + TypeScript + Vite
├─ Tailwind CSS
├─ React Query (API calls)
└─ Zustand (State management)

API GATEWAY
└─ Nginx (Optional for demo, direct FastAPI OK)

BACKEND LAYER
├─ FastAPI 0.109+
├─ Python 3.11
├─ SQLAlchemy 2.0+
├─ Pydantic 2.5+
└─ PostgreSQL 15

INFRASTRUCTURE
├─ Docker Compose
├─ PostgreSQL 15
├─ Redis 7 (Session & cache)
└─ (Optional) Prometheus for monitoring
```

### Database Schema (27 Tables - Simplified for MVP)

**MVP Tables** (15 tables prioritized):
```
1. users                      # Authentication
2. categories                 # Master data
3. products                   # Master data
4. partners                   # Suppliers
5. manufacturing_orders       # Core: MO
6. spks                       # Core: SPK
7. work_orders               # Core: Work orders
8. spk_daily_production      # Core: Daily input
9. bom_headers               # Material planning
10. bom_details              # Material components
11. stock_quants             # Inventory
12. stock_moves              # Inventory movements
13. locations                # Warehouse locations
14. purchase_orders          # PO tracking
15. sales_orders             # Customer orders
```

**Phase 2+ Tables** (12 tables deferred):
- bom_variants, qc_inspections, material_debts, spk_modifications, etc.

---

## 📦 PHASE 1: FOUNDATION SETUP (Week 1-2)

### Day 1-2: Environment Setup

#### Task 1.1: Docker Environment
```powershell
# File: setup-demo-env.ps1
# Clone repository (if fresh start)
git clone <repo-url> d:\Project\ERP2026-Demo
cd d:\Project\ERP2026-Demo

# Copy environment template
Copy-Item .env.example .env

# Edit .env for demo configuration
# DB_HOST=postgres
# DB_NAME=erp_demo
# DB_USER=erp_user
# DB_PASSWORD=demo123
# JWT_SECRET=demo_secret_key_change_in_production

# Start Docker services
docker-compose up -d postgres redis

# Wait for DB ready
Start-Sleep -Seconds 10

# Check services
docker-compose ps
```

#### Task 1.2: Database Migration
```powershell
# File: migrate-demo-db.ps1
cd d:\Project\ERP2026-Demo\erp-softtoys

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Run migrations (Alembic)
alembic upgrade head

# Verify tables created
python -c "from app.core.database import engine; from sqlalchemy import inspect; print(inspect(engine).get_table_names())"
```

#### Task 1.3: Seed Master Data
```python
# File: erp-softtoys/scripts/seed_demo_data.py
"""Seed essential data for demo"""
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.core.models.users import User, UserRole
from app.core.models.products import Category, Product, Partner
from app.core.security import PasswordUtils
from datetime import datetime

def seed_users(db: Session):
    """Create demo users"""
    users_data = [
        {"username": "admin", "email": "admin@quty.com", "role": UserRole.SUPERADMIN, "password": "admin123"},
        {"username": "ppic1", "email": "ppic@quty.com", "role": UserRole.PPIC_STAFF, "password": "ppic123"},
        {"username": "cutting1", "email": "cutting@quty.com", "role": UserRole.CUTTING_ADMIN, "password": "cut123"},
        {"username": "sewing1", "email": "sewing@quty.com", "role": UserRole.SEWING_ADMIN, "password": "sew123"},
    ]
    
    for data in users_data:
        user = User(
            username=data["username"],
            email=data["email"],
            role=data["role"],
            hashed_password=PasswordUtils.hash_password(data["password"]),
            is_active=True,
            created_at=datetime.utcnow()
        )
        db.add(user)
    
    db.commit()
    print(f"✅ Created {len(users_data)} demo users")

def seed_categories(db: Session):
    """Create product categories"""
    categories = [
        {"code": "RAW", "name": "Raw Material", "type": "material"},
        {"code": "FG", "name": "Finished Goods", "type": "product"},
        {"code": "WIP", "name": "Work in Progress", "type": "semi_finished"},
    ]
    
    for cat in categories:
        category = Category(**cat)
        db.add(category)
    
    db.commit()
    print(f"✅ Created {len(categories)} categories")

def seed_products(db: Session):
    """Create sample products"""
    # Get category IDs
    cat_raw = db.query(Category).filter_by(code="RAW").first()
    cat_fg = db.query(Category).filter_by(code="FG").first()
    
    products = [
        # Raw materials
        {"default_code": "IKHR504", "name": "KOHAIR Fabric", "category_id": cat_raw.id, "uom": "YD", "price": 15000},
        {"default_code": "IKP20157", "name": "Filling Material", "category_id": cat_raw.id, "uom": "KG", "price": 45000},
        
        # Finished goods
        {"default_code": "40551542", "name": "AFTONSPARV Doll", "category_id": cat_fg.id, "uom": "PCS", "price": 85000},
    ]
    
    for prod in products:
        product = Product(**prod)
        db.add(product)
    
    db.commit()
    print(f"✅ Created {len(products)} products")

def seed_partners(db: Session):
    """Create suppliers and customers"""
    partners = [
        {"name": "IKEA Sweden", "partner_type": "customer", "email": "ikea@sweden.com"},
        {"name": "Fabric Supplier A", "partner_type": "supplier", "email": "supplier@fabric.com"},
    ]
    
    for partner in partners:
        p = Partner(**partner)
        db.add(p)
    
    db.commit()
    print(f"✅ Created {len(partners)} partners")

if __name__ == "__main__":
    db = SessionLocal()
    try:
        seed_users(db)
        seed_categories(db)
        seed_products(db)
        seed_partners(db)
        print("\n🎉 Demo data seeded successfully!")
    finally:
        db.close()
```

**Run seeding**:
```powershell
python scripts/seed_demo_data.py
```

---

### Day 3-4: Authentication System

#### Task 2.1: Backend Auth API (Already Exists!)
Check existing file: `erp-softtoys/app/api/v1/auth.py`

**Endpoints needed**:
- ✅ `POST /api/v1/auth/login` - Already implemented
- ✅ `POST /api/v1/auth/register` - Already implemented
- ✅ `GET /api/v1/auth/me` - Need to add

**Add missing endpoint**:
```python
# File: erp-softtoys/app/api/v1/auth.py
# Add this endpoint after login

@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user)
):
    """Get current logged-in user profile"""
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        role=current_user.role.value,
        is_active=current_user.is_active,
        created_at=current_user.created_at
    )
```

#### Task 2.2: Frontend Auth UI
```typescript
// File: erp-ui/frontend/src/pages/Login.tsx
import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '@/store/authStore'
import { apiClient } from '@/api/client'

export const LoginPage: React.FC = () => {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  
  const navigate = useNavigate()
  const { setUser, setToken } = useAuthStore()

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')

    try {
      const response = await apiClient.post('/auth/login', {
        username,
        password
      })

      const { access_token, user } = response.data
      
      // Store token and user
      setToken(access_token)
      setUser(user)
      
      // Redirect to dashboard
      navigate('/dashboard')
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Login failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100">
      <div className="bg-white p-8 rounded-lg shadow-md w-96">
        <h1 className="text-2xl font-bold mb-6 text-center">
          ERP Quty Karunia
        </h1>
        
        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
            {error}
          </div>
        )}

        <form onSubmit={handleLogin}>
          <div className="mb-4">
            <label className="block text-gray-700 mb-2">Username</label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full px-4 py-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
            />
          </div>

          <div className="mb-6">
            <label className="block text-gray-700 mb-2">Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-4 py-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-600 text-white py-2 rounded hover:bg-blue-700 disabled:bg-gray-400"
          >
            {loading ? 'Logging in...' : 'Login'}
          </button>
        </form>

        <div className="mt-4 text-center text-sm text-gray-600">
          <p>Demo Accounts:</p>
          <p>Admin: admin / admin123</p>
          <p>PPIC: ppic1 / ppic123</p>
        </div>
      </div>
    </div>
  )
}
```

#### Task 2.3: Auth Store (Zustand)
```typescript
// File: erp-ui/frontend/src/store/authStore.ts
import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface User {
  id: number
  username: string
  email: string
  role: string
}

interface AuthState {
  user: User | null
  token: string | null
  setUser: (user: User) => void
  setToken: (token: string) => void
  logout: () => void
  isAuthenticated: () => boolean
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      
      setUser: (user) => set({ user }),
      setToken: (token) => set({ token }),
      
      logout: () => {
        set({ user: null, token: null })
        localStorage.removeItem('auth-storage')
      },
      
      isAuthenticated: () => {
        const { token, user } = get()
        return !!token && !!user
      }
    }),
    {
      name: 'auth-storage'
    }
  )
)
```

---

### Day 5-6: Master Data Setup

**Already seeded on Day 1-2**, now create UI to view/manage:

```typescript
// File: erp-ui/frontend/src/pages/Products.tsx
import React, { useEffect, useState } from 'react'
import { apiClient } from '@/api/client'

interface Product {
  id: number
  default_code: string
  name: string
  uom: string
  price: number
}

export const ProductsPage: React.FC = () => {
  const [products, setProducts] = useState<Product[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadProducts()
  }, [])

  const loadProducts = async () => {
    try {
      const response = await apiClient.get('/products')
      setProducts(response.data)
    } catch (error) {
      console.error('Failed to load products:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) return <div>Loading...</div>

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4">Products</h1>
      
      <table className="w-full bg-white shadow-md rounded">
        <thead className="bg-gray-200">
          <tr>
            <th className="p-3 text-left">Code</th>
            <th className="p-3 text-left">Name</th>
            <th className="p-3 text-left">UOM</th>
            <th className="p-3 text-right">Price</th>
          </tr>
        </thead>
        <tbody>
          {products.map(product => (
            <tr key={product.id} className="border-t hover:bg-gray-50">
              <td className="p-3">{product.default_code}</td>
              <td className="p-3">{product.name}</td>
              <td className="p-3">{product.uom}</td>
              <td className="p-3 text-right">
                Rp {product.price.toLocaleString()}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
```

---

### Day 7-8: Basic UI Shell

#### Task 4.1: Dashboard Layout
```typescript
// File: erp-ui/frontend/src/components/Layout.tsx
import React from 'react'
import { Outlet, Link, useNavigate } from 'react-router-dom'
import { useAuthStore } from '@/store/authStore'

export const Layout: React.FC = () => {
  const { user, logout } = useAuthStore()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <header className="bg-blue-600 text-white p-4 shadow-md">
        <div className="container mx-auto flex justify-between items-center">
          <h1 className="text-xl font-bold">ERP Quty Karunia - Demo</h1>
          
          <div className="flex items-center gap-4">
            <span>{user?.username} ({user?.role})</span>
            <button
              onClick={handleLogout}
              className="bg-red-500 px-4 py-2 rounded hover:bg-red-600"
            >
              Logout
            </button>
          </div>
        </div>
      </header>

      <div className="flex">
        {/* Sidebar */}
        <aside className="w-64 bg-white shadow-md min-h-screen">
          <nav className="p-4">
            <Link to="/dashboard" className="block p-3 hover:bg-gray-100 rounded mb-2">
              📊 Dashboard
            </Link>
            
            {user?.role === 'ppic_staff' && (
              <>
                <Link to="/manufacturing-orders" className="block p-3 hover:bg-gray-100 rounded mb-2">
                  🏭 Manufacturing Orders
                </Link>
                <Link to="/spks" className="block p-3 hover:bg-gray-100 rounded mb-2">
                  📋 SPK List
                </Link>
              </>
            )}
            
            {user?.role === 'cutting_admin' && (
              <Link to="/production-input" className="block p-3 hover:bg-gray-100 rounded mb-2">
                ✍️ Production Input
              </Link>
            )}
            
            <Link to="/products" className="block p-3 hover:bg-gray-100 rounded mb-2">
              📦 Products
            </Link>
          </nav>
        </aside>

        {/* Main Content */}
        <main className="flex-1 p-6">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
```

#### Task 4.2: Router Setup
```typescript
// File: erp-ui/frontend/src/App.tsx
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { LoginPage } from './pages/Login'
import { DashboardPage } from './pages/Dashboard'
import { ProductsPage } from './pages/Products'
import { ManufacturingOrdersPage } from './pages/ManufacturingOrders'
import { Layout } from './components/Layout'
import { useAuthStore } from './store/authStore'

function PrivateRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated } = useAuthStore()
  return isAuthenticated() ? children : <Navigate to="/login" />
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        
        <Route path="/" element={<PrivateRoute><Layout /></PrivateRoute>}>
          <Route index element={<Navigate to="/dashboard" />} />
          <Route path="dashboard" element={<DashboardPage />} />
          <Route path="products" element={<ProductsPage />} />
          <Route path="manufacturing-orders" element={<ManufacturingOrdersPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}

export default App
```

---

### Day 9-10: Integration Testing Phase 1

**Test Checklist**:
- ✅ Login dengan admin/admin123
- ✅ Login dengan ppic1/ppic123
- ✅ Logout
- ✅ View products list
- ✅ Navigation antar pages
- ✅ Token refresh
- ✅ Protected routes (redirect ke login jika tidak auth)

---

## 📦 PHASE 2: CORE FEATURES (Week 3-4)

### Day 11-12: Manufacturing Order (MO) Creation

#### Task 5.1: Backend MO API
```python
# File: erp-softtoys/app/api/v1/ppic.py (already exists, verify)

@router.post("/manufacturing-order", response_model=dict)
async def create_manufacturing_order(
    mo_data: dict,
    current_user: User = Depends(require_permission("ppic.create_mo")),
    db: Session = Depends(get_db)
):
    """Create new Manufacturing Order"""
    # Validate product exists
    product = db.query(Product).filter_by(id=mo_data["product_id"]).first()
    if not product:
        raise HTTPException(404, "Product not found")
    
    # Create MO
    mo = ManufacturingOrder(
        name=f"MO-{datetime.now().strftime('%Y-%m')}-{generate_sequence()}",
        product_id=mo_data["product_id"],
        quantity=mo_data["quantity"],
        state="draft",  # Initial state
        mode="partial",  # Will upgrade to 'released' later
        created_by=current_user.id,
        created_at=datetime.utcnow()
    )
    
    db.add(mo)
    db.commit()
    db.refresh(mo)
    
    return {
        "success": True,
        "mo_id": mo.id,
        "mo_name": mo.name,
        "message": "MO created successfully"
    }
```

#### Task 5.2: Frontend MO Create Form
```typescript
// File: erp-ui/frontend/src/pages/ManufacturingOrders.tsx
import React, { useState } from 'react'
import { apiClient } from '@/api/client'

export const ManufacturingOrdersPage: React.FC = () => {
  const [showForm, setShowForm] = useState(false)
  const [formData, setFormData] = useState({
    product_id: '',
    quantity: 0
  })

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault()
    
    try {
      await apiClient.post('/ppic/manufacturing-order', formData)
      alert('MO created successfully!')
      setShowForm(false)
      // Refresh list
    } catch (error) {
      alert('Failed to create MO')
    }
  }

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Manufacturing Orders</h1>
        <button
          onClick={() => setShowForm(true)}
          className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
        >
          + Create MO
        </button>
      </div>

      {showForm && (
        <div className="bg-white p-6 rounded shadow-md mb-6">
          <h2 className="text-xl font-semibold mb-4">New Manufacturing Order</h2>
          <form onSubmit={handleCreate}>
            <div className="mb-4">
              <label className="block mb-2">Product</label>
              <select
                value={formData.product_id}
                onChange={(e) => setFormData({ ...formData, product_id: e.target.value })}
                className="w-full px-4 py-2 border rounded"
                required
              >
                <option value="">Select Product</option>
                <option value="1">AFTONSPARV Doll</option>
              </select>
            </div>

            <div className="mb-4">
              <label className="block mb-2">Quantity</label>
              <input
                type="number"
                value={formData.quantity}
                onChange={(e) => setFormData({ ...formData, quantity: parseInt(e.target.value) })}
                className="w-full px-4 py-2 border rounded"
                required
                min="1"
              />
            </div>

            <div className="flex gap-2">
              <button
                type="submit"
                className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700"
              >
                Create
              </button>
              <button
                type="button"
                onClick={() => setShowForm(false)}
                className="bg-gray-400 text-white px-4 py-2 rounded hover:bg-gray-500"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      {/* MO List will go here */}
    </div>
  )
}
```

---

### Day 13-14: SPK Auto-Generation

#### Task 6.1: Backend SPK Service
```python
# File: erp-softtoys/app/services/spk_service.py
from sqlalchemy.orm import Session
from app.core.models.manufacturing import ManufacturingOrder, SPK, Department
from datetime import datetime

class SPKService:
    """Service for SPK auto-generation"""
    
    @staticmethod
    def generate_spks_from_mo(mo_id: int, db: Session):
        """Auto-generate SPKs when MO is created"""
        mo = db.query(ManufacturingOrder).filter_by(id=mo_id).first()
        if not mo:
            raise ValueError("MO not found")
        
        # Define departments in sequence
        departments = ["CUTTING", "SEWING", "FINISHING", "PACKING"]
        
        # Define buffer per department
        buffer_config = {
            "CUTTING": 1.10,    # +10%
            "SEWING": 1.067,    # +6.7%
            "FINISHING": 1.044, # +4.4%
            "PACKING": 1.033    # +3.3%
        }
        
        created_spks = []
        
        for dept in departments:
            buffer = buffer_config.get(dept, 1.0)
            target_qty = int(mo.quantity * buffer)
            
            spk = SPK(
                name=f"SPK-{dept[:3]}-{datetime.now().strftime('%Y-%m')}-{generate_sequence()}",
                mo_id=mo.id,
                department=dept,
                product_id=mo.product_id,
                target_quantity=target_qty,
                state="ready" if mo.mode == "released" else "locked",
                created_at=datetime.utcnow()
            )
            
            db.add(spk)
            created_spks.append(spk)
        
        db.commit()
        return created_spks
```

#### Task 6.2: Trigger SPK on MO Creation
```python
# File: erp-softtoys/app/api/v1/ppic.py
# Update create_manufacturing_order

from app.services.spk_service import SPKService

@router.post("/manufacturing-order", response_model=dict)
async def create_manufacturing_order(
    mo_data: dict,
    current_user: User = Depends(require_permission("ppic.create_mo")),
    db: Session = Depends(get_db)
):
    # ... existing MO creation code ...
    
    db.add(mo)
    db.commit()
    db.refresh(mo)
    
    # 🆕 Auto-generate SPKs
    spks = SPKService.generate_spks_from_mo(mo.id, db)
    
    return {
        "success": True,
        "mo_id": mo.id,
        "mo_name": mo.name,
        "spks_created": len(spks),
        "spk_names": [spk.name for spk in spks],
        "message": f"MO created with {len(spks)} SPKs"
    }
```

---

### Day 15-16: SPK Listing & Detail

#### Task 7.1: Backend SPK API
```python
# File: erp-softtoys/app/api/v1/spk.py (create new)
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.core.dependencies import get_db, get_current_user
from app.core.models.manufacturing import SPK
from app.core.models.users import User

router = APIRouter(prefix="/spk", tags=["SPK"])

@router.get("/list")
async def get_spk_list(
    department: str = Query(None),
    state: str = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get SPK list filtered by department/state"""
    query = db.query(SPK)
    
    if department:
        query = query.filter(SPK.department == department)
    
    if state:
        query = query.filter(SPK.state == state)
    
    spks = query.all()
    
    return {
        "total": len(spks),
        "spks": [
            {
                "id": spk.id,
                "name": spk.name,
                "department": spk.department,
                "target_quantity": spk.target_quantity,
                "state": spk.state,
                "mo_name": spk.manufacturing_order.name
            }
            for spk in spks
        ]
    }

@router.get("/{spk_id}")
async def get_spk_detail(
    spk_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get SPK detail"""
    spk = db.query(SPK).filter_by(id=spk_id).first()
    if not spk:
        raise HTTPException(404, "SPK not found")
    
    return {
        "id": spk.id,
        "name": spk.name,
        "department": spk.department,
        "target_quantity": spk.target_quantity,
        "state": spk.state,
        "mo": {
            "id": spk.mo_id,
            "name": spk.manufacturing_order.name,
            "product_name": spk.product.name
        }
    }
```

#### Task 7.2: Frontend SPK List
```typescript
// File: erp-ui/frontend/src/pages/SPKList.tsx
import React, { useEffect, useState } from 'react'
import { apiClient } from '@/api/client'
import { useAuthStore } from '@/store/authStore'

export const SPKListPage: React.FC = () => {
  const { user } = useAuthStore()
  const [spks, setSPKs] = useState([])
  const [filter, setFilter] = useState({
    department: user?.role === 'cutting_admin' ? 'CUTTING' : '',
    state: ''
  })

  useEffect(() => {
    loadSPKs()
  }, [filter])

  const loadSPKs = async () => {
    try {
      const params = new URLSearchParams()
      if (filter.department) params.append('department', filter.department)
      if (filter.state) params.append('state', filter.state)
      
      const response = await apiClient.get(`/spk/list?${params}`)
      setSPKs(response.data.spks)
    } catch (error) {
      console.error('Failed to load SPKs:', error)
    }
  }

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4">SPK List</h1>

      {/* Filters */}
      <div className="bg-white p-4 rounded shadow mb-4 flex gap-4">
        <div>
          <label className="block text-sm mb-1">Department</label>
          <select
            value={filter.department}
            onChange={(e) => setFilter({ ...filter, department: e.target.value })}
            className="px-3 py-2 border rounded"
          >
            <option value="">All</option>
            <option value="CUTTING">Cutting</option>
            <option value="SEWING">Sewing</option>
            <option value="FINISHING">Finishing</option>
            <option value="PACKING">Packing</option>
          </select>
        </div>

        <div>
          <label className="block text-sm mb-1">State</label>
          <select
            value={filter.state}
            onChange={(e) => setFilter({ ...filter, state: e.target.value })}
            className="px-3 py-2 border rounded"
          >
            <option value="">All</option>
            <option value="ready">Ready</option>
            <option value="in_progress">In Progress</option>
            <option value="done">Done</option>
            <option value="locked">Locked</option>
          </select>
        </div>
      </div>

      {/* SPK Table */}
      <table className="w-full bg-white shadow-md rounded">
        <thead className="bg-gray-200">
          <tr>
            <th className="p-3 text-left">SPK Name</th>
            <th className="p-3 text-left">Department</th>
            <th className="p-3 text-left">MO</th>
            <th className="p-3 text-right">Target</th>
            <th className="p-3 text-center">State</th>
            <th className="p-3 text-center">Actions</th>
          </tr>
        </thead>
        <tbody>
          {spks.map((spk: any) => (
            <tr key={spk.id} className="border-t hover:bg-gray-50">
              <td className="p-3">{spk.name}</td>
              <td className="p-3">{spk.department}</td>
              <td className="p-3">{spk.mo_name}</td>
              <td className="p-3 text-right">{spk.target_quantity} pcs</td>
              <td className="p-3 text-center">
                <span className={`px-2 py-1 rounded text-sm ${
                  spk.state === 'ready' ? 'bg-green-200' :
                  spk.state === 'in_progress' ? 'bg-yellow-200' :
                  spk.state === 'done' ? 'bg-blue-200' :
                  'bg-gray-200'
                }`}>
                  {spk.state}
                </span>
              </td>
              <td className="p-3 text-center">
                <button className="text-blue-600 hover:underline">
                  View
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
```

---

### Day 17-18: Daily Production Input

#### Task 8.1: Backend Production Input API
```python
# File: erp-softtoys/app/api/v1/production/daily_input.py (already exists!)
# Verify and enhance

@router.post("/input")
async def create_daily_production(
    data: dict,
    current_user: User = Depends(require_permission("production.input")),
    db: Session = Depends(get_db)
):
    """Create daily production input"""
    spk = db.query(SPK).filter_by(id=data["spk_id"]).first()
    if not spk:
        raise HTTPException(404, "SPK not found")
    
    # Validate quantities
    if data["good_qty"] + data["defect_qty"] != data["total_output"]:
        raise HTTPException(400, "Good + Defect must equal Total Output")
    
    # Create daily production record
    daily_prod = SPKDailyProduction(
        spk_id=data["spk_id"],
        production_date=data["production_date"],
        shift=data.get("shift", "DAY"),
        good_qty=data["good_qty"],
        defect_qty=data["defect_qty"],
        rework_qty=data.get("rework_qty", 0),
        input_by=current_user.id,
        created_at=datetime.utcnow()
    )
    
    db.add(daily_prod)
    
    # Update SPK progress
    total_good = db.query(func.sum(SPKDailyProduction.good_qty))\
        .filter_by(spk_id=spk.id).scalar() or 0
    total_good += data["good_qty"]
    
    spk.actual_quantity = total_good
    spk.state = "done" if total_good >= spk.target_quantity else "in_progress"
    
    db.commit()
    
    return {
        "success": True,
        "message": "Production input recorded",
        "spk_progress": f"{total_good}/{spk.target_quantity}"
    }
```

#### Task 8.2: Frontend Production Input Form
```typescript
// File: erp-ui/frontend/src/pages/ProductionInput.tsx
import React, { useState } from 'react'
import { apiClient } from '@/api/client'

export const ProductionInputPage: React.FC = () => {
  const [formData, setFormData] = useState({
    spk_id: '',
    production_date: new Date().toISOString().split('T')[0],
    shift: 'DAY',
    good_qty: 0,
    defect_qty: 0,
    rework_qty: 0
  })

  const totalOutput = formData.good_qty + formData.defect_qty

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    try {
      await apiClient.post('/production/daily-input/input', {
        ...formData,
        total_output: totalOutput
      })
      
      alert('Production input recorded!')
      // Reset form
      setFormData({
        ...formData,
        good_qty: 0,
        defect_qty: 0,
        rework_qty: 0
      })
    } catch (error) {
      alert('Failed to record production')
    }
  }

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4">Daily Production Input</h1>

      <div className="bg-white p-6 rounded shadow-md max-w-2xl">
        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label className="block mb-2">SPK</label>
            <select
              value={formData.spk_id}
              onChange={(e) => setFormData({ ...formData, spk_id: e.target.value })}
              className="w-full px-4 py-2 border rounded"
              required
            >
              <option value="">Select SPK</option>
              {/* Load SPKs from API */}
            </select>
          </div>

          <div className="mb-4">
            <label className="block mb-2">Production Date</label>
            <input
              type="date"
              value={formData.production_date}
              onChange={(e) => setFormData({ ...formData, production_date: e.target.value })}
              className="w-full px-4 py-2 border rounded"
              required
            />
          </div>

          <div className="mb-4">
            <label className="block mb-2">Shift</label>
            <select
              value={formData.shift}
              onChange={(e) => setFormData({ ...formData, shift: e.target.value })}
              className="w-full px-4 py-2 border rounded"
            >
              <option value="DAY">Day Shift</option>
              <option value="NIGHT">Night Shift</option>
            </select>
          </div>

          <div className="grid grid-cols-3 gap-4 mb-4">
            <div>
              <label className="block mb-2">Good Qty</label>
              <input
                type="number"
                value={formData.good_qty}
                onChange={(e) => setFormData({ ...formData, good_qty: parseInt(e.target.value) })}
                className="w-full px-4 py-2 border rounded"
                required
                min="0"
              />
            </div>

            <div>
              <label className="block mb-2">Defect Qty</label>
              <input
                type="number"
                value={formData.defect_qty}
                onChange={(e) => setFormData({ ...formData, defect_qty: parseInt(e.target.value) })}
                className="w-full px-4 py-2 border rounded"
                required
                min="0"
              />
            </div>

            <div>
              <label className="block mb-2">Rework Qty</label>
              <input
                type="number"
                value={formData.rework_qty}
                onChange={(e) => setFormData({ ...formData, rework_qty: parseInt(e.target.value) })}
                className="w-full px-4 py-2 border rounded"
                min="0"
              />
            </div>
          </div>

          <div className="bg-blue-50 p-4 rounded mb-4">
            <p className="text-lg font-semibold">
              Total Output: {totalOutput} pcs
            </p>
          </div>

          <button
            type="submit"
            className="bg-green-600 text-white px-6 py-3 rounded hover:bg-green-700 w-full"
          >
            Submit Production Input
          </button>
        </form>
      </div>
    </div>
  )
}
```

---

### Day 19-20: Dashboard Metrics

#### Task 9.1: Backend Dashboard API
```python
# File: erp-softtoys/app/api/v1/dashboard.py (enhance)

@router.get("/production-overview")
async def get_production_overview(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get production overview metrics"""
    
    # Total MOs
    total_mos = db.query(ManufacturingOrder).count()
    active_mos = db.query(ManufacturingOrder).filter(
        ManufacturingOrder.state.in_(["draft", "confirmed", "in_progress"])
    ).count()
    
    # Total SPKs by state
    spk_stats = db.query(
        SPK.state,
        func.count(SPK.id)
    ).group_by(SPK.state).all()
    
    # Production efficiency
    total_production = db.query(
        func.sum(SPKDailyProduction.good_qty)
    ).scalar() or 0
    
    total_defects = db.query(
        func.sum(SPKDailyProduction.defect_qty)
    ).scalar() or 0
    
    efficiency = (total_production / (total_production + total_defects) * 100) if total_production else 0
    
    return {
        "manufacturing_orders": {
            "total": total_mos,
            "active": active_mos
        },
        "spks": {
            state: count for state, count in spk_stats
        },
        "production": {
            "total_good": total_production,
            "total_defects": total_defects,
            "efficiency_percent": round(efficiency, 2)
        }
    }
```

#### Task 9.2: Frontend Dashboard
```typescript
// File: erp-ui/frontend/src/pages/Dashboard.tsx
import React, { useEffect, useState } from 'react'
import { apiClient } from '@/api/client'

export const DashboardPage: React.FC = () => {
  const [metrics, setMetrics] = useState<any>(null)

  useEffect(() => {
    loadMetrics()
  }, [])

  const loadMetrics = async () => {
    try {
      const response = await apiClient.get('/dashboard/production-overview')
      setMetrics(response.data)
    } catch (error) {
      console.error('Failed to load metrics:', error)
    }
  }

  if (!metrics) return <div>Loading...</div>

  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold mb-6">Production Dashboard</h1>

      {/* Metrics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
        <div className="bg-white p-6 rounded shadow-md">
          <h3 className="text-gray-500 text-sm mb-2">Manufacturing Orders</h3>
          <p className="text-3xl font-bold">{metrics.manufacturing_orders.active}</p>
          <p className="text-sm text-gray-500">Active / {metrics.manufacturing_orders.total} Total</p>
        </div>

        <div className="bg-white p-6 rounded shadow-md">
          <h3 className="text-gray-500 text-sm mb-2">Total Production</h3>
          <p className="text-3xl font-bold">{metrics.production.total_good}</p>
          <p className="text-sm text-gray-500">Good Pieces</p>
        </div>

        <div className="bg-white p-6 rounded shadow-md">
          <h3 className="text-gray-500 text-sm mb-2">Efficiency</h3>
          <p className="text-3xl font-bold text-green-600">
            {metrics.production.efficiency_percent}%
          </p>
          <p className="text-sm text-gray-500">
            Defects: {metrics.production.total_defects}
          </p>
        </div>
      </div>

      {/* SPK Status */}
      <div className="bg-white p-6 rounded shadow-md">
        <h3 className="text-xl font-semibold mb-4">SPK Status</h3>
        <div className="grid grid-cols-4 gap-4">
          <div className="text-center">
            <p className="text-2xl font-bold text-green-600">
              {metrics.spks.ready || 0}
            </p>
            <p className="text-sm text-gray-500">Ready</p>
          </div>
          <div className="text-center">
            <p className="text-2xl font-bold text-yellow-600">
              {metrics.spks.in_progress || 0}
            </p>
            <p className="text-sm text-gray-500">In Progress</p>
          </div>
          <div className="text-center">
            <p className="text-2xl font-bold text-blue-600">
              {metrics.spks.done || 0}
            </p>
            <p className="text-sm text-gray-500">Done</p>
          </div>
          <div className="text-center">
            <p className="text-2xl font-bold text-gray-600">
              {metrics.spks.locked || 0}
            </p>
            <p className="text-sm text-gray-500">Locked</p>
          </div>
        </div>
      </div>
    </div>
  )
}
```

---

## 🚀 PHASE 3: TESTING & DEPLOYMENT (Week 5-6)

### Day 25-27: End-to-End Testing

#### Test Scenarios
```markdown
# File: docs/testing/E2E_TEST_SCENARIOS.md

## E2E Test Scenarios for Live Demo

### Scenario 1: Complete Production Flow (Happy Path)
**Actors**: PPIC Staff, Cutting Admin

**Steps**:
1. PPIC logs in → Dashboard shows 0 active MOs
2. PPIC creates MO:
   - Product: AFTONSPARV Doll
   - Quantity: 450 pcs
   - Expected: 4 SPKs auto-generated
3. Check SPK list:
   - CUT-BODY: Ready (target 495)
   - CUT-BAJU: Ready (target 495)
   - SEW-BODY: Locked
   - SEW-BAJU: Locked
4. Cutting Admin logs in
5. Input production (Day 1):
   - SPK: CUT-BODY
   - Date: Today
   - Shift: DAY
   - Good: 100
   - Defect: 5
6. Check dashboard:
   - Total good: 100
   - Defect: 5
   - Efficiency: 95.2%
7. Input production (Day 2):
   - Good: 200
   - Defect: 10
8. Check SPK progress:
   - CUT-BODY: 300/495 (60.6%)
   - State: in_progress
9. Complete SPK (Day 3):
   - Good: 195
   - Defect: 5
10. Check SPK:
    - CUT-BODY: 495/495 (100%)
    - State: done ✅

**Expected**: Full flow successful, all data accurate

### Scenario 2: Multi-user Concurrent Access
**Actors**: PPIC Staff, 2x Cutting Admins

**Steps**:
1. PPIC creates MO (450 pcs)
2. Cutting Admin 1 inputs Day shift data
3. Cutting Admin 2 inputs Night shift data (same day)
4. Both inputs should be recorded
5. SPK progress = sum of both shifts

**Expected**: No data loss, correct aggregation

### Scenario 3: Authorization Test
**Actors**: Cutting Admin (wrong role)

**Steps**:
1. Cutting Admin tries to access PPIC menu
2. System blocks access (403 Forbidden)
3. Cutting Admin can only access Production Input

**Expected**: Role-based access working
```

#### Testing Tools
```bash
# File: tests/e2e/run_e2e_tests.sh

echo "🧪 Running E2E Tests for Live Demo"

# Backend tests
cd d:\Project\ERP2026\erp-softtoys
pytest tests/test_mo_spk_flow.py -v

# Frontend tests (manual for demo)
echo "Manual testing checklist:"
echo "1. Login as admin ✓"
echo "2. Login as ppic1 ✓"
echo "3. Create MO ✓"
echo "4. Check SPK generation ✓"
echo "5. Input production ✓"
echo "6. Check dashboard ✓"
```

---

### Day 28-29: Bug Fixing & Polish

**Common Issues to Fix**:
1. Token expiration (add refresh token logic)
2. Form validation (client & server side)
3. Loading states (skeleton screens)
4. Error handling (user-friendly messages)
5. Mobile responsive (tablet minimum)
6. Date timezone handling
7. Number formatting (thousand separators)

---

### Day 30-31: User Acceptance Testing (UAT)

#### UAT Checklist
```markdown
# File: docs/testing/UAT_CHECKLIST.md

## User Acceptance Testing Checklist

### Functionality
- [ ] Login works smoothly
- [ ] MO creation is intuitive
- [ ] SPK auto-generation is visible
- [ ] Production input form is clear
- [ ] Dashboard shows real-time data
- [ ] Logout works properly

### Usability
- [ ] UI is clean and professional
- [ ] Navigation is logical
- [ ] Forms have clear labels
- [ ] Error messages are helpful
- [ ] Loading indicators are present
- [ ] Mobile tablet view works

### Performance
- [ ] Page load < 2 seconds
- [ ] API response < 500ms
- [ ] No lag when typing
- [ ] Dashboard refreshes quickly

### Security
- [ ] Passwords are hidden
- [ ] Unauthorized access blocked
- [ ] Session timeout works
- [ ] JWT tokens expire properly
```

---

### Day 32-33: Deploy to Staging

#### Deployment Script
```powershell
# File: deploy-staging.ps1
Write-Host "🚀 Deploying ERP Demo to Staging Server" -ForegroundColor Green

# Configuration
$SERVER_IP = "192.168.1.100"  # Change to actual server
$SERVER_USER = "ubuntu"
$PROJECT_PATH = "/var/www/erp-demo"

Write-Host "Step 1: Building Docker images..." -ForegroundColor Yellow
docker-compose -f docker-compose.staging.yml build

Write-Host "Step 2: Pushing to registry..." -ForegroundColor Yellow
docker-compose -f docker-compose.staging.yml push

Write-Host "Step 3: Deploying to server..." -ForegroundColor Yellow
ssh $SERVER_USER@$SERVER_IP "cd $PROJECT_PATH && docker-compose pull && docker-compose up -d"

Write-Host "Step 4: Running database migrations..." -ForegroundColor Yellow
ssh $SERVER_USER@$SERVER_IP "cd $PROJECT_PATH && docker-compose exec backend alembic upgrade head"

Write-Host "Step 5: Seeding demo data..." -ForegroundColor Yellow
ssh $SERVER_USER@$SERVER_IP "cd $PROJECT_PATH && docker-compose exec backend python scripts/seed_demo_data.py"

Write-Host "✅ Deployment complete!" -ForegroundColor Green
Write-Host "Access at: http://$SERVER_IP" -ForegroundColor Cyan
```

#### Staging Environment Config
```yaml
# File: docker-compose.staging.yml
version: '3.8'

services:
  backend:
    image: erp-backend:latest
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://erp_user:demo123@postgres:5432/erp_demo
      - JWT_SECRET=${JWT_SECRET}
      - ENVIRONMENT=staging
    depends_on:
      - postgres
      - redis

  frontend:
    image: erp-frontend:latest
    ports:
      - "80:80"
    environment:
      - VITE_API_URL=http://${SERVER_IP}:8000/api/v1

  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=erp_demo
      - POSTGRES_USER=erp_user
      - POSTGRES_PASSWORD=demo123
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

volumes:
  postgres_data:
```

---

### Day 34-35: Documentation & Training

#### User Manual
```markdown
# File: docs/USER_MANUAL_DEMO.md

# 📖 ERP QUTY KARUNIA - USER MANUAL (Demo Version)

## 🎯 Quick Start

### 1. Accessing the System
- URL: http://192.168.1.100 (staging server)
- Demo accounts:
  - **Admin**: admin / admin123
  - **PPIC**: ppic1 / ppic123
  - **Cutting**: cutting1 / cut123

### 2. Login Process
1. Enter username
2. Enter password
3. Click "Login"
4. You'll see the dashboard

### 3. Creating Manufacturing Order (PPIC Only)
1. Click "Manufacturing Orders" in sidebar
2. Click "+ Create MO" button
3. Select product: AFTONSPARV Doll
4. Enter quantity: 450
5. Click "Create"
6. System auto-generates 4 SPKs

### 4. Viewing SPKs
1. Click "SPK List" in sidebar
2. Filter by department (optional)
3. Click "View" to see details

### 5. Input Daily Production (Cutting Admin)
1. Click "Production Input" in sidebar
2. Select SPK from dropdown
3. Enter production date
4. Select shift (Day/Night)
5. Enter quantities:
   - Good qty: Number of good pieces
   - Defect qty: Number of defective pieces
   - Rework qty: Number being reworked
6. Check total output (auto-calculated)
7. Click "Submit Production Input"

### 6. Viewing Dashboard
- Dashboard shows real-time metrics:
  - Active Manufacturing Orders
  - Total Production (good pieces)
  - Efficiency percentage
  - SPK status breakdown

## ⚠️ Important Notes
- This is a DEMO version (MVP)
- Some features are not yet implemented
- Data is for testing only
- System resets every week

## 🆘 Troubleshooting
- **Can't login**: Check username/password
- **SPK not showing**: Check if you selected correct department filter
- **Production not saving**: Ensure all required fields are filled
- **Dashboard not updating**: Refresh the page
```

---

### Day 36: GO LIVE Demo

#### Launch Checklist
```markdown
# File: docs/GOLIVE_CHECKLIST.md

## 🚀 GO LIVE CHECKLIST

### Pre-Launch (1 hour before)
- [ ] Verify server is running
- [ ] Test all demo accounts
- [ ] Clear test data
- [ ] Seed fresh demo data
- [ ] Test complete flow once
- [ ] Prepare backup server (if available)
- [ ] Have developer on standby

### During Demo
- [ ] Welcome stakeholders
- [ ] Explain demo scope (MVP)
- [ ] Walk through Scenario 1 (Happy Path)
- [ ] Let stakeholders try hands-on
- [ ] Note feedback & questions
- [ ] Address concerns immediately

### Post-Demo
- [ ] Collect feedback forms
- [ ] Document bug reports
- [ ] Schedule follow-up meeting
- [ ] Plan Phase 2 features
- [ ] Celebrate success! 🎉
```

---

## 📊 RESOURCE REQUIREMENTS

### Development Team
| Role | Time Allocation | Responsibility |
|------|----------------|----------------|
| **Backend Developer** | Full-time (36 days) | FastAPI, database, APIs |
| **Frontend Developer** | Full-time (36 days) | React UI, integration |
| **QA Tester** | Part-time (10 days) | Testing, bug reporting |
| **DevOps Engineer** | Part-time (5 days) | Deployment, server setup |
| **Project Manager** | Part-time (36 days) | Coordination, reporting |

### Infrastructure
| Resource | Specification | Cost Estimate |
|----------|--------------|---------------|
| **Dev Laptop** | 16GB RAM, i7, 500GB SSD | Existing |
| **Staging Server** | 4 vCPU, 8GB RAM, 100GB SSD | $50/month |
| **PostgreSQL DB** | Included in server | $0 |
| **Domain Name** | erp-demo.qutykarunia.com | $10/year |
| **SSL Certificate** | Let's Encrypt | $0 |

**Total Monthly Cost**: ~$50 USD (Rp 800,000)

---

## 🎯 SUCCESS CRITERIA

### Demo is Successful If:
1. ✅ Login works for all 3 roles
2. ✅ PPIC dapat create MO
3. ✅ SPK auto-generated (4 SPKs)
4. ✅ Cutting admin dapat input produksi
5. ✅ Dashboard menampilkan data real-time
6. ✅ No critical bugs during demo
7. ✅ Stakeholders satisfied (70%+ approval)
8. ✅ System accessible 24/7 during trial period

---

## 🚧 RISK MITIGATION

### Potential Risks
| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| **Database crash during demo** | HIGH | LOW | Backup DB daily, have restore script ready |
| **Server downtime** | HIGH | MEDIUM | Setup backup server, monitoring alerts |
| **Critical bug found** | MEDIUM | HIGH | Extensive testing Phase 3, hotfix plan |
| **User confusion (complex UI)** | MEDIUM | MEDIUM | User manual, training session |
| **Incomplete features** | LOW | LOW | Clear MVP scope, Phase 2 roadmap |
| **Performance issues** | MEDIUM | MEDIUM | Load testing, optimize queries |

---

## 📅 NEXT STEPS AFTER DEMO

### Phase 2 Features (Week 7-12)
1. **Warehouse Module**
   - Material receiving
   - Stock tracking
   - FIFO logic

2. **Quality Control**
   - Lab tests
   - Inline inspection
   - Segregation handling

3. **Advanced SPK**
   - SPK editing with approval
   - Material debt system
   - Rework tracking

4. **Reporting**
   - PDF export
   - Excel reports
   - Email notifications

5. **Mobile App**
   - Android native
   - Barcode scanner
   - Offline mode

### Phase 3: Production Rollout (Week 13-16)
1. Real data migration
2. User training (all staff)
3. Parallel run with existing system
4. Full cutover
5. Post-launch support

---

## 💡 CONCLUSION

### Summary
✅ **FEASIBLE**: Prototype dapat dibuat dalam 6 minggu  
✅ **REALISTIC**: Menggunakan existing infrastructure 70%  
✅ **COST-EFFECTIVE**: Budget minimal ($50/month hosting)  
✅ **SCALABLE**: Arsitektur siap untuk full production

### Recommendation
**LANJUTKAN DEVELOPMENT** dengan plan ini!

**Why?**
- Dokumentasi lengkap sudah tersedia
- Infrastruktur 70% sudah siap
- Team familiar dengan tech stack
- MVP scope jelas dan achievable
- Low risk, high value

### Call to Action
1. **Approve budget**: $50/month staging + development time
2. **Assign team**: Backend dev, Frontend dev, QA tester
3. **Set timeline**: Start Week 1 on Monday
4. **Schedule demo**: Week 6 Friday with stakeholders
5. **Prepare for success**: Training materials, user manual

---

**Prepared by**: IT Developer Expert Team  
**Reviewed by**: Daniel Rizaldy  
**Date**: 3 Februari 2026  
**Version**: 1.0

**Contact**: daniel@qutykarunia.com  
**Repository**: https://github.com/santz1994/ERP

---

🚀 **READY TO BUILD THE FUTURE OF QUTY KARUNIA!**
