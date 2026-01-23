# 🔧 BOM Management API Documentation

**Updated**: 2026-01-23  
**Version**: 1.0  
**Base URL**: `http://localhost:8000/api/v1`

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Authentication](#authentication)
3. [Endpoints](#endpoints)
4. [Data Models](#data-models)
5. [Response Format](#response-format)
6. [Error Handling](#error-handling)
7. [Examples](#examples)

---

## Overview

BOM (Bill of Materials) API menyediakan operasi CRUD untuk mengelola material/komponen yang dibutuhkan dalam produksi.

### Supported Operations:
- ✅ CREATE - Tambah BOM baru
- ✅ READ - Lihat detail BOM atau list
- ✅ UPDATE - Edit BOM yang sudah ada
- ✅ DELETE - Hapus BOM
- ✅ LIST - Lihat daftar BOM dengan filter & pagination
- ✅ IMPORT - Bulk import BOM dari file
- ✅ EXPORT - Bulk export BOM ke file

---

## Authentication

Semua endpoint require Authentication dengan token JWT.

### Header yang diperlukan:
```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

### Get Token:
```bash
POST /api/v1/auth/login
{
  "email": "user@example.com",
  "password": "password123"
}

Response:
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

---

## Endpoints

### 1. CREATE BOM (Add New)

**Endpoint:**
```
POST /api/v1/bom
```

**Permission Required:**
- `ppic.create_bom` (PBAC)

**Request Body:**
```json
{
  "product_code": "TS-001",
  "product_name": "T-Shirt Premium",
  "material_component": "Cotton Fabric",
  "quantity_required": 1.5,
  "unit": "m",
  "unit_price": 25000,
  "material_type": "fabric",
  "status": "active",
  "notes": "Premium quality cotton, 100% cotton, white color"
}
```

**Field Validation:**

| Field | Type | Required | Validation |
|-------|------|----------|-----------|
| product_code | string | ✅ | Max 50 chars, unique per product+material |
| product_name | string | ✅ | Max 100 chars |
| material_component | string | ✅ | Max 100 chars |
| quantity_required | number | ✅ | Min 0.01, Max 999999 |
| unit | string | ✅ | kg, m, pcs, L, box |
| unit_price | number | ❌ | Min 0, Max 999999999 |
| material_type | string | ❌ | fabric, thread, button, zipper, elastic, lace, other |
| status | string | ❌ | active (default), inactive |
| notes | string | ❌ | Max 500 chars |

**Response Success (201):**
```json
{
  "status": "success",
  "message": "BOM created successfully",
  "data": {
    "id": 1,
    "product_code": "TS-001",
    "product_name": "T-Shirt Premium",
    "material_component": "Cotton Fabric",
    "quantity_required": 1.5,
    "unit": "m",
    "unit_price": 25000,
    "material_type": "fabric",
    "status": "active",
    "notes": "Premium quality cotton...",
    "created_at": "2026-01-23T10:30:00Z",
    "created_by": "admin@example.com"
  }
}
```

**Response Error (400):**
```json
{
  "status": "error",
  "message": "Validation error",
  "errors": [
    {
      "field": "quantity_required",
      "message": "Quantity must be greater than 0"
    }
  ]
}
```

---

### 2. GET BOM Detail

**Endpoint:**
```
GET /api/v1/bom/{id}
```

**Permission Required:**
- `ppic.view_bom`

**Parameters:**
- `id` (path, required) - BOM ID

**Response Success (200):**
```json
{
  "status": "success",
  "data": {
    "id": 1,
    "product_code": "TS-001",
    "product_name": "T-Shirt Premium",
    "material_component": "Cotton Fabric",
    "quantity_required": 1.5,
    "unit": "m",
    "unit_price": 25000,
    "material_type": "fabric",
    "status": "active",
    "notes": "Premium quality cotton...",
    "created_at": "2026-01-23T10:30:00Z",
    "updated_at": "2026-01-23T10:30:00Z",
    "created_by": "admin@example.com",
    "updated_by": "admin@example.com"
  }
}
```

---

### 3. LIST BOM (With Filtering & Pagination)

**Endpoint:**
```
GET /api/v1/bom
```

**Permission Required:**
- `ppic.view_bom`

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|------------|
| page | int | 1 | Page number |
| per_page | int | 20 | Items per page (max 100) |
| product_code | string | - | Filter by product code |
| product_name | string | - | Filter by product name (case-insensitive) |
| material_type | string | - | Filter by material type |
| status | string | active | Filter by status (active/inactive/all) |
| sort_by | string | created_at | Sort field (id, product_code, created_at) |
| sort_order | string | desc | asc or desc |

**Examples:**

```bash
# Get all active BOMs
GET /api/v1/bom?status=active

# Get BOMs for specific product
GET /api/v1/bom?product_code=TS-001

# Get page 2 with 50 items per page
GET /api/v1/bom?page=2&per_page=50

# Get fabric materials only
GET /api/v1/bom?material_type=fabric

# Combined filter
GET /api/v1/bom?product_code=TS-001&status=active&sort_by=material_component
```

**Response Success (200):**
```json
{
  "status": "success",
  "data": [
    {
      "id": 1,
      "product_code": "TS-001",
      "product_name": "T-Shirt Premium",
      "material_component": "Cotton Fabric",
      "quantity_required": 1.5,
      "unit": "m",
      "unit_price": 25000,
      "material_type": "fabric",
      "status": "active"
    },
    {
      "id": 2,
      "product_code": "TS-001",
      "product_name": "T-Shirt Premium",
      "material_component": "Thread White",
      "quantity_required": 2,
      "unit": "pcs",
      "unit_price": 5000,
      "material_type": "thread",
      "status": "active"
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total_items": 150,
    "total_pages": 8,
    "has_next": true,
    "has_prev": false
  }
}
```

---

### 4. UPDATE BOM

**Endpoint:**
```
PUT /api/v1/bom/{id}
```

**Permission Required:**
- `ppic.edit_bom`

**Request Body:**
```json
{
  "quantity_required": 2.0,
  "unit_price": 28000,
  "status": "active",
  "notes": "Updated: Premium quality cotton"
}
```

**Note:** Field berikut TIDAK bisa diubah:
- `product_code` (use DELETE + CREATE)
- `product_name` (use DELETE + CREATE)
- `material_component` (use DELETE + CREATE)
- `created_at`
- `created_by`

**Response Success (200):**
```json
{
  "status": "success",
  "message": "BOM updated successfully",
  "data": {
    "id": 1,
    "quantity_required": 2.0,
    "unit_price": 28000,
    "status": "active",
    "notes": "Updated: Premium quality cotton",
    "updated_at": "2026-01-23T11:45:00Z",
    "updated_by": "supervisor@example.com"
  }
}
```

---

### 5. DELETE BOM

**Endpoint:**
```
DELETE /api/v1/bom/{id}
```

**Permission Required:**
- `ppic.delete_bom`

**Query Parameters:**
- `force` (optional, boolean) - Force delete jika BOM sedang digunakan

**Response Success (200):**
```json
{
  "status": "success",
  "message": "BOM deleted successfully",
  "data": {
    "id": 1,
    "deleted_at": "2026-01-23T12:00:00Z"
  }
}
```

**Response Warning (400 - Jika BOM sedang digunakan):**
```json
{
  "status": "error",
  "message": "BOM is in use",
  "warning": "This BOM is currently used in 5 active production orders",
  "affected_orders": ["MO-2026-001", "MO-2026-002"],
  "suggestion": "Set status to 'inactive' instead, or use force=true to delete anyway"
}
```

---

### 6. BULK IMPORT BOM

**Endpoint:**
```
POST /api/v1/bom/import
```

**Permission Required:**
- `ppic.create_bom`
- `admin.import`

**Content-Type:**
```
multipart/form-data
```

**Request:**
```
form-data:
  file: <CSV or Excel file>
  skip_duplicates: true (default: false)
  update_existing: true (default: false)
```

**Supported Formats:**
- `.csv` (CSV - Comma Separated)
- `.xlsx` (Excel 2007+)
- `.xls` (Excel 97-2003)

**CSV Format:**
```csv
product_code,product_name,material_component,quantity_required,unit,unit_price,material_type,status,notes
TS-001,T-Shirt Premium,Cotton Fabric,1.5,m,25000,fabric,active,Premium quality
TS-001,T-Shirt Premium,Thread White,2,pcs,5000,thread,active,Polyester
```

**Response Success (200):**
```json
{
  "status": "success",
  "message": "Import completed",
  "stats": {
    "total_rows": 50,
    "imported": 48,
    "skipped": 2,
    "errors": 0,
    "warnings": 2
  },
  "details": {
    "imported_items": [
      {"row": 1, "id": 101, "product_code": "TS-001", "material_component": "Cotton Fabric"},
      {"row": 2, "id": 102, "product_code": "TS-001", "material_component": "Thread"}
    ],
    "skipped_items": [
      {"row": 15, "reason": "Duplicate BOM", "data": "TS-001 / Cotton Fabric"},
      {"row": 32, "reason": "Quantity invalid", "data": "-1"}
    ],
    "warnings": [
      {"row": 5, "warning": "Material type not recognized, set to 'other'"}
    ]
  }
}
```

---

### 7. BULK EXPORT BOM

**Endpoint:**
```
GET /api/v1/bom/export
```

**Permission Required:**
- `ppic.view_bom`

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|------------|
| format | string | csv | csv atau xlsx |
| product_code | string | - | Filter by product code |
| status | string | all | active, inactive, all |
| include_fields | string | all | Comma-separated fields to include |

**Examples:**

```bash
# Export all as CSV
GET /api/v1/bom/export?format=csv

# Export as Excel
GET /api/v1/bom/export?format=xlsx

# Export specific product only
GET /api/v1/bom/export?format=xlsx&product_code=TS-001

# Export active BOMs only
GET /api/v1/bom/export?format=csv&status=active
```

**Response Success (200):**
```
Content-Type: text/csv (or application/vnd.openxmlformats-officedocument.spreadsheetml.sheet)
Content-Disposition: attachment; filename="bom_export_2026_01_23.csv"

[File content with BOM data]
```

---

## Data Models

### BOM Object

```json
{
  "id": 1,
  "product_code": "TS-001",
  "product_name": "T-Shirt Premium",
  "material_component": "Cotton Fabric",
  "quantity_required": 1.5,
  "unit": "m",
  "unit_price": 25000,
  "material_type": "fabric",
  "status": "active",
  "notes": "Premium quality cotton, 100% cotton, white color",
  "created_at": "2026-01-23T10:30:00Z",
  "updated_at": "2026-01-23T10:30:00Z",
  "created_by": "admin@example.com",
  "updated_by": "admin@example.com"
}
```

### Enums

**Unit Options:**
```
"kg"    - Kilogram (untuk bahan cair/bubuk)
"m"     - Meter (untuk kain/material lembaran)
"pcs"   - Pieces (untuk barang individual)
"L"     - Liter (untuk cairan)
"box"   - Box/Karton (untuk kemasan)
```

**Material Type Options:**
```
"fabric"    - Kain
"thread"    - Benang
"button"    - Kancing/Tombol
"zipper"    - Resleting
"elastic"   - Elastis
"lace"      - Renda
"other"     - Lainnya
```

**Status Options:**
```
"active"    - Aktif digunakan
"inactive"  - Tidak digunakan
```

---

## Response Format

### Success Response (2xx)

```json
{
  "status": "success",
  "message": "Operation successful",
  "data": { /* Response data */ },
  "meta": {
    "timestamp": "2026-01-23T10:30:00Z",
    "request_id": "req_123456"
  }
}
```

### Error Response (4xx/5xx)

```json
{
  "status": "error",
  "message": "Human-readable error message",
  "error_code": "INVALID_REQUEST",
  "errors": [
    {
      "field": "quantity_required",
      "message": "Must be greater than 0",
      "code": "VALIDATION_ERROR"
    }
  ],
  "meta": {
    "timestamp": "2026-01-23T10:30:00Z",
    "request_id": "req_123456"
  }
}
```

---

## Error Handling

### HTTP Status Codes

| Code | Meaning | Example |
|------|---------|---------|
| 200 | OK - Request berhasil | GET, PUT, DELETE success |
| 201 | Created - Resource dibuat | POST BOM created |
| 400 | Bad Request - Invalid data | Missing required field |
| 401 | Unauthorized - No token | Missing Authorization header |
| 403 | Forbidden - No permission | Permission denied by PBAC |
| 404 | Not Found - Resource tidak ada | BOM ID not found |
| 409 | Conflict - Duplicate data | Duplicate BOM entry |
| 422 | Unprocessable Entity - Validation error | Invalid email format |
| 429 | Too Many Requests - Rate limited | Exceeded request limit |
| 500 | Server Error - Internal error | Database error |

### Error Codes

| Code | Description |
|------|------------|
| VALIDATION_ERROR | Field validation failed |
| DUPLICATE_ERROR | Duplicate resource |
| NOT_FOUND | Resource tidak ditemukan |
| UNAUTHORIZED | Authentication failed |
| FORBIDDEN | Permission denied |
| CONFLICT | Data conflict dengan existing |
| SERVER_ERROR | Internal server error |

---

## Examples

### Example 1: Create BOM for T-Shirt Premium

**Request:**
```bash
curl -X POST http://localhost:8000/api/v1/bom \
  -H "Authorization: Bearer eyJhbGc..." \
  -H "Content-Type: application/json" \
  -d '{
    "product_code": "TS-001",
    "product_name": "T-Shirt Premium",
    "material_component": "Cotton Fabric",
    "quantity_required": 1.5,
    "unit": "m",
    "unit_price": 25000,
    "material_type": "fabric",
    "status": "active",
    "notes": "Premium quality cotton, 100% cotton"
  }'
```

**Response:**
```json
{
  "status": "success",
  "message": "BOM created successfully",
  "data": {
    "id": 1,
    "product_code": "TS-001",
    "material_component": "Cotton Fabric",
    "quantity_required": 1.5,
    "unit": "m",
    "unit_price": 25000,
    "status": "active"
  }
}
```

### Example 2: Get all BOMs for Product TS-001

**Request:**
```bash
curl -X GET "http://localhost:8000/api/v1/bom?product_code=TS-001&status=active" \
  -H "Authorization: Bearer eyJhbGc..."
```

**Response:**
```json
{
  "status": "success",
  "data": [
    {
      "id": 1,
      "product_code": "TS-001",
      "material_component": "Cotton Fabric",
      "quantity_required": 1.5,
      "unit": "m"
    },
    {
      "id": 2,
      "product_code": "TS-001",
      "material_component": "Thread White",
      "quantity_required": 2,
      "unit": "pcs"
    }
  ],
  "pagination": {
    "total_items": 3,
    "total_pages": 1
  }
}
```

### Example 3: Update BOM Quantity

**Request:**
```bash
curl -X PUT http://localhost:8000/api/v1/bom/1 \
  -H "Authorization: Bearer eyJhbGc..." \
  -H "Content-Type: application/json" \
  -d '{
    "quantity_required": 2.0,
    "notes": "Updated quantity due to design change"
  }'
```

**Response:**
```json
{
  "status": "success",
  "message": "BOM updated successfully",
  "data": {
    "id": 1,
    "quantity_required": 2.0,
    "notes": "Updated quantity due to design change"
  }
}
```

### Example 4: Bulk Import BOM from CSV

**Request:**
```bash
curl -X POST http://localhost:8000/api/v1/bom/import \
  -H "Authorization: Bearer eyJhbGc..." \
  -F "file=@bom_data.csv" \
  -F "skip_duplicates=true"
```

**bom_data.csv:**
```csv
product_code,product_name,material_component,quantity_required,unit,unit_price,status
TS-001,T-Shirt Premium,Cotton Fabric,1.5,m,25000,active
TS-001,T-Shirt Premium,Thread White,2,pcs,5000,active
TS-002,T-Shirt Standard,Cotton Fabric,1.0,m,15000,active
```

**Response:**
```json
{
  "status": "success",
  "message": "Import completed",
  "stats": {
    "total_rows": 3,
    "imported": 3,
    "skipped": 0,
    "errors": 0
  }
}
```

---

## Integration Example: Python

```python
import requests

# Initialize client
BASE_URL = "http://localhost:8000/api/v1"
TOKEN = "your_jwt_token_here"
headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

# Create BOM
def create_bom(product_code, material_component, quantity, unit, price):
    data = {
        "product_code": product_code,
        "product_name": "T-Shirt Premium",
        "material_component": material_component,
        "quantity_required": quantity,
        "unit": unit,
        "unit_price": price,
        "status": "active"
    }
    response = requests.post(f"{BASE_URL}/bom", json=data, headers=headers)
    return response.json()

# Get BOMs for product
def get_product_boms(product_code):
    params = {"product_code": product_code, "status": "active"}
    response = requests.get(f"{BASE_URL}/bom", params=params, headers=headers)
    return response.json()

# Update BOM
def update_bom(bom_id, quantity, price):
    data = {"quantity_required": quantity, "unit_price": price}
    response = requests.put(f"{BASE_URL}/bom/{bom_id}", json=data, headers=headers)
    return response.json()

# Usage
create_bom("TS-001", "Cotton Fabric", 1.5, "m", 25000)
boms = get_product_boms("TS-001")
print(f"Found {len(boms['data'])} BOMs for TS-001")
```

---

**End of Document**

*Last Updated: 2026-01-23*  
*Version: 1.0*
