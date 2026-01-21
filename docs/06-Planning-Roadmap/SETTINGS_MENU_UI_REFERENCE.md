# 🎨 SETTINGS MENU - VISUAL REFERENCE & USER JOURNEYS

**Date**: January 21, 2026  
**Version**: 1.0

---

## 📱 SETTINGS MENU LAYOUT (Desktop & Mobile)

### **Desktop View - Left Sidebar Navigation**

```
┌──────────────────────────────────────────────┐
│ ⚙️  SETTINGS & ADMINISTRATION                │
├──────────────────────────────────────────────┤
│                                               │
│ 👤 ACCOUNT (Collapse/Expand)                 │
│ ├─ 🔐 Change Password             →         │
│ ├─ 🌍 Language & Timezone          →        │
│ ├─ 🔔 Notifications                →        │
│ └─ 🎨 Display Preferences          →        │
│                                               │
│ 👥 USER MANAGEMENT (Admin)                   │
│ ├─ 🔑 Portal Users                 →        │
│ ├─ 🛡️ Access Control                →       │
│ ├─ ⚙️ User Permissions             →        │
│ └─ 💬 Channels                     →        │
│                                               │
│ 🏢 COMPANY SETTINGS (Admin)                  │
│ ├─ 📧 Email Configuration          →        │
│ ├─ 📄 Document Templates           →        │
│ ├─ ✍️ Signatures                   →        │
│ └─ 🏢 Multi-Company                →        │
│                                               │
│ 🔒 SECURITY (Admin)                         │
│ ├─ 🔐 Security Settings            →        │
│ ├─ 💾 Database Management          →        │
│ ├─ 📊 Audit Logs                   →        │
│ └─ 📋 Compliance                   →        │
│                                               │
└──────────────────────────────────────────────┘
```

---

## 🔐 USER JOURNEY: CHANGE PASSWORD

### **Step 1: Navigate to Settings**
```
Dashboard → (Avatar) ⬇️ → "Settings" → "Account" → "Change Password"
```

### **Screen: Change Password Form**
```
┌─────────────────────────────────────────────────┐
│ ← SETTINGS > ACCOUNT > CHANGE PASSWORD          │
├─────────────────────────────────────────────────┤
│                                                  │
│ Current Password *                              │
│ [________________]                              │
│ Forgot password?                                │
│                                                  │
│ New Password *                                  │
│ [________________]                              │
│ ✓ Uppercase letter (A-Z)                       │
│ ✓ Lowercase letter (a-z)                       │
│ ✓ Number (0-9)                                 │
│ ✗ Special character (!@#$%)                    │
│ ✓ At least 8 characters                        │
│                                                  │
│ Confirm Password *                              │
│ [________________]                              │
│                                                  │
│ [ Cancel ]              [ Save Changes ]        │
│                                                  │
│ Last changed: 45 days ago                       │
└─────────────────────────────────────────────────┘
```

### **Email Confirmation (Async)**
```
From: system@qutykarunia.com
To: user@company.com
Subject: Password Changed Successfully ✓

Your password was successfully changed on Jan 21, 2026 at 14:30 WIB
from IP: 192.168.1.100

If this wasn't you, click here to undo: [UNDO LINK]

Questions? Contact support@qutykarunia.com
```

---

## 🌍 USER JOURNEY: CUSTOMIZE LANGUAGE & TIMEZONE

### **Step 1: Navigate to Settings**
```
Settings → Account → Language & Timezone
```

### **Screen: Language & Regional Settings**
```
┌──────────────────────────────────────────────────┐
│ ← SETTINGS > ACCOUNT > LANGUAGE & TIMEZONE       │
├──────────────────────────────────────────────────┤
│                                                   │
│ 🌍 LANGUAGE & REGIONAL SETTINGS                 │
│                                                   │
│ Language (Display)                               │
│ [  🇮🇩 Bahasa Indonesia  ▼ ]                    │
│    • Bahasa Indonesia (default)                  │
│    • English                                     │
│    • (Expandable for future)                     │
│                                                   │
│ Timezone (for timestamps & scheduling)           │
│ [  🕐 WIB (UTC+7) - Jakarta  ▼ ]                │
│    • WIB (Waktu Indonesia Barat) - UTC+7        │
│    • WITA (Waktu Indonesia Tengah) - UTC+8      │
│    • WIT (Waktu Indonesia Timur) - UTC+9        │
│    • UTC (International)                         │
│                                                   │
│ Date Format                                      │
│ [  DD/MM/YYYY  ▼ ]                              │
│    • DD/MM/YYYY (21/01/2026)                    │
│    • MM/DD/YYYY (01/21/2026)                    │
│    • YYYY-MM-DD (2026-01-21)                    │
│                                                   │
│ Time Format                                      │
│ [  24-hour (14:30) ▼ ]                          │
│    • 24-hour (14:30)                            │
│    • 12-hour (02:30 PM)                         │
│                                                   │
│ Number Format                                    │
│ [  1.234,56  ▼ ]                                │
│    • 1.234,56 (European)                        │
│    • 1,234.56 (US)                              │
│                                                   │
│ Currency Display                                 │
│ [  IDR (Rp)  ▼ ]                                │
│    • IDR (Rp) - Indonesian Rupiah               │
│    • USD ($) - US Dollar                        │
│    • EUR (€) - Euro                             │
│                                                   │
│ Preview: 21 Januari 2026, 14:30 WIB             │
│          Amount: Rp 1.234,56                     │
│                                                   │
│ [ Cancel ]                  [ Save Changes ]     │
│                                                   │
└──────────────────────────────────────────────────┘
```

