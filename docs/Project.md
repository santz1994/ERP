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
    - Barcode/QR Code Scanning: Pada Warehouse dan Operator untuk mempercepat proses input data.

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

---

## 9. STRATEGIC ENHANCEMENT RECOMMENDATIONS (January 2026)
**Status**: AWAITING APPROVAL
**Prepared by**: Daniel Rizaldy (Senior IT Developer)

### 9.1 Advanced Analytics & Business Intelligence 📊

#### **Predictive Production Planning**
- **Objective**: Forecast demand and optimize production scheduling
- **Technology**: Machine Learning (Python scikit-learn, TensorFlow)
- **Features**:
  - Historical data analysis for demand forecasting
  - Optimal routing recommendation based on patterns
  - Machine downtime prediction
  - Material shortage early warning
- **Impact**: 20-30% reduction in production delays
- **Complexity**: High | **Timeline**: 3-4 months
- **ROI**: High - reduces waste and improves delivery times

#### **Real-Time Production Dashboard with KPIs**
- **Objective**: Executive-level visibility into production metrics
- **Features**:
  - OEE (Overall Equipment Effectiveness) calculation
  - Real-time production vs target visualization
  - Quality yield percentage by department
  - Bottleneck identification with heat maps
  - Interactive Gantt charts for MO tracking
- **Technology**: Grafana dashboards, custom React charts
- **Impact**: Better decision-making for management
- **Complexity**: Medium | **Timeline**: 2 months
- **ROI**: Medium - improves management oversight

---

### 9.2 IoT & Industry 4.0 Integration 🏭

#### **IoT Sensor Integration**
- **Objective**: Automate data collection from production floor
- **Devices**:
  - Weight sensors on stuffing machines (automatic weight verification)
  - Temperature/humidity sensors (fabric storage monitoring)
  - Vibration sensors on sewing machines (predictive maintenance)
  - RFID readers at each department gateway (automatic transfer logging)
- **Protocol**: MQTT broker (Mosquitto) for device communication
- **Benefits**: Eliminates manual data entry, real-time monitoring
- **Complexity**: High | **Timeline**: 4-6 months
- **ROI**: Very High - reduces labor costs and errors

#### **RFID System Implementation** 🔖
- **Status**: Already mentioned in requirements as "next implementation"
- **Scope**:
  - RFID tags on fabric rolls and carton boxes
  - Fixed readers at department entrances/exits
  - Handheld readers for operators
  - Bulk scanning capability (scan entire pallet at once)
  - Integration with existing barcode system
- **Advantages over Barcode**:
  - No line-of-sight required
  - Faster scanning (multiple items simultaneously)
  - More durable tags
  - Higher capacity data storage
- **Implementation Plan**:
  - Phase 1: Pilot in Warehouse (3 months)
  - Phase 2: Expand to all departments (6 months)
  - Phase 3: Complete migration (12 months)
- **Complexity**: High | **Timeline**: 12 months
- **ROI**: Very High - significant time savings

---

### 9.3 Mobile-First Enhancements 📱

#### **Offline-First Mobile App**
- **Objective**: Enable production floor operations without internet
- **Features**:
  - Complete offline functionality with local storage
  - Background sync when connection restored
  - Conflict resolution for concurrent edits
  - Progressive Web App (PWA) for easy installation
- **Technology**: React Native + WatermelonDB (offline database)
- **Impact**: Eliminates internet dependency on factory floor
- **Complexity**: Medium | **Timeline**: 2-3 months
- **ROI**: High - ensures continuous operations

#### **Voice Commands & Hands-Free Operation**
- **Objective**: Operators can work without touching devices
- **Features**:
  - Voice-activated QC pass/fail recording
  - Spoken barcode confirmation
  - Voice notes for defect description
  - Multilingual support (Indonesia, English)
- **Technology**: Web Speech API, Google Speech-to-Text
- **Impact**: Faster data entry, improved hygiene
- **Complexity**: Medium | **Timeline**: 1-2 months
- **ROI**: Medium - improves operator efficiency

---

### 9.4 AI-Powered Quality Control 🤖

#### **Computer Vision for Defect Detection**
- **Objective**: Automated visual inspection using AI
- **Implementation**:
  - Cameras at critical inspection points
  - CNN model trained on defect images
  - Real-time defect classification (torn fabric, wrong color, missing parts)
  - Automatic defect photo capture and logging
- **Technology**: TensorFlow, OpenCV, Raspberry Pi cameras
- **Benefits**: 
  - 99%+ inspection accuracy
  - Reduces inspector fatigue
  - Consistent quality standards
- **Complexity**: Very High | **Timeline**: 6-8 months
- **ROI**: Very High - reduces rework and returns

