**Flow Production Quty Karunia**

    1.	Warehouse -> Cutting (WIP CUT) -> Embroidery/Subcon -> Sewing (WIP SEW) -> Finishing Dept (Stuffing/QC)
    2.	Warehouse -> Cutting (WIP CUT) -> Sewing (WIP SEW) -> Finishing Dept (Stuffing/QC)
    3.	Warehouse -> Cutting (WIP CUT) -> Embroidery/Subcon -> Finishing Dept (Stuffing/QC)

Penjelasan singkat:
    •	Warehouse -> Material
    •	Cutting -> Pemotongan material dari roll menjadi potongan piece
    •	Embrodery -> Pemasangan mata/hiasan lainnya juga pengiriman ke PT lain untuk pembuatan barang setengah jadi atau barang jadi.
    •	Sewing -> Penjahitan barang setengah jadi dari Cutting dan Embrodery. dan pemasangan label.
    •	Finishgood -> Pengisian isian boneka dan perapihan jahitan dan pengecekan fisik akhir boneka serta penyortiran
    •	Packing -> Penyortiran dan packing barang jadi sesuai Label yang tertera.
    •	Finishgood -> Penyimpanan hasil packing untuk dikirim ke negara-negara yang dituju

Proses produksi
    1.	PO terdiri dari berbagai article IKEA dan berbagai negara tujuan dari Ikea masuk
    2.	Purchasing membeli material produksi untuk kebutuhan produksi sesuai dengan article.
    3.	Material datang diterima oleh warehouse. Dicocokan sesuai dengan surat pembelian.
    4.	Dept Cutting melakukan permintaan material ke warehouse untuk kebutuhan produksi sesuai dengan PO yang ada. Mengeluarkan SPK/MO untuk pengerjaan material (Article Cutting) untuk dibuat menjadi barang setengah jadi(WIP CUT). Dan Embroderi (WIP EMBO) melakukan penjahitan hiasan dari potongan (WIP CUT) (mata, kumis, dll).
    5.	Barang setengah jadi dari Cutting (WIP CUT) dan embroderi (WIP EMBO masuk ke departemen Sewing, untuk dilakukan penjahitan juga pemasangan label produk, destinasi dll, material sesuai dengan yang ada pada Article Sewing. Juga diperlukan SPK/MO untuk menghasilkan barang jadi (WIP SEW).
    6.	Barang jadi Sewing (WIP SEW) menuju finishing sesuai dengan label destinasi dan week juga article Finishgood untuk dilakukan pengisian isian boneka agar menjadi Barang jadi tanpa code WIP. Tetap menggunakan surat jalan dari sewing dan lalu mengeluarkan SPK/MO sebagai perintah kerja ke operator Finishgood.
    7.	Barang jadi dari Finishgood menuju packing menggunakan Surat Jalan. Lalu dilakukan SPK/MO Pengepackan sesuai dengan label destinasi dan week. juga mengikuti article Packing
    8.	Dari Packing barang menuju Finishgood menggunakan surat jalan. Hasil dari finish good menjadi hasil akhir yang sesuai dengan PO IKEA dan Article IKEA.

notes:
    1.	Ada beberapa hasil sewing yang kembali ke sewing untuk dilakukan penjahitan proses penjahitan stik seperti jari boneka misalnya.
    2.	Sewing dapat menerima material dari Cutting dan Embro secara bersamaan atau salah satu saja.
    3.	Setiap Dept (Cutting, Embrodery, Sewing, Finishing, dan Packing) masing-masing memiliki articlenya sendiri. Berbeda dengan FinishGood hasilnya sesuai dengan Article milik Buyer (IKEA)
    4.	Setiap produksi dari hasil cutting dapat menghasilkan output week yang berbeda, namun satu article yang sama. 

STANDAR OPERASIONAL PROSEDUR (SOP) PRODUKSI
I. KONSEP DASAR: STRUKTUR ARTIKEL & ROUTING
Sebelum masuk ke langkah kerja, penting untuk menetapkan hierarki Artikel sesuai Note 3 Anda, karena ini mempengaruhi SPK yang keluar.
    •	Article Buyer (IKEA): Kode Final (misal: BLAHAJ-100). Hanya muncul di PO Awal dan Finish Good.
    •	Internal Articles (Child Codes):
        o	Article Cutting: Kode pola potong (misal: CUT-BLA-01).
        o	Article Embro: Kode panel bordir (misal: EMB-BLA-01).
        o	Article Sewing: Kode skin/kulit (misal: SEW-BLA-01).
        o	Article Packing: Kode barang loose (misal: PAC-BLA-01).
________________________________________
II. DIAGRAM ALUR PRODUKSI (3 VARIASI)
    •	Route 1 (Full Process):
    Warehouse -> Cutting (WIP CUT) -> Embroidery (WIP EMBO) -> Sewing (WIP SEW) -> Finishing -> Packing -> Finish Good
    •	Route 2 (Direct Sewing):
    Warehouse -> Cutting (WIP CUT) -> Sewing (WIP SEW) -> Finishing -> Packing -> Finish Good
    •	Route 3 (Subcon/Bypass):
    Warehouse -> Cutting (WIP CUT) -> Subcon (Jahit Luar) -> Finishing -> Packing -> Finish Good
________________________________________
III. DETAIL PROSES PRODUKSI (STEP-BY-STEP)
A. TAHAP PERENCANAAN & MATERIAL (Pre-Production)
    1.	Order Incoming
        •	PO masuk dari IKEA berisi Article Buyer, Qty, Destination, dan Week.
        •	PPIC memecah PO tersebut menjadi BOM (Bill of Material) untuk menentukan Article Cutting, Article Embro, dll.
    2.	Purchasing
        •	Membeli material berdasarkan kebutuhan Article Buyer.
    3.	Warehouse Incoming
        •	Material diterima, dicocokkan dengan surat jalan, dan disimpan sebagai stok Raw Material.
B. TAHAP PEMOTONGAN (CUTTING)
    4.	Proses Cutting
        •	Input: Material Roll dari Warehouse.
        •	Dokumen: SPK Cutting (berdasarkan Article Cutting).
        •	Aktivitas: Potong kain.
        •	Output: WIP CUT.
        •	Manajemen Week (Sesuai Note 4):
            o	Satu kali proses cutting (Batch besar) bisa untuk memenuhi kebutuhan beberapa Week.
            o	Contoh: Potong 10.000 pcs (Article Cutting X). Saat serah terima, 3.000 pcs diberi label Week 22, 7.000 pcs diberi label Week 23.
        •	Distribusi: WIP CUT dikirim ke Embroidery ATAU Sewing sesuai Route.
C. TAHAP DEKORASI (EMBROIDERY / SUBCON)
    5.	Proses Embroidery (Opsional sesuai Route)
        •	Input: WIP CUT.
        •	Dokumen: SPK Embro (berdasarkan Article Embro).
        •	Aktivitas: Jahit mata, kumis, aplikasi hiasan.
        •	Output: WIP EMBO.
        •	Internal: Penjahitan dilakukan menggunakan mesin sendiri. (WIP EMBO)
        •	Subcon: Jika dikirim ke PT Lain (Route 3), status barang keluar pabrik. Saat kembali, barang bisa berstatus WIP EMBO (panel) atau Barang Setengah Jadi (Skin) tergantung kontrak kerja.
D. TAHAP PERAKITAN (SEWING)
    6.	Proses Sewing
        •	Input (Sesuai Note 2):
            o	Menerima WIP CUT saja (Route 2).
            o	Menerima WIP EMBO saja.
            o	Menerima kombinasi WIP CUT + WIP EMBO (Route 1).
        •	Dokumen: SPK Sewing (berdasarkan Article Sewing).
        •	Aktivitas Utama:
            o	Assembly komponen.
            o	Pemasangan Label (Care Label & Brand Label) sesuai Destinasi.
        •	Internal Loop (Sesuai Note 1):
            o	Langkah: Jahit Body -> Transfer ke station "Stik/Jari" (Balik Jahitan) -> Kembali ke Line Jahit Body untuk penutupan.
            o	Proses ini terjadi dalam satu departemen Sewing.
        •	Output: WIP SEW (Kulit Boneka/Skin).
E. TAHAP PENYELESAIAN (FINISHING DEPT)
    7.	Proses Finishing
        •	Input: WIP SEW dari Sewing (atau Skin dari Subcon Route 3).
        •	Dokumen: SPK Finishing (berdasarkan Article Finishing).
        •	Transformasi Kode: Di sini kode WIP (WIP SEW) dihapus. Barang diproses menjadi produk akhir.
        •	Aktivitas:
            o	Stuffing (Isi Dacron).
            o	Sewing Closing (Jahit Tutup).
            o	Shaping & Grooming.
            o	QC Final & Metal Detector.
        •	Output: Barang Jadi (Loose) siap packing.
F. TAHAP PENGEMASAN (PACKING)
    8.	Proses Packing
        •	Input: Barang Jadi dari Finishing.
        •	Dokumen: SPK Packing (berdasarkan Article Packing).
        •	Aktivitas:
            o	Sortir berdasarkan Label Destinasi dan Week.
            o	Packing ke Polybag & Karton.
            o	Penempelan Shipping Mark.
        •	Output: Master Carton.
G. GUDANG BARANG JADI (FINISH GOOD)
    9.	Penyimpanan & Pengiriman
        •	Input: Master Carton dari Packing + Surat Jalan.
        •	Verifikasi: Petugas gudang memastikan barang yang masuk sesuai dengan Article Buyer (IKEA).
        •	Aktivitas: Penyimpanan per blok negara/week dan loading ke kontainer.
________________________________________
IV. MATRIX KONTROL (MENGATASI NOTES ANDA)
Berikut adalah ringkasan bagaimana sistem mengatasi Notes khusus Anda:
Isu / Note	Solusi Sistem
Note 1: Sewing Loop (Balik lagi) : Dibuat sebagai Internal Line Balancing. Dalam SPK Sewing, ada sub-proses (Pos 1: Rakit, Pos 2: Stik, Pos 3: Rakit Akhir). Tidak perlu Surat Jalan keluar departemen, cukup kartu kendali meja.
Note 2: Input Sewing Variatif : SPK Sewing harus mencantumkan BOM (Daftar Material) yang jelas. Apakah materialnya 100% dari Cutting atau 50% Cutting + 50% Embro.
Note 3: Beda Article Tiap Dept : Sistem ERP/Admin harus menggunakan Parent-Child Relation. Article IKEA adalah "Induk", Article Tiap Dept adalah "Anak". SPK diterbitkan per "Anak".
Note 4: Cutting Beda Week	Penerapan Split Lot. Hasil output Cutting 1 SPK, dipecah menjadi beberapa Surat Jalan Transfer dengan label Week yang berbeda saat diserahkan ke Sewing/Embro.
________________________________________
I. UPDATE: FLOW PRODUCTION (KONSEP ALUR)
Berdasarkan penemuan di QT-09-TCK03 (Transfer Finishing -> Packing), kita harus mengadopsi logika ketat ini ke seluruh departemen.
Perubahan Konsep:
1.	Adopsi "Handover Protocol" (Protokol Serah Terima):
    o	Sebelumnya: Asumsi barang pindah begitu saja antar departemen.
    o	Update: Menerapkan aturan "Jeda Waktu & Segregasi" dari QT-09 ke transfer Cutting -> Sewing. Operator Cutting tidak boleh kirim Artikel B sebelum Artikel A tuntas diterima Sewing (Line Clearance).
2.	Digitalisasi QC Testing:
    o	Sebelumnya: QC hanya Pass/Fail.
    o	Update: Memasukkan input data numerik untuk Drop Test & Stability Test (Sesuai SOP ISO/IKEA yang Anda upload) agar tersimpan history-nya di ERP.
3.	Aturan Kanban Aksesoris:
    o	Update: Mengaktifkan fitur E-Kanban untuk permintaan aksesoris di Packing (sesuai poin 6.2.4 di SOP QT-09).
4.  PPIC di perusahaan ini hanya sebagai admin penginputan saja namun tidak melakukan planning produksi. Planning produksi dilakukan oleh masing-masing departemen sesuai dengan kapasitas mesin dan operator yang ada di departemen tersebut. Mereka hanya bekerja sesuai arahan manager produksi saja.

Dengan perubahan ini, alur produksi menjadi lebih terstruktur dan sesuai standar kualitas yang diharapkan oleh IKEA. Pastikan semua departemen memahami dan menerapkan protokol baru ini untuk kelancaran proses produksi.