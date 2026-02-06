# 🎯 PROMPT: IMPLEMENTASI UI/UX ERP QUTY KARUNIA

**Target**: IT Fullstack Developer (Claude AI)  
**Project**: ERP Manufacturing System - PT Quty Karunia (Soft Toys)  
**Objective**: Implementasi lengkap UI/UX dari spesifikasi dokumen  
**Date**: 5 Februari 2026  
**Priority**: HIGH - Production Ready Implementation

---

## ⚠️ CRITICAL UPDATE - February 6, 2026

**🚨 NEW MANDATORY REFERENCE DOCUMENT ADDED! 🚨**

**File**: `NAVIGATION_INTEGRATION_AUDIT.md` (479 lines)

**CRITICAL DISCOVERY**: Navigation integration audit revealed that:
- ❌ New detail pages (CreatePOPage, QCCheckpointPage) were created WITHOUT refactoring old landing pages
- ❌ Old pages (PurchasingPage, QCPage) have DUPLICATE implementations
- ❌ No navigation flow: Dashboard → Landing → Detail
- ❌ User confusion: Which page to use?

**ACTION REQUIRED**:
Before implementing ANY new page, you MUST:
1. ✅ Read `NAVIGATION_INTEGRATION_AUDIT.md` completely
2. ✅ Check if functionality already exists in old pages
3. ✅ Refactor old pages to remove duplicates
4. ✅ Add navigation cards to create proper flow
5. ✅ Test navigation: Dashboard → Landing → Detail → Back

**REFACTORING PHASES** (from audit):
- **Phase 1**: Refactor PurchasingPage, QCPage, ReworkPage → Landing Dashboards
- **Phase 2**: Enhance department pages with navigation buttons
- **Phase 3**: Eliminate code duplication (API, schemas, utilities)
- **Phase 4**: Test backend connectivity end-to-end

**⚠️ RULE**: **NEVER create a new page without consulting NAVIGATION_INTEGRATION_AUDIT.md first!**

---

## 📋 CONTEXT & BACKGROUND

### Project Overview
Anda adalah **IT Fullstack Expert** yang ditugaskan untuk mengimplementasikan sistem ERP Manufacturing untuk PT Quty Karunia, perusahaan manufaktur soft toys yang memproduksi boneka untuk IKEA dan buyer internasional lainnya.

### Business Domain
- **Industry**: Soft Toys Manufacturing (Export Quality)
- **Scale**: Medium-sized factory dengan 6 departemen produksi
- **Complexity**: 
  - Dual Trigger Production System (PO Kain + PO Label)
  - 3 Purchasing Specialists (parallel workflow)
  - 6-Stage Production Flow (Cutting → Embroidery → Sewing → Finishing 2-stage → Packing → FG)
  - Warehouse 3-Types (Main, Finishing Internal, FG)
  - QC 4-Checkpoint dengan Rework Module
  - Material Debt Management (Negative Stock)
  - Real-time WIP tracking

### Current Tech Stack (Existing)
**Backend**:
- Python 3.11+
- FastAPI (REST API)
- PostgreSQL 15
- SQLAlchemy ORM
- Alembic (migrations)
- JWT Authentication
- Docker Compose

**Frontend** (To Be Enhanced/Rebuilt):
- React 18+ atau Next.js 14+ (pilih yang paling sesuai)
- TypeScript (mandatory)
- TailwindCSS + shadcn/ui atau Material-UI
- React Query / TanStack Query (data fetching)
- Zustand atau Redux Toolkit (state management)
- React Hook Form + Zod (form validation)
- Recharts atau Chart.js (visualisasi)
- React Router v6 (routing)

**Mobile** (Future Enhancement):
- React Native atau Flutter (untuk Barcode Scanning)
- Progressive Web App (PWA) support

---

## 📚 REFERENCE DOCUMENTS - WAJIB DIBACA

### 1. PRIMARY SPECIFICATION (CRITICAL ⚠️)
**File**: `docs/00-Overview/Logic UI/Rencana Tampilan.md` (6,200+ lines)

**Isi Dokumen**:
- ✅ Complete UI/UX specification untuk ALL modules
- ✅ Workflow diagrams dengan ASCII art visualization
- ✅ Screen mockups dengan detail layout
- ✅ Navigation structure (16 sections)
- ✅ User roles & permissions
- ✅ Business logic & validation rules
- ✅ Real-time dashboard requirements
- ✅ Mobile app specifications (Barcode scanning)
- ✅ Security & fraud prevention

**Sections** (16 total):
1. Dashboard Utama (dengan Login Screen)
2. Menu Navigasi (Complete sidebar structure)
3. Purchasing Module (3 Specialists + Dual Mode)
4. PPIC Module (MO creation, SPK auto-generation)
5. Production Module (6-Stage flow dengan calendar view)
6. Warehouse & Inventory (3-Types dengan Material Receipt UI)
7. Rework & Quality Control (NEW - 4-Checkpoint QC)
8. Masterdata (Material, BOM, Supplier, Article, etc.)
9. Reporting (Production, Purchasing, Inventory, Debt, Rework)
10. User Management (Roles, Permissions, Approval Workflow)
11. Mobile Application (Barcode scanning untuk FG)
12. Notification System (Real-time alerts)
13. Material Flow Tracking (5W1H audit trail)
14. Timeline & Gantt Chart (16-day production cycle)
15. Barcode & Label System
16. Security & Fraud Prevention

### 2. SECONDARY REFERENCES (Supporting Documents)
- `docs/00-Overview/PRESENTASI_MANAGEMENT_ERP_QUTY_KARUNIA.md` (4,642 lines) - Business context & system architecture
- `docs/00-Overview/ILUSTRASI_WORKFLOW_LENGKAP.md` (1,566 lines) - Workflow visualizations
- `docs/BOM_QUICK_GUIDE_ID.md` - BOM structure & logic
- `docs/FINISHGOOD_LABEL_SYSTEM_GUIDE.md` - Barcode & labeling system
- `docs/PHASE2A_FINISHING_2STAGE_IMPLEMENTATION_GUIDE.md` - Finishing dept 2-stage process
- `docs/PHASE2B_REWORK_QC_IMPLEMENTATION_GUIDE.md` - Rework & QC module
- `docs/SESSION_43_ENTERPRISE_UI_UX_UPGRADE.md` - UI/UX best practices

### 3. BACKEND API REFERENCES
- `erp-softtoys/app/main.py` - FastAPI main application
- `erp-softtoys/app/routers/` - API endpoints per module
- `erp-softtoys/app/models/` - Database models (SQLAlchemy)
- `erp-softtoys/app/schemas/` - Pydantic schemas (request/response)

### 4. NAVIGATION INTEGRATION AUDIT (CRITICAL ⚠️)
**File**: `NAVIGATION_INTEGRATION_AUDIT.md` (479 lines)

**⚠️ CRITICAL DISCOVERY**: This audit revealed that new detail pages (CreatePOPage, QCCheckpointPage) were created WITHOUT refactoring old landing pages, causing:
- ❌ Code duplication (old pages have their own implementations)
- ❌ Navigation disconnection (no links from landing → detail)
- ❌ User confusion (which page to use?)
- ❌ Maintenance nightmare (same code in multiple files)

**Why This Document Is MANDATORY**:
Before implementing ANY new page, you MUST first:
1. ✅ **Audit existing pages** - Check if functionality already exists
2. ✅ **Read this navigation audit** - Understand 3-tier architecture
3. ✅ **Refactor old pages** - Remove duplicates, add navigation cards
4. ✅ **Establish proper flow** - Dashboard → Landing → Detail

**Key Concepts**:
- **3-Tier Architecture**: Dashboard → Module Landing → Detail Pages
- **NavigationCard Component**: Reusable card component for linking modules
- **Landing Page Pattern**: KPIs + Status Overview + Navigation Cards
- **Zero Duplication Rule**: One implementation per functionality

**Page Categories** (from audit):
1. **Category 1**: Comprehensive Dashboards (Keep & Enhance) - PPICPage, WarehousePage
2. **Category 2**: Generic Pages (Rework → Landing) - PurchasingPage, QCPage, ReworkPage
3. **Category 3**: Department Pages (Keep as Dashboards) - CuttingPage, SewingPage, etc.
4. **Category 4**: Admin/Settings Pages (Keep as-is) - AdminUserPage, AuditTrailPage, etc.
5. **Category 5**: Utility/Special Pages - BarcodeBigButtonMode, KanbanPage, etc.

