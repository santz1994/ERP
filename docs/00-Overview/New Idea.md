⚠️ **New Idea**:
1.  Sebelumnya alur proses production dimulai dari PO IKEA. Sekarang, alur proses produksi akan dimulai dari PO Purchasing.
2.  Proses pembelian material PO IKEA -> PO Purchassing (Material Kain) -> PO Purchasing (Material Label) -> MO Purchassing (Material) -> Warehouse Receiving
3.  Macro Flowchart alur proses produksi:
    [PO IKEA (Forecast)] --> (Manual Check)
                                  |
                                  v
                       [PO PURCHASING (Kain)] 
                                  |
                                  v
                       [PO PURCHASING (Material Label)] <-- [PO PURCHASING (Material Lainnya)]
                                  |
                          (TRIGGER UTAMA)
                                  v
                        [MO MANUFACTURING (PPIC)]
                                  |
                                  v
                      [WAREHOUSE RECEIVING] <---(Material In)--- [SUPPLIER]
                                  |
                                  v
                      [PRODUCTION EXECUTION] (Cutting -> Embroidery -> Sewing -> Finishing -> Packing)
                                  |
                                  v
                      [FINISH GOOD INVENTORY] ---> [SHIPPING]

4.  Production Floor & Material Movement Detail Flowchart:
    4.1. Preparation & Cutting
      - Main Material: Kain (Roll/Yard).
      - Bahan Penolong: (Sesuai BOM / MO Manufacturing) 
        - Kertas Marker (Pola)
        - Plastik Bundle
        - Kapur/Tinta
        - Pisau Cutting.
        - Benang
        - Dan lainnya sesuai kebutuhan.
      - Activity: Warehouse release kain sesuai MO + release bahan penolong sesuai estimasi kebutuhan mingguan/harian.
    4.2. Embroidery (Bordir)
      - Input WIP: Potongan Kain dari Cutting.
      - Bahan Penolong (Request ke Warehouse): (Sesuai BOM / MO Manufacturing)
        - Benang Bordir (Aneka Warna).
        - Kain Keras (Backing Paper/Interlining).
        - Jarum Bordir.
        - Dan lainnya sesuai kebutuhan.
      - Activity: Operator mengambil benang sesuai kebutuhan warna desain MO.
    4.3. Sewing (Penjahitan)
      - Input WIP: Potongan Bordir/Polos + Label Identity.
      - Bahan Penolong (Request ke Warehouse): (Sesuai BOM / MO Manufacturing)
        - Benang Jahit (Sesuai warna kain).
        - Jarum Jahit.
        - Perekat (Adhesive).
        - Minyak Mesin (Consumables).
        - Gunting/Cekris.
        - Dan lainnya sesuai kebutuhan.
      - Activity: Distribusi benang ke setiap line/operator.
    4.4. Finishing (Stuffing & Closing)
      - Input WIP: Skin (dari Warehouse Finishing).
      - Bahan Penolong (Request ke Warehouse): (Sesuai BOM / MO Manufacturing)
        - Kapas/Dacron (Material Kritis - Volume Besar) → Dikonsumsi pada tahap STUFFING.
        - Benang Jahit Tangan (untuk Closing) → Dikonsumsi pada tahap CLOSING.
        - Hangtag / Price Tag (Aksesoris).
        - Cairan Pembersih (Cleaning Fluid).
        - Dan lainnya sesuai kebutuhan.
      - Activity: Kapas biasanya di-supply dalam bentuk Bale (Karung Besar) langsung ke area mesin stuffing.
      - **Internal Process Flow**:
        1. **Stuffing**: Skin + Kapas → Stuffed Body (Status berubah di Warehouse Finishing, no surat jalan)
        2. **Closing**: Stuffed Body + Benang Jahit → Finished Doll (ready untuk Packing)
      - **Warehouse Finishing Internal Conversion**:
        - Skin → Stuffed Body: Log produksi internal, stok Skin berkurang, stok Stuffed Body bertambah
        - Stuffed Body → Finished Doll: Transfer ke Packing, stok Stuffed Body berkurang
      - **Validasi Stok**:
        - Proses Stuffing tidak bisa diinput jika stok Skin = 0 di Warehouse Finishing
        - Proses Closing tidak bisa diinput jika stok Stuffed Body = 0 di Warehouse Finishing
      - **BOM Logic**: 
        - BOM Finishing tahap Stuffing: Skin (1 pcs) + Kapas (X gram) = Stuffed Body (1 pcs)
        - BOM Finishing tahap Closing: Stuffed Body (1 pcs) + Benang (Y meter) = Finished Doll (1 pcs)
    4.5. Packing
      - Input WIP: Boneka Jadi (Lolos QC).
      - Bahan Penolong (Request ke Warehouse): (Sesuai BOM / MO Manufacturing)
        - Master Box / Karton (Material Kritis - Penentu Stok FG).
        - Polybag (Plastik Pembungkus).
        - Lakban (Tape).
        - Silica Gel.
        - Stiker Barcode.
        - Pallet (Untuk Pengiriman).
        - Dan lainnya sesuai kebutuhan.
      - Activity: Packing mengambil kardus dan palet sesuai target packing hari itu.
    
    Workflow Proses Produksi Baru:
      **Main Production Flow:**
      - Purchase (Material Kain dan Label) -> Warehouse Receiving -> Manufacturing (Cutting -> Embroidery (Optional) -> Sewing) -> **Warehouse Finishing (Internal Conversion)** -> Manufacturing (Finishing: Stuffing & Closing -> Packing) -> Finish Good Inventory
      
      **Material Supply dari Warehouse ke Departemen:**
      - Warehouse Main -> Cutting (Kain, Marker, Plastik Bundle, dll sesuai BOM)
      - Warehouse Main -> Embroidery (Benang Bordir, Kain Keras, dll sesuai BOM)
      - Warehouse Main -> Sewing (Benang Jahit, Label Identity, dll sesuai BOM)
      - Warehouse Main -> Finishing Stuffing (Kapas/Dacron sesuai BOM)
      - Warehouse Main -> Finishing Closing (Benang Jahit Tangan, Hangtag, dll sesuai BOM)
      - Warehouse Main -> Packing (Karton, Polybag, Lakban, dll sesuai BOM)
      
      **WIP Transfer Antar Departemen:**
      - Cutting -> Embroidery (WIP: Potongan Kain) [dengan Surat Jalan]
      - Embroidery -> Sewing (WIP: Potongan Bordir) [dengan Surat Jalan]
      - Cutting -> Sewing (WIP: Potongan Kain Polos, jika tanpa Embroidery) [dengan Surat Jalan]
      - Sewing -> Warehouse Finishing (WIP: Skin belum isi) [dengan Surat Jalan]
      
      **Warehouse Finishing - Internal Conversion (NO Surat Jalan):**
      - Stok 1: Skin (dari Sewing)
      - Process: Stuffing (Skin + Kapas -> Stuffed Body) [Log produksi internal, stok Skin berkurang, Stuffed Body bertambah]
      - Stok 2: Stuffed Body (intermediate WIP, ready untuk Closing)
      - Process: Closing (Stuffed Body + Benang -> Finished Doll) [Stok Stuffed Body berkurang]
      
      **Final Transfer:**
      - Warehouse Finishing -> Packing (Finished Doll hasil Closing) [dengan Surat Jalan]
      - Packing -> Finish Good Inventory (Boxed Product) [dengan Barcode Scan]
      
      **External Vendor Flow (Optional):**
      - Embroidery -> Vendor (Potongan Kain untuk proses khusus) [dengan Surat Jalan]
      - Vendor -> Embroidery (Potongan hasil proses vendor) [dengan Surat Jalan + QC]
      
      **Catatan Penting:**
      - ⚠️ Warehouse Finishing mengelola 2 jenis stok berbeda: (1) Skin dan (2) Stuffed Body
      - 🔄 Internal Conversion di Warehouse Finishing TIDAK memerlukan Surat Jalan, hanya log produksi internal
      - ✅ Validasi: Stuffing perlu stok Skin > 0, Closing perlu stok Stuffed Body > 0
      - 📦 Transfer keluar Warehouse Finishing (ke Packing) WAJIB pakai Surat Jalan

