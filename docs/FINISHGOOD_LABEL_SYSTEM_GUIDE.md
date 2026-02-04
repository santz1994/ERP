# 🏷️ FINISH GOOD LABEL SYSTEM
## Complete IKEA Traceability - PO → MO → SPK/WO

---

## 📋 OVERVIEW

Sistem ini menghasilkan label Finish Good yang **LENGKAP** dengan informasi traceability sesuai requirement IKEA:

### ✅ INFORMASI YANG TERCAKUP:

1. **NO PO** (Purchase Order)
   - PO Number
   - PO Type (KAIN, LABEL, ACCESSORIES)
   - Qty Ordered
   - Week target
   - Destination country

2. **NO MO** (Manufacturing Order)
   - MO Batch Number
   - Production Week (IKEA format: WW-YYYY)
   - Qty Planned vs Produced
   - Label Production Date
   - Traceability Code
   - Routing Type

3. **DATESTAMP (Week)**
   - Production Week (e.g., "10-2026")
   - Planned Production Date
   - Actual Start/End Dates
   - Label Date (di physical label)

4. **PRODUCT INFORMATION**
   - Product Code (e.g., 302.213.49)
   - Product Name (e.g., AFTONSPARV)
   - Category (FINISH GOOD)
   - Description

5. **SPK/WO HIERARCHY** (Complete flow)
   - SPK/WO Cutting
   - SPK/WO Embroidery (jika ada)
   - SPK/WO Sewing
   - SPK/WO Finishing
   - SPK/WO Packing
   - Semua dengan: WO number, sequence, dates, status

---

## 🎯 STRUKTUR HIERARKI

```
PO No PO-2026-001 | QTY: 500 pcs | Week: 10-2026 | Dest: Belgium
│
└── MO No MO-20260301-001 (Week 10-2026)
    ├── Qty: 465/450 pcs
    ├── Label Date: 2026-03-05
    ├── Traceability: MO-W10-001-BE
    ├── Route: Route 1
    │
    ├── ✓ WO-CUT-001 - CUTTING
    │   ├── Seq: 1 | Qty: 495 pcs
    │   ├── Start: 2026-03-01
    │   ├── Done: 2026-03-02
    │   └── Stamp: 2026-03-01
    │
    ├── ✓ WO-EMBO-001 - EMBROIDERY
    │   ├── Seq: 2 | Qty: 495 pcs
    │   ├── Start: 2026-03-02
    │   ├── Done: 2026-03-03
    │   └── Stamp: 2026-03-02
    │
    ├── ✓ WO-SEW-001 - SEWING
    │   ├── Seq: 3 | Qty: 517 pcs
    │   ├── Start: 2026-03-03
    │   ├── Done: 2026-03-05
    │   └── Stamp: 2026-03-03
    │
    ├── ✓ WO-FIN-001 - FINISHING
    │   ├── Seq: 4 | Qty: 480 pcs
    │   ├── Start: 2026-03-05
    │   ├── Done: 2026-03-07
    │   └── Stamp: 2026-03-05
    │
    └── ✓ WO-PACK-001 - PACKING
        ├── Seq: 5 | Qty: 465 pcs
        ├── Start: 2026-03-07
        ├── Done: 2026-03-09
        └── Stamp: 2026-03-07
```

---

## 📡 API ENDPOINTS

### 1. Generate Labels (Packing Dept)

**POST** `/api/finish-good-labels/generate`

```json
{
  "mo_id": 123,
  "carton_numbers": ["CTN001", "CTN002", "CTN003"],
  "qty_per_carton": [60, 60, 45]
}
```