**Refactoring Phases** (from audit):
- **Phase 1 (Week 1)**: Refactor PurchasingPage, QCPage, ReworkPage → Landing Dashboards
- **Phase 2 (Week 2)**: Enhance department pages with "Input Production" buttons
- **Phase 3 (Week 2)**: Eliminate code duplication (API, schemas, utils)
- **Phase 4 (Week 3)**: Test backend connectivity end-to-end

**Success Metrics**:
- ✅ Zero code duplication across all pages
- ✅ Clear 3-tier navigation hierarchy
- ✅ Consistent UX pattern across modules
- ✅ All old pages refactored as landing dashboards
- ✅ All new detail pages accessible via navigation cards

**⚠️ IMPLEMENTATION RULE**:
**NEVER create a new page without reading NAVIGATION_INTEGRATION_AUDIT.md first!**

---

## 🎯 YOUR MISSION - IMPLEMENTATION TASKS

### PHASE 1: SETUP & FOUNDATION (Week 1)

#### Task 1.1: Project Analysis & Planning
**Action**:
1. ✅ Read `Rencana Tampilan.md` completely (ALL 6,200+ lines)
2. ✅ Understand business domain & workflows
3. ✅ Map UI specifications to implementation tasks
4. ✅ Create detailed implementation plan dengan priority
5. ✅ Setup development environment

**Deliverable**:
- Implementation roadmap document
- Task breakdown dengan time estimates
- Technical architecture diagram (Frontend components)

#### Task 1.2: Project Structure Setup
**Action**:
1. Create/refactor folder structure:
   ```
   erp-ui/frontend/
   ├── public/
   ├── src/
   │   ├── app/              # Next.js App Router (or pages/)
   │   ├── components/       # Reusable components
   │   │   ├── ui/          # shadcn/ui components
   │   │   ├── forms/       # Form components
   │   │   ├── tables/      # Data table components
   │   │   ├── charts/      # Chart components
   │   │   ├── modals/      # Modal dialogs
   │   │   └── layouts/     # Layout components
   │   ├── features/         # Feature-based modules
   │   │   ├── auth/
   │   │   ├── dashboard/
   │   │   ├── purchasing/
   │   │   ├── ppic/
   │   │   ├── production/
   │   │   ├── warehouse/
   │   │   ├── rework-qc/
   │   │   ├── masterdata/
   │   │   ├── reporting/
   │   │   └── user-management/
   │   ├── lib/              # Utilities & helpers
   │   │   ├── api.ts       # API client (axios/fetch)
   │   │   ├── hooks/       # Custom React hooks
   │   │   ├── utils/       # Utility functions
   │   │   └── validations/ # Zod schemas
   │   ├── store/            # State management (Zustand)
   │   ├── types/            # TypeScript types & interfaces
   │   ├── styles/           # Global styles (Tailwind config)
   │   └── constants/        # Constants & enums
   ├── .env.local           # Environment variables
   ├── next.config.js       # Next.js configuration
   ├── tailwind.config.js   # Tailwind configuration
   ├── tsconfig.json        # TypeScript configuration
   └── package.json         # Dependencies
   ```

2. Install dependencies:
   ```bash
   npm install next@latest react@latest react-dom@latest typescript
   npm install @tanstack/react-query axios
   npm install zustand
   npm install react-hook-form @hookform/resolvers zod
   npm install tailwindcss @tailwindcss/forms
   npm install shadcn-ui # or @mui/material
   npm install recharts date-fns lucide-react
   npm install @types/node @types/react @types/react-dom
   ```

**Deliverable**:
- Clean project structure
- All dependencies installed
- Environment configuration (API endpoints, etc.)
- README.md dengan setup instructions

#### Task 1.3: Core Infrastructure
**Action**:
1. Setup API client (`lib/api.ts`):
   - Axios instance dengan interceptors
   - JWT token management
   - Error handling (401, 403, 500)
   - Request/response logging

2. Setup authentication flow:
   - Login screen (Section 1.0 dari Rencana Tampilan)
   - JWT token storage (localStorage/cookies)
   - Protected routes (HOC/middleware)
   - Auto-refresh token mechanism
   - Session timeout handling

3. Setup global state management (Zustand):
   - User state (current user, roles, permissions)
   - Notification state (alerts, toasts)
   - UI state (sidebar open/close, theme)
   - Cache invalidation strategy

4. Setup routing:
   - Define all routes dari Menu Navigasi (Section 2)
   - Protected routes berdasarkan role
   - 404 Not Found page
   - Unauthorized page (403)

**Deliverable**:
- Working authentication system
- API client ready untuk use
- State management configured
- Routing structure complete

**⚠️ CRITICAL REMINDER - Route Configuration**:
After creating ANY new page component, you MUST:
1. Add import statement in `App.tsx` (e.g., `import NewPage from '@/pages/module/NewPage'`)
2. Add Route definition with PrivateRoute wrapper:
   ```tsx
   <Route
     path="/module/new-page"
     element={
       <PrivateRoute module="module_name">
         <ProtectedLayout>
           <NewPage />
         </ProtectedLayout>
       </PrivateRoute>
     }
   />
   ```
3. Test navigation to ensure page is accessible
4. Verify module permission access control

**Route Configuration Checklist**:
- ✅ Import added at top of App.tsx
- ✅ Route definition added in Routes section
- ✅ PrivateRoute wrapper with correct module prop
- ✅ ProtectedLayout wrapper included
- ✅ Path matches navigation links in UI
- ✅ Tested navigation flow

---

## 🔍 CODE QUALITY & REFACTORING CHECKLIST

### **⚠️ MANDATORY - Before ANY Implementation Session**

After implementing features OR before starting new work, you MUST run this comprehensive code quality check:

#### **1. DUPLICATE CODE DETECTION**

**Check for Duplicated Functions:**
```bash
# Search for common function patterns across files
grep -r "const.*=.*=>.*{" erp-ui/frontend/src/pages/
grep -r "function.*(" erp-ui/frontend/src/pages/
```

**Common Duplicates to Check:**
- ✅ API calls (should use centralized `api` from `@/api`)
- ✅ Form validation logic (should use Zod schemas from `@/lib/schemas`)
- ✅ Formatting functions (should use utilities from `@/lib/utils`)
- ✅ Status badge rendering (should use `getStatusBadge()`)
- ✅ Date formatting (should use `formatDate()`)
- ✅ Number/currency formatting (should use `formatNumber()`, `formatCurrency()`)

**Refactoring Actions:**
- Extract common logic to `src/lib/utils.ts`
- Create reusable hooks in `src/hooks/`
- Move API calls to `src/api/index.ts`
- Consolidate UI components in `src/components/ui/`

#### **2. IMPORT CONSISTENCY CHECK**

**API Imports - MUST be consistent:**
```typescript
// ✅ CORRECT (centralized)
import { api, apiClient } from '@/api'

// ❌ WRONG (scattered)
import { apiClient } from '@/api/client'
import apiClient from './client'
```

**Component Imports - Use path aliases:**
```typescript
// ✅ CORRECT
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'

// ❌ WRONG
import { Button } from '../../components/ui/button'
import { cn } from '../lib/utils'
```

**Check Command:**
```bash
# Find inconsistent API imports
grep -r "from.*api/client" erp-ui/frontend/src/pages/

# Find relative imports (should use @/ alias)
grep -r "from ['\"]\.\./" erp-ui/frontend/src/pages/
```

#### **3. TYPESCRIPT ERRORS & WARNINGS**

**Run Type Checking:**
```bash
cd erp-ui/frontend
npm run build  # Checks for TypeScript errors
npx tsc --noEmit  # Type check without build
```

**Common Issues:**
- ✅ Unused variables/imports
- ✅ Implicit `any` types
- ✅ Missing type annotations
- ✅ Type mismatches in props
- ✅ Incorrect API response types

**Fix Pattern:**
- Add proper TypeScript types to all functions
- Define interfaces for all data structures
- Use Zod schemas for runtime validation
- Export types from `@/types` or `@/lib/schemas`

#### **4. TYPOS & NAMING CONVENTIONS**

**Variable Naming Standards:**
```typescript
// ✅ CORRECT
const isLoading = useState(false)
const userData = useState<User[]>([])
const handleSubmit = () => {}
const materialStockList = []

// ❌ WRONG
const loading = useState(false)  // Not descriptive
const data = useState([])  // Too generic
const submit = () => {}  // Missing 'handle' prefix
const list = []  // Too generic
```