5.  Production dibagi menjadi beberapa departemen: Cutting -> Embroidery (jika ada) -> Sewing -> Finishing -> Packing. Setiap departemen membuat SPK/WO sendiri berdasarkan Week Planning Production yang ditentukan di MO Manufacturing.
6.  MO Manufacturing dibuat secara otomatis atau manual berdasarkan ketersediaan/PO Material Label.
      - Datestamp (Week Production) dan Destination (Gudang Tujuan) pada MO diwariskan/diambil dari data yang ada pada PO Label.
      - Jika PO Label belum ada, MO tidak dapat dijadwalkan (System Lock), meskipun kain sudah tersedia.
7.  PO Purchasing (Material) dibuat berdasarkan BOM Purchasing berisikan rencana pembelian material dari supplier. Namun karena untuk pembuatan POnya dilakukan oleh admin berbeda, maka PO Purchasing (Material) tidak menjadi trigger utama untuk pembuatan MO Manufacturing. Trigger utama untuk pembuatan MO Manufacturing adalah PO Purchasing (Material Label) yang berisikan informasi lengkap tentang rencana pembelian material label dari supplier.
8. Alur proses produksi dimulai dari PO Purchasing (Material Label) yang menjadi trigger utama untuk pembuatan MO Manufacturing (PPIC) dan SPK/WO di setiap departemen produksi hingga produk jadi diterima di Finish Good Inventory.
9.  Structurenya
    - PO IKEA (SPI) (Rencana pembelian dari IKEA, forecast 2 mingguan) (Tidak diinputkan dalam ERP)
      - PO Purchasing (Material Non-Label: Kain, dll)
      - PO Purchasing (Material Label) -> TRIGGER UTAMA
        - Menghasilkan MO Purchasing (Material)
        - Menghasilkan MO Manufacturing (PPIC) (Week & Destination ikut Label)
          - SPK (Surat Perintah Kerja)/WO (Work order) Cutting
          - SPK/WO Embroidery (Jika ada)
          - SPK/WO Sewing
          - SPK/WO Finishing
          - SPK/WO Packing
        - Finish Good (FG) Inventory (Receiving and Shipping)
        - PO Material (Karton)
10. PO Purchasing berisikan informasi lengkap tentang rencana pembelian material dari supplier, termasuk:
    - PO Purchasing Document
      - No PO IKEA (Auto dari PO IKEA terkait) (SPI) (Tidak Wajib)
      - No PO Purchasing
      - Tanggal PO Purchasing
      - Material yang dipesan
        - Supplier
        - Kode jenis material* (Raw Material, Bahan Penolong) 
        - Kode material
        - Deskripsi material
        - Jumlah yang dipesan
        - Satuan
        - Harga per unit
        - Total harga
      - Tanggal perkiraan kedatangan material
      - Status PO Purchasing (Pending, Approved, Received, Cancelled)
11. MO berisikan informasi lengkap tentang rencana produksi berdasarkan PO Purchasing, termasuk:
    - MO Manufacturing Document
      - No PO Purchasing (Auto dari PO Purchasing terkait)
      - No MO Manufacturing
      - Week Planning Production (Perencanaan produksi mingguan berdasarkan PO Purchasing dan kapasitas produksi)
      - Nomor Artikel (Auto dari PO Purchasing terkait)
      - Nama Produk (Auto dari PO Purchasing terkait)
      - Kode Artikel (Auto dari PO Purchasing terkait)
      - Deskripsi/Product Information (Auto dari PO Purchasing terkait)
      - Jumlah yang direncanakan untuk diproduksi
      - Tanggal Mulai Produksi (Start Production Date)
      - Tanggal Selesai Produksi (End Production Date)
      - Status MO (Planned, In Progress, Completed, Cancelled)
12. SPK/WO berikan informasi lengkap tentang proses produksi di setiap departemen, termasuk:
    - SPK/WO Document
      - No PO Purchasing (Auto dari MO Manufacturing terkait)
      - No MO Manufacturing
        - No SPK/WO (Surat Perintah Kerja/Work Order)
        - Week Planning Production (Auto dari MO Manufacturing terkait)
      - Nama Produk (Auto dari MO Manufacturing terkait)
      - Kode Artikel (Auto dari MO Manufacturing terkait)
      - Deskripsi/Product Information (Auto dari MO Manufacturing terkait)
      - Material yang digunakan (Auto dari BOM Manufacturing terkait MO Manufacturing)
        - Kode jenis material* (Raw Material, Bahan Penolong, WIP) (Auto dari BOM Manufacturing terkait MO Manufacturing)
        - Kode material (Auto dari BOM Manufacturing terkait MO Manufacturing)
        - Deskripsi material (Auto dari BOM Manufacturing terkait MO Manufacturing)
      - Jumlah material yang digunakan (Daily Material Input)
        - Pcs (Pieces)
        - Satuan (Unit)
        - Yard/Meter (Cutting)
        - Box/Dus (Packing)
        - Gram (Finishing - Isi Kapas)
      - Jumlah yang diproduksi (Daily Production Input)
        - Pcs (Pieces)
      - Tanggal Mulai Produksi (Start Production Date Departemen Cutting)
      - Tanggal Selesai Produksi (End Production Date Departemen Packing)
      - Nomor batch
      - Status QC
      - Lokasi penyimpanan di gudang bayangan departemen (Jika ada)
      - Catatan tambahan
13. Document finish good berisikan informasi lengkap tentang produk jadi, termasuk:
    - Finish Good (FG) Document  
      - No PO IKEA (Auto dari BOM Manufacturing terkait MO Manufacturing)
      - No PO Purchasing (Auto dari BOM Manufacturing terkait MO Manufacturing)
      - No MO Manufacturing
        - No SPK/WO (Surat Perintah Kerja/Work Order)
        - Week Planning Production (Auto dari BOM Manufacturing terkait MO Manufacturing)
      - Nama Produk (Auto dari BOM Manufacturing terkait MO Manufacturing)
      - Kode Artikel (Auto dari BOM Manufacturing terkait MO Manufacturing)
      - Deskripsi/Product Information (Auto dari BOM Manufacturing terkait MO Manufacturing)
      - Informasi Kuantitas & Konversi (Wajib Ada)
        - Satuan Utama Inventory (Pieces)
        - Satuan Packing: Box/Dus
        - Nilai Konversi UOM (Unit of Measure) (Contoh: 1 Box = 50 Pieces)
      - Jumlah Produk Jadi yang Diterima di Gudang FG (auto-convert)
        - Input User (Packing): Jumlah Box/Dus yang diterima
        - System Record (Inventory): 500 Pcs (50 Dus x 10).
      - Tanggal Mulai Produksi -> Berdasarkan data dari Cutting (Tanggal mulai produksi pertama)
      - Tanggal diterima di gudang FG (Receiving Date)
      - Tanggal pengiriman ke customer (Shipping Date)
      - No/Kode ECIS (jika ada) -> Berdasarkan data dari EXIM
      - Nomor batch
      - Status QC
      - Lokasi penyimpanan di gudang
      - Informasi pengiriman (jika sudah dikirim)
      - Catatan tambahan
14. Setiap departement, walau alur produksinya dimulai dari PO Purchasing, tetap akan melakukan receiving material bahan dari Warehouse Receiving sebelum memulai produksi.*
15. Setiap departemen menerima WIP (Cutting, Embroidery, Sewing) dari departemen sebelumnya untuk diproses lebih lanjut hingga menjadi product jadi di Finishing.
16. Setiap departemen memiliki warehouse bayangan sendiri. Hasil dari Sewing (Skin/WIP) akan disimpan di gudang bayangan Finishing. Di dalam departemen Finishing, WIP tersebut akan diproses: Stuffing (Isi Kapas) -> Closing (Jahit Tutup) -> Cleaning/QC Akhir. Setelah selesai, barang diserahkan ke Packing.
    - **Warehouse Finishing Internal Conversion**: Perubahan status stok dari Skin menjadi Stuffed Body di dalam Warehouse Finishing tidak memerlukan Surat Jalan antar departemen, cukup dengan log produksi internal yang mencatat: timestamp, operator, qty Skin consumed, qty Stuffed Body produced, dan qty Kapas used.
    - **Dual Inventory Type**: Warehouse Finishing mengelola 2 jenis stok berbeda: (1) Skin/WIP dari Sewing, dan (2) Stuffed Body yang sudah diisi kapas tapi belum di-closing.
    - **Material Consumption Tracking**: Kapas dikonsumsi dan dicatat pada tahap Stuffing, bukan Closing. Benang jahit tangan dikonsumsi pada tahap Closing.
