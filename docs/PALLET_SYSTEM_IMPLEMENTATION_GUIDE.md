# 📦 PALLET SYSTEM IMPLEMENTATION GUIDE

**Project**: ERP Quty Karunia - Packing & Pallet Management  
**Date**: February 6, 2026  
**Priority**: P0 (CRITICAL) - Affects PO calculation, Packing, and FG Warehouse  
**Status**: Design Complete - Ready for Implementation

---

## 📋 EXECUTIVE SUMMARY

### Business Problem

PT Quty Karunia's current ERP system does not enforce **FIXED packing quantities**, leading to:

❌ **Inconsistent packing**: Operators pack varying quantities per carton  
❌ **Partial pallets**: FG warehouse receives incomplete pallets  
❌ **PO calculation errors**: Purchasing creates POs not aligned with pallet multiples  
❌ **Inventory confusion**: Stock displayed in PCS only, pallets not tracked  
❌ **Shipping inefficiency**: Cannot optimize container loading without pallet data

### Solution: Fixed Pallet System

✅ **Database-enforced packing specs**: Each article has fixed pcs_per_carton & cartons_per_pallet  
✅ **PO in pallet multiples**: Purchasing specifies # of pallets → auto-calculates PCS quantity  
✅ **Packing validation**: System validates exact quantities during carton & pallet formation  
✅ **Multi-UOM display**: FG stock shown in Pallets / Cartons / Pcs simultaneously  
✅ **Shipping optimization**: Container planning based on pallet count

---

## 🎯 CORE CONCEPT

### Three-Level Hierarchy

```
PALLET (Physical Unit for Storage & Shipping)
   ├─ Contains: FIXED number of cartons
   └─ Example: 8 cartons per pallet
        │
        └─ CARTON (Packaging Unit)
             ├─ Contains: FIXED number of pieces
             └─ Example: 60 pcs per carton
                  │
                  └─ PCS (Production Unit)
                       └─ Individual finished goods from Finishing dept
```

### Mathematical Relationship

```
pcs_per_pallet = pcs_per_carton × cartons_per_pallet

Example:
- Article: AFTONSPARV Bear
- Pcs per carton: 60 pcs
- Cartons per pallet: 8 cartons
- Pcs per pallet: 60 × 8 = 480 pcs

Therefore:
- 1 pallet = 8 cartons = 480 pcs
- 2 pallets = 16 cartons = 960 pcs
- 3 pallets = 24 cartons = 1,440 pcs
```

---

## 📊 DATA ANALYSIS RESULTS

### From Packing.xlsx (BOM Production)

**Total Records**: 1,228 BOM lines  
**Unique Articles**: 211 articles

**Pallet Specification** (Extracted from BOM):
```
Material: [ACB30121] PALLET 1140X750X50
Ratio: 0.125 PCE per finished good

Calculation:
1 finished good = 0.125 pallet
Therefore: 1 pallet = 1 / 0.125 = 8 finished goods

Interpretation: 8 CARTONS per pallet (not pcs!)
```

**Carton Specification** (From same BOM):
```
Material: [ACB30104] CARTON 570X375X450
Ratio: Varies by article (typically 1/60 to 1/84)

Common ratios:
- 1/60 = 60 pcs per carton
- 1/84 = 84 pcs per carton
- 1/10 = 10 pcs per carton (small items)
```

### From Carton.xlsx (Karton Masterdata)

**Format**: "1CT : XXX PCS" in REMARK column

**Sample Data**:
| Article Name | Pcs/Carton | Remark |
|-------------|------------|---------|
| KLAPPAR HAJJ N Soft toy | 10 | 1CT : 10PCS |
| (Other articles) | 60, 84 | 1CT : 60PCS, 1CT : 84PCS |

**Common Values**:
- 10 pcs/carton (small toys)
- 12 pcs/carton
- 24 pcs/carton
- 36 pcs/carton
- 48 pcs/carton
- 60 pcs/carton (most common for medium toys)
- 84 pcs/carton (large toys)

---

## 🔄 BUSINESS PROCESS FLOW

### Current Flow (Without Pallet System)