**Check for Common Typos:**
```bash
# Search for common misspellings
grep -ri "seperate" erp-ui/frontend/src/
grep -ri "recieve" erp-ui/frontend/src/
grep -ri "occured" erp-ui/frontend/src/
grep -ri "accross" erp-ui/frontend/src/
```

**Component/File Naming:**
- Components: PascalCase (`CreateMOPage.tsx`, `MaterialStockCard.tsx`)
- Utilities: camelCase (`formatDate.ts`, `apiClient.ts`)
- Constants: UPPER_SNAKE_CASE (`API_BASE_URL`, `MAX_RETRIES`)

#### **5. OLD/LEGACY CODE DETECTION**

**Deprecated Patterns:**
```typescript
// ❌ OLD - React Query v3
import { useQuery } from 'react-query'

// ✅ NEW - React Query v5
import { useQuery } from '@tanstack/react-query'

// ❌ OLD - Class components
class MyComponent extends React.Component {}

// ✅ NEW - Functional components with hooks
const MyComponent: React.FC = () => {}

// ❌ OLD - Axios direct calls
axios.get('/api/endpoint')

// ✅ NEW - Centralized API
api.module.method()
```

**Search for Legacy Code:**
```bash
# Find old React Query imports
grep -r "from 'react-query'" erp-ui/frontend/src/

# Find class components
grep -r "extends React.Component" erp-ui/frontend/src/

# Find direct axios calls
grep -r "axios\.(get|post|put|delete)" erp-ui/frontend/src/pages/
```

#### **6. UNUSED CODE & DEAD CODE**

**Identify Unused:**
- ✅ Unused imports (ESLint will catch these)
- ✅ Unused functions
- ✅ Unused variables
- ✅ Commented-out code blocks
- ✅ Unreachable code

**Check Command:**
```bash
# Find TODO/FIXME comments
grep -r "TODO\|FIXME\|HACK\|XXX" erp-ui/frontend/src/

# Find commented code blocks (potential dead code)
grep -r "^[[:space:]]*//.*(" erp-ui/frontend/src/
```

**Clean-up Actions:**
- Remove unused imports
- Delete commented-out code
- Remove unused functions/variables
- Convert TODOs to GitHub issues

#### **7. PERFORMANCE OPTIMIZATION**

**Check for Performance Issues:**
```typescript
// ❌ BAD - Inline function creation in render
<Button onClick={() => handleClick(id)}>

// ✅ GOOD - useCallback for stable reference
const handleClick = useCallback(() => {...}, [dependencies])

// ❌ BAD - No memoization for expensive computations
const total = items.reduce((sum, item) => sum + item.price, 0)

// ✅ GOOD - useMemo for expensive computations
const total = useMemo(() => 
  items.reduce((sum, item) => sum + item.price, 0), 
  [items]
)
```

**Optimization Checklist:**
- ✅ Use `React.memo()` for expensive components
- ✅ Use `useMemo()` for expensive calculations
- ✅ Use `useCallback()` for stable function references
- ✅ Implement virtualization for large lists (react-virtual)
- ✅ Code splitting with lazy loading

#### **8. ACCESSIBILITY (A11Y) CHECK**

**Accessibility Requirements:**
```typescript
// ✅ Proper button semantics
<button type="button" aria-label="Close">×</button>

// ✅ Form labels
<label htmlFor="email">Email</label>
<input id="email" type="email" />

// ✅ Alt text for images
<img src="..." alt="Description" />

// ✅ Keyboard navigation
<div role="button" tabIndex={0} onKeyPress={handleKeyPress}>
```

**Check Command:**
```bash
# Find buttons without aria-label or text
grep -r "<button" erp-ui/frontend/src/ | grep -v "aria-label\|children"

# Find inputs without labels
grep -r "<input" erp-ui/frontend/src/ | grep -v "label"
```

#### **9. SECURITY BEST PRACTICES**

**Security Checklist:**
- ✅ No hardcoded secrets/API keys
- ✅ Proper input sanitization
- ✅ XSS prevention (no dangerouslySetInnerHTML without sanitization)
- ✅ CSRF token handling
- ✅ Secure authentication flow

**Check for Issues:**
```bash
# Find potential XSS vulnerabilities
grep -r "dangerouslySetInnerHTML" erp-ui/frontend/src/

# Find hardcoded secrets
grep -ri "password.*=.*['\"]" erp-ui/frontend/src/
grep -ri "api_key.*=.*['\"]" erp-ui/frontend/src/
```

#### **10. TESTING COVERAGE**

**Test Requirements:**
```typescript
// ✅ Unit tests for utilities
describe('formatCurrency', () => {
  it('formats number as currency', () => {
    expect(formatCurrency(1000)).toBe('Rp 1.000')
  })
})

// ✅ Integration tests for API calls
describe('api.auth.login', () => {
  it('logs in user successfully', async () => {
    const response = await api.auth.login({ username, password })
    expect(response.token).toBeDefined()
  })
})

// ✅ Component tests
describe('Button', () => {
  it('renders with correct variant', () => {
    render(<Button variant="primary">Click</Button>)
    expect(screen.getByRole('button')).toHaveClass('btn-primary')
  })
})
```

---

### **📋 REFACTORING WORKFLOW**

**Step 1: Inventory Check**
```bash
# Count files per module
find erp-ui/frontend/src/pages -type f -name "*.tsx" | wc -l

# Check file sizes (large files may need splitting)
find erp-ui/frontend/src/pages -type f -name "*.tsx" -exec wc -l {} \; | sort -nr | head -20
```

**Step 2: Systematic Analysis**
1. Read each page file completely
2. Document duplicated logic
3. Identify inconsistent patterns
4. Note potential optimizations
5. Check for TypeScript errors

**Step 3: Create Refactoring Plan**
- Group related changes
- Prioritize by impact (high → low)
- Estimate effort per change
- Create GitHub issues for tracking

**Step 4: Implement Refactoring**
- One module at a time
- Test after each change
- Update documentation
- Run full build to verify

**Step 5: Validation**
```bash
# Build check
npm run build

# Type check
npx tsc --noEmit

# Lint check
npm run lint

# Test check
npm run test
```

---

### **🎯 REFACTORING PRIORITIES**

**Priority 1: Critical (Do First)**
- ✅ Fix TypeScript errors
- ✅ Consolidate API imports
- ✅ Remove security vulnerabilities
- ✅ Fix broken functionality

**Priority 2: High (Do Soon)**
- ✅ Extract duplicated functions
- ✅ Standardize naming conventions
- ✅ Add missing error boundaries
- ✅ Implement proper loading states

**Priority 3: Medium (Plan for Next Sprint)**
- ✅ Optimize performance (memo, callback)
- ✅ Add comprehensive tests
- ✅ Improve accessibility
- ✅ Add JSDoc comments

**Priority 4: Low (Technical Debt)**
- ✅ Code splitting
- ✅ Bundle optimization
- ✅ Progressive enhancement
- ✅ Internationalization (i18n)

---

### **✅ REFACTORING COMPLETION CHECKLIST**

Before marking refactoring as "DONE":
- [ ] All TypeScript errors fixed
- [ ] No duplicate functions across pages
- [ ] Consistent import patterns (all use `@/` aliases)
- [ ] No unused imports/variables
- [ ] All API calls use centralized `api` object
- [ ] All formatting uses utility functions
- [ ] Proper error handling in all pages
- [ ] Loading states for all async operations
- [ ] Accessibility attributes where needed
- [ ] Build passes without errors/warnings
- [ ] Documentation updated

---

### PHASE 2: CORE MODULES IMPLEMENTATION (Week 2-4)

#### Task 2.1: Dashboard Utama (Section 1)
**Reference**: `Rencana Tampilan.md` Section 1.0-1.2

**UI Components to Build**:
1. **Login Screen** (1.0):
   - Form: Username/Password dengan validation
   - Remember me checkbox
   - Forgot password link
   - Multi-language toggle (ID/EN)
   - Mobile app download links
   - Security indicators (SSL, version)

2. **Dashboard Overview** (1.1):
   - KPI Cards (6 cards): Total SPK, Material Critical, MO Terlambat, Produksi Hari Ini, QC Pending, FG Ready Ship
   - Production Progress Chart (Bar + Line + Pie)
   - Material Stock Alert dengan color coding (🟢🟡🔴⚫)
   - SPK Status Overview dengan progress bar
   - Quick Action floating buttons