17. Tampilan report dan dashboard dapat diatur sesuai kebutuhan setiap departemen untuk memantau kinerja produksi mereka masing-masing.
18. Barang Jadi dari Packing masuk ke FinishGood Inventory otomatis menarik data dari SPK/WO Packing terkait untuk update stok FG Inventory. Lalu dikonfirmasi menggunakan Scan Barcode pada box/pallet FG saat receiving di gudang FG. Setiap dilakukan scan barcode pada box/pallet FG saat receiving di gudang FG, maka stok FG Inventory akan bertambah sesuai qty product jadi yang diterima. Tampilan report dan dashboard FinishGood Inventory dapat diatur sesuai kebutuhan untuk memantau stok barang jadi secara real-time.
19. Finishing memiliki gudang bayangan sendiri (Warehouse Finishing) untuk menyimpan 2 jenis material: (1) Skin/WIP dari Sewing yang belum diisi kapas, dan (2) Stuffed Body yang sudah diisi kapas tapi belum di-closing. Internal conversion dari Skin ke Stuffed Body dicatat sebagai log produksi internal tanpa surat jalan, dengan validasi stok: Stuffing tidak bisa jalan jika stok Skin = 0, Closing tidak bisa jalan jika stok Stuffed Body = 0.
20. Setiap perpindahan material/barang jadi/barang setengah jadi antar departemen dicatat secara digital di sistem ERP untuk pelacakan lengkap dengan tanda serah terima barang atau surat jalan yang berisikan keterangan lengkap datestamp, nama product, qty, departemen pengirim, departemen penerima, dan operator yang bertanggung jawab.
21. Setiap departemen memiliki dashboard yang menampilkan status produksi mereka secara real-time, termasuk progress harian, target produksi, dan kendala yang dihadapi.
22. Setiap departemen dapat memilih untuk otomatis (1 click) membuat SPK/WO berdasarkan Week Planning Production yang telah ditentukan di MO Manufacturing (Penarikan informasi nya), atau membuat SPK/WO secara manual sesuai kebutuhan mendesak.
23. Label Validation Rule: Pada form pembuatan MO, field "Nomor PO Label" adalah Mandatory (Wajib). Sistem harus memvalidasi apakah PO Label tersebut statusnya sudah Approved/On-Order. Jika belum, sistem menampilkan error dan tidak mengizinkan pembuatan MO Manufacturing, meskipun kain sudah tersedia di warehouse.
24. Inheritance Rule: Field Week dan Destination di MO Manufacturing harus Read-Only (Tidak bisa diedit manual), nilainya otomatis mengambil dari PO Label yang dipilih.
25. Inventory Calculation Rule: Saat Receiving FG, rumus penambahan stok gudang adalah: Qty Input (Dus) * Nilai Konversi = Stok Masuk (Pcs). Ini mencegah selisih stok antara fisik (dus) dan sistem (pcs).
26. MO bisa dibuat status Draft untuk menghitung kebutuhan kain, tapi tombol Release to SPK terkunci sampai Nomor PO Label diinput.
27. Rule Validate Datestamp hanya berjalan pada SPK/WO Sewing, Finishing, dan Packing. SPK Cutting dan Embroidery tidak perlu validasi datestamp.
28. Total produksi SPK per departemen tidak harus sesuai dengan jumlah di MO, karena ada kemungkinan reject/over produksi di departemen sebelumnya.
29. Daily Material Input dan Daily Production Input di setiap departemen harus diinput harian untuk tracking real-time di dalam SPK/WO.
30. Apa yang sudah terinput daily pada SPK tidak dapat diubah atau diinput ulang, sebelum product jadi diterima di gudang FG.
31. Setelah product jadi diterima di gudang FG, sistem mengunci semua Daily Input di SPK terkait untuk mencegah perubahan data historis. Adjustment product dilakukan dengan pembuatan SPK baru (Ada tanda/keterangan SPK Tambahan. Hanya dapat dibuat menggunakan account SPV dan wajib dengan approval Manager).
32. Setiap departemen dapat mengakses laporan produksi harian, mingguan, dan bulanan untuk analisis kinerja dan perencanaan ke depan.
33. UOM Conversion juga ada pada departemen Cutting dan Packing harus diterapkan untuk konsistensi pelaporan stok dan produksi.
34. Sistem harus mendukung integrasi dengan sistem EXIM untuk otomatisasi pengisian data ECIS pada dokumen Finish Good.
35. Sistem harus mendukung pembuatan laporan kustom oleh setiap departemen sesuai kebutuhan mereka.
36. Sistem harus memiliki fitur notifikasi untuk mengingatkan admin atau manajer tentang status kritis, seperti keterlambatan produksi atau stok material yang menipis.
37. Fitur material Debt harus diimplementasikan untuk mengizinkan produksi berjalan meskipun stok material tidak mencukupi, dengan proses approval dan penyesuaian stok setelah MO dinyatakan selesai. Hanya berlaku untuk material bahan baku (Raw Material) dan bahan penolong (Auxiliary Material), tidak berlaku untuk WIP dan Finished Goods.
38. Setiap SPK di semua Departement akan memunculkan 2 tampilan SPK dalam 1 halaman: 
      - Tampilan utama untuk Daily Material Input dan Daily Production Input.
      - Tampilan sekunder untuk melihat rincian BOM Manufacturing yang digunakan di SPK tersebut (Non-editable).
39. Warehouse Finishing Internal Conversion: Sistem harus mengizinkan perubahan status stok di dalam Warehouse Finishing dari Skin menjadi Stuffed Body tanpa membuat Surat Jalan antar departemen. Cukup dengan log produksi internal yang mencatat timestamp, operator, qty converted, dan material consumed (kapas).
40. Validasi Stok Warehouse Finishing:
      - Proses Stuffing tidak bisa diinput di SPK Finishing jika stok Skin di Warehouse Finishing = 0. Sistem harus menampilkan error: "Stok Skin tidak tersedia, proses Stuffing tidak dapat dilakukan".
      - Proses Closing tidak bisa diinput di SPK Finishing jika stok Stuffed Body di Warehouse Finishing = 0. Sistem harus menampilkan error: "Stok Stuffed Body tidak tersedia, proses Closing tidak dapat dilakukan".
      - Validasi dilakukan real-time saat operator melakukan Daily Input di SPK Finishing.
41. BOM Finishing Logic:
      - BOM Finishing harus dibagi menjadi 2 tahap terpisah:
        * **Tahap 1 - Stuffing**: Input (Skin + Kapas) → Output (Stuffed Body). Kapas dikonsumsi dan dicatat pada tahap ini.
        * **Tahap 2 - Closing**: Input (Stuffed Body + Benang Jahit Tangan) → Output (Finished Doll). Benang dikonsumsi pada tahap ini.
      - Ini penting untuk akurasi perhitungan stok kapas dan tracking material consumption per tahap proses.
      - Daily Material Input di SPK Finishing harus sesuai dengan tahap yang sedang dikerjakan (Stuffing input kapas, Closing input benang).
42. Material Request Flow: Setiap departemen dapat membuat Material Request ke Warehouse untuk permintaan material tambahan diluar BOM. Material Request harus mendapat approval dari SPV departemen dan Warehouse Manager sebelum material dikeluarkan.
43. Rejection & Rework Handling: Produk yang ditolak QC akan dicatat sebagai Rejection dan dapat dibuat Rework SPK untuk perbaikan. Rework SPK akan mencatat jumlah reject, penyebab reject, dan material tambahan yang dibutuhkan untuk perbaikan.
44. Quality Control Checkpoint: QC dilakukan di setiap akhir departemen sebelum WIP/FG diserahkan ke departemen berikutnya. Setiap QC checkpoint mencatat hasil inspeksi, jumlah pass, jumlah reject, dan catatan defect.
45. Barcode System: Setiap material, WIP, dan FG memiliki barcode unik untuk tracking. Barcode digunakan untuk receiving, material issue, transfer antar departemen, dan shipping.
46. Traceability: Sistem harus dapat melacak setiap produk jadi dari bahan baku awal hingga pengiriman ke customer, termasuk batch material, operator yang menangani, dan hasil QC di setiap stage.
47. Capacity Planning: PPIC dapat melihat kapasitas produksi setiap departemen dan merencanakan schedule produksi berdasarkan kapasitas tersebut. Sistem memberikan warning jika schedule melebihi kapasitas.
48. Material Shortage Alert: Sistem otomatis memberikan notifikasi ketika stok material mencapai minimum level atau ketika material yang dibutuhkan untuk MO tidak tersedia di warehouse.
49. Overtime & Shift Management: Sistem mencatat overtime dan shift kerja operator di setiap departemen untuk perhitungan productivity dan costing.
50. Vendor Management: Sistem mencatat performance vendor berdasarkan on-time delivery, quality material yang dikirim, dan lead time actual vs planned.
51. Cost Tracking: Setiap SPK mencatat actual cost yang dikeluarkan (material cost, labor cost, overhead cost) untuk dibandingkan dengan standard cost dari BOM.
52. Dashboard KPI: Dashboard menampilkan KPI utama seperti OEE (Overall Equipment Effectiveness), On-Time Delivery Rate, First Pass Yield, Material Utilization Rate, dan Production Efficiency per departemen.
53. Mobile App Integration: Operator dapat melakukan Daily Input, QC Check, dan Material Request melalui mobile app untuk kemudahan penggunaan di production floor.
54. Approval Workflow: Setiap transaksi kritis (Material Request, Rework SPK, SPK Tambahan, Material Debt) harus melalui approval workflow multi-level sesuai dengan authority matrix.