```
┌────────────────────────────────────────────────────────────────┐
│ ❌ CURRENT PROCESS (PROBLEMS)                                   │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│ 1. PO Kain Creation (Purchasing)                               │
│    └─ Enter quantity: 500 pcs (arbitrary number)               │
│       ❌ Problem: Not aligned with pallet multiples             │
│                                                                 │
│ 2. Production (Finishing → Packing)                            │
│    └─ Finishing produces: 500 pcs                              │
│    └─ Packing receives: 500 pcs                                │
│    └─ Pack into cartons: 500 ÷ 60 = 8.33 cartons              │
│       ❌ Problem: Partial carton! (20 pcs loose)                │
│                                                                 │
│ 3. FG Warehouse Receiving                                      │
│    └─ Receive: 8.33 cartons (stored as 500 pcs)               │
│       ❌ Problem: Cannot stack on pallet (need 8 full cartons) │
│       ❌ Display: 500 pcs (no carton/pallet info)              │
│                                                                 │
│ 4. Shipping                                                    │
│    └─ Load 8 cartons + 20 loose pcs                           │
│       ❌ Problem: Inefficient, manual count, risk of damage    │
└────────────────────────────────────────────────────────────────┘
```

### New Flow (With Pallet System)

```
┌────────────────────────────────────────────────────────────────┐
│ ✅ NEW PROCESS (PALLET SYSTEM)                                 │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│ 1. PO Kain Creation (Purchasing)                               │
│    ├─ Select article: AFTONSPARV Bear                          │
│    ├─ System displays packing spec:                            │
│    │  • 60 pcs/carton                                          │
│    │  • 8 cartons/pallet                                       │
│    │  • 480 pcs/pallet                                         │
│    ├─ Purchasing enters: 2 pallets                             │
│    └─ System auto-calculates:                                  │
│       • MO Quantity: 2 × 480 = 960 pcs                         │
│       • Expected cartons: 2 × 8 = 16 cartons                   │
│       ✅ Guaranteed: Exact pallet multiple                     │
│                                                                 │
│ 2. Production (Finishing → Packing)                            │
│    ├─ Finishing produces: 960 pcs (with buffer)                │
│    ├─ Packing receives: 960 pcs                                │
│    ├─ Pack into cartons:                                       │
│    │  └─ 960 ÷ 60 = 16 cartons EXACT ✅                        │
│    ├─ System validation:                                       │
│    │  • Count cartons: 16                                      │
│    │  • Input packed pcs: 960                                  │
│    │  • Validate: 16 × 60 = 960 ✅ (MATCH!)                    │
│    └─ Stack on pallets:                                        │
│       • 16 cartons ÷ 8 = 2 pallets EXACT ✅                    │
│       ✅ System blocks if variance > 0%                        │
│                                                                 │
│ 3. FG Warehouse Receiving                                      │
│    ├─ Receive from Packing: 2 PALLETS                          │
│    ├─ Scan pallet barcode: PLT-2026-00001, PLT-2026-00002     │
│    ├─ System auto-calculates:                                  │
│    │  • Pallets: 2 (primary unit)                              │
│    │  • Cartons: 2 × 8 = 16 cartons                            │
│    │  • Pcs: 2 × 480 = 960 pcs                                 │
│    └─ Display in FG Stock:                                     │
│       "2 PLT / 16 CTN / 960 PCS" ✅                            │
│                                                                 │
│ 4. Shipping                                                    │
│    └─ Load 2 pallets (shrink-wrapped, labeled)                │
│       ✅ Clean, efficient, no loose items                      │
│       ✅ Container optimization based on pallet count          │
└────────────────────────────────────────────────────────────────┘
```

---

## 🗄️ DATABASE SCHEMA CHANGES

### 1. Add Pallet Specifications to Products Table

```sql
-- Migration: Add pallet specifications to products table
ALTER TABLE products ADD COLUMN pcs_per_carton INTEGER;
ALTER TABLE products ADD COLUMN cartons_per_pallet INTEGER;
ALTER TABLE products ADD COLUMN pcs_per_pallet INTEGER GENERATED ALWAYS AS 
    (pcs_per_carton * cartons_per_pallet) STORED;

-- Add constraints
ALTER TABLE products ADD CONSTRAINT chk_pcs_per_carton_positive 
    CHECK (pcs_per_carton > 0);
ALTER TABLE products ADD CONSTRAINT chk_cartons_per_pallet_positive 
    CHECK (cartons_per_pallet > 0);

-- Add indexes for performance
CREATE INDEX idx_products_pallet_specs ON products (pcs_per_carton, cartons_per_pallet);

-- Comments
COMMENT ON COLUMN products.pcs_per_carton IS 'Fixed number of pieces per carton (e.g., 60 for AFTONSPARV)';
COMMENT ON COLUMN products.cartons_per_pallet IS 'Fixed number of cartons per pallet (typically 8)';
COMMENT ON COLUMN products.pcs_per_pallet IS 'Computed: pcs_per_carton × cartons_per_pallet (e.g., 480)';
```