3. **Dashboard by Role** (1.2):
   - PPIC Dashboard
   - Manager Dashboard
   - Director Dashboard
   - Warehouse Dashboard

**Technical Requirements**:
- Real-time data updates (React Query dengan refetchInterval)
- Responsive design (Desktop, Tablet, Mobile)
- Charts dengan Recharts atau Chart.js
- Color-coded alerts (success, warning, error, critical)
- Loading states (skeleton screens)
- Error boundaries

**Validation Rules**:
- Login: Min 3 chars username, min 6 chars password
- Session timeout: 30 minutes idle
- Auto-logout on browser close

**API Endpoints** (Backend should provide):
- `POST /api/auth/login` - User login
- `GET /api/dashboard/kpi` - KPI metrics
- `GET /api/dashboard/production-chart` - Chart data
- `GET /api/dashboard/material-alerts` - Stock alerts
- `GET /api/dashboard/spk-status` - SPK overview

**Deliverable**:
- Fully functional login screen
- Interactive dashboard dengan real-time data
- Role-based dashboard views
- Responsive layout

---

#### Task 2.2: Menu Navigasi (Section 2)
**Reference**: `Rencana Tampilan.md` Section 2

**UI Components to Build**:
1. **Sidebar Navigation**:
   - Collapsible menu (icon-only mode)
   - Multi-level menu (expandable sections)
   - Active route highlighting
   - User profile section (avatar + name + role)
   - Notification badge count
   - Logout button

2. **Breadcrumb Navigation**:
   - Auto-generated dari current route
   - Clickable untuk navigate back

3. **Top Bar**:
   - Company logo
   - Search bar (global search)
   - Notification bell (dengan dropdown)
   - User menu (Profile, Settings, Logout)
   - Language toggle (ID/EN)

**Technical Requirements**:
- Smooth animations (collapse/expand)
- Permission-based menu visibility
- Keyboard shortcuts (Ctrl+K untuk search)
- Mobile hamburger menu

**Deliverable**:
- Responsive sidebar navigation
- Breadcrumb component
- Top bar dengan notifications

---

#### Task 2.3: Purchasing Module (Section 3)
**Reference**: `Rencana Tampilan.md` Section 3.1-3.2

**Critical Features** (UNIQUE BUSINESS LOGIC):
1. **Three Purchasing Specialists** - Parallel workflow
2. **Dual-Mode PO Creation**: AUTO (BOM Explosion) vs MANUAL
3. **Dual Trigger System**: PO Kain (TRIGGER 1) + PO Label (TRIGGER 2)

**UI Components to Build**:

1. **PO List & Dashboard**:
   - Filter by Type (Kain/Label/Accessories)
   - Filter by Specialist (PURCHASING A/B/C)
   - Filter by Status (Draft/Sent/Partial/Complete)
   - Search by PO Number/Article
   - Visual workflow diagram (3 parallel streams)

2. **Create PO - Dual Mode** (CRITICAL ⚠️):

   **MODE 1: AUTO from Article (BOM Explosion)**:
   - UI Flow:
     ```
     Step 1: Select PO Type (Kain/Label/Accessories)
     Step 2: Select Article (dropdown dengan preview)
     Step 3: Input Quantity (pcs)
     Step 4: Click "Generate from BOM" button
     Step 5: System auto-populate material list
     Step 6: Review & edit materials (qty, price, supplier)
     Step 7: Submit PO
     ```
   - Validation: BOM must exist untuk selected article
   - Display: Show BOM explosion progress (loading spinner)
   - Material list: Editable table dengan inline edit

   **MODE 2: MANUAL Input**:
   - UI Flow:
     ```
     Step 1: Select PO Type
     Step 2: Click "Add Material" button (repeatable)
     Step 3: For each material:
        - Select Material Code (autocomplete)
        - Input Quantity & UOM
        - Input Unit Price
        - Select Supplier
        - Add Notes
     Step 4: Submit PO
     ```
   - Validation: At least 1 material required
   - Display: Dynamic add/remove rows

3. **PO Detail View**:
   - PO Header: PO Number, Type, Date, Supplier, Status
   - Material List Table: Material Code, Name, Qty, UOM, Price, Amount
   - Timeline: Created → Sent → Received (with dates)
   - Actions: Edit, Cancel, Mark as Received
   - Audit Trail: Who created, who approved, when

4. **PO Tracking Dashboard**:
   - Kanban Board: Draft → Sent → Partial → Complete
   - Drag & drop untuk update status
   - Color coding berdasarkan urgency
   - Lead Time indicators

**Technical Requirements**:
- BOM Explosion API call dengan loading state
- Real-time PO status updates
- Inline editing untuk material list (editable table)
- UOM conversion validation
- Supplier autocomplete dengan debounce
- Form validation dengan Zod schema
- Unsaved changes warning (modal)

**API Endpoints**:
- `GET /api/purchasing/po` - List PO dengan filters
- `POST /api/purchasing/po/create` - Create new PO
- `POST /api/purchasing/po/bom-explosion` - BOM explosion untuk AUTO mode
- `GET /api/purchasing/po/{id}` - PO detail
- `PUT /api/purchasing/po/{id}` - Update PO
- `DELETE /api/purchasing/po/{id}` - Cancel PO
- `POST /api/purchasing/po/{id}/receive` - Mark as received

**Validation Rules**:
- AUTO mode: Article + Qty > 0 required
- MANUAL mode: Min 1 material required
- Material qty: Must be > 0
- Price: Must be >= 0
- Supplier: Required untuk each material
- PO Type validation: Kain must have fabric materials only

**Deliverable**:
- PO List dengan filters & search
- Dual-Mode PO Creation form (AUTO + MANUAL)
- PO Detail view dengan actions
- PO Tracking dashboard (Kanban)

---

#### Task 2.4: PPIC Module (Section 4)
**Reference**: `Rencana Tampilan.md` Section 4

**Critical Features** (UNIQUE BUSINESS LOGIC):
1. **MO Auto-Creation from PO Label** (TRIGGER 2)
2. **PARTIAL vs RELEASED Status** (2-stage approval)
3. **SPK Auto-Generation per Department**
4. **BOM Cascade Validation** (dept to dept)
5. **Material Allocation Logic** (Buffer + Debt)

**UI Components to Build**:

1. **MO List & Dashboard**:
   - Filter by Status (Draft/Partial/Released/Completed)
   - Filter by Article
   - Filter by Week Number
   - Search by MO Number
   - Visual workflow: Draft → Partial → Released
   - Critical fields display: Week, Destination (inherited from PO Label)

2. **Create/Edit MO**:
   - MO Header:
     - MO Number (auto-generate)
     - Article Selection (link to PO Label)
     - Target Qty (pcs)
     - **Week Number** (auto-inherit from PO Label) ⚠️ CRITICAL
     - **Destination** (auto-inherit from PO Label) ⚠️ CRITICAL
     - Start Date (date picker)
     - Target Completion Date (date picker)
   - Display: Alert jika PO Kain belum diterima (TRIGGER 1 check)
   - Display: Highlight Week & Destination (visual emphasis)

3. **MO Release Workflow**:
   - **PARTIAL Release**:
     - Action: "Release Fabric Departments" button
     - Effect: Generate SPK untuk Cutting + Embroidery saja
     - Status: MO = PARTIAL
     - Validation: PO Kain must be received (TRIGGER 1 ✅)
   
   - **FULL Release**:
     - Trigger: PO Label received (TRIGGER 2 ✅)
     - Action: Automatic sistem generate SPK untuk Sewing + Finishing + Packing
     - Status: MO = RELEASED
     - Display: Modal confirmation "PO Label received! Full release available"

4. **SPK List & Management**:
   - Grouped by Department (Cutting, Embroidery, Sewing, Finishing, Packing)
   - Display: SPK Number, Article, Target Qty, Status, Progress
   - Calendar View: Show SPK timeline (Gantt chart style)
   - Detail View: SPK details dengan BOM materials

5. **Material Allocation Dashboard**:
   - BOM Explosion result per SPK
   - Stock Availability Check:
     - 🟢 Available: Stock >= Required
     - 🟡 Partial: Stock < Required
     - 🔴 Shortage: Stock = 0
     - ⚫ Debt: Negative stock (production continues)
   - Reservation Status per Material
   - Allocation Actions: Reserve, Release, Adjust

**Technical Requirements**:
- Multi-stage approval workflow (Draft → Partial → Released)
- Auto-generation logic (MO from PO Label, SPK from MO)
- BOM cascade validation (check if previous dept BOM exists)
- Real-time material availability check
- Week & Destination inheritance tracking
- Timeline visualization (Gantt chart)
- Material reservation locking mechanism