## 🏭 SPK FINISHING - DETAIL IMPLEMENTATION

### Tampilan SPK Finishing
SPK Finishing memiliki 2 tab terpisah untuk 2 tahap proses yang berbeda:

#### Tab 1: Stuffing Process
**Input Form:**
- Date/Shift
- Operator Name
- Machine/Line Number
- **Material Input**:
  - Skin (Pcs) - Auto-check stok dari Warehouse Finishing
  - Kapas (Gram) - Sesuai standard BOM, input actual usage
  - Material penolong lain (jika ada)
- **Production Output**:
  - Stuffed Body Produced (Pcs)
  - Reject (Pcs) + Defect Type (jika ada)
- **Quality Check**:
  - Weight Check (Gram per piece) - Pastikan berat kapas sesuai standard
  - Visual Inspection Result
- Notes/Remarks

**Validasi:**
- ❌ Form tidak bisa submit jika stok Skin di Warehouse Finishing = 0
- ⚠️ Warning jika actual kapas usage > 10% dari standard BOM
- ✅ Success submit: Stok Skin berkurang, stok Stuffed Body bertambah (internal conversion)

**Log yang Tercatat:**
```json
{
  "process_type": "Stuffing",
  "timestamp": "2026-01-30 08:15:00",
  "operator": "OP-FIN-001",
  "spk_no": "SPK-FIN-202601-001",
  "material_consumed": {
    "Skin": {"qty": 100, "unit": "pcs", "from_warehouse": "WH-Finishing"},
    "Kapas": {"qty": 15000, "unit": "gram", "from_warehouse": "WH-Main"}
  },
  "output_produced": {
    "Stuffed_Body": {"qty": 98, "unit": "pcs", "to_warehouse": "WH-Finishing"},
    "Reject": {"qty": 2, "reason": "Uneven stuffing"}
  },
  "conversion_status": "Skin → Stuffed Body (Internal)",
  "surat_jalan": null
}
```

#### Tab 2: Closing Process
**Input Form:**
- Date/Shift
- Operator Name
- Workstation Number
- **Material Input**:
  - Stuffed Body (Pcs) - Auto-check stok dari Warehouse Finishing
  - Benang Jahit Tangan (Meter/Roll) - Input actual usage
  - Hangtag, Price Tag (Pcs)
  - Cleaning fluid (ml) - optional
- **Production Output**:
  - Finished Doll (Pcs)
  - Reject (Pcs) + Defect Type (jika ada)
- **Quality Check**:
  - Closing stitch quality
  - Cleaning result
  - Final inspection before Packing
- Notes/Remarks

**Validasi:**
- ❌ Form tidak bisa submit jika stok Stuffed Body di Warehouse Finishing = 0
- ⚠️ Warning jika reject rate > 5%
- ✅ Success submit: Stok Stuffed Body berkurang, produk diserahkan ke Packing (keluar dari Warehouse Finishing)

**Log yang Tercatat:**
```json
{
  "process_type": "Closing",
  "timestamp": "2026-01-30 14:30:00",
  "operator": "OP-FIN-005",
  "spk_no": "SPK-FIN-202601-001",
  "material_consumed": {
    "Stuffed_Body": {"qty": 98, "unit": "pcs", "from_warehouse": "WH-Finishing"},
    "Benang_Jahit": {"qty": 196, "unit": "meter", "from_warehouse": "WH-Main"},
    "Hangtag": {"qty": 98, "unit": "pcs", "from_warehouse": "WH-Main"}
  },
  "output_produced": {
    "Finished_Doll": {"qty": 96, "unit": "pcs", "to_department": "Packing"},
    "Reject": {"qty": 2, "reason": "Closing stitch not neat"}
  },
  "transfer_status": "WH-Finishing → Packing Dept",
  "surat_jalan": "SJ-FIN-PKG-20260130-001"
}
```

### BOM Finishing Structure

**BOM Artikel: Teddy Bear 30cm**

**Stage 1: Stuffing**
| Material Code | Material Name | Qty | Unit | Type | Consumption Point |
|---------------|---------------|-----|------|------|-------------------|
| WIP-SKIN-001 | Teddy Bear Skin | 1 | pcs | WIP | Input |
| RM-KAPAS-001 | Dacron Fiber | 150 | gram | Raw Material | Stuffing |
| - | - | - | - | - | - |
| **OUTPUT** | **Stuffed Body** | **1** | **pcs** | **WIP** | **Intermediate** |

**Stage 2: Closing**
| Material Code | Material Name | Qty | Unit | Type | Consumption Point |
|---------------|---------------|-----|------|------|-------------------|
| WIP-STF-001 | Stuffed Body | 1 | pcs | WIP | Input |
| RM-BNG-002 | Hand Stitch Thread | 2 | meter | Raw Material | Closing |
| ACC-TAG-001 | Hangtag IKEA | 1 | pcs | Accessory | Closing |
| AUX-CLN-001 | Cleaning Fluid | 5 | ml | Auxiliary | Cleaning |
| - | - | - | - | - | - |
| **OUTPUT** | **Finished Doll** | **1** | **pcs** | **Finished Good** | **Final** |

### Dashboard Warehouse Finishing

**Real-time Stock Monitor:**
```
╔══════════════════════════════════════════════════════════╗
║  WAREHOUSE FINISHING - STOCK STATUS                      ║
║  Updated: 2026-01-30 15:45:00                           ║
╠══════════════════════════════════════════════════════════╣
║                                                          ║
║  📦 SKIN (from Sewing)                                   ║
║  ├─ Available: 1,250 pcs                                ║
║  ├─ Reserved for SPK: 500 pcs                           ║
║  └─ Free Stock: 750 pcs            [⚠️ Below Min: 1000] ║
║                                                          ║
║  🧸 STUFFED BODY (ready for Closing)                     ║
║  ├─ Available: 2,100 pcs                                ║
║  ├─ In Closing Process: 300 pcs                         ║
║  └─ Free Stock: 1,800 pcs                    [✅ Normal] ║
║                                                          ║
║  📊 Conversion Rate Today                                ║
║  ├─ Skin → Stuffed Body: 450 pcs (Target: 500)          ║
║  ├─ Stuffed Body → Finished: 420 pcs (Target: 480)      ║
║  └─ Overall Efficiency: 91% (Target: 95%)               ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
```

**Alert System:**
1. **Critical**: Stok Skin < 500 pcs → Block Stuffing process
2. **Warning**: Stok Skin < 1000 pcs → Notify SPV & PPIC
3. **Critical**: Stok Stuffed Body < 200 pcs → Block Closing process
4. **Warning**: Stok Stuffed Body < 500 pcs → Notify SPV Finishing
5. **Info**: Daily target not met → Report to Production Manager

## 🔐 USER ROLES & PERMISSIONS

### Admin Level
- **Super Admin**: Full access ke semua modul, setting system, user management
- **IT Admin**: Maintenance system, backup data, technical support

### Management Level
- **General Manager**: View all reports, approval authority tertinggi, strategic planning
- **Production Manager**: Approval SPK Tambahan, Rework, Material Debt, monitoring overall production
- **Warehouse Manager**: Approval Material Issue, Material Request, stock adjustment
- **PPIC Manager**: Create & edit MO, approval PO to MO conversion, capacity planning
- **QC Manager**: Approval reject product, final QC decision, quality standard setting

