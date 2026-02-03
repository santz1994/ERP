# 🗄️ ER DIAGRAM - DATABASE SCHEMA
**ERP Quty Karunia - Complete Database Schema**  
**Generated**: 2 Februari 2026  
**Total Tables**: 27 Tables

---

## 📊 ENTITY RELATIONSHIP DIAGRAM

```mermaid
erDiagram
    %% =================================================================
    %% MASTER DATA MODULE (6 Tables)
    %% =================================================================
    
    categories ||--o{ products : "has"
    categories {
        int id PK
        varchar name UK
        text description
        timestamp created_at
    }
    
    products ||--o{ products : "parent-child"
    products ||--o{ bom_headers : "has BOM"
    products ||--o{ stock_quants : "has stock"
    products ||--o{ stock_moves : "moves"
    products ||--o{ manufacturing_orders : "produces"
    products ||--o{ work_orders : "uses"
    products {
        int id PK
        varchar code UK "Article Code"
        varchar name "Product Name"
        enum type "Raw Material|WIP|Finish Good|Service"
        enum uom "Pcs|Meter|Yard|Kg|Roll|Cm"
        int category_id FK
        int parent_article_id FK "Parent Article"
        decimal min_stock "Safety Stock"
        boolean is_active
        timestamp created_at
    }
    
    partners ||--o{ purchase_orders : "orders from"
    partners ||--o{ sales_orders : "orders to"
    partners {
        int id PK
        varchar name
        enum type "Customer|Supplier|Subcon"
        text address
        varchar contact_person
        varchar phone
        varchar email
        timestamp created_at
    }
    
    %% =================================================================
    %% BOM MODULE (3 Tables)
    %% =================================================================
    
    bom_headers ||--o{ bom_details : "contains"
    bom_headers {
        int id PK
        int product_id FK "Article to produce"
        enum bom_type "Manufacturing|Kit/Phantom"
        decimal qty_output "Usually 1.0"
        boolean is_active
        varchar revision "Rev 1.0"
        boolean supports_multi_material
        varchar default_variant_selection
        int revised_by FK
        text revision_reason
        timestamp revision_date
        timestamp created_at
        timestamp updated_at
    }
    
    bom_details ||--o{ bom_variants : "has variants"
    bom_details {
        int id PK
        int bom_header_id FK
        int component_id FK "Material/WIP needed"
        decimal qty_needed "Qty per 1 unit"
        decimal wastage_percent "Estimated waste"
        boolean has_variants
        varchar variant_selection_mode
        timestamp created_at
        timestamp updated_at
    }
    
    bom_variants {
        int id PK
        int bom_detail_id FK
        int material_id FK
        enum variant_type "Primary|Alternative|Optional"
        int sequence "Preference order"
        decimal qty_variance "Override quantity"
        decimal qty_variance_percent
        decimal weight "Selection weight"
        decimal selection_probability
        int preferred_vendor_id FK
        int vendor_lead_time_days
        decimal cost_variance
        boolean is_active
        varchar approval_status
        text notes
        timestamp created_at
        timestamp updated_at
    }
    
    %% =================================================================
    %% SALES MODULE (2 Tables)
    %% =================================================================
    
    sales_orders ||--o{ sales_order_lines : "contains"
    sales_orders {
        int id PK
        varchar po_number_buyer UK "IKEA PO"
        int buyer_id FK
        date order_date
        int delivery_week "Week number"
        varchar destination "Country code"
        enum status "Draft|Confirmed|Production|Done|Cancelled"
        timestamp created_at
        timestamp updated_at
    }
    
    sales_order_lines ||--o{ manufacturing_orders : "triggers"
    sales_order_lines {
        int id PK
        int sales_order_id FK
        int product_id FK "Finish Good"
        decimal qty_ordered
        decimal qty_produced
        timestamp created_at
        timestamp updated_at
    }
    
    %% =================================================================
    %% MANUFACTURING MODULE (5 Tables)
    %% =================================================================
    
    manufacturing_orders ||--o{ work_orders : "creates"
    manufacturing_orders ||--o{ spks : "generates"
    manufacturing_orders ||--o{ transfer_logs : "tracks"
    manufacturing_orders {
        int id PK
        int so_line_id FK "Link to sales order"
        int product_id FK "Article to produce"
        decimal qty_planned "Target from BOM"
        decimal qty_produced "Actual output"
        enum routing_type "Route 1|Route 2|Route 3"
        varchar batch_number UK "Traceability"
        enum state "Draft|In Progress|Done|Cancelled"
        timestamp created_at
        timestamp started_at
        timestamp completed_at
    }
    
    spks ||--o{ spk_daily_production : "daily inputs"
    spks ||--o{ spk_production_completion : "completion"
    spks ||--o{ spk_modifications : "audit trail"
    spks ||--o{ material_debts : "negative inventory"
    spks ||--o{ spk_material_allocation : "allocations"
    spks {
        int id PK
        int mo_id FK
        enum department "Cutting|Embroidery|Sewing|Finishing|Packing"
        int original_qty "Initial target"
        int modified_qty "Modified target"
        int target_qty "Current target"
        int produced_qty "Actual produced"
        varchar modification_reason
        int modified_by_id FK
        timestamp modified_at
        varchar production_status "NOT_STARTED|IN_PROGRESS|COMPLETED|CANCELLED"
        date start_date
        date target_completion_date
        date completion_date
        boolean allow_negative_inventory
        varchar negative_approval_status
        int negative_approved_by_id FK
        timestamp negative_approved_at
        int created_by_id FK
        timestamp created_at
        timestamp updated_at
    }
    
    work_orders ||--o{ mo_material_consumption : "consumes"
    work_orders ||--o{ qc_inspections : "inspected"
    work_orders {
        int id PK
        int mo_id FK
        int product_id FK
        enum department
        enum status "Pending|Running|Finished"
        timestamp start_time
        timestamp end_time
        decimal input_qty "Material received"
        decimal output_qty "Can be Surplus/Shortage"
        decimal reject_qty "Defective units"
        int worker_id FK
        timestamp created_at
    }
    
    mo_material_consumption {
        int id PK
        int work_order_id FK
        int product_id FK "Material used"
        decimal qty_planned "Target by BOM"
        decimal qty_actual "Real consumption"
        int lot_id FK "Batch/roll"
        timestamp created_at
    }
    
    %% =================================================================
    %% SPK PRODUCTION TRACKING (5 Tables)
    %% =================================================================
    
    spk_daily_production {
        int id PK
        int spk_id FK
        date production_date
        int input_qty "Daily production"
        int cumulative_qty "Running total"
        int input_by_id FK
        varchar status "DRAFT|CONFIRMED|COMPLETED"
        varchar notes
        timestamp created_at
        timestamp updated_at
    }
    
    spk_production_completion {
        int id PK
        int spk_id FK
        int target_qty
        int actual_qty
        date completed_date
        int confirmed_by_id FK
        varchar confirmation_notes
        timestamp confirmed_at
        boolean is_completed
    }
    
    spk_modifications {
        int id PK
        int spk_id FK
        varchar field_name "qty|start_date|due_date"
        text old_value
        text new_value
        text modification_reason
        int modified_by_id FK
        timestamp modified_at
        varchar approval_status
        int approved_by_id FK
        timestamp approved_at
    }
    
    material_debts ||--o{ material_debt_settlements : "settled by"
    material_debts {
        int id PK
        int spk_id FK
        int material_id FK
        decimal qty_debt "Negative stock amount"
        varchar status "PENDING|PARTIALLY_SETTLED|FULLY_SETTLED"
        text reason
        int requested_by_id FK
        int approved_by_id FK
        timestamp requested_at
        timestamp approved_at
        timestamp created_at
        timestamp updated_at
    }
    
    material_debt_settlements {
        int id PK
        int material_debt_id FK
        decimal qty_settled "Amount settled"
        varchar settlement_type "PO_RECEIVED|MANUAL_ADJUSTMENT"
        text notes
        int settled_by_id FK
        timestamp settled_at
    }
    
    spk_material_allocation {
        int id PK
        int spk_id FK
        int material_id FK
        int mo_id FK
        decimal qty_needed
        decimal qty_allocated
        decimal qty_from_stock
        decimal qty_from_debt
        decimal wastage_qty
        decimal wastage_percentage
        enum allocation_status
        boolean material_shortage
        decimal shortage_qty
        int warehouse_location_id FK
        boolean has_material_debt
        int material_debt_id FK
        timestamp debt_created_at
        int allocated_by_id FK
        timestamp allocated_at
        timestamp completed_at
        varchar notes
        int bom_line_id FK
    }
    
    %% =================================================================
    %% WAREHOUSE MODULE (5 Tables)
    %% =================================================================
    
    purchase_orders ||--o{ stock_lots : "receives"
    purchase_orders {
        int id PK
        int supplier_id FK
        date order_date
        date expected_date
        enum status "Draft|Sent|Received|Done"
        varchar po_number UK
        timestamp created_at
        timestamp updated_at
    }
    
    locations ||--o{ stock_quants : "stores"
    locations ||--o{ stock_moves : "from/to"
    locations ||--o{ line_occupancy : "occupies"
    locations {
        int id PK
        varchar name UK "Rak A1|Line Sewing"
        enum type "View|Internal|Customer|Supplier|Production|Inventory Loss"
        decimal capacity
        boolean is_active
        timestamp created_at
    }
    
    stock_moves {
        int id PK
        int product_id FK
        decimal qty
        varchar uom "Pcs|Meter|Kg|Roll"
        int location_id_from FK
        int location_id_to FK
        varchar reference_doc "SPK|PO number"
        enum state "Draft|Done"
        int lot_id FK
        timestamp date
        timestamp created_at
    }
    
    stock_quants {
        int id PK
        int product_id FK
        int location_id FK
        decimal quantity "Current stock"
        varchar uom
        int lot_id FK
        timestamp last_updated
    }
    
    stock_lots {
        int id PK
        varchar lot_number UK
        int product_id FK
        int purchase_order_id FK
        decimal qty_received
        date receive_date
        date expiry_date
        varchar supplier_batch
        timestamp created_at
    }
    
    line_occupancy {
        int id PK
        int location_id FK "Production line"
        int manufacturing_order_id FK
        timestamp occupied_at
        timestamp released_at
        varchar status "OCCUPIED|RELEASED"
    }
    
    transfer_logs {
        int id PK
        int manufacturing_order_id FK
        enum from_dept
        enum to_dept
        decimal qty_transferred
        int transferred_by_id FK
        timestamp transferred_at
    }
    
    %% =================================================================
    %% QUALITY CONTROL MODULE (2 Tables)
    %% =================================================================
    
    qc_lab_tests {
        int id PK
        varchar batch_number "Lot Produksi"
        enum test_type "Drop Test|Stability 10|Stability 27|Seam Strength"
        enum test_result "Pass|Fail"
        numeric measured_value
        varchar measured_unit "Newton|cm|%"
        varchar iso_standard "ISO 8124"
        varchar test_location
        int inspector_id FK
        varchar evidence_photo_url
        timestamp tested_at
        timestamp created_at
    }
    
    qc_inspections {
        int id PK
        int work_order_id FK
        enum type "Incoming|Inline Sewing|Final Metal Detector"
        enum status "Pass|Fail"
        text defect_reason
        varchar defect_location
        int defect_qty
        int inspected_by FK
        varchar corrective_action
        timestamp inspected_at
        timestamp created_at
    }
    
    %% =================================================================
    %% KANBAN MODULE (3 Tables)
    %% =================================================================
    
    kanban_boards ||--o{ kanban_cards : "contains"
    kanban_boards ||--o{ kanban_rules : "has rules"
    kanban_boards {
        int id PK
        varchar name UK "Purchasing Board"
        varchar description
        boolean is_active
        timestamp created_at
    }
    
    kanban_cards {
        int id PK
        int board_id FK
        varchar title
        text description
        varchar stage "TODO|IN_PROGRESS|BLOCKED|DONE"
        int priority "1-5"
        int assigned_to FK
        date due_date
        int order_position "Display order"
        timestamp created_at
        timestamp updated_at
    }
    
    kanban_rules {
        int id PK
        int board_id FK
        varchar stage_name "Column name"
        int wip_limit "Max cards in stage"
        int order_position
        boolean is_active
    }
    
    %% =================================================================
    %% USER & AUDIT MODULE (4 Tables)
    %% =================================================================
    
    users ||--o{ audit_logs : "performs"
    users ||--o{ user_activity_logs : "activity"
    users ||--o{ security_logs : "security events"
    users {
        int id PK
        varchar username UK
        varchar email UK
        varchar hashed_password
        varchar full_name
        enum role "22 roles"
        varchar department
        boolean is_active
        boolean is_verified
        timestamp created_at
        timestamp last_login
        timestamp last_password_change
        int login_attempts
        timestamp locked_until
    }
    
    audit_logs {
        int id PK
        int user_id FK
        varchar action "CREATE|UPDATE|DELETE|VIEW"
        varchar table_name
        int record_id
        text old_value
        text new_value
        varchar ip_address
        timestamp created_at
    }
    
    user_activity_logs {
        int id PK
        int user_id FK
        varchar activity_type "LOGIN|LOGOUT|CREATE|UPDATE"
        varchar module "Production|Warehouse|QC"
        text description
        varchar ip_address
        timestamp created_at
    }
    
    security_logs {
        int id PK
        int user_id FK
        varchar event_type "FAILED_LOGIN|UNAUTHORIZED_ACCESS|PASSWORD_CHANGE"
        varchar severity "LOW|MEDIUM|HIGH|CRITICAL"
        text description
        varchar ip_address
        timestamp created_at
    }
    
    %% =================================================================
    %% EXCEPTION HANDLING MODULE (2 Tables)
    %% =================================================================
    
    alert_logs ||--o{ segregasi_acknowledgements : "requires action"
    alert_logs {
        int id PK
        varchar alert_type "SEGREGASI|QC_FAIL|STOCK_SHORTAGE"
        varchar severity "LOW|MEDIUM|HIGH|CRITICAL"
        text message
        varchar module "Production|QC|Warehouse"
        int related_record_id
        boolean is_resolved
        int resolved_by_id FK
        timestamp created_at
        timestamp resolved_at
    }
    
    segregasi_acknowledgements {
        int id PK
        int alert_id FK
        int work_order_id FK
        varchar segregation_reason
        int qty_segregated
        int acknowledged_by_id FK
        varchar disposal_action "REWORK|SCRAP|RETURN"
        timestamp acknowledged_at
    }
    
    %% =================================================================
    %% RELATIONSHIPS
    %% =================================================================
    
    users ||--o{ bom_headers : "revises"
    users ||--o{ bom_variants : "prefers vendor"
    users ||--o{ spks : "creates|modifies|approves"
    users ||--o{ spk_daily_production : "inputs"
    users ||--o{ spk_production_completion : "confirms"
    users ||--o{ spk_modifications : "modifies|approves"
    users ||--o{ material_debts : "requests|approves"
    users ||--o{ material_debt_settlements : "settles"
    users ||--o{ spk_material_allocation : "allocates"
    users ||--o{ work_orders : "worker"
    users ||--o{ transfer_logs : "transfers"
    users ||--o{ qc_lab_tests : "inspects"
    users ||--o{ qc_inspections : "inspects"
    users ||--o{ kanban_cards : "assigned"
    users ||--o{ alert_logs : "resolves"
    users ||--o{ segregasi_acknowledgements : "acknowledges"
    
    products ||--o{ bom_details : "component"
    products ||--o{ bom_variants : "material"
    products ||--o{ mo_material_consumption : "consumed"
    products ||--o{ stock_lots : "received"
    
    stock_lots ||--o{ stock_quants : "lot tracking"
    stock_lots ||--o{ stock_moves : "lot tracking"
    stock_lots ||--o{ mo_material_consumption : "lot tracking"
    
    manufacturing_orders ||--o{ line_occupancy : "occupies line"
```

