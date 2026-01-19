This project is for ERP QUTY KARUNIA do not share any part of this project without permission.
Yang nantinya akan dikembangkan AI Erp System untuk mengelola proses manufaktur di Quty Karunia sesuai alur produksi yang telah dijelaskan sebelumnya.

## 1. High Level Architecture (Design Pattern)
Untuk sistem manufaktur seperti ini (terintegrasi ketat tapi modulnya banyak), saya sangat menyarankan Modular Monolith Architecture.

Mengapa bukan Microservices? Microservices terlalu rumit untuk fase awal. Anda butuh data yang konsisten (ACID Transaction) saat memindahkan stok dari Cutting ke Sewing. Modular Monolith memungkinkan integrasi database yang ketat tapi kodenya tetap rapi terpisah per folder modul.

Struktur Folder Code (Draft):
erp-softtoys/
├── app/
│   ├── core/
│   │   ├── database.py           # SQLAlchemy setup
│   │   ├── models/
│   │   │   ├── products.py       # Articles + Categories (parent-child)
│   │   │   ├── bom.py            # Bill of Materials
│   │   │   ├── manufacturing.py  # MO + Work Orders
│   │   │   ├── transfer.py       # Transfer logs + Line occupancy
│   │   │   ├── warehouse.py      # Stock management + FIFO
│   │   │   ├── quality.py        # QC tests + Inspections
│   │   │   ├── exceptions.py     # Alerts + Acknowledgements
│   │   │   └── users.py          # Users + Roles
│   │   ├── config.py             # Configuration (coming Week 2)
│   │   ├── security.py           # Auth & encryption (coming Week 2)
│   │   └── constants.py          # System constants
│   ├── api/
│   │   └── v1/                   # API routes (coming Week 2)
│   ├── modules/                  # Business logic (coming Week 3)
│   ├── shared/                   # Common utilities (coming Week 2)
│   └── main.py                   # FastAPI app
├── migrations/                   # Alembic DB migrations
├── tests/                        # Test suite (coming Week 9)
├── requirements.txt              # Python dependencies
├── .env.example                  # Environment template
└── README.md                     # This file

docs/
├── IMPLEMENTATION_ROADMAP.md     # 11-week development plan
├── WEEK1_SETUP_GUIDE.md          # Week 1 setup instructions
├── WEEK1_SUMMARY.md              # Phase 0 completion report
└── Project Docs/
    ├── Project.md                # Project overview & recommendations
    ├── Flow Production.md         # Production SOP
    ├── Database Scheme.csv        # Schema reference
    └── Flowchart ERP.csv         # Process flowchart