### Supervisor Level
- **SPV Production**: Create SPK Tambahan, approval daily input, monitoring departemen
- **SPV Warehouse**: Approval material issue, receiving material, stock opname
- **SPV QC**: QC inspection, approval minor reject, quality recording

### Operator Level
- **PPIC Staff**: Create PO Purchasing, create MO Manufacturing, planning production schedule
- **Purchasing Staff**: Create & manage PO Purchasing, vendor coordination
- **Warehouse Staff**: Receiving material, material issue, stock recording
- **Production Operator**: Daily Material Input, Daily Production Input, WIP transfer
- **QC Inspector**: QC inspection, recording defect, quality check
- **Packing Operator**: Packing process, FG barcode scanning, shipping preparation

### Viewer Level
- **Finance Viewer**: View cost reports, production costing, material valuation
- **Management Viewer**: View all reports without edit permission

## 📊 REPORTING REQUIREMENTS

### Daily Reports
1. **Daily Production Report**: Produksi harian per departemen (target vs actual)
2. **Daily Material Consumption**: Konsumsi material harian vs standard BOM
3. **Daily QC Report**: Hasil QC harian (pass, reject, defect type)
4. **Daily Attendance**: Kehadiran operator dan productivity per operator
5. **Daily Material Request**: Permintaan material tambahan yang dibuat hari ini
6. **Daily Warehouse Finishing Movement**: Laporan khusus internal conversion Skin → Stuffed Body dan transfer ke Packing
   - Opening Stock (Skin & Stuffed Body)
   - Received from Sewing (Skin)
   - Stuffing Conversion (Skin → Stuffed Body)
   - Closing Transfer (Stuffed Body → Packing)
   - Reject & Rework
   - Closing Stock (Skin & Stuffed Body)
   - Kapas Consumption (Actual vs Standard)
   - Alert: Stok di bawah minimum level

### Weekly Reports
1. **Weekly Production Summary**: Ringkasan produksi mingguan per artikel dan departemen
2. **Weekly Material Usage Variance**: Selisih penggunaan material actual vs standard
3. **Weekly WIP Inventory**: Stok WIP di setiap departemen end of week
4. **Weekly OEE Report**: Overall Equipment Effectiveness per departemen
5. **Weekly On-Time Delivery**: Persentase MO yang selesai on-time

### Monthly Reports
1. **Monthly Production Performance**: Kinerja produksi bulanan (efficiency, output, quality)
2. **Monthly Material Valuation**: Nilai inventory material end of month
3. **Monthly Rejection Analysis**: Analisis rejection per defect type dan root cause
4. **Monthly Cost Analysis**: Actual cost vs standard cost per artikel
5. **Monthly Vendor Performance**: Performance vendor (delivery, quality, lead time)
6. **Monthly Capacity Utilization**: Tingkat utilisasi kapasitas per departemen

### Management Reports
1. **Production Forecast vs Actual**: Perbandingan forecast dengan actual achievement
2. **Profitability Analysis**: Analisis profitabilitas per artikel dan per customer
3. **Inventory Aging Report**: Umur inventory material dan FG
4. **Material Debt Outstanding**: Daftar material debt yang belum diselesaikan
5. **Critical Material Status**: Status material kritis (low stock, long lead time)

## 🔄 MATERIAL REQUEST & APPROVAL FLOW

### Material Request Types
1. **Regular Material Request**: Permintaan material sesuai BOM untuk produksi normal
   - Auto-approved jika stok tersedia dan sesuai BOM
   - Langsung dikurangi dari warehouse inventory
   
2. **Additional Material Request**: Permintaan material tambahan diluar BOM
   - Approval: SPV Production → Warehouse Manager
   - Alasan wajib diisi (contoh: reject, over consumption, trial)
   - Dicatat sebagai variance dari standard BOM
   
3. **Emergency Material Request**: Permintaan material mendesak diluar schedule
   - Approval: SPV Production → Production Manager
   - Priority tinggi, warehouse harus process maksimal 2 jam
   - Harus ada justifikasi kuat (contoh: breakdown, urgent order)

### Material Debt Mechanism
1. **Material Debt Creation**:
   - Terjadi ketika stok material tidak mencukupi tapi produksi harus jalan
   - Sistem record sebagai "Material Debt" dengan qty yang di-debt
   - Approval: Production Manager → General Manager
   - Hanya untuk Raw Material dan Auxiliary Material
   
2. **Material Debt Settlement**:
   - Ketika material datang, system auto-adjust dan close debt
   - Jika produksi selesai sebelum settlement, wajib adjustment manual
   - Report Material Debt Outstanding harus review weekly

3. **Material Debt Limitation**:
   - Maximum 3 active debt per artikel
   - Maximum debt value per artikel: 10% dari total MO value
   - Debt tidak boleh lebih dari 14 hari (warning di dashboard)

## ❌ REJECTION & REWORK HANDLING

### Rejection Process
1. **QC Rejection Recording**:
   - QC Inspector scan barcode product/WIP yang reject
   - Input reject quantity dan defect type
   - Upload foto evidence (mandatory untuk major defect)
   - Reject product dipindah ke area isolasi

2. **Defect Classification**:
   - **Critical**: Safety issue, tidak bisa dirework (scrap)
   - **Major**: Defect signifikan, bisa dirework dengan effort tinggi
   - **Minor**: Defect kecil, mudah diperbaiki
   
3. **Rejection Approval**:
   - Minor reject: SPV QC dapat approve langsung
   - Major reject: QC Manager approval
   - Critical reject: Production Manager + QC Manager approval

### Rework Process
1. **Rework Decision**:
   - Jika reject bisa diperbaiki, QC create Rework Request
   - Rework Request mencantumkan: qty reject, defect type, estimated effort, material tambahan
   - Approval: SPV Production → Production Manager

2. **Rework SPK Creation**:
   - System create Rework SPK linked ke SPK original
   - Rework SPK include: parent SPK, qty to rework, rework instruction, additional material
   - Priority: Normal atau Urgent (tergantung deadline MO)

3. **Rework Execution**:
   - Operator process rework sesuai instruction
   - Daily input untuk rework terpisah dari produksi normal
   - Setelah rework selesai, QC inspect ulang

4. **Rework Costing**:
   - Rework cost (labor + material) dicatat terpisah
   - Report menampilkan rework cost per artikel dan per defect type
   - Rework cost dipakai untuk vendor evaluation jika material issue

## 🏷️ BARCODE IMPLEMENTATION

### Barcode Format
1. **Material Barcode**: MTR-[Material Code]-[Batch No]-[Date]
   - Contoh: MTR-KN001-B202601-20260130
   
2. **WIP Barcode**: WIP-[SPK No]-[Dept]-[Batch]-[Seq]
   - Contoh: WIP-SPK202601001-CTT-B01-001
   
3. **FG Barcode**: FG-[Artikel]-[Week]-[Box No]
   - Contoh: FG-ART12345-W0526-001
   
4. **Pallet Barcode**: PLT-[FG]-[Pallet No]-[Total Box]
   - Contoh: PLT-FG-ART12345-P001-50

### Barcode Scanning Points
1. **Warehouse Receiving**: Scan material barcode saat receiving dari supplier
2. **Material Issue**: Scan material barcode saat issue ke departemen
3. **WIP Transfer**: Scan WIP barcode saat transfer antar departemen
4. **FG Receiving**: Scan FG box barcode saat receiving di gudang FG
5. **FG Shipping**: Scan pallet barcode saat loading ke container

### Barcode Printing
- Material barcode: Print otomatis saat receiving
- WIP barcode: Print saat departemen pertama (Cutting) complete cutting
- FG box barcode: Print saat packing selesai
- Pallet barcode: Print saat FG packing di-pallet

## 🔗 SYSTEM INTEGRATION POINTS

### 1. EXIM System Integration
- **Direction**: Bi-directional
- **Data Flow**: 
  - ERP → EXIM: FG data, shipping schedule, article info
  - EXIM → ERP: ECIS code, customs status, shipping confirmation
- **Integration Method**: REST API real-time
- **Sync Frequency**: Real-time untuk shipping, daily untuk master data

### 2. Barcode Scanner Integration
- **Device**: Handheld scanner, fixed scanner, mobile app
- **Protocol**: Bluetooth, WiFi, USB
- **Data Capture**: Material code, WIP code, FG code, quantity
- **Offline Mode**: Support offline scanning dengan sync when online