### 2. Update PO Kain Table (Purchase Orders)

```sql
-- Add pallet planning fields to purchase_orders table
ALTER TABLE purchase_orders ADD COLUMN target_pallets INTEGER;
ALTER TABLE purchase_orders ADD COLUMN expected_cartons INTEGER;
ALTER TABLE purchase_orders ADD COLUMN calculated_pcs INTEGER;

-- Add constraint: quantity must match calculated_pcs
ALTER TABLE purchase_orders ADD CONSTRAINT chk_po_quantity_matches_pallet 
    CHECK (quantity = calculated_pcs);

-- Comments
COMMENT ON COLUMN purchase_orders.target_pallets IS 'Number of pallets Purchasing wants to produce';
COMMENT ON COLUMN purchase_orders.expected_cartons IS 'Computed: target_pallets × cartons_per_pallet';
COMMENT ON COLUMN purchase_orders.calculated_pcs IS 'Computed: target_pallets × pcs_per_pallet';
```

### 3. Update Packing Work Orders Table

```sql
-- Add pallet tracking to work_orders table (for Packing dept)
ALTER TABLE work_orders ADD COLUMN cartons_packed INTEGER DEFAULT 0;
ALTER TABLE work_orders ADD COLUMN pallets_formed INTEGER DEFAULT 0;
ALTER TABLE work_orders ADD COLUMN packing_validated BOOLEAN DEFAULT FALSE;

-- Comments
COMMENT ON COLUMN work_orders.cartons_packed IS 'Number of cartons packed (must be multiple of cartons_per_pallet)';
COMMENT ON COLUMN work_orders.pallets_formed IS 'Number of pallets formed (cartons_packed / cartons_per_pallet)';
COMMENT ON COLUMN work_orders.packing_validated IS 'TRUE if packed quantities validated against specs';
```

### 4. Update FG Stock Table

```sql
-- Add multi-UOM display to fg_stock table
ALTER TABLE fg_stock ADD COLUMN stock_pallets DECIMAL(10, 2);
ALTER TABLE fg_stock ADD COLUMN stock_cartons DECIMAL(10, 2);
ALTER TABLE fg_stock ADD COLUMN stock_pcs DECIMAL(10, 2);

-- Add constraint: ensure consistency
ALTER TABLE fg_stock ADD CONSTRAINT chk_fg_stock_consistency 
    CHECK (stock_pcs = stock_cartons * (SELECT pcs_per_carton FROM products WHERE products.id = fg_stock.product_id));

-- Comments
COMMENT ON COLUMN fg_stock.stock_pallets IS 'Primary unit: Number of pallets in warehouse';
COMMENT ON COLUMN fg_stock.stock_cartons IS 'Secondary unit: Number of cartons (pallets × cartons_per_pallet)';
COMMENT ON COLUMN fg_stock.stock_pcs IS 'Tertiary unit: Number of pieces (cartons × pcs_per_carton)';
```

---

## 🔧 BACKEND API CHANGES

### 1. PO Kain Creation with Pallet Calculator

**Endpoint**: `POST /api/v1/purchasing/po-kain`

**New Request Schema**:
```json
{
  "article_id": 123,
  "target_pallets": 5,
  "delivery_date": "2026-03-15",
  "supplier_id": 45,
  "notes": "W06-2026 production for Belgium"
}
```

**Backend Logic**:
```python
class POKainService:
    @staticmethod
    def create_po_with_pallet_calculation(
        db: Session,
        article_id: int,
        target_pallets: int,
        delivery_date: date,
        supplier_id: int
    ) -> PurchaseOrder:
        """Create PO Kain with automatic pallet-based quantity calculation"""
        
        # 1. Get article packing specs
        article = db.query(Product).filter(Product.id == article_id).first()
        if not article:
            raise HTTPException(status_code=404, detail="Article not found")
        
        if not article.pcs_per_carton or not article.cartons_per_pallet:
            raise HTTPException(
                status_code=400,
                detail=f"Article {article.product_code} missing packing specifications"
            )
        
        # 2. Calculate quantities
        pcs_per_pallet = article.pcs_per_carton * article.cartons_per_pallet
        expected_cartons = target_pallets * article.cartons_per_pallet
        calculated_pcs = target_pallets * pcs_per_pallet
        
        # 3. Create PO
        po = PurchaseOrder(
            po_type="PO_KAIN",
            article_id=article_id,
            target_pallets=target_pallets,
            expected_cartons=expected_cartons,
            calculated_pcs=calculated_pcs,
            quantity=calculated_pcs,  # MO will use this
            delivery_date=delivery_date,
            supplier_id=supplier_id,
            status="DRAFT"
        )
        
        db.add(po)
        db.commit()
        
        return po
```

