# FinishGood Barcode Format Specification

**Version**: 1.0  
**Date**: 26 January 2026  
**Format Type**: IKEA-Style Article Barcode  
**GTIN-13 Compatible**: Yes (encoded in barcode)  

---

## 📋 Barcode Structure

### Format Overview

```
BARCODE = [MO_ID]-[PRODUCT_CODE]-[BOX_NUMBER]
Example: 501-PRODA01-0001
```

### Component Breakdown

| Component | Length | Format | Description | Example |
|-----------|--------|--------|-------------|---------|
| **MO_ID** | 3-4 digits | Numeric | Manufacturing Order ID | 501 |
| **PRODUCT_CODE** | 8-12 chars | Alphanumeric | Product code (IKEA article) | PRODA01 |
| **BOX_NUMBER** | 4 digits | Numeric (zero-padded) | Sequential box number | 0001 |

### Full Barcode Examples

```
501-PRODA01-0001   (Box 1 of MO 501, Product PRODA01)
501-PRODA01-0025   (Box 25 of MO 501, Product PRODA01)
1002-TSHIRT-XL-0001 (Box 1 of MO 1002, T-Shirt XL)
```

---

## 🔤 Encoding Standards

### Barcode Types Supported

1. **Code 128** (Primary)
   - Supports full alphanumeric character set
   - Compatible with mobile scanners
   - High-density encoding

2. **Code 39**
   - Optional, for backward compatibility
   - Supports: A-Z, 0-9, space, - . * $ / + %

3. **QR Code** (Optional)
   - Alternative format
   - Better error correction
   - Can include additional metadata

### Character Set

```
Allowed Characters:
- Digits: 0-9
- Uppercase: A-Z
- Separators: hyphen (-)

Not Allowed:
- Lowercase letters
- Special characters (except -)
- Spaces
```

---

## 📊 Barcode Label Specifications

### Label Format (Thermal Printer)

```
┌─────────────────────────────────┐
│ ┌─┐  ┌─ ─┐  ┌─────┐  ┌──┐      │  ← Barcode image (Code 128)
│ │ │  │   │  │     │  │  │      │     Width: 80mm, Height: 30mm
│ └─┘  └─ ─┘  └─────┘  └──┘      │
│                                  │
│  501-PRODA01-0001               │  ← Human readable text
│                                  │
│  MO: 501                         │
│  Product: T-Shirt XL Blue        │
│  Article: PRODA01               │
│  Box: 1 of 25                    │
│  Units: 20                       │
│  Date: 26-01-2026               │
│                                  │
│  ▪▪▪▪▪▪▪▪▪▪▪▪                  │  ← Reception signature line
│  Sign: ____________             │
└─────────────────────────────────┘
```

### Print Settings

- **Printer Type**: Thermal printer (300 DPI recommended)
- **Label Size**: 100mm × 150mm (4" × 6")
- **Font Size**: 12pt (human readable text)
- **Barcode Height**: 30mm
- **Paper**: Adhesive thermal labels

---

## 🔍 Barcode Generation

### Backend Generation (Python)

```python
import barcode
from barcode.writer import ImageWriter

def generate_finishgood_barcode(mo_id: int, product_code: str, box_number: int) -> bytes:
    """Generate Code 128 barcode for FinishGood box."""
    
    # Format barcode string
    barcode_str = f"{mo_id}-{product_code}-{box_number:04d}"
    
    # Generate Code 128 barcode
    ean = barcode.get_barcode_class('code128')
    barcode_obj = ean(barcode_str, writer=ImageWriter())
    
    # Save to bytes
    image_data = barcode_obj.render()
    return image_data
```

### Thermal Printer Integration

```python
def print_finishgood_label(
    mo_id: int,
    product_code: str,
    box_number: int,
    product_name: str,
    quantity: int,
    print_quantity: int = 1
):
    """Print thermal label for FinishGood box."""
    
    # Generate barcode
    barcode_str = f"{mo_id}-{product_code}-{box_number:04d}"
    barcode_bytes = generate_finishgood_barcode(mo_id, product_code, box_number)
    
    # Format label content
    label_content = f"""
    {barcode_str}
    
    MO: {mo_id}
    Product: {product_name}
    Article: {product_code}
    Box: {box_number}
    Units: {quantity}
    Date: {datetime.now().strftime('%d-%m-%Y')}
    """
    
    # Send to printer (requires CUPS or Windows Print Spooler)
    # Implementation varies by printer type
    printer.print_image(barcode_bytes)
    printer.print_text(label_content)
```

