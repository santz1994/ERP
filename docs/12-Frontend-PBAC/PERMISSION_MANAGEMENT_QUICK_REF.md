# Permission Management Quick Reference Guide
## Phase 16 Week 4 | Session 13.5

**Last Updated:** 2026-01-21  
**Purpose:** Quick guide for developers and admins using the new Permission Management system

---

## 🚀 Quick Start

### Accessing Permission Management

**URL:** `http://localhost:5173/admin/permissions`

**Required Permission:**
- View: `admin.view_system_info`
- Modify: `admin.manage_users`

**Menu Path:**
```
Sidebar → Admin → Permissions
```

---

## 👤 User Roles & Access

| Role | View Permissions | Grant/Revoke | User Management |
|------|-----------------|--------------|-----------------|
Superadmin | ✅ | ✅ | ✅ |
Developer | ✅ | ✅ | ✅ |
| **ADMIN** | ✅ | ✅ | ❌ |
| **MANAGER** | ✅ | ❌ | ❌ |
| **OPERATOR** | ❌ | ❌ | ❌ |
| **SPV** | ❌ | ❌ | ❌ |

---

## 🎯 Common Tasks

### 1. View User Permissions

**Steps:**
1. Navigate to `/admin/permissions`
2. Search for user in left panel
3. Click on username
4. View 3 sections:
   - **Statistics** (top cards)
   - **Role Permissions** (purple badges)
   - **Custom Permissions** (green badges)

**What You'll See:**
```
Statistics:
┌────────────┬──────────┬─────────┐
│ Total: 42  │ Role: 36 │ Custom: 6 │
└────────────┴──────────┴─────────┘

Role Permissions (36):
[cutting.view_status] [cutting.allocate_material] ...

Custom Permissions (6):
[sewing.inline_qc] CUSTOM | Granted by: admin_user | Expires: 2026-02-01
```

---

### 2. Grant Custom Permission

**When to Use:**
- Temporary access needed (e.g., QC training)
- Cross-department coverage (e.g., SPV helping other department)
- Special project access (e.g., consultant needs specific view)

**Steps:**
1. Select user from list
2. Click **[+ Grant Permission]** button
3. Select module filter (optional, helps narrow down list)
4. Choose permission from dropdown
5. Set expiration date (optional, leave empty for permanent)
6. Click **[Grant]**

**Example:**
```
User: john_doe (Operator - Cutting)
Grant: sewing.inline_qc
Reason: Cross-training for 2 weeks
Expiration: 2026-02-05
```

**Result:**
- User gains permission immediately
- Green badge appears in Custom Permissions section
- Shows "Expires in X days" indicator
- Audit log created automatically

---

### 3. Revoke Custom Permission

**When to Use:**
- Training period ended
- Project completed
- Security concern
- Permission no longer needed

**Steps:**
1. Select user from list
2. Find permission in **Custom Permissions** section
3. Click **[❌]** button on right side of badge
4. Confirm revocation

**Important:**
- ⚠️ Cannot revoke role-based permissions (by design)
- ⚠️ Only custom permissions can be revoked
- ✅ Change takes effect immediately
- ✅ Audit log created automatically

---

### 4. Search for Users

**Search by:**
- Username (e.g., "john_doe")
- Email (e.g., "john@example.com")
- Role (e.g., "OPERATOR")

**Real-time filtering:**
Type in search box → Results filter instantly

---

## 📋 Permission Code Structure

### Format
```
module.action
```

### Examples
```
admin.manage_users          - Create/edit/delete users
admin.view_system_info      - View system info (read-only)
cutting.allocate_material   - Start cutting operation
cutting.complete_operation  - Complete cutting work order
sewing.inline_qc           - Perform QC inspection (QC Inspector)
sewing.create_transfer     - Transfer to next department
finishing.metal_detector_qc - Run metal detector test (IKEA compliance)
finishing.convert_to_fg    - Convert WIP to Finished Goods
packing.label_carton       - Generate carton labels
ppic.approve_mo            - Approve Manufacturing Order (Manager only)
```

### Module List
```
admin       - System administration
dashboard   - Dashboard access
cutting     - Cutting department
sewing      - Sewing department
finishing   - Finishing department
packing     - Packing department
ppic        - PPIC/Manufacturing Orders
warehouse   - Warehouse operations
purchasing  - Purchasing module
qc          - Quality Control
```