#### **Natural Language Processing for Defect Reports**
- **Objective**: Automatically categorize and analyze defect descriptions
- **Features**:
  - Text mining of QC notes to identify recurring issues
  - Root cause analysis suggestions
  - Automatic categorization of defect types
  - Trend analysis for proactive quality improvement
- **Technology**: spaCy, NLTK for Indonesian language processing
- **Complexity**: Medium | **Timeline**: 2 months
- **ROI**: Medium - improves quality management

---

### 9.5 Advanced Planning & Optimization 🎯

#### **Advanced Planning and Scheduling (APS)**
- **Objective**: Optimize production sequences across all departments
- **Features**:
  - Constraint-based scheduling (machine capacity, operator skills, material availability)
  - What-if scenario analysis
  - Automatic rescheduling on delays or shortages
  - Critical path method (CPM) for MO dependencies
- **Technology**: OR-Tools (Google Operations Research)
- **Impact**: 15-25% improvement in throughput
- **Complexity**: Very High | **Timeline**: 4-6 months
- **ROI**: Very High - maximizes production efficiency

#### **Inventory Optimization with AI**
- **Objective**: Minimize inventory costs while ensuring material availability
- **Features**:
  - Dynamic safety stock calculation based on lead time variability
  - Economic Order Quantity (EOQ) optimization
  - ABC analysis for inventory prioritization
  - Automatic reorder point suggestions
- **Complexity**: Medium | **Timeline**: 2-3 months
- **ROI**: High - reduces working capital needs

---

### 9.6 Collaboration & Communication 💬

#### **Integrated Communication Platform**
- **Objective**: Unified communication for production team
- **Features**:
  - In-app chat between departments
  - @mentions for specific users/roles
  - File sharing (photos, documents)
  - Integration with WhatsApp Business API
  - Broadcast messages from management
- **Technology**: Socket.io (already have WebSocket), WhatsApp Business API
- **Impact**: Faster issue resolution, better coordination
- **Complexity**: Low | **Timeline**: 1 month
- **ROI**: Medium - improves team collaboration

#### **Supplier Portal**
- **Objective**: Self-service portal for suppliers
- **Features**:
  - View PO status
  - Acknowledge orders
  - Update delivery schedules
  - Upload shipping documents
  - Invoice submission
- **Technology**: Separate React app with limited API access
- **Impact**: Reduces procurement admin work
- **Complexity**: Medium | **Timeline**: 2-3 months
- **ROI**: Medium - improves supplier relationships

---

### 9.7 Compliance & Sustainability 🌱

#### **Carbon Footprint Tracking**
- **Objective**: Measure and report environmental impact
- **Features**:
  - Energy consumption tracking per product
  - Material waste measurement
  - Carbon emissions calculation
  - Sustainability reports for IKEA compliance
- **Impact**: Meets ESG (Environmental, Social, Governance) standards
- **Complexity**: Medium | **Timeline**: 2 months
- **ROI**: Low (Compliance) - but may become mandatory

#### **Blockchain for Supply Chain Traceability**
- **Objective**: Immutable record of product journey
- **Features**:
  - End-to-end traceability from raw material to delivery
  - QR code for customers to verify authenticity
  - Supplier certification verification
  - Tamper-proof quality records
- **Technology**: Hyperledger Fabric (private blockchain)
- **Impact**: Enhanced trust and transparency
- **Complexity**: Very High | **Timeline**: 8-12 months
- **ROI**: Low-Medium - brand differentiation

---

### 9.8 Performance & Scalability 🚀

#### **Microservices Migration (Long-term)**
- **Objective**: Scale beyond modular monolith when needed
- **When to Consider**:
  - Multiple factories or locations
  - More than 500 concurrent users
  - Different scaling needs per module
- **Approach**: Gradual extraction of modules
  - Start with high-traffic modules (Warehouse, QC)
  - Keep core modules together initially
- **Complexity**: Very High | **Timeline**: 12-18 months
- **ROI**: Depends on scale - only if growth demands it

#### **Edge Computing for Factory Floor**
- **Objective**: Process data locally for faster response
- **Implementation**:
  - Edge servers at each department
  - Local data processing for real-time operations
  - Sync to central server periodically
- **Benefits**: Lower latency, works during WAN outages
- **Complexity**: High | **Timeline**: 4-6 months
- **ROI**: Medium - improves reliability

---

### 9.9 Advanced Reporting & Compliance 📑

#### **Automated Compliance Reports for IKEA**
- **Objective**: Generate ISO/IKEA compliance reports automatically
- **Features**:
  - ISO 8124 test result compilation
  - REACH compliance documentation
  - FSC/GOTS certification tracking
  - Automatic report generation on schedule
  - Digital signature for authenticity
- **Complexity**: Medium | **Timeline**: 2 months
- **ROI**: High - reduces manual reporting effort

