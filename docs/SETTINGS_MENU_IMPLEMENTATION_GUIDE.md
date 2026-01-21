# ⚙️ SETTINGS & ADMINISTRATION MENU - IMPLEMENTATION GUIDE

**Document Version**: 1.0  
**Date Created**: January 21, 2026  
**Status**: ✅ Added to Project.md  
**Author**: Development Team

---

## 📋 OVERVIEW

A comprehensive Settings & Administration menu system has been added to support granular user management and system configuration. The system differentiates between:

- **User Settings** (All users can modify personal settings)
- **Administration Settings** (SuperAdmin only)

---

## 🎯 MAIN SETTINGS MENU STRUCTURE

### **12 Primary Menu Items**

```
⚙️ SETTINGS & ADMINISTRATION
│
├─ 📋 MY SETTINGS (All Users)
│  ├─ 🔐 Change Password
│  ├─ 🌍 Language & Timezone Settings  
│  ├─ 🔔 Notification Preferences
│  └─ 🎨 Display Preferences
│
├─ 👥 USER & ACCESS MANAGEMENT (SuperAdmin)
│  ├─ 🔑 Portal User Access
│  ├─ 🛡️ User Access Control & Permissions
│  ├─ 💬 Channel Discussion
│  └─ ⚙️ Technical User Settings (Per Module)
│
├─ 📊 COMPANY SETTINGS (SuperAdmin)
│  ├─ 🏢 Multi-Company Management
│  ├─ 📧 Email Configuration (Incoming & Outgoing)
│  ├─ 📄 Document Templates & Layout
│  └─ ✍️ Electronic Signatures
│
└─ 🔒 SYSTEM SECURITY (SuperAdmin)
   ├─ 🔐 Security Settings
   ├─ 💾 Database Management
   └─ 📋 Audit Logs & Compliance
```

---

## 📑 DETAILED MENU ITEMS

### **1. Portal User Access** 🔑
- Grant access to external users (suppliers, partners)
- Portal users can monitor Sales Orders & Purchase Orders
- Email-based invitations
- Permission levels: View-only, Edit, Approve
- Real-time dashboard access for portal users

### **2. User Password Management** 🔐
- Change own password (all users)
- Reset password for other users (SuperAdmin)
- Email-based password reset links
- Temporary password generation
- Password complexity enforcement
- Password history tracking (last 5)

### **3. User Timezone & Language** 🌍
- Language: Indonesian, English (expandable)
- Timezone: WIB, WITA, WIT, UTC
- Date format customization
- Time format (12-hour or 24-hour)
- Currency & number format preferences

### **4. User Access Control** 🛡️
- Role-based access assignment (Superadmin, Manager, Supervisor, Operator, Viewer)
- Module-level access control
- View-only vs Edit permissions
- Temporary access granting (time-limited)
- Comprehensive access audit trail

### **5. Electronic Signature** ✍️
- Upload digital signature images
- Configure signature placement on documents
- Multi-level approval signatures
- Timestamped signatures (compliance-ready)
- Signature verification & audit trail
- Apply to Invoice, Delivery Slip, PO, etc.

### **6. Email Configuration** 📧

**Outgoing (SMTP)**:
- SMTP server configuration
- Port settings (587, 465, 25)
- TLS/SSL encryption
- Email sender configuration
- Test email functionality
- Email template management

**Incoming (IMAP/POP3)**:
- IMAP/POP3 server setup
- Auto-sync interval
- Folder mapping
- Email archive settings
- Spam filtering