**Response**:
```json
{
  "po_number": "PO-KAIN-2026-0089",
  "article_code": "40551542",
  "article_name": "AFTONSPARV Bear",
  "packing_specs": {
    "pcs_per_carton": 60,
    "cartons_per_pallet": 8,
    "pcs_per_pallet": 480
  },
  "order_calculation": {
    "target_pallets": 5,
    "expected_cartons": 40,
    "total_pcs": 2400
  },
  "mo_quantity": 2400,
  "status": "DRAFT"
}
```

### 2. Packing Validation Service

**Endpoint**: `POST /api/v1/production/packing/validate-cartons`

**Request**:
```json
{
  "work_order_id": 456,
  "cartons_packed": 16,
  "total_pcs_packed": 960
}
```

**Backend Logic**:
```python
class PackingValidationService:
    @staticmethod
    def validate_carton_packing(
        db: Session,
        work_order_id: int,
        cartons_packed: int,
        total_pcs_packed: int
    ) -> dict:
        """Validate that packing matches article specifications EXACTLY"""
        
        # 1. Get work order and article specs
        wo = db.query(WorkOrder).filter(WorkOrder.id == work_order_id).first()
        article = wo.manufacturing_order.article
        
        # 2. Calculate expected values
        expected_pcs = cartons_packed * article.pcs_per_carton
        variance_pcs = total_pcs_packed - expected_pcs
        variance_percent = (variance_pcs / expected_pcs * 100) if expected_pcs > 0 else 0
        
        # 3. Validation rules
        if variance_percent == 0:
            status = "EXACT_MATCH"
            message = f"✅ Perfect! {cartons_packed} CTN × {article.pcs_per_carton} pcs = {total_pcs_packed} pcs"
            allow_proceed = True
        
        elif abs(variance_percent) <= 1:
            status = "MINOR_VARIANCE"
            message = f"⚠️ Minor variance: {variance_percent:.2f}% ({variance_pcs:+d} pcs)"
            allow_proceed = True  # Allow with warning
        
        else:
            status = "BLOCKED"
            message = f"❌ Variance too high: {variance_percent:.2f}% ({variance_pcs:+d} pcs). Recount required!"
            allow_proceed = False
        
        # 4. Check pallet formation possibility
        can_form_pallets = (cartons_packed % article.cartons_per_pallet == 0)
        complete_pallets = cartons_packed // article.cartons_per_pallet
        remaining_cartons = cartons_packed % article.cartons_per_pallet
        
        return {
            "status": status,
            "message": message,
            "allow_proceed": allow_proceed,
            "validation_details": {
                "cartons_packed": cartons_packed,
                "expected_pcs_per_carton": article.pcs_per_carton,
                "expected_total_pcs": expected_pcs,
                "actual_total_pcs": total_pcs_packed,
                "variance_pcs": variance_pcs,
                "variance_percent": variance_percent
            },
            "pallet_formation": {
                "can_form_complete_pallets": can_form_pallets,
                "complete_pallets": complete_pallets,
                "remaining_cartons": remaining_cartons,
                "cartons_per_pallet": article.cartons_per_pallet
            }
        }
```

### 3. FG Receiving with Pallet Unit

**Endpoint**: `POST /api/v1/warehouse/fg-receipt`

**Request**:
```json
{
  "work_order_id": 456,
  "received_pallets": 2,
  "barcode_scan": ["PLT-2026-00001", "PLT-2026-00002"]
}
```

