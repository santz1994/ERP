# 🎓 WEEK 2: DEPARTMENT TRAINING GUIDE
**ERP Quty Karunia - Work Order System Training**

**Training Date**: Week 2 (11-15 Februari 2026)  
**Conducted by**: IT Developer Expert Team  
**Participants**: CUTTING, SEWING, FINISHING Departments  
**Duration**: 2 hours per department

---

## 📋 TRAINING OBJECTIVES

Setelah training ini, setiap department akan mampu:

✅ **Memahami** konsep Work Order (WO) dalam sistem ERP  
✅ **Melihat** daftar WO yang assigned ke department mereka  
✅ **Memahami** status WO (PENDING, READY, IN_PROGRESS, FINISHED)  
✅ **Melakukan** input produksi harian menggunakan WO  
✅ **Melaporkan** masalah atau shortage material

---

## 🎯 SESSION 1: INTRODUCTION TO WORK ORDERS (30 menit)

### Apa itu Work Order (WO)?

**Definisi Sederhana**:
> Work Order adalah **surat perintah kerja digital** untuk satu department, yang memberitahu:
> - **APA** yang harus diproduksi
> - **BERAPA** target quantity
> - **MATERIAL APA** yang dibutuhkan
> - **KAPAN** deadline-nya

### Perbedaan MO vs WO

| Aspek | Manufacturing Order (MO) | Work Order (WO) |
|-------|-------------------------|----------------|
| **Dibuat oleh** | PPIC | System (auto-generate) |
| **Untuk** | Semua department | Satu department saja |
| **Scope** | Finished Good (produk jadi) | WIP (Work In Progress) |
| **Jumlah** | 1 MO per order | 4-5 WO per MO |

**Contoh**:
```
MO-202602-00001: 450 pcs AFTONSPARV bear
   └─ Auto-generate 5 WOs:
      ├─ WO-CUT-001 (CUTTING)    → 495 pcs (buffer +10%)
      ├─ WO-EMB-002 (EMBROIDERY) → 495 pcs
      ├─ WO-SEW-003 (SEWING)     → 480 pcs
      ├─ WO-FIN-004 (FINISHING)  → 470 pcs
      └─ WO-PCK-005 (PACKING)    → 465 pcs
```

---

## 🖥️ SESSION 2: NAVIGATING WO SYSTEM (45 menit)

### 2.1 Login ke System

**URL**: `http://erp.qutykarunia.com` (atau IP local)

**Credentials**:
- **CUTTING**: Username `cutting_admin`, Password `cutting123`
- **SEWING**: Username `sewing_admin`, Password `sewing123`
- **FINISHING**: Username `finishing_admin`, Password `finishing123`

### 2.2 Dashboard Overview

Setelah login, Anda akan melihat:

```
┌──────────────────────────────────────────────────────┐
│  📊 DASHBOARD - CUTTING DEPARTMENT                   │
├──────────────────────────────────────────────────────┤
│  Today's Summary:                                    │
│  • Work Orders: 3 READY, 2 IN_PROGRESS               │
│  • Materials: 2 SHORTAGES (⚠️)                       │
│  • Production: 250/500 pcs completed (50%)           │
└──────────────────────────────────────────────────────┘

📋 Work Orders List

┌─────────────┬────────────┬────────┬──────────┬──────────┐
│ WO Number   │ Product    │ Target │ Status   │ Action   │
├─────────────┼────────────┼────────┼──────────┼──────────┤
│ WO-CUT-001  │ AFTONSPARV │ 495    │ READY ✅ │ [START]  │
│ WO-CUT-002  │ BLÅHAJ     │ 660    │ PENDING  │ [WAIT]   │
│ WO-CUT-003  │ GOSIG      │ 572    │ PROGRESS │ [INPUT]  │
└─────────────┴────────────┴────────┴──────────┴──────────┘
```

### 2.3 WO Status Explanation

| Status | Icon | Arti | Action yang Bisa Dilakukan |
|--------|------|------|---------------------------|
| **PENDING** | ⏳ | Menunggu department sebelumnya selesai | Tidak bisa start |
| **READY** | ✅ | Siap untuk dimulai, material tersedia | Bisa klik START |
| **IN_PROGRESS** | 🔄 | Sedang dikerjakan | Input produksi harian |
| **FINISHED** | ✔️ | Sudah selesai | Tidak ada action |
| **CANCELLED** | ❌ | Dibatalkan | - |

---

## 🔧 SESSION 3: STARTING A WORK ORDER (30 menit)