### **7. Channel Discussion** 💬
- Department-level discussion channels (#cutting, #sewing, etc.)
- Channel membership control
- Pinned messages for announcements
- File sharing
- Message threading & search
- Auto-archive old channels

### **8. Technical User Settings** ⚙️
- Module-level granular permissions:
  - Dashboard, Cutting, Embroidery, Sewing, Finishing, Packing
  - Warehouse, Quality, Purchasing, Sales, Reporting, Admin
- Feature-level access (override validation, view cost, etc.)
- API token management
- Database query access (filtered, read-only)

### **9. Database Management** 💾
- Manual & automatic backup
- Full/incremental backup options
- Database restoration
- Database duplication/cloning
- Master encryption password management
- Database maintenance & optimization
- Connection monitoring

### **10. Security Settings** 🔒
- Two-factor authentication (2FA) configuration
- Session timeout settings
- IP whitelist/blacklist
- VPN requirements
- Data encryption at rest & in transit
- API key rotation policies
- Audit logging configuration

### **11. Multi-Company Management** 🏢
- Create/edit company entities
- Company-level settings (currency, fiscal year, language)
- User assignment to multiple companies
- Company data isolation
- Inter-company transaction support
- Consolidated reporting
- Company-specific approval workflows

### **12. Document Templates** 📄
- WYSIWYG template builder
- Support for Invoice, PO, Delivery Slip, Quotation, Reports
- Drag-and-drop layout customization
- Branding (logo, header, footer)
- Conditional formatting
- Multiple language templates
- PDF/Excel/Print export

---

## 🔐 ADDITIONAL ACCESS PERMISSIONS (13 Items)

| # | Permission | Description | Default Role |
|---|-----------|-------------|--------------|
| 1 | **Overwrite Price** | Override system-suggested prices | Sales Manager |
| 2 | **Show Non-Valuation Inventory** | Display unvalued inventory | Finance Manager |
| 3 | **Show Cost** | View product costs | Finance, Manager |
| 4 | **Show Price** | View selling prices | Manager, Operator |
| 5 | **Show & Modify Scrap Location** | Manage inventory loss locations | Warehouse Manager |
| 6 | **Update Cost** | Modify cost basis methods | Finance Manager |
| 7 | **Calendar Access** | Access production scheduling | PPIC, Manager |
| 8 | **Employee Access** | Manage employee data | HR Manager |
| 9 | **Multi-Company Support** | Work with multiple entities | Director |
| 10 | **Modify MPS** | Edit Master Production Schedule | PPIC Manager |
| 11 | **Multi-Currency** | Work with multiple currencies | Finance Manager |
| 12 | **Sales Report Access** | View sales analytics | Sales Manager |
| 13 | **Discount on Lines** | Apply line-level discounts | Sales Manager |

---

## 💾 DATABASE SCHEMA

### **Core Tables**

```sql
-- User Settings
user_settings (
  id, user_id, timezone, language, date_format, 
  time_format, currency, theme, notifications, email_digest
)

-- Advanced Permissions
user_advanced_permissions (
  id, user_id, can_overwrite_price, can_view_cost,
  can_update_cost, can_modify_mps, can_apply_discount, ...
)

-- Email Configuration
email_configuration (
  id, company_id, email_type, smtp_server, imap_server,
  smtp_port, sender_name, sender_address
)

-- Document Templates
document_templates (
  id, company_id, template_name, document_type,
  template_json, is_active, version, created_by
)

-- Portal Users
portal_users (
  id, email, company_id, access_level, created_at
)

-- Settings Audit
settings_audit_log (
  id, user_id, setting_name, old_value, new_value, changed_at
)
```

---

## 🚀 IMPLEMENTATION ROADMAP

### **Phase 1: User Settings (Week 1-2)**
- [ ] User password management
- [ ] Language & timezone settings
- [ ] User profile preferences

### **Phase 2: Access Control (Week 2-3)**
- [ ] Portal user management
- [ ] User access control & permissions
- [ ] Technical user settings

### **Phase 3: Company Settings (Week 3-4)**
- [ ] Email configuration
- [ ] Document templates
- [ ] Electronic signatures
- [ ] Multi-company management

### **Phase 4: Security & Admin (Week 4-5)**
- [ ] Database management
- [ ] Security settings
- [ ] Audit logging
- [ ] Channel discussion system

### **Phase 5: Testing & Deployment (Week 5-6)**
- [ ] Unit tests (80%+ coverage)
- [ ] Integration tests
- [ ] UAT
- [ ] Production deployment

---

## 🎯 ESTIMATED EFFORT

| Component | Hours | Priority |
|-----------|-------|----------|
| User Settings | 16 | ⭐⭐⭐ |
| Access Control | 24 | ⭐⭐⭐ |
| Email Configuration | 12 | ⭐⭐⭐ |
| Document Templates | 20 | ⭐⭐ |
| Database Management | 16 | ⭐⭐ |
| Security Settings | 12 | ⭐⭐ |
| Multi-Company | 20 | ⭐⭐ |
| Portal Users | 12 | ⭐ |
| Channel Discussion | 16 | ⭐ |
| **TOTAL** | **~150 hours** | |

**Timeline**: 5-6 weeks (with 1 developer + 1 AI)

---

## 📊 SUCCESS METRICS

- ✅ All 12 menu items fully functional
- ✅ 13 additional permissions configurable
- ✅ 80%+ test coverage
- ✅ <2 second settings page load time
- ✅ Zero security vulnerabilities
- ✅ >95% uptime
- ✅ Audit trail 100% complete

---

## 🔗 INTEGRATION POINTS

- **Authentication**: OAuth, JWT tokens
- **Authorization**: RBAC with role inheritance
- **Email Service**: SMTP/IMAP integration
- **Database**: PostgreSQL with encryption
- **Frontend**: React settings UI
- **API**: RESTful endpoints for all settings

---

**Status**: ✅ Ready for Implementation  
**Last Updated**: January 21, 2026