---

## 🎨 UI Elements Guide

### Permission Badges

#### Color Coding
```
🟣 Purple  - admin.*
🔵 Blue    - dashboard.*
🟠 Orange  - cutting.*
🩷 Pink    - sewing.*
🟢 Green   - finishing.*
🟡 Yellow  - packing.*
🟣 Indigo  - ppic.*
⚪ Gray    - warehouse.*
🔵 Cyan    - purchasing.*
🔴 Red     - qc.*
```

#### Badge Types

**Role Permission:**
```
[🛡️ cutting.view_status]
```
- Purple/module color background
- Shield icon
- No CUSTOM label
- Cannot be revoked

**Custom Permission (Active):**
```
[✅ sewing.inline_qc] CUSTOM | 🗓️ Expires: 2026-02-01
```
- Green background
- CUSTOM label
- Calendar icon if expires
- Can be revoked (❌ button)

**Expired Permission:**
```
[⚠️ cutting.allocate_material] CUSTOM | Expired
```
- Gray background
- Alert icon
- Strikethrough text
- Can be revoked (cleanup)

---

## 🔍 Troubleshooting

### Issue: "Access Denied" page

**Cause:** User lacks `admin.view_system_info` permission

**Solution:**
1. Request admin to grant `admin.view_system_info`
2. Or use admin account
3. Check role assignment (only ADMIN/MANAGER should have this)

---

### Issue: [+ Grant Permission] button not visible

**Cause:** User lacks `admin.manage_users` permission

**Solution:**
- You have view-only access
- Request full admin account if you need to grant permissions
- This is by design (security separation)

---

### Issue: Can't revoke role permission

**Cause:** Role permissions cannot be revoked individually

**Explanation:**
Role permissions come from user's role definition (e.g., OPERATOR role has 20 permissions). To revoke role permissions, you must:
1. Change user's role (in User Management page)
2. Or grant a different role
3. Role permissions = inherited, not individually controlled

**Only custom permissions can be revoked.**

---

### Issue: Permission granted but not working

**Checklist:**
1. ✅ User logged out and back in? (permission cache refresh)
2. ✅ Permission not expired? (check expiration date)
3. ✅ Correct permission code? (check spelling)
4. ✅ Permission exists in database? (backend seeding issue)
5. ✅ Backend API working? (check network tab)

**Solution:**
- Have user logout and login again
- Check browser console for errors
- Verify backend API responds correctly: `GET /auth/permissions`

---

### Issue: Permission expired but still showing

**Cause:** Frontend cache not updated

**Solution:**
1. User logout and login
2. Or refresh page (F5)
3. Backend will enforce expiration regardless of UI display

---

## 📊 Audit & Reporting

### Audit Trail Location
`/admin/audit-trail` (separate page)

### What's Logged
```
Action: GRANT_PERMISSION
User: admin_user (ID: 1)
Target: john_doe (ID: 42)
Permission: sewing.inline_qc
Expiration: 2026-02-01
IP: 192.168.1.100
Timestamp: 2026-01-21 14:30:25
```

### Common Queries

**Who granted permission X to user Y?**
→ Check audit trail, filter by `GRANT_PERMISSION` action

**When will user's custom permissions expire?**
→ View user in Permission Management, check 🗓️ dates

**How many custom permissions are active?**
→ Check "Custom" statistics card for selected user

---

## 🔐 Security Best Practices

### 1. Use Expiration Dates
**✅ Good:**
```
Grant: sewing.inline_qc
Expires: 2026-02-15 (2 weeks training)
```

**❌ Bad:**
```
Grant: sewing.inline_qc
Expires: (empty) = permanent
```

**Why:** Temporary access should have expiration to prevent permission creep.

---

### 2. Principle of Least Privilege
**✅ Good:**
Grant only the specific permission needed:
```
User needs to view QC reports only
→ Grant: qc.view_reports
```

**❌ Bad:**
Grant broad access:
```
User needs to view QC reports
→ Grant: qc.* (all QC permissions)
```

---

### 3. Regular Audits
**Schedule:**
- Weekly: Review custom permissions
- Monthly: Review expired permissions (cleanup)
- Quarterly: Review role permissions (adjust role definitions)