**API Endpoints**:
- `GET /api/ppic/mo` - List MO dengan filters
- `POST /api/ppic/mo/create` - Create MO (auto from PO Label)
- `PUT /api/ppic/mo/{id}/release-partial` - PARTIAL release
- `PUT /api/ppic/mo/{id}/release-full` - FULL release (auto on PO Label receive)
- `GET /api/ppic/spk` - List SPK dengan filters
- `POST /api/ppic/spk/generate` - Auto-generate SPK from MO
- `GET /api/ppic/material-allocation/{mo_id}` - Material allocation status
- `POST /api/ppic/material-allocation/reserve` - Reserve materials

**Validation Rules**:
- PARTIAL release: PO Kain (TRIGGER 1) must be received
- FULL release: PO Label (TRIGGER 2) must be received
- SPK generation: BOM cascade validation (previous dept output exists)
- Material allocation: Cannot exceed available stock (unless Debt allowed)

**Deliverable**:
- MO List dengan status filters
- MO Creation form dengan Week/Destination inheritance
- MO Release workflow (PARTIAL + FULL buttons)
- SPK List dengan calendar view
- Material Allocation dashboard dengan color coding

---

#### Task 2.5: Production Module (Section 5)
**Reference**: `Rencana Tampilan.md` Section 5

**Critical Features** (UNIQUE BUSINESS LOGIC):
1. **6-Stage Production Flow** (Cutting → Embroidery → Sewing → Finishing 2-stage → Packing)
2. **Calendar-based Daily Input** (bukan cumulative)
3. **Real-Time WIP Tracking** per Department
4. **Material Consumption Tracking** per Stage
5. **Finishing 2-Stage Process** (Stuffing + Closing)

**UI Components to Build**:

1. **Production Dashboard (per Department)**:
   - Department Selection (tabs): Cutting | Embroidery | Sewing | Finishing | Packing
   - KPI Cards:
     - Today's Target vs Actual
     - Weekly Progress (%)
     - Active SPK Count
     - WIP Stock Level
   - Production Calendar (monthly view)
   - Real-Time WIP Table

2. **Daily Production Input Form** (CRITICAL ⚠️):

   **Common Flow** (untuk semua dept):
   ```
   Step 1: Select Department (Cutting/Embroidery/Sewing/Finishing/Packing)
   Step 2: Select SPK Number (dropdown - only active SPK)
   Step 3: Select Date (calendar picker - default: today)
   Step 4: Input Daily Output (qty for that specific day)
   Step 5: Input Good vs Defect breakdown
   Step 6: [Optional] Material Consumption (if applicable)
   Step 7: Submit (validate cumulative <= target)
   ```

   **UI Design**:
   - Large Calendar Component (click date to input)
   - Selected Date Highlight (green border)
   - Existing Data Display (show previous inputs with edit icon)
   - Cumulative Progress Bar (visual indicator: X / Target pcs)
   - Validation Alert: "Cumulative exceeds target!" (red message)

   **Department-Specific Fields**:

   - **Cutting**:
     - Input: Good Output (pcs), Defect (pcs)
     - Material Consumption: Fabric usage (YARD → PCS conversion)
     - Display: Yield % (Good / (Good + Defect))

   - **Embroidery**:
     - Subcontract Toggle: [In-house] / [Subcontractor]
     - If Subcon: Select Subcon Name, Send Date, Expected Return
     - Input: Good Output, Defect
     - Display: Subcon Status (Sent/Returned)

   - **Sewing**:
     - Parallel Streams: Body & Baju (separate inputs)
     - Input: Good Output (Body), Good Output (Baju), Defect
     - Constraint Check: Body ≥ Baju (validation)
     - Display: Body vs Baju comparison chart

   - **Finishing** (🆕 2-STAGE):
     - **Stage Selection**: [Stage 1: Stuffing] / [Stage 2: Closing]
     
     - **Stage 1 Input**:
       - Input: Skin (from Sewing), Filling (gram), Stuffed Body Output
       - Material: Track Filling consumption per pcs (auto-calculate)
       - Display: Filling gram/pcs average
     
     - **Stage 2 Input**:
       - Input: Stuffed Body (from Stage 1), Finished Doll Output
       - Process: Hang Tag attachment count
       - Display: Stage 1 → Stage 2 conversion rate

   - **Packing**:
     - Constraint Check: Doll + Baju availability (must both exist)
     - Input: Packed Sets (pcs), Cartons (pcs), Pallet (optional)
     - UOM Conversion: Sets → Cartons (auto-calculate based on packing std)
     - Barcode Generation: Print label button
     - Display: FG ready for shipment count

3. **Production Calendar View**:
   - Monthly Calendar Layout
   - Color Coding:
     - 🟢 Green: Target met
     - 🟡 Yellow: Partial progress
     - 🔴 Red: No production
     - ⚫ Grey: No target (rest day)
   - Click Date: Open input modal
   - Hover Date: Show tooltip (qty produced)

4. **Real-Time WIP Dashboard**:
   - Live Stock Table per Department:
     ```
     | Article | Cutting | Embroidery | Sewing | Finishing | Packing | FG |
     |---------|---------|------------|--------|-----------|---------|-----|
     | AFTONS  |  125    |    85      |   60   |    45     |   30    | 15  |
     | KRAMIG  |  200    |   180      |  150   |   120     |  100    | 80  |
     ```
   - Material Consumption Chart (per dept)
   - Bottleneck Detection (highlight dept with lowest output)

5. **Production Report (Daily/Weekly)**:
   - Filter by Department/Article/Date Range
   - Table: Date | Target | Actual | Variance | Efficiency %
   - Charts: Line chart (trend), Bar chart (comparison)
   - Export: Excel/PDF button

**Technical Requirements**:
- Calendar component dengan date picker (react-day-picker)
- Real-time data sync (React Query dengan refetchInterval: 30s)
- UOM conversion validation (YARD → PCS, Box → PCS)
- Cumulative calculation (sum all daily inputs)
- Constraint validation (Sewing: Body ≥ Baju, Packing: Doll + Baju check)
- Material consumption tracking (Filling gram per pcs)
- Subcontractor management (Embroidery)
- Barcode generation (Packing)
- 2-Stage process handling (Finishing)

**API Endpoints**:
- `GET /api/production/spk/{dept}` - List active SPK per dept
- `GET /api/production/calendar/{dept}/{month}` - Calendar data per dept
- `POST /api/production/input` - Daily production input
- `GET /api/production/wip` - Real-time WIP dashboard data
- `GET /api/production/report` - Production report dengan filters
- `PUT /api/production/subcon` - Send/receive from subcontractor

**Validation Rules**:
- Daily input: Must select SPK + Date
- Good Output: Must be > 0
- Defect: Must be >= 0
- Cumulative check: Sum(all daily inputs) <= Target SPK
- Sewing constraint: Body qty >= Baju qty
- Packing constraint: Doll stock >= Packed sets AND Baju stock >= Packed sets
- Finishing Stage 1: Skin + Filling input required
- Finishing Stage 2: Stuffed Body input required

**Deliverable**:
- Production Dashboard per Department
- Daily Production Input Form (calendar-based)
- Department-specific input fields (Cutting, Embroidery, Sewing, Finishing 2-stage, Packing)
- Real-Time WIP Dashboard
- Production Report dengan charts & export

---

#### Task 2.6: Warehouse & Inventory Module (Section 6)
**Reference**: `Rencana Tampilan.md` Section 6

**Critical Features** (UNIQUE BUSINESS LOGIC):
1. **Warehouse 3-Types**: Main (Materials) + Finishing Internal (2-stage) + FG
2. **Material Receipt with Validation** (0-5% auto, 5-10% SPV, >10% Manager)
3. **Negative Stock (Material Debt)** management
4. **UOM Conversion** (Box → Pcs, YARD → PCS)
5. **Barcode Scanning** (Mobile app integration)
6. **FIFO/FEFO Logic** untuk FG Out

**UI Components to Build**:

1. **Warehouse Dashboard (Overview)**:
   - 3 Warehouse Cards:
     - **Main Warehouse**: Material stock level, Critical items count
     - **Finishing Warehouse**: Skin, Stuffed Body, Finished Doll counts
     - **FG Warehouse**: Total FG pcs, Cartons, Pallets ready
   - Stock Movement Chart (In vs Out per day)
   - Low Stock Alert Table (Top 10 critical materials)