**Backend Logic**:
```python
class FGReceivingService:
    @staticmethod
    def receive_by_pallet(
        db: Session,
        work_order_id: int,
        received_pallets: int,
        barcode_scan: list[str]
    ) -> dict:
        """Receive finished goods in PALLET unit, auto-calculate cartons & pcs"""
        
        # 1. Get work order and article
        wo = db.query(WorkOrder).filter(WorkOrder.id == work_order_id).first()
        article = wo.manufacturing_order.article
        
        # 2. Auto-calculate quantities
        received_cartons = received_pallets * article.cartons_per_pallet
        received_pcs = received_pallets * (article.pcs_per_carton * article.cartons_per_pallet)
        
        # 3. Validate against packing output
        if wo.pallets_formed != received_pallets:
            raise HTTPException(
                status_code=400,
                detail=f"Pallet mismatch: Packing formed {wo.pallets_formed} pallets, but receiving {received_pallets} pallets"
            )
        
        # 4. Create FG stock record
        fg_stock = FGStock(
            article_id=article.id,
            mo_number=wo.manufacturing_order.mo_number,
            stock_pallets=received_pallets,
            stock_cartons=received_cartons,
            stock_pcs=received_pcs,
            location="FG-WAREHOUSE",
            pallet_barcodes=barcode_scan,
            received_date=datetime.utcnow()
        )
        
        db.add(fg_stock)
        db.commit()
        
        return {
            "receipt_id": fg_stock.id,
            "article_code": article.product_code,
            "received_quantity": {
                "pallets": received_pallets,
                "cartons": received_cartons,
                "pcs": received_pcs
            },
            "display_format": f"{received_pallets} PLT / {received_cartons} CTN / {received_pcs:,} PCS",
            "pallet_barcodes": barcode_scan
        }
```

---

## 🎨 FRONTEND UI CHANGES

### 1. PO Kain Creation Page - Pallet Calculator Widget

```tsx
// Component: PalletCalculatorWidget.tsx

interface PalletCalculatorProps {
  article: Article;
  onCalculate: (result: PalletCalculation) => void;
}

function PalletCalculatorWidget({ article, onCalculate }: PalletCalculatorProps) {
  const [targetPallets, setTargetPallets] = useState<number>(1);
  
  // Auto-calculate when pallets change
  const calculation = useMemo(() => {
    const expectedCartons = targetPallets * article.cartons_per_pallet;
    const totalPcs = targetPallets * article.pcs_per_pallet;
    
    return {
      targetPallets,
      expectedCartons,
      totalPcs,
      moQuantity: totalPcs
    };
  }, [targetPallets, article]);
  
  return (
    <Card className="bg-blue-50 border-blue-300">
      <div className="p-6">
        <h3 className="text-lg font-bold text-blue-900 mb-4">
          📦 Pallet Calculator
        </h3>
        
        {/* Article Packing Specs */}
        <div className="bg-white rounded p-4 mb-4">
          <p className="text-sm text-gray-600 mb-2">Packing Specifications:</p>
          <div className="grid grid-cols-3 gap-4 text-center">
            <div>
              <p className="text-xs text-gray-500">Pcs/Carton</p>
              <p className="text-2xl font-bold text-gray-900">
                {article.pcs_per_carton}
              </p>
            </div>
            <div>
              <p className="text-xs text-gray-500">Cartons/Pallet</p>
              <p className="text-2xl font-bold text-gray-900">
                {article.cartons_per_pallet}
              </p>
            </div>
            <div>
              <p className="text-xs text-gray-500">Pcs/Pallet</p>
              <p className="text-2xl font-bold text-blue-600">
                {article.pcs_per_pallet}
              </p>
            </div>
          </div>
        </div>
        
        {/* Pallet Input */}
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            How many pallets to produce?
          </label>
          <input
            type="number"
            min="1"
            value={targetPallets}
            onChange={(e) => setTargetPallets(parseInt(e.target.value) || 1)}
            className="w-full px-4 py-3 text-2xl font-bold text-center border-2 border-blue-300 rounded"
          />
        </div>
        
        {/* Calculation Result */}
        <div className="bg-gradient-to-r from-blue-500 to-indigo-600 text-white rounded p-4">
          <p className="text-xs opacity-80 mb-2">Production Order:</p>
          <div className="grid grid-cols-3 gap-2 text-center">
            <div>
              <p className="text-xs opacity-80">Pallets</p>
              <p className="text-xl font-bold">{calculation.targetPallets}</p>
            </div>
            <div>
              <p className="text-xs opacity-80">Cartons</p>
              <p className="text-xl font-bold">{calculation.expectedCartons}</p>
            </div>
            <div>
              <p className="text-xs opacity-80">Total Pcs</p>
              <p className="text-2xl font-bold">{calculation.totalPcs.toLocaleString()}</p>
            </div>
          </div>
        </div>
        
        {/* MO Quantity Display */}
        <div className="mt-4 p-3 bg-green-100 border-2 border-green-400 rounded">
          <p className="text-sm text-green-800 font-semibold">
            ✅ MO Quantity: {calculation.moQuantity.toLocaleString()} pcs
          </p>
          <p className="text-xs text-green-700 mt-1">
            This quantity is guaranteed to form complete pallets
          </p>
        </div>
      </div>
    </Card>
  );
}
```

