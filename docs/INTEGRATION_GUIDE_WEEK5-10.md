# 🔗 INTEGRATION GUIDE - Week 5-10 Components
**How to Integrate New Components into Existing Pages**

**Date**: 4 Februari 2026  
**Target Audience**: Frontend Developers  
**Estimated Time**: 2-3 hours for all integrations

---

## 📋 QUICK INTEGRATION CHECKLIST

### Priority 1 Components (Manufacturing)
- [ ] Integrate `MOCreateForm` into PPICPage.tsx
- [ ] Integrate `WorkOrdersDashboard` into DashboardPage.tsx
- [ ] Integrate `MaterialShortageAlerts` into DashboardPage.tsx

### Priority 2 Components (BOM)
- [ ] Integrate `BOMExplorer` into PPICPage.tsx (new tab)
- [ ] Integrate `BOMExplosionViewer` into PPICPage.tsx (MO detail view)

### Priority 3 Components (Warehouse)
- [ ] Integrate `StockManagement` into WarehousePage.tsx
- [ ] Integrate `MaterialReservation` into WarehousePage.tsx
- [ ] Integrate `StockDeductionTracker` into WarehousePage.tsx

---

## 🎯 INTEGRATION 1: PPIC PAGE

### File: `src/pages/PPICPage.tsx`

**Step 1: Import new components**
```typescript
import { MOCreateForm } from '@/components/manufacturing';
import { BOMExplorer, BOMExplosionViewer } from '@/components/bom';
```

**Step 2: Add state for modals**
```typescript
const [showMOForm, setShowMOForm] = useState(false);
const [showBOMExplorer, setShowBOMExplorer] = useState(false);
const [selectedMOForExplosion, setSelectedMOForExplosion] = useState<number | null>(null);
```

**Step 3: Update tabs**
```typescript
const [activeTab, setActiveTab] = useState<'mos' | 'bom' | 'planning' | 'workorders' | 'bom-explorer'>('mos');

// Add new tab button
<button
  onClick={() => setActiveTab('bom-explorer')}
  className={activeTab === 'bom-explorer' ? 'active' : ''}
>
  BOM Explorer
</button>
```

**Step 4: Replace old Create MO button with new form**
```typescript
// OLD CODE (to be replaced):
<button onClick={() => setShowCreateModal(true)}>
  Create MO
</button>

// NEW CODE:
<button onClick={() => setShowMOForm(true)} className="btn-primary">
  <Plus size={20} />
  Create Manufacturing Order
</button>

{/* MO Create Form Modal */}
{showMOForm && (
  <MOCreateForm 
    onClose={() => setShowMOForm(false)}
    onSuccess={() => {
      queryClient.invalidateQueries({ queryKey: ['manufacturing-orders'] });
    }}
  />
)}
```

**Step 5: Add BOM Explorer tab content**
```typescript
{activeTab === 'bom-explorer' && (
  <div className="mt-6">
    <BOMExplorer showSearch={true} />
  </div>
)}
```

**Step 6: Add Explosion viewer to MO list**
```typescript
// In MO list rendering, add "View Explosion" button
<button
  onClick={() => setSelectedMOForExplosion(mo.id)}
  className="text-blue-600 hover:text-blue-700"
>
  <Eye size={16} />
  View BOM Explosion
</button>

{/* BOM Explosion Modal */}
{selectedMOForExplosion && (
  <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
    <div className="bg-white rounded-lg max-w-6xl w-full max-h-[90vh] overflow-y-auto">
      <div className="flex items-center justify-between p-4 border-b">
        <h3 className="text-xl font-bold">BOM Explosion - MO #{selectedMOForExplosion}</h3>
        <button onClick={() => setSelectedMOForExplosion(null)}>
          <X size={24} />
        </button>
      </div>
      <div className="p-4">
        <BOMExplosionViewer moId={selectedMOForExplosion} showCosts={true} />
      </div>
    </div>
  </div>
)}
```

---

## 📊 INTEGRATION 2: DASHBOARD PAGE

### File: `src/pages/DashboardPage.tsx`

