# 📦 BOM Manual Entry & Edit Guide

**Updated**: 2026-01-23  
**Version**: 1.0  
**Status**: ✅ Complete

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Cara Memasukkan BOM Manual](#cara-memasukkan-bom-manual)
3. [Cara Mengedit BOM](#cara-mengedit-bom)
4. [Cara Menghapus BOM](#cara-menghapus-bom)
5. [Import/Export BOM (Batch)](#importexport-bom-batch)
6. [BOM Fields Reference](#bom-fields-reference)
7. [Tips & Best Practices](#tips--best-practices)

---

## Overview

**Bill of Materials (BOM)** adalah daftar lengkap bahan/komponen yang diperlukan untuk membuat satu unit produk.

### 3 Cara Mengelola BOM di Sistem:

| Metode | Cara | Kapan Digunakan |
|--------|------|-----------------|
| **Manual Entry** | Form di halaman PPIC | Tambah 1-2 BOM, edit cepat |
| **Bulk Import** | Upload CSV/Excel | Tambah puluhan BOM sekaligus |
| **Direct Edit** | Edit di tabel BOM list | Ubah nilai quantity, price, dll |

---

## 🎯 Cara Memasukkan BOM Manual

### Step 1: Buka Halaman PPIC
```
Menu: Production → PPIC
atau langsung ke: /ppic
```

### Step 2: Masuk ke Tab BOM
- Di halaman PPIC, klik tab **"📦 BOM Management"**
- Anda akan melihat beberapa opsi di atas

### Step 3: Klik Tombol "Add BOM Manually"
- Tombol warna **ungu** dengan ikon ➕
- Form akan muncul di bawah heading

### Step 4: Isi Form BOM
Berikut adalah field yang harus diisi:

#### **A. Informasi Produk** (Wajib diisi *)
```
Product Name *         → Nama produk lengkap
                         Contoh: "T-Shirt Premium"

Product Code *         → Kode unik produk
                         Contoh: "TS-001"
```

#### **B. Informasi Material/Komponen** (Wajib diisi *)
```
Material/Component *   → Nama bahan atau komponen
                         Contoh: "Cotton Fabric", "Thread White", "Button"

Quantity Required *    → Jumlah bahan yang dibutuhkan
                         Contoh: 1.5, 2, 5

Unit *                 → Satuan pengukuran
                         Pilihan:
                         - Kilogram (kg)
                         - Meter (m)
                         - Pieces (pcs)
                         - Liter (L)
                         - Box
```

#### **C. Informasi Harga & Kategori**
```
Unit Price             → Harga satuan bahan
                         Contoh: 25000

Material Type          → Tipe material (bantuan kategorisasi)
                         Pilihan:
                         - Fabric (Kain)
                         - Thread (Benang)
                         - Button (Kancing)
                         - Zipper (Resleting)
                         - Elastic (Elastis)
                         - Lace (Renda)
                         - Other (Lainnya)

Status                 → Status aktif/tidak
                         - Active (Aktif digunakan)
                         - Inactive (Tidak digunakan)
```

#### **D. Catatan**
```
Notes/Description      → Keterangan tambahan
                         Contoh: "Premium quality cotton, 100% cotton, white color"
```

### Step 5: Simpan BOM
- Klik tombol **"✅ Save BOM"** (warna ungu)
- BOM akan ditambahkan ke sistem
- Anda akan melihat BOM baru di tabel "BOM List - View & Edit" di bawah

---

## ✏️ Cara Mengedit BOM

### Metode 1: Edit dari Tabel BOM List (Rekomendasi)

```
1. Scroll ke bagian "📋 BOM List - View & Edit"
2. Cari BOM yang ingin diedit
3. Klik tombol "✏️ Edit" pada baris tersebut
4. Ubah field yang diperlukan:
   - Quantity Required (jumlah)
   - Unit Price (harga)
   - Status (aktif/tidak)
   - Material Type (kategori)
   - Notes (catatan)
5. Klik "✅ Update BOM" untuk menyimpan perubahan
```

### Metode 2: Edit via Manual Form

```
1. Klik tombol "➕ Add BOM Manually"
2. Form akan terbuka
3. Masukkan Product Code untuk mencari BOM yang ada
4. Sistem akan load data BOM yang ada
5. Ubah field yang diperlukan
6. Klik "✅ Update BOM" (tombol berubah dari "Save" ke "Update")
```

### ⚠️ Field Yang Bisa Diedit:
- ✅ Quantity Required (bisa diubah)
- ✅ Unit Price (bisa diubah)
- ✅ Unit (bisa diubah)
- ✅ Material Type (bisa diubah)
- ✅ Status (bisa diubah)
- ✅ Notes/Description (bisa diubah)
- ❌ Product Code (tidak bisa diubah, gunakan Delete + Add jika perlu)
- ❌ Material/Component Name (tidak bisa diubah, gunakan Delete + Add jika perlu)

---

## 🗑️ Cara Menghapus BOM

### Step 1: Scroll ke Tabel BOM List
Di halaman PPIC → Tab BOM → Bagian "📋 BOM List - View & Edit"

### Step 2: Cari BOM yang Ingin Dihapus
Lihat di tabel dengan kolom:
- Product
- Material/Component
- Qty Required
- Unit
- Status

### Step 3: Klik Tombol "🗑️ Delete"
- Tombol merah di kolom "Actions"
- Sistem akan meminta konfirmasi penghapusan

### Step 4: Konfirmasi Penghapusan
```
Popup: "Apakah Anda yakin ingin menghapus BOM ini?"
Pilih: "Ya, Hapus" atau "Batal"
```

### ⚠️ Perhatian:
- Penghapusan BOM **tidak dapat dibatalkan** (Permanent Delete)
- Pastikan tidak ada production order yang menggunakan BOM ini
- Jika BOM sedang digunakan, akan muncul warning

---

## 📥📤 Import/Export BOM (Batch)

Untuk menambahkan puluhan atau ratusan BOM sekaligus, gunakan fitur Import/Export.

### A. IMPORT BOM (Upload File)

**Kapan digunakan:**
- Tambah 10+ BOM sekaligus
- Migrasi data dari sistem lain
- Update data massal

**Langkah-langkah:**

```
1. Buka halaman PPIC
2. Klik tombol "📥 Import BOM" (biru)
3. Pilih file CSV atau Excel (.xlsx)
4. Preview data yang akan diimport
5. Jika sudah benar, klik "Confirm Import"
6. Tunggu proses selesai
```

**Format File CSV:**
```csv
Product Code,Product Name,Material/Component,Quantity,Unit,Unit Price,Material Type,Status,Notes
TS-001,T-Shirt Premium,Cotton Fabric,1.5,m,25000,fabric,active,Premium quality
TS-001,T-Shirt Premium,Thread White,2,pcs,5000,thread,active,100% polyester
TS-001,T-Shirt Premium,Button 4 hole,5,pcs,2000,button,active,Plastic button
```

**Format File Excel:**
- Gunakan header di baris pertama
- Setiap BOM dalam satu baris
- Maksimal 1000 BOM per file

### B. EXPORT BOM (Download File)

**Kapan digunakan:**
- Backup data BOM
- Analisis data di Excel
- Kirim ke supplier/vendor
- Presentasi ke management

**Langkah-langkah:**

```
1. Buka halaman PPIC → Tab BOM
2. Klik tombol "📤 Export BOM" (hijau)
3. Pilih format:
   - CSV (Recommended untuk data besar)
   - Excel (.xlsx) (Recommended untuk presentasi)
4. Klik "Download"
5. File akan terunduh dengan nama:
   bom_export_2026_01_23.csv
   atau
   bom_export_2026_01_23.xlsx
```

---

## 📋 BOM Fields Reference

### Field Descriptions

| Field | Tipe | Wajib | Max Length | Deskripsi |
|-------|------|-------|-----------|-----------|
| Product Code | Text | ✅ | 50 | Kode unik produk (misal: TS-001) |
| Product Name | Text | ✅ | 100 | Nama lengkap produk |
| Material/Component | Text | ✅ | 100 | Nama bahan atau komponen |
| Quantity Required | Number | ✅ | - | Jumlah bahan (bisa desimal: 1.5) |
| Unit | Select | ✅ | - | Satuan: kg, m, pcs, L, box |
| Unit Price | Number | ❌ | - | Harga per satuan (tanpa format) |
| Material Type | Select | ❌ | - | Kategori: fabric, thread, button, dll |
| Status | Select | ❌ | - | active atau inactive |
| Notes | Text | ❌ | 500 | Catatan tambahan untuk referensi |

### Unit Options
```
kg      = Kilogram (untuk bahan cair/bubuk)
m       = Meter (untuk kain/material berbentuk lembaran)
pcs     = Pieces/Unit (untuk barang individual)
L       = Liter (untuk cairan)
box     = Box/Karton (untuk kemasan)
```

### Material Type Categories
```
fabric     = Kain (cotton, polyester, dll)
thread     = Benang (benang jahit, dst)
button     = Kancing/Tombol
zipper     = Resleting/Zipper
elastic    = Elastis (karet, dst)
lace       = Renda/Trim
other      = Lainnya (kategori bebas)
```

---

## 💡 Tips & Best Practices

### ✅ Best Practices

1. **Naming Convention untuk Product Code**
   ```
   Format: [Category]-[Number]
   
   Contoh:
   TS-001 → T-Shirt Premium
   TS-002 → T-Shirt Standard
   SH-001 → Shorts Premium
   JK-001 → Jacket Winter
   ```

2. **Group BOM Items**
   ```
   Satu produk bisa punya multiple BOM items:
   
   T-Shirt Premium (TS-001)
   ├── Cotton Fabric: 1.5 m
   ├── Thread White: 2 pcs
   ├── Button: 5 pcs
   └── Label: 1 pcs
   
   Sistem akan otomatis group berdasarkan Product Code
   ```

3. **Accurate Quantity**
   ```
   Pastikan quantity akurat untuk:
   - Costing yang benar
   - Planning material yang tepat
   - Tidak ada shortage saat production
   
   Contoh benar:
   Cotton Fabric: 1.5 m (bukan 2 m)
   Button: 5 pcs (untuk 1 unit produk)
   ```

4. **Unit Price untuk Costing**
   ```
   Masukkan harga satuan yang akurat untuk:
   - Hitung total cost of goods
   - Budget planning
   - Profit margin calculation
   
   Format: Hanya angka (misal: 25000)
   Jangan: Rp 25.000 atau 25,000
   ```

5. **Use Status Active/Inactive**
   ```
   Active = Digunakan dalam production aktif
   Inactive = BOM discontinued atau tidak diproduksi
   
   Saat planning, sistem hanya filter BOM Active
   ```

6. **Detail Notes untuk Reference**
   ```
   Notes field gunakan untuk:
   - Spesifikasi material: "Premium quality cotton, 100% cotton, white"
   - Supplier info: "Supplier: PT ABC, Min order: 50kg"
   - Quality notes: "Grade A, must check color before cutting"
   ```

### ⚠️ Common Mistakes to Avoid

1. **❌ Wrong Unit Selection**
   ```
   Salah: Fabric 5 pcs (seharusnya 5 m)
   Benar: Fabric 5 m
   ```

2. **❌ Inconsistent Naming**
   ```
   Salah: Cotton Fabric, cotton fabric, COTTON FABRIC
   Benar: Cotton Fabric (consistent)
   ```

3. **❌ Missing Material Type**
   ```
   Salah: Type field kosong
   Benar: Type = "fabric" atau "thread"
   
   Gunakan untuk filtering dan reporting
   ```

4. **❌ Outdated Quantity**
   ```
   Salah: Tidak update qty saat design berubah
   Benar: Update qty sesuai final design
   
   Check dengan Designer/Pattern Maker
   ```

5. **❌ Zero or Negative Quantity**
   ```
   Salah: Quantity = 0 atau -1
   Benar: Quantity = actual value (min 0.01)
   ```

### 🔄 Workflow Rekomendasi

#### **Scenario 1: Produk Baru**
```
1. Design finalisasi
2. Pattern maker tentukan material & qty
3. Costing hitung unit price
4. QA review BOM
5. Input ke sistem (manual atau batch)
6. Set status = Active
```

#### **Scenario 2: Update BOM (Quantity Change)**
```
1. Designer request qty change
2. Buka BOM di sistem
3. Edit Quantity Required
4. Update Unit Price jika berubah
5. Add note tentang perubahan
6. Save
7. Notify production team
```

#### **Scenario 3: Discontinue Product**
```
1. Approve dari management
2. Buka BOM item
3. Set Status = Inactive
4. Add note: "Discontinued 2026-01-23"
5. BOM masih ada di history
6. Produksi tidak bisa pakai BOM ini
```

#### **Scenario 4: Batch Import dari Excel**
```
1. Finance/Costing team siapkan data di Excel
2. Format sesuai template (download di sistem)
3. Validate data: no duplicates, qty > 0
4. Upload via Import BOM
5. Preview hasil import
6. Confirm & wait for completion
7. Check hasil import di BOM List
```

---

## 🔗 Integrasi dengan Module Lain

BOM yang dibuat akan otomatis digunakan di:

### 1. **Cutting Module** ✂️
```
- Validate material vs BOM saat input
- Hitung kebutuhan material total untuk batch
- Tracking material usage vs BOM
```

### 2. **Sewing Module** 🧵
```
- Input validation vs BOM spec
- Track component usage (threads, buttons, etc)
- Quality check vs BOM
```

### 3. **Finishing Module** ✨
```
- Material tracking
- Defect tracking vs BOM spec
- Usage variance report
```

### 4. **Packing Module** 📦
```
- Final BOM verification
- Check semua component ada
- Generate packing list dari BOM
```

### 5. **Costing Module** 💰
```
- Auto calculate product cost dari BOM
- Unit price × Quantity = Material cost
- Total product cost = Material + Labor + Overhead
```

---

## 📞 Support & Troubleshooting

### Masalah: BOM tidak tersimpan

**Solusi:**
```
1. Check apakah semua field wajib sudah diisi (*)
2. Lihat error message di form
3. Pastikan quantity > 0
4. Refresh halaman dan coba lagi
```

### Masalah: BOM tidak muncul di list

**Solusi:**
```
1. Check apakah status = Active
2. Filter mungkin aktif, clear filter
3. Refresh halaman (F5)
4. Check browser console untuk error
```

### Masalah: Tidak bisa delete BOM

**Solusi:**
```
1. BOM mungkin sedang digunakan di production order
2. Coba set status = Inactive dulu
3. Contact administrator jika masih error
```

### Masalah: Import file error

**Solusi:**
```
1. Check format file (CSV atau Excel)
2. Pastikan header sesuai template
3. Tidak ada karakter special di data
4. Quantity semua > 0
5. Download template dari sistem dan gunakan
```

---

## 📊 Example: Complete BOM Entry

### Contoh Kasus: Buat BOM untuk T-Shirt Premium (TS-001)

**Step 1: Manual Entry di Form**

```
Product Name *         : T-Shirt Premium
Product Code *         : TS-001
Material/Component *   : Cotton Fabric
Quantity Required *    : 1.5
Unit *                 : m
Unit Price             : 25000
Material Type          : fabric
Status                 : Active
Notes                  : Premium quality cotton, 100% cotton, white color
```

**Step 2: Submit & Lihat di Tabel**

```
| Product            | Material        | Qty  | Unit | Price   | Status |
|-------------------|-----------------|------|------|---------|--------|
| TS-001 T-Shirt    | Cotton Fabric   | 1.5  | m    | 25,000  | Active |
```

**Step 3: Tambah Item Kedua (Thread)**

```
Product Name *         : T-Shirt Premium
Product Code *         : TS-001
Material/Component *   : Thread White
Quantity Required *    : 2
Unit *                 : pcs
Unit Price             : 5000
Material Type          : thread
Status                 : Active
Notes                  : Polyester thread, white, 30wt
```

**Step 4: Tambah Item Ketiga (Button)**

```
Product Name *         : T-Shirt Premium
Product Code *         : TS-001
Material/Component *   : Button 4-hole
Quantity Required *    : 5
Unit *                 : pcs
Unit Price             : 2000
Material Type          : button
Status                 : Active
Notes                  : Plastic button, 15mm diameter
```

**Final Result: BOM Complete**

```
T-Shirt Premium (TS-001) Total Cost: Rp 47,500

Items:
1. Cotton Fabric: 1.5 m × Rp 25,000 = Rp 37,500
2. Thread White: 2 pcs × Rp 5,000 = Rp 10,000
3. Button 4-hole: 5 pcs × Rp 2,000 = Rp 10,000
   ─────────────────────────────────────────────
   Total Material Cost per Unit: Rp 47,500
```

---

**End of Document**

*Untuk pertanyaan atau feedback, hubungi: Admin / Supervisor / PPIC Team*