---

## 📱 Mobile Scanner Reading

### Barcode Scanning Process

```typescript
const handleBarCodeScanned = ({ type, data }: { type: string; data: string }) => {
  // Raw data from scanner: "501-PRODA01-0001"
  
  // Parse barcode components
  const parts = data.split('-');
  
  if (parts.length !== 3) {
    throw new Error('Invalid barcode format');
  }
  
  const [moIdStr, productCode, boxNumberStr] = parts;
  const moId = parseInt(moIdStr);
  const boxNumber = parseInt(boxNumberStr);
  
  // Validate ranges
  if (moId < 1 || moId > 99999) throw new Error('Invalid MO ID');
  if (boxNumber < 1 || boxNumber > 9999) throw new Error('Invalid box number');
  if (!productCode.match(/^[A-Z0-9-]+$/)) throw new Error('Invalid product code');
  
  // Call API to validate and get product info
  const productInfo = await validateBarcode(data);
  
  return {
    moId,
    productCode,
    boxNumber,
    productInfo
  };
};
```

---

## 🔐 Validation Rules

### Mobile App Validation

```typescript
interface BarcodeValidation {
  valid: boolean;
  errors: string[];
  warnings: string[];
}

function validateBarcode(barcode: string): BarcodeValidation {
  const errors: string[] = [];
  const warnings: string[] = [];
  
  // Check format
  if (!barcode.includes('-')) {
    errors.push('Missing separators (-) in barcode');
    return { valid: false, errors, warnings };
  }
  
  const parts = barcode.split('-');
  if (parts.length !== 3) {
    errors.push(`Expected 3 parts, got ${parts.length}`);
    return { valid: false, errors, warnings };
  }
  
  const [moIdStr, productCode, boxNumberStr] = parts;
  
  // Validate MO ID
  const moId = parseInt(moIdStr);
  if (isNaN(moId)) {
    errors.push('MO ID must be numeric');
  } else if (moId < 1 || moId > 99999) {
    errors.push('MO ID out of range (1-99999)');
  }
  
  // Validate product code
  if (!productCode.match(/^[A-Z0-9-]{3,12}$/)) {
    errors.push('Product code invalid (3-12 alphanumeric/hyphen)');
  }
  
  // Validate box number
  const boxNumber = parseInt(boxNumberStr);
  if (isNaN(boxNumber)) {
    errors.push('Box number must be numeric');
  } else if (boxNumber < 1 || boxNumber > 9999) {
    errors.push('Box number out of range (1-9999)');
  } else if (boxNumberStr !== boxNumber.toString().padStart(4, '0')) {
    warnings.push('Box number not zero-padded (auto-correcting)');
  }
  
  return {
    valid: errors.length === 0,
    errors,
    warnings
  };
}
```

### Server-Side Validation

```python
def validate_barcode(barcode_str: str) -> dict:
    """Validate barcode format and content on backend."""
    
    import re
    
    # Check format
    pattern = r'^(\d{1,4})-([A-Z0-9-]{3,12})-(\d{4})$'
    match = re.match(pattern, barcode_str)
    
    if not match:
        raise ValueError(f"Invalid barcode format: {barcode_str}")
    
    mo_id, product_code, box_number = match.groups()
    mo_id = int(mo_id)
    box_number = int(box_number)
    
    # Check MO exists
    mo = db.query(ManufacturingOrder).filter(
        ManufacturingOrder.id == mo_id
    ).first()
    
    if not mo:
        raise ValueError(f"Manufacturing Order {mo_id} not found")
    
    # Check product matches MO
    if product_code not in [item.product_code for item in mo.items]:
        raise ValueError(f"Product {product_code} not in MO {mo_id}")
    
    # Check box number in range
    mo_item = next(item for item in mo.items if item.product_code == product_code)
    expected_boxes = math.ceil(mo_item.quantity / mo_item.unit_per_box)
    
    if box_number > expected_boxes:
        raise ValueError(f"Box {box_number} exceeds expected {expected_boxes} boxes")
    
    return {
        'valid': True,
        'mo_id': mo_id,
        'product_code': product_code,
        'box_number': box_number,
        'expected_quantity': mo_item.unit_per_box
    }
```

---