**Step 1: Import new components**
```typescript
import { MaterialShortageAlerts } from '@/components/manufacturing';
import { WorkOrdersDashboard } from '@/components/manufacturing';
```

**Step 2: Add Material Shortage widget to main dashboard**
```typescript
export const DashboardPage: React.FC = () => {
  return (
    <div>
      <EnvironmentBanner />
      <div className="p-6">
        {/* Existing dashboard header */}
        <h1 className="text-3xl font-bold">Dashboard</h1>

        {/* Stats Grid (existing) */}
        <div className="grid grid-cols-4 gap-6 mb-8">
          {/* existing stat cards */}
        </div>

        {/* NEW: Material Shortage Alerts Widget */}
        <div className="mb-8">
          <MaterialShortageAlerts maxItems={5} />
        </div>

        {/* NEW: Work Orders Dashboard Widget (optional) */}
        <div className="mb-8">
          <h2 className="text-2xl font-bold mb-4">Production Status</h2>
          <WorkOrdersDashboard departmentFilter="ALL" />
        </div>

        {/* Rest of existing dashboard content */}
      </div>
    </div>
  );
};
```

**Alternative: Add as collapsible section**
```typescript
const [showShortages, setShowShortages] = useState(true);

return (
  <div>
    <div className="mb-4 flex items-center justify-between">
      <h2 className="text-2xl font-bold">Material Alerts</h2>
      <button onClick={() => setShowShortages(!showShortages)}>
        {showShortages ? 'Hide' : 'Show'}
      </button>
    </div>
    
    {showShortages && (
      <MaterialShortageAlerts maxItems={5} />
    )}
  </div>
);
```

---

## 📦 INTEGRATION 3: WAREHOUSE PAGE

### File: `src/pages/WarehousePage.tsx`

**Step 1: Import new components**
```typescript
import { 
  StockManagement, 
  MaterialReservation, 
  StockDeductionTracker 
} from '@/components/warehouse';
```

**Step 2: Replace or enhance existing content**
```typescript
export const WarehousePage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'stock' | 'reservation' | 'deduction'>('stock');

  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold mb-6">Warehouse Management</h1>

      {/* Tab Navigation */}
      <div className="flex gap-2 mb-6 border-b">
        <button
          onClick={() => setActiveTab('stock')}
          className={`px-4 py-2 font-medium border-b-2 transition-colors ${
            activeTab === 'stock'
              ? 'border-blue-600 text-blue-600'
              : 'border-transparent text-gray-600 hover:text-gray-900'
          }`}
        >
          📦 Stock Management
        </button>
        <button
          onClick={() => setActiveTab('reservation')}
          className={`px-4 py-2 font-medium border-b-2 transition-colors ${
            activeTab === 'reservation'
              ? 'border-blue-600 text-blue-600'
              : 'border-transparent text-gray-600 hover:text-gray-900'
          }`}
        >
          🔒 Material Reservation
        </button>
        <button
          onClick={() => setActiveTab('deduction')}
          className={`px-4 py-2 font-medium border-b-2 transition-colors ${
            activeTab === 'deduction'
              ? 'border-blue-600 text-blue-600'
              : 'border-transparent text-gray-600 hover:text-gray-900'
          }`}
        >
          📉 Stock Deduction
        </button>
      </div>

      {/* Tab Content */}
      {activeTab === 'stock' && <StockManagement />}
      {activeTab === 'reservation' && <MaterialReservation />}
      {activeTab === 'deduction' && <StockDeductionTracker />}
    </div>
  );
};
```

---

## 🧪 TESTING GUIDE

### Test Scenario 1: Create MO with Dual Trigger
1. Login as PPIC user
2. Navigate to PPIC page
3. Click "Create Manufacturing Order"
4. Select PARTIAL mode
5. Choose product, enter quantity
6. Select PO Fabric only
7. Submit → Verify MO created with PARTIAL state
8. Repeat with RELEASED mode (both PO Fabric + PO Label)

### Test Scenario 2: Material Shortage Alerts
1. Navigate to Dashboard
2. Check Material Shortage widget
3. Verify alerts show CRITICAL/HIGH/MEDIUM severity
4. Click "View in Warehouse" → Should navigate to warehouse page
5. Verify auto-refresh works (wait 10 seconds)

