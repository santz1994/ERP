# 🚀 QUICK REFERENCE - SESSION 31 NEW ENDPOINTS & FEATURES

**Updated**: January 26, 2026  
**Backend Status**: ✅ Complete  
**Android Status**: ✅ 80% Complete  
**Frontend Status**: ⏳ Ready for implementation  

---

## 🎯 PRODUCTION STAFF - Daily Input (Web + Mobile)

### Endpoint 1: Record Daily Production
```
Method:  POST
Route:   /production/spk/{spk_id}/daily-input
Auth:    Bearer <JWT>
Role:    PRODUCTION_STAFF, PRODUCTION_SPV

Request:
{
    "production_date": "2026-01-26",
    "input_qty": 50,
    "notes": "Good quality production",
    "status": "CONFIRMED"
}

Response:
{
    "success": true,
    "data": {
        "spk_id": 1,
        "input_qty": 50,
        "cumulative_qty": 150,
        "target_qty": 500,
        "completion_pct": 30.0,
        "remaining_qty": 350,
        "status": "IN_PROGRESS",
        "message": "✅ Input recorded. 350 units more needed"
    }
}

✅ Web Portal: /src/pages/ProductionPage.tsx
✅ Mobile: POST /production/mobile/daily-input
```

### Endpoint 2: View SPK Progress
```
Method:  GET
Route:   /production/spk/{spk_id}/progress
Auth:    Bearer <JWT>
Role:    PRODUCTION_STAFF, PRODUCTION_SPV

Response:
{
    "success": true,
    "data": {
        "spk_id": 1,
        "spk_number": "SPK-2026-001",
        "product": "Soft Toy Bear",
        "target_qty": 500,
        "actual_qty": 150,
        "remaining_qty": 350,
        "completion_pct": 30.0,
        "status": "IN_PROGRESS",
        "daily_entries": [
            {
                "date": "2026-01-24",
                "qty": 50,
                "cumulative": 50,
                "status": "CONFIRMED",
                "notes": "Good production"
            },
            ...
        ],
        "summary": {
            "total_days_tracked": 3,
            "avg_daily_rate": 50.0,
            "est_days_remaining": 7
        }
    }
}

✅ Calendar component: DailyProductionInput.tsx
```

### Endpoint 3: Get My SPKs
```
Method:  GET
Route:   /production/my-spks
Auth:    Bearer <JWT>
Role:    PRODUCTION_STAFF
Query:   status=IN_PROGRESS | NOT_STARTED | COMPLETED

Response:
{
    "success": true,
    "data": [
        {
            "spk_id": 1,
            "spk_number": "SPK-2026-001",
            "product": "Soft Toy Bear",
            "target_qty": 500,
            "actual_qty": 150,
            "completion_pct": 30.0,
            "status": "IN_PROGRESS",
            "created_date": "2026-01-20"
        },
        ...
    ],
    "summary": {
        "total_spks": 5,
        "in_progress": 3,
        "completed": 1,
        "not_started": 1
    }
}

✅ Dashboard: ProductionDashboard.tsx
```

---

## 🎯 PPIC - Monitoring & Alerts (View-Only)

### Endpoint 1: Dashboard Overview
```
Method:  GET
Route:   /ppic/dashboard
Auth:    Bearer <JWT>
Role:    PPIC_MANAGER, MANAGER

Response:
{
    "success": true,
    "data": {
        "dashboard": {
            "total_spks": 10,
            "in_progress": 5,
            "completed": 3,
            "not_started": 2,
            "on_track": 4,
            "off_track": 1
        },
        "spks": [
            {
                "spk_id": 1,
                "spk_number": "SPK-001",
                "product": "Soft Toy Bear",
                "target_qty": 500,
                "actual_qty": 150,
                "completion_pct": 30.0,
                "status": "IN_PROGRESS",
                "health": "ON_TRACK",
                "est_completion": "2026-02-01",
                "daily_rate": 50.0
            },
            ...
        ]
    }
}

✅ Component: PPICDashboard.tsx
```

### Endpoint 2: Daily Summary Report
```
Method:  GET
Route:   /ppic/reports/daily-summary
Auth:    Bearer <JWT>
Role:    PPIC_MANAGER
Query:   report_date=2026-01-26 (optional, default: today)

Response:
{
    "success": true,
    "data": {
        "report_date": "2026-01-26",
        "total_entries": 15,
        "total_qty": 450,
        "by_spk": [
            {
                "spk_id": 1,
                "spk_number": "SPK-001",
                "qty_today": 50,
                "cumulative": 150,
                "target": 500,
                "completion_pct": 30.0
            },
            ...
        ]
    }
}

✅ Report: PPICReports.tsx
```