**Response**:
```json
{
  "success": true,
  "message": "Generated 3 labels successfully",
  "labels": [
    {
      "fg_barcode": "FG-2026-00123-CTN001",
      "carton_number": "CTN001",
      "qty_in_carton": 60,
      "packing_date": "2026-03-09",
      "product": {
        "product_code": "302.213.49",
        "product_name": "AFTONSPARV",
        "product_category": "FINISH GOOD"
      },
      "purchase_orders": [
        {
          "po_number": "PO-2026-001",
          "po_type": "KAIN",
          "qty_ordered": 500,
          "week": "10-2026",
          "destination": "Belgium",
          "manufacturing_orders": [
            {
              "mo_number": "MO-20260301-001",
              "production_week": "10-2026",
              "qty_planned": 450,
              "qty_produced": 465,
              "label_production_date": "2026-03-05",
              "traceability_code": "MO-W10-001-BE",
              "routing_type": "Route 1",
              "work_orders": [
                {
                  "wo_number": "WO-CUT-001",
                  "department": "CUTTING",
                  "sequence": 1,
                  "target_qty": 495,
                  "actual_start_date": "2026-03-01",
                  "actual_completion_date": "2026-03-02",
                  "production_date_stamp": "2026-03-01"
                },
                {
                  "wo_number": "WO-EMBO-001",
                  "department": "EMBROIDERY",
                  "sequence": 2,
                  "target_qty": 495,
                  "actual_start_date": "2026-03-02",
                  "actual_completion_date": "2026-03-03"
                }
                // ... more WOs
              ]
            }
          ]
        }
      ],
      "total_qty": 165,
      "total_cartons": 3
    }
    // ... 2 more labels
  ]
}
```

---

### 2. Scan Barcode (Warehouse/QC)

**GET** `/api/finish-good-labels/barcode/{barcode}`

**Example**: `/api/finish-good-labels/barcode/FG-2026-00123-CTN001`

**Response**: Same structure as generate (single label)

---

### 3. Print ke Thermal Printer

**POST** `/api/finish-good-labels/print/{mo_id}?carton_number=CTN001`

**Response**:
```json
{
  "success": true,
  "message": "Label ready for printing",
  "print_text": "================================================\nQUTY KARUNIA - FINISH GOOD LABEL\nIKEA TRACEABILITY\n...",
  "label": { /* full label object */ }
}
```

**Print Output** (80mm thermal printer):
```
================================================
QUTY KARUNIA - FINISH GOOD LABEL
IKEA TRACEABILITY
================================================

PRODUCT INFORMATION:
  Code     : 302.213.49
  Name     : AFTONSPARV
  Category : FINISH GOOD

CARTON INFORMATION:
  Barcode  : FG-2026-00123-CTN001
  Carton   : CTN001
  Qty      : 60 pcs
  Packed   : 2026-03-09
  Total    : 165 pcs / 3 CTN

------------------------------------------------
PO No PO-2026-001 | QTY: 500 pcs
Type: KAIN | Week: 10-2026 | Dest: Belgium

  MO No MO-20260301-001 (Week 10-2026)
  Qty: 465/450 pcs
  Label Date: 2026-03-05
  Traceability: MO-W10-001-BE
  Route: Route 1
  Destination: Belgium

    ✓ WO-CUT-001 - CUTTING
       Seq: 1 | Qty: 495 pcs
       Start: 2026-03-01
       Done: 2026-03-02
       Stamp: 2026-03-01

    ✓ WO-EMBO-001 - EMBROIDERY
       Seq: 2 | Qty: 495 pcs
       Start: 2026-03-02
       Done: 2026-03-03
       Stamp: 2026-03-02

    ✓ WO-SEW-001 - SEWING
       Seq: 3 | Qty: 517 pcs
       Start: 2026-03-03
       Done: 2026-03-05
       Stamp: 2026-03-03

    ✓ WO-FIN-001 - FINISHING
       Seq: 4 | Qty: 480 pcs
       Start: 2026-03-05
       Done: 2026-03-07
       Stamp: 2026-03-05

    ✓ WO-PACK-001 - PACKING
       Seq: 5 | Qty: 465 pcs
       Start: 2026-03-07
       Done: 2026-03-09
       Stamp: 2026-03-07

================================================
Generated: 2026-03-09 14:30:00
================================================
```

---

### 4. Preview Label (PPIC/Management)