### 2. Packing Page - Carton/Pallet Validation

```tsx
// Component: PackingValidation.tsx

function PackingValidation({ workOrder, article }: Props) {
  const [cartonsPacked, setCartonsPacked] = useState<number>(0);
  const [totalPcs, setTotalPcs] = useState<number>(0);
  const [validation, setValidation] = useState<ValidationResult | null>(null);
  
  const handleValidate = async () => {
    const result = await api.packing.validateCartons({
      work_order_id: workOrder.id,
      cartons_packed: cartonsPacked,
      total_pcs_packed: totalPcs
    });
    
    setValidation(result);
  };
  
  return (
    <div className="space-y-4">
      {/* Input Section */}
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="text-sm font-medium">Cartons Packed</label>
          <input
            type="number"
            value={cartonsPacked}
            onChange={(e) => setCartonsPacked(parseInt(e.target.value) || 0)}
            className="w-full px-3 py-2 border rounded"
          />
        </div>
        <div>
          <label className="text-sm font-medium">Total Pcs</label>
          <input
            type="number"
            value={totalPcs}
            onChange={(e) => setTotalPcs(parseInt(e.target.value) || 0)}
            className="w-full px-3 py-2 border rounded"
          />
        </div>
      </div>
      
      <button
        onClick={handleValidate}
        className="w-full px-4 py-3 bg-blue-600 text-white font-semibold rounded"
      >
        🔍 Validate Packing
      </button>
      
      {/* Validation Result */}
      {validation && (
        <div className={`p-4 rounded border-2 ${
          validation.status === 'EXACT_MATCH' ? 'bg-green-50 border-green-400' :
          validation.status === 'MINOR_VARIANCE' ? 'bg-yellow-50 border-yellow-400' :
          'bg-red-50 border-red-400'
        }`}>
          <p className="font-semibold mb-2">{validation.message}</p>
          
          {/* Pallet Formation Check */}
          {validation.pallet_formation.can_form_complete_pallets ? (
            <div className="mt-3 p-3 bg-green-100 rounded">
              <p className="text-sm font-semibold text-green-800">
                ✅ Can form {validation.pallet_formation.complete_pallets} complete pallet(s)
              </p>
            </div>
          ) : (
            <div className="mt-3 p-3 bg-orange-100 rounded">
              <p className="text-sm font-semibold text-orange-800">
                ⚠️ Incomplete pallet: {validation.pallet_formation.remaining_cartons} carton(s) remaining
              </p>
              <p className="text-xs text-orange-700 mt-1">
                Need {article.cartons_per_pallet - validation.pallet_formation.remaining_cartons} more carton(s) for complete pallet
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
```

### 3. FG Stock Page - Multi-UOM Display

```tsx
// Component: FGStockDisplay.tsx

function FGStockDisplay({ stock }: { stock: FGStock }) {
  return (
    <div className="border rounded-lg p-4 hover:shadow-lg transition">
      {/* Article Info */}
      <div className="mb-3">
        <p className="font-semibold text-gray-900">{stock.article_code}</p>
        <p className="text-sm text-gray-600">{stock.article_name}</p>
      </div>
      
      {/* Multi-UOM Display */}
      <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded p-3 mb-3">
        <p className="text-xs text-gray-600 mb-2">Stock Quantity:</p>
        <div className="flex items-center justify-between">
          {/* Primary: Pallets */}
          <div className="text-center">
            <p className="text-2xl font-bold text-blue-600">{stock.stock_pallets}</p>
            <p className="text-xs text-gray-600">Pallets</p>
          </div>
          
          <span className="text-gray-400 text-xl">=</span>
          
          {/* Secondary: Cartons */}
          <div className="text-center">
            <p className="text-xl font-bold text-indigo-600">{stock.stock_cartons}</p>
            <p className="text-xs text-gray-600">Cartons</p>
          </div>
          
          <span className="text-gray-400 text-xl">=</span>
          
          {/* Tertiary: Pcs */}
          <div className="text-center">
            <p className="text-lg font-bold text-gray-900">{stock.stock_pcs.toLocaleString()}</p>
            <p className="text-xs text-gray-600">Pcs</p>
          </div>
        </div>
      </div>
      
      {/* Compact Display Format */}
      <div className="text-center p-2 bg-gray-100 rounded">
        <p className="text-sm font-mono font-semibold text-gray-700">
          {stock.stock_pallets} PLT / {stock.stock_cartons} CTN / {stock.stock_pcs.toLocaleString()} PCS
        </p>
      </div>
    </div>
  );
}
```