2. **Warehouse Main - Material Management**:

   **A. Stock Material View**:
   - Table: Material Code | Name | Stock | UOM | Min Stock | Status | Location
   - Color Coding:
     - 🟢 Green (>50% min stock): Safe
     - 🟡 Yellow (15-50% min stock): Warning
     - 🔴 Red (<15% min stock): Critical
     - ⚫ Black (Negative): DEBT
   - Actions: View History, Adjust Stock, Transfer

   **B. Material Receipt (GRN)** (🆕 STEP-BY-STEP UI):
   
   **Step 1: Scan Barcode / Input PO**
   ```
   UI Layout:
   ┌─────────────────────────────────────────────┐
   │  📦 MATERIAL RECEIPT                        │
   ├─────────────────────────────────────────────┤
   │  🔍 Scan PO Barcode or Input Manual         │
   │  ┌────────────────────────────────────┐    │
   │  │ [Scan Icon] 📷 Scan Barcode        │    │
   │  │ ──────────── OR ───────────────    │    │
   │  │ PO Number: [Input field]   [🔍]    │    │
   │  └────────────────────────────────────┘    │
   │                                             │
   │  Mode: [🖥️ Desktop] / [📱 Mobile]          │
   └─────────────────────────────────────────────┘
   ```
   
   **Step 2: Input Received Quantity**
   ```
   UI Layout:
   ┌─────────────────────────────────────────────┐
   │  PO-FAB-2026-0456 | Supplier: PT Fabric Co  │
   ├─────────────────────────────────────────────┤
   │  Material List:                             │
   │                                             │
   │  ┌─────────────────────────────────────┐   │
   │  │ [IKHR504] KOHAIR 7MM D.BROWN        │   │
   │  │                                      │   │
   │  │ PO Qty: 70.4 YD                      │   │
   │  │ Received Qty: [Input] YD  [Scan 📷] │   │
   │  │                                      │   │
   │  │ ⚠️ Variance: -3.2 YD (-4.5%)         │   │
   │  │ Status: ✅ Within tolerance (< 5%)   │   │
   │  │ Auto-approve: YES                    │   │
   │  └─────────────────────────────────────┘   │
   │                                             │
   │  [Add Next Material] [Cancel] [Confirm]    │
   └─────────────────────────────────────────────┘
   ```
   
   **Validation Rules** (CRITICAL ⚠️):
   - **0-5% variance**: ✅ Auto-approve (system update stock immediately)
   - **5-10% variance**: ⚠️ Supervisor approval required (modal popup)
   - **>10% variance**: 🔴 Manager approval + reason input mandatory
   
   **Step 3: Confirmation & Stock Update**
   ```
   UI Layout:
   ┌─────────────────────────────────────────────┐
   │  ✅ RECEIPT CONFIRMED                       │
   ├─────────────────────────────────────────────┤
   │  PO-FAB-2026-0456                           │
   │  Total Materials: 4 items                   │
   │  Total Received: 162.9 YD                   │
   │                                             │
   │  Stock Updated: ✅                          │
   │  GRN Number: GRN-2026-00123                 │
   │  Receipt Date: 2026-02-05 10:30 AM          │
   │  Received By: John Warehouse                │
   │                                             │
   │  Auto Actions Completed:                    │
   │  ✅ Stock updated in Warehouse Main         │
   │  ✅ PO status updated to "Partial Received" │
   │  ✅ Material debt cleared (-12 KG → 0)      │
   │  ✅ Notification sent to PPIC               │
   │  ✅ Document created (GRN PDF)              │
   │                                             │
   │  [Print GRN] [View Stock] [New Receipt]    │
   └─────────────────────────────────────────────┘
   ```

   **C. Material Issue (to Production)**:
   - Select SPK (dropdown)
   - Display: Required materials from BOM
   - Input: Issued Qty per material
   - Validation: Check stock availability
   - Negative Stock Handling:
     - If Stock < Required: Show alert "Insufficient stock! Proceed with debt?"
     - If Proceed: Create Material Debt record
     - Display: Debt amount, Expected settlement date

   **D. Stock Adjustment**:
   - Reason Selection: Physical count, Damage, Expired, Other
   - Input: Adjustment Qty (+/-)
   - Approval Workflow: Warehouse Manager → Director (if >$500)
   - Audit Trail: Before/After stock, Reason, Approver

3. **Warehouse Finishing - 2-Stage Internal**:

   **Stage 1: Skin Storage**:
   - Input: Receipt from Sewing (SKU: Skin)
   - Display: Available Skin count per article
   - Queue: FIFO queue untuk Stage 1 processing

   **Stage 2: Stuffed Body Storage**:
   - Input: Receipt from Finishing Stage 1 (SKU: Stuffed Body)
   - Display: Available Stuffed Body count
   - Queue: FIFO queue untuk Stage 2 processing

   **Final: Finished Doll Storage**:
   - Input: Receipt from Finishing Stage 2 (SKU: Finished Doll)
   - Display: Ready for Packing count
   - Transfer to Packing: Click button to issue to Packing dept

4. **Warehouse Finished Goods**:

   **A. Stock FG View**:
   - Table: Article | Week | Destination | Cartons | Pcs | Pallet | Location
   - Filter by: Week, Destination, Article
   - Actions: View Details, Transfer to Shipping

   **B. FG Receipt (from Packing)**:
   - Input: Carton Count (scan barcode 📱)
   - UOM Conversion: Cartons → Pcs (auto-calculate)
   - Validation: Check if qty matches Packing output (<10% variance auto-accept)
   - Pallet Assignment: Auto-assign or manual input
   - Label Printing: Generate FG label with barcode

   **C. FG Shipment (Out)**:
   - Input: Delivery Order (DO) number
   - Pick List Generation: FIFO/FEFO logic (oldest first)
   - Carton Selection: Checkbox per carton to load
   - Loading List: Print dengan carton details
   - Shipment Confirmation: Update FG stock, Mark DO as shipped

5. **Stock Opname (Cycle Count)**:
   - Schedule: Monthly/Quarterly calendar
   - Input: Physical Count per material/FG
   - Variance Calculation: System Stock vs Physical Count
   - Adjustment Request: Auto-create adjustment if variance >2%
   - Report: Variance Analysis dengan root cause

**Technical Requirements**:
- Barcode scanning integration (Mobile app via PWA or React Native)
- Real-time stock updates (WebSocket or React Query polling)
- UOM conversion validation (Box → Pcs, YARD → PCS)
- Negative stock handling (Material Debt tracking)
- FIFO/FEFO logic implementation (queue-based)
- Variance validation (0-5%, 5-10%, >10% approval workflow)
- Multi-step form (Material Receipt 3 steps)
- Pallet management (stacking logic)
- Label printing (PDF generation atau thermal printer integration)

**API Endpoints**:
- `GET /api/warehouse/material/stock` - Material stock list
- `POST /api/warehouse/material/receipt` - Material receipt (GRN)
- `POST /api/warehouse/material/issue` - Issue to production
- `POST /api/warehouse/material/adjust` - Stock adjustment
- `GET /api/warehouse/finishing/stock` - Finishing warehouse stock (3 stages)
- `POST /api/warehouse/finishing/transfer` - Transfer between stages
- `GET /api/warehouse/fg/stock` - FG stock list
- `POST /api/warehouse/fg/receipt` - FG receipt from Packing
- `POST /api/warehouse/fg/shipment` - FG shipment out
- `POST /api/warehouse/opname` - Stock opname input

**Validation Rules**:
- Material Receipt variance: 0-5% auto, 5-10% SPV, >10% Manager
- Material Issue: Cannot exceed available stock (unless Debt approved)
- FG Receipt: UOM conversion must match (Carton × Std Packing = Pcs)
- FG Shipment: FIFO/FEFO logic enforced (oldest carton first)
- Stock Adjustment: Reason mandatory, Approval required if >$500

**Deliverable**:
- Warehouse Dashboard (3 warehouses overview)
- Material Stock Management dengan color coding
- Material Receipt 3-Step UI dengan validation
- Material Issue dengan Debt handling
- Finishing Warehouse 2-Stage management
- FG Stock Management dengan FIFO logic
- FG Receipt dengan barcode scanning
- FG Shipment dengan pick list
- Stock Opname dengan variance analysis

---

#### Task 2.7: Rework & Quality Control Module (Section 7)
**Reference**: `Rencana Tampilan.md` Section 7