```

## 2. Technology Stack
Python Ecosystem:
    - Backend: FastAPI/Django (Ringan, Cepat, Asynchronous)
    - Database: PostgreSQL (Kuat untuk transaksi kompleks)
    - ORM: SQLAlchemy/Django ORM (Abstraksi DB)
    - Frontend: React.js/Vue.js (Interaktif, Komponen Reusable)
    - Deployment: Docker + Kubernetes (Scalable, Isolated Environments)
    - Message Broker: RabbitMQ/Redis (Untuk notifikasi real-time, e.g. alert segregasi)
    - Testing: PyTest/Jest (Unit & Integration Tests)

## 3. API Design (Menghubungkan Flowchart dengan Sistem)
Sebelum koding tampilan, Anda harus mendefinisikan bagaimana sistem "berbicara". Gunakan Flowchart CSV yang sudah kita buat sebagai dasar Endpoint API.

Contoh Implementasi Logika "Line Clearance" (Modul Cutting):
    - Endpoint: POST /api/production/transfer
    - Payload (Data yang dikirim): (JSON)
        {
        "from_dept": "Cutting",
        "to_dept": "Sewing",
        "batch_id": "BATCH-001",
        "qty": 500
        }
    - Logic: (JavaScript/Python Pseudocode)
        function transferItems(data) {
        // 1. Cek apakah Line Sewing kosong (Logika QT-09)
        const isLineClear = checkLineStatus(data.to_dept);
        if (!isLineClear) {
            return Error("Line Sewing masih mengerjakan artikel lain!");
        }

        // 2. Cek apakah Qty cukup (Logika Warehouse)
        const stock = checkStock(data.from_dept, data.batch_id);
        if (stock < data.qty) {
            return Error("Stok tidak cukup!");
        }

        // 3. Eksekusi Pindah
        createTransferLog(data);
        return Success("Barang dipindahkan, menunggu Approval Sewing");
        }

## 4. Wireframe & UI/UX
Jangan biarkan developer mendesain UI sambil koding. Buat sketsa layar (Wireframe) terlebih dahulu, terutama untuk Operator Lapangan.

Halaman Kunci yang Perlu Didesain:
    1. Dashboard PPIC: Tampilan Gantt Chart untuk jadwal produksi & Status SPK.
    2. Mobile View Operator:
        - Tombol besar untuk input output (Touchscreen friendly).
        - Tampilan scan barcode/QR.
        - Alert Merah besar jika salah scan (Segregasi Article).
    3. QC Tablet View: Checklist digital (Pass/Fail) untuk Drop Test & Metal Detector.

## 5. Tambahan Fitur:
    - Notifikasi Real-time: Gunakan WebSocket untuk mengirim alert ke operator jika ada masalah (misal: Line Clearance Required).
    - Reporting Module: Generate laporan produksi harian/mingguan otomatis dalam format PDF/Excel.
    - Audit Trail: Simpan log lengkap setiap perubahan stok & status produksi untuk kepatuhan ISO/IKEA.
    - User Roles & Permissions: Pastikan hanya user tertentu yang bisa approve transfer antar departemen.
    - Backup Otomatis: Jadwalkan backup database harian untuk menghindari kehilangan data.
    - Bahasa Lokal: Implementasi multi-bahasa (Indonesia & Inggris) untuk user interface.
    - Waktu : Implementasi timezone lokal (WIB) di seluruh sistem untuk konsistensi waktu produksi.
    - Training Mode: Mode simulasi untuk pelatihan operator tanpa mengubah data produksi nyata.
    - Dokumentasi API: Gunakan Swagger/OpenAPI untuk mendokumentasikan semua endpoint API.
    - API Versioning: Terapkan versioning pada API untuk memudahkan update di masa depan tanpa mengganggu sistem yang berjalan.
    - Penambahan module Inventory Management: Untuk mengelola stok bahan baku, barang dalam proses, dan barang jadi secara lebih rinci.
    - Integrasi dengan sistem eksternal: seperti sistem QC produksi atau sistem ERP lainnya jika diperlukan di masa depan.
    - Import Export data (BOM, Masterdata, optional pilihan lainnya) melalui file CSV/Excel untuk memudahkan migrasi data awal dan backup data.
    - User Activity Logging: Mencatat aktivitas user untuk keamanan dan audit internal.
    - UAC/RBAC: Implementasi User Access Control/Role-Based Access Control untuk mengatur hak akses user berdasarkan peran mereka.
    - Pengembangan module lain sesuai kebutuhan mungkin akan bertambah di masa depan.
    - Pastikan sistem dirancang agar mudah di-maintain dan scalable untuk penambahan fitur di masa depan.
    - Flow produksi dan SOP harus selalu menjadi acuan utama dalam pengembangan sistem ERP ini.
    - Tambahkan License header pada setiap file kode sumber untuk kepemilikan intelektual.

Dengan arsitektur modular, teknologi yang tepat, desain API yang jelas, dan fokus pada UI/UX operator, sistem ERP manufaktur untuk Quty Karunia dapat dibangun dengan efisien dan efektif sesuai kebutuhan produksi mainan boneka.

---

## 6. IMMEDIATE RECOMMENDATIONS (Before Development Starts)

### 6.1 Resolve Database Schema Gaps

**Gap 1: Add Parent-Child Article Relationship**
- **Current Issue**: products.type = {WIP, Finish Good} lacks parent linking
- **Risk**: Orphaned articles, incorrect BOM references
- **Solution**: Add `parent_article_id` (BIGINT, FK) to products table
  ```sql
  ALTER TABLE products ADD COLUMN parent_article_id BIGINT;
  ALTER TABLE products ADD CONSTRAINT fk_parent_article 
    FOREIGN KEY (parent_article_id) REFERENCES products(id);
  ```
- **Use Case**: BLAHAJ-100 (IKEA Parent) → CUT-BLA-01, SEW-BLA-01, PAC-BLA-01 (Child Articles)

**Gap 2: Create Line Occupancy Tracking Table**
- **Current Issue**: Line Clearance checks (ID 290, 380, 405) have no real-time status data
- **Risk**: Cannot efficiently determine if line is clear
- **Solution**: New table `line_occupancy`
  ```sql
  CREATE TABLE line_occupancy (
    id BIGINT PRIMARY KEY,
    dept_name ENUM('Cutting', 'Embroidery', 'Sewing', 'Finishing', 'Packing'),
    line_number INT,
    current_article_id BIGINT,
    current_batch_id VARCHAR(50),
    occupancy_status ENUM('CLEAR', 'OCCUPIED', 'PAUSED'),
    destination VARCHAR(50),
    week_number INT,
    locked_at DATETIME,
    locked_by BIGINT (User ID),
    expected_clear_time DATETIME,
    FOREIGN KEY (current_article_id) REFERENCES products(id)
  );
  ```
- **Used By**: Transfer validation logic (ID 290, 380, 405)

**Gap 3: Expand transfer_logs.from_dept Enum**
- **Current Issue**: Enum only includes {Finishing, Cutting, Sewing} - missing Embroidery
- **Risk**: Cannot track internal Embroidery transfers
- **Solution**: Update enum to {Cutting, Embroidery, Sewing, Finishing, Packing}
  ```sql
  ALTER TABLE transfer_logs MODIFY COLUMN from_dept 
    ENUM('Cutting', 'Embroidery', 'Sewing', 'Finishing', 'Packing');
  ALTER TABLE transfer_logs MODIFY COLUMN to_dept 
    ENUM('Embroidery', 'Sewing', 'Finishing', 'Packing', 'Subcon', 'FinishGood');
  ```

**Gap 4: Add Revision Tracking to BOM**
- **Current Issue**: bom_headers.revision string only - no audit trail
- **Solution**: Add timestamp and user tracking
  ```sql
  ALTER TABLE bom_headers ADD COLUMN revision_date DATETIME;
  ALTER TABLE bom_headers ADD COLUMN revised_by BIGINT;
  ALTER TABLE bom_headers ADD COLUMN revision_reason VARCHAR(255);
  ```

**Gap 5: Improve QC Lab Test Precision**
- **Current Issue**: qc_lab_tests.measured_value (FLOAT) lacks unit and precision
- **Solution**: Refactor for ISO compliance
  ```sql
  ALTER TABLE qc_lab_tests MODIFY COLUMN measured_value NUMERIC(10,2);
  ALTER TABLE qc_lab_tests ADD COLUMN measured_unit VARCHAR(20);
  ALTER TABLE qc_lab_tests ADD COLUMN iso_standard VARCHAR(50);
  ALTER TABLE qc_lab_tests ADD COLUMN test_location VARCHAR(100);
  ```

---

### 6.2 Define Alert/Block Escalation Workflows

**Escalation Path 1: Line Clearance Block (ID 292)**

| Scenario | Trigger | Action | Approval By | Timeout |
|----------|---------|--------|-------------|---------|
| Sewing Line NOT ready for transfer | Workflow ID 290 → 292 | BLOCK Print Surat Jalan | SPV Cut | 30 min |
| SPV Cut override required | Manual Request | Escalate to PPIC Manager | PPIC Manager | 5 min |
| Final override if critical | Manager approval | System auto-unlock line | Factory Manager | 15 min |

**Implementation Details**:
- When ID 292 triggered → Generate notification to SPV Cut mobile app
- If no response in 30 min → Auto-escalate to PPIC Manager
- SPV Cut must confirm reason: "Sewing line delayed" / "Article still processing" / "Manual clearance needed"
- System logs: `alert_logs` table tracks all overrides for audit

**Escalation Path 2: Segregasi Alarm Manual Intervention (ID 382)**

| Scenario | Trigger | Action | Status |
|----------|---------|--------|--------|
| Destination MISMATCH detected | Workflow ID 380 → 382 | ALARM + Block Transfer | Manual HOLD |
| Example: USA vs EUROPE mix | Line conveyor segregation check | Alert Admin Sewing + SPV Sewing | Requires Manual Clearance |
| Operator must verify | Physical 5-meter gap or line stop | Scan "CLEARANCE COMPLETE" QR | Transfer Proceeds |
| If ignored (timeout > 10 min) | Auto-escalate to Prod Manager | SMS + Email notification | Manager Override Only |

**Implementation Details**:
- Alarm: Audio + Visual (Red flashing light on department tablet)
- Manual intervention = Physical line clearance (5 meters separation) + Digital confirmation
- QR scan to acknowledge: `segregasi_acknowledgement` table records timestamp + user
- No auto-stop: Operator has discretion (manual mode allows flexibility for emergency situations)

**New Tables for Escalation**:
```sql
CREATE TABLE alert_logs (
  id BIGINT PRIMARY KEY,
  alert_type ENUM('LINE_CLEARANCE_BLOCK', 'SEGREGASI_ALARM', 'QC_FAIL', 'SHORTAGE'),
  severity ENUM('INFO', 'WARNING', 'CRITICAL'),
  triggered_at DATETIME,
  triggered_by BIGINT,
  triggered_in_workflow_id INT,
  escalated_to BIGINT,
  escalation_level INT,
  status ENUM('PENDING', 'ACKNOWLEDGED', 'RESOLVED', 'OVERRIDDEN'),
  resolution_time DATETIME,
  notes TEXT
);