#### **Business Intelligence (BI) Suite Integration**
- **Objective**: Advanced data analysis capabilities
- **Tools**: 
  - Power BI or Tableau integration
  - Superset (open-source alternative)
- **Features**:
  - Custom dashboards for each department
  - Drill-down analysis
  - Cross-departmental analytics
  - Export to PDF/Excel with branding
- **Complexity**: Medium | **Timeline**: 1-2 months
- **ROI**: High - empowers data-driven decisions

---

### 9.10 Training & Gamification 🎮

#### **Training Mode with Simulation**
- **Objective**: Train new operators without affecting production data
- **Features**:
  - Sandbox environment with dummy data
  - Guided tutorials with step-by-step instructions
  - Achievement badges for completed modules
  - Leaderboard for training completion
  - Quiz system for certification
- **Impact**: Faster onboarding, reduced training costs
- **Complexity**: Medium | **Timeline**: 2 months
- **ROI**: High - improves workforce readiness

#### **Gamification for Productivity**
- **Objective**: Motivate operators through game mechanics
- **Features**:
  - Daily/weekly challenges (e.g., "Complete 500 units with 0 defects")
  - Points system for quality performance
  - Team competitions between shifts
  - Recognition system (Employee of the Month)
- **Impact**: 10-15% productivity increase
- **Complexity**: Low | **Timeline**: 1 month
- **ROI**: Very High - low cost, high impact

---

## 9.11 PRIORITIZATION MATRIX

### **Must Have (High Value, Low Effort)**
1. ✅ RFID Integration (already planned)
2. ✅ Real-Time Production Dashboard
3. ✅ Offline-First Mobile App
4. ✅ Integrated Communication Platform
5. ✅ Training Mode with Simulation

### **Should Have (High Value, Medium Effort)**
6. ✅ Predictive Production Planning
7. ✅ Advanced Planning and Scheduling (APS)
8. ✅ Inventory Optimization with AI
9. ✅ Automated Compliance Reports
10. ✅ Voice Commands

### **Could Have (Medium Value, High Effort)**
11. 🟡 IoT Sensor Integration
12. 🟡 Computer Vision for Defect Detection
13. 🟡 Supplier Portal
14. 🟡 BI Suite Integration

### **Future Consideration (Low Priority)**
15. 🔴 Blockchain for Traceability
16. 🔴 Microservices Migration
17. 🔴 Carbon Footprint Tracking

---

## 9.12 IMPLEMENTATION ROADMAP (2026-2027)

### **Q2 2026 (Apr-Jun)**: Foundation Enhancements
- [ ] Real-Time Production Dashboard with KPIs
- [ ] Integrated Communication Platform
- [ ] Training Mode with Simulation
- [ ] Gamification for Productivity

**Estimated Cost**: $15,000 | **Team**: 2 developers | **Timeline**: 3 months

---

### **Q3 2026 (Jul-Sep)**: Mobile & AI Basics
- [ ] Offline-First Mobile App
- [ ] Voice Commands & Hands-Free Operation
- [ ] Inventory Optimization with AI
- [ ] Automated Compliance Reports

**Estimated Cost**: $25,000 | **Team**: 2 developers + 1 ML engineer | **Timeline**: 3 months

---

### **Q4 2026 (Oct-Dec)**: RFID Implementation (Phase 1)
- [ ] RFID Pilot in Warehouse
- [ ] Handheld reader deployment
- [ ] Training for warehouse staff
- [ ] Integration with existing barcode system

**Estimated Cost**: $35,000 (including hardware) | **Team**: 2 developers + 1 hardware engineer | **Timeline**: 3 months

---

### **Q1 2027 (Jan-Mar)**: Advanced Planning
- [ ] Predictive Production Planning (ML model)
- [ ] Advanced Planning and Scheduling (APS)
- [ ] NLP for Defect Reports
- [ ] BI Suite Integration

**Estimated Cost**: $30,000 | **Team**: 2 developers + 1 data scientist | **Timeline**: 3 months

---

### **Q2 2027 (Apr-Jun)**: RFID Expansion + IoT
- [ ] RFID expansion to all departments (Phase 2)
- [ ] IoT Sensor Integration (pilot)
- [ ] Supplier Portal
- [ ] Edge Computing setup

**Estimated Cost**: $50,000 (including hardware) | **Team**: 3 developers + 1 IoT engineer | **Timeline**: 3 months

---

### **Q3-Q4 2027**: Advanced AI & Vision
- [ ] Computer Vision for Defect Detection
- [ ] Complete RFID Migration (Phase 3)
- [ ] IoT rollout to all machines
- [ ] Advanced analytics models

**Estimated Cost**: $60,000+ | **Team**: 4 developers + 2 ML engineers | **Timeline**: 6 months

---

## 9.13 TECHNOLOGY EVALUATION

### **Emerging Technologies to Watch**