**Critical Features** (NEW MODULE ⚠️):
1. **QC 4-Checkpoint System** (After Cutting, After Sewing, After Finishing, Pre-Packing)
2. **Rework Workflow** (Defect → Queue → Repair → Re-QC)
3. **COPQ Analysis** (Cost of Poor Quality tracking)
4. **Defect Classification** (Fixable vs Scrap)
5. **Root Cause Analysis** (Pareto chart)

**UI Components to Build**:

1. **Rework Dashboard**:
   - KPI Cards:
     - Total Defects (by dept)
     - In Rework Queue (pending)
     - Completed Rework (success)
     - Recovery Rate (%)
   - Defect Pareto Chart (Top 10 defect types)
   - Rework Timeline (aging analysis)
   - COPQ Summary (cost by dept)

2. **QC Checkpoint Input Form**:
   - Checkpoint Selection: [After Cutting] / [After Sewing] / [After Finishing] / [Pre-Packing]
   - Input:
     - SPK Number (dropdown)
     - Inspection Date (date picker)
     - Sample Size (pcs)
     - Inspected Qty (pcs)
     - Pass Qty (pcs)
     - Fail Qty (pcs)
   - Defect Details (if Fail > 0):
     - Defect Type (dropdown): Fabric tear, Stitch loose, Stuffing uneven, Label wrong, etc.
     - Defect Qty (pcs)
     - Severity: [Minor] / [Major] / [Critical]
     - Action: [Send to Rework] / [Scrap]
     - Notes (text area)
   - Photo Upload: Attach defect photos
   - Submit: Create Rework Order or Scrap record

3. **Rework List & Management**:
   - Table: Rework ID | Article | Dept | Defect Type | Qty | Priority | Status | Age (days)
   - Filter by: Department, Status (Queue/In Progress/Completed), Priority
   - Sort by: Age (oldest first), Priority (urgent first)
   - Actions: Start Rework, Complete, Scrap

4. **Rework Station Input**:
   - Select Rework Order (from queue)
   - Process Details:
     - Rework Start Time (auto)
     - Rework Process (text area): Describe repair steps
     - Material Used (if any): Select materials + qty
     - Rework Duration (minutes)
   - Result:
     - Success Qty (pcs): Fixed successfully
     - Scrap Qty (pcs): Cannot be fixed
   - Re-QC:
     - If Success > 0: Send to Re-QC (create QC task)
     - If Scrap > 0: Update scrap record
   - Cost Calculation:
     - Labor cost (duration × labor rate)
     - Material cost (sum of materials used)
     - Total COPQ (labor + material)

5. **Rework Report & Analytics**:
   - **Defect Analysis**:
     - By Department: Table + Bar chart
     - By Article: Table + Pie chart
     - By Defect Type: Pareto chart (80/20 rule)
   - **Rework Performance**:
     - Recovery Rate: Success / (Success + Scrap) × 100%
     - Average Rework Time (minutes per pcs)
     - COPQ per Article (cost breakdown)
   - **Root Cause Analysis**:
     - Fishbone diagram (manual drawing atau tool)
     - 5 Whys template
     - Corrective Action Tracking
   - **First Pass Yield (FPY)**:
     - FPY per Department: (Pass / Inspected) × 100%
     - Trend chart (monthly FPY)
     - Target vs Actual comparison

**Technical Requirements**:
- Photo upload (drag & drop, max 5MB per file)
- Real-time queue management (FIFO for rework orders)
- Cost calculation (auto from labor rate + material price)
- Aging analysis (calculate days since defect detected)
- Pareto chart (sort by frequency, show cumulative %)
- Export report (Excel/PDF dengan charts)

**API Endpoints**:
- `POST /api/qc/checkpoint` - QC checkpoint input
- `GET /api/rework/orders` - List rework orders dengan filters
- `POST /api/rework/start` - Start rework process
- `POST /api/rework/complete` - Complete rework (with result)
- `GET /api/rework/dashboard` - Rework dashboard KPIs
- `GET /api/rework/report/defect-analysis` - Defect analysis data
- `GET /api/rework/report/copq` - COPQ report
- `GET /api/rework/report/fpy` - First Pass Yield report

**Validation Rules**:
- QC Input: Inspected Qty must be > 0
- QC Input: Pass + Fail must equal Inspected Qty
- Defect Details: If Fail > 0, Defect Type + Action mandatory
- Rework Result: Success + Scrap must equal Rework Qty
- Re-QC: If Success > 0, must create Re-QC task

**Deliverable**:
- Rework Dashboard dengan KPIs
- QC Checkpoint Input Form (4 checkpoints)
- Rework List dengan filters & aging
- Rework Station Input dengan cost tracking
- Rework Report dengan Defect Analysis, COPQ, FPY

---

### PHASE 3: SUPPORTING MODULES (Week 5-6)

#### Task 3.1: Masterdata Management (Section 8)
**Reference**: `Rencana Tampilan.md` Section 8

**UI Components to Build**:
1. Material Master (CRUD)
2. Supplier Master (CRUD)
3. BOM Master (CRUD with cascade validation)
4. Article Master (CRUD dengan UOM conversion)
5. Department Master (CRUD)
6. Subcontractor Master (CRUD)

**Key Features**:
- Search & filter per masterdata type
- Import/Export Excel functionality
- Version control untuk BOM
- BOM cascade validation (dept to dept)
- Material-Supplier mapping

**Deliverable**:
- Complete CRUD interfaces untuk all masterdata
- Import/Export Excel feature
- BOM cascade validation logic

---

#### Task 3.2: Reporting Module (Section 9)
**Reference**: `Rencana Tampilan.md` Section 9

**UI Components to Build**:
1. Production Reports (Daily, Weekly, Monthly)
2. Purchasing Reports (PO Summary, Delivery Performance)
3. Inventory Reports (Stock Movement, ABC Analysis)
4. Material Debt Report (Current Debt, Settlement Tracking)
5. Rework & Quality Reports (Defect Analysis, Recovery Rate, FPY)
6. Flexible Target Analysis
7. Executive Dashboard (KPI untuk Director)

**Key Features**:
- Dynamic date range filter
- Multiple chart types (Line, Bar, Pie, Pareto)
- Export to Excel/PDF
- Email schedule (automatic daily/weekly report)
- Drill-down capability (click chart to see details)

**Deliverable**:
- All report screens dengan charts
- Export functionality (Excel, PDF)
- Email scheduling system

---

#### Task 3.3: User Management & System (Section 10)
**Reference**: `Rencana Tampilan.md` Section 10

**UI Components to Build**:
1. User Management (CRUD)
2. Role & Permission Matrix
3. Approval Workflow configuration
4. Audit Trail viewer
5. System Configuration

**Key Features**:
- Predefined roles (10 roles)
- Custom permission per module
- Multi-level approval workflow
- Activity log dengan search & filter
- System parameters configuration

**Deliverable**:
- User Management interface
- Role & Permission matrix UI
- Approval Workflow configurator
- Audit Trail viewer dengan filters

---

#### Task 3.4: Mobile Application (Section 11)
**Reference**: `Rencana Tampilan.md` Section 11

**UI Components to Build**:
1. Mobile Login Screen
2. Barcode Scanner (Camera integration)
3. Material Receipt (Mobile version)
4. FG Receipt (Mobile version)
5. Production Input (simplified)
6. Notification Center (push notifications)

**Technical Requirements**:
- Progressive Web App (PWA) atau React Native
- Camera API untuk barcode scanning
- Offline mode support (local storage sync)
- Push notification integration (Firebase/OneSignal)

**Deliverable**:
- Mobile-optimized UI
- Barcode scanning functionality
- Offline mode support
- Push notifications

---

### PHASE 4: ADVANCED FEATURES (Week 7-8)

#### Task 4.1: Real-Time Features
1. **WebSocket Integration**:
   - Real-time dashboard updates
   - Live notification push
   - Multi-user collaboration (concurrent editing lock)

2. **Material Flow Tracking** (Section 13):
   - 5W1H Audit Trail visualization
   - Timeline view per material batch
   - Chain of custody tracking

3. **Timeline & Gantt Chart** (Section 14):
   - 16-day production cycle visualization
   - Interactive Gantt chart (drag to reschedule)
   - Critical path highlighting

**Deliverable**:
- WebSocket client implementation
- Material Flow Tracking UI
- Interactive Gantt Chart

---

#### Task 4.2: Barcode & Label System (Section 15)
**Reference**: `Rencana Tampilan.md` Section 15