**GET** `/api/finish-good-labels/mo/{mo_id}/preview`

**Example**: `/api/finish-good-labels/mo/123/preview`

**Response**:
```json
{
  "success": true,
  "message": "Preview generated",
  "label": { /* full label structure */ },
  "print_preview": "... full print text ...",
  "mobile_format": {
    "barcode": "FG-2026-00123-PREVIEW",
    "carton": "PREVIEW",
    "qty": 1,
    "product": {
      "code": "302.213.49",
      "name": "AFTONSPARV"
    },
    "traceability": [
      {
        "po": "PO-2026-001",
        "week": "10-2026",
        "mos": [
          {
            "mo": "MO-20260301-001",
            "week": "10-2026",
            "qty": "465",
            "trace_code": "MO-W10-001-BE",
            "departments": [
              {
                "dept": "CUTTING",
                "wo": "WO-CUT-001",
                "completed": true
              },
              {
                "dept": "EMBROIDERY",
                "wo": "WO-EMBO-001",
                "completed": true
              }
              // ... more depts
            ]
          }
        ]
      }
    ]
  }
}
```

---

### 5. Complete Traceability Query

**GET** `/api/finish-good-labels/traceability/{fg_barcode}`

**Example**: `/api/finish-good-labels/traceability/FG-2026-00123-CTN001`

**Response**:
```json
{
  "success": true,
  "traceability": {
    "fg_barcode": "FG-2026-00123-CTN001",
    "product": {
      "product_code": "302.213.49",
      "product_name": "AFTONSPARV"
    },
    "chain": [
      {
        "po_number": "PO-2026-001",
        "po_type": "KAIN",
        "qty_ordered": "500",
        "week": "10-2026",
        "destination": "Belgium",
        "manufacturing_orders": [
          {
            "mo_number": "MO-20260301-001",
            "production_week": "10-2026",
            "qty_planned": "450",
            "qty_produced": "465",
            "label_date": "2026-03-05",
            "traceability_code": "MO-W10-001-BE",
            "routing": "Route 1",
            "dates": {
              "planned": "2026-03-01",
              "actual_start": "2026-03-01",
              "actual_end": "2026-03-09"
            },
            "work_orders": [
              {
                "wo_number": "WO-CUT-001",
                "department": "CUTTING",
                "sequence": 1,
                "target_qty": "495",
                "dates": {
                  "start": "2026-03-01",
                  "completion": "2026-03-02",
                  "stamp": "2026-03-01"
                },
                "status": "COMPLETED"
              }
              // ... all other WOs
            ]
          }
        ]
      }
    ]
  }
}
```

---

## 🔧 USE CASES

### Use Case 1: Packing Dept Generate Labels

**Scenario**: Admin packing selesai packing MO-20260301-001 menjadi 8 cartons

**Steps**:
1. Admin buka Packing module di mobile app
2. Scan MO barcode atau input MO number
3. Input jumlah carton: 8
4. Input qty per carton: [60, 60, 60, 60, 60, 60, 60, 45]
5. System auto-generate carton numbers: CTN001-CTN008
6. Click [GENERATE LABELS]
7. System call API: POST `/api/finish-good-labels/generate`
8. Response: 8 labels dengan complete traceability
9. Admin print ke thermal printer (connect via Bluetooth)
10. Labels printed dan ditempel di setiap carton

---

### Use Case 2: Warehouse Verify FG Receiving

**Scenario**: Warehouse admin menerima FG dari packing

**Steps**:
1. Admin scan barcode FG: `FG-2026-00123-CTN001`
2. System call API: GET `/api/finish-good-labels/barcode/FG-2026-00123-CTN001`
3. System tampilkan info:
   - Product: AFTONSPARV 302.213.49
   - Qty: 60 pcs
   - PO: PO-2026-001 (Week 10-2026, Belgium)
   - MO: MO-20260301-001
   - All WOs completed ✓
4. Admin verify data match dengan physical carton
5. Click [CONFIRM RECEIVING]
6. Stock FG updated automatically