---

## 🛡️ ADMIN JOURNEY: GRANT USER ACCESS

### **Step 1: Navigate to User Management**
```
Settings → User Management → Access Control
```

### **Screen: User Access Control**
```
┌────────────────────────────────────────────────────┐
│ ← SETTINGS > USER MANAGEMENT > ACCESS CONTROL      │
├────────────────────────────────────────────────────┤
│                                                     │
│ Search: [________________]  [+ Add User]           │
│                                                     │
│ ┌─────────────────────────────────────────────┐   │
│ │ User Name      │ Role        │ Modules   │ ✎ │ │
│ ├─────────────────────────────────────────────┤   │
│ │ Ahmad Sutrisno │ Manager     │ 8/12  ⚠️ │ ✎ │ │
│ │ Siti Rahayu    │ Supervisor  │ 5/12      │ ✎ │ │
│ │ Budi Santoso   │ Operator    │ 3/12      │ ✎ │ │
│ │ Eka Putra      │ Viewer      │ 2/12      │ ✎ │ │
│ └─────────────────────────────────────────────┘   │
│                                                     │
└────────────────────────────────────────────────────┘
```

### **Step 2: Edit User (Click ✎)**
```
┌──────────────────────────────────────────────────────┐
│ EDIT USER: Ahmad Sutrisno (Manager)                  │
├──────────────────────────────────────────────────────┤
│                                                       │
│ Basic Info:                                          │
│ • Name: Ahmad Sutrisno                               │
│ • Email: ahmad.sutrisno@qutykarunia.com              │
│ • Role: [Manager ▼]                                  │
│   - Superadmin, Manager, Supervisor, Operator, Viewer
│                                                       │
│ Module Access:                                       │
│ ☑️ Dashboard (View, Create Reports)                 │
│ ☑️ Cutting (View, Edit SPK)                         │
│ ☑️ Embroidery (View, Record Output)                 │
│ ☑️ Sewing (View, Record Output)                     │
│ ☑️ Finishing (View, Record Output)                  │
│ ☑️ Packing (View, Create Shipping)                  │
│ ☐ Warehouse (View Stock, Edit Stock)                │
│ ☑️ Quality (View Tests, Create Tests)               │
│ ☑️ Purchasing (View PO, Approve PO)                 │
│ ☑️ Sales (View SO, Create SO)                       │
│ ☐ Administration (Manage Users)                     │
│ ☐ Reporting (View, Export, Create Custom)           │
│                                                       │
│ Advanced Permissions:                                │
│ ☑️ View Prices                                       │
│ ☐ Override Prices                                    │
│ ☐ View Costs                                         │
│ ☐ Update Costs                                       │
│ ☑️ Create Discounts (Line Level)                    │
│ ☐ Modify MPS                                         │
│ ☑️ Multi-Currency Access                            │
│ ☐ Modify Scrap Location                             │
│                                                       │
│ [ Cancel ]                    [ Save Changes ]       │
│ [ Revoke Access ]             [ Force Logout ]       │
│                                                       │
└──────────────────────────────────────────────────────┘
```

---

## 📧 ADMIN JOURNEY: CONFIGURE EMAIL