### Step-by-Step: Memulai WO

#### Step 1: Cek Material Availability

Sebelum start, pastikan material tersedia!

```
WO-CUT-001 Details:
┌──────────────────────────────────────────────────┐
│  Material Requirements:                          │
│  ✅ KOHAIR fabric: 70.4 YD (Available: 125 YD)  │
│  ✅ POLYESTER: 85.3 YD (Available: 450 YD)      │
│  ⚠️ NYLEX: 2.5 YD (Available: 1.0 YD) SHORTAGE! │
└──────────────────────────────────────────────────┘
```

**Jika ada shortage** (⚠️):
1. **Report** ke warehouse via system (klik "Report Shortage")
2. Atau hubungi warehouse via phone
3. **Jangan start WO** sampai material datang

#### Step 2: Click "START WO"

Sistem akan:
1. **Auto-deduct stock** dari warehouse (FIFO)
2. **Change status** ke IN_PROGRESS
3. **Record start date** untuk traceability

**Confirmation Dialog**:
```
┌────────────────────────────────────────────────┐
│  ⚠️ Confirm Start Work Order                   │
├────────────────────────────────────────────────┤
│  WO Number: WO-CUT-001                         │
│  Product: AFTONSPARV bear (body parts)         │
│  Target: 495 pcs                               │
│                                                │
│  Materials will be deducted from warehouse.    │
│                                                │
│  [Cancel]  [Confirm Start] ←                   │
└────────────────────────────────────────────────┘
```

#### Step 3: Production Begins!

Sekarang WO dalam status IN_PROGRESS, siap untuk input harian!

---

## 📝 SESSION 4: DAILY PRODUCTION INPUT (30 menit)

### 4.1 Input Produksi Harian

Setiap hari, operator harus input:
- ✅ **Good Output**: Berapa pcs yang bagus
- ⚠️ **Defect**: Berapa pcs yang cacat
- 🔧 **Rework**: Berapa pcs yang perlu repair

**Example Form**:

```
┌─────────────────────────────────────────────────────┐
│  📝 Daily Production Input - WO-CUT-001             │
├─────────────────────────────────────────────────────┤
│  Date: 2026-02-11                                   │
│  Shift: [ ] Morning  [✓] Afternoon  [ ] Night       │
│                                                     │
│  Good Output:     [____100____] pcs                 │
│  Defect:          [______5____] pcs                 │
│  Rework:          [______2____] pcs                 │
│                                                     │
│  Notes (optional):                                  │
│  ┌───────────────────────────────────────────────┐ │
│  │ Cutting pattern KOHAIR sulit, banyak waste   │ │
│  └───────────────────────────────────────────────┘ │
│                                                     │
│  [Cancel]  [Submit] ←                               │
└─────────────────────────────────────────────────────┘
```

**After Submit**:
```
✅ Production input saved!

Progress Update:
• Total Good: 100/495 pcs (20.2%)
• Total Defect: 5 pcs (1%)
• Remaining: 395 pcs
```

### 4.2 Defect Reporting

**Jika ada defect**, sistem akan tanya:

```
┌────────────────────────────────────────────┐
│  ⚠️ Defect Reported: 5 pcs                 │
├────────────────────────────────────────────┤
│  Defect Type:                              │
│  ( ) Cutting error                         │
│  ( ) Material defect                       │
│  (✓) Pattern mismatch                      │
│  ( ) Other                                 │
│                                            │
│  Can be reworked?                          │
│  (✓) Yes - Send to rework                 │
│  ( ) No - Scrap                            │
│                                            │
│  [Submit]                                  │
└────────────────────────────────────────────┘
```

**Sistem akan auto**:
- Create rework task (jika Yes)
- Deduct dari Good Output
- Notify QC team

---

## 🚨 SESSION 5: HANDLING ISSUES (15 menit)

### Common Issues & Solutions

#### Issue #1: Material Shortage During Production

**Scenario**: Sedang cutting, material habis di tengah jalan.

**Action**:
1. **Pause production** (jangan paksa lanjut)
2. **Report shortage** via system:
   ```
   [Report Shortage] → Material: KOHAIR → Qty needed: 20 YD
   ```
3. System akan:
   - Send alert ke warehouse
   - Send alert ke PPIC
   - Mark WO dengan "⚠️ SHORTAGE" flag
4. **Wait** sampai material datang
5. **Resume** production setelah confirmed

#### Issue #2: WO Tidak Bisa Start (Status PENDING)