CREATE TABLE segregasi_acknowledgement (
  id BIGINT PRIMARY KEY,
  transfer_log_id BIGINT,
  acknowledged_at DATETIME,
  acknowledged_by BIGINT,
  clearance_method ENUM('PHYSICAL_GAP', 'LINE_STOP', 'MANUAL_INSPECTION'),
  proof_photo_url VARCHAR(500),
  FOREIGN KEY (transfer_log_id) REFERENCES transfer_logs(id)
);
```

---

### 6.3 Establish Test Data Strategy

**Test Scenario 1: Route 1 Full Process (with Embroidery)**
```json
{
  "scenario_name": "Route1_FullEmbo_Week22",
  "po_number": "PO-2026-001",
  "article_parent": "BLAHAJ-100",
  "route": "Route 1",
  "qty_planned": 5000,
  "destination": "DE",
  "week": 22,
  "test_cases": [
    {
      "test_id": "T1.1",
      "description": "Cutting process, check surplus handling",
      "input_qty": 5000,
      "expected_output": 5150,
      "expected_action": "Auto-Revise SPK Sewing (150 units surplus)"
    },
    {
      "test_id": "T1.2",
      "description": "Line Clearance pass: Embroidery ready",
      "line_status": "CLEAR",
      "expected_result": "Transfer allowed"
    },
    {
      "test_id": "T1.3",
      "description": "Sewing segregasi check: Destination matches",
      "current_line_destination": "DE",
      "incoming_destination": "DE",
      "expected_result": "No alarm, transfer proceeds"
    }
  ]
}
```

**Test Scenario 2: Route 2 Direct Sewing (Skip Embroidery)**
```json
{
  "scenario_name": "Route2_NormalSewing_Week23",
  "po_number": "PO-2026-002",
  "route": "Route 2",
  "qty_planned": 3000,
  "destination": "US",
  "week": 23
}
```

**Test Scenario 3: Route 3 Subcon (External Vendor)**
```json
{
  "scenario_name": "Route3_Subcon_Week24",
  "po_number": "PO-2026-003",
  "route": "Route 3",
  "subcon_vendor": "PT-ABC-123",
  "gate_pass_out_time": "08:30",
  "expected_return_time": "16:00"
}
```

**Barcode/QR Format Specification**:
```
[Department]|[Article_Code]|[Batch_ID]|[Week]|[Destination]|[Qty]|[Timestamp]