### **Screen: Email Configuration**
```
┌────────────────────────────────────────────────────┐
│ ← SETTINGS > COMPANY > EMAIL CONFIGURATION         │
├────────────────────────────────────────────────────┤
│                                                     │
│ 📤 OUTGOING EMAIL (SMTP)                           │
│                                                     │
│ SMTP Server Address *                              │
│ [smtp.gmail.com________________]                   │
│                                                     │
│ SMTP Port *                                        │
│ [587__]  (587, 465, 25)                            │
│                                                     │
│ Sender Email Address *                             │
│ [system@qutykarunia.com________]                   │
│                                                     │
│ Sender Name *                                      │
│ [PT Quty Karunia ERP System____]                   │
│                                                     │
│ Username *                                         │
│ [system@qutykarunia.com________]                   │
│                                                     │
│ Password *                                         │
│ [••••••••••]  (Encrypted)                          │
│                                                     │
│ ☑️ Use TLS/SSL Encryption                          │
│                                                     │
│ [ Test Email ]  (Sends test to your email)         │
│                                                     │
│ ─────────────────────────────────────────────────  │
│                                                     │
│ 📥 INCOMING EMAIL (IMAP)                           │
│                                                     │
│ IMAP Server Address *                              │
│ [imap.gmail.com________________]                   │
│                                                     │
│ IMAP Port *                                        │
│ [993__]  (993, 143)                                │
│                                                     │
│ Email Account *                                    │
│ [system@qutykarunia.com________]                   │
│                                                     │
│ Password *                                         │
│ [••••••••••]  (Encrypted)                          │
│                                                     │
│ Auto-Sync Interval                                 │
│ [Every 5 minutes ▼]                                │
│                                                     │
│ ☑️ Use TLS/SSL Encryption                          │
│                                                     │
│ [ Cancel ]                [ Save & Test ]          │
│                                                     │
└────────────────────────────────────────────────────┘
```

---

## 📄 ADMIN JOURNEY: CUSTOMIZE DOCUMENT TEMPLATE

### **Screen: Document Template Builder**
```
┌──────────────────────────────────────────────────────┐
│ ← SETTINGS > COMPANY > DOCUMENT TEMPLATES            │
├──────────────────────────────────────────────────────┤
│                                                       │
│ [+ New Template]  [View All]  [Import]  [Export]     │
│                                                       │
│ ┌────────────────────────────────────────────────┐  │
│ │ Template Name: Invoice EN (v2)                 │  │
│ │ Document Type: [Invoice ▼]                     │  │
│ │ Language: [English ▼]                          │  │
│ │ Status: [Active ▼]                             │  │
│ │ Version: 2                                      │  │
│ └────────────────────────────────────────────────┘  │
│                                                       │
│ LAYOUT BUILDER (Drag & Drop)                         │
│                                                       │
│ ┌─ TOOLBAR ───────────────────────────────────────┐ │
│ │ [Logo] [Text] [Image] [Table] [Barcode] [QR]   │ │
│ │ [Line] [Shape] [Field] [Calculation]           │ │
│ └──────────────────────────────────────────────────┘ │
│                                                       │
│ ┌────── TEMPLATE PREVIEW ──────────────────────────┐ │
│ │                                                  │ │
│ │  [🏢 LOGO]     PT QUTY KARUNIA                  │ │
│ │                INVOICE                          │ │
│ │  Invoice #: [AUTO-FIELD]                        │ │
│ │  Date: [AUTO-DATE]                              │ │
│ │                                                  │ │
│ │  Bill To:                                       │ │
│ │  [CUSTOMER-NAME]                                │ │
│ │  [ADDRESS]                                      │ │
│ │                                                  │ │
│ │  ┌─────┬────────────┬─────┬──────┐             │ │
│ │  │ No. │ Description│ Qty │ Price│             │ │
│ │  ├─────┼────────────┼─────┼──────┤             │ │
│ │  │ 1   │ [ITEM]     │ [Q] │ [P]  │             │ │
│ │  │ 2   │ [ITEM]     │ [Q] │ [P]  │             │ │
│ │  │ 3   │ [ITEM]     │ [Q] │ [P]  │             │ │
│ │  └─────┴────────────┴─────┴──────┘             │ │
│ │                                                  │ │
│ │  Subtotal: [CALC-SUM]                          │ │
│ │  Tax (10%): [CALC-TAX]                         │ │
│ │  Total: [CALC-TOTAL]                           │ │
│ │                                                  │ │
│ │  Signature: ___________  Date: ___________      │ │
│ │                                                  │ │
│ └──────────────────────────────────────────────────┘ │
│                                                       │
│ [ Preview ]  [ Cancel ]              [ Save Template ]
│                                                       │
└──────────────────────────────────────────────────────┘
```

---

## 🔒 ADMIN JOURNEY: SECURITY SETTINGS

