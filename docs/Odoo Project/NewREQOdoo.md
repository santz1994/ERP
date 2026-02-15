📘 PROJECT SCOPE & TECHNICAL REQUIREMENTS DEFINITION

PT Quty Karunia - ERP Implementation (Odoo)

Dokumen: Master Requirement Specification (MRS) v3.0

Status: 🔴 CRITICAL / HIGH STAKES (Wajib Baca bagi Vendor)

Tanggal: 13 Februari 2026

Revisi: Major Update based on Req Document2.docx (Corrected Dept/Warehouse Flow)

1. PROJECT BACKGROUND & OBJECTIVES

1.1 Konteks Bisnis

PT Quty Karunia adalah manufaktur Soft Toys (Boneka) ekspor (Supplier Utama: IKEA). Sistem ERP Odoo dibutuhkan untuk menggantikan spreadsheet terfragmentasi, dengan fokus pada Compliance, Traceability, dan Inventory Control.

1.2 Tujuan Utama (Mandatory Goals)

Single Source of Truth: Data produksi, purchasing, dan inventory terintegrasi.

Strict Inventory Control (Multi-Location): Setiap departemen (Cutting, Sewing, dll) memiliki "Gudang" sendiri untuk melacak perpindahan barang WIP.

Loss Reduction: Kontrol ketat terhadap Fabric Yield (Susut Kain) dan Waste.

2. ARSITEKTUR GUDANG & ALUR PRODUKSI (CRITICAL GAP)

KOREKSI PENTING: Berdasarkan dokumen requirements, struktur produksi BUKAN satu lokasi besar. Setiap Departemen bertindak sebagai Internal Warehouse yang melakukan transaksi terima-serah (Handover).

2.1 Konsep "Department as a Warehouse"

Setiap perpindahan barang antar proses adalah transaksi inventory (Internal Transfer) yang harus di-scan/input.

Departemen

Input (Barang Masuk)

Proses (Work Center)

Output (Barang Keluar/WIP)

Gudang Kain

Terima dari Supplier (Vendor)

Penyimpanan & QC Kain

Transfer ke Cutting

Dept. Cutting

Terima Kain (Roll/Yard)

Potong Pola

Output: Potongan Kain (Pcs/Set)

Dept. Sewing

Terima Potongan Kain

Menjahit Skin (Kulit Boneka)

Output: Skin Boneka (Pcs)

Dept. Stuffing

Terima Skin + Dacron (Kg)

Pengisian

Output: Boneka Gembung (Pcs)

Dept. Finishing

Terima Boneka Gembung + Mata

Pasang Mata, Bersih Benang

Output: Barang Jadi (Pcs)

Gudang FG

Terima Barang Jadi

Packing & Sortir

Kirim ke Customer

Requirement: Sistem harus mencatat "Stock on Hand" di meja Sewing, meja Cutting, dst. Bukan hanya stock di gudang utama.

3. COMPREHENSIVE WORKFLOW (PURCHASING TO PRODUCTION)

3.1 Alur Purchasing (The 3 PO Types)

Purchasing tidak seragam. Terdapat 3 jenis PO dengan perlakuan berbeda:

PO TYPE A: KAIN (Fabric) - The Initiator

Input: Yard/Roll.

Fungsi: Trigger MO Partial. Begitu PO Kain confirm, orang gudang tahu barang akan datang, dan PPIC tahu produksi bisa dimulai (Early Start).

PO TYPE B: LABEL & PACKAGING - The Validator

Input: Pcs/Set.

Fungsi: Trigger MO Release. Membawa informasi krusial: Negara Tujuan (Destination) dan Minggu Pengiriman (Week).

Logic: Produksi tidak boleh Finish (Packing) jika PO Label belum datang/belum diinput, karena resiko salah label bahasa/negara.

PO TYPE C: AKSESORIS (Mata, Benang, Hidung)

Fungsi: Consumables. Harus tersedia, tapi tidak men-trigger pembuatan MO. Hanya validasi ketersediaan stok (Availability Check).

3.2 Alur Produksi & Peran Admin (Daily Input)

Berbeda dengan pabrik otomotif high-tech, input data di Quty dilakukan oleh Admin Produksi, bukan operator mesin satu per satu.

Aktor: Admin Produksi (1 orang per Dept/Line).

Alat: Tablet Android / PC Station.

Workflow Input Harian:

Start Shift: Admin menerima SPK (Surat Perintah Kerja) dari sistem.

Proses Fisik: Operator (Tukang Potong/Jahit) bekerja manual.

End Shift / Hourly: Admin mengumpulkan data output dari lantai produksi.