Examples:
CUT|CUT-BLA-01|BATCH-2026-001|22|DE|5000|20260119083000
SEW|SEW-BLA-01|BATCH-2026-001|22|DE|5000|20260119101500
FIN|PAC-BLA-01|BATCH-2026-001|22|DE|5000|20260119143000
```

**Mock Scanner Input**:
- Simulate barcode scanner via API endpoint: `POST /api/test/mock-scanner`
- Accept QR code data in JSON format
- Support batch scanning (multiple QR codes in sequence)
- Log all scanner inputs for replay/debugging

---

### 6.4 Add Error Handling Flowchart

**Exception Flow Categories**:

| Category | Error Type | Handler | Recovery |
|----------|-----------|---------|----------|
| **Network** | Scanner offline | Offline queue to local storage | Retry sync on reconnection |
| **Network** | Database connection timeout | Fallback to cache | Alert IT, manual entry if critical |
| **Validation** | Qty mismatch > 10% | Block transfer + notify SPV | Manual override + adjustment |
| **Validation** | Article code invalid | Reject scan + red alert | Re-scan or manual entry |
| **Validation** | Barcode duplicate | Log duplicate attempt | Allow or block per policy |
| **QC** | Metal detector fail | Auto-reject + segregate | Incident report required |
| **QC** | Drop test fail (>5 fails) | Hold lot + notify QC Manager | Batch rework or scrap decision |
| **Transfer** | Line occupied (blocked) | Escalate to SPV Cut | Manual clearance or reschedule |
| **Transfer** | Segregasi mismatch | Manual alarm + hold | Operator must clear line |
| **Warehouse** | Stock insufficient | Auto-generate PR to Purchasing | Block production or allocate reserve |

**New Exception Flow Document Structure**:
```
EXCEPTION_FLOW_<ModuleName>.csv format:
ID, Error_ID, Error_Type, Condition, Alert_To, Recovery_Action, Next_Step, Timeout
```

**Exception Flow Examples**:
```csv
Mod_Cutting_Exception,,,,,,
ID,Error_ID,Error_Type,Condition,Alert_To,Recovery_Action,Next_Step,Timeout_Minutes
E100,E100,Shortage,Output < Target 90%,SPV Cut,Approve extra material,Return to Step 240,30
E101,E101,ScanFailure,Invalid barcode format,Admin Cut,Manual entry required,Allow transfer after verification,10
E102,E102,LineBlocked,Sewing line still occupied,SPV Cut,Escalate to PPIC,Wait or reschedule,30