### Endpoint 3: On-Track Status & Alerts
```
Method:  GET
Route:   /ppic/reports/on-track-status
Auth:    Bearer <JWT>
Role:    PPIC_MANAGER

Response:
{
    "success": true,
    "data": {
        "on_track": [
            {
                "spk_id": 1,
                "spk_number": "SPK-001",
                "status": "ON_TRACK",
                "reason": "Daily rate: 50 units/day, est complete 2026-02-01"
            }
        ],
        "off_track": [
            {
                "spk_id": 2,
                "spk_number": "SPK-002",
                "status": "OFF_TRACK",
                "reason": "Behind schedule: need 75 units/day but only 40/day",
                "alert": "🔴 URGENT - will not meet deadline",
                "required_daily_rate": 75.0,
                "current_daily_rate": 40.0
            }
        ],
        "summary": {
            "on_track_count": 4,
            "off_track_count": 1
        }
    }
}

✅ Component: AlertPanel.tsx
```

### Endpoint 4: Real-Time Alerts
```
Method:  GET
Route:   /ppic/alerts
Auth:    Bearer <JWT>
Role:    PPIC_MANAGER
Query:   severity=critical|warning|info (optional)

Response:
{
    "success": true,
    "data": [
        {
            "alert_id": "OFF_TRACK_2",
            "severity": "🔴 CRITICAL",
            "title": "SPK-002 OFF-TRACK",
            "message": "Will not meet deadline at current rate (40 units/day)",
            "spk_id": 2,
            "created_at": "2026-01-26T14:30:00"
        },
        {
            "alert_id": "AT_RISK_3",
            "severity": "🟡 WARNING",
            "title": "SPK-003 AT-RISK",
            "message": "Production rate declining, at risk of missing deadline",
            "spk_id": 3,
            "created_at": "2026-01-26T14:35:00"
        }
    ],
    "summary": {
        "total_alerts": 2,
        "critical": 1,
        "warning": 1
    }
}

✅ Component: AlertCenter.tsx (polling every 30s)
```

---

## 🎯 FINISHGOOD - Barcode Scanning (Mobile Android)

### Endpoint 1: Get Pending Transfers
```
Method:  GET
Route:   /warehouse/finishgood/pending-transfers
Auth:    Bearer <JWT>
Role:    WAREHOUSE_STAFF, WAREHOUSE_SPV

Response:
{
    "success": true,
    "data": [
        {
            "transfer_id": 1,
            "carton_id": "CTN20260001",
            "article": "IKEA123456",
            "article_name": "Soft Toy Bear - Brown",
            "qty": 100,
            "status": "PENDING",
            "barcode": "IKEA123456|CTN20260001|100|20260126"
        },
        ...
    ]
}

✅ Android: FinishGoodViewModel.loadPendingTransfers()
```

### Endpoint 2: Verify Barcode
```
Method:  POST
Route:   /warehouse/finishgood/verify
Auth:    Bearer <JWT>
Role:    WAREHOUSE_STAFF

Request:
{
    "carton_id": "CTN20260001",
    "scanned_barcode": "IKEA123456|CTN20260001|100|20260126",
    "manual_count": null
}

Response:
{
    "success": true,
    "data": {
        "carton_id": "CTN20260001",
        "article": "IKEA123456",
        "system_qty": 100,
        "manual_count": null,
        "match": true,
        "message": "✅ Barcode verified. Carton found in pending"
    }
}

✅ Android: FinishGoodViewModel.verifyBarcode()
```

### Endpoint 3: Confirm Carton Count
```
Method:  POST
Route:   /warehouse/finishgood/confirm
Auth:    Bearer <JWT>
Role:    WAREHOUSE_STAFF

Request:
{
    "transfer_id": 1,
    "carton_id": "CTN20260001",
    "final_count": 100,
    "notes": "Mobile FinishGood scan verification"
}

Response:
{
    "success": true,
    "data": {
        "carton_id": "CTN20260001",
        "status": "COUNTED",
        "message": "✅ Carton confirmed. 99 more cartons pending"
    }
}

✅ Android: FinishGoodViewModel.confirmCarton()
```

---

## 📱 ANDROID APP - Barcode Formats