**Reason**: Department sebelumnya belum selesai.

**Example**:
```
WO-SEW-003 - Status: PENDING ⏳

Waiting for: WO-CUT-001 (CUTTING)
Current status: IN_PROGRESS (60% complete)
Estimated ready: 2026-02-12
```

**Action**: **Tunggu** sampai CUTTING selesai. Tidak bisa dipaksa start.

#### Issue #3: Target Quantity Berubah

**Reason**: PPIC adjust target karena urgent order.

**System Notification**:
```
🔔 WO Target Updated!

WO-CUT-001:
• Old target: 495 pcs
• New target: 550 pcs (+55 pcs)
• Reason: Urgent order addition

Additional materials allocated:
• KOHAIR: +8.7 YD
• POLYESTER: +10.2 YD
```

**Action**: Lanjutkan production dengan target baru.

---

## 📊 SESSION 6: REPORTING & DASHBOARD (10 menit)

### What You Can See

1. **My WOs** - Semua WO department Anda
2. **Today's Progress** - Real-time production progress
3. **Material Status** - Availability & shortages
4. **Defect Rate** - Quality metrics
5. **Target vs Actual** - Performance tracking

### Daily Report Example

```
📊 CUTTING DEPARTMENT - DAILY REPORT
Date: 2026-02-11

Work Orders:
• WO-CUT-001: 100/495 pcs (20.2%) ✅
• WO-CUT-003: 572/572 pcs (100%) ✔️ FINISHED!

Production:
• Total Good Output: 672 pcs
• Total Defect: 8 pcs (1.2%)
• Efficiency: 98.8%

Materials Consumed:
• KOHAIR: 95.2 YD
• POLYESTER: 180.5 YD
• NYLEX: 10.3 YD
```

---

## 🎓 SESSION 7: Q&A & PRACTICE (20 menit)

### Practice Scenario

**Task**: Start WO-CUT-001 dan input produksi harian

**Steps**:
1. Login dengan credentials department Anda
2. Navigate ke "Work Orders" page
3. Find WO-CUT-001 (status: READY)
4. Click "View Details"
5. Check material availability (semua ✅)
6. Click "START WO"
7. Confirm
8. Navigate ke "Daily Input"
9. Input:
   - Good: 50 pcs
   - Defect: 2 pcs
   - Notes: "Test input"
10. Submit

**Expected Result**:
```
✅ Success! Production input saved.
Progress: 50/495 pcs (10.1%)
```

---

## 📝 FEEDBACK FORM

Setelah training, mohon isi feedback form:

### Training Quality (1-5 stars)

- [ ] Materi jelas & mudah dipahami: ⭐⭐⭐⭐⭐
- [ ] Sistem mudah digunakan: ⭐⭐⭐⭐⭐
- [ ] Praktek membantu: ⭐⭐⭐⭐⭐

### Issues Encountered

1. _[Your feedback here]_
2. _[Your feedback here]_
3. _[Your feedback here]_

### Improvement Requests

1. _[Your feedback here]_
2. _[Your feedback here]_

### Overall Satisfaction

- [ ] ✅ Ready to use system in production
- [ ] ⚠️ Need more practice
- [ ] ❌ Need more training

---

## 🆘 SUPPORT CONTACTS

**Technical Issues**:
- IT Support: ext. 555 atau WA: 0812-3456-7890
- Email: it@qutykarunia.com

**System Questions**:
- PPIC: ext. 100
- Production Manager: ext. 200

**Emergency**:
- Call IT hotline: 0812-3456-7890 (24/7)

---

## 📚 ADDITIONAL RESOURCES

- **User Manual**: `\\server\erp\docs\user_manual.pdf`
- **Video Tutorial**: `\\server\erp\videos\wo_training.mp4`
- **Cheat Sheet**: Attached at end of this document

---

## ✅ TRAINING COMPLETION CHECKLIST

Setelah training, peserta harus bisa:

- [ ] Login ke system
- [ ] View daftar WO department mereka
- [ ] Understand WO status (PENDING, READY, IN_PROGRESS)
- [ ] Start WO dengan confidence
- [ ] Input produksi harian
- [ ] Report material shortage
- [ ] View production progress
- [ ] Know siapa yang dihubungi jika ada masalah

**Trainer Signature**: _______________  
**Participant Signature**: _______________  
**Date**: _______________

---

**Generated by**: IT Developer Expert  
**Last Updated**: 4 Februari 2026  
**Version**: 1.0
