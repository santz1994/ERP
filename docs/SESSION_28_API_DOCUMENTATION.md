# API DOCUMENTATION - SESSION 28 PHASE 1

**Version**: 1.0  
**Date**: January 26, 2026  
**Status**: 📖 COMPREHENSIVE  
**Total Endpoints**: 126 (118 existing + 8 Phase 1 new)

---

## 📑 TABLE OF CONTENTS

1. [Overview](#overview)
2. [Authentication](#authentication)
3. [New Phase 1 Endpoints](#new-phase-1-endpoints)
   - [BOM Management](#bom-management)
   - [PPIC Lifecycle](#ppic-lifecycle)
4. [Path Changes](#path-changes)
5. [Error Handling](#error-handling)
6. [Code Examples](#code-examples)
7. [FAQ](#faq)

---

## 🔗 OVERVIEW

### Base URL
```
Development:  http://localhost:8000/api/v1
Production:   https://api.erp2026.com/api/v1
Staging:      https://staging-api.erp2026.com/api/v1
```

### API Features
- ✅ RESTful architecture
- ✅ JSON request/response
- ✅ JWT authentication
- ✅ Role-based access control (RBAC)
- ✅ Permission-based access control (PBAC)
- ✅ ISO 8601 datetime format
- ✅ Comprehensive audit logging
- ✅ OpenAPI/Swagger documentation

### Standards Compliance
- HTTP Status Codes: RFC 7231
- Content-Type: application/json
- DateTime: ISO 8601 (UTC)
- Pagination: offset/limit pattern

---

## 🔐 AUTHENTICATION

### JWT Token Format

All protected endpoints require Authorization header:

```
Authorization: Bearer <JWT_TOKEN>
```

### Token Structure

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

### Obtaining Token

```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "username": "ppic_manager",
  "password": "secure_password"
}
```

### Token Expiration

- Lifetime: 1 hour (3600 seconds)
- Refresh: Use refresh endpoint
- Revocation: Immediate on logout

---

## ✨ NEW PHASE 1 ENDPOINTS

### BOM MANAGEMENT

Bill of Materials endpoints for warehouse management.

---

#### 1️⃣ Create Bill of Materials

**Endpoint**
```http
POST /api/v1/warehouse/bom
```

**Authentication**
- Required: Yes
- Permission: `warehouse.create`

**Request Body**
```json
{
  "product_id": 5,
  "bom_type": "Manufacturing",
  "qty_output": 1.0,
  "supports_multi_material": false,
  "revision": "Rev 1.0"
}
```

**Response** (201 Created)
```json
{
  "id": 12,
  "product_id": 5,
  "product_name": "Toy Bear - Soft Toys Inc",
  "bom_type": "Manufacturing",
  "qty_output": 1.0,
  "revision": "Rev 1.0",
  "revision_count": 1,
  "supports_multi_material": false,
  "is_active": true,
  "revised_by": 1,
  "revision_reason": "Initial BOM creation by ppic_manager",
  "created_at": "2026-01-26T10:30:45.123Z",
  "created_by": 1,
  "updated_at": "2026-01-26T10:30:45.123Z"
}
```

**Error Responses**

```json
// 400 - Product not found
{
  "detail": "Product with ID 999 not found"
}

// 409 - BOM already exists
{
  "detail": "Active BOM already exists for product Toy Bear (ID: 5)"
}

// 403 - Insufficient permissions
{
  "detail": "User does not have permission: warehouse.create"
}
```

**cURL Example**
```bash
curl -X POST http://localhost:8000/api/v1/warehouse/bom \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": 5,
    "bom_type": "Manufacturing",
    "qty_output": 1.0,
    "supports_multi_material": false,
    "revision": "Rev 1.0"
  }'
```

---

#### 2️⃣ List Bill of Materials

**Endpoint**
```http
GET /api/v1/warehouse/bom
```

**Authentication**
- Required: Yes
- Permission: `warehouse.view`

**Query Parameters**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| skip | integer | 0 | Skip first N results |
| limit | integer | 50 | Max results (max 500) |
| active_only | boolean | true | Show only active BOMs |
| product_id | integer | null | Filter by product |
| bom_type | string | null | Filter by type (Manufacturing/Kit) |

**Response** (200 OK)
```json
[
  {
    "id": 1,
    "product_id": 5,
    "product_name": "Toy Bear",
    "bom_type": "Manufacturing",
    "qty_output": 1.0,
    "revision": "Rev 1.0",
    "revision_count": 1,
    "supports_multi_material": false,
    "is_active": true,
    "created_at": "2026-01-25T14:20:00Z",
    "updated_at": "2026-01-25T14:20:00Z"
  },
  {
    "id": 2,
    "product_id": 6,
    "product_name": "Toy Rabbit",
    "bom_type": "Kit/Phantom",
    "qty_output": 1.0,
    "revision": "Rev 2.1",
    "revision_count": 2,
    "supports_multi_material": true,
    "is_active": true,
    "created_at": "2026-01-20T09:15:00Z",
    "updated_at": "2026-01-26T08:45:00Z"
  }
]
```

**cURL Example**
```bash
# List active BOMs for product ID 5
curl -X GET "http://localhost:8000/api/v1/warehouse/bom?product_id=5&active_only=true" \
  -H "Authorization: Bearer $TOKEN"
```

---

#### 3️⃣ Get BOM Details

**Endpoint**
```http
GET /api/v1/warehouse/bom/{bom_id}
```

**Authentication**
- Required: Yes
- Permission: `warehouse.view`

**Path Parameters**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| bom_id | integer | Yes | BOM identifier |

**Response** (200 OK)
```json
{
  "id": 1,
  "product_id": 5,
  "product_name": "Toy Bear",
  "product_code": "TOY-BEAR-001",
  "bom_type": "Manufacturing",
  "qty_output": 1.0,
  "revision": "Rev 1.0",
  "revision_count": 1,
  "supports_multi_material": false,
  "is_active": true,
  "revised_by": 1,
  "revised_by_username": "ppic_manager",
  "revision_reason": "Initial BOM creation",
  "created_at": "2026-01-25T14:20:00Z",
  "created_by": 1,
  "updated_at": "2026-01-25T14:20:00Z",
  "components": [
    {
      "component_id": 101,
      "material_id": 25,
      "material_name": "Fabric - Cotton",
      "quantity": 0.5,
      "unit": "M"
    }
  ]
}
```

**Error Response** (404 Not Found)
```json
{
  "detail": "BOM with ID 999 not found"
}
```

**cURL Example**
```bash
curl -X GET http://localhost:8000/api/v1/warehouse/bom/1 \
  -H "Authorization: Bearer $TOKEN"
```

---

#### 4️⃣ Update BOM Configuration

**Endpoint**
```http
PUT /api/v1/warehouse/bom/{bom_id}
```

**Authentication**
- Required: Yes
- Permission: `warehouse.update`

**Path Parameters**
| Parameter | Type | Required |
|-----------|------|----------|
| bom_id | integer | Yes |

**Request Body**
```json
{
  "supports_multi_material": true,
  "default_variant_selection": "weighted",
  "revision_reason": "Enable multi-material support for cost optimization"
}
```

**Response** (200 OK)
```json
{
  "id": 1,
  "product_id": 5,
  "bom_type": "Manufacturing",
  "qty_output": 1.0,
  "revision": "Rev 2.0",
  "revision_count": 2,
  "supports_multi_material": true,
  "default_variant_selection": "weighted",
  "is_active": true,
  "revised_by": 1,
  "revision_reason": "Enable multi-material support for cost optimization",
  "updated_at": "2026-01-26T10:35:00Z"
}
```

**cURL Example**
```bash
curl -X PUT http://localhost:8000/api/v1/warehouse/bom/1 \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "supports_multi_material": true,
    "default_variant_selection": "weighted",
    "revision_reason": "Enable multi-material support"
  }'
```

---

#### 5️⃣ Delete Bill of Materials

**Endpoint**
```http
DELETE /api/v1/warehouse/bom/{bom_id}
```

**Authentication**
- Required: Yes
- Permission: `warehouse.delete`

**Path Parameters**
| Parameter | Type | Required |
|-----------|------|----------|
| bom_id | integer | Yes |

**Response** (204 No Content)
```
(no body)
```

**Error Response** (400 Bad Request)
```json
{
  "detail": "Cannot delete BOM: 5 active manufacturing orders depend on it"
}
```

**cURL Example**
```bash
curl -X DELETE http://localhost:8000/api/v1/warehouse/bom/1 \
  -H "Authorization: Bearer $TOKEN"
```

---

### PPIC LIFECYCLE

Manufacturing order state machine endpoints.

---

#### 6️⃣ Approve Manufacturing Task

**Endpoint**
```http
POST /api/v1/ppic/tasks/{task_id}/approve
```

**Authentication**
- Required: Yes
- Permission: `ppic.approve`

**Path Parameters**
| Parameter | Type | Required |
|-----------|------|----------|
| task_id | integer | Yes |

**Query Parameters**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| approval_notes | string | No | Reason for approval |

**Response** (200 OK)
```json
{
  "id": 42,
  "product_id": 5,
  "quantity": 100,
  "order_date": "2026-01-26T08:00:00Z",
  "state": "APPROVED",
  "approved_at": "2026-01-26T10:40:00Z",
  "approved_by": 1,
  "approved_by_username": "ppic_manager",
  "approval_notes": "Approved for immediate production",
  "created_at": "2026-01-26T08:00:00Z",
  "updated_at": "2026-01-26T10:40:00Z"
}
```

**Error Responses**

```json
// 400 - Task already in wrong state
{
  "detail": "Cannot approve task in state: IN_PROGRESS. Expected: DRAFT"
}

// 404 - Task not found
{
  "detail": "Manufacturing order with ID 999 not found"
}

// 403 - Permission denied
{
  "detail": "User does not have permission: ppic.approve"
}
```

**State Transitions**
```
DRAFT → APPROVED ✓
APPROVED (cannot re-approve) ✗
IN_PROGRESS (cannot approve) ✗
COMPLETED (cannot approve) ✗
```

**cURL Example**
```bash
curl -X POST "http://localhost:8000/api/v1/ppic/tasks/42/approve?approval_notes=Approved%20for%20production" \
  -H "Authorization: Bearer $TOKEN"
```

---

#### 7️⃣ Start Manufacturing Task

**Endpoint**
```http
POST /api/v1/ppic/tasks/{task_id}/start
```

**Authentication**
- Required: Yes
- Permission: `ppic.execute`

**Path Parameters**
| Parameter | Type | Required |
|-----------|------|----------|
| task_id | integer | Yes |

**Query Parameters**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| start_notes | string | No | Production notes |

**Response** (200 OK)
```json
{
  "id": 42,
  "product_id": 5,
  "quantity": 100,
  "state": "IN_PROGRESS",
  "approved_at": "2026-01-26T10:40:00Z",
  "started_at": "2026-01-26T10:45:00Z",
  "started_by": 2,
  "started_by_username": "operator_cutting",
  "start_notes": "Starting production run",
  "work_orders": [
    {
      "id": 101,
      "department": "cutting",
      "quantity": 100,
      "status": "PENDING"
    }
  ],
  "updated_at": "2026-01-26T10:45:00Z"
}
```

**Error Responses**

```json
// 400 - Task not approved
{
  "detail": "Cannot start task in state: DRAFT. Must be APPROVED first"
}

// 409 - Task already started
{
  "detail": "Task already in progress"
}
```

**State Transitions**
```
DRAFT (not allowed) ✗
APPROVED → IN_PROGRESS ✓
IN_PROGRESS (already started) ✗
COMPLETED (cannot restart) ✗
```

**Side Effects**
- Creates initial work order for first department
- Sets start timestamp
- Records operator

**cURL Example**
```bash
curl -X POST "http://localhost:8000/api/v1/ppic/tasks/42/start?start_notes=Production%20begins" \
  -H "Authorization: Bearer $TOKEN"
```

---

#### 8️⃣ Complete Manufacturing Task

**Endpoint**
```http
POST /api/v1/ppic/tasks/{task_id}/complete
```

**Authentication**
- Required: Yes
- Permission: `ppic.execute`

**Path Parameters**
| Parameter | Type | Required |
|-----------|------|----------|
| task_id | integer | Yes |

**Query Parameters**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| actual_quantity | integer | Yes | Quantity completed |
| quality_notes | string | No | QC comments |
| variance_override | boolean | No | Override variance check |

**Response** (200 OK)
```json
{
  "id": 42,
  "product_id": 5,
  "quantity": 100,
  "actual_quantity": 100,
  "state": "COMPLETED",
  "started_at": "2026-01-26T10:45:00Z",
  "completed_at": "2026-01-26T15:30:00Z",
  "completed_by": 2,
  "quality_notes": "All items passed QC",
  "variance_percent": 0.0,
  "variance_status": "EXACT",
  "duration_hours": 4.75,
  "updated_at": "2026-01-26T15:30:00Z"
}
```

**Error Responses**

```json
// 400 - Task not in progress
{
  "detail": "Cannot complete task in state: DRAFT"
}

// 422 - Quantity out of valid range
{
  "detail": "Actual quantity must be > 0"
}

// 409 - Variance exceeds threshold
{
  "detail": "Quantity variance 25% exceeds threshold (10%). Use variance_override=true to force"
}
```

**Variance Calculation**
```
variance_percent = |actual_qty - expected_qty| / expected_qty * 100

✅ EXACT:   variance ≤ 1%
⚠️  MINOR:   variance 1-10%
🔴 MAJOR:   variance > 10% (requires override)
```

**cURL Example**
```bash
curl -X POST "http://localhost:8000/api/v1/ppic/tasks/42/complete?actual_quantity=100&quality_notes=All%20passed%20QC" \
  -H "Authorization: Bearer $TOKEN"
```

---

## 🔄 PATH CHANGES

### Updated Paths (Session 28)

#### Kanban Endpoints (Moved)

**Before:**
```
GET  /api/v1/kanban/cards/all
POST /api/v1/kanban/cards/{id}/approve
POST /api/v1/kanban/cards/{id}/reject
POST /api/v1/kanban/cards/{id}/ship
POST /api/v1/kanban/cards/{id}/receive
```

**After:**
```
GET  /api/v1/ppic/kanban/cards/all
POST /api/v1/ppic/kanban/cards/{id}/approve
POST /api/v1/ppic/kanban/cards/{id}/reject
POST /api/v1/ppic/kanban/cards/{id}/ship
POST /api/v1/ppic/kanban/cards/{id}/receive
```

**Migration Impact**
- Frontend: ✅ Already updated
- Mobile App: ⚠️ Needs updating
- Third-party: ❌ Will break (deprecated old path)

#### Other Paths (Unchanged)

```
✅ /api/v1/import-export/*   (Correct)
✅ /api/v1/warehouse/stock/* (Correct)
✅ /api/v1/ppic/*            (Correct)
```

---

## ⚠️ ERROR HANDLING

### HTTP Status Codes

| Code | Meaning | Example |
|------|---------|---------|
| 200 | Success - GET/PUT/PATCH | BOM retrieved successfully |
| 201 | Success - Resource created | BOM created |
| 204 | Success - No content | BOM deleted |
| 400 | Bad Request | Product ID invalid |
| 401 | Unauthorized | Missing token |
| 403 | Forbidden | No permission |
| 404 | Not Found | BOM ID doesn't exist |
| 409 | Conflict | BOM already exists |
| 422 | Validation Error | Invalid quantity |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Server Error | Database connection failed |

### Error Response Format

```json
{
  "detail": "User-friendly error message",
  "error_code": "WAREHOUSE_BOM_NOT_FOUND",
  "timestamp": "2026-01-26T10:30:45Z",
  "request_id": "req_123456789"
}
```

### Common Errors

**401 Unauthorized**
```json
{
  "detail": "Not authenticated",
  "error_code": "AUTHENTICATION_REQUIRED"
}
```

**403 Forbidden**
```json
{
  "detail": "Insufficient permissions for operation: warehouse.create",
  "error_code": "PERMISSION_DENIED"
}
```

**422 Validation Error**
```json
{
  "detail": [
    {
      "loc": ["body", "qty_output"],
      "msg": "ensure this value is greater than 0",
      "type": "value_error.number.not_gt"
    }
  ]
}
```

---

## 💻 CODE EXAMPLES

### JavaScript/Node.js

```javascript
// Import axios
const axios = require('axios');

// 1. Create BOM
async function createBOM(token) {
  try {
    const response = await axios.post(
      'http://localhost:8000/api/v1/warehouse/bom',
      {
        product_id: 5,
        bom_type: 'Manufacturing',
        qty_output: 1.0,
        supports_multi_material: false,
        revision: 'Rev 1.0'
      },
      {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      }
    );
    console.log('BOM created:', response.data);
  } catch (error) {
    console.error('Error:', error.response.data);
  }
}

// 2. List BOMs
async function listBOMs(token) {
  try {
    const response = await axios.get(
      'http://localhost:8000/api/v1/warehouse/bom?active_only=true',
      {
        headers: { 'Authorization': `Bearer ${token}` }
      }
    );
    console.log('BOMs:', response.data);
  } catch (error) {
    console.error('Error:', error.message);
  }
}

// 3. Approve task
async function approveMOTask(token, taskId) {
  try {
    const response = await axios.post(
      `http://localhost:8000/api/v1/ppic/tasks/${taskId}/approve`,
      null,
      {
        params: {
          approval_notes: 'Approved for production'
        },
        headers: { 'Authorization': `Bearer ${token}` }
      }
    );
    console.log('Task approved:', response.data);
  } catch (error) {
    console.error('Error:', error.response.data);
  }
}
```

### Python

```python
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000/api/v1"
TOKEN = "your-jwt-token"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

# 1. Create BOM
def create_bom(product_id):
    payload = {
        "product_id": product_id,
        "bom_type": "Manufacturing",
        "qty_output": 1.0,
        "supports_multi_material": False,
        "revision": "Rev 1.0"
    }
    response = requests.post(f"{BASE_URL}/warehouse/bom", json=payload, headers=headers)
    if response.status_code == 201:
        return response.json()
    else:
        print(f"Error: {response.status_code}")
        print(response.json())

# 2. List BOMs
def list_boms(active_only=True):
    params = {"active_only": active_only, "limit": 50}
    response = requests.get(f"{BASE_URL}/warehouse/bom", params=params, headers=headers)
    return response.json() if response.status_code == 200 else None

# 3. Approve task
def approve_task(task_id, notes=""):
    params = {"approval_notes": notes}
    response = requests.post(
        f"{BASE_URL}/ppic/tasks/{task_id}/approve",
        params=params,
        headers=headers
    )
    return response.json() if response.status_code == 200 else None

# Usage
bom = create_bom(5)
print(f"Created BOM: {bom['id']}")

boms = list_boms()
print(f"Total BOMs: {len(boms)}")

result = approve_task(42, "Ready for production")
print(f"Task state: {result['state']}")
```

### React

```javascript
import axios from 'axios';
import { useState } from 'react';

function BOMManagement() {
  const [boms, setBOMs] = useState([]);
  const [loading, setLoading] = useState(false);
  const token = localStorage.getItem('access_token');

  const api = axios.create({
    baseURL: 'http://localhost:8000/api/v1',
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });

  // Fetch BOMs
  const fetchBOMs = async () => {
    setLoading(true);
    try {
      const response = await api.get('/warehouse/bom?active_only=true');
      setBOMs(response.data);
    } catch (error) {
      console.error('Error fetching BOMs:', error);
    }
    setLoading(false);
  };

  // Create BOM
  const createBOM = async (productId) => {
    try {
      const response = await api.post('/warehouse/bom', {
        product_id: productId,
        bom_type: 'Manufacturing',
        qty_output: 1.0,
        supports_multi_material: false,
        revision: 'Rev 1.0'
      });
      setBOMs([...boms, response.data]);
      return response.data;
    } catch (error) {
      console.error('Error creating BOM:', error.response.data);
    }
  };

  return (
    <div>
      <button onClick={fetchBOMs}>Fetch BOMs</button>
      <button onClick={() => createBOM(5)}>Create BOM</button>
      {loading ? <p>Loading...</p> : <BOMList boms={boms} />}
    </div>
  );
}
```

---

## ❓ FAQ

### Q: What permissions do I need for BOM endpoints?
**A**: 
- Read: `warehouse.view`
- Create: `warehouse.create`
- Update: `warehouse.update`
- Delete: `warehouse.delete`

### Q: Can I batch approve multiple PPIC tasks?
**A**: Not in Phase 1, but this is planned for Phase 2.

### Q: How do I handle datetime in my app?
**A**: All dates are ISO 8601 UTC format. Parse with: `new Date(date_string)`

### Q: What happens if I request an old path (e.g., `/kanban/*`)?
**A**: Returns 404 Not Found. Update to `/ppic/kanban/*`

### Q: How long do JWT tokens last?
**A**: 1 hour (3600 seconds). Use refresh endpoint to extend.

### Q: Can I update a BOM that's currently in manufacturing?
**A**: Yes, but it won't affect orders already started. Only affects new orders.

### Q: What's the maximum variance I can have on task completion?
**A**: 10% before override required. Contact team lead for variance > 10%.

---

## 📞 SUPPORT

- **API Issues**: Slack #api-support
- **Documentation**: GitHub Wiki
- **Bug Report**: Jira ERP-2026
- **Feature Request**: Product Roadmap

---

**Document Version**: 1.0  
**Last Updated**: January 26, 2026  
**Next Update**: After Phase 2 implementation
