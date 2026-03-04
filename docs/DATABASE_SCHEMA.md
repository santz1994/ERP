# Database Schema — ERP Quty Karunia

> **Generated:** 2026-03-04 14:40  
> **Database:** `erp_quty_karunia`  
> **Engine:** PostgreSQL 18  
> **Total Tables:** 55  
> **Custom Enum Types:** 43

---
## Table of Contents

1. [Enum Types](#enum-types)
2. [Table Summary](#table-summary)
3. [Table Details](#table-details)
   - [alembic_version](#alembic-version)
   - [alert_logs](#alert-logs)
   - [approval_requests](#approval-requests)
   - [approval_steps](#approval-steps)
   - [audit_logs](#audit-logs)
   - [bom_details](#bom-details)
   - [bom_headers](#bom-headers)
   - [bom_variants](#bom-variants)
   - [bom_wip_routing](#bom-wip-routing)
   - [categories](#categories)
   - [defect_categories](#defect-categories)
   - [finishing_inputs_outputs](#finishing-inputs-outputs)
   - [finishing_material_consumptions](#finishing-material-consumptions)
   - [kanban_boards](#kanban-boards)
   - [kanban_cards](#kanban-cards)
   - [kanban_rules](#kanban-rules)
   - [line_occupancy](#line-occupancy)
   - [locations](#locations)
   - [manufacturing_orders](#manufacturing-orders)
   - [material_debt](#material-debt)
   - [material_debt_settlement](#material-debt-settlement)
   - [material_requests](#material-requests)
   - [mo_material_consumption](#mo-material-consumption)
   - [pallet_barcodes](#pallet-barcodes)
   - [partners](#partners)
   - [po_delete_requests](#po-delete-requests)
   - [products](#products)
   - [purchase_order_lines](#purchase-order-lines)
   - [purchase_orders](#purchase-orders)
   - [qc_checkpoints](#qc-checkpoints)
   - [qc_inspections](#qc-inspections)
   - [qc_lab_tests](#qc-lab-tests)
   - [rework_materials](#rework-materials)
   - [rework_requests](#rework-requests)
   - [sales_order_lines](#sales-order-lines)
   - [sales_orders](#sales-orders)
   - [security_logs](#security-logs)
   - [segregasi_acknowledgement](#segregasi-acknowledgement)
   - [spk_daily_production](#spk-daily-production)
   - [spk_edit_history](#spk-edit-history)
   - [spk_material_allocation](#spk-material-allocation)
   - [spk_material_allocation_old](#spk-material-allocation-old)
   - [spk_material_allocations](#spk-material-allocations)
   - [spk_modifications](#spk-modifications)
   - [spk_production_completion](#spk-production-completion)
   - [spks](#spks)
   - [stock_lots](#stock-lots)
   - [stock_moves](#stock-moves)
   - [stock_quants](#stock-quants)
   - [transfer_logs](#transfer-logs)
   - [user_activity_logs](#user-activity-logs)
   - [users](#users)
   - [warehouse_finishing_stocks](#warehouse-finishing-stocks)
   - [wip_transfer_logs](#wip-transfer-logs)
   - [work_orders](#work-orders)

---
## Enum Types

Custom PostgreSQL enum types used across the schema:

| Enum Type | Values |
|-----------|--------|
| `alertseverity` | `INFO` · `WARNING` · `CRITICAL` |
| `alertstatus` | `PENDING` · `ACKNOWLEDGED` · `RESOLVED` · `OVERRIDDEN` |
| `alerttype` | `LINE_CLEARANCE_BLOCK` · `SEGREGASI_ALARM` · `QC_FAIL` · `SHORTAGE` · `DUPLICATE_SCAN` · `SCANNER_OFFLINE` |
| `auditaction` | `CREATE` · `READ` · `UPDATE` · `DELETE` · `LOGIN` · `LOGOUT` · `APPROVE` · `REJECT` · `TRANSFER` · `EXPORT` · `IMPORT` |
| `auditmodule` | `AUTH` · `PPIC` · `CUTTING` · `EMBROIDERY` · `SEWING` · `FINISHING` · `PACKING` · `QUALITY` · `WAREHOUSE` · `KANBAN` · `REPORTS` · `ADMIN` |
| `bomcategory` | `Production` · `Purchase` |
| `bomtype` | `MANUFACTURING` · `KIT_PHANTOM` |
| `bomvarianttype` | `PRIMARY` · `ALTERNATIVE` · `OPTIONAL` |
| `clearancemethod` | `PHYSICAL_GAP` · `LINE_STOP` · `MANUAL_INSPECTION` |
| `defectseverity` | `MINOR` · `MAJOR` · `CRITICAL` |
| `defecttype` | `STITCHING` · `MATERIAL` · `FILLING` · `ASSEMBLY` · `PAINT` · `OTHER` |
| `department` | `CUTTING` · `EMBROIDERY` · `SUBCON` · `SEWING` · `FINISHING` · `PACKING` |
| `kanbanpriority` | `LOW` · `NORMAL` · `HIGH` · `URGENT` |
| `kanbanstatus` | `PENDING` · `APPROVED` · `IN_PROGRESS` · `COMPLETED` · `CANCELLED` |
| `linestatus` | `CLEAR` · `OCCUPIED` · `PAUSED` |
| `locationtype` | `VIEW` · `INTERNAL` · `CUSTOMER` · `SUPPLIER` · `PRODUCTION` · `INVENTORY_LOSS` |
| `materialrequeststatus` | `PENDING` · `APPROVED` · `REJECTED` · `COMPLETED` |
| `mostate` | `DRAFT` · `IN_PROGRESS` · `DONE` · `CANCELLED` |
| `motype` | `BUYER` · `PRODUCTION` |
| `palletstatus` | `PACKED` · `RECEIVED` · `SHIPPED` |
| `partnertype` | `CUSTOMER` · `SUPPLIER` · `SUBCON` |
| `poinputmode` | `AUTO_BOM` · `MANUAL` |
| `porequeststatus` | `PENDING` · `APPROVED` · `REJECTED` |
| `postatus` | `DRAFT` · `SENT` · `RECEIVED` · `DONE` |
| `potype` | `KAIN` · `LABEL` · `ACCESSORIES` |
| `producttype` | `RAW_MATERIAL` · `WIP` · `FINISH_GOOD` · `SERVICE` |
| `qccheckpointtype` | `AFTER_CUTTING` · `AFTER_SEWING` · `AFTER_FINISHING` · `PRE_PACKING` |
| `qcinspectiontype` | `INCOMING` · `INLINE_SEWING` · `FINAL_METAL_DETECTOR` |
| `qcstatus` | `PASS` · `FAIL` |
| `reworkstatus` | `PENDING` · `QC_REVIEW` · `APPROVED` · `REJECTED` · `IN_PROGRESS` · `COMPLETED` · `VERIFIED` |
| `routingtype` | `ROUTE1` · `ROUTE2` · `ROUTE3` |
| `sostatus` | `DRAFT` · `CONFIRMED` · `PRODUCTION` · `DONE` · `CANCELLED` |
| `spkeditstatus` | `PENDING_APPROVAL` · `APPROVED` · `REJECTED` · `APPLIED` · `CANCELLED` |
| `spkedittype` | `EDIT_QUANTITY` · `EDIT_DEADLINE` · `EDIT_NOTES` · `EDIT_ARTICLE` · `EDIT_MULTIPLE` |
| `spkmaterialallocationstatus` | `PENDING` · `ALLOCATED` · `DEBT_CREATED` · `FAILED` |
| `stockmovestatus` | `DRAFT` · `DONE` |
| `testresult` | `PASS` · `FAIL` |
| `testtype` | `DROP_TEST` · `STABILITY_10` · `STABILITY_27` · `SEAM_STRENGTH` |
| `transferdept` | `CUTTING` · `EMBROIDERY` · `SEWING` · `FINISHING` · `PACKING` · `SUBCON` · `FINISHGOOD` |
| `transferstatus` | `INITIATED` · `BLOCKED` · `LOCKED` · `ACCEPTED` · `COMPLETED` · `CANCELLED` |
| `uom` | `PCS` · `METER` · `YARD` · `KG` · `ROLL` · `CM` · `GRAM` · `CTN` · `BOX` · `CONE` · `PACK` · `LITER` · `SET` · `SHEET` · `LUSIN` · `BALL` |
| `userrole` | `DEVELOPER` · `SUPERADMIN` · `MANAGER` · `FINANCE_MANAGER` · `ADMIN` · `PPIC_MANAGER` · `PPIC_ADMIN` · `SPV_CUTTING` · `SPV_SEWING` · `SPV_FINISHING` · `WAREHOUSE_ADMIN` · `QC_LAB` · `PURCHASING_HEAD` · `PURCHASING` · `ADMIN_CUTTING` · `ADMIN_EMBROIDERY` · `ADMIN_SEWING` · `ADMIN_FINISHING` · `ADMIN_PACKING` · `QC_INSPECTOR` · `WAREHOUSE_OP` · `SECURITY` |
| `workorderstatus` | `PENDING` · `RUNNING` · `FINISHED` |

---
## Table Summary

| Table | Columns | Rows | FK Refs |
|-------|---------|------|---------|
| [`alembic_version`](#alembic-version) | 1 | 1 | — |
| [`alert_logs`](#alert-logs) | 14 | 0 | `users`, `users`, `users` |
| [`approval_requests`](#approval-requests) | 15 | 0 | `users`, `users` |
| [`approval_steps`](#approval-steps) | 9 | 0 | `approval_requests`, `users` |
| [`audit_logs`](#audit-logs) | 17 | 3 | `users` |
| [`bom_details`](#bom-details) | 9 | 9628 | `bom_headers`, `products` |
| [`bom_headers`](#bom-headers) | 16 | 1333 | `products`, `users` |
| [`bom_variants`](#bom-variants) | 17 | 0 | `bom_details`, `products`, `users` |
| [`bom_wip_routing`](#bom-wip-routing) | 9 | 0 | `bom_headers`, `products`, `products` |
| [`categories`](#categories) | 4 | 52 | — |
| [`defect_categories`](#defect-categories) | 9 | 0 | — |
| [`finishing_inputs_outputs`](#finishing-inputs-outputs) | 13 | 0 | `users`, `spks` |
| [`finishing_material_consumptions`](#finishing-material-consumptions) | 10 | 0 | `products`, `spks` |
| [`kanban_boards`](#kanban-boards) | 10 | 0 | — |
| [`kanban_cards`](#kanban-cards) | 23 | 0 | `users`, `users`, `users`, `products`, `users`, `work_orders` |
| [`kanban_rules`](#kanban-rules) | 8 | 0 | `products` |
| [`line_occupancy`](#line-occupancy) | 12 | 0 | `products`, `users` |
| [`locations`](#locations) | 6 | 5 | — |
| [`manufacturing_orders`](#manufacturing-orders) | 37 | 2 | `manufacturing_orders`, `products`, `purchase_orders`, `purchase_orders`, `purchase_orders`, `products`, `sales_order_lines` |
| [`material_debt`](#material-debt) | 12 | 0 | `users`, `users`, `products`, `spks` |
| [`material_debt_settlement`](#material-debt-settlement) | 8 | 0 | `material_debt`, `users`, `users` |
| [`material_requests`](#material-requests) | 16 | 0 | `users`, `locations`, `products`, `users`, `users` |
| [`mo_material_consumption`](#mo-material-consumption) | 7 | 0 | `stock_lots`, `products`, `work_orders` |
| [`pallet_barcodes`](#pallet-barcodes) | 11 | 0 | `locations`, `products`, `work_orders` |
| [`partners`](#partners) | 8 | 15 | — |
| [`po_delete_requests`](#po-delete-requests) | 10 | 0 | `purchase_orders`, `users`, `users` |
| [`products`](#products) | 13 | 1441 | `categories`, `products` |
| [`purchase_order_lines`](#purchase-order-lines) | 11 | 0 | `products`, `purchase_orders`, `partners` |
| [`purchase_orders`](#purchase-orders) | 26 | 1 | `users`, `products`, `manufacturing_orders`, `products`, `purchase_orders`, `partners` |
| [`qc_checkpoints`](#qc-checkpoints) | 14 | 0 | `users`, `work_orders` |
| [`qc_inspections`](#qc-inspections) | 10 | 0 | `users`, `work_orders` |
| [`qc_lab_tests`](#qc-lab-tests) | 12 | 0 | `users` |
| [`rework_materials`](#rework-materials) | 8 | 0 | `products`, `rework_requests` |
| [`rework_requests`](#rework-requests) | 23 | 0 | `defect_categories`, `users`, `users`, `users`, `spks`, `users` |
| [`sales_order_lines`](#sales-order-lines) | 7 | 0 | `products`, `sales_orders` |
| [`sales_orders`](#sales-orders) | 9 | 0 | `partners` |
| [`security_logs`](#security-logs) | 10 | 0 | `users` |
| [`segregasi_acknowledgement`](#segregasi-acknowledgement) | 8 | 0 | `users`, `transfer_logs` |
| [`spk_daily_production`](#spk-daily-production) | 10 | 0 | `users`, `spks` |
| [`spk_edit_history`](#spk-edit-history) | 24 | 0 | `users`, `users`, `users`, `users`, `users`, `spks` |
| [`spk_material_allocation`](#spk-material-allocation) | 14 | 0 | `users`, `products`, `spks` |
| [`spk_material_allocation_old`](#spk-material-allocation-old) | 14 | 0 | `users`, `products`, `spks` |
| [`spk_material_allocations`](#spk-material-allocations) | 12 | 0 | `products`, `work_orders` |
| [`spk_modifications`](#spk-modifications) | 8 | 0 | `users`, `spks` |
| [`spk_production_completion`](#spk-production-completion) | 9 | 0 | `users`, `spks` |
| [`spks`](#spks) | 28 | 0 | `users`, `manufacturing_orders`, `users`, `users` |
| [`stock_lots`](#stock-lots) | 10 | 0 | `products`, `purchase_orders`, `partners` |
| [`stock_moves`](#stock-moves) | 11 | 0 | `locations`, `locations`, `stock_lots`, `products` |
| [`stock_quants`](#stock-quants) | 7 | 1441 | `locations`, `stock_lots`, `products` |
| [`transfer_logs`](#transfer-logs) | 19 | 0 | `users`, `users`, `manufacturing_orders` |
| [`user_activity_logs`](#user-activity-logs) | 9 | 0 | `users` |
| [`users`](#users) | 14 | 14 | — |
| [`warehouse_finishing_stocks`](#warehouse-finishing-stocks) | 7 | 0 | `products` |
| [`wip_transfer_logs`](#wip-transfer-logs) | 10 | 0 | `users`, `products`, `work_orders` |
| [`work_orders`](#work-orders) | 26 | 1 | `products`, `products`, `manufacturing_orders`, `products`, `products`, `products`, `users` |

---
## Table Details

### `alembic_version`

| # | Column | Type | Nullable | Default | Notes |
|---|--------|------|----------|---------|-------|
| 1 | `version_num` | `varchar(100)` | NOT NULL |  | 🔑 PK |

**Indexes:**
- `alembic_version_pkey` — `CREATE UNIQUE INDEX alembic_version_pkey ON public.alembic_version USING btree (version_num)`

### `alert_logs`

| # | Column | Type | Nullable | Default | Notes |
|---|--------|------|----------|---------|-------|
| 1 | `id` | `integer` | NOT NULL | auto-increment | 🔑 PK |
| 2 | `alert_type` | `alerttype` | NOT NULL |  |  |
| 3 | `severity` | `alertseverity` | NOT NULL |  |  |
| 4 | `triggered_at` | `timestamp with time zone` |  | NOW() |  |
| 5 | `triggered_by` | `integer` |  |  | FK → `users.id` |
| 6 | `triggered_in_workflow_id` | `integer` |  |  |  |
| 7 | `escalated_to` | `integer` |  |  | FK → `users.id` |
| 8 | `escalation_level` | `integer` |  |  |  |
| 9 | `status` | `alertstatus` |  |  |  |
| 10 | `resolution_time` | `timestamp with time zone` |  |  |  |
| 11 | `resolved_by` | `integer` |  |  | FK → `users.id` |
| 12 | `message` | `varchar(500)` | NOT NULL |  |  |
| 13 | `notes` | `text` |  |  |  |
| 14 | `created_at` | `timestamp with time zone` |  | NOW() |  |

**Foreign Keys:**
- `escalated_to` → `users.id`
- `resolved_by` → `users.id`
- `triggered_by` → `users.id`

**Indexes:**
- `alert_logs_pkey` — `CREATE UNIQUE INDEX alert_logs_pkey ON public.alert_logs USING btree (id)`
- `ix_alert_logs_alert_type` — `CREATE INDEX ix_alert_logs_alert_type ON public.alert_logs USING btree (alert_type)`
- `ix_alert_logs_id` — `CREATE INDEX ix_alert_logs_id ON public.alert_logs USING btree (id)`
- `ix_alert_logs_severity` — `CREATE INDEX ix_alert_logs_severity ON public.alert_logs USING btree (severity)`
- `ix_alert_logs_status` — `CREATE INDEX ix_alert_logs_status ON public.alert_logs USING btree (status)`
- `ix_alert_logs_triggered_at` — `CREATE INDEX ix_alert_logs_triggered_at ON public.alert_logs USING btree (triggered_at)`

### `approval_requests`

| # | Column | Type | Nullable | Default | Notes |
|---|--------|------|----------|---------|-------|
| 1 | `id` | `uuid` | NOT NULL |  | 🔑 PK |
| 2 | `entity_type` | `varchar(50)` | NOT NULL |  |  |
| 3 | `entity_id` | `uuid` | NOT NULL |  |  |
| 4 | `submitted_by` | `integer` | NOT NULL |  | FK → `users.id` |
| 5 | `changes` | `json` | NOT NULL |  |  |
| 6 | `reason` | `text` | NOT NULL |  |  |
| 7 | `status` | `varchar(20)` | NOT NULL |  |  |
| 8 | `current_step` | `integer` | NOT NULL |  |  |
| 9 | `approval_chain` | `json` | NOT NULL |  |  |
| 10 | `approvals` | `json` |  |  |  |
| 11 | `rejection_reason` | `text` |  |  |  |
| 12 | `rejected_by` | `integer` |  |  | FK → `users.id` |
| 13 | `rejected_at` | `timestamp without time zone` |  |  |  |
| 14 | `created_at` | `timestamp without time zone` | NOT NULL |  |  |
| 15 | `updated_at` | `timestamp without time zone` |  |  |  |

**Foreign Keys:**
- `rejected_by` → `users.id`
- `submitted_by` → `users.id`

**Indexes:**
- `approval_requests_pkey` — `CREATE UNIQUE INDEX approval_requests_pkey ON public.approval_requests USING btree (id)`
- `idx_approval_requests_created` — `CREATE INDEX idx_approval_requests_created ON public.approval_requests USING btree (created_at)`
- `idx_approval_requests_entity` — `CREATE INDEX idx_approval_requests_entity ON public.approval_requests USING btree (entity_type, entity_id)`
- `idx_approval_requests_status` — `CREATE INDEX idx_approval_requests_status ON public.approval_requests USING btree (status)`
- `ix_approval_requests_entity_id` — `CREATE INDEX ix_approval_requests_entity_id ON public.approval_requests USING btree (entity_id)`
- `ix_approval_requests_entity_type` — `CREATE INDEX ix_approval_requests_entity_type ON public.approval_requests USING btree (entity_type)`
- `ix_approval_requests_status` — `CREATE INDEX ix_approval_requests_status ON public.approval_requests USING btree (status)`

### `approval_steps`

| # | Column | Type | Nullable | Default | Notes |
|---|--------|------|----------|---------|-------|
| 1 | `id` | `uuid` | NOT NULL |  | 🔑 PK |
| 2 | `approval_request_id` | `uuid` | NOT NULL |  | FK → `approval_requests.id` |
| 3 | `step_number` | `integer` | NOT NULL |  |  |
| 4 | `approver_role` | `varchar(50)` | NOT NULL |  |  |
| 5 | `status` | `varchar(20)` | NOT NULL |  |  |
| 6 | `approved_by` | `integer` |  |  | FK → `users.id` |
| 7 | `approved_at` | `timestamp without time zone` |  |  |  |
| 8 | `notes` | `text` |  |  |  |
| 9 | `created_at` | `timestamp without time zone` | NOT NULL |  |  |

**Foreign Keys:**
- `approval_request_id` → `approval_requests.id`
- `approved_by` → `users.id`

**Indexes:**
- `approval_steps_pkey` — `CREATE UNIQUE INDEX approval_steps_pkey ON public.approval_steps USING btree (id)`
- `idx_approval_steps_request` — `CREATE INDEX idx_approval_steps_request ON public.approval_steps USING btree (approval_request_id)`
- `idx_approval_steps_status` — `CREATE INDEX idx_approval_steps_status ON public.approval_steps USING btree (status)`
- `ix_approval_steps_approval_request_id` — `CREATE INDEX ix_approval_steps_approval_request_id ON public.approval_steps USING btree (approval_request_id)`
- `ix_approval_steps_status` — `CREATE INDEX ix_approval_steps_status ON public.approval_steps USING btree (status)`

### `audit_logs`

| # | Column | Type | Nullable | Default | Notes |
|---|--------|------|----------|---------|-------|
| 1 | `id` | `bigint` | NOT NULL | auto-increment | 🔑 PK |
| 2 | `timestamp` | `timestamp without time zone` | NOT NULL |  |  |
| 3 | `user_id` | `bigint` |  |  | FK → `users.id` |
| 4 | `username` | `varchar(100)` |  |  |  |
| 5 | `user_role` | `varchar(50)` |  |  |  |
| 6 | `ip_address` | `varchar(45)` |  |  |  |
| 7 | `action` | `auditaction` | NOT NULL |  |  |
| 8 | `module` | `auditmodule` | NOT NULL |  |  |
| 9 | `entity_type` | `varchar(100)` |  |  |  |
| 10 | `entity_id` | `bigint` |  |  |  |
| 11 | `description` | `text` | NOT NULL |  |  |
| 12 | `old_values` | `json` |  |  |  |
| 13 | `new_values` | `json` |  |  |  |
| 14 | `session_id` | `varchar(255)` |  |  |  |
| 15 | `request_method` | `varchar(10)` |  |  |  |
| 16 | `request_path` | `varchar(500)` |  |  |  |
| 17 | `response_status` | `bigint` |  |  |  |

**Foreign Keys:**
- `user_id` → `users.id`

**Indexes:**
- `audit_logs_pkey` — `CREATE UNIQUE INDEX audit_logs_pkey ON public.audit_logs USING btree (id)`
- `idx_audit_entity` — `CREATE INDEX idx_audit_entity ON public.audit_logs USING btree (entity_type, entity_id)`
- `idx_audit_module_action` — `CREATE INDEX idx_audit_module_action ON public.audit_logs USING btree (module, action)`
- `idx_audit_timestamp_user` — `CREATE INDEX idx_audit_timestamp_user ON public.audit_logs USING btree ("timestamp", user_id)`
- `ix_audit_logs_action` — `CREATE INDEX ix_audit_logs_action ON public.audit_logs USING btree (action)`
- `ix_audit_logs_entity_id` — `CREATE INDEX ix_audit_logs_entity_id ON public.audit_logs USING btree (entity_id)`
- `ix_audit_logs_entity_type` — `CREATE INDEX ix_audit_logs_entity_type ON public.audit_logs USING btree (entity_type)`
- `ix_audit_logs_module` — `CREATE INDEX ix_audit_logs_module ON public.audit_logs USING btree (module)`
- `ix_audit_logs_timestamp` — `CREATE INDEX ix_audit_logs_timestamp ON public.audit_logs USING btree ("timestamp")`
- `ix_audit_logs_user_id` — `CREATE INDEX ix_audit_logs_user_id ON public.audit_logs USING btree (user_id)`

### `bom_details`

| # | Column | Type | Nullable | Default | Notes |
|---|--------|------|----------|---------|-------|
| 1 | `id` | `integer` | NOT NULL | auto-increment | 🔑 PK |
| 2 | `bom_header_id` | `integer` | NOT NULL |  | FK → `bom_headers.id` |
| 3 | `component_id` | `integer` | NOT NULL |  | FK → `products.id` |
| 4 | `qty_needed` | `numeric(10,2)` | NOT NULL |  |  |
| 5 | `wastage_percent` | `numeric(5,2)` |  |  |  |
| 6 | `has_variants` | `boolean` |  |  |  |
| 7 | `variant_selection_mode` | `varchar(50)` |  |  |  |
| 8 | `created_at` | `timestamp with time zone` |  | NOW() |  |
| 9 | `updated_at` | `timestamp with time zone` |  | NOW() |  |

**Foreign Keys:**
- `bom_header_id` → `bom_headers.id`
- `component_id` → `products.id`

**Indexes:**
- `bom_details_pkey` — `CREATE UNIQUE INDEX bom_details_pkey ON public.bom_details USING btree (id)`
- `idx_bom_details_component_id` — `CREATE INDEX idx_bom_details_component_id ON public.bom_details USING btree (component_id)`
- `ix_bom_details_bom_header_id` — `CREATE INDEX ix_bom_details_bom_header_id ON public.bom_details USING btree (bom_header_id)`
- `ix_bom_details_id` — `CREATE INDEX ix_bom_details_id ON public.bom_details USING btree (id)`

### `bom_headers`

| # | Column | Type | Nullable | Default | Notes |
|---|--------|------|----------|---------|-------|
| 1 | `id` | `integer` | NOT NULL | auto-increment | 🔑 PK |
| 2 | `product_id` | `integer` | NOT NULL |  | FK → `products.id` |
| 3 | `bom_type` | `bomtype` | NOT NULL |  |  |
| 4 | `qty_output` | `numeric(10,2)` |  |  |  |
| 5 | `is_active` | `boolean` |  |  |  |
| 6 | `revision` | `varchar(10)` |  |  |  |
| 7 | `supports_multi_material` | `boolean` |  |  |  |
| 8 | `default_variant_selection` | `varchar(100)` |  |  |  |
| 9 | `revision_date` | `timestamp with time zone` |  | NOW() |  |
| 10 | `revised_by` | `integer` |  |  | FK → `users.id` |
| 11 | `revision_reason` | `text` |  |  |  |
| 12 | `created_at` | `timestamp with time zone` |  | NOW() |  |
| 13 | `updated_at` | `timestamp with time zone` |  | NOW() |  |
| 14 | `routing_department` | `varchar(50)` |  |  |  |
| 15 | `routing_sequence` | `integer` |  |  |  |
| 16 | `bom_category` | `bomcategory` | NOT NULL | 'Production'::bomcategory |  |

**Foreign Keys:**
- `product_id` → `products.id`
- `revised_by` → `users.id`

**Indexes:**
- `bom_headers_pkey` — `CREATE UNIQUE INDEX bom_headers_pkey ON public.bom_headers USING btree (id)`
- `idx_bom_headers_bom_category` — `CREATE INDEX idx_bom_headers_bom_category ON public.bom_headers USING btree (bom_category)`
- `idx_bom_headers_revision` — `CREATE INDEX idx_bom_headers_revision ON public.bom_headers USING btree (revision)`
- `ix_bom_headers_id` — `CREATE INDEX ix_bom_headers_id ON public.bom_headers USING btree (id)`
- `ix_bom_headers_is_active` — `CREATE INDEX ix_bom_headers_is_active ON public.bom_headers USING btree (is_active)`
- `ix_bom_headers_product_id` — `CREATE INDEX ix_bom_headers_product_id ON public.bom_headers USING btree (product_id)`

### `bom_variants`

| # | Column | Type | Nullable | Default | Notes |
|---|--------|------|----------|---------|-------|
| 1 | `id` | `integer` | NOT NULL | auto-increment | 🔑 PK |
| 2 | `bom_detail_id` | `integer` | NOT NULL |  | FK → `bom_details.id` |
| 3 | `material_id` | `integer` | NOT NULL |  | FK → `products.id` |
| 4 | `variant_type` | `bomvarianttype` |  |  |  |
| 5 | `sequence` | `integer` |  |  |  |
| 6 | `qty_variance` | `numeric(10,2)` |  |  |  |
| 7 | `qty_variance_percent` | `numeric(5,2)` |  |  |  |
| 8 | `weight` | `numeric(5,2)` |  |  |  |
| 9 | `selection_probability` | `numeric(5,2)` |  |  |  |
| 10 | `preferred_vendor_id` | `integer` |  |  | FK → `users.id` |
| 11 | `vendor_lead_time_days` | `integer` |  |  |  |
| 12 | `cost_variance` | `numeric(10,2)` |  |  |  |
| 13 | `is_active` | `boolean` |  |  |  |
| 14 | `approval_status` | `varchar(50)` |  |  |  |
| 15 | `notes` | `text` |  |  |  |
| 16 | `created_at` | `timestamp with time zone` |  | NOW() |  |
| 17 | `updated_at` | `timestamp with time zone` |  | NOW() |  |

**Foreign Keys:**
- `bom_detail_id` → `bom_details.id`
- `material_id` → `products.id`
- `preferred_vendor_id` → `users.id`

**Indexes:**
- `bom_variants_pkey` — `CREATE UNIQUE INDEX bom_variants_pkey ON public.bom_variants USING btree (id)`
- `ix_bom_variants_bom_detail_id` — `CREATE INDEX ix_bom_variants_bom_detail_id ON public.bom_variants USING btree (bom_detail_id)`
- `ix_bom_variants_id` — `CREATE INDEX ix_bom_variants_id ON public.bom_variants USING btree (id)`
- `ix_bom_variants_material_id` — `CREATE INDEX ix_bom_variants_material_id ON public.bom_variants USING btree (material_id)`

### `bom_wip_routing`

| # | Column | Type | Nullable | Default | Notes |
|---|--------|------|----------|---------|-------|
| 1 | `id` | `integer` | NOT NULL | auto-increment | 🔑 PK |
| 2 | `bom_header_id` | `integer` | NOT NULL |  | FK → `bom_headers.id` |
| 3 | `department` | `varchar(50)` | NOT NULL |  |  |
| 4 | `sequence` | `integer` | NOT NULL |  |  |
| 5 | `input_wip_product_id` | `integer` |  |  | FK → `products.id` |
| 6 | `output_wip_product_id` | `integer` | NOT NULL |  | FK → `products.id` |
| 7 | `is_optional` | `boolean` |  |  |  |
| 8 | `created_at` | `timestamp with time zone` |  | NOW() |  |
| 9 | `updated_at` | `timestamp with time zone` |  | NOW() |  |

**Foreign Keys:**
- `bom_header_id` → `bom_headers.id`
- `input_wip_product_id` → `products.id`
- `output_wip_product_id` → `products.id`

**Indexes:**
- `bom_wip_routing_pkey` — `CREATE UNIQUE INDEX bom_wip_routing_pkey ON public.bom_wip_routing USING btree (id)`
- `idx_bom_wip_routing_bom_header` — `CREATE INDEX idx_bom_wip_routing_bom_header ON public.bom_wip_routing USING btree (bom_header_id)`
- `idx_bom_wip_routing_department` — `CREATE INDEX idx_bom_wip_routing_department ON public.bom_wip_routing USING btree (department)`

### `categories`

| # | Column | Type | Nullable | Default | Notes |
|---|--------|------|----------|---------|-------|
| 1 | `id` | `integer` | NOT NULL | auto-increment | 🔑 PK |
| 2 | `name` | `varchar(100)` | NOT NULL |  | UNIQUE |
| 3 | `description` | `text` |  |  |  |
| 4 | `created_at` | `timestamp with time zone` |  | NOW() |  |

**Indexes:**
- `categories_name_key` — `CREATE UNIQUE INDEX categories_name_key ON public.categories USING btree (name)`
- `categories_pkey` — `CREATE UNIQUE INDEX categories_pkey ON public.categories USING btree (id)`
- `ix_categories_id` — `CREATE INDEX ix_categories_id ON public.categories USING btree (id)`

### `defect_categories`

| # | Column | Type | Nullable | Default | Notes |
|---|--------|------|----------|---------|-------|
| 1 | `id` | `integer` | NOT NULL | auto-increment | 🔑 PK |
| 2 | `code` | `varchar(50)` | NOT NULL |  |  |
| 3 | `name` | `varchar(100)` | NOT NULL |  |  |
| 4 | `defect_type` | `defecttype` | NOT NULL |  |  |
| 5 | `description` | `varchar(500)` |  |  |  |
| 6 | `severity` | `defectseverity` | NOT NULL |  |  |
| 7 | `default_rework_hours` | `integer` |  |  |  |
| 8 | `created_at` | `timestamp with time zone` |  | NOW() |  |
| 9 | `updated_at` | `timestamp with time zone` |  | NOW() |  |

**Indexes:**
- `defect_categories_pkey` — `CREATE UNIQUE INDEX defect_categories_pkey ON public.defect_categories USING btree (id)`
- `ix_defect_categories_code` — `CREATE UNIQUE INDEX ix_defect_categories_code ON public.defect_categories USING btree (code)`
- `ix_defect_categories_id` — `CREATE INDEX ix_defect_categories_id ON public.defect_categories USING btree (id)`

### `finishing_inputs_outputs`

| # | Column | Type | Nullable | Default | Notes |
|---|--------|------|----------|---------|-------|
| 1 | `id` | `integer` | NOT NULL | auto-increment | 🔑 PK |
| 2 | `spk_id` | `integer` | NOT NULL |  | FK → `spks.id` |
| 3 | `stage` | `varchar(20)` | NOT NULL |  |  |
| 4 | `production_date` | `date` | NOT NULL |  |  |
| 5 | `input_qty` | `numeric(10,2)` | NOT NULL |  |  |
| 6 | `good_qty` | `numeric(10,2)` | NOT NULL |  |  |
| 7 | `defect_qty` | `numeric(10,2)` | NOT NULL |  |  |
| 8 | `rework_qty` | `numeric(10,2)` | NOT NULL | '0'::numeric |  |
| 9 | `yield_rate` | `numeric(5,2)` | NOT NULL |  |  |
| 10 | `operator_id` | `integer` |  |  | FK → `users.id` |
| 11 | `notes` | `text` |  |  |  |
| 12 | `created_at` | `timestamp without time zone` | NOT NULL | NOW() |  |
| 13 | `updated_at` | `timestamp without time zone` | NOT NULL | NOW() |  |

**Foreign Keys:**
- `operator_id` → `users.id`
- `spk_id` → `spks.id`

**Indexes:**
- `finishing_inputs_outputs_pkey` — `CREATE UNIQUE INDEX finishing_inputs_outputs_pkey ON public.finishing_inputs_outputs USING btree (id)`
- `ix_finishing_inputs_outputs_production_date` — `CREATE INDEX ix_finishing_inputs_outputs_production_date ON public.finishing_inputs_outputs USING btree (production_date)`
- `ix_finishing_inputs_outputs_spk_id` — `CREATE INDEX ix_finishing_inputs_outputs_spk_id ON public.finishing_inputs_outputs USING btree (spk_id)`

### `finishing_material_consumptions`

| # | Column | Type | Nullable | Default | Notes |
|---|--------|------|----------|---------|-------|
| 1 | `id` | `integer` | NOT NULL | auto-increment | 🔑 PK |
| 2 | `spk_id` | `integer` | NOT NULL |  | FK → `spks.id` |
| 3 | `stage` | `varchar(20)` | NOT NULL |  |  |
| 4 | `material_id` | `integer` | NOT NULL |  | FK → `products.id` |
| 5 | `qty_planned` | `numeric(10,2)` | NOT NULL |  |  |
| 6 | `qty_actual` | `numeric(10,2)` |  |  |  |
| 7 | `uom` | `varchar(10)` | NOT NULL |  |  |
| 8 | `lot_id` | `integer` |  |  |  |
| 9 | `created_at` | `timestamp without time zone` | NOT NULL | NOW() |  |
| 10 | `updated_at` | `timestamp without time zone` | NOT NULL | NOW() |  |

**Foreign Keys:**
- `material_id` → `products.id`
- `spk_id` → `spks.id`

**Indexes:**
- `finishing_material_consumptions_pkey` — `CREATE UNIQUE INDEX finishing_material_consumptions_pkey ON public.finishing_material_consumptions USING btree (id)`
- `ix_finishing_material_consumptions_spk_id` — `CREATE INDEX ix_finishing_material_consumptions_spk_id ON public.finishing_material_consumptions USING btree (spk_id)`

### `kanban_boards`

| # | Column | Type | Nullable | Default | Notes |
|---|--------|------|----------|---------|-------|
| 1 | `id` | `bigint` | NOT NULL | auto-increment | 🔑 PK |
| 2 | `department` | `varchar(50)` | NOT NULL |  | UNIQUE |
| 3 | `max_pending` | `integer` |  |  |  |
| 4 | `max_in_progress` | `integer` |  |  |  |
| 5 | `enable_auto_approve` | `boolean` |  |  |  |
| 6 | `auto_approve_threshold` | `integer` |  |  |  |
| 7 | `notify_on_new_card` | `boolean` |  |  |  |
| 8 | `notify_on_approval` | `boolean` |  |  |  |
| 9 | `notify_on_fulfillment` | `boolean` |  |  |  |
| 10 | `is_active` | `boolean` |  |  |  |

**Indexes:**
- `kanban_boards_department_key` — `CREATE UNIQUE INDEX kanban_boards_department_key ON public.kanban_boards USING btree (department)`
- `kanban_boards_pkey` — `CREATE UNIQUE INDEX kanban_boards_pkey ON public.kanban_boards USING btree (id)`

### `kanban_cards`

| # | Column | Type | Nullable | Default | Notes |
|---|--------|------|----------|---------|-------|
| 1 | `id` | `bigint` | NOT NULL | auto-increment | 🔑 PK |
| 2 | `card_number` | `varchar(50)` | NOT NULL |  |  |
| 3 | `requested_by_dept` | `varchar(50)` | NOT NULL |  |  |
| 4 | `requested_by_user_id` | `bigint` | NOT NULL |  | FK → `users.id` |
| 5 | `requested_at` | `timestamp without time zone` | NOT NULL |  |  |
| 6 | `product_id` | `bigint` | NOT NULL |  | FK → `products.id` |
| 7 | `qty_requested` | `integer` | NOT NULL |  |  |
| 8 | `priority` | `kanbanpriority` | NOT NULL |  |  |
| 9 | `needed_by` | `timestamp without time zone` |  |  |  |
| 10 | `status` | `kanbanstatus` | NOT NULL |  |  |
| 11 | `approved_by_user_id` | `bigint` |  |  | FK → `users.id` |
| 12 | `approved_at` | `timestamp without time zone` |  |  |  |
| 13 | `qty_fulfilled` | `integer` | NOT NULL |  |  |
| 14 | `fulfilled_by_user_id` | `bigint` |  |  | FK → `users.id` |
| 15 | `fulfilled_at` | `timestamp without time zone` |  |  |  |
| 16 | `work_order_id` | `bigint` |  |  | FK → `work_orders.id` |
| 17 | `request_reason` | `text` |  |  |  |
| 18 | `fulfillment_notes` | `text` |  |  |  |
| 19 | `is_auto_replenish` | `boolean` |  |  |  |
| 20 | `reorder_point` | `integer` |  |  |  |
| 21 | `cancelled_by_user_id` | `bigint` |  |  | FK → `users.id` |
| 22 | `cancelled_at` | `timestamp without time zone` |  |  |  |
| 23 | `cancellation_reason` | `text` |  |  |  |

**Foreign Keys:**
- `approved_by_user_id` → `users.id`
- `cancelled_by_user_id` → `users.id`
- `fulfilled_by_user_id` → `users.id`
- `product_id` → `products.id`
- `requested_by_user_id` → `users.id`
- `work_order_id` → `work_orders.id`

**Indexes:**
- `ix_kanban_cards_card_number` — `CREATE UNIQUE INDEX ix_kanban_cards_card_number ON public.kanban_cards USING btree (card_number)`
- `ix_kanban_cards_requested_by_dept` — `CREATE INDEX ix_kanban_cards_requested_by_dept ON public.kanban_cards USING btree (requested_by_dept)`
- `ix_kanban_cards_status` — `CREATE INDEX ix_kanban_cards_status ON public.kanban_cards USING btree (status)`
- `kanban_cards_pkey` — `CREATE UNIQUE INDEX kanban_cards_pkey ON public.kanban_cards USING btree (id)`

### `kanban_rules`

| # | Column | Type | Nullable | Default | Notes |
|---|--------|------|----------|---------|-------|
| 1 | `id` | `bigint` | NOT NULL | auto-increment | 🔑 PK |
| 2 | `product_id` | `bigint` | NOT NULL |  | FK → `products.id` |
| 3 | `department` | `varchar(50)` | NOT NULL |  |  |
| 4 | `reorder_point` | `integer` | NOT NULL |  |  |
| 5 | `order_quantity` | `integer` | NOT NULL |  |  |
| 6 | `default_priority` | `kanbanpriority` |  |  |  |
| 7 | `lead_time_days` | `integer` |  |  |  |
| 8 | `is_active` | `boolean` |  |  |  |

**Foreign Keys:**
- `product_id` → `products.id`

**Indexes:**
- `kanban_rules_pkey` — `CREATE UNIQUE INDEX kanban_rules_pkey ON public.kanban_rules USING btree (id)`

### `line_occupancy`

| # | Column | Type | Nullable | Default | Notes |
|---|--------|------|----------|---------|-------|
| 1 | `id` | `integer` | NOT NULL | auto-increment | 🔑 PK |
| 2 | `dept_name` | `transferdept` | NOT NULL |  |  |
| 3 | `line_number` | `integer` |  |  |  |
| 4 | `current_article_id` | `integer` |  |  | FK → `products.id` |
| 5 | `current_batch_id` | `varchar(50)` |  |  |  |
| 6 | `current_destination` | `varchar(50)` |  |  |  |
| 7 | `current_week` | `integer` |  |  |  |
| 8 | `occupancy_status` | `linestatus` |  |  |  |
| 9 | `locked_at` | `timestamp with time zone` |  |  |  |
| 10 | `locked_by` | `integer` |  |  | FK → `users.id` |
| 11 | `expected_clear_time` | `timestamp with time zone` |  |  |  |
| 12 | `updated_at` | `timestamp with time zone` |  | NOW() |  |

**Foreign Keys:**
- `current_article_id` → `products.id`
- `locked_by` → `users.id`

**Indexes:**
- `ix_line_occupancy_current_batch_id` — `CREATE INDEX ix_line_occupancy_current_batch_id ON public.line_occupancy USING btree (current_batch_id)`
- `ix_line_occupancy_dept_name` — `CREATE INDEX ix_line_occupancy_dept_name ON public.line_occupancy USING btree (dept_name)`
- `ix_line_occupancy_id` — `CREATE INDEX ix_line_occupancy_id ON public.line_occupancy USING btree (id)`
- `ix_line_occupancy_occupancy_status` — `CREATE INDEX ix_line_occupancy_occupancy_status ON public.line_occupancy USING btree (occupancy_status)`
- `line_occupancy_pkey` — `CREATE UNIQUE INDEX line_occupancy_pkey ON public.line_occupancy USING btree (id)`

### `locations`

| # | Column | Type | Nullable | Default | Notes |
|---|--------|------|----------|---------|-------|
| 1 | `id` | `integer` | NOT NULL | auto-increment | 🔑 PK |
| 2 | `name` | `varchar(100)` | NOT NULL |  |  |
| 3 | `type` | `locationtype` | NOT NULL |  |  |
| 4 | `capacity` | `numeric(10,2)` |  |  |  |
| 5 | `created_at` | `timestamp with time zone` |  | NOW() |  |
| 6 | `is_active` | `boolean` |  |  |  |

**Indexes:**
- `ix_locations_id` — `CREATE INDEX ix_locations_id ON public.locations USING btree (id)`
- `ix_locations_name` — `CREATE UNIQUE INDEX ix_locations_name ON public.locations USING btree (name)`
- `ix_locations_type` — `CREATE INDEX ix_locations_type ON public.locations USING btree (type)`
- `locations_pkey` — `CREATE UNIQUE INDEX locations_pkey ON public.locations USING btree (id)`

### `manufacturing_orders`

| # | Column | Type | Nullable | Default | Notes |
|---|--------|------|----------|---------|-------|
| 1 | `id` | `integer` | NOT NULL | auto-increment | 🔑 PK |
| 2 | `so_line_id` | `integer` |  |  | FK → `sales_order_lines.id` |
| 3 | `product_id` | `integer` | NOT NULL |  | FK → `products.id` |
| 4 | `qty_planned` | `numeric(10,2)` | NOT NULL |  |  |
| 5 | `qty_produced` | `numeric(10,2)` |  |  |  |
| 6 | `routing_type` | `routingtype` | NOT NULL |  |  |
| 7 | `batch_number` | `varchar(50)` | NOT NULL |  |  |
| 8 | `state` | `mostate` |  |  |  |
| 9 | `created_at` | `timestamp with time zone` |  | NOW() |  |
| 10 | `started_at` | `timestamp with time zone` |  |  |  |
| 11 | `completed_at` | `timestamp with time zone` |  |  |  |
| 12 | `finished_good_product_id` | `integer` |  |  | FK → `products.id` |
| 13 | `bom_explosion_complete` | `boolean` |  |  |  |
| 14 | `total_departments` | `integer` |  |  |  |
| 15 | `po_id` | `integer` |  |  | FK → `purchase_orders.id` |
| 16 | `planned_production_date` | `date` |  |  |  |
| 17 | `actual_production_start_date` | `date` |  |  |  |
| 18 | `actual_production_end_date` | `date` |  |  |  |
| 19 | `label_production_date` | `date` |  |  |  |
| 20 | `production_week` | `varchar(10)` |  |  |  |
| 21 | `destination_country` | `varchar(50)` |  |  |  |
| 22 | `traceability_code` | `varchar(50)` |  |  |  |
| 23 | `target_shipment_date` | `date` |  |  |  |
| 24 | `po_fabric_id` | `integer` |  |  | FK → `purchase_orders.id` |
| 25 | `po_label_id` | `integer` |  |  | FK → `purchase_orders.id` |
| 26 | `trigger_mode` | `varchar(20)` | NOT NULL | 'PARTIAL'::character varying |  |
| 27 | `target_quantity` | `numeric(15,3)` | NOT NULL |  |  |
| 28 | `buffer_quantity` | `numeric(15,3)` | NOT NULL |  |  |
| 29 | `production_quantity` | `numeric(15,3)` | NOT NULL |  |  |
| 30 | `auto_calculate_buffer` | `boolean` | NOT NULL |  |  |
| 31 | `week` | `varchar(50)` |  |  |  |
| 32 | `destination` | `varchar(100)` |  |  |  |
| 33 | `week_destination_locked` | `boolean` | NOT NULL |  |  |
| 34 | `extra_metadata` | `json` |  |  |  |
| 35 | `mo_type` | `varchar(20)` | NOT NULL | 'PRODUCTION'::character varying |  |
| 36 | `is_qty_locked` | `boolean` | NOT NULL | false |  |
| 37 | `buyer_mo_id` | `integer` |  |  | FK → `manufacturing_orders.id` |

**Foreign Keys:**
- `buyer_mo_id` → `manufacturing_orders.id`
- `finished_good_product_id` → `products.id`
- `po_fabric_id` → `purchase_orders.id`
- `po_id` → `purchase_orders.id`
- `po_label_id` → `purchase_orders.id`
- `product_id` → `products.id`
- `so_line_id` → `sales_order_lines.id`

**Indexes:**
- `idx_mo_destination` — `CREATE INDEX idx_mo_destination ON public.manufacturing_orders USING btree (destination)`
- `idx_mo_fg_product` — `CREATE INDEX idx_mo_fg_product ON public.manufacturing_orders USING btree (finished_good_product_id)`
- `idx_mo_label_date` — `CREATE INDEX idx_mo_label_date ON public.manufacturing_orders USING btree (label_production_date)`
- `idx_mo_planned_date` — `CREATE INDEX idx_mo_planned_date ON public.manufacturing_orders USING btree (planned_production_date)`
- `idx_mo_production_week` — `CREATE INDEX idx_mo_production_week ON public.manufacturing_orders USING btree (production_week)`
- `idx_mo_week` — `CREATE INDEX idx_mo_week ON public.manufacturing_orders USING btree (week)`
- `idx_mo_week_dest_locked` — `CREATE INDEX idx_mo_week_dest_locked ON public.manufacturing_orders USING btree (week_destination_locked)`
- `ix_manufacturing_orders_batch_number` — `CREATE UNIQUE INDEX ix_manufacturing_orders_batch_number ON public.manufacturing_orders USING btree (batch_number)`
- `ix_manufacturing_orders_destination_country` — `CREATE INDEX ix_manufacturing_orders_destination_country ON public.manufacturing_orders USING btree (destination_country)`
- `ix_manufacturing_orders_id` — `CREATE INDEX ix_manufacturing_orders_id ON public.manufacturing_orders USING btree (id)`
- `ix_manufacturing_orders_po_fabric_id` — `CREATE INDEX ix_manufacturing_orders_po_fabric_id ON public.manufacturing_orders USING btree (po_fabric_id)`
- `ix_manufacturing_orders_po_label_id` — `CREATE INDEX ix_manufacturing_orders_po_label_id ON public.manufacturing_orders USING btree (po_label_id)`
- `ix_manufacturing_orders_production_week` — `CREATE INDEX ix_manufacturing_orders_production_week ON public.manufacturing_orders USING btree (production_week)`
- `ix_manufacturing_orders_routing_type` — `CREATE INDEX ix_manufacturing_orders_routing_type ON public.manufacturing_orders USING btree (routing_type)`
- `ix_manufacturing_orders_state` — `CREATE INDEX ix_manufacturing_orders_state ON public.manufacturing_orders USING btree (state)`
- `ix_manufacturing_orders_traceability_code` — `CREATE UNIQUE INDEX ix_manufacturing_orders_traceability_code ON public.manufacturing_orders USING btree (traceability_code)`
- `ix_manufacturing_orders_trigger_mode` — `CREATE INDEX ix_manufacturing_orders_trigger_mode ON public.manufacturing_orders USING btree (trigger_mode)`
- `manufacturing_orders_pkey` — `CREATE UNIQUE INDEX manufacturing_orders_pkey ON public.manufacturing_orders USING btree (id)`

### `material_debt`

| # | Column | Type | Nullable | Default | Notes |
|---|--------|------|----------|---------|-------|
| 1 | `id` | `integer` | NOT NULL | auto-increment | 🔑 PK |
| 2 | `spk_id` | `integer` | NOT NULL |  | FK → `spks.id` |
| 3 | `product_id` | `integer` | NOT NULL |  | FK → `products.id` |
| 4 | `qty_owed` | `integer` | NOT NULL |  |  |
| 5 | `qty_settled` | `integer` |  |  |  |
| 6 | `approval_status` | `varchar(50)` |  |  |  |
| 7 | `created_by_id` | `integer` | NOT NULL |  | FK → `users.id` |
| 8 | `approved_by_id` | `integer` |  |  | FK → `users.id` |
| 9 | `approved_at` | `timestamp without time zone` |  |  |  |
| 10 | `approval_reason` | `varchar(255)` |  |  |  |
| 11 | `created_at` | `timestamp without time zone` |  |  |  |
| 12 | `updated_at` | `timestamp without time zone` |  |  |  |

**Foreign Keys:**
- `approved_by_id` → `users.id`
- `created_by_id` → `users.id`
- `product_id` → `products.id`
- `spk_id` → `spks.id`

**Indexes:**
- `ix_material_debt_id` — `CREATE INDEX ix_material_debt_id ON public.material_debt USING btree (id)`
- `ix_material_debt_spk_id` — `CREATE INDEX ix_material_debt_spk_id ON public.material_debt USING btree (spk_id)`
- `material_debt_pkey` — `CREATE UNIQUE INDEX material_debt_pkey ON public.material_debt USING btree (id)`

### `material_debt_settlement`

| # | Column | Type | Nullable | Default | Notes |
|---|--------|------|----------|---------|-------|
| 1 | `id` | `integer` | NOT NULL | auto-increment | 🔑 PK |
| 2 | `material_debt_id` | `integer` | NOT NULL |  | FK → `material_debt.id` |
| 3 | `qty_settled` | `integer` | NOT NULL |  |  |
| 4 | `settlement_date` | `date` | NOT NULL |  |  |
| 5 | `received_by_id` | `integer` | NOT NULL |  | FK → `users.id` |
| 6 | `settled_by_id` | `integer` | NOT NULL |  | FK → `users.id` |
| 7 | `settlement_notes` | `varchar(255)` |  |  |  |
| 8 | `created_at` | `timestamp without time zone` |  |  |  |

**Foreign Keys:**
- `material_debt_id` → `material_debt.id`
- `received_by_id` → `users.id`
- `settled_by_id` → `users.id`

**Indexes:**
- `ix_material_debt_settlement_id` — `CREATE INDEX ix_material_debt_settlement_id ON public.material_debt_settlement USING btree (id)`
- `ix_material_debt_settlement_material_debt_id` — `CREATE INDEX ix_material_debt_settlement_material_debt_id ON public.material_debt_settlement USING btree (material_debt_id)`
- `ix_material_debt_settlement_settlement_date` — `CREATE INDEX ix_material_debt_settlement_settlement_date ON public.material_debt_settlement USING btree (settlement_date)`
- `material_debt_settlement_pkey` — `CREATE UNIQUE INDEX material_debt_settlement_pkey ON public.material_debt_settlement USING btree (id)`

### `material_requests`

| # | Column | Type | Nullable | Default | Notes |
|---|--------|------|----------|---------|-------|
| 1 | `id` | `integer` | NOT NULL | auto-increment | 🔑 PK |
| 2 | `product_id` | `integer` | NOT NULL |  | FK → `products.id` |
| 3 | `location_id` | `integer` | NOT NULL |  | FK → `locations.id` |
| 4 | `qty_requested` | `numeric(10,2)` | NOT NULL |  |  |
| 5 | `uom` | `varchar(10)` | NOT NULL |  |  |
| 6 | `requested_by_id` | `integer` | NOT NULL |  | FK → `users.id` |
| 7 | `requested_at` | `timestamp with time zone` |  | NOW() |  |
| 8 | `approved_by_id` | `integer` |  |  | FK → `users.id` |
| 9 | `approved_at` | `timestamp with time zone` |  |  |  |
| 10 | `rejection_reason` | `varchar(500)` |  |  |  |
| 11 | `status` | `materialrequeststatus` | NOT NULL |  |  |
| 12 | `purpose` | `varchar(500)` | NOT NULL |  |  |
| 13 | `received_by_id` | `integer` |  |  | FK → `users.id` |
| 14 | `received_at` | `timestamp with time zone` |  |  |  |
| 15 | `created_at` | `timestamp with time zone` |  | NOW() |  |
| 16 | `updated_at` | `timestamp with time zone` |  |  |  |

**Foreign Keys:**
- `approved_by_id` → `users.id`
- `location_id` → `locations.id`
- `product_id` → `products.id`
- `received_by_id` → `users.id`
- `requested_by_id` → `users.id`

**Indexes:**
- `ix_material_requests_id` — `CREATE INDEX ix_material_requests_id ON public.material_requests USING btree (id)`
- `ix_material_requests_location_id` — `CREATE INDEX ix_material_requests_location_id ON public.material_requests USING btree (location_id)`
- `ix_material_requests_product_id` — `CREATE INDEX ix_material_requests_product_id ON public.material_requests USING btree (product_id)`
- `ix_material_requests_requested_by_id` — `CREATE INDEX ix_material_requests_requested_by_id ON public.material_requests USING btree (requested_by_id)`
- `ix_material_requests_status` — `CREATE INDEX ix_material_requests_status ON public.material_requests USING btree (status)`
- `material_requests_pkey` — `CREATE UNIQUE INDEX material_requests_pkey ON public.material_requests USING btree (id)`

### `mo_material_consumption`

| # | Column | Type | Nullable | Default | Notes |
|---|--------|------|----------|---------|-------|
| 1 | `id` | `integer` | NOT NULL | auto-increment | 🔑 PK |
| 2 | `work_order_id` | `integer` | NOT NULL |  | FK → `work_orders.id` |
| 3 | `product_id` | `integer` | NOT NULL |  | FK → `products.id` |
| 4 | `qty_planned` | `numeric(10,2)` | NOT NULL |  |  |
| 5 | `qty_actual` | `numeric(10,2)` |  |  |  |
| 6 | `lot_id` | `integer` |  |  | FK → `stock_lots.id` |
| 7 | `created_at` | `timestamp with time zone` |  | NOW() |  |

**Foreign Keys:**
- `lot_id` → `stock_lots.id`
- `product_id` → `products.id`
- `work_order_id` → `work_orders.id`

**Indexes:**
- `ix_mo_material_consumption_id` — `CREATE INDEX ix_mo_material_consumption_id ON public.mo_material_consumption USING btree (id)`
- `ix_mo_material_consumption_work_order_id` — `CREATE INDEX ix_mo_material_consumption_work_order_id ON public.mo_material_consumption USING btree (work_order_id)`
- `mo_material_consumption_pkey` — `CREATE UNIQUE INDEX mo_material_consumption_pkey ON public.mo_material_consumption USING btree (id)`

### `pallet_barcodes`

| # | Column | Type | Nullable | Default | Notes |
|---|--------|------|----------|---------|-------|
| 1 | `id` | `integer` | NOT NULL | auto-increment | 🔑 PK |
| 2 | `barcode` | `varchar(50)` | NOT NULL |  |  |
| 3 | `product_id` | `integer` | NOT NULL |  | FK → `products.id` |
| 4 | `work_order_id` | `integer` |  |  | FK → `work_orders.id` |
| 5 | `carton_count` | `integer` | NOT NULL |  |  |
| 6 | `total_pcs` | `integer` | NOT NULL |  |  |
| 7 | `status` | `palletstatus` | NOT NULL |  |  |
| 8 | `location_id` | `integer` |  |  | FK → `locations.id` |
| 9 | `created_at` | `timestamp with time zone` |  | NOW() |  |
| 10 | `received_at` | `timestamp with time zone` |  |  |  |
| 11 | `shipped_at` | `timestamp with time zone` |  |  |  |

**Foreign Keys:**
- `location_id` → `locations.id`
- `product_id` → `products.id`
- `work_order_id` → `work_orders.id`

**Indexes:**
- `ix_pallet_barcodes_barcode` — `CREATE UNIQUE INDEX ix_pallet_barcodes_barcode ON public.pallet_barcodes USING btree (barcode)`
- `ix_pallet_barcodes_id` — `CREATE INDEX ix_pallet_barcodes_id ON public.pallet_barcodes USING btree (id)`
- `ix_pallet_barcodes_product_id` — `CREATE INDEX ix_pallet_barcodes_product_id ON public.pallet_barcodes USING btree (product_id)`
- `ix_pallet_barcodes_status` — `CREATE INDEX ix_pallet_barcodes_status ON public.pallet_barcodes USING btree (status)`
- `pallet_barcodes_pkey` — `CREATE UNIQUE INDEX pallet_barcodes_pkey ON public.pallet_barcodes USING btree (id)`

### `partners`

| # | Column | Type | Nullable | Default | Notes |
|---|--------|------|----------|---------|-------|
| 1 | `id` | `integer` | NOT NULL | auto-increment | 🔑 PK |
| 2 | `name` | `varchar(255)` | NOT NULL |  |  |
| 3 | `type` | `partnertype` | NOT NULL |  |  |
| 4 | `address` | `text` |  |  |  |
| 5 | `contact_person` | `varchar(100)` |  |  |  |
| 6 | `phone` | `varchar(20)` |  |  |  |
| 7 | `email` | `varchar(100)` |  |  |  |
| 8 | `created_at` | `timestamp with time zone` |  | NOW() |  |

**Indexes:**
- `ix_partners_id` — `CREATE INDEX ix_partners_id ON public.partners USING btree (id)`
- `partners_pkey` — `CREATE UNIQUE INDEX partners_pkey ON public.partners USING btree (id)`

### `po_delete_requests`

| # | Column | Type | Nullable | Default | Notes |
|---|--------|------|----------|---------|-------|
| 1 | `id` | `integer` | NOT NULL | auto-increment | 🔑 PK |
| 2 | `po_id` | `integer` |  |  | FK → `purchase_orders.id` |
| 3 | `po_number` | `varchar(100)` | NOT NULL |  |  |
| 4 | `request_reason` | `text` | NOT NULL |  |  |
| 5 | `status` | `porequeststatus` | NOT NULL |  |  |
| 6 | `requested_by` | `integer` | NOT NULL |  | FK → `users.id` |
| 7 | `requested_at` | `timestamp with time zone` |  | NOW() |  |
| 8 | `responded_by` | `integer` |  |  | FK → `users.id` |
| 9 | `responded_at` | `timestamp with time zone` |  |  |  |
| 10 | `response_note` | `text` |  |  |  |

**Foreign Keys:**
- `po_id` → `purchase_orders.id`
- `requested_by` → `users.id`
- `responded_by` → `users.id`

**Indexes:**
- `ix_po_delete_requests_id` — `CREATE INDEX ix_po_delete_requests_id ON public.po_delete_requests USING btree (id)`
- `ix_po_delete_requests_po_id` — `CREATE INDEX ix_po_delete_requests_po_id ON public.po_delete_requests USING btree (po_id)`
- `ix_po_delete_requests_status` — `CREATE INDEX ix_po_delete_requests_status ON public.po_delete_requests USING btree (status)`
- `po_delete_requests_pkey` — `CREATE UNIQUE INDEX po_delete_requests_pkey ON public.po_delete_requests USING btree (id)`

### `products`

| # | Column | Type | Nullable | Default | Notes |
|---|--------|------|----------|---------|-------|
| 1 | `id` | `integer` | NOT NULL | auto-increment | 🔑 PK |
| 2 | `code` | `varchar(255)` | NOT NULL |  |  |
| 3 | `name` | `varchar(255)` | NOT NULL |  |  |
| 4 | `type` | `producttype` | NOT NULL |  |  |
| 5 | `uom` | `uom` | NOT NULL |  |  |
| 6 | `category_id` | `integer` | NOT NULL |  | FK → `categories.id` |
| 7 | `parent_article_id` | `integer` |  |  | FK → `products.id` |
| 8 | `min_stock` | `numeric(10,2)` |  |  |  |
| 9 | `created_at` | `timestamp with time zone` |  | NOW() |  |
| 10 | `is_active` | `boolean` |  |  |  |
| 11 | `product_type` | `varchar(20)` |  |  |  |
| 12 | `cartons_per_pallet` | `integer` |  |  |  |
| 13 | `pcs_per_carton` | `integer` |  |  |  |

**Foreign Keys:**
- `category_id` → `categories.id`
- `parent_article_id` → `products.id`

**Indexes:**
- `idx_products_type` — `CREATE INDEX idx_products_type ON public.products USING btree (type)`
- `ix_products_code` — `CREATE UNIQUE INDEX ix_products_code ON public.products USING btree (code)`
- `ix_products_id` — `CREATE INDEX ix_products_id ON public.products USING btree (id)`
- `ix_products_is_active` — `CREATE INDEX ix_products_is_active ON public.products USING btree (is_active)`
- `ix_products_type` — `CREATE INDEX ix_products_type ON public.products USING btree (type)`
- `products_pkey` — `CREATE UNIQUE INDEX products_pkey ON public.products USING btree (id)`

### `purchase_order_lines`

| # | Column | Type | Nullable | Default | Notes |
|---|--------|------|----------|---------|-------|
| 1 | `id` | `integer` | NOT NULL | auto-increment | 🔑 PK |
| 2 | `purchase_order_id` | `integer` | NOT NULL |  | FK → `purchase_orders.id` |
| 3 | `product_id` | `integer` | NOT NULL |  | FK → `products.id` |
| 4 | `supplier_id` | `integer` |  |  | FK → `partners.id` |
| 5 | `quantity` | `numeric(15,3)` | NOT NULL |  |  |
| 6 | `unit_price` | `numeric(18,2)` | NOT NULL |  |  |
| 7 | `subtotal` | `numeric(18,2)` | NOT NULL |  |  |
| 8 | `uom` | `varchar(20)` | NOT NULL |  |  |
| 9 | `extra_metadata` | `json` |  |  |  |
| 10 | `created_at` | `timestamp with time zone` |  | NOW() |  |
| 11 | `updated_at` | `timestamp with time zone` |  |  |  |

**Foreign Keys:**
- `product_id` → `products.id`
- `purchase_order_id` → `purchase_orders.id`
- `supplier_id` → `partners.id`

**Indexes:**
- `idx_po_line_po_id` — `CREATE INDEX idx_po_line_po_id ON public.purchase_order_lines USING btree (purchase_order_id)`
- `idx_po_line_product_id` — `CREATE INDEX idx_po_line_product_id ON public.purchase_order_lines USING btree (product_id)`
- `idx_po_line_supplier_id` — `CREATE INDEX idx_po_line_supplier_id ON public.purchase_order_lines USING btree (supplier_id)`
- `ix_purchase_order_lines_product_id` — `CREATE INDEX ix_purchase_order_lines_product_id ON public.purchase_order_lines USING btree (product_id)`
- `ix_purchase_order_lines_purchase_order_id` — `CREATE INDEX ix_purchase_order_lines_purchase_order_id ON public.purchase_order_lines USING btree (purchase_order_id)`
- `ix_purchase_order_lines_supplier_id` — `CREATE INDEX ix_purchase_order_lines_supplier_id ON public.purchase_order_lines USING btree (supplier_id)`
- `purchase_order_lines_pkey` — `CREATE UNIQUE INDEX purchase_order_lines_pkey ON public.purchase_order_lines USING btree (id)`

### `purchase_orders`

| # | Column | Type | Nullable | Default | Notes |
|---|--------|------|----------|---------|-------|
| 1 | `id` | `integer` | NOT NULL | auto-increment | 🔑 PK |
| 2 | `supplier_id` | `integer` | NOT NULL |  | FK → `partners.id` |
| 3 | `order_date` | `date` | NOT NULL |  |  |
| 4 | `expected_date` | `date` | NOT NULL |  |  |
| 5 | `status` | `postatus` | NOT NULL |  |  |
| 6 | `po_number` | `varchar(100)` | NOT NULL |  |  |
| 7 | `created_at` | `timestamp with time zone` |  | NOW() |  |
| 8 | `updated_at` | `timestamp with time zone` |  |  |  |
| 9 | `input_mode` | `varchar(20)` | NOT NULL | 'MANUAL'::character varying |  |
| 10 | `source_article_id` | `integer` |  |  | FK → `products.id` |
| 11 | `article_quantity` | `numeric(15,3)` |  |  |  |
| 12 | `po_type` | `varchar(20)` | NOT NULL | 'ACCESSORIES'::character varying |  |
| 13 | `linked_mo_id` | `integer` |  |  | FK → `manufacturing_orders.id` |
| 14 | `extra_metadata` | `json` |  |  |  |
| 15 | `total_amount` | `numeric(18,2)` |  | 0.00 |  |
| 16 | `currency` | `varchar(10)` |  | 'IDR'::character varying |  |
| 17 | `approved_by` | `integer` |  |  | FK → `users.id` |
| 18 | `approved_at` | `timestamp with time zone` |  |  |  |
| 19 | `source_po_kain_id` | `integer` |  |  | FK → `purchase_orders.id` |
| 20 | `article_id` | `integer` |  |  | FK → `products.id` |
| 21 | `article_qty` | `integer` |  |  |  |
| 22 | `week` | `varchar(20)` |  |  |  |
| 23 | `destination` | `varchar(100)` |  |  |  |
| 24 | `target_pallets` | `integer` |  |  |  |
| 25 | `expected_cartons` | `integer` |  |  |  |
| 26 | `calculated_pcs` | `integer` |  |  |  |

**Foreign Keys:**
- `approved_by` → `users.id`
- `article_id` → `products.id`
- `linked_mo_id` → `manufacturing_orders.id`
- `source_article_id` → `products.id`
- `source_po_kain_id` → `purchase_orders.id`
- `supplier_id` → `partners.id`

**Indexes:**
- `idx_po_article` — `CREATE INDEX idx_po_article ON public.purchase_orders USING btree (article_id)`
- `idx_po_input_mode` — `CREATE INDEX idx_po_input_mode ON public.purchase_orders USING btree (input_mode)`
- `idx_po_linked_mo` — `CREATE INDEX idx_po_linked_mo ON public.purchase_orders USING btree (linked_mo_id)`
- `idx_po_source_po_kain` — `CREATE INDEX idx_po_source_po_kain ON public.purchase_orders USING btree (source_po_kain_id)`
- `idx_po_type` — `CREATE INDEX idx_po_type ON public.purchase_orders USING btree (po_type)`
- `idx_po_type_status` — `CREATE INDEX idx_po_type_status ON public.purchase_orders USING btree (po_type, status)`
- `idx_po_week` — `CREATE INDEX idx_po_week ON public.purchase_orders USING btree (week)`
- `ix_purchase_orders_id` — `CREATE INDEX ix_purchase_orders_id ON public.purchase_orders USING btree (id)`
- `ix_purchase_orders_po_number` — `CREATE UNIQUE INDEX ix_purchase_orders_po_number ON public.purchase_orders USING btree (po_number)`
- `ix_purchase_orders_status` — `CREATE INDEX ix_purchase_orders_status ON public.purchase_orders USING btree (status)`
- `ix_purchase_orders_supplier_id` — `CREATE INDEX ix_purchase_orders_supplier_id ON public.purchase_orders USING btree (supplier_id)`
- `purchase_orders_pkey` — `CREATE UNIQUE INDEX purchase_orders_pkey ON public.purchase_orders USING btree (id)`

### `qc_checkpoints`

| # | Column | Type | Nullable | Default | Notes |
|---|--------|------|----------|---------|-------|
| 1 | `id` | `integer` | NOT NULL | auto-increment | 🔑 PK |
| 2 | `spk_id` | `integer` | NOT NULL |  | FK → `work_orders.id` |
| 3 | `checkpoint` | `qccheckpointtype` | NOT NULL |  |  |
| 4 | `inspected_qty` | `integer` | NOT NULL |  |  |
| 5 | `pass_qty` | `integer` | NOT NULL |  |  |
| 6 | `fail_qty` | `integer` | NOT NULL |  |  |
| 7 | `defect_type` | `varchar(255)` |  |  |  |
| 8 | `defect_description` | `text` |  |  |  |
| 9 | `inspector_name` | `varchar(255)` | NOT NULL |  |  |
| 10 | `inspected_by` | `integer` |  |  | FK → `users.id` |
| 11 | `inspection_date` | `varchar(20)` |  |  |  |
| 12 | `notes` | `text` |  |  |  |
| 13 | `first_pass_yield` | `numeric(5,2)` |  |  |  |
| 14 | `created_at` | `timestamp with time zone` |  | NOW() |  |

**Foreign Keys:**
- `inspected_by` → `users.id`
- `spk_id` → `work_orders.id`

**Indexes:**
- `ix_qc_checkpoints_checkpoint` — `CREATE INDEX ix_qc_checkpoints_checkpoint ON public.qc_checkpoints USING btree (checkpoint)`
- `ix_qc_checkpoints_created_at` — `CREATE INDEX ix_qc_checkpoints_created_at ON public.qc_checkpoints USING btree (created_at)`
- `ix_qc_checkpoints_id` — `CREATE INDEX ix_qc_checkpoints_id ON public.qc_checkpoints USING btree (id)`
- `ix_qc_checkpoints_spk_id` — `CREATE INDEX ix_qc_checkpoints_spk_id ON public.qc_checkpoints USING btree (spk_id)`
- `qc_checkpoints_pkey` — `CREATE UNIQUE INDEX qc_checkpoints_pkey ON public.qc_checkpoints USING btree (id)`

### `qc_inspections`

| # | Column | Type | Nullable | Default | Notes |
|---|--------|------|----------|---------|-------|
| 1 | `id` | `integer` | NOT NULL | auto-increment | 🔑 PK |
| 2 | `work_order_id` | `integer` | NOT NULL |  | FK → `work_orders.id` |
| 3 | `type` | `qcinspectiontype` | NOT NULL |  |  |
| 4 | `status` | `qcstatus` | NOT NULL |  |  |
| 5 | `defect_reason` | `text` |  |  |  |
| 6 | `defect_location` | `varchar(255)` |  |  |  |
| 7 | `defect_qty` | `integer` |  |  |  |
| 8 | `inspected_by` | `integer` | NOT NULL |  | FK → `users.id` |
| 9 | `inspected_at` | `timestamp with time zone` |  | NOW() |  |
| 10 | `created_at` | `timestamp with time zone` |  | NOW() |  |

**Foreign Keys:**
- `inspected_by` → `users.id`
- `work_order_id` → `work_orders.id`

**Indexes:**
- `ix_qc_inspections_id` — `CREATE INDEX ix_qc_inspections_id ON public.qc_inspections USING btree (id)`
- `ix_qc_inspections_inspected_at` — `CREATE INDEX ix_qc_inspections_inspected_at ON public.qc_inspections USING btree (inspected_at)`
- `ix_qc_inspections_status` — `CREATE INDEX ix_qc_inspections_status ON public.qc_inspections USING btree (status)`
- `ix_qc_inspections_type` — `CREATE INDEX ix_qc_inspections_type ON public.qc_inspections USING btree (type)`
- `ix_qc_inspections_work_order_id` — `CREATE INDEX ix_qc_inspections_work_order_id ON public.qc_inspections USING btree (work_order_id)`
- `qc_inspections_pkey` — `CREATE UNIQUE INDEX qc_inspections_pkey ON public.qc_inspections USING btree (id)`

### `qc_lab_tests`

| # | Column | Type | Nullable | Default | Notes |
|---|--------|------|----------|---------|-------|
| 1 | `id` | `integer` | NOT NULL | auto-increment | 🔑 PK |
| 2 | `batch_number` | `varchar(50)` | NOT NULL |  |  |
| 3 | `test_type` | `testtype` | NOT NULL |  |  |
| 4 | `test_result` | `testresult` | NOT NULL |  |  |
| 5 | `measured_value` | `numeric(10,2)` |  |  |  |
| 6 | `measured_unit` | `varchar(20)` |  |  |  |
| 7 | `iso_standard` | `varchar(50)` |  |  |  |
| 8 | `test_location` | `varchar(100)` |  |  |  |
| 9 | `inspector_id` | `integer` | NOT NULL |  | FK → `users.id` |
| 10 | `evidence_photo_url` | `varchar(500)` |  |  |  |
| 11 | `tested_at` | `timestamp with time zone` |  | NOW() |  |
| 12 | `created_at` | `timestamp with time zone` |  | NOW() |  |

**Foreign Keys:**
- `inspector_id` → `users.id`

**Indexes:**
- `ix_qc_lab_tests_batch_number` — `CREATE INDEX ix_qc_lab_tests_batch_number ON public.qc_lab_tests USING btree (batch_number)`
- `ix_qc_lab_tests_id` — `CREATE INDEX ix_qc_lab_tests_id ON public.qc_lab_tests USING btree (id)`
- `ix_qc_lab_tests_test_result` — `CREATE INDEX ix_qc_lab_tests_test_result ON public.qc_lab_tests USING btree (test_result)`
- `ix_qc_lab_tests_test_type` — `CREATE INDEX ix_qc_lab_tests_test_type ON public.qc_lab_tests USING btree (test_type)`
- `ix_qc_lab_tests_tested_at` — `CREATE INDEX ix_qc_lab_tests_tested_at ON public.qc_lab_tests USING btree (tested_at)`
- `qc_lab_tests_pkey` — `CREATE UNIQUE INDEX qc_lab_tests_pkey ON public.qc_lab_tests USING btree (id)`

### `rework_materials`

| # | Column | Type | Nullable | Default | Notes |
|---|--------|------|----------|---------|-------|
| 1 | `id` | `integer` | NOT NULL | auto-increment | 🔑 PK |
| 2 | `rework_request_id` | `integer` | NOT NULL |  | FK → `rework_requests.id` |
| 3 | `product_id` | `integer` | NOT NULL |  | FK → `products.id` |
| 4 | `qty_used` | `numeric(10,2)` | NOT NULL |  |  |
| 5 | `uom` | `varchar(10)` | NOT NULL |  |  |
| 6 | `unit_cost` | `numeric(12,2)` | NOT NULL |  |  |
| 7 | `total_cost` | `numeric(12,2)` | NOT NULL |  |  |
| 8 | `created_at` | `timestamp with time zone` |  | NOW() |  |

**Foreign Keys:**
- `product_id` → `products.id`
- `rework_request_id` → `rework_requests.id`

**Indexes:**
- `ix_rework_materials_id` — `CREATE INDEX ix_rework_materials_id ON public.rework_materials USING btree (id)`
- `ix_rework_materials_rework_request_id` — `CREATE INDEX ix_rework_materials_rework_request_id ON public.rework_materials USING btree (rework_request_id)`
- `rework_materials_pkey` — `CREATE UNIQUE INDEX rework_materials_pkey ON public.rework_materials USING btree (id)`

### `rework_requests`

| # | Column | Type | Nullable | Default | Notes |
|---|--------|------|----------|---------|-------|
| 1 | `id` | `integer` | NOT NULL | auto-increment | 🔑 PK |
| 2 | `spk_id` | `integer` | NOT NULL |  | FK → `spks.id` |
| 3 | `defect_qty` | `numeric(10,2)` | NOT NULL |  |  |
| 4 | `defect_category_id` | `integer` | NOT NULL |  | FK → `defect_categories.id` |
| 5 | `defect_notes` | `varchar(500)` |  |  |  |
| 6 | `status` | `reworkstatus` | NOT NULL |  |  |
| 7 | `qc_reviewed_by_id` | `integer` |  |  | FK → `users.id` |
| 8 | `qc_reviewed_at` | `timestamp with time zone` |  |  |  |
| 9 | `qc_approval_notes` | `varchar(500)` |  |  |  |
| 10 | `rework_started_at` | `timestamp with time zone` |  |  |  |
| 11 | `rework_completed_at` | `timestamp with time zone` |  |  |  |
| 12 | `rework_operator_id` | `integer` |  |  | FK → `users.id` |
| 13 | `rework_notes` | `varchar(500)` |  |  |  |
| 14 | `verified_by_id` | `integer` |  |  | FK → `users.id` |
| 15 | `verified_at` | `timestamp with time zone` |  |  |  |
| 16 | `verified_good_qty` | `numeric(10,2)` |  |  |  |
| 17 | `verified_failed_qty` | `numeric(10,2)` |  |  |  |
| 18 | `material_cost` | `numeric(12,2)` |  |  |  |
| 19 | `labor_cost` | `numeric(12,2)` |  |  |  |
| 20 | `total_cost` | `numeric(12,2)` |  |  |  |
| 21 | `created_at` | `timestamp with time zone` |  | NOW() |  |
| 22 | `requested_by_id` | `integer` | NOT NULL |  | FK → `users.id` |
| 23 | `updated_at` | `timestamp with time zone` |  | NOW() |  |

**Foreign Keys:**
- `defect_category_id` → `defect_categories.id`
- `qc_reviewed_by_id` → `users.id`
- `requested_by_id` → `users.id`
- `rework_operator_id` → `users.id`
- `spk_id` → `spks.id`
- `verified_by_id` → `users.id`

**Indexes:**
- `ix_rework_requests_id` — `CREATE INDEX ix_rework_requests_id ON public.rework_requests USING btree (id)`
- `ix_rework_requests_spk_id` — `CREATE INDEX ix_rework_requests_spk_id ON public.rework_requests USING btree (spk_id)`
- `ix_rework_requests_status` — `CREATE INDEX ix_rework_requests_status ON public.rework_requests USING btree (status)`
- `rework_requests_pkey` — `CREATE UNIQUE INDEX rework_requests_pkey ON public.rework_requests USING btree (id)`

### `sales_order_lines`

| # | Column | Type | Nullable | Default | Notes |
|---|--------|------|----------|---------|-------|
| 1 | `id` | `integer` | NOT NULL | auto-increment | 🔑 PK |
| 2 | `sales_order_id` | `integer` | NOT NULL |  | FK → `sales_orders.id` |
| 3 | `product_id` | `integer` | NOT NULL |  | FK → `products.id` |
| 4 | `qty_ordered` | `numeric(10,2)` | NOT NULL |  |  |
| 5 | `qty_produced` | `numeric(10,2)` |  |  |  |
| 6 | `created_at` | `timestamp with time zone` |  | NOW() |  |
| 7 | `updated_at` | `timestamp with time zone` |  |  |  |

**Foreign Keys:**
- `product_id` → `products.id`
- `sales_order_id` → `sales_orders.id`

**Indexes:**
- `ix_sales_order_lines_id` — `CREATE INDEX ix_sales_order_lines_id ON public.sales_order_lines USING btree (id)`
- `ix_sales_order_lines_product_id` — `CREATE INDEX ix_sales_order_lines_product_id ON public.sales_order_lines USING btree (product_id)`
- `ix_sales_order_lines_sales_order_id` — `CREATE INDEX ix_sales_order_lines_sales_order_id ON public.sales_order_lines USING btree (sales_order_id)`
- `sales_order_lines_pkey` — `CREATE UNIQUE INDEX sales_order_lines_pkey ON public.sales_order_lines USING btree (id)`

### `sales_orders`

| # | Column | Type | Nullable | Default | Notes |
|---|--------|------|----------|---------|-------|
| 1 | `id` | `integer` | NOT NULL | auto-increment | 🔑 PK |
| 2 | `po_number_buyer` | `varchar(100)` | NOT NULL |  |  |
| 3 | `buyer_id` | `integer` |  |  | FK → `partners.id` |
| 4 | `order_date` | `date` | NOT NULL |  |  |
| 5 | `delivery_week` | `integer` | NOT NULL |  |  |
| 6 | `destination` | `varchar(50)` | NOT NULL |  |  |
| 7 | `status` | `sostatus` | NOT NULL |  |  |
| 8 | `created_at` | `timestamp with time zone` |  | NOW() |  |
| 9 | `updated_at` | `timestamp with time zone` |  |  |  |

**Foreign Keys:**
- `buyer_id` → `partners.id`

**Indexes:**
- `ix_sales_orders_destination` — `CREATE INDEX ix_sales_orders_destination ON public.sales_orders USING btree (destination)`
- `ix_sales_orders_id` — `CREATE INDEX ix_sales_orders_id ON public.sales_orders USING btree (id)`
- `ix_sales_orders_order_date` — `CREATE INDEX ix_sales_orders_order_date ON public.sales_orders USING btree (order_date)`
- `ix_sales_orders_po_number_buyer` — `CREATE UNIQUE INDEX ix_sales_orders_po_number_buyer ON public.sales_orders USING btree (po_number_buyer)`
- `ix_sales_orders_status` — `CREATE INDEX ix_sales_orders_status ON public.sales_orders USING btree (status)`
- `sales_orders_pkey` — `CREATE UNIQUE INDEX sales_orders_pkey ON public.sales_orders USING btree (id)`

### `security_logs`

| # | Column | Type | Nullable | Default | Notes |
|---|--------|------|----------|---------|-------|
| 1 | `id` | `bigint` | NOT NULL | auto-increment | 🔑 PK |
| 2 | `timestamp` | `timestamp without time zone` | NOT NULL |  |  |
| 3 | `ip_address` | `varchar(45)` | NOT NULL |  |  |
| 4 | `event_type` | `varchar(50)` | NOT NULL |  |  |
| 5 | `severity` | `varchar(20)` | NOT NULL |  |  |
| 6 | `user_id` | `bigint` |  |  | FK → `users.id` |
| 7 | `username_attempted` | `varchar(100)` |  |  |  |
| 8 | `description` | `text` | NOT NULL |  |  |
| 9 | `user_agent` | `varchar(500)` |  |  |  |
| 10 | `action_taken` | `varchar(100)` |  |  |  |

**Foreign Keys:**
- `user_id` → `users.id`

**Indexes:**
- `idx_security_time_severity` — `CREATE INDEX idx_security_time_severity ON public.security_logs USING btree ("timestamp", severity)`
- `ix_security_logs_event_type` — `CREATE INDEX ix_security_logs_event_type ON public.security_logs USING btree (event_type)`
- `ix_security_logs_ip_address` — `CREATE INDEX ix_security_logs_ip_address ON public.security_logs USING btree (ip_address)`
- `ix_security_logs_severity` — `CREATE INDEX ix_security_logs_severity ON public.security_logs USING btree (severity)`
- `ix_security_logs_timestamp` — `CREATE INDEX ix_security_logs_timestamp ON public.security_logs USING btree ("timestamp")`
- `ix_security_logs_user_id` — `CREATE INDEX ix_security_logs_user_id ON public.security_logs USING btree (user_id)`
- `security_logs_pkey` — `CREATE UNIQUE INDEX security_logs_pkey ON public.security_logs USING btree (id)`

### `segregasi_acknowledgement`

| # | Column | Type | Nullable | Default | Notes |
|---|--------|------|----------|---------|-------|
| 1 | `id` | `integer` | NOT NULL | auto-increment | 🔑 PK |
| 2 | `transfer_log_id` | `integer` | NOT NULL |  | FK → `transfer_logs.id` |
| 3 | `acknowledged_at` | `timestamp with time zone` |  | NOW() |  |
| 4 | `acknowledged_by` | `integer` | NOT NULL |  | FK → `users.id` |
| 5 | `clearance_method` | `clearancemethod` | NOT NULL |  |  |
| 6 | `proof_photo_url` | `varchar(500)` |  |  |  |
| 7 | `clearance_notes` | `text` |  |  |  |
| 8 | `created_at` | `timestamp with time zone` |  | NOW() |  |

**Foreign Keys:**
- `acknowledged_by` → `users.id`
- `transfer_log_id` → `transfer_logs.id`

**Indexes:**
- `ix_segregasi_acknowledgement_acknowledged_at` — `CREATE INDEX ix_segregasi_acknowledgement_acknowledged_at ON public.segregasi_acknowledgement USING btree (acknowledged_at)`
- `ix_segregasi_acknowledgement_id` — `CREATE INDEX ix_segregasi_acknowledgement_id ON public.segregasi_acknowledgement USING btree (id)`
- `ix_segregasi_acknowledgement_transfer_log_id` — `CREATE INDEX ix_segregasi_acknowledgement_transfer_log_id ON public.segregasi_acknowledgement USING btree (transfer_log_id)`
- `segregasi_acknowledgement_pkey` — `CREATE UNIQUE INDEX segregasi_acknowledgement_pkey ON public.segregasi_acknowledgement USING btree (id)`

### `spk_daily_production`

| # | Column | Type | Nullable | Default | Notes |
|---|--------|------|----------|---------|-------|
| 1 | `id` | `integer` | NOT NULL | auto-increment | 🔑 PK |
| 2 | `spk_id` | `integer` | NOT NULL |  | FK → `spks.id` · UNIQUE |
| 3 | `production_date` | `date` | NOT NULL |  | UNIQUE |
| 4 | `input_qty` | `integer` | NOT NULL |  |  |
| 5 | `cumulative_qty` | `integer` |  |  |  |
| 6 | `input_by_id` | `integer` | NOT NULL |  | FK → `users.id` |
| 7 | `status` | `varchar(50)` |  |  |  |
| 8 | `notes` | `varchar(500)` |  |  |  |
| 9 | `created_at` | `timestamp without time zone` |  |  |  |
| 10 | `updated_at` | `timestamp without time zone` |  |  |  |

**Foreign Keys:**
- `input_by_id` → `users.id`
- `spk_id` → `spks.id`

**Indexes:**
- `ix_spk_daily_production_id` — `CREATE INDEX ix_spk_daily_production_id ON public.spk_daily_production USING btree (id)`
- `ix_spk_daily_production_production_date` — `CREATE INDEX ix_spk_daily_production_production_date ON public.spk_daily_production USING btree (production_date)`
- `ix_spk_daily_production_spk_id` — `CREATE INDEX ix_spk_daily_production_spk_id ON public.spk_daily_production USING btree (spk_id)`
- `spk_daily_production_pkey` — `CREATE UNIQUE INDEX spk_daily_production_pkey ON public.spk_daily_production USING btree (id)`
- `uk_spk_date` — `CREATE UNIQUE INDEX uk_spk_date ON public.spk_daily_production USING btree (spk_id, production_date)`

### `spk_edit_history`

| # | Column | Type | Nullable | Default | Notes |
|---|--------|------|----------|---------|-------|
| 1 | `id` | `integer` | NOT NULL | auto-increment | 🔑 PK |
| 2 | `spk_id` | `integer` | NOT NULL |  | FK → `spks.id` |
| 3 | `edit_type` | `spkedittype` | NOT NULL |  |  |
| 4 | `status` | `spkeditstatus` |  |  |  |
| 5 | `old_values` | `json` | NOT NULL |  |  |
| 6 | `new_values` | `json` | NOT NULL |  |  |
| 7 | `requested_by_id` | `integer` | NOT NULL |  | FK → `users.id` |
| 8 | `request_reason` | `text` |  |  |  |
| 9 | `requested_at` | `timestamp without time zone` |  | NOW() |  |
| 10 | `approval_request_id` | `integer` |  |  |  |
| 11 | `approved_by_id` | `integer` |  |  | FK → `users.id` |
| 12 | `approved_at` | `timestamp without time zone` |  |  |  |
| 13 | `approval_notes` | `text` |  |  |  |
| 14 | `rejected_by_id` | `integer` |  |  | FK → `users.id` |
| 15 | `rejected_at` | `timestamp without time zone` |  |  |  |
| 16 | `rejection_reason` | `text` |  |  |  |
| 17 | `applied_at` | `timestamp without time zone` |  |  |  |
| 18 | `applied_by_id` | `integer` |  |  | FK → `users.id` |
| 19 | `cancelled_at` | `timestamp without time zone` |  |  |  |
| 20 | `cancelled_by_id` | `integer` |  |  | FK → `users.id` |
| 21 | `cancellation_reason` | `text` |  |  |  |
| 22 | `material_reallocation_details` | `json` |  |  |  |
| 23 | `created_at` | `timestamp without time zone` |  | NOW() |  |
| 24 | `updated_at` | `timestamp without time zone` |  | NOW() |  |

**Foreign Keys:**
- `applied_by_id` → `users.id`
- `approved_by_id` → `users.id`
- `cancelled_by_id` → `users.id`
- `rejected_by_id` → `users.id`
- `requested_by_id` → `users.id`
- `spk_id` → `spks.id`

**Indexes:**
- `ix_spk_edit_history_id` — `CREATE INDEX ix_spk_edit_history_id ON public.spk_edit_history USING btree (id)`
- `ix_spk_edit_history_spk_id` — `CREATE INDEX ix_spk_edit_history_spk_id ON public.spk_edit_history USING btree (spk_id)`
- `spk_edit_history_pkey` — `CREATE UNIQUE INDEX spk_edit_history_pkey ON public.spk_edit_history USING btree (id)`

### `spk_material_allocation`

| # | Column | Type | Nullable | Default | Notes |
|---|--------|------|----------|---------|-------|
| 1 | `id` | `integer` | NOT NULL | auto-increment | 🔑 PK |
| 2 | `spk_id` | `integer` | NOT NULL |  | FK → `spks.id` |
| 3 | `material_id` | `integer` | NOT NULL |  | FK → `products.id` |
| 4 | `qty_allocated` | `numeric(10,2)` | NOT NULL |  |  |
| 5 | `qty_from_stock` | `numeric(10,2)` | NOT NULL |  |  |
| 6 | `qty_from_debt` | `numeric(10,2)` | NOT NULL |  |  |
| 7 | `wastage_qty` | `numeric(10,2)` | NOT NULL |  |  |
| 8 | `wastage_percentage` | `numeric(5,2)` | NOT NULL |  |  |
| 9 | `allocation_status` | `spkmaterialallocationstatus` |  |  |  |
| 10 | `material_shortage` | `boolean` |  |  |  |
| 11 | `shortage_qty` | `numeric(10,2)` |  |  |  |
| 12 | `created_by` | `integer` |  |  | FK → `users.id` |
| 13 | `created_at` | `timestamp without time zone` |  | NOW() |  |
| 14 | `updated_at` | `timestamp without time zone` |  | NOW() |  |

**Foreign Keys:**
- `created_by` → `users.id`
- `material_id` → `products.id`
- `spk_id` → `spks.id`

**Indexes:**
- `ix_spk_material_allocation_id` — `CREATE INDEX ix_spk_material_allocation_id ON public.spk_material_allocation USING btree (id)`
- `ix_spk_material_allocation_material_id` — `CREATE INDEX ix_spk_material_allocation_material_id ON public.spk_material_allocation USING btree (material_id)`
- `ix_spk_material_allocation_spk_id` — `CREATE INDEX ix_spk_material_allocation_spk_id ON public.spk_material_allocation USING btree (spk_id)`
- `spk_material_allocation_pkey` — `CREATE UNIQUE INDEX spk_material_allocation_pkey ON public.spk_material_allocation USING btree (id)`

### `spk_material_allocation_old`

| # | Column | Type | Nullable | Default | Notes |
|---|--------|------|----------|---------|-------|
| 1 | `id` | `integer` | NOT NULL | auto-increment | 🔑 PK |
| 2 | `spk_id` | `integer` | NOT NULL |  | FK → `spks.id` |
| 3 | `material_id` | `integer` | NOT NULL |  | FK → `products.id` |
| 4 | `qty_allocated` | `numeric(10,2)` | NOT NULL |  |  |
| 5 | `qty_from_stock` | `numeric(10,2)` | NOT NULL |  |  |
| 6 | `qty_from_debt` | `numeric(10,2)` | NOT NULL |  |  |
| 7 | `wastage_qty` | `numeric(10,2)` | NOT NULL |  |  |
| 8 | `wastage_percentage` | `numeric(5,2)` | NOT NULL |  |  |
| 9 | `allocation_status` | `spkmaterialallocationstatus` |  |  |  |
| 10 | `material_shortage` | `boolean` |  |  |  |
| 11 | `shortage_qty` | `numeric(10,2)` |  |  |  |
| 12 | `created_by` | `integer` |  |  | FK → `users.id` |
| 13 | `created_at` | `timestamp without time zone` |  | NOW() |  |
| 14 | `updated_at` | `timestamp without time zone` |  | NOW() |  |

**Foreign Keys:**
- `created_by` → `users.id`
- `material_id` → `products.id`
- `spk_id` → `spks.id`

**Indexes:**
- `ix_spk_material_allocation_old_id` — `CREATE INDEX ix_spk_material_allocation_old_id ON public.spk_material_allocation_old USING btree (id)`
- `ix_spk_material_allocation_old_material_id` — `CREATE INDEX ix_spk_material_allocation_old_material_id ON public.spk_material_allocation_old USING btree (material_id)`
- `ix_spk_material_allocation_old_spk_id` — `CREATE INDEX ix_spk_material_allocation_old_spk_id ON public.spk_material_allocation_old USING btree (spk_id)`
- `spk_material_allocation_old_pkey` — `CREATE UNIQUE INDEX spk_material_allocation_old_pkey ON public.spk_material_allocation_old USING btree (id)`

### `spk_material_allocations`

| # | Column | Type | Nullable | Default | Notes |
|---|--------|------|----------|---------|-------|
| 1 | `id` | `integer` | NOT NULL | auto-increment | 🔑 PK |
| 2 | `wo_id` | `integer` | NOT NULL |  | FK → `work_orders.id` |
| 3 | `material_id` | `integer` | NOT NULL |  | FK → `products.id` |
| 4 | `qty_allocated` | `numeric(12,3)` | NOT NULL |  |  |
| 5 | `qty_consumed` | `numeric(12,3)` | NOT NULL |  |  |
| 6 | `uom` | `varchar(20)` |  |  |  |
| 7 | `is_reserved` | `boolean` | NOT NULL |  |  |
| 8 | `is_consumed` | `boolean` | NOT NULL |  |  |
| 9 | `allocated_at` | `timestamp without time zone` |  |  |  |
| 10 | `consumed_at` | `timestamp without time zone` |  |  |  |
| 11 | `created_at` | `timestamp with time zone` |  | NOW() |  |
| 12 | `updated_at` | `timestamp with time zone` |  |  |  |

**Foreign Keys:**
- `material_id` → `products.id`
- `wo_id` → `work_orders.id`

**Indexes:**
- `ix_spk_material_allocations_id` — `CREATE INDEX ix_spk_material_allocations_id ON public.spk_material_allocations USING btree (id)`
- `ix_spk_material_allocations_material_id` — `CREATE INDEX ix_spk_material_allocations_material_id ON public.spk_material_allocations USING btree (material_id)`
- `ix_spk_material_allocations_wo_id` — `CREATE INDEX ix_spk_material_allocations_wo_id ON public.spk_material_allocations USING btree (wo_id)`
- `spk_material_allocations_pkey` — `CREATE UNIQUE INDEX spk_material_allocations_pkey ON public.spk_material_allocations USING btree (id)`

### `spk_modifications`

| # | Column | Type | Nullable | Default | Notes |
|---|--------|------|----------|---------|-------|
| 1 | `id` | `integer` | NOT NULL | auto-increment | 🔑 PK |
| 2 | `spk_id` | `integer` | NOT NULL |  | FK → `spks.id` |
| 3 | `field_name` | `varchar(50)` | NOT NULL |  |  |
| 4 | `old_value` | `varchar(255)` |  |  |  |
| 5 | `new_value` | `varchar(255)` |  |  |  |
| 6 | `modified_by_id` | `integer` | NOT NULL |  | FK → `users.id` |
| 7 | `modification_reason` | `varchar(255)` |  |  |  |
| 8 | `created_at` | `timestamp without time zone` |  |  |  |

**Foreign Keys:**
- `modified_by_id` → `users.id`
- `spk_id` → `spks.id`

**Indexes:**
- `ix_spk_modifications_created_at` — `CREATE INDEX ix_spk_modifications_created_at ON public.spk_modifications USING btree (created_at)`
- `ix_spk_modifications_id` — `CREATE INDEX ix_spk_modifications_id ON public.spk_modifications USING btree (id)`
- `ix_spk_modifications_spk_id` — `CREATE INDEX ix_spk_modifications_spk_id ON public.spk_modifications USING btree (spk_id)`
- `spk_modifications_pkey` — `CREATE UNIQUE INDEX spk_modifications_pkey ON public.spk_modifications USING btree (id)`

### `spk_production_completion`

| # | Column | Type | Nullable | Default | Notes |
|---|--------|------|----------|---------|-------|
| 1 | `id` | `integer` | NOT NULL | auto-increment | 🔑 PK |
| 2 | `spk_id` | `integer` | NOT NULL |  | FK → `spks.id` |
| 3 | `target_qty` | `integer` | NOT NULL |  |  |
| 4 | `actual_qty` | `integer` | NOT NULL |  |  |
| 5 | `completed_date` | `date` | NOT NULL |  |  |
| 6 | `confirmed_by_id` | `integer` | NOT NULL |  | FK → `users.id` |
| 7 | `confirmation_notes` | `varchar(255)` |  |  |  |
| 8 | `confirmed_at` | `timestamp without time zone` | NOT NULL |  |  |
| 9 | `is_completed` | `boolean` |  |  |  |

**Foreign Keys:**
- `confirmed_by_id` → `users.id`
- `spk_id` → `spks.id`

**Indexes:**
- `ix_spk_production_completion_completed_date` — `CREATE INDEX ix_spk_production_completion_completed_date ON public.spk_production_completion USING btree (completed_date)`
- `ix_spk_production_completion_id` — `CREATE INDEX ix_spk_production_completion_id ON public.spk_production_completion USING btree (id)`
- `ix_spk_production_completion_spk_id` — `CREATE INDEX ix_spk_production_completion_spk_id ON public.spk_production_completion USING btree (spk_id)`
- `spk_production_completion_pkey` — `CREATE UNIQUE INDEX spk_production_completion_pkey ON public.spk_production_completion USING btree (id)`

### `spks`

| # | Column | Type | Nullable | Default | Notes |
|---|--------|------|----------|---------|-------|
| 1 | `id` | `integer` | NOT NULL | auto-increment | 🔑 PK |
| 2 | `mo_id` | `integer` | NOT NULL |  | FK → `manufacturing_orders.id` |
| 3 | `department` | `department` | NOT NULL |  |  |
| 4 | `original_qty` | `integer` | NOT NULL |  |  |
| 5 | `modified_qty` | `integer` |  |  |  |
| 6 | `target_qty` | `integer` | NOT NULL |  |  |
| 7 | `produced_qty` | `integer` |  |  |  |
| 8 | `modification_reason` | `varchar(255)` |  |  |  |
| 9 | `modified_by_id` | `integer` |  |  | FK → `users.id` |
| 10 | `modified_at` | `timestamp without time zone` |  |  |  |
| 11 | `production_status` | `varchar(50)` |  |  |  |
| 12 | `start_date` | `date` |  |  |  |
| 13 | `target_completion_date` | `date` |  |  |  |
| 14 | `completion_date` | `date` |  |  |  |
| 15 | `allow_negative_inventory` | `boolean` |  |  |  |
| 16 | `negative_approval_status` | `varchar(50)` |  |  |  |
| 17 | `negative_approved_by_id` | `integer` |  |  | FK → `users.id` |
| 18 | `negative_approved_at` | `timestamp without time zone` |  |  |  |
| 19 | `created_by_id` | `integer` | NOT NULL |  | FK → `users.id` |
| 20 | `created_at` | `timestamp without time zone` |  |  |  |
| 21 | `updated_at` | `timestamp without time zone` |  |  |  |
| 22 | `planned_start_date` | `date` |  |  |  |
| 23 | `actual_start_date` | `date` |  |  |  |
| 24 | `production_date_stamp` | `date` |  |  |  |
| 25 | `buffer_percentage` | `numeric(5,2)` | NOT NULL | 0 |  |
| 26 | `good_qty` | `integer` | NOT NULL | 0 |  |
| 27 | `defect_qty` | `integer` | NOT NULL | 0 |  |
| 28 | `rework_qty` | `integer` | NOT NULL | 0 |  |

**Foreign Keys:**
- `created_by_id` → `users.id`
- `mo_id` → `manufacturing_orders.id`
- `modified_by_id` → `users.id`
- `negative_approved_by_id` → `users.id`

**Indexes:**
- `ix_spks_department` — `CREATE INDEX ix_spks_department ON public.spks USING btree (department)`
- `ix_spks_id` — `CREATE INDEX ix_spks_id ON public.spks USING btree (id)`
- `ix_spks_mo_id` — `CREATE INDEX ix_spks_mo_id ON public.spks USING btree (mo_id)`
- `ix_spks_production_status` — `CREATE INDEX ix_spks_production_status ON public.spks USING btree (production_status)`
- `spks_pkey` — `CREATE UNIQUE INDEX spks_pkey ON public.spks USING btree (id)`

### `stock_lots`

| # | Column | Type | Nullable | Default | Notes |
|---|--------|------|----------|---------|-------|
| 1 | `id` | `integer` | NOT NULL | auto-increment | 🔑 PK |
| 2 | `product_id` | `integer` | NOT NULL |  | FK → `products.id` |
| 3 | `lot_number` | `varchar(50)` | NOT NULL |  |  |
| 4 | `qty_initial` | `numeric(10,2)` | NOT NULL |  |  |
| 5 | `qty_remaining` | `numeric(10,2)` | NOT NULL |  |  |
| 6 | `supplier_id` | `integer` |  |  | FK → `partners.id` |
| 7 | `purchase_order_id` | `integer` |  |  | FK → `purchase_orders.id` |
| 8 | `received_date` | `timestamp with time zone` | NOT NULL |  |  |
| 9 | `expiry_date` | `timestamp with time zone` |  |  |  |
| 10 | `created_at` | `timestamp with time zone` |  | NOW() |  |

**Foreign Keys:**
- `product_id` → `products.id`
- `purchase_order_id` → `purchase_orders.id`
- `supplier_id` → `partners.id`

**Indexes:**
- `ix_stock_lots_id` — `CREATE INDEX ix_stock_lots_id ON public.stock_lots USING btree (id)`
- `ix_stock_lots_lot_number` — `CREATE UNIQUE INDEX ix_stock_lots_lot_number ON public.stock_lots USING btree (lot_number)`
- `stock_lots_pkey` — `CREATE UNIQUE INDEX stock_lots_pkey ON public.stock_lots USING btree (id)`

### `stock_moves`

| # | Column | Type | Nullable | Default | Notes |
|---|--------|------|----------|---------|-------|
| 1 | `id` | `integer` | NOT NULL | auto-increment | 🔑 PK |
| 2 | `product_id` | `integer` | NOT NULL |  | FK → `products.id` |
| 3 | `qty` | `numeric(10,2)` | NOT NULL |  |  |
| 4 | `uom` | `varchar(10)` | NOT NULL |  |  |
| 5 | `location_id_from` | `integer` | NOT NULL |  | FK → `locations.id` |
| 6 | `location_id_to` | `integer` | NOT NULL |  | FK → `locations.id` |
| 7 | `reference_doc` | `varchar(100)` | NOT NULL |  |  |
| 8 | `state` | `stockmovestatus` |  |  |  |
| 9 | `lot_id` | `integer` |  |  | FK → `stock_lots.id` |
| 10 | `date` | `timestamp with time zone` |  | NOW() |  |
| 11 | `created_at` | `timestamp with time zone` |  | NOW() |  |

**Foreign Keys:**
- `location_id_from` → `locations.id`
- `location_id_to` → `locations.id`
- `lot_id` → `stock_lots.id`
- `product_id` → `products.id`

**Indexes:**
- `ix_stock_moves_date` — `CREATE INDEX ix_stock_moves_date ON public.stock_moves USING btree (date)`
- `ix_stock_moves_id` — `CREATE INDEX ix_stock_moves_id ON public.stock_moves USING btree (id)`
- `ix_stock_moves_product_id` — `CREATE INDEX ix_stock_moves_product_id ON public.stock_moves USING btree (product_id)`
- `ix_stock_moves_state` — `CREATE INDEX ix_stock_moves_state ON public.stock_moves USING btree (state)`
- `stock_moves_pkey` — `CREATE UNIQUE INDEX stock_moves_pkey ON public.stock_moves USING btree (id)`

### `stock_quants`

| # | Column | Type | Nullable | Default | Notes |
|---|--------|------|----------|---------|-------|
| 1 | `id` | `integer` | NOT NULL | auto-increment | 🔑 PK |
| 2 | `product_id` | `integer` | NOT NULL |  | FK → `products.id` |
| 3 | `location_id` | `integer` | NOT NULL |  | FK → `locations.id` |
| 4 | `lot_id` | `integer` |  |  | FK → `stock_lots.id` |
| 5 | `qty_on_hand` | `numeric(10,2)` |  |  |  |
| 6 | `qty_reserved` | `numeric(10,2)` |  |  |  |
| 7 | `updated_at` | `timestamp with time zone` |  | NOW() |  |

**Foreign Keys:**
- `location_id` → `locations.id`
- `lot_id` → `stock_lots.id`
- `product_id` → `products.id`

**Indexes:**
- `ix_stock_quants_id` — `CREATE INDEX ix_stock_quants_id ON public.stock_quants USING btree (id)`
- `ix_stock_quants_location_id` — `CREATE INDEX ix_stock_quants_location_id ON public.stock_quants USING btree (location_id)`
- `ix_stock_quants_product_id` — `CREATE INDEX ix_stock_quants_product_id ON public.stock_quants USING btree (product_id)`
- `stock_quants_pkey` — `CREATE UNIQUE INDEX stock_quants_pkey ON public.stock_quants USING btree (id)`

### `transfer_logs`

| # | Column | Type | Nullable | Default | Notes |
|---|--------|------|----------|---------|-------|
| 1 | `id` | `integer` | NOT NULL | auto-increment | 🔑 PK |
| 2 | `mo_id` | `integer` | NOT NULL |  | FK → `manufacturing_orders.id` |
| 3 | `from_dept` | `transferdept` | NOT NULL |  |  |
| 4 | `to_dept` | `transferdept` | NOT NULL |  |  |
| 5 | `article_code` | `varchar(50)` | NOT NULL |  |  |
| 6 | `batch_id` | `varchar(50)` | NOT NULL |  |  |
| 7 | `week_number` | `integer` |  |  |  |
| 8 | `destination` | `varchar(50)` |  |  |  |
| 9 | `qty_sent` | `numeric(10,2)` | NOT NULL |  |  |
| 10 | `qty_received` | `numeric(10,2)` |  |  |  |
| 11 | `is_line_clear` | `boolean` |  |  |  |
| 12 | `line_checked_at` | `timestamp with time zone` |  |  |  |
| 13 | `line_checked_by` | `integer` |  |  | FK → `users.id` |
| 14 | `status` | `transferstatus` |  |  |  |
| 15 | `timestamp_start` | `timestamp with time zone` |  | NOW() |  |
| 16 | `timestamp_accept` | `timestamp with time zone` |  |  |  |
| 17 | `timestamp_end` | `timestamp with time zone` |  |  |  |
| 18 | `accepted_by` | `integer` |  |  | FK → `users.id` |
| 19 | `created_at` | `timestamp with time zone` |  | NOW() |  |

**Foreign Keys:**
- `accepted_by` → `users.id`
- `line_checked_by` → `users.id`
- `mo_id` → `manufacturing_orders.id`

**Indexes:**
- `ix_transfer_logs_article_code` — `CREATE INDEX ix_transfer_logs_article_code ON public.transfer_logs USING btree (article_code)`
- `ix_transfer_logs_from_dept` — `CREATE INDEX ix_transfer_logs_from_dept ON public.transfer_logs USING btree (from_dept)`
- `ix_transfer_logs_id` — `CREATE INDEX ix_transfer_logs_id ON public.transfer_logs USING btree (id)`
- `ix_transfer_logs_mo_id` — `CREATE INDEX ix_transfer_logs_mo_id ON public.transfer_logs USING btree (mo_id)`
- `ix_transfer_logs_status` — `CREATE INDEX ix_transfer_logs_status ON public.transfer_logs USING btree (status)`
- `ix_transfer_logs_to_dept` — `CREATE INDEX ix_transfer_logs_to_dept ON public.transfer_logs USING btree (to_dept)`
- `transfer_logs_pkey` — `CREATE UNIQUE INDEX transfer_logs_pkey ON public.transfer_logs USING btree (id)`

### `user_activity_logs`

| # | Column | Type | Nullable | Default | Notes |
|---|--------|------|----------|---------|-------|
| 1 | `id` | `bigint` | NOT NULL | auto-increment | 🔑 PK |
| 2 | `user_id` | `bigint` | NOT NULL |  | FK → `users.id` |
| 3 | `activity_type` | `varchar(50)` | NOT NULL |  |  |
| 4 | `activity_details` | `text` |  |  |  |
| 5 | `session_id` | `varchar(255)` |  |  |  |
| 6 | `ip_address` | `varchar(45)` |  |  |  |
| 7 | `user_agent` | `varchar(500)` |  |  |  |
| 8 | `timestamp` | `timestamp without time zone` | NOT NULL |  |  |
| 9 | `duration_seconds` | `bigint` |  |  |  |

**Foreign Keys:**
- `user_id` → `users.id`

**Indexes:**
- `idx_activity_user_time` — `CREATE INDEX idx_activity_user_time ON public.user_activity_logs USING btree (user_id, "timestamp")`
- `ix_user_activity_logs_activity_type` — `CREATE INDEX ix_user_activity_logs_activity_type ON public.user_activity_logs USING btree (activity_type)`
- `ix_user_activity_logs_session_id` — `CREATE INDEX ix_user_activity_logs_session_id ON public.user_activity_logs USING btree (session_id)`
- `ix_user_activity_logs_timestamp` — `CREATE INDEX ix_user_activity_logs_timestamp ON public.user_activity_logs USING btree ("timestamp")`
- `ix_user_activity_logs_user_id` — `CREATE INDEX ix_user_activity_logs_user_id ON public.user_activity_logs USING btree (user_id)`
- `user_activity_logs_pkey` — `CREATE UNIQUE INDEX user_activity_logs_pkey ON public.user_activity_logs USING btree (id)`

### `users`

| # | Column | Type | Nullable | Default | Notes |
|---|--------|------|----------|---------|-------|
| 1 | `id` | `integer` | NOT NULL | auto-increment | 🔑 PK |
| 2 | `username` | `varchar(50)` | NOT NULL |  |  |
| 3 | `email` | `varchar(100)` | NOT NULL |  |  |
| 4 | `hashed_password` | `varchar(255)` | NOT NULL |  |  |
| 5 | `full_name` | `varchar(100)` | NOT NULL |  |  |
| 6 | `role` | `userrole` | NOT NULL |  |  |
| 7 | `department` | `varchar(50)` |  |  |  |
| 8 | `is_active` | `boolean` |  |  |  |
| 9 | `is_verified` | `boolean` |  |  |  |
| 10 | `created_at` | `timestamp with time zone` |  | NOW() |  |
| 11 | `last_login` | `timestamp with time zone` |  |  |  |
| 12 | `last_password_change` | `timestamp with time zone` |  |  |  |
| 13 | `login_attempts` | `integer` |  |  |  |
| 14 | `locked_until` | `timestamp with time zone` |  |  |  |

**Indexes:**
- `ix_users_created_at` — `CREATE INDEX ix_users_created_at ON public.users USING btree (created_at)`
- `ix_users_email` — `CREATE UNIQUE INDEX ix_users_email ON public.users USING btree (email)`
- `ix_users_id` — `CREATE INDEX ix_users_id ON public.users USING btree (id)`
- `ix_users_is_active` — `CREATE INDEX ix_users_is_active ON public.users USING btree (is_active)`
- `ix_users_role` — `CREATE INDEX ix_users_role ON public.users USING btree (role)`
- `ix_users_username` — `CREATE UNIQUE INDEX ix_users_username ON public.users USING btree (username)`
- `users_pkey` — `CREATE UNIQUE INDEX users_pkey ON public.users USING btree (id)`

### `warehouse_finishing_stocks`

| # | Column | Type | Nullable | Default | Notes |
|---|--------|------|----------|---------|-------|
| 1 | `id` | `integer` | NOT NULL | auto-increment | 🔑 PK |
| 2 | `stage` | `varchar(20)` | NOT NULL |  | UNIQUE |
| 3 | `product_id` | `integer` | NOT NULL |  | FK → `products.id` · UNIQUE |
| 4 | `good_qty` | `numeric(10,2)` | NOT NULL | '0'::numeric |  |
| 5 | `defect_qty` | `numeric(10,2)` | NOT NULL | '0'::numeric |  |
| 6 | `created_at` | `timestamp without time zone` | NOT NULL | NOW() |  |
| 7 | `updated_at` | `timestamp without time zone` | NOT NULL | NOW() |  |

**Foreign Keys:**
- `product_id` → `products.id`

**Indexes:**
- `uq_stage_product` — `CREATE UNIQUE INDEX uq_stage_product ON public.warehouse_finishing_stocks USING btree (stage, product_id)`
- `warehouse_finishing_stocks_pkey` — `CREATE UNIQUE INDEX warehouse_finishing_stocks_pkey ON public.warehouse_finishing_stocks USING btree (id)`

### `wip_transfer_logs`

| # | Column | Type | Nullable | Default | Notes |
|---|--------|------|----------|---------|-------|
| 1 | `id` | `integer` | NOT NULL | auto-increment | 🔑 PK |
| 2 | `wo_id` | `integer` | NOT NULL |  | FK → `work_orders.id` |
| 3 | `wip_product_id` | `integer` | NOT NULL |  | FK → `products.id` |
| 4 | `from_department` | `varchar(50)` | NOT NULL |  |  |
| 5 | `to_department` | `varchar(50)` | NOT NULL |  |  |
| 6 | `qty_transferred` | `numeric(10,2)` | NOT NULL |  |  |
| 7 | `transfer_date` | `timestamp with time zone` |  | NOW() |  |
| 8 | `transferred_by` | `integer` |  |  | FK → `users.id` |
| 9 | `notes` | `text` |  |  |  |
| 10 | `created_at` | `timestamp with time zone` |  | NOW() |  |

**Foreign Keys:**
- `transferred_by` → `users.id`
- `wip_product_id` → `products.id`
- `wo_id` → `work_orders.id`

**Indexes:**
- `idx_wip_transfer_date` — `CREATE INDEX idx_wip_transfer_date ON public.wip_transfer_logs USING btree (transfer_date)`
- `idx_wip_transfer_product` — `CREATE INDEX idx_wip_transfer_product ON public.wip_transfer_logs USING btree (wip_product_id)`
- `idx_wip_transfer_wo` — `CREATE INDEX idx_wip_transfer_wo ON public.wip_transfer_logs USING btree (wo_id)`
- `wip_transfer_logs_pkey` — `CREATE UNIQUE INDEX wip_transfer_logs_pkey ON public.wip_transfer_logs USING btree (id)`

### `work_orders`

| # | Column | Type | Nullable | Default | Notes |
|---|--------|------|----------|---------|-------|
| 1 | `id` | `integer` | NOT NULL | auto-increment | 🔑 PK |
| 2 | `mo_id` | `integer` | NOT NULL |  | FK → `manufacturing_orders.id` |
| 3 | `product_id` | `integer` | NOT NULL |  | FK → `products.id` |
| 4 | `department` | `department` | NOT NULL |  |  |
| 5 | `status` | `workorderstatus` |  |  |  |
| 6 | `start_time` | `timestamp with time zone` |  |  |  |
| 7 | `end_time` | `timestamp with time zone` |  |  |  |
| 8 | `input_qty` | `numeric(10,2)` | NOT NULL |  |  |
| 9 | `output_qty` | `numeric(10,2)` |  |  |  |
| 10 | `reject_qty` | `numeric(10,2)` |  |  |  |
| 11 | `worker_id` | `integer` |  |  | FK → `users.id` |
| 12 | `created_at` | `timestamp with time zone` |  | NOW() |  |
| 13 | `input_wip_product_id` | `integer` |  |  | FK → `products.id` |
| 14 | `output_wip_product_id` | `integer` |  |  | FK → `products.id` |
| 15 | `sequence` | `integer` |  |  |  |
| 16 | `wo_number` | `varchar(100)` |  |  |  |
| 17 | `target_qty` | `numeric(10,2)` |  |  |  |
| 18 | `notes` | `text` |  |  |  |
| 19 | `planned_start_date` | `date` |  |  |  |
| 20 | `actual_start_date` | `date` |  |  |  |
| 21 | `planned_completion_date` | `date` |  |  |  |
| 22 | `actual_completion_date` | `date` |  |  |  |
| 23 | `production_date_stamp` | `date` |  |  |  |
| 24 | `cartons_packed` | `integer` |  | 0 |  |
| 25 | `pallets_formed` | `integer` |  | 0 |  |
| 26 | `packing_validated` | `boolean` |  | false |  |

**Foreign Keys:**
- `input_wip_product_id` → `products.id`
- `input_wip_product_id` → `products.id`
- `mo_id` → `manufacturing_orders.id`
- `output_wip_product_id` → `products.id`
- `output_wip_product_id` → `products.id`
- `product_id` → `products.id`
- `worker_id` → `users.id`

**Indexes:**
- `idx_wo_actual_start` — `CREATE INDEX idx_wo_actual_start ON public.work_orders USING btree (actual_start_date)`
- `idx_wo_planned_start` — `CREATE INDEX idx_wo_planned_start ON public.work_orders USING btree (planned_start_date)`
- `idx_work_orders_mo_id` — `CREATE INDEX idx_work_orders_mo_id ON public.work_orders USING btree (mo_id)`
- `idx_work_orders_sequence` — `CREATE INDEX idx_work_orders_sequence ON public.work_orders USING btree (mo_id, sequence)`
- `idx_work_orders_status` — `CREATE INDEX idx_work_orders_status ON public.work_orders USING btree (status)`
- `ix_work_orders_department` — `CREATE INDEX ix_work_orders_department ON public.work_orders USING btree (department)`
- `ix_work_orders_id` — `CREATE INDEX ix_work_orders_id ON public.work_orders USING btree (id)`
- `ix_work_orders_mo_id` — `CREATE INDEX ix_work_orders_mo_id ON public.work_orders USING btree (mo_id)`
- `ix_work_orders_status` — `CREATE INDEX ix_work_orders_status ON public.work_orders USING btree (status)`
- `work_orders_pkey` — `CREATE UNIQUE INDEX work_orders_pkey ON public.work_orders USING btree (id)`