## 📈 Barcode Database Schema

### Barcode History Table

```sql
CREATE TABLE barcode_scans (
  scan_id SERIAL PRIMARY KEY,
  barcode VARCHAR(50) NOT NULL,
  mo_id INT NOT NULL,
  product_code VARCHAR(12) NOT NULL,
  box_number INT NOT NULL,
  scanned_at TIMESTAMP NOT NULL,
  user_id INT NOT NULL,
  action VARCHAR(20) NOT NULL,  -- 'scan', 'verify', 'confirm'
  location VARCHAR(20),
  quantity_verified INT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  
  FOREIGN KEY (mo_id) REFERENCES manufacturing_orders(id),
  FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE INDEX idx_barcode_scans_mo ON barcode_scans(mo_id);
CREATE INDEX idx_barcode_scans_time ON barcode_scans(scanned_at);
```

---

## 🔄 Barcode Lifecycle

### Barcode Creation

```
1. Manufacturing Order Created
   └─ MO ID assigned (e.g., 501)

2. Packing Stage
   ├─ Print labels on thermal printer
   ├─ Barcode: 501-PRODA01-0001
   ├─ Stick on box
   └─ Box ready for FinishGood

3. FinishGood Receipt
   ├─ Warehouse staff scans barcode
   ├─ Mobile app validates
   ├─ Backend records scan
   └─ Inventory updated
```

### Barcode Reusability

- **NOT reusable** - Each barcode is unique per box
- **Archived** - Scan history maintained for audit
- **No duplicate** - Prevents double-counting

---

## 🎯 Quality Assurance

### Barcode Print Quality

- **Quiet Zone**: 3mm minimum margin around barcode
- **X Dimension**: 0.3mm (minimum scannable)
- **Contrast**: Black on white, ΔE ≥ 3.0
- **Clarity**: No smudges, tears, or fading

### Scanning Verification

- **Read Rate**: >99% first attempt
- **False Negatives**: <1% (missed scans)
- **False Positives**: 0% (no wrong reads)

### Testing Checklist

- [ ] Barcode scans on all compatible scanners
- [ ] No scanning errors in production
- [ ] Label adhesive quality
- [ ] Barcode not damaged after packaging
- [ ] Mobile app reads correctly
- [ ] Server validation passes
- [ ] Audit trail captures all scans

---

## 📚 Example Scenarios

### Scenario 1: Standard Receipt

```
MO 501: 500 units T-Shirt XL Blue
Expected: 25 boxes × 20 units/box

Barcodes printed:
501-PRODA01-0001 → Box 1
501-PRODA01-0002 → Box 2
...
501-PRODA01-0025 → Box 25

Mobile app scans all 25 → Confirms receipt
Database records: 25 scans, 500 units total
```

### Scenario 2: Partial Reception

```
Transfer from Packing: 500 units (25 boxes)
Received: Only 23 boxes

Barcodes scanned:
501-PRODA01-0001 to 501-PRODA01-0023

Status: ⚠️ Incomplete (2 boxes missing)
Mobile app warning: "Only 23 of 25 boxes scanned"
User can:
  - Continue scanning if found later
  - Confirm receipt with variance
  - Hold and investigate
```

### Scenario 3: Quality Issue

```
Box 5 damaged during transport
Barcode unreadable

Options:
1. Manual entry: 501-PRODA01-0005
2. Reprint label on new box
3. Document discrepancy in audit trail

Mobile app: Records as manual entry with note
Backend: Flags for manager review
```

---

## 🔗 Integration Points

### With Packing Module
- Generates barcodes at packing stage
- Prints on thermal printer
- Creates barcode master list

### With FinishGood Mobile Screen
- Scans barcode
- Validates format
- Retrieves product info
- Records scan

### With Backend API
- Stores scan records
- Validates against MO
- Updates inventory
- Generates audit trail

### With Reporting
- Barcode scan history per MO
- Receipt accuracy metrics
- Discrepancy analysis

---

## 📞 Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| Barcode won't scan | Poor print quality | Reprint with higher DPI |
| Invalid format error | Incorrect separator | Check format: MO-CODE-BOX |
| Product not found | Wrong MO ID | Verify MO exists in system |
| Box number out of range | Typo in box number | Correct and rescan |
| Duplicate scan | Same box scanned twice | Check scan history |

---

**Last Updated**: 26 January 2026  
**Status**: ✅ Production Ready
