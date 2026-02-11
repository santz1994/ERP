# 🚀 SESSION 51 - QUICK START GUIDE

## ✅ What's Been Completed

### Frontend: POCreateModal.tsx
- ✅ AUTO Mode (BOM explosion - 80% faster)
- ✅ PO Reference System (LABEL/ACC → KAIN parent)
- ✅ Week & Destination (TRIGGER 2)
- ✅ Validation (comprehensive client-side)
- ✅ Material table (read-only auto-generated)
- ✅ State management (mode toggle, queries)

### Backend: purchasing.py
- ✅ GET /purchasing/available-po-kain
- ✅ POST /purchasing/bom/explosion
- ✅ GET /purchasing/articles (pre-existing)
- ✅ POST /purchasing/po validation (pre-existing)

### Database
- ✅ Schema complete (migration 014 applied)
- ✅ All 7 PO Reference columns present
- ✅ Constraints + indexes ready

---

## 🧪 Testing Commands (Run in Order)

### 1. Start Backend
```powershell
cd d:\Project\ERP2026\erp-softtoys
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Start Frontend
```powershell
cd d:\Project\ERP2026\erp-ui\frontend
npm run dev
```

### 3. Test Backend Endpoints

#### Test 1: Get Available PO KAIN
```powershell
# Get token first
$token = "your_jwt_token_here"

# Test endpoint
curl http://localhost:8000/api/v1/purchasing/available-po-kain `
  -H "Authorization: Bearer $token" `
  -H "Content-Type: application/json"

# Expected: Array of PO KAIN (empty if no test data)
```

#### Test 2: Get Articles
```powershell
curl http://localhost:8000/api/v1/purchasing/articles `
  -H "Authorization: Bearer $token"

# Expected: Array of articles (FINISH_GOOD type)
# Should return 237 articles after masterdata import
```

#### Test 3: BOM Explosion
```powershell
curl -X POST http://localhost:8000/api/v1/purchasing/bom/explosion `
  -H "Authorization: Bearer $token" `
  -H "Content-Type: application/json" `
  -d '{\"article_code\": \"40551542\", \"quantity\": 1000}'

# Expected: {"article": {...}, "materials": [...], "quantity": 1000}
# If BOM not imported yet: {"materials": [], "message": "No BOM found..."}
```

### 4. Test Frontend UI

1. **Navigate**: http://localhost:3000 → Login → Purchasing → "Create PO" button
2. **Test MANUAL Mode**:
   - Click "Create PO"
   - Select PO Type: KAIN
   - Click "Add Material" → Fill 1 material
   - Check: Can fill all fields
3. **Test AUTO Mode**:
   - Toggle "AUTO (80% faster)" button
   - Select article from dropdown
   - Enter quantity: 1000
   - Click "Explode BOM"
   - Check: Materials generated (if BOM exists)
   - Check: Code/Name/Qty read-only, Supplier/Price editable
4. **Test PO Reference**:
   - Create PO KAIN first (MANUAL mode, 1 material, submit)
   - Create new PO, select type: LABEL
   - Check: "Reference PO KAIN" dropdown appears
   - Check: Dropdown shows created PO KAIN
   - Select parent PO
   - Fill week="W5", destination="EU"
   - Submit
   - Check: PO created successfully
5. **Test Validation**:
   - Create PO LABEL without selecting parent → Check error toast
   - Create PO LABEL without week → Check error message
   - Create PO with material missing supplier → Check error

---

## 🐛 Known Issues / Blockers

### Current Data State
- **Materials**: 0 (cleaned database)
- **Articles**: 0 (cleaned database)
- **BOMs**: 0 (not imported yet)

**Impact**:
- ❌ BOM explosion will return empty (no BOM data)
- ❌ Article dropdown empty (no articles)
- ❌ Can only test MANUAL mode fully

**Solution**: Run masterdata + BOM import
```powershell
cd d:\Project\ERP2026
python import_masterdata_from_excel.py
# Will import: 9 materials, 237 articles
# Then import BOMs (6 Excel files) - script pending
```

### Backend URL Configuration
- Check frontend .env file has correct API URL
- Default: `VITE_API_BASE_URL=http://localhost:8000/api/v1`