### **Screen: Security Configuration**
```
┌──────────────────────────────────────────────────┐
│ ← SETTINGS > SECURITY > SECURITY SETTINGS        │
├──────────────────────────────────────────────────┤
│                                                   │
│ AUTHENTICATION                                    │
│                                                   │
│ ☑️ Require Two-Factor Authentication (2FA)       │
│ ☐ Require Hardware Security Key                  │
│                                                   │
│ Session Timeout (minutes)                        │
│ [30] minutes of inactivity                       │
│                                                   │
│ Maximum Failed Logins                            │
│ [5] attempts before lockout                      │
│                                                   │
│ Account Lockout Duration (minutes)               │
│ [15] minutes                                     │
│                                                   │
│ Password Expiration (days)                       │
│ [90] days (0 = never)                            │
│                                                   │
│ ─────────────────────────────────────────────────│
│                                                   │
│ AUTHORIZATION                                     │
│                                                   │
│ IP Whitelist (optional)                          │
│ [192.168.1.0/24____________]                     │
│ [203.0.113.0/24____________]                     │
│ [+ Add IP Range]                                 │
│                                                   │
│ IP Blacklist (optional)                          │
│ [10.0.0.0/8________________]                     │
│ [+ Add IP Range]                                 │
│                                                   │
│ ☑️ Require VPN Connection                        │
│ ☐ Require Specific Geolocation                   │
│                                                   │
│ ─────────────────────────────────────────────────│
│                                                   │
│ DATA ENCRYPTION                                   │
│                                                   │
│ ☑️ Encrypt Data at Rest (Database)               │
│ ☑️ Enforce HTTPS/SSL (In Transit)                │
│ ☑️ Mask Sensitive Data in Logs                   │
│                                                   │
│ API Key Rotation (days)                          │
│ [90] days                                        │
│                                                   │
│ ─────────────────────────────────────────────────│
│                                                   │
│ AUDIT & COMPLIANCE                                │
│                                                   │
│ ☑️ Enable Detailed Audit Logging                 │
│ Audit Log Retention (days)                       │
│ [365] days (0 = forever)                         │
│                                                   │
│ [ Export Audit Logs ]                            │
│ [ Generate Compliance Report ]                   │
│                                                   │
│ ─────────────────────────────────────────────────│
│                                                   │
│ Recent Suspicious Activities                      │
│ • Failed login: 203.0.113.15 - 10 min ago       │
│ • Unusual data access: User ID 42 - 1 hour ago  │
│                                                   │
│ [ Cancel ]                   [ Save Changes ]    │
│                                                   │
└──────────────────────────────────────────────────┘
```

---

## 📊 MOBILE VIEW - RESPONSIVE DESIGN

### **Mobile Settings Menu (iPhone)**
```
┌─────────────────────────┐
│ ⚙️ Settings    ≡ Menu   │
├─────────────────────────┤
│                          │
│ 👤 Account               │
│ ├─ 🔐 Change Password   │
│ ├─ 🌍 Language          │
│ ├─ 🔔 Notifications     │
│ └─ 🎨 Theme             │
│                          │
│ 👥 Manage Users    ✓     │
│ 📊 Company Setup   ✓     │
│ 🔒 Security        ✓     │
│                          │
│ [ Help ]  [ About ]  [ ]│
│                          │
└─────────────────────────┘
```

### **Responsive Change Password (Mobile)**
```
┌──────────────────────────────┐
│ ← Change Password            │
├──────────────────────────────┤
│                               │
│ Current Password             │
│ [________________]           │
│ Forgot?                      │
│                               │
│ New Password                 │
│ [________________]           │
│                               │
│ ✓ Uppercase (A-Z)            │
│ ✗ Number (0-9)               │
│ ✓ Special (!@#$)             │
│ ✓ 8 characters               │
│                               │
│ Confirm Password             │
│ [________________]           │
│                               │
│ ┌──────────────────────────┐ │
│ │     [ Save Changes ]     │ │
│ └──────────────────────────┘ │
│                               │
│          Last changed:        │
│          45 days ago          │
│                               │
└──────────────────────────────┘
```

---

## ✨ KEY UI/UX FEATURES

### **1. Consistency**
- Same design system across all settings pages
- Consistent button placement (Cancel | Save)
- Consistent form field patterns

### **2. Accessibility**
- Large touch targets for mobile (44px minimum)
- Clear visual hierarchy
- Error messages in red, success in green
- Support for dark mode

### **3. Feedback**
- Save confirmation messages
- Loading spinners for async operations
- Email confirmations for critical changes
- Audit trail visible in UI

### **4. Discoverability**
- Breadcrumb navigation (Settings > Account > Language)
- Search functionality
- Help icons (?) with tooltips
- Quick access to most-used settings

### **5. Safety**
- Confirmation dialogs for destructive actions
- "Are you sure?" prompts
- Undo options where possible
- Changes logged to audit trail

---

**Last Updated**: January 21, 2026  
**Status**: ✅ Complete