### Supported Barcode Types:
```
1. QR Code (Preferred)
   Format: "ARTICLE|CARTON_ID|QTY|DATE"
   Example: "IKEA123456|CTN20260001|100|20260126"
   Pros: More data, larger scan area

2. Code128 (Warehouse Standard)
   Format: "CARTON_ID-ARTICLE"
   Example: "CTN20260001-IKEA123456"
   Pros: Reliable, widely supported

3. EAN-13 (Carton code)
   Format: Plain number
   Example: "5901234123457"
   Pros: Standard retail barcode

4. Code39 (Legacy)
   Format: Text + numbers
   Example: "CTN20260001"
   Pros: Simple, for fallback
```

### ML Kit Scanner Configuration:
```kotlin
BarcodeScannerOptions.Builder()
    .setBarcodeFormats(
        com.google.mlkit.vision.barcode.Barcode.FORMAT_QR_CODE,
        com.google.mlkit.vision.barcode.Barcode.FORMAT_CODE_128,
        com.google.mlkit.vision.barcode.Barcode.FORMAT_CODE_39,
        com.google.mlkit.vision.barcode.Barcode.FORMAT_EAN_13
    )
    .build()
```

---

## 🔑 Authentication & Authorization

### Login (Web + Mobile)
```
Method:  POST
Route:   /auth/login
Auth:    None (public endpoint)

Request:
{
    "pin": "1234",              // OR
    "rfid_card": "CARD12345"    // RFID scan code
}

Response:
{
    "success": true,
    "data": {
        "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
        "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
        "token_type": "Bearer",
        "user": {
            "id": 1,
            "username": "operator_001",
            "email": "operator@quty.com",
            "role": "PRODUCTION_STAFF",
            "department": "PRODUCTION"
        }
    }
}

✅ Web: LoginPage.tsx
✅ Mobile: LoginScreen.kt
```

### Permissions Matrix:
```
ROLE                    | Production Daily | PPIC Monitor | Edit SPK | Barcode Scan
------------------------|------------------|--------------|----------|-------------
PRODUCTION_STAFF        | ✅ Input         | ❌           | ❌       | ❌
PRODUCTION_SPV          | ✅ Input         | ⚠️ View      | ✅       | ❌
PPIC_MANAGER            | ❌               | ✅ View Only | ❌       | ❌
WAREHOUSE_STAFF         | ❌               | ❌           | ❌       | ✅
WAREHOUSE_SPV           | ❌               | ⚠️ View      | ❌       | ✅
MANAGER                 | ❌               | ✅ View All  | ✅ Approve| ⚠️
SUPERADMIN              | ✅ All           | ✅ All       | ✅ All   | ✅ All
```

---

## 📊 Database Tables (New)

### spk_daily_production
```sql
id, spk_id, production_date, input_qty, cumulative_qty, 
input_by_id, status, notes, created_at
```

### spk_production_completion
```sql
id, spk_id, target_qty, actual_qty, completed_date,
confirmed_by_id, confirmation_notes, confirmed_at, is_completed
```

### spk_modifications
```sql
id, spk_id, field_name, old_value, new_value,
modified_by_id, modification_reason, created_at
```

### material_debt
```sql
id, spk_id, material_id, qty_owed, qty_settled, reason,
created_by_id, approval_status, approved_by_id, approved_at, 
approval_reason, created_at
```

### material_debt_settlement
```sql
id, material_debt_id, qty_settled, settlement_date,
received_by_id, settled_by_id, settlement_notes, created_at
```

---

## 🧪 TESTING CHECKLIST

### Backend Tests
- [ ] Daily input cumulative calculation
- [ ] SPK completion logic
- [ ] Modification audit trail
- [ ] Material debt approval flow
- [ ] Permission checks (all 4 endpoints)

### Frontend Tests
- [ ] Daily production input form
- [ ] Calendar display
- [ ] Progress calculation
- [ ] Edit modal validation
- [ ] PPIC dashboard refresh

### Android Tests
- [ ] Barcode scanning QR
- [ ] Barcode scanning Code128
- [ ] Offline queue sync
- [ ] JWT token refresh
- [ ] Network error handling

### E2E Tests
- [ ] Full production workflow
- [ ] FinishGood counting workflow
- [ ] Approval workflow
- [ ] Material debt settlement

---

## 🚀 DEPLOYMENT CHECKLIST

Before Go-Live:
- [ ] Update API base URL to production
- [ ] Update CORS to specific domain (not wildcard)
- [ ] Enable HTTPS/SSL certificates
- [ ] Database backup & restore test
- [ ] Load testing (100+ users)
- [ ] Security audit
- [ ] User training completed
- [ ] Support documentation ready

---

✅ **Ready for Frontend & Testing Implementation**