---

## 📝 IMPLEMENTATION ROADMAP

### Phase 1: Database Migration (Day 1) - 4 hours

**Tasks**:
1. ✅ Create migration script: `add_pallet_specifications.sql`
2. ✅ Add columns to `products` table
3. ✅ Add columns to `purchase_orders` table
4. ✅ Add columns to `work_orders` table
5. ✅ Add columns to `fg_stock` table
6. ✅ Test migration on staging database

**Deliverable**: Database schema updated with pallet fields

---

### Phase 2: Masterdata Import (Day 1-2) - 6 hours

**Tasks**:
1. ✅ Extract pcs_per_carton from Packing.xlsx BOM
2. ✅ Extract cartons_per_pallet from Packing.xlsx BOM
3. ✅ Create Python script: `import_pallet_specs.py`
4. ✅ Validate extracted data (check for nulls, negatives)
5. ✅ Bulk update `products` table with pallet specs
6. ✅ Verify: All 211+ articles have pallet specs

**Deliverable**: All articles populated with packing specifications

---

### Phase 3: Backend API (Day 2-3) - 8 hours

**Tasks**:
1. ✅ Create `POKainService.create_po_with_pallet_calculation()`
2. ✅ Create `PackingValidationService.validate_carton_packing()`
3. ✅ Create `FGReceivingService.receive_by_pallet()`
4. ✅ Update existing PO Kain endpoint
5. ✅ Add new validation endpoints
6. ✅ Write unit tests (80%+ coverage)

**Deliverable**: 3 new backend services operational

---

### Phase 4: Frontend UI (Day 3-5) - 12 hours

**Tasks**:
1. ✅ Create `PalletCalculatorWidget.tsx` component
2. ✅ Update `CreatePOPage.tsx` to use pallet calculator
3. ✅ Create `PackingValidation.tsx` component
4. ✅ Update `PackingInputPage.tsx` with validation
5. ✅ Update `FGStockPage.tsx` with multi-UOM display
6. ✅ Test all UI flows end-to-end

**Deliverable**: 3 pages updated with pallet system

---

### Phase 5: Testing & Deployment (Day 5) - 4 hours

**Tasks**:
1. ✅ E2E test: PO Kain creation with 3 pallets → MO generation
2. ✅ E2E test: Packing 16 cartons → 2 pallets → FG receiving
3. ✅ E2E test: FG stock display shows pallets/cartons/pcs
4. ✅ UAT with Purchasing team (3 POs)
5. ✅ UAT with Packing team (2 work orders)
6. ✅ Production deployment

**Deliverable**: Pallet system live in production

---

## ✅ SUCCESS CRITERIA

### Technical Metrics

1. **Database**: 100% of articles have pallet specs (no nulls)
2. **PO Creation**: All new PO Kain have `target_pallets` field populated
3. **Validation**: Packing validation blocks if variance > 1%
4. **Display**: FG stock shows all 3 UOMs (pallets/cartons/pcs)
5. **Performance**: Pallet calculation < 200ms response time

### Business Metrics

1. **PO Accuracy**: 100% of POs are multiples of pcs_per_pallet
2. **Packing Compliance**: Zero partial pallets formed
3. **FG Receiving**: All receipts in PALLET unit (not pcs)
4. **Shipping Efficiency**: Container loading planned by pallet count
5. **User Adoption**: 100% of Purchasing & Packing staff using pallet system by Week 2

### User Experience

1. **Purchasing**: "Easy to calculate how many pallets to order"
2. **Packing**: "System prevents mistakes with auto-validation"
3. **Warehouse**: "Clear visibility of pallets, cartons, and pcs"
4. **Management**: "Optimized shipping with pallet-based planning"

