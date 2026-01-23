# 📦 Panduan Singkat: Cara Memasukkan & Mengedit BOM

**Pertanyaan**: "Bagaimana cara memasukkan BOM secara manual atau jika mau melakukan pengeditan BOM?"

**Jawaban**: Ada 3 cara! Berikut adalah panduan singkatnya:

---

## ✅ CARA 1: Input BOM Manual (Paling Mudah)

### Step-by-Step:

**1. Buka halaman PPIC**
```
Dari menu utama:
Produksi → PPIC
atau langsung: /ppic
```

**2. Masuk tab "BOM Management"**
```
Di halaman PPIC, cari tab:
📦 BOM Management (3 tab pilihan: MO, BOM, Planning)
```

**3. Klik tombol "➕ Add BOM Manually"**
```
Tombol ungu di bagian atas tab BOM
Form akan muncul di bawah
```

**4. Isi form dengan data:**

```
┌─────────────────────────────────────────────┐
│ INFORMASI PRODUK                            │
├─────────────────────────────────────────────┤
│ Product Code *      : TS-001                │
│ Product Name *      : T-Shirt Premium       │
│                                             │
│ INFORMASI MATERIAL                          │
├─────────────────────────────────────────────┤
│ Material/Component *: Cotton Fabric         │
│ Quantity Required * : 1.5                   │
│ Unit *              : m (meter)             │
│ Unit Price          : 25000                 │
│                                             │
│ TIPE & STATUS                               │
├─────────────────────────────────────────────┤
│ Material Type       : fabric                │
│ Status              : active                │
│ Notes               : Premium quality...    │
│                                             │
│ [CANCEL]            [✅ SAVE BOM]           │
└─────────────────────────────────────────────┘
```

**5. Klik "✅ Save BOM"**
```
BOM akan otomatis ditambahkan ke sistem
Dan muncul di tabel BOM List di bawah
```

---

## ✏️ CARA 2: Edit BOM yang Sudah Ada

### Metode A: Edit dari Tabel (Paling Cepat)

**1. Scroll ke bagian "📋 BOM List - View & Edit"**

**2. Cari BOM yang ingin diedit**
```
Cari di tabel dengan kolom:
- Product
- Material/Component
- Quantity
- Unit Price
```

**3. Klik tombol "✏️ Edit"**
```
Tombol biru di kolom "Actions"
Form akan terbuka di atas
```

**4. Ubah field yang diinginkan**
```
Bisa mengubah:
✅ Quantity (berapa banyak)
✅ Unit Price (harga satuan)
✅ Status (active/inactive)
✅ Material Type (kategori)
✅ Notes (catatan)

❌ TIDAK bisa mengubah:
- Product Code
- Product Name
- Material Name
(Jika perlu ubah ini, delete & buat baru)
```

**5. Klik "✅ Update BOM"**
```
Perubahan akan disimpan
Tabel akan refresh otomatis
```

### Metode B: Edit via Form Manual

**1. Klik "➕ Add BOM Manually"**

**2. Di form, cari/masukkan Product Code**
```
Sistem akan auto-load data BOM yang ada
```

**3. Ubah data yang diperlukan**

**4. Klik "✅ Update BOM"** (bukan Save)
```
Tombol berubah jika system detect BOM existing
```

---

## 🗑️ CARA 3: Hapus BOM

### Step-by-Step:

**1. Scroll ke tabel "📋 BOM List - View & Edit"**

**2. Cari BOM yang ingin dihapus**

**3. Klik tombol "🗑️ Delete"**
```
Tombol merah di kolom "Actions"
```

**4. Konfirmasi penghapusan**
```
Popup: "Apakah Anda yakin ingin menghapus?"
Klik: "Ya, Hapus" atau "Batal"
```

**5. Done! ✅**
```
BOM akan dihapus dari sistem
```

⚠️ **PERHATIAN**: Penghapusan PERMANENT dan tidak bisa dibatalkan!

---

## 📥 CARA 4: Import BOM Massal (CSV/Excel)

Untuk tambah 10+ BOM sekaligus:

**1. Klik tombol "📥 Import BOM"** (tombol biru)

**2. Siapkan file dengan format**
```
File: CSV atau Excel (.xlsx)

Isi file:
┌──────────┬────────────┬──────────────┬────────┬─────┬────────┐
│ Product  │ Product    │ Material     │ Qty    │Unit │ Price  │
│ Code     │ Name       │ Component    │        │     │        │
├──────────┼────────────┼──────────────┼────────┼─────┼────────┤
│ TS-001   │ T-Shirt    │ Cotton       │ 1.5    │ m   │ 25000  │
│ TS-001   │ T-Shirt    │ Thread White │ 2      │pcs  │ 5000   │
│ TS-001   │ T-Shirt    │ Button       │ 5      │pcs  │ 2000   │
└──────────┴────────────┴──────────────┴────────┴─────┴────────┘
```

**3. Upload file**

**4. Preview & Konfirmasi**