**UI Components to Build**:
1. Label Design Template Editor
2. Barcode Generation (QR Code, Code128)
3. Label Printing (PDF atau thermal printer)
4. Label Verification Scanner (Mobile)

**Deliverable**:
- Label template editor
- Barcode generation system
- Label printing functionality
- Mobile scanner app

---

#### Task 4.3: Security & Fraud Prevention (Section 16)
**Reference**: `Rencana Tampilan.md` Section 16

**Security Features to Implement**:
1. **Authentication**:
   - JWT token dengan refresh mechanism
   - 2FA optional (Google Authenticator)
   - IP whitelist untuk production access
   - Session timeout (30 min idle)

2. **Authorization**:
   - Role-based access control (RBAC)
   - Permission-based UI rendering (hide/show buttons)
   - API endpoint protection (middleware)

3. **Audit Trail**:
   - Log all critical actions (create, update, delete)
   - User activity tracking
   - Data change history (before/after)

4. **Fraud Prevention**:
   - Stock adjustment anomaly detection
   - Duplicate PO warning
   - Unusual activity alert (e.g., delete 100+ records)

**Deliverable**:
- Complete authentication flow
- RBAC implementation
- Audit logging system
- Fraud detection alerts

---

## 🎨 UI/UX DESIGN GUIDELINES

### Design System
1. **Color Palette**:
   - Primary: Blue (#3B82F6) - Actions, Links
   - Success: Green (#10B981) - Positive status
   - Warning: Yellow (#F59E0B) - Alerts
   - Danger: Red (#EF4444) - Errors, Critical
   - Neutral: Gray (#6B7280) - Text, Borders
   - Debt: Black (#000000) - Negative stock

2. **Typography**:
   - Font Family: Inter, Roboto, atau system font
   - Heading: Bold, 24-32px
   - Body: Regular, 14-16px
   - Caption: Regular, 12px

3. **Spacing**:
   - Base unit: 4px (0.25rem)
   - Common: 8px, 12px, 16px, 24px, 32px

4. **Components**:
   - Use shadcn/ui atau Material-UI components
   - Consistent button styles (solid, outline, ghost)
   - Form inputs dengan validation states (error, success)
   - Loading states (spinner, skeleton)

### Responsive Design
- **Desktop**: 1920x1080 (primary)
- **Tablet**: 768x1024 (landscape)
- **Mobile**: 375x667 (portrait)

### Accessibility
- WCAG 2.1 Level AA compliance
- Keyboard navigation support
- Screen reader friendly
- Color contrast ratio >4.5:1

---

## 🧪 TESTING REQUIREMENTS

### Unit Testing
- Jest + React Testing Library
- Test coverage: >80%
- Critical components: Forms, Tables, Charts

### Integration Testing
- Test API integration (mock API)
- Test user flows (login → create PO → submit)

### E2E Testing (Optional)
- Playwright atau Cypress
- Test critical paths: Login, Create MO, Production Input

---

## 📦 DELIVERABLES CHECKLIST

### Week 1-2:
- ✅ Project setup complete
- ✅ Authentication flow working
- ✅ Dashboard Utama implemented
- ✅ Menu Navigasi implemented

### Week 3-4:
- ✅ Purchasing Module complete (Dual Mode PO)
- ✅ PPIC Module complete (MO + SPK + Material Allocation)
- ✅ Production Module complete (6-Stage dengan Calendar)

### Week 5-6:
- ✅ Warehouse Module complete (3-Types dengan Receipt UI)
- ✅ Rework & QC Module complete (4-Checkpoint + COPQ)
- ✅ Masterdata Management complete
- ✅ Reporting Module complete

### Week 7-8:
- ✅ Real-time features (WebSocket, Material Flow, Gantt)
- ✅ Barcode & Label System
- ✅ Security & Fraud Prevention
- ✅ Mobile App (PWA)

### Final:
- ✅ All modules tested & working
- ✅ Responsive design validated
- ✅ Documentation complete (README, API docs, User Guide)
- ✅ Deployment ready (Docker, CI/CD)

---

## 📝 DOCUMENTATION REQUIREMENTS

### Code Documentation
- JSDoc comments untuk functions
- README.md per feature module
- Component Storybook (optional)

### User Documentation
- User Guide (PDF) per role
- Video tutorials (Loom/YouTube)
- FAQ document

### Technical Documentation
- Architecture diagram (Mermaid)
- API documentation (Swagger/OpenAPI)
- Database schema (ERD)
- Deployment guide (Docker Compose)

---

## 🚀 DEPLOYMENT & DEVOPS

### Development Environment
- Docker Compose (Backend + Frontend + DB)
- Hot reload (Next.js dev mode)
- API proxy (avoid CORS issues)

### Production Environment
- Docker Compose (optimized build)
- Nginx reverse proxy
- PostgreSQL 15 (persistent volume)
- SSL/TLS (Let's Encrypt)

### CI/CD (Optional)
- GitHub Actions (lint + test + build)
- Auto-deploy to staging on push
- Manual deploy to production

---

## 🎯 SUCCESS CRITERIA

### Functional Completeness
- ✅ All 16 sections dari Rencana Tampilan implemented
- ✅ All critical features working (Dual Trigger, 2-Stage Finishing, Material Debt, etc.)
- ✅ All user roles supported
- ✅ All reports available

### Performance
- ✅ Page load time <2s (initial load)
- ✅ API response time <500ms (average)
- ✅ Real-time updates within 5s

### Quality
- ✅ Test coverage >80%
- ✅ No critical bugs
- ✅ Responsive design validated
- ✅ Accessibility compliance (WCAG 2.1 AA)

### User Experience
- ✅ Intuitive navigation
- ✅ Clear error messages
- ✅ Helpful tooltips & instructions
- ✅ Smooth animations & transitions

---

## ❓ SUPPORT & COMMUNICATION

### Questions & Clarifications
- If you need clarification on business logic: Ask specific questions referencing section in Rencana Tampilan.md
- If you encounter technical blockers: Document the issue + attempted solutions
- If you need additional resources: Specify what documents/APIs needed

### Progress Updates
- Daily: Brief summary of completed tasks
- Weekly: Detailed report dengan screenshots/demo
- Blockers: Report immediately dengan context

---

## 🏁 FINAL NOTES

### Critical Reminders
1. **READ NAVIGATION_INTEGRATION_AUDIT.MD FIRST!** ⚠️ - This document reveals critical gaps: new pages were created without refactoring old pages, causing code duplication and broken navigation. ALWAYS check this audit before creating ANY new page!
2. **READ RENCANA TAMPILAN.MD COMPLETELY** - This is your source of truth (6,200+ lines)
3. **Understand Business Logic FIRST** - Don't implement without understanding WHY
4. **Follow 3-Tier Architecture** - Dashboard → Module Landing → Detail Pages (NO shortcuts!)
5. **Zero Duplication Rule** - Before creating new functionality, check if it exists in old pages
6. **Test Navigation Flows** - Always test: Dashboard → Landing → Detail → Back
7. **Refactor Old Pages First** - Remove duplicates before adding new detail pages
8. **Focus on User Experience** - This is factory floor software (must be fast & reliable)
9. **Test with Real Scenarios** - Use realistic data (actual articles, PO numbers, etc.)
10. **Ask Questions** - Better to clarify than to implement wrong

### Your Approach
1. **Phase 1**: Read docs + setup project (Week 1)
2. **Phase 2**: Core modules (Dashboard, Purchasing, PPIC, Production, Warehouse, Rework) (Week 2-4)
3. **Phase 3**: Supporting modules (Masterdata, Reporting, User Management, Mobile) (Week 5-6)
4. **Phase 4**: Advanced features (Real-time, Barcode, Security) (Week 7-8)

### Quality Over Speed
- Don't rush - Build it right the first time
- Code quality matters - Clean code, good structure
- User experience is CRITICAL - Factory workers will use this daily

---

## 🚀 START HERE

**Step 1**: Read `docs/00-Overview/Logic UI/Rencana Tampilan.md` completely (6,200+ lines).  
**Step 2**: Ask clarifying questions if anything is unclear.  
**Step 3**: Create implementation plan dengan task breakdown.  
**Step 4**: Setup project structure.  
**Step 5**: Start implementing Phase 1.

**GOOD LUCK! 🎉**

---

**Document Version**: 2.6  
**Last Updated**: 5 Februari 2026  
**Author**: ERP Project Lead  
**Target Audience**: IT Fullstack Developer (Claude AI)
