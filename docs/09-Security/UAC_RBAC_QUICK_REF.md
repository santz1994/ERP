# UAC/RBAC Quick Reference
## 20 Roles - 5-Level Hierarchy

**Last Updated**: 2026-01-20

---

## 🎯 ROLE HIERARCHY SUMMARY

```
Level 0: DEVELOPER             (1 user)  🔐 Full System + Code
Level 1: SUPERADMIN            (1 user)  👑 User Management + System Config
Level 2: MANAGER               (2 users) 📊 View-Only Everything
Level 3: ADMIN                 (1 user)  🛠️ Operations Admin
Level 4: Department Managers   (9 roles) 👔 Department Leadership
Level 5: Operations Staff     (11 roles) 👷 Daily Operations
```

---

## 📋 ROLE COMPARISON TABLE

| Feature | DEVELOPER | SUPERADMIN | MANAGER | ADMIN | Others |
|---------|-----------|------------|---------|-------|--------|
| **User Management** | ✅ | ✅ | ❌ | ❌ | ❌ |
| **System Settings** | ✅ | ✅ | 👁️ | ❌ | ❌ |
| **Database Access** | ✅ | ❌ | ❌ | ❌ | ❌ |
| **Code Deployment** | ✅ | ❌ | ❌ | ❌ | ❌ |
| **View All Modules** | ✅ | ✅ | ✅ | ✅ | 🔒 Limited |
| **Modify Data** | ✅ | ✅ | ❌ | ✅ | 🔒 Limited |
| **Delete Records** | ✅ | ✅ | ❌ | 🔒 Draft | ❌ |
| **Export Reports** | ✅ | ✅ | ✅ | ✅ | 🔒 Limited |
| **Override Workflows** | ✅ | ✅ | ❌ | ✅ | ❌ |

---

## 🔑 KEY DIFFERENCES

### DEVELOPER vs SUPERADMIN
**DEVELOPER**:
- ✅ Database direct access
- ✅ Code repository access
- ✅ System architecture changes
- ✅ API endpoint modification
- **Use Case**: IT Development Team

**SUPERADMIN**:
- ❌ No database direct access
- ❌ No code changes
- ✅ Application-level full control
- ✅ User & role management
- **Use Case**: System Administrator

### SUPERADMIN vs ADMIN
**SUPERADMIN**:
- ✅ Create/edit/delete users
- ✅ Assign roles to users
- ✅ System configuration (email, notifications)
- ✅ Master data setup
- **Use Case**: IT Administration

**ADMIN**:
- ❌ Cannot manage users
- ❌ Cannot change system settings
- ✅ Module configuration
- ✅ Workflow overrides (emergency)
- **Use Case**: Department/Operations Admin

### MANAGER vs Other Roles
**MANAGER**:
- 👁️ **View-Only** all modules
- ❌ **Cannot create** any data
- ❌ **Cannot modify** any data
- ❌ **Cannot delete** any records
- ✅ **Can export** all reports
- **Use Case**: Executive oversight (CEO, GM, Directors)

---

## 🛡️ SECURITY REQUIREMENTS

### Level 0-1 (DEVELOPER, SUPERADMIN)
- ✅ **Multi-Factor Authentication (MFA)** MANDATORY
- ✅ **IP Whitelist** enforcement
- ✅ **Activity Logging** with alerts
- ✅ **Session timeout**: 15 minutes
- ✅ **Audit trail** for all actions

### Level 2-3 (MANAGER, ADMIN)
- ✅ **Strong password** (12+ chars)
- ✅ **Activity logging**
- ✅ **Session timeout**: 30 minutes
- ⚠️ **MFA** recommended

### Level 4-5 (Staff & Operators)
- ✅ **Password** (8+ chars)
- ✅ **Basic activity logging**
- ✅ **Session timeout**: 60 minutes

---

## 📊 ACCESS PATTERN SUMMARY

### Who Can Create Users?
- ✅ DEVELOPER
- ✅ SUPERADMIN
- ❌ All others

### Who Can See Everything?
- ✅ DEVELOPER (Full access)
- ✅ SUPERADMIN (Full access)
- ✅ MANAGER (View-only)
- ✅ ADMIN (Operational data)
- 🔒 Others: Limited to department/role

### Who Can Delete Data?
- ✅ DEVELOPER (All with audit)
- ✅ SUPERADMIN (Users, system records)
- ✅ ADMIN (Draft records only)
- ✅ PPIC_MANAGER (Draft MOs only)
- ❌ Others: Soft delete/void only

### Who Can Export Reports?
- ✅ DEVELOPER
- ✅ SUPERADMIN
- ✅ MANAGER
- ✅ ADMIN
- ✅ PPIC_MANAGER
- ✅ PPIC_ADMIN
- ✅ Supervisors (department reports)
- ✅ QC_LAB
- ✅ WAREHOUSE_ADMIN
- ✅ PURCHASING
- 🔒 Operators: Own records only

---

## 🚀 IMPLEMENTATION CHECKLIST

### Phase 1: Core Roles (Week 1)
- [x] Add 3 new roles to backend enum
- [x] Add 3 new roles to frontend enum
- [ ] Update Sidebar menu for new roles
- [ ] Test authentication with new roles
- [ ] Create seed script for test users

### Phase 2: Access Control (Week 2)
- [ ] Implement backend role decorators
- [ ] Add frontend route guards by role
- [ ] Create MANAGER view-only middleware
- [ ] Test all permission levels

### Phase 3: User Management (Week 3)
- [ ] Build user management UI (SUPERADMIN only)
- [ ] Role assignment interface
- [ ] User activity logs
- [ ] Account suspension feature

### Phase 4: Security (Week 4)
- [ ] MFA for DEVELOPER/SUPERADMIN
- [ ] IP whitelist configuration
- [ ] Session management by role
- [ ] Audit trail dashboard

---

## 📞 QUICK CONTACT

**For Access Issues**:
- User locked: Contact SUPERADMIN
- Permission denied: Contact SUPERADMIN
- System error: Contact DEVELOPER

**For Role Assignment**:
- New user setup: SUPERADMIN
- Role change: SUPERADMIN
- Department transfer: SUPERADMIN + Manager approval

---

**Document Version**: 1.1  
**Changes**: Added DEVELOPER, SUPERADMIN, MANAGER roles  
**Next Review**: 2026-01-27
