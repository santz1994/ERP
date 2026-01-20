# 📷 BARCODE SCANNER SYSTEM

**Feature**: Alternative barcode scanner for warehouse receiving and picking operations  
**Locations**: Warehouse & Finishgoods  
**Future**: RFID integration planned  
**Status**: ✅ Production Ready

---

## 🎯 OVERVIEW

The Barcode Scanner System provides efficient goods receiving and picking operations using camera-based or manual barcode input. This system eliminates manual data entry errors and speeds up warehouse operations.

### **Key Features**
- 📷 **Camera Scanner**: Real-time barcode scanning using device camera
- ⌨️ **Manual Input**: Fallback for cameras or damaged barcodes
- ✅ **Validation**: Instant product verification before transaction
- 📊 **FIFO Logic**: Automatic First-In-First-Out stock allocation
- 📝 **History Tracking**: Complete audit trail of all scans
- 🔒 **Permission-Based**: Integrated with UAC/RBAC system

---

## 🏗️ ARCHITECTURE

### Backend API

**Module**: `app/api/v1/barcode.py`  
**Endpoints**: 5 REST APIs

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/barcode/validate` | POST | Validate barcode before transaction |
| `/barcode/receive` | POST | Receive goods (increase inventory) |
| `/barcode/pick` | POST | Pick goods (decrease inventory with FIFO) |
| `/barcode/history` | GET | Get scanning history |
| `/barcode/stats` | GET | Get daily statistics |

### Frontend Components

**Component**: `erp-ui/frontend/src/components/BarcodeScanner.tsx`  
**Integration**: WarehousePage.tsx (✅ Complete), FinishgoodsPage.tsx (✅ Complete)  
**Library**: html5-qrcode (camera scanning)

---

## 📱 USAGE

### 1. Receiving Goods

**Use Case**: When goods arrive from suppliers

**Steps**:
1. Navigate to Warehouse page
2. Click "Barcode Scanner" tab
3. Select "Receive Goods" mode
4. Scan barcode or enter manually
5. System validates product
6. Enter quantity received
7. Add optional notes (PO reference, etc.)
8. Submit transaction
9. System creates:
   - Stock lot with auto-generated lot number
   - Stock move record
   - Updates inventory quantity
   - Audit log entry

**Auto-Generated Lot Number Format**: `{PRODUCT-CODE}-{YYYYMMDD}-{XXX}`  
Example: `FAB-VEL-BLU-20260120-001`

### 2. Picking Goods

**Use Case**: When taking goods for production

**Steps**:
1. Navigate to Warehouse page
2. Click "Barcode Scanner" tab
3. Select "Pick Goods" mode
4. Scan barcode or enter manually
5. System validates available stock
6. Enter quantity to pick
7. System applies FIFO logic (oldest lots first)
8. Submit transaction
9. System:
   - Picks from multiple lots if needed
   - Creates stock move record
   - Updates inventory quantities
   - Returns lot numbers used

**FIFO Logic**: Automatically picks from oldest lots first

---

## 🔧 TECHNICAL IMPLEMENTATION

### Backend Logic

```python
# Validation
POST /api/v1/barcode/validate
{
  "barcode": "FAB-VEL-BLU",
  "operation": "receive",  // or "pick"
  "location": "warehouse"  // or "finishgoods"
}

# Response
{
  "valid": true,
  "product_id": 1,
  "product_code": "FAB-VEL-BLU",
  "product_name": "Velboa Blue Fabric",
  "current_qty": 5000.0,
  "location": "warehouse",
  "lot_number": "FAB-VEL-BLU-20260120-001",
  "message": "Barcode validated successfully"
}

# Receive
POST /api/v1/barcode/receive
{
  "barcode": "FAB-VEL-BLU",
  "qty": 500,
  "location": "warehouse",
  "lot_number": null,  // auto-generated if null
  "po_reference": "PO-2024-001",
  "notes": "Shipment from Supplier A"
}

# Pick (with FIFO)
POST /api/v1/barcode/pick
{
  "barcode": "FAB-VEL-BLU",
  "qty": 300,
  "location": "warehouse",
  "work_order_id": 123,
  "destination": "cutting",
  "notes": "For WO-123"
}

# Response
{
  "success": true,
  "message": "Picked 300 Meter of Velboa Blue Fabric",
  "product": {...},
  "picked_lots": [
    {"lot_number": "FAB-VEL-BLU-20260115-001", "qty": 200},
    {"lot_number": "FAB-VEL-BLU-20260118-001", "qty": 100}
  ],
  "location": "warehouse",
  "timestamp": "2026-01-20T10:30:00"
}
```

### Frontend Component

```typescript
import BarcodeScanner from '../components/BarcodeScanner';

<BarcodeScanner
  onScan={(barcode) => handleBarcodeScan(barcode)}
  operation="receive"  // or "pick"
  location="warehouse"  // or "finishgoods"