---

## 🎓 USER TRAINING

### Purchasing Department (1 hour)

**Topics**:
1. Understanding pallet hierarchy (pallet → carton → pcs)
2. Using pallet calculator in PO Kain creation
3. How to determine optimal pallet quantity
4. Week & Destination assignment workflow

**Hands-on Exercise**:
- Create PO for 3 pallets of AFTONSPARV (480 pcs/pallet)
- Verify MO auto-generates with 1,440 pcs quantity
- Observe calculation breakdown

---

### Packing Department (1 hour)

**Topics**:
1. Receiving from Finishing in PCS
2. Packing into cartons (exact quantity required)
3. Stacking cartons on pallets (cartons_per_pallet)
4. Using validation tool before transfer to FG

**Hands-on Exercise**:
- Pack 960 pcs into 16 cartons (60 pcs each)
- Validate using system tool
- Form 2 pallets (8 cartons each)
- Scan pallet barcodes for FG transfer

---

### Warehouse Department (30 minutes)

**Topics**:
1. Receiving finished goods in PALLET unit
2. Scanning pallet barcodes
3. Understanding multi-UOM display
4. Stock rotation by pallet

**Hands-on Exercise**:
- Receive 2 pallets from Packing
- Verify auto-calculation of cartons & pcs
- View FG stock display (pallets/cartons/pcs)

---

## 📊 REPORTING & ANALYTICS

### New Reports

1. **Pallet Production Report** (Daily)
   - Articles produced
   - Pallets formed
   - Cartons packed
   - Packing efficiency (target vs actual)

2. **FG Stock by Pallet** (Real-time)
   - Total pallets in warehouse
   - Pallets by article
   - Pallets by week/destination
   - Shipping-ready pallets

3. **PO Pallet Planning** (Weekly)
   - Upcoming POs with pallet targets
   - Material requirements by pallet
   - Container optimization recommendations

---

## 🔒 VALIDATION RULES

### PO Kain Creation

```
RULE 1: target_pallets MUST BE > 0
RULE 2: quantity MUST EQUAL (target_pallets × pcs_per_pallet)
RULE 3: article MUST HAVE pallet specs (not null)
```

### Packing Validation

```
RULE 1: cartons_packed × pcs_per_carton = total_pcs_packed (exact match)
RULE 2: variance_percent MUST BE ≤ 1% (block if > 1%)
RULE 3: cartons_packed SHOULD BE multiple of cartons_per_pallet (warning if not)
```

### FG Receiving

```
RULE 1: received_pallets MUST MATCH work_order.pallets_formed
RULE 2: pallet_barcodes MUST BE unique (no duplicates)
RULE 3: stock calculation MUST BE consistent (pcs = pallets × pcs_per_pallet)
```

---

## 📞 SUPPORT & TROUBLESHOOTING

### Common Issues

**Issue 1**: "Article missing pallet specifications"  
**Solution**: Run masterdata import script to populate pcs_per_carton & cartons_per_pallet

**Issue 2**: "Packing validation failing with 2% variance"  
**Solution**: Recount cartons and pcs, ensure exact quantities entered

**Issue 3**: "Partial pallet cannot be transferred"  
**Solution**: Complete remaining cartons to form full pallet, or adjust MO quantity

**Issue 4**: "FG stock shows negative cartons"  
**Solution**: Database inconsistency, run stock reconciliation script

---

## ✅ COMPLETION CHECKLIST

**Analysis Phase** (February 6, 2026):
- [x] Analyzed Packing.xlsx for pallet ratios
- [x] Analyzed Carton.xlsx for pcs_per_carton
- [x] Created comprehensive implementation guide
- [x] Documented business process flow

**Implementation Phase** (Pending):
- [ ] Database schema migration
- [ ] Masterdata import (pallet specs)
- [ ] Backend API services
- [ ] Frontend UI components
- [ ] End-to-end testing
- [ ] User training
- [ ] Production deployment

**Post-Deployment**:
- [ ] Monitor first 10 POs with pallet system
- [ ] Collect user feedback
- [ ] Optimize container loading algorithm
- [ ] Integrate with shipping module

---

**Document Version**: 1.0  
**Last Updated**: February 6, 2026  
**Next Review**: After Phase 1 completion  
**Owner**: IT Fullstack Developer (Claude AI)