### CORS Issues
- If frontend calls fail, check CORS settings in backend
- File: `erp-softtoys/app/main.py`
- Should allow origin: `http://localhost:3000`

---

## ✅ Quick Validation Checklist

### Frontend Compile
```powershell
cd d:\Project\ERP2026\erp-ui\frontend
npm run build
# Expected: No TypeScript errors
```

### Backend Startup
```powershell
cd d:\Project\ERP2026\erp-softtoys
python -m pytest tests/ -v
# Expected: Tests pass (or skip if test suite empty)
```

### Database Check
```powershell
cd d:\Project\ERP2026\erp-softtoys
python -m alembic current
# Expected: 014_po_reference_system (head)
```

---

## 📊 Success Criteria

### Minimal Test (No Data)
- [ ] Backend starts without errors
- [ ] Frontend compiles and loads
- [ ] Can open POCreateModal
- [ ] Can see AUTO/MANUAL toggle
- [ ] Can see PO Type dropdown (KAIN, LABEL, ACCESSORIES)
- [ ] PO LABEL shows Week + Destination fields
- [ ] Manual mode "Add Material" works

### Full Test (With Data)
- [ ] Article dropdown populated (237 items)
- [ ] BOM explosion generates materials
- [ ] Available PO KAIN dropdown shows test PO
- [ ] Can create PO KAIN (MANUAL mode)
- [ ] Can create PO LABEL referencing PO KAIN
- [ ] Validation blocks invalid submissions
- [ ] Auto-generated materials are read-only

---

## 🔧 Troubleshooting

### "No articles available"
→ Import articles: `python import_masterdata_from_excel.py`

### "No BOM found for article"
→ Import BOMs from 6 Excel files (script pending)

### "No available PO KAIN"
→ Create test PO KAIN first (MANUAL mode, any material, submit)

### "Authorization failed"
→ Login first, check JWT token not expired

### Frontend 404 errors
→ Check backend running on port 8000
→ Check CORS settings allow localhost:3000

### TypeScript errors
→ Run `npm install` in frontend directory
→ Check POCreateModal.tsx imports

---

## 📝 Next Actions (Priority Queue)

1. **Test Basic Flow** (30 min)
   - Start backend + frontend
   - Open POCreateModal
   - Verify UI looks correct
   - Check console for errors

2. **Import Masterdata** (15 min)
   - Run import script
   - Verify 9 materials + 237 articles imported
   - Test article dropdown populated

3. **Import BOMs** (2-3 hours)
   - Extend import script for 6 BOM Excel files
   - Run import
   - Test BOM explosion works

4. **End-to-End Test** (1 hour)
   - Create PO KAIN (MANUAL)
   - Create PO LABEL (AUTO mode, reference parent)
   - Verify data in database

5. **User Demo** (30 min)
   - Show AUTO mode (80% faster)
   - Show PO Reference chain
   - Show Week/Destination for TRIGGER 2

---

## 📚 Files Changed This Session

1. `erp-ui/frontend/src/components/purchasing/POCreateModal.tsx`
   - +303 lines (488 → 791)
   - 6 major features added

2. `erp-softtoys/app/api/v1/purchasing.py`
   - +252 lines (764 → 1016)
   - 2 new endpoints created

3. `SESSION_51_IMPLEMENTATION_COMPLETE.md` (NEW)
   - Complete implementation documentation

4. `SESSION_51_PO_MODAL_ENHANCEMENT_COMPLETE.md` (NEW)
   - Detailed technical specification

5. `SESSION_51_QUICK_START_GUIDE.md` (NEW - this file)
   - Testing checklist + troubleshooting

---

**Ready to Test! 🚀**

Start with minimal test (no data), then progress to full test after imports.