---

## 📋 TABEL SUMMARY

### Master Data (6 Tables)
| Table | Records | Purpose |
|-------|---------|---------|
| categories | ~10 | Product categories |
| products | ~500 | Raw materials, WIP, Finish Goods |
| partners | ~50 | Customers, Suppliers, Subcon |
| users | ~40 | Staff with 22 roles |
| bom_headers | ~100 | Bill of Materials headers |
| bom_details | ~1000 | BOM components |

### Production (10 Tables)
| Table | Records | Purpose |
|-------|---------|---------|
| manufacturing_orders | ~1000/mo | Master production orders |
| spks | ~5000/mo | Per-department work orders |
| work_orders | ~5000/mo | Department work instructions |
| spk_daily_production | ~10000/mo | Daily production inputs |
| spk_production_completion | ~5000/mo | SPK completion records |
| spk_modifications | ~500/mo | SPK edit audit trail |
| material_debts | ~100/mo | Negative inventory tracking |
| material_debt_settlements | ~100/mo | Debt settlement records |
| spk_material_allocation | ~5000/mo | Material allocations |
| mo_material_consumption | ~10000/mo | Material consumption |

### Warehouse (6 Tables)
| Table | Records | Purpose |
|-------|---------|---------|
| purchase_orders | ~200/mo | Supplier POs |
| locations | ~50 | Warehouse & production locations |
| stock_moves | ~20000/mo | Inventory movements (FIFO) |
| stock_quants | ~500 | Current stock levels |
| stock_lots | ~1000 | Lot/batch tracking |
| line_occupancy | ~1000/mo | Production line tracking |
| transfer_logs | ~5000/mo | Inter-department transfers |