### 3. Financial System Integration
- **Direction**: One-way (ERP → Financial)
- **Data Flow**: 
  - Production cost (material, labor, overhead)
  - Inventory valuation
  - Purchase order value
- **Integration Method**: Daily batch file transfer
- **Format**: CSV atau API

### 4. Email/SMS Notification System
- **Use Cases**: 
  - Alert material shortage
  - Approval request notification
  - Production milestone notification
  - QC rejection alert
- **Priority Level**: Critical, High, Normal, Low
- **Delivery Method**: Email, SMS, Push notification (mobile app)

### 5. Mobile App Integration
- **Platform**: Android (minimum Android 8.0)
- **Features**: 
  - Daily Material Input
  - Daily Production Input
  - QC Inspection
  - Material Request
  - Barcode Scanning
  - Real-time Dashboard
- **Connectivity**: Online mode (real-time sync), Offline mode (queue sync)

## 📚 GLOSSARY ISTILAH PENTING

*Week Planning Production*: Perencanaan produksi mingguan berdasarkan PO Purchasing dan kapasitas produksi. (Mengikat pada MO Manufacturing dan SPK/WO, tidak dapat diubah setelah dibuat).
*Destination*: Tujuan produk jadi berdasarkan PO Label terkait pada MO Manufacturing.
*Kode jenis material*:
  - Raw Material (Bahan Baku) (Contoh: kain, karton, label, benang)
  - Bahan Penolong (Auxiliary Material) (Contoh: perekat, benang jahit, aksesoris kecil)
  - Work-in-Progress (WIP) (Material setengah jadi antar departemen, biasanya berupa skin bahan yang sudah dipotong tapi belum selesai) (Setiap departemen menerima WIP (Cutting, Sewing) dari departemen sebelumnya untuk diproses lebih lanjut hingga menjadi product jadi di Finishing)
  - Barang Jadi (Finished Goods) (Produk jadi yang siap kirim ke customer)
*Goods Inventory*: Gudang penyimpanan material bahan baku, bahan penolong, WIP, dan barang jadi.
*Warehouse Receiving*: Proses penerimaan material bahan baku di gudang.
*Finish Good Inventory*: Gudang penyimpanan produk jadi siap kirim ke customer.
*Daily Material Input*: Input harian jumlah material yang digunakan di setiap departemen produksi.
*Daily Production Input*: Input harian jumlah produk yang dihasilkan di setiap departemen produksi.
*SPK Tambahan*: SPK baru yang dibuat untuk menyesuaikan jumlah produksi setelah product jadi diterima di gudang FG, hanya dapat dibuat oleh SPV dengan approval Manager.
*Scan Barcode*: Proses pemindaian barcode pada box/pallet FG saat receiving di gudang FG untuk konfirmasi penerimaan produk jadi. Dan penerimaan material di warehouse receiving.
*QT-09 Handshake*: Proses otomatis untuk menginformasikan departemen berikutnya bahwa material WIP sudah siap untuk diproses lebih lanjut.
*Adjustment Product*: Proses penyesuaian jumlah produksi melalui pembuatan SPK Tambahan setelah product jadi diterima di gudang FG.
*UOM Conversion*: Konversi satuan unit pengukuran untuk konsistensi pelaporan stok dan produksi di setiap departemen. Terutama pada departemen Cutting, Packing, dan FinishGood Inventory.
*Warehouse Finishing*: Gudang bayangan milik departemen Finishing untuk menyimpan 2 jenis stok: (1) Skin/WIP dari Sewing, dan (2) Stuffed Body yang sudah diisi kapas. Mengelola internal conversion dari Skin ke Stuffed Body tanpa surat jalan antar departemen.
*Internal Conversion*: Proses perubahan status stok di dalam gudang yang sama (contoh: Skin → Stuffed Body di Warehouse Finishing) yang dicatat sebagai log produksi internal tanpa memerlukan surat jalan antar departemen. Hanya berlaku untuk proses internal di dalam satu departemen.
*Stuffed Body*: Status WIP di Warehouse Finishing, yaitu Skin yang sudah diisi kapas tapi belum di-closing. Merupakan hasil dari proses Stuffing sebelum masuk ke proses Closing.
*Material Request*: Permintaan material dari departemen produksi ke warehouse, bisa regular (sesuai BOM), additional (diluar BOM), atau emergency (urgent).
*Material Debt*: Mekanisme yang memungkinkan produksi berjalan meskipun stok material tidak mencukupi, dengan pencatatan hutang material yang harus diselesaikan saat material datang.
*Rework SPK*: SPK khusus untuk memperbaiki produk yang reject dari QC, mencatat qty reject, defect type, dan material tambahan yang dibutuhkan.
*QC Checkpoint*: Titik pemeriksaan kualitas di setiap akhir proses departemen sebelum WIP/FG diserahkan ke departemen berikutnya.
*Defect Classification*: Klasifikasi jenis defect menjadi Critical (scrap), Major (rework dengan effort tinggi), atau Minor (mudah diperbaiki).
*Traceability*: Kemampuan sistem untuk melacak setiap produk jadi dari bahan baku awal hingga pengiriman ke customer, termasuk batch, operator, dan hasil QC.
*OEE (Overall Equipment Effectiveness)*: Metrik yang mengukur efektivitas equipment berdasarkan Availability x Performance x Quality.
*First Pass Yield*: Persentase produk yang lolos QC pada inspeksi pertama tanpa perlu rework.
*Material Utilization Rate*: Persentase penggunaan material actual dibandingkan dengan standard BOM.
*Capacity Planning*: Perencanaan schedule produksi berdasarkan kapasitas tersedia di setiap departemen.
*Authority Matrix*: Matriks yang mendefinisikan approval authority untuk setiap jenis transaksi berdasarkan value dan user role.
*Batch Tracking*: Pelacakan material dan produk berdasarkan nomor batch untuk quality control dan recall management.
*Production Milestone*: Titik-titik penting dalam proses produksi yang perlu dimonitor dan dilaporkan (contoh: cutting complete, sewing complete, packing complete).
*Variance Analysis*: Analisis perbedaan antara actual (material usage, cost, time) dengan standard/plan.
*Lead Time*: Waktu yang dibutuhkan dari PO created hingga material received, atau dari MO created hingga FG received.
*Stock Opname*: Proses perhitungan fisik inventory untuk memastikan kesesuaian antara stok fisik dengan stok system.
*Material Consumption Variance*: Selisih antara material yang seharusnya digunakan (sesuai BOM) dengan material yang actual digunakan dalam produksi.

## ⚠️ DEVELOPER NOTES - CRITICAL ATTENTION REQUIRED

### 🔴 PRIORITY 1: UOM Conversion Implementation

Dua modul ini adalah **TITIK KRITIS** yang paling rawan error dalam perhitungan inventory. **Developer WAJIB** memahami dengan detail dan implement dengan extra validation.

#### 1️⃣ Cutting Department - UOM Conversion (Meter/Yard → Pcs)

**Challenge:**
- Input: Kain dalam Meter atau Yard (Roll)
- Output: Potongan Kain dalam Pcs (Pieces)
- Conversion rate berbeda per artikel (tergantung ukuran pattern)

**Implementation Requirements:**

**A. Master Data Setup:**
```sql
-- Table: bom_cutting_conversion
artikel_code      VARCHAR(50)   -- "TEDDY-30CM"
marker_length     DECIMAL(10,2) -- Length marker dalam meter (contoh: 2.5 meter)
pieces_per_marker INT           -- Berapa pcs dalam 1 marker (contoh: 8 pcs)
fabric_width      DECIMAL(10,2) -- Lebar kain standard (contoh: 1.5 meter)
waste_percentage  DECIMAL(5,2)  -- Allowance waste (contoh: 5%)
```

**B. Calculation Formula:**
```javascript
// Input dari operator
const fabricUsed = 100; // meter
const markerLength = 2.5; // meter (dari BOM)
const piecesPerMarker = 8; // pcs (dari BOM)
const wastePercentage = 5; // % (dari BOM)

// Rumus Conversion
const totalMarkers = fabricUsed / markerLength; // 100 / 2.5 = 40 markers
const theoreticalOutput = totalMarkers * piecesPerMarker; // 40 * 8 = 320 pcs
const actualOutput = theoreticalOutput * (1 - wastePercentage/100); // 320 * 0.95 = 304 pcs

// Variance Check
const inputByOperator = 300; // pcs (actual yang diinput operator)
const variance = (inputByOperator - actualOutput) / actualOutput * 100; // -1.3%

if (Math.abs(variance) > 10) {
  showWarning("Output variance melebihi 10%, mohon verifikasi ulang!");
}
```