**Checklist:**
- [ ] Users with expired permissions → Revoke
- [ ] Users who left company → Deactivate account
- [ ] Custom permissions still needed? → Renew or revoke
- [ ] Any suspicious grants? → Investigate

---

### 4. Document Custom Grants
**Best Practice:**
When granting custom permission, note reason:
```
User: john_doe
Permission: finishing.convert_to_fg
Reason: Covering for Jane (on leave 2026-01-20 to 2026-02-05)
Expires: 2026-02-06
Granted by: admin_user
```

Keep external documentation (e.g., Confluence, wiki) for audit purposes.

---

## 🛠️ Developer Notes

### Backend API Endpoints

#### Get User Permissions
```bash
GET /admin/users/{userId}/permissions
Authorization: Bearer <token>

Response:
{
  "user": { "id": 42, "username": "john_doe", ... },
  "role_permissions": ["cutting.view_status", "cutting.allocate_material", ...],
  "custom_permissions": [
    {
      "permission_code": "sewing.inline_qc",
      "granted_by_username": "admin_user",
      "granted_at": "2026-01-20T14:30:00",
      "expires_at": "2026-02-01T00:00:00"
    }
  ],
  "effective_permissions": [...]
}
```

#### Grant Permission
```bash
POST /admin/users/{userId}/permissions
Authorization: Bearer <token>
Content-Type: application/json

Body:
{
  "permission_code": "sewing.inline_qc",
  "expires_at": "2026-02-01T00:00:00"  # Optional, null = permanent
}

Response: 201 Created
{
  "message": "Permission granted successfully",
  "permission": { ... }
}
```

#### Revoke Permission
```bash
DELETE /admin/users/{userId}/permissions/{permissionCode}
Authorization: Bearer <token>

Response: 200 OK
{
  "message": "Permission revoked successfully"
}
```

#### List All Permissions
```bash
GET /admin/permissions
Authorization: Bearer <token>

Response:
[
  {
    "id": 1,
    "code": "admin.manage_users",
    "name": "Manage Users",
    "description": "Create, edit, and delete user accounts",
    "module": "admin",
    "category": "administration"
  },
  ...
]
```

---

### Frontend Components

#### usePermission Hook
```tsx
import { usePermission } from '@/hooks/usePermission'

const MyComponent = () => {
  const canEdit = usePermission('admin.manage_users')
  
  return (
    <div>
      {canEdit && <button>Edit User</button>}
    </div>
  )
}
```

#### PermissionBadge Component
```tsx
import { PermissionBadge } from '@/components/PermissionBadge'

<PermissionBadge
  code="cutting.allocate_material"
  source="role"
  size="md"
  showIcon={true}
/>

<PermissionBadge
  code="sewing.inline_qc"
  source="custom"
  expiresAt="2026-02-01T00:00:00"
  description="Perform inline QC inspection during sewing"
  size="sm"
/>
```

#### PermissionBadgeList Component
```tsx
import { PermissionBadgeList } from '@/components/PermissionBadge'

<PermissionBadgeList
  permissions={[
    { code: 'cutting.view_status', source: 'role' },
    { code: 'sewing.inline_qc', source: 'custom', expiresAt: '2026-02-01' }
  ]}
  columns={2}
  size="sm"
/>
```

---

## 📞 Support

### For Issues
1. Check this guide first
2. Check browser console for errors
3. Check network tab for API errors
4. Contact: IT Support or System Administrator

### For Feature Requests
- Permission Management enhancement ideas
- New permission codes needed
- UI improvements
- Report issues via: [Your issue tracking system]

---

## 📚 Related Documentation

1. **Session 13.5 Completion Report:** `docs/SESSION_13.5_DAY3_COMPLETION.md`
2. **Week 4 Progress Report:** `docs/WEEK4_PROGRESS_REPORT.md`
3. **Backend PBAC Guide:** Week 3 documentation
4. **Frontend Hook Guide:** Session 13.3 (Day 1)
5. **User Management Guide:** Admin section

---

**Quick Reference Version:** 1.0  
**Last Updated:** 2026-01-21  
**Maintained By:** Development Team  
**Status:** 🟢 Production Ready (after Day 5 testing)