**5. Sistem import otomatis**

---

## 🎯 Unit Pilihan

Saat input BOM, pilih salah satu:

```
m    = Meter          (untuk kain, material lembaran)
kg   = Kilogram       (untuk bahan curah)
pcs  = Pieces/Unit    (untuk barang individual)
L    = Liter          (untuk cairan)
box  = Box            (untuk kemasan/karton)
```

---

## 🏷️ Material Type Pilihan

Kategorisasi bahan (opsional):

```
fabric   = Kain (cotton, polyester, dll)
thread   = Benang jahit
button   = Kancing/tombol
zipper   = Resleting
elastic  = Elastis (karet, dll)
lace     = Renda/trim
other    = Lainnya
```

---

## 📊 Contoh: Buat BOM T-Shirt Premium

**STEP 1: Input Cotton Fabric**
```
Product Code *       : TS-001
Product Name *       : T-Shirt Premium
Material/Component * : Cotton Fabric
Qty Required *       : 1.5
Unit *               : m
Unit Price           : 25000
Material Type        : fabric
Status               : active
Notes                : Premium quality cotton
[Save]
```

**STEP 2: Input Thread**
```
Product Code *       : TS-001
Product Name *       : T-Shirt Premium
Material/Component * : Thread White
Qty Required *       : 2
Unit *               : pcs
Unit Price           : 5000
Material Type        : thread
Status               : active
[Save]
```

**STEP 3: Input Button**
```
Product Code *       : TS-001
Product Name *       : T-Shirt Premium
Material/Component * : Button 4-hole
Qty Required *       : 5
Unit *               : pcs
Unit Price           : 2000
Material Type        : button
Status               : active
[Save]
```

**RESULT:**
```
✅ T-Shirt Premium (TS-001) BOM Complete!

Items:
1. Cotton Fabric: 1.5 m  @ Rp 25,000 = Rp 37,500
2. Thread White:  2 pcs  @ Rp  5,000 = Rp 10,000
3. Button 4-hole: 5 pcs  @ Rp  2,000 = Rp 10,000
                          ─────────────────────
                          TOTAL = Rp 47,500/unit
```

---

## 💡 Tips Penting

### ✅ Field Yang Wajib Diisi (*)
```
- Product Code
- Product Name
- Material/Component
- Quantity Required
- Unit
```

### ✅ Field Opsional (Tapi Rekomendasi Diisi)
```
- Unit Price (untuk costing akurat)
- Material Type (untuk kategorisasi)
- Notes (untuk referensi)
```

### ⚠️ Perhatian Saat Edit
```
Bisa diubah:
✅ Quantity
✅ Unit Price
✅ Status
✅ Material Type
✅ Notes

Tidak bisa diubah:
❌ Product Code
❌ Product Name
❌ Material Name

Jika perlu ubah yang tidak bisa,
gunakan: DELETE lalu CREATE baru
```

---

## 🔧 Field Validation

Pastikan data valid:

```
Quantity:
- Minimal 0.01
- Maksimal 999,999
- Bisa desimal (1.5, 2.25, dll)
- Tidak boleh 0 atau negatif

Unit Price:
- Tanpa format (hanya angka)
- Contoh BENAR: 25000
- Contoh SALAH: Rp 25.000 atau 25,000

Product Code:
- Maksimal 50 karakter
- Gunakan format: [KATEGORI]-[NOMOR]
- Contoh: TS-001, SH-002, JK-001
```

---

## 📞 Butuh Bantuan?

### Quick Tips
1. Lihat instruksi di halaman PPIC (ada 3 card)
2. Ikuti contoh di atas
3. Gunakan tabel BOM List untuk referensi

### Detail Penuh
- File: `docs/BOM_MANUAL_ENTRY_GUIDE.md`
- Berisi: Troubleshooting, best practices, contoh lengkap

### Developer/API
- File: `docs/BOM_API_DOCUMENTATION.md`
- Berisi: Semua endpoint, request/response, contoh code

---

## ✨ Yang Akan Terjadi Setelah Input BOM

Setelah BOM disimpan, BOM akan otomatis digunakan di:

```
✂️  CUTTING MODULE
    - Validasi material vs BOM
    - Hitung kebutuhan material

🧵 SEWING MODULE
    - Input validation vs BOM
    - Track component usage

✨ FINISHING MODULE
    - Material tracking
    - Defect vs BOM

📦 PACKING MODULE
    - Final BOM verification
    - Generate packing list

💰 COSTING MODULE
    - Calculate product cost
    - Material cost auto-calculated
```

---

**RINGKAS:**

| Kebutuhan | Cara | Waktu |
|-----------|------|-------|
| Tambah 1-2 BOM | Manual Entry Form | 2-3 menit |
| Edit BOM | Edit via Tabel | 1-2 menit |
| Hapus BOM | Delete Button | 1 menit |
| Tambah 10+ BOM | Import CSV/Excel | 5 menit |

---

**Sudah jelas? Silahkan coba! 🚀**