**C. Validation Rules:**
```javascript
// Rule 1: Output tidak boleh melebihi theoretical max
if (actualOutput > theoreticalOutput * 1.05) {
  throw new Error("Output melebihi kapasitas marker! Mohon cek input fabric used.");
}

// Rule 2: Fabric usage harus sesuai estimasi BOM
const bomEstimate = (targetOutput / piecesPerMarker) * markerLength;
const bomTolerance = bomEstimate * 1.1; // 10% tolerance

if (fabricUsed > bomTolerance) {
  showWarning("Penggunaan kain melebihi estimasi BOM +10%. Material Request tambahan diperlukan.");
}

// Rule 3: Daily input harus consistent
if (fabricUsedMeter === 0 && outputPcs > 0) {
  throw new Error("Input fabric tidak boleh 0 jika ada output pieces!");
}
```

**D. UI Requirements:**
- ✅ Auto-calculate expected output saat operator input fabric used
- ✅ Real-time variance indicator (Green: <5%, Yellow: 5-10%, Red: >10%)
- ⚠️ Warning popup jika variance >10%
- 📊 Display: "Fabric Used: 100m → Expected Output: ~304 pcs (±5%)"

**E. Reporting:**
```
Daily Cutting Report:
- Fabric Input: 100 meter
- Expected Output: 304 pcs (based on marker)
- Actual Output: 300 pcs
- Variance: -1.3% (Normal)
- Waste: 4.5 meter (4.5%)
```

---

#### 2️⃣ Finish Good Receiving - UOM Conversion (Dus/Box → Pcs)

**Challenge:**
- Operator Packing input dalam Box/Dus
- Sistem inventory record dalam Pcs (Pieces)
- Nilai konversi berbeda per artikel (box size bervariasi)

**Implementation Requirements:**

**A. Master Data Setup:**
```sql
-- Table: artikel_uom_conversion
artikel_code       VARCHAR(50)   -- "TEDDY-30CM"
uom_primary        VARCHAR(10)   -- "PCS" (satuan utama inventory)
uom_packing        VARCHAR(10)   -- "BOX" atau "DUS"
conversion_factor  INT           -- Isi per box (contoh: 24 pcs/box)
box_barcode_prefix VARCHAR(20)   -- "FG-TEDDY30-"
is_active          BOOLEAN       -- TRUE
```

**B. Calculation Formula:**
```javascript
// Scenario 1: Input dari Packing (Scan Box)
const boxScanned = 50; // box
const conversionFactor = 24; // pcs per box (dari master artikel)
const totalPcs = boxScanned * conversionFactor; // 50 * 24 = 1,200 pcs

// Update inventory
inventory.addStock({
  artikel_code: "TEDDY-30CM",
  qty_pcs: totalPcs,        // 1,200 (primary UOM)
  qty_box: boxScanned,       // 50 (secondary UOM - informasi saja)
  conversion_used: conversionFactor
});

// Scenario 2: Validasi saat input manual (tanpa barcode)
function validateBoxInput(articleCode, boxQty) {
  const master = getArticleMaster(articleCode);
  
  if (!master.conversion_factor) {
    throw new Error(`Artikel ${articleCode} belum setup UOM Conversion! Hubungi IT Admin.`);
  }
  
  const pcsCalculated = boxQty * master.conversion_factor;
  
  // Show confirmation
  return {
    input_box: boxQty,
    conversion_factor: master.conversion_factor,
    calculated_pcs: pcsCalculated,
    message: `${boxQty} Box = ${pcsCalculated} Pcs (@ ${master.conversion_factor} pcs/box)`
  };
}
```

**C. Validation Rules:**
```javascript
// Rule 1: Artikel WAJIB punya conversion factor
if (!artikel.conversion_factor) {
  throw new Error("UOM Conversion belum disetup untuk artikel ini. Proses receiving ditolak!");
}

// Rule 2: Conversion factor tidak boleh 0
if (artikel.conversion_factor <= 0) {
  throw new Error("Conversion factor invalid! Mohon hubungi IT Admin.");
}

// Rule 3: Cross-check dengan SPK Packing
const spkPackingOutput = getSPKPackingOutput(spkNo);
const expectedBox = Math.ceil(spkPackingOutput.total_pcs / artikel.conversion_factor);
const variance = Math.abs(inputBox - expectedBox) / expectedBox * 100;

if (variance > 15) {
  showWarning(`Input ${inputBox} box berbeda signifikan dengan SPK Packing (expected: ~${expectedBox} box). Mohon verifikasi!`);
  requireSPVApproval = true;
}

// Rule 4: Prevent duplicate receiving
if (isBoxBarcodeAlreadyScanned(boxBarcode)) {
  throw new Error(`Box barcode ${boxBarcode} sudah pernah di-scan sebelumnya!`);
}
```

**D. UI Requirements - Form Receiving FG:**
```
╔═══════════════════════════════════════════════════════╗
║  FINISH GOOD RECEIVING                                ║
╠═══════════════════════════════════════════════════════╣
║                                                       ║
║  Artikel: [TEDDY-30CM] Teddy Bear 30cm               ║
║  SPK No: SPK-PKG-202601-001                          ║
║                                                       ║
║  📦 INPUT BOX QUANTITY:                               ║
║  ┌─────────────────────────────────────────────────┐ ║
║  │  [  50  ] Box                                   │ ║
║  └─────────────────────────────────────────────────┘ ║
║                                                       ║
║  ℹ️  CONVERSION INFO:                                 ║
║  • Isi per Box: 24 pcs                               ║
║  • Total akan masuk: 1,200 pcs                       ║
║                                                       ║
║  ✅ Auto-calculation:                                 ║
║  50 Box × 24 pcs/box = 1,200 Pcs                     ║
║                                                       ║
║  📊 Comparison dengan SPK:                            ║
║  • SPK Target: 1,250 pcs (~52 box)                   ║
║  • Your Input: 1,200 pcs (50 box)                    ║
║  • Variance: -4% [✅ Normal]                          ║
║                                                       ║
║  [Confirm Receiving]  [Cancel]                       ║
║                                                       ║
╚═══════════════════════════════════════════════════════╝
```

**E. Database Transaction (ACID Compliance):**
```sql
BEGIN TRANSACTION;

-- 1. Insert receiving record
INSERT INTO fg_receiving (spk_no, artikel_code, receive_date, box_qty, pcs_qty, operator)
VALUES ('SPK-PKG-001', 'TEDDY-30CM', NOW(), 50, 1200, 'OP-WH-001');

-- 2. Update inventory stock (PRIMARY: PCS)
UPDATE inventory_fg 
SET qty_pcs = qty_pcs + 1200,
    last_updated = NOW()
WHERE artikel_code = 'TEDDY-30CM';

-- 3. Update SPK Packing status
UPDATE spk_packing
SET fg_received = TRUE,
    fg_received_date = NOW(),
    fg_received_qty_pcs = 1200
WHERE spk_no = 'SPK-PKG-001';

-- 4. Lock SPK daily input (prevent further changes)
UPDATE spk_daily_input
SET is_locked = TRUE
WHERE spk_no = 'SPK-PKG-001';

COMMIT;
```

**F. Critical Error Prevention:**
```javascript
// ❌ WRONG IMPLEMENTATION (Bahaya!)
inventory.qty = inputBox; // Salah! Langsung simpan box, harusnya convert ke pcs dulu

// ✅ CORRECT IMPLEMENTATION
const pcsCalculated = inputBox * conversionFactor;
inventory.qty_pcs = pcsCalculated; // Inventory SELALU dalam PCS
inventory.qty_box_info = inputBox; // Informasi saja, bukan primary stock
```

---

### 📋 Testing Checklist for Developer

**Cutting Module:**
- [ ] BOM Cutting Conversion master data lengkap untuk semua artikel
- [ ] Auto-calculation fabric → pieces berfungsi correct
- [ ] Variance warning muncul jika >10%
- [ ] Tidak bisa input 0 meter tapi output >0 pcs
- [ ] Reporting variance calculation correct

**FG Receiving Module:**
- [ ] Semua artikel sudah setup UOM Conversion Factor
- [ ] Error jika artikel belum setup conversion
- [ ] Auto-calculate Box → Pcs correct di UI
- [ ] Database transaction ACID compliant
- [ ] Inventory stock bertambah dalam PCS, bukan BOX
- [ ] SPK Packing auto-locked setelah FG received
- [ ] Barcode scanning prevent duplicate receiving
- [ ] Cross-check dengan SPK Packing berfungsi
- [ ] SPV approval required jika variance >15%