Input System: Admin menginput "Daily Production Report" ke Odoo:

Berapa Good Qty?

Berapa Reject?

Siapa yang mengerjakan (Group/Leader)?

Validasi: Sistem memotong stok material di lokasi departemen tersebut secara otomatis (Backflush) atau manual issue.

4. MATERIAL MANAGEMENT & UOM MATRIX

Masalah terbesar saat ini adalah kekacauan satuan. Odoo harus menangani konversi ini secara Otomatis & Presisi.

4.1 Tabel Konversi UOM (Contoh Kasus: Boneka AFTONSPARV)

Kategori Material

UOM Beli (Purchase)

UOM Simpan (Stock)

UOM Pakai (BOM/Production)

Konversi Logic

Kain (Fabric)

YARD / ROLL

YARD

YARD / METER

1 Yard = 0.9144 Meter (Fixed)

Isian (Dacron)

BAL / KG

KG

GRAM

1 Kg = 1000 Gram

Benang (Thread)

CONE / LUSIN

CONE

CM / METER

1 Cone = ~5000 Meter (Perlu Rumus)

Aksesoris (Mata)

GROSS / PCS

PCS

PCS

1 Gross = 144 Pcs

4.2 Requirement Validasi UOM

Toleransi: Sistem harus menolak jika user menginput pemakaian kain yang tidak masuk akal (misal: 1 boneka kecil menghabiskan 5 Yard kain -> ERROR/WARNING).

Yield Report: Laporan harus menyajikan persentase penggunaan kain.

Standard: 1 Yard jadi 5 Boneka.

Actual: 1 Yard jadi 4.5 Boneka.

Result: Yield Loss detected.

5. DUAL TRIGGER SYSTEM (REFINED LOGIC)

Logika ini harus diimplementasikan via Custom Add-on atau Automated Action Server yang kuat.

Action 1: User Confirm PO Kain.

System: Check apakah MO sudah ada? Jika belum, Create MO (State: Draft/Partial).

Info: MO berisi Estimasi Qty berdasarkan jumlah kain.

Action 2: User Confirm PO Label & Input Data Week + Destination.

System: Cari MO yang statusnya Partial. Update MO tersebut.

Update: Inject data Week & Destination ke MO Header dan seluruh Work Order (SPK) anakannya.

State Change: MO berubah menjadi Confirmed/Released.

6. ROLE BASED ACCESS CONTROL (RBAC) & SECURITY

Mengacu pada Req Document2.docx, keamanan data adalah prioritas untuk mencegah fraud dan menjaga fokus kerja.

6.1 Matriks Akses (Strict Separation)

Role

Menu yang BISA Diakses

Menu yang DIBLOKIR (Hidden)

Admin Gudang Kain

Receipts (GRN), Internal Transfer (ke Cutting), Stock Opname Kain.

Nilai Harga (Cost), Menu Produksi, Menu Sales.

Admin Produksi (Cutting/Sewing)

Work Order Input, Output Production, Request Material.

Inventory Value, Purchasing, Accounting.

Admin Warehouse FG

Receipt from Finishing, Delivery Order (DO), Packing List.

Edit Qty PO, Edit BOM.

Purchasing Staff

Purchase Order, Vendor Bill (View Only).

Edit Stock Level Manual (Adjustment).

Management/Owner

DASHBOARD ONLY (WIP View, Financial Report, Production Status).

(Full Access tapi Read-Only disarankan).

7. DELIVERABLES & EXPECTATIONS

Vendor Odoo wajib menyediakan item berikut sebelum fase development:

Blueprint Alur Gudang: Diagram yang menunjukkan setiap lokasi (Virtual Location) per departemen dan aturan Routes (Push/Pull rules) yang akan disetting.

Mockup Input Harian: Tampilan UI untuk Admin Produksi input hasil harian (harus simpel, grid view matrix per tanggal dan operator).

UOM Conversion Plan: Dokumen teknis bagaimana menangani konversi Yard ke Pcs dalam BOM.

Migration Script: Rencana migrasi data master (BOM, Produk, Vendor) dari Excel ke Odoo.

8. CLOSING CHECKLIST (User Validation)

Apakah dokumen ini sudah mencakup:

✅ Setiap Dept melakukan SO (Warehouse Transfer)? Ya, di Section 2.

✅ Terkait Admin Input Daily? Ya, di Section 3.2.

✅ Alur Workflow Lengkap? Ya, di Section 3.

✅ Alur Purchasing 3 Tipe? Ya, di Section 3.1.

✅ UOM di seluruh Dept? Ya, di Section 4.

Dokumen ini sekarang menjadi acuan tunggal yang valid.