Mod_Sewing_Exception,,,,,,
E200,E200,SegregasiMismatch,"Destination <> Line destination",Admin Sew,Manual line clearance,Scan clearance QR,10
E201,E201,QtyMismatch,Received Qty > BOM 10%,System,Review & adjust,Manual adjustment required,15
E202,E202,ReworkLoop,Rework count > 3,QC Sew,Escalate to QC Supervisor,Send to scrap or rework decision,20
```

---

### 6.5 Monitoring & Alerting Strategy

**KPI 1: Line Utilization Rate**
```
Formula: (Actual Run Time / Available Shift Time) × 100
Target: > 85%
Alert Threshold: < 75% (warning) | < 50% (critical)
Tracked By: start_time, end_time in work_orders table
Dashboard View: Real-time gauge per department
```

**KPI 2: Transfer Cycle Time**
```
Formula: timestamp_end - timestamp_start (in transfer_logs)
Target: Cutting→Sewing < 15 min, Sewing→Finishing < 10 min
Alert Threshold: > 20 min (warning) | > 30 min (critical)
Tracked By: Handshake Digital timestamps
Dashboard View: Time series graph (hourly average)
```

**KPI 3: QC Reject Rate**
```
Formula: (Reject_Qty / Total_Output_Qty) × 100
Target: < 2%
Alert Threshold: > 3% (warning) | > 5% (critical)
Tracked By: reject_qty in work_orders, defect_reason in qc_inspections
Dashboard View: By department breakdown
```

**KPI 4: Line Clearance Compliance**
```
Formula: (Times Line Cleared / Total Transfer Attempts) × 100
Target: 100%
Alert Threshold: < 95% (warning)
Tracked By: is_line_clear in transfer_logs
Dashboard View: Compliance dashboard
```

**KPI 5: Handshake Digital Acknowledgement Rate**
```
Formula: (ACCEPT scans received / Transfers sent) × 100
Target: 100%
Alert Threshold: < 98% (warning) | < 90% (critical)
Tracked By: segregasi_acknowledgement, transfer_logs
Dashboard View: Real-time monitoring
```

**Prometheus Metrics Collection**:
```python
# Example metrics to expose:
erp_line_utilization{dept="Cutting"} 0.87
erp_transfer_cycle_time_seconds{from_dept="Cutting", to_dept="Sewing"} 720
erp_qc_reject_rate{dept="Finishing"} 0.015
erp_line_clearance_compliance{dept="Sewing"} 1.0
erp_handshake_acknowledgement{dept="Sewing"} 0.99