### Quality Control (2 Tables)
| Table | Records | Purpose |
|-------|---------|---------|
| qc_lab_tests | ~100/mo | Lab test results (ISO) |
| qc_inspections | ~5000/mo | Inline & final inspections |

### Sales (2 Tables)
| Table | Records | Purpose |
|-------|---------|---------|
| sales_orders | ~50/mo | IKEA customer orders |
| sales_order_lines | ~200/mo | Order line items |

### Supporting (5 Tables)
| Table | Records | Purpose |
|-------|---------|---------|
| kanban_boards | ~5 | Visual boards |
| kanban_cards | ~100 | Task cards |
| kanban_rules | ~20 | Board rules |
| audit_logs | unlimited | Full audit trail |
| user_activity_logs | unlimited | User activities |
| security_logs | unlimited | Security events |
| alert_logs | ~500/mo | System alerts |
| segregasi_acknowledgements | ~50/mo | QC failure handling |

---

## 🔑 KEY RELATIONSHIPS

### Primary Flow
```
SalesOrder → SalesOrderLine → ManufacturingOrder → SPK → SPKDailyProduction → SPKProductionCompletion
                                      ↓
                                  WorkOrder → MaterialConsumption → QCInspection
```

### Material Flow
```
PurchaseOrder → StockLot → StockMove → StockQuant → SPKMaterialAllocation → MaterialConsumption
                                                            ↓
                                                    (if shortage)
                                                            ↓
                                                    MaterialDebt → MaterialDebtSettlement
```

### BOM Flow
```
Product (Finish Good) → BOMHeader → BOMDetail → BOMVariant (Multi-material support)
                                         ↓
                                  SPKMaterialAllocation (Auto-allocate)
```

---

## 💡 SPECIAL FEATURES

### 1. Flexible Target System
- SPK can have different target than MO
- Supports surplus/shortage tracking
- Auto buffer allocation per department

### 2. Multi-Material BOM Support
- Primary, Alternative, Optional materials
- Vendor preference & cost variance
- Weighted selection algorithm

### 3. Material Debt Management
- Tracks negative inventory
- Settlement workflow
- Approval system

### 4. Comprehensive Audit Trail
- All modifications tracked
- User activity logging
- Security event monitoring

### 5. Quality Integration
- Lab tests (ISO standards)
- Inline inspections
- Metal detector checks
- Segregation handling

---

**CATATAN PENTING**:
- Database menggunakan **PostgreSQL 15**
- Total 27 Tables
- Supports **FIFO** inventory
- Full **audit trail** untuk semua transaksi
- **Multi-material** BOM support untuk flexibility
- **Negative inventory** tracking dengan approval workflow