/>
```

**Camera Requirements**:
- Modern browser (Chrome, Edge, Safari, Firefox)
- HTTPS connection (camera access requires secure context)
- User permission for camera access

**Fallback**: Manual input always available if camera fails

---

## 📊 DATABASE SCHEMA

### Tables Used

1. **stock_lots** - Lot tracking
   - `lot_number`: Auto-generated unique identifier
   - `product_id`: Product reference
   - `quantity`: Initial quantity
   - `created_at`: Receipt timestamp (for FIFO)

2. **stock_moves** - Transaction history
   - `move_type`: 'receive' or 'pick'
   - `quantity`: Amount moved
   - `from_location`: Source
   - `to_location`: Destination
   - `reference`: PO/WO reference
   - `notes`: Additional info

3. **stock_quants** - Current inventory
   - `product_id`: Product reference
   - `location`: Storage location
   - `lot_id`: Lot reference
   - `quantity`: Current quantity
   - `reserved_quantity`: Allocated stock

---

## 🔒 SECURITY

### Permissions Required

- **Module**: WAREHOUSE or FINISHGOODS
- **Permission**: VIEW (validate), CREATE (receive), UPDATE (pick)
- **Implementation**: FastAPI dependencies

```python
@router.post("/receive")
async def receive_goods(
    request: ReceiveGoodsRequest,
    current_user: User = Depends(require_module_access(ModuleName.WAREHOUSE))
):
    # Only users with Warehouse module access can receive goods
```

### Audit Trail

All barcode transactions are logged in:
- **audit_logs** table (action, user, timestamp, details)
- **stock_moves** table (complete transaction history)

---

## 📈 STATISTICS & REPORTING

### Daily Stats Endpoint

```
GET /api/v1/barcode/stats

Response:
{
  "today": {
    "date": "2026-01-20",
    "receives": {
      "count": 45,
      "total_qty": 15000
    },
    "picks": {
      "count": 38,
      "total_qty": 12500
    },
    "unique_products": 23
  }
}
```

### History Endpoint

```
GET /api/v1/barcode/history?location=warehouse&limit=50

Returns last 50 scans with:
- Product info
- Operation type
- Quantity
- Timestamp
- User who scanned
```

---

## 🎯 USE CASES

### 1. Raw Material Receiving
**Scenario**: Fabric delivery from supplier  
**Operation**: Receive  
**Location**: Warehouse  
**Benefit**: Instant inventory update with lot tracking

### 2. Production Material Picking
**Scenario**: Cutting department needs fabric  
**Operation**: Pick  
**Location**: Warehouse  
**Benefit**: FIFO compliance, accurate stock deduction

### 3. Finished Goods Receiving
**Scenario**: Completed products from Packing  
**Operation**: Receive  
**Location**: Finishgoods  
**Benefit**: Track completion quantities with lot numbers

### 4. Shipment Picking
**Scenario**: Preparing customer order  
**Operation**: Pick  
**Location**: Finishgoods  
**Benefit**: Ensure oldest products ship first (FIFO)

---

## 🚀 FUTURE ENHANCEMENTS

### Planned: RFID Integration

**Timeline**: Phase 13 (Q2 2026)

**Features**:
- Bulk scanning (multiple items simultaneously)
- Longer read range (up to 10 meters)
- No line-of-sight requirement
- Faster processing (100+ items/second)
- Integration with existing barcode system

**Hardware Required**:
- RFID readers (handheld or fixed)
- RFID tags for products
- Gateway for data transmission

**Implementation**:
- Add RFID endpoints alongside barcode
- Support both barcode and RFID simultaneously
- Gradual migration strategy

---

## 💡 BEST PRACTICES

### For Operators

1. **Clean Barcodes**: Ensure barcodes are not damaged or dirty
2. **Good Lighting**: Camera scanning requires adequate light
3. **Stable Position**: Hold camera steady for 2-3 seconds
4. **Verify Display**: Always check product name after scan
5. **Double-Check Quantity**: Confirm qty before submitting

### For Administrators

1. **Standard Barcodes**: Use Code128 or QR codes
2. **Print Quality**: High-resolution barcode labels
3. **Consistent Format**: Product code = barcode value
4. **Regular Audits**: Compare physical vs system stock
5. **Train Staff**: Proper scanner usage and troubleshooting

### For Developers

1. **Error Handling**: Graceful camera permission failures
2. **Validation**: Always validate before write operations
3. **FIFO Logic**: Maintain strict oldest-first picking
4. **Audit Logs**: Log all transactions for traceability
5. **Performance**: Optimize database queries for speed

---

## 🐛 TROUBLESHOOTING

### Camera Not Working

**Issue**: "Camera not detected" message  
**Solutions**:
1. Check browser permissions (Settings → Privacy → Camera)
2. Ensure HTTPS connection (camera requires secure context)
3. Try different browser (Chrome/Edge recommended)
4. Use manual input as fallback

### Barcode Not Scanning

**Issue**: Barcode detected but not validating  
**Solutions**:
1. Check barcode format matches product code exactly
2. Ensure product exists in system
3. Verify barcode quality (not damaged/faded)
4. Try manual input to test validation logic

### Insufficient Stock Error

**Issue**: "Insufficient stock for picking"  
**Solutions**:
1. Check current inventory via Stock Inventory tab
2. Verify location (warehouse vs finishgoods)
3. Check if stock is reserved for other orders
4. Contact warehouse admin to adjust stock

---

## 📝 NOTES

- Barcode format must match product code in database
- System assumes 1 barcode = 1 product (future: support multiple formats)
- Lot numbers are auto-generated using date-based sequence
- FIFO logic ensures oldest stock is used first
- Manual input available when camera unavailable
- Mobile app will have native barcode scanning (better performance)
- RFID integration planned for Phase 13

---

**Last Updated**: January 20, 2026  
**Feature**: Barcode Scanner System  
**Status**: Production Ready  
**Next**: RFID Integration (Phase 13)