1. **5G for Factory Connectivity**
   - Ultra-low latency for real-time control
   - Massive IoT device connectivity
   - Private 5G network for security
   - **Timeline**: 2027-2028

2. **Digital Twin Technology**
   - Virtual replica of entire factory
   - Simulation for optimization
   - Predictive maintenance
   - **Timeline**: 2028+

3. **Collaborative Robots (Cobots)**
   - Work alongside human operators
   - Automatic stuffing and packing
   - Reduces physical strain
   - **Timeline**: 2027-2028

4. **Augmented Reality (AR) for Training**
   - AR glasses for step-by-step guidance
   - Remote expert assistance
   - Visual quality inspection aids
   - **Timeline**: 2027+

---

## 9.14 ESTIMATED TOTAL INVESTMENT (2026-2027)

| Category | Cost Range | Priority |
|----------|------------|----------|
| **Must Have Features** | $40,000 - $60,000 | ⭐⭐⭐ |
| **Should Have Features** | $50,000 - $80,000 | ⭐⭐ |
| **RFID Implementation** | $70,000 - $100,000 | ⭐⭐⭐ |
| **IoT & Industry 4.0** | $80,000 - $120,000 | ⭐⭐ |
| **AI & Computer Vision** | $60,000 - $100,000 | ⭐ |
| **Infrastructure & Scalability** | $30,000 - $50,000 | ⭐⭐ |

**Total Estimated Investment**: $330,000 - $510,000 over 18-24 months

**Expected ROI**: 
- Productivity improvement: 25-35%
- Quality improvement: 15-20%
- Cost reduction: 20-30%
- **Payback period**: 18-24 months

---

## 9.15 RISK ASSESSMENT

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| **Technology complexity** | High | High | Gradual rollout, pilot testing |
| **User adoption resistance** | Medium | Medium | Training, change management |
| **Hardware compatibility** | Medium | High | Vendor evaluation, POC testing |
| **Budget overrun** | Medium | High | Phased approach, strict cost control |
| **Integration challenges** | Medium | Medium | Modular design, API-first approach |
| **Vendor lock-in** | Low | Medium | Open standards, multi-vendor strategy |

---

## 9.16 SUCCESS METRICS

### **Technical KPIs**
- System uptime: >99.5%
- API response time: <200ms (95th percentile)
- Mobile app performance: 60fps
- Data accuracy: >99.9%
- Test coverage: >85%

### **Business KPIs**
- Production cycle time reduction: 20%+
- Quality defect rate: <2%
- Inventory turnover: +15%
- On-time delivery: >95%
- Training time reduction: 40%+

### **User Experience KPIs**
- User satisfaction: >4.5/5
- Mobile app adoption: >80% of operators
- Support tickets: <5% of active users/month
- Feature usage: >70% of available features

---

## 9.17 RECOMMENDATIONS SUMMARY

### **Immediate Actions (Next 3 Months)**
1. ✅ Implement Real-Time Production Dashboard
2. ✅ Add Integrated Communication Platform
3. ✅ Deploy Training Mode with Simulation
4. ✅ Start Offline-First Mobile App development

### **Short-Term (3-6 Months)**
1. 🟡 Complete Offline Mobile App
2. 🟡 Implement Voice Commands
3. 🟡 Deploy Inventory Optimization AI
4. 🟡 Pilot RFID in Warehouse

### **Medium-Term (6-12 Months)**
1. 🔴 Full RFID rollout
2. 🔴 Advanced Planning & Scheduling (APS)
3. 🔴 IoT sensor integration pilot
4. 🔴 Predictive analytics for demand forecasting

### **Long-Term (12-24 Months)**
1. ⚪ Computer Vision for QC
2. ⚪ Complete IoT implementation
3. ⚪ Edge computing deployment
4. ⚪ Advanced AI/ML models

---

## 📌 APPROVAL & SIGN-OFF

**Document Version**: 1.0  
**Date Prepared**: January 20, 2026  
**Prepared By**: Daniel Rizaldy (Senior IT Developer)

**Approval Required From**:
- [ ] IT Manager / CTO
- [ ] Production Manager
- [ ] Finance Director (Budget Approval)
- [ ] IKEA Compliance Representative

**Next Steps**:
1. Review recommendations with management team
2. Prioritize features based on business goals and budget
3. Create detailed project plan for approved items
4. Allocate resources and timeline
5. Begin implementation of Phase 1 (Q2 2026)

---

**Note**: All recommendations are based on:
- Current ERP system assessment (Score: 94/100)
- Industry 4.0 best practices
- IKEA manufacturing standards
- Cost-benefit analysis
- Technical feasibility study
- Market research on similar implementations

**Status**: ⏳ AWAITING MANAGEMENT APPROVAL

---

**Created by: Daniel Rizaldy**