### Test Scenario 3: BOM Explorer
1. Navigate to PPIC page → BOM Explorer tab
2. Select a product with BOM
3. Verify tree structure displays
4. Click expand/collapse nodes
5. Use search to filter components
6. Test "Expand All" and "Collapse All" buttons

### Test Scenario 4: Stock Management
1. Navigate to Warehouse page → Stock Management tab
2. Verify FIFO age displays correctly
3. Filter by location and product
4. Toggle "Show only low stock"
5. Switch to "Stock Moves" view
6. Verify data refreshes

### Test Scenario 5: Material Reservation
1. Navigate to Warehouse page → Reservation tab
2. Select a work order
3. Click "Reserve Materials (Auto FIFO)"
4. Verify reservations created
5. Click "Release" on a reservation
6. Verify it returns to available stock

### Test Scenario 6: Stock Deduction Tracker
1. Navigate to Warehouse page → Deduction tab
2. Select a running work order
3. Verify deductions show with negative qty
4. Check department breakdown chart
5. Filter by date range
6. Verify audit trail with timestamps

---

## 🚨 TROUBLESHOOTING

### Issue 1: Import errors
**Error**: `Module not found: Can't resolve '@/components/manufacturing'`

**Solution**: Verify index.ts files exist:
- `src/components/manufacturing/index.ts`
- `src/components/bom/index.ts`
- `src/components/warehouse/index.ts`

### Issue 2: TypeScript errors
**Error**: `Property 'X' does not exist on type 'Y'`

**Solution**: Ensure interfaces match API responses. Add type definitions if needed:
```typescript
interface MaterialShortage {
  id: number;
  material_code: string;
  // ... other fields
}
```

### Issue 3: API endpoints not found
**Error**: `404 Not Found` on API calls

**Solution**: Verify backend routes exist:
- `/material-allocation/shortages`
- `/work-orders?department=X`
- `/bom/{id}/explosion`

Check backend is running on port 8000.

### Issue 4: Components not rendering
**Error**: Blank screen or components missing

**Solution**: 
1. Check browser console for errors
2. Verify imports are correct
3. Check React Query QueryClient is configured in App.tsx
4. Verify Tailwind CSS classes are working

---

## 📝 QUICK INTEGRATION COMMANDS

### Install Frontend (if not done)
```powershell
cd d:\Project\ERP2026\erp-ui\frontend
npm install
```

### Start Frontend Dev Server
```powershell
npm run dev
# Access at http://localhost:5173
```

### Start Backend (parallel terminal)
```powershell
cd d:\Project\ERP2026\erp-softtoys
.\venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --port 8000
```

### Type Check
```powershell
npm run type-check
```

### Build Production
```powershell
npm run build
```

---

## ✅ INTEGRATION CHECKLIST

### Pre-Integration
- [ ] Backend running on port 8000
- [ ] Frontend dependencies installed
- [ ] TypeScript compiles without errors
- [ ] All index.ts export files created

### Post-Integration
- [ ] All imports resolve correctly
- [ ] No TypeScript errors
- [ ] Components render without crashes
- [ ] API calls work (check Network tab)
- [ ] Real-time updates working
- [ ] Responsive design works on different screen sizes

### Production Ready
- [ ] All test scenarios pass
- [ ] No console errors
- [ ] Performance acceptable (< 2s page load)
- [ ] Error handling works (test with network offline)
- [ ] User permissions respected (RBAC)

---

## 🎉 COMPLETION

When all integrations complete, you will have:
✅ Fully functional PPIC dashboard with dual trigger MO creation  
✅ Real-time production monitoring with WO dashboard  
✅ Material shortage alerts on main dashboard  
✅ Multi-level BOM explorer with visual tree  
✅ BOM explosion viewer for MOs  
✅ Complete warehouse stock management with FIFO  
✅ Material reservation system  
✅ Stock deduction tracking with audit trail  

**Total**: 10 new features integrated across 3 main pages! 🚀

**Next**: User Acceptance Testing (UAT) with actual PPIC and Warehouse staff!