---

### Use Case 3: Customer Service Trace Product

**Scenario**: Customer complaint untuk product AFTONSPARV

**Steps**:
1. CS scan barcode dari product: `FG-2026-00123-CTN001`
2. System call API: GET `/api/finish-good-labels/traceability/FG-2026-00123-CTN001`
3. System tampilkan complete history:
   - PO-2026-001 (Belgium, Week 10-2026)
   - MO-20260301-001 (Started: 2026-03-01, Completed: 2026-03-09)
   - All departments dengan dates:
     - Cutting: 2026-03-01 - 2026-03-02
     - Embroidery: 2026-03-02 - 2026-03-03
     - Sewing: 2026-03-03 - 2026-03-05
     - Finishing: 2026-03-05 - 2026-03-07
     - Packing: 2026-03-07 - 2026-03-09
4. CS identify mungkin issue di Sewing (date range normal)
5. Forward ke QC dept untuk investigation

---

### Use Case 4: IKEA Audit

**Scenario**: IKEA audit team request traceability untuk batch MO-W10-001-BE

**Steps**:
1. Management open web portal
2. Navigate to: Reports → Traceability
3. Input Traceability Code: `MO-W10-001-BE`
4. System find all related FG barcodes
5. Display complete production flow:
   - PO source & material
   - MO planning & execution
   - All WO dengan operator & dates
   - Material consumption per stage
   - Quality metrics per department
6. Export to PDF untuk IKEA
7. ✅ Audit passed (complete data)

---

## 📱 MOBILE APP INTEGRATION

### Label Scanner (React Native)

```javascript
import { BarCodeScanner } from 'expo-barcode-scanner';

const ScanFGLabel = () => {
  const handleBarCodeScanned = async ({ data }) => {
    // data = "FG-2026-00123-CTN001"
    
    try {
      const response = await fetch(
        `${API_URL}/finish-good-labels/barcode/${data}`
      );
      const label = await response.json();
      
      // Display traceability info
      showTraceabilityModal(label);
    } catch (error) {
      Alert.alert('Error', 'Invalid barcode or label not found');
    }
  };
  
  return (
    <BarCodeScanner
      onBarCodeScanned={handleBarCodeScanned}
      style={StyleSheet.absoluteFillObject}
    />
  );
};
```

---

## 🎯 BENEFITS

### 1. **Complete IKEA Compliance** ✅
- Label berisi semua informasi required
- Traceability code format sesuai standard
- Week format IKEA (WW-YYYY)
- Destination tracking untuk multi-country

### 2. **Full Production Traceability** 🔍
- Dari FG bisa trace kembali ke PO
- Setiap department production date tracked
- Operator/admin identification
- Material batch tracking

### 3. **Quality Issue Investigation** 🔧
- Defect bisa di-trace ke department tertentu
- Production date range untuk isolate batch
- Root cause analysis lebih cepat
- Targeted recall jika diperlukan

### 4. **Automated Label Generation** ⚡
- No manual input (data dari database)
- Consistent format
- Reduce human error
- Fast printing (thermal printer)

### 5. **Mobile-Friendly** 📱
- Barcode scanner integration
- Offline-capable (cache label data)
- Quick verification di warehouse
- Real-time stock update

---

## 🚀 NEXT STEPS

1. ✅ Database migration completed (datestamp fields)
2. ✅ Schema & service created
3. ✅ API endpoints ready
4. ⏳ **TODO**: Test dengan real MO data
5. ⏳ **TODO**: Integrate dengan Packing module
6. ⏳ **TODO**: Mobile app barcode scanner
7. ⏳ **TODO**: Thermal printer driver setup
8. ⏳ **TODO**: QR code generation (alternative to barcode)

---

## 📞 SUPPORT

Untuk pertanyaan atau issue terkait FG Label System:
- Contact: ERP Development Team
- Email: dev@qutykarunia.com
- Hotline: +62-XXX-XXXX-XXXX