**Integration Testing:**
- [ ] End-to-end: SPK Cutting → Material Consumption → Inventory Update
- [ ] End-to-end: SPK Packing → FG Receiving → Inventory Update → SPK Lock
- [ ] Stress test: 1000 transactions dalam 1 hari
- [ ] Data consistency check: Sum SPK output = Inventory increase

---

### 🎓 Training Material Required

Developer harus prepare training material untuk:
1. **Admin PPIC**: Setup BOM Cutting Conversion per artikel
2. **Operator Cutting**: Cara input daily dengan UOM conversion
3. **Operator Packing**: Cara input box quantity dan understand conversion
4. **Warehouse FG**: Cara receiving dengan barcode scan dan manual input
5. **SPV Production**: Cara handle variance warning dan approval

## 🎯 BUSINESS RULES SUMMARY

### PO & MO Rules
1. PO Label adalah trigger mandatory untuk create MO Manufacturing
2. Week dan Destination di MO harus inherit dari PO Label (read-only)
3. MO bisa dibuat status Draft tanpa PO Label, tapi tidak bisa release ke SPK
4. Satu PO Label bisa generate multiple MO jika qty besar
5. PO Material non-label tidak block pembuatan MO

### SPK/WO Rules
1. SPK hanya bisa dibuat jika MO statusnya Released
2. Datestamp validation hanya untuk SPK Sewing, Finishing, Packing
3. SPK Tambahan hanya bisa dibuat oleh SPV dengan approval Manager
4. Total qty di SPK tidak harus match dengan MO (karena reject/over production)
5. Daily Input di SPK locked setelah FG received di gudang

### Material & Inventory Rules
1. Material Issue harus sesuai BOM, jika excess perlu Additional Material Request
2. Material Debt hanya untuk Raw Material dan Auxiliary Material
3. Maximum 3 active debt per artikel, maximum 10% dari MO value
4. UOM Conversion mandatory di Cutting, Packing, dan FG Receiving
5. Barcode scanning mandatory untuk semua material movement
6. Warehouse Finishing internal conversion (Skin → Stuffed Body) tidak perlu surat jalan, cukup log produksi
7. Validasi stok real-time: Stuffing perlu stok Skin > 0, Closing perlu stok Stuffed Body > 0
8. BOM Finishing harus split 2 tahap: Stuffing (consume Kapas) dan Closing (consume Benang)

### QC & Quality Rules
1. QC checkpoint mandatory di setiap akhir departemen
2. Critical reject harus approval Production Manager + QC Manager
3. Rework SPK perlu approval dari Production Manager
4. Foto evidence mandatory untuk Major dan Critical defect
5. First Pass Yield target minimum 95% per departemen

### Approval Authority
1. Material Request >$1000: Warehouse Manager approval
2. SPK Tambahan: SPV → Manager
3. Material Debt: Production Manager → General Manager
4. Rework untuk qty >100pcs: Production Manager approval
5. Stock Adjustment >5%: Warehouse Manager → General Manager

## 📋 IMPLEMENTATION PRIORITY

### Phase 1: Core Production Flow (Month 1-2)
1. ✅ Master Data (Material, BOM, Artikel)
2. ✅ PO Purchasing Module
3. ✅ MO Manufacturing Module
4. ✅ SPK/WO Module (5 Departments)
5. ✅ Warehouse Receiving & Material Issue
6. ⚙️ Basic Daily Input (Material & Production)
7. 🔥 **Warehouse Finishing Internal Conversion** (Critical - 2 Stage BOM Implementation)
   - Skin → Stuffed Body conversion tracking
   - Real-time stock validation for Stuffing & Closing
   - Dual inventory management (Skin + Stuffed Body)
   - Dashboard monitoring for WH Finishing

### Phase 2: Quality & Tracking (Month 3)
1. QC Module & Checkpoint
2. Rejection & Rework Handling
3. Barcode System Implementation
4. WIP Transfer & Tracking
5. FG Receiving & Shipping

### Phase 3: Advanced Features (Month 4-5)
1. Material Request & Approval Flow
2. Material Debt Mechanism
3. Dashboard & KPI
4. Reporting Module (Daily, Weekly, Monthly)
5. Notification System

### Phase 4: Integration & Optimization (Month 6)
1. EXIM System Integration
2. Mobile App Development
3. Financial System Integration
4. Advanced Analytics & Forecasting
5. User Training & Go-Live Support

## 🚨 CRITICAL SUCCESS FACTORS

1. **PO Label Discipline**: Semua user harus commit bahwa tidak ada MO tanpa PO Label
2. **Daily Input Compliance**: Operator wajib input daily data sebelum shift selesai
3. **QC Checkpoint Enforcement**: Tidak boleh ada WIP transfer tanpa QC approval
4. **Barcode Adoption**: 100% material movement harus pakai barcode scanning
5. **Warehouse Finishing Discipline**: 
   - Operator Finishing harus strict follow 2-stage process (Stuffing dulu, baru Closing)
   - Tidak boleh skip validasi stok (Stuffing perlu Skin, Closing perlu Stuffed Body)
   - Internal conversion log harus akurat untuk traceability kapas consumption
6. **🔴 UOM Conversion Accuracy (SUPER CRITICAL)**:
   - **Cutting**: Developer WAJIB implement dynamic marker calculation (Meter/Yard → Pcs) dengan variance validation ±10%
   - **FG Receiving**: Developer WAJIB implement foolproof Box → Pcs conversion dengan error handling jika artikel belum setup
   - **Zero Tolerance**: Salah konversi = Inventory chaos. Testing harus extra thorough untuk 2 modul ini!
   - **Training**: User WAJIB training khusus tentang UOM conversion sebelum go-live
7. **Approval SLA**: Approval request maksimal 4 jam working hours
8. **Data Accuracy**: Target 99% accuracy untuk inventory data, terutama WH Finishing dual inventory dan UOM conversion
9. **System Uptime**: Minimum 99.5% uptime during production hours
10. **User Training**: Minimum 8 jam training per user role, dengan focus khusus untuk:
    - Finishing dept (2-stage BOM logic)
    - Cutting dept (UOM Conversion Meter → Pcs)
    - Warehouse FG (UOM Conversion Box → Pcs)
11. **Change Management**: Weekly meeting untuk review dan improvement
12. **Continuous Monitoring**: Daily review dashboard dan KPI oleh management, dengan special attention pada:
    - WH Finishing stock level
    - Cutting material variance
    - FG receiving conversion accuracy

## 🔧 SYSTEM REQUIREMENTS

### Hardware Requirements
1. **Server**: 
   - CPU: Minimum 8 cores
   - RAM: Minimum 32GB
   - Storage: 1TB SSD (data), 2TB HDD (backup)
   - Network: 1Gbps LAN
   
2. **Client**: 
   - PC: Intel i5 atau equivalent, 8GB RAM, Windows 10/11
   - Tablet: Android 8.0+, minimum 4GB RAM (untuk mobile app)
   - Barcode Scanner: Support 1D & 2D barcode, wireless connectivity

3. **Network Infrastructure**:
   - WiFi Coverage di semua area produksi
   - Backup internet connection
   - Local network speed minimum 100Mbps

### Software Requirements
1. **Backend**: Python, FastAPI, PostgreSQL
2. **Frontend**: React, TypeScript, Material-UI
3. **Mobile**: React Native atau Flutter
4. **Integration**: REST API, WebSocket (real-time), MQTT (IoT devices)
5. **Security**: SSL/TLS, JWT Authentication, Role-based Access Control

### Data Backup & Recovery
1. **Backup Schedule**:
   - Full backup: Daily at 11 PM
   - Incremental backup: Every 4 hours
   - Transaction log backup: Every 30 minutes
   
2. **Backup Retention**:
   - Daily backup: 30 days
   - Weekly backup: 3 months
   - Monthly backup: 1 year
   
3. **Recovery Time Objective (RTO)**: Maximum 2 hours
4. **Recovery Point Objective (RPO)**: Maximum 30 minutes data loss

---

**Document Version**: 2.0  
**Last Updated**: 30 January 2026  
**Author**: Daniel Rizaldy - IT Programmer - ERP Implementation  
**Status**: Ready for Development  
**Next Review**: 15 February 2026