# Alert Rules (Prometheus AlertManager):
- alert: HighLineUtilizationWarning
  expr: erp_line_utilization < 0.75
  for: 5m
  
- alert: TransferCycleTimeExceeded
  expr: erp_transfer_cycle_time_seconds > 1800
  for: 10m
  
- alert: QCRejectRateCritical
  expr: erp_qc_reject_rate > 0.05
  for: 1m
```

**Grafana Dashboard Sections**:
1. **Production Status**: Real-time line status (CLEAR/OCCUPIED/PAUSED per department)
2. **KPI Overview**: 5 key metrics with color-coded status
3. **Transfer Analytics**: Cycle time trends, bottleneck identification
4. **QC Metrics**: Reject rate by article, test type failure analysis
5. **Alert History**: Last 24 hours of critical/warning events
6. **Compliance Report**: Line clearance, handshake acknowledgement rates

---

## 7. IMPLEMENTATION PRIORITY & TIMELINE

| Phase | Component | Duration | Dependencies | Status |
|-------|-----------|----------|--------------|--------|
| **Phase 0: Setup** | Database schema corrections | 1 week | None | 🔴 Week 1 |
| **Phase 0: Setup** | Line occupancy infrastructure | 1 week | DB schema | 🔴 Week 1 |
| **Phase 1: Core** | API skeleton (FastAPI) | 2 weeks | DB, architecture | 🔴 Week 1-2 |
| **Phase 1: Core** | Authentication & Role-based access | 1 week | API | 🔴 Week 2 |
| **Phase 2: QT-09** | Line Clearance validation logic | 2 weeks | API, line_occupancy | 🔴 Week 2-3 |
| **Phase 2: QT-09** | Transfer Handshake protocol | 2 weeks | Line Clearance | 🔴 Week 3-4 |
| **Phase 3: UI** | Operator mobile UI (React Native) | 3 weeks | API endpoints | 🟡 Week 4-6 |
| **Phase 3: UI** | QC Lab test input forms | 2 weeks | API | 🟡 Week 5-6 |
| **Phase 4: Dashboard** | PPIC Gantt chart dashboard | 2 weeks | API, data ready | 🟢 Week 6-7 |
| **Phase 4: Dashboard** | Real-time monitoring dashboards | 1 week | Prometheus setup | 🟢 Week 7 |
| **Phase 5: Test** | Unit tests (PyTest) | 2 weeks | All modules | 🟢 Week 7-8 |
| **Phase 5: Test** | Integration tests | 2 weeks | All modules | 🟢 Week 8-9 |
| **Phase 6: Deploy** | Docker containerization | 1 week | All code | 🟢 Week 9 |
| **Phase 6: Deploy** | Kubernetes orchestration | 1 week | Docker | 🟢 Week 10 |
| **Phase 7: UAT** | User Acceptance Testing | 2 weeks | Full system | 🟢 Week 10-11 |

**Total Timeline**: 1 year to full production deployment

---

## 8. Development Team & Responsibilities

| Role | Responsibility | Team Size |
|------|-----------------|-----------|
| Full-Stack Developer | API development, DB integration, backend logic | 1 Person |
| Frontend Developer | Mobile UI, Dashboard, Operator interfaces | 1 Person + 1 AI |
| QA Engineer | Test case creation, automated testing, bug tracking | 1 Person + 1 AI |
| DevOps Engineer | Dockerization, Kubernetes setup, CI/CD pipelines | 1 Person + 1 AI |
| Project Manager | Timeline management, stakeholder communication | 1 Person + 1 AI |
| UX/UI Designer | Wireframe creation, user experience optimization | 1 Person + 1 AI |
| Technical Writer | Documentation, API specs, user manuals | 1 Person + 1 AI |
| Support Engineer | Post-deployment support, issue resolution | 1 Person + 1 AI |

**Recommended Total**: 1 Person + 1 AI for 1 year sprint

**Created by: Daniel Rizaldy**