"""
Generate IMPROVED workflow flowchart diagrams
Shows clear comparison: MANUAL (with pain points) vs ODOO (automated)
"""
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle
import textwrap

# Set font
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans']

def wrap_text(text, width=40):
    """Wrap text to specified width"""
    return '\n'.join(textwrap.wrap(text, width=width))

def create_box(ax, x, y, width, height, text, color='lightblue', fontsize=9, bold=False, edge_color='black', edge_width=2):
    """Create a rounded box with text"""
    box = FancyBboxPatch((x, y), width, height, 
                          boxstyle="round,pad=0.1", 
                          edgecolor=edge_color, 
                          facecolor=color, 
                          linewidth=edge_width)
    ax.add_patch(box)
    
    # Add text with wrapping
    weight = 'bold' if bold else 'normal'
    ax.text(x + width/2, y + height/2, text, 
            ha='center', va='center', 
            fontsize=fontsize, weight=weight)

def create_arrow(ax, x1, y1, x2, y2, label='', color='black', style='->'):
    """Create an arrow between two points"""
    arrow = FancyArrowPatch((x1, y1), (x2, y2),
                           arrowstyle=style, 
                           mutation_scale=25, 
                           linewidth=2.5,
                           color=color)
    ax.add_patch(arrow)
    
    if label:
        mid_x = (x1 + x2) / 2
        mid_y = (y1 + y2) / 2
        ax.text(mid_x + 0.5, mid_y, label, 
                fontsize=8, style='italic',
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.9))

def create_problem_badge(ax, x, y, text):
    """Create a red problem badge"""
    circle = plt.Circle((x, y), 0.4, color='red', alpha=0.3, zorder=1)
    ax.add_patch(circle)
    ax.text(x, y, text, ha='center', va='center', 
            fontsize=7, weight='bold', color='darkred', zorder=2)


# ========== DIAGRAM 1: MANUAL PURCHASING (WITH PAIN POINTS) ==========
def diagram_1_manual_purchasing():
    """Diagram 1: Manual Purchasing Workflow (Current - with problems)"""
    fig, ax = plt.subplots(figsize=(14, 20))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 24)
    ax.axis('off')
    
    # Title with red theme (MANUAL = PROBLEMS)
    ax.text(7, 23, 'ALUR PURCHASING: SISTEM MANUAL (SEKARANG)', 
            ha='center', fontsize=18, weight='bold', color='darkred')
    ax.text(7, 22.3, 'PT Quty Karunia - Sistem Berbasis Excel', 
            ha='center', fontsize=12, style='italic')
    
    y = 21
    
    # Step 1: Receive IKEA Order
    create_box(ax, 2, y, 10, 1.3, 
               'LANGKAH 1: Terima Order IKEA\n' +
               'SKU apa? Quantity berapa? Rencana produksi kapan?',
               'lightyellow', fontsize=10, bold=True)
    create_arrow(ax, 7, y, 7, y-0.5)
    y -= 2
    
    # Step 2: Manual BOM Lookup (PROBLEM!)
    create_box(ax, 2, y, 10, 2, 
               'LANGKAH 2: Buka Excel BOM (MANUAL!)\n' +
               '• Cari SKU di Excel (478 SKU × 15-30 material each)\n' +
               '• Hitung kebutuhan material pakai KALKULATOR!\n' +
               '• Copy-paste dari multiple Excel sheets',
               'lightcoral', fontsize=9, edge_color='red', edge_width=3)
    create_problem_badge(ax, 1, y+1, '⚠')
    ax.text(0.5, y+0.4, 'LAMA &\nREPOT!', ha='center', fontsize=7, 
            weight='bold', color='red', bbox=dict(boxstyle='round', facecolor='yellow'))
    create_arrow(ax, 7, y, 7, y-0.5, color='red')
    y -= 2.8
    
    # Step 3: Multi-unit Conversion (PROBLEM!)
    create_box(ax, 2, y, 10, 2.2, 
               'LANGKAH 3: Konversi Multi-unit MANUAL (SERING ERROR!)\n' +
               '• ROLL → PCS: Hitung manual (1 ROLL = berapa meter?)\n' +
               '• KG → GRAM: Konversi manual\n' +
               '• Purchasing BUKAN technical! Error sering terjadi!',
               'lightcoral', fontsize=9, edge_color='red', edge_width=3)
    create_problem_badge(ax, 1, y+1.1, '⚠')
    ax.text(13, y+1.1, 'SERING\nSALAH!', ha='center', fontsize=7, 
            weight='bold', color='red', bbox=dict(boxstyle='round', facecolor='yellow'))
    create_arrow(ax, 7, y, 7, y-0.5, color='red')
    y -= 2.8
    
    # Step 4: Pallet Calculation (PROBLEM!)
    create_box(ax, 2, y, 10, 2.2, 
               'LANGKAH 4: Hitung Pallet MANUAL (Aturan IKEA Rumit!)\n' +
               '• Karton per pallet HARUS GENAP!\n' +
               '• Manual Excel formula: ROUNDUP(qty/pcs_per_karton/24)\n' +
               '• 1523 pcs → Berapa pallet? Sisa karton genap tidak?',
               'lightcoral', fontsize=9, edge_color='red', edge_width=3)
    create_problem_badge(ax, 1, y+1.1, '⚠')
    ax.text(13, y+1.1, 'RUMIT &\nMANUAL!', ha='center', fontsize=7, 
            weight='bold', color='red', bbox=dict(boxstyle='round', facecolor='yellow'))
    create_arrow(ax, 7, y, 7, y-0.5, color='red')
    y -= 2.8
    
    # Step 5: Check Stock (DELAYED!)
    create_box(ax, 2, y, 10, 2, 
               'LANGKAH 5: Cek Stock di Excel Warehouse\n' +
               '• Data TIDAK REAL-TIME (delay dari warehouse aktual!)\n' +
               '• Material cukup tidak? → Manual cek Excel\n' +
               '• Hitung: Material mana yang harus order',
               'lightcoral', fontsize=9, edge_color='red', edge_width=3)
    create_problem_badge(ax, 1, y+1, '⚠')
    ax.text(13, y+1, 'DATA\nOUTDATED!', ha='center', fontsize=7, 
            weight='bold', color='red', bbox=dict(boxstyle='round', facecolor='yellow'))
    create_arrow(ax, 7, y, 7, y-0.5, color='red')
    y -= 2.5
    
    # Step 6: Create PO Manual
    create_box(ax, 2, y, 10, 1.8, 
               'LANGKAH 6: Buat PO Manual di Excel\n' +
               '• Copy-paste data material (RESIKO TYPO!)\n' +
               '• Email manual ke supplier (lampiran Excel/PDF)',
               'lightcoral', fontsize=9, edge_color='red', edge_width=3)
    create_problem_badge(ax, 1, y+0.9, '⚠')
    create_arrow(ax, 7, y, 7, y-0.5, color='red')
    y -= 2.3
    
    # Step 7: Track PO Manual
    create_box(ax, 2, y, 10, 1.8, 
               'LANGKAH 7: Tracking PO Manual\n' +
               '• Email supplier: "Sudah kirim belum?"\n' +
               '• Catat manual di Excel: "PO-001 status: Pending"',
               'lightcoral', fontsize=9, edge_color='red', edge_width=3)
    create_problem_badge(ax, 1, y+0.9, '⚠')
    create_arrow(ax, 7, y, 7, y-0.5, color='red')
    y -= 2.3
    
    # Step 8: Material Datang
    create_box(ax, 2, y, 10, 1.8, 
               'LANGKAH 8: Material Datang (Admin Warehouse)\n' +
               '• Catat manual: Material apa, quantity, dari PO mana\n' +
               '• Baru input ke Excel akhir hari (SERING SALAH INPUT!)',
               'lightcoral', fontsize=9, edge_color='red', edge_width=3)
    create_problem_badge(ax, 13, y+0.9, '⚠')
    
    # SUMMARY BOX
    y -= 2.5
    create_box(ax, 1, y, 12, 2.5, 
               'RANGKUMAN MASALAH UTAMA:\n' +
               '❌ BOM explosion: Manual dan lama per order!\n' +
               '❌ Konversi UOM: SERING ERROR (Purchasing bukan technical!)\n' +
               '❌ Hitung pallet: MANUAL dengan Excel formula rumit!\n' +
               '❌ Visibilitas stock: Tidak real-time!\n' +
               '❌ Tracking PO: Email manual terus ke supplier!',
               'mistyrose', fontsize=9, edge_color='darkred', edge_width=3)
    
    plt.tight_layout()
    plt.savefig('DIAGRAM_1_MANUAL_PURCHASING.png', dpi=300, bbox_inches='tight')
    print("✓ Created: DIAGRAM_1_MANUAL_PURCHASING.png")
    plt.close()


# ========== DIAGRAM 2: ODOO PURCHASING (AUTOMATED) ==========
def diagram_2_odoo_purchasing():
    """Diagram 2: Odoo Purchasing Workflow (Automated - solutions)"""
    fig, ax = plt.subplots(figsize=(14, 20))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 24)
    ax.axis('off')
    
    # Title with green theme (ODOO = SOLUTIONS)
    ax.text(7, 23, 'ALUR PURCHASING: SISTEM ODOO (OTOMATIS)', 
            ha='center', fontsize=18, weight='bold', color='darkgreen')
    ax.text(7, 22.3, 'PT Quty Karunia - Odoo ERP 2026', 
            ha='center', fontsize=12, style='italic')
    
    y = 21
    
    # Step 1: Input to Odoo
    create_box(ax, 2, y, 10, 1.3, 
               'LANGKAH 1: Input Order IKEA ke Odoo\n' +
               'Pilih SKU, Input quantity → Klik "Hitung Material"',
               'lightgreen', fontsize=10, bold=True, edge_color='darkgreen', edge_width=3)
    create_arrow(ax, 7, y, 7, y-0.5, color='green')
    y -= 2
    
    # Step 2: AUTO BOM Explosion (SOLUTION!)
    create_box(ax, 2, y, 10, 2, 
               'LANGKAH 2: Sistem AUTO-EXPLODE BOM (INSTAN!)\n' +
               '✓ 478 SKU dihitung OTOMATIS (tidak manual!)\n' +
               '✓ Semua material + quantity otomatis!\n' +
               '✓ Konversi multi-unit OTOMATIS!',
               'lightgreen', fontsize=9, bold=True, edge_color='darkgreen', edge_width=3)
    ax.text(0.5, y+0.5, 'CEPAT &\nOTOMATIS!', ha='center', fontsize=8, 
            weight='bold', color='green', bbox=dict(boxstyle='round', facecolor='lightgreen'))
    create_arrow(ax, 7, y, 7, y-0.5, color='green')
    y -= 2.8
    
    # Step 3: AUTO Multi-unit (SOLUTION!)
    create_box(ax, 2, y, 10, 2, 
               'LANGKAH 3: Konversi Multi-unit OTOMATIS!\n' +
               '✓ ROLL → PCS: Sistem hitung otomatis!\n' +
               '✓ KG → GRAM: Built-in konversi!\n' +
               '✓ TIDAK ADA ERROR!',
               'lightgreen', fontsize=9, bold=True, edge_color='darkgreen', edge_width=3)
    ax.text(13, y+1, 'AKURAT\n100%!', ha='center', fontsize=8, 
            weight='bold', color='green', bbox=dict(boxstyle='round', facecolor='lightgreen'))
    create_arrow(ax, 7, y, 7, y-0.5, color='green')
    y -= 2.5
    
    # Step 4: AUTO Pallet Calc (SOLUTION!)
    create_box(ax, 2, y, 10, 2.2, 
               'LANGKAH 4: Hitung Pallet OTOMATIS!\n' +
               '✓ Aturan pallet IKEA BUILT-IN!\n' +
               '✓ Karton per pallet GENAP otomatis!\n' +
               '✓ Contoh: 1523 pcs → System: "4 pallet (24 karton)"',
               'lightgreen', fontsize=9, bold=True, edge_color='darkgreen', edge_width=3)
    ax.text(13, y+1.1, 'PRESISI\n100%!', ha='center', fontsize=8, 
            weight='bold', color='green', bbox=dict(boxstyle='round', facecolor='lightgreen'))
    create_arrow(ax, 7, y, 7, y-0.5, color='green')
    y -= 2.8
    
    # Step 5: REAL-TIME Stock Check (SOLUTION!)
    create_box(ax, 2, y, 10, 2, 
               'LANGKAH 5: Cek Stock REAL-TIME!\n' +
               '✓ Sistem cek: Warehouse + In-Transit + Reserved\n' +
               '✓ Dashboard: "15 material perlu order sekarang"\n' +
               '✓ Auto-create Purchase Requisition list',
               'lightgreen', fontsize=9, bold=True, edge_color='darkgreen', edge_width=3)
    ax.text(13, y+1, 'DATA\nREAL-TIME!', ha='center', fontsize=8, 
            weight='bold', color='green', bbox=dict(boxstyle='round', facecolor='lightgreen'))
    create_arrow(ax, 7, y, 7, y-0.5, color='green')
    y -= 2.5
    
    # Step 6A & 6B: Dual PO Auto
    create_box(ax, 1.5, y, 5, 2, 
               'LANGKAH 6A: PO FABRIC (Week 0)\n' +
               '✓ Klik "Buat PO"\n' +
               '✓ Email AUTO-KIRIM!\n' +
               '✓ Trigger: Cutting +\n   Embroidery UNLOCK',
               'lightblue', fontsize=8, bold=True, edge_color='darkgreen', edge_width=2)
    create_box(ax, 7.5, y, 5, 2, 
               'LANGKAH 6B: PO LABEL (Week +2)\n' +
               '✓ Info label TERKUNCI\n' +
               '✓ AUTO-INHERIT ke\n   SEMUA dept!\n' +
               '✓ TIDAK ADA MIX LABEL!',
               'orange', fontsize=8, bold=True, edge_color='darkgreen', edge_width=2)
    create_arrow(ax, 4, y-0.3, 7, y-2.5, color='green')
    create_arrow(ax, 10, y-0.3, 7, y-2.5, color='green')
    y -= 3
    
    # Step 7: AUTO Tracking
    create_box(ax, 2, y, 10, 1.5, 
               'LANGKAH 7: Tracking PO OTOMATIS!\n' +
               '✓ Dashboard: Status real-time per PO\n' +
               '✓ Notifikasi email otomatis (tidak perlu follow-up manual!)',
               'lightgreen', fontsize=9, bold=True, edge_color='darkgreen', edge_width=3)
    create_arrow(ax, 7, y, 7, y-0.5, color='green')
    y -= 2.3
    
    # Step 8: Material Received
    create_box(ax, 2, y, 10, 1.8, 
               'LANGKAH 8: Material Diterima → Stock UPDATE LANGSUNG!\n' +
               '✓ Warehouse validasi PO → Stock AUTO-UPDATE!\n' +
               '✓ Notifikasi otomatis ke Purchasing + Production',
               'lightgreen', fontsize=9, bold=True, edge_color='darkgreen', edge_width=3)
    
    # BENEFITS BOX
    y -= 2.5
    create_box(ax, 1, y, 12, 2.8, 
               'MANFAAT UTAMA:\n' +
               '✓ BOM explosion: Manual → INSTAN! (Jauh lebih cepat!)\n' +
               '✓ Konversi UOM: TIDAK ADA ERROR (otomatis!)\n' +
               '✓ Hitung pallet: 100% AKURAT (aturan IKEA built-in!)\n' +
               '✓ Visibilitas stock: REAL-TIME (tidak ada delay!)\n' +
               '✓ Tracking PO: OTOMATIS (tidak perlu email manual!)\n' +
               '✓ Waktu admin: Berkurang drastis per order!',
               'honeydew', fontsize=9, bold=True, edge_color='darkgreen', edge_width=3)
    
    plt.tight_layout()
    plt.savefig('DIAGRAM_2_ODOO_PURCHASING.png', dpi=300, bbox_inches='tight')
    print("✓ Created: DIAGRAM_2_ODOO_PURCHASING.png")
    plt.close()


# ========== DIAGRAM 3: MANUAL PRODUCTION (5 DEPT WITH PROBLEMS) ==========
def diagram_3_manual_production():
    """Diagram 3: Manual Production 5 Departments (Current - with problems)"""
    fig, ax = plt.subplots(figsize=(16, 22))
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 26)
    ax.axis('off')
    
    # Title
    ax.text(8, 25, 'PRODUCTION WORKFLOW: MANUAL (CURRENT)', 
            ha='center', fontsize=18, weight='bold', color='darkred')
    ax.text(8, 24.3, '5 Departments - Excel-based Tracking', 
            ha='center', fontsize=12, style='italic')
    
    y = 23
    
    # NO MO!
    create_box(ax, 3, y, 10, 1.5, 
               '❌ TIDAK ADA MO (Manufacturing Order)!\n' +
               'Tiap dept jadwal sendiri dari meeting verbal!',
               'lightcoral', fontsize=10, bold=True, edge_color='red', edge_width=3)
    create_problem_badge(ax, 2, y+0.75, '⚠')
    create_arrow(ax, 8, y, 8, y-0.5, color='red')
    y -= 2.3
    
    # Dept 1: Cutting
    create_box(ax, 1, y, 7, 2.5, 
               'DEPT 1: CUTTING\n' +
               '• Ambil material: Surat jalan KERTAS\n' +
               '• Admin catat consumption: EXCEL manual\n' +
               '• Daily output: Form kertas → Excel\n' +
               '• Production: 1050 pcs cut pieces',
               'lightcoral', fontsize=8, edge_color='red', edge_width=2)
    create_box(ax, 9, y, 6, 2.5, 
               'QC CHECKPOINT 1\n' +
               '• Inspector check: VERBAL!\n' +
               '• Admin QC: Excel terpisah\n' +
               '• Defect: 30, Pass: 1050\n' +
               '• Rework: TIDAK tracked!',
               'mistyrose', fontsize=8, edge_color='red', edge_width=2)
    create_problem_badge(ax, 0.2, y+1.25, '⚠')
    ax.text(0.2, y+0.5, 'EXCEL\nMANUAL!', ha='center', fontsize=7, 
            weight='bold', color='red', bbox=dict(boxstyle='round', facecolor='yellow'))
    create_arrow(ax, 4, y, 8, y-3, color='red')
    y -= 3.5
    
    # Transfer Problem
    create_box(ax, 3, y, 10, 1, 
               'Transfer Cutting → Embroidery: MANUAL CATAT (SERING TIDAK MATCH!)',
               'mistyrose', fontsize=8, edge_color='red', edge_width=2)
    create_problem_badge(ax, 2, y+0.5, '⚠')
    create_arrow(ax, 8, y, 8, y-0.3, color='red')
    y -= 1.5
    
    # Dept 2: Embroidery
    create_box(ax, 1, y, 7, 2, 
               'DEPT 2: EMBROIDERY\n' +
               '• Admin catat: Excel manual\n' +
               '• Production: 1060 pcs embroidered\n' +
               '• TIDAK tahu sisa WIP Cutting!',
               'lightcoral', fontsize=8, edge_color='red', edge_width=2)
    create_problem_badge(ax, 0.2, y+1, '⚠')
    create_arrow(ax, 4, y, 8, y-2.3, color='red')
    y -= 2.8
    
    # Transfer Problem
    create_box(ax, 3, y, 10, 1, 
               'Transfer Embroidery → Sewing: DELAY ENTRY (tidak sync!)',
               'mistyrose', fontsize=8, edge_color='red', edge_width=2)
    create_problem_badge(ax, 2, y+0.5, '⚠')
    create_arrow(ax, 8, y, 8, y-0.3, color='red')
    y -= 1.5
    
    # Dept 3: Sewing (CRITICAL!)
    create_box(ax, 1, y, 7, 3, 
               'DEPT 3: SEWING (38 LINES!)\n' +
               '• 38 lines = 38 tracking points MANUAL!\n' +
               '• Admin track per line: EXCEL nightmare!\n' +
               '• Admin time: 2-3 JAM/HARI!\n' +
               '• Aggregate output manual: 1010 pcs\n' +
               '• TIDAK tahu order IKEA mana!',
               'lightcoral', fontsize=8, bold=True, edge_color='red', edge_width=3)
    create_box(ax, 9, y, 6, 3, 
               'QC CHECKPOINT 2\n' +
               '• Inspector: VERBAL report\n' +
               '• Admin QC: Excel terpisah\n' +
               '• Defect: 30, Pass: 1010\n' +
               '• TIDAK tahu defect dari\n   line mana! (no analysis!)\n' +
               '• Rework: TIDAK tracked!',
               'mistyrose', fontsize=8, edge_color='red', edge_width=2)
    create_problem_badge(ax, 0.2, y+1.5, '⚠')
    ax.text(0.2, y+0.5, '2-3 JAM\nADMIN!', ha='center', fontsize=7, 
            weight='bold', color='red', bbox=dict(boxstyle='round', facecolor='yellow'))
    create_arrow(ax, 4, y, 8, y-3.5, color='red')
    y -= 4
    
    # Transfer Problem
    create_box(ax, 3, y, 10, 1, 
               'Transfer Sewing → Finishing: SERING LUPA CATAT! (chaos!)',
               'mistyrose', fontsize=8, edge_color='red', edge_width=2)
    create_problem_badge(ax, 2, y+0.5, '⚠')
    create_arrow(ax, 8, y, 8, y-0.3, color='red')
    y -= 1.5
    
    # Dept 4: Finishing
    create_box(ax, 1, y, 7, 3, 
               'DEPT 4: FINISHING (2-STAGE)\n' +
               '• Stage 1 (Stuffing): 1010 pcs\n' +
               '  Intermediate TIDAK tracked!\n' +
               '• Stage 2 (Closing): 1010 pcs\n' +
               '• Operator lihat Label: EXCEL/Email!\n' +
               '  RISK: Salah lihat Week/Destination!',
               'lightcoral', fontsize=8, bold=True, edge_color='red', edge_width=3)
    create_box(ax, 9, y, 6, 3, 
               'QC CHECKPOINT 3\n' +
               '• Inspector: VERBAL!\n' +
               '• Admin QC: Excel terpisah\n' +
               '• Defect: 10, Pass: 1000\n' +
               '• TIDAK tahu defect dari\n   Stage 1 atau Stage 2!\n' +
               '• Rework: TIDAK tracked!',
               'mistyrose', fontsize=8, edge_color='red', edge_width=2)
    create_problem_badge(ax, 0.2, y+1.5, '⚠')
    ax.text(0.2, y+0.5, 'LABEL\nRISK!', ha='center', fontsize=7, 
            weight='bold', color='red', bbox=dict(boxstyle='round', facecolor='yellow'))
    create_arrow(ax, 4, y, 8, y-3.5, color='red')
    y -= 4
    
    # Transfer Problem (CRITICAL!)
    create_box(ax, 3, y, 10, 1.2, 
               'Transfer Finishing → Packing: LABEL INFO SALAH! (MIX LABEL RISK!)',
               'red', fontsize=8, bold=True, edge_color='darkred', edge_width=3)
    create_problem_badge(ax, 2, y+0.6, '⚠')
    create_arrow(ax, 8, y, 8, y-0.3, color='darkred')
    y -= 1.8
    
    # Dept 5: Packing (CRITICAL!)
    create_box(ax, 1, y, 7, 3.2, 
               'DEPT 5: PACKING\n' +
               '• Operator lihat Label: dari Finishing!\n' +
               '  RISK: Info dari Finishing SUDAH SALAH!\n' +
               '• Packing: Group by Week & Destination\n' +
               '  CRITICAL: MIX LABEL FREQUENT!\n' +
               '  Week 08 + Label 07 = IKEA REJECT!\n' +
               '• QTY KURANG FREQUENT! (Missing 20 pcs!)\n' +
               '• TIDAK ADA PENGECEKAN KEMBALI!',
               'red', fontsize=8, bold=True, edge_color='darkred', edge_width=3)
    create_box(ax, 9, y, 6, 3.2, 
               'QC CHECKPOINT 4 (FG)\n' +
               '• Unit: PER PALLET\n' +
               '• Inspector: Manual check\n' +
               '• Pass: 15 pallet\n' +
               '• Defect: 2 pallet\n' +
               '• Rework: TIDAK tracked!\n' +
               '• Admin QC: 4 checkpoints\n' +
               '  sendirian! (overwhelmed!)',
               'mistyrose', fontsize=8, edge_color='red', edge_width=2)
    create_problem_badge(ax, 0.2, y+1.6, '⚠')
    ax.text(0.2, y+0.5, 'MIX LABEL\nRISK!', ha='center', fontsize=7, 
            weight='bold', color='darkred', bbox=dict(boxstyle='round', facecolor='yellow'))
    
    # SUMMARY BOX
    y -= 4
    create_box(ax, 1, y, 14, 3, 
               'PAIN POINTS SUMMARY:\n' +
               '❌ NO MO! Tiap dept jadwal sendiri (tidak sinkron!)\n' +
               '❌ 38 sewing lines: MANUAL track = 2-3 JAM/HARI admin time!\n' +
               '❌ QC data: EXCEL TERPISAH (4 checkpoints tidak terintegrasi!)\n' +
               '❌ MIX LABEL: CRITICAL RISK! (Finishing & Packing salah lihat!)\n' +
               '❌ QTY KURANG: FREQUENT di Packing! (Missing/hilang, tidak tahu why!)\n' +
               '❌ Rework: TIDAK tracked! (No cost analysis, no pattern detection!)\n' +
               '❌ Reconciliation: 2-4 JAM meeting/hari untuk match Excel dept!',
               'mistyrose', fontsize=9, edge_color='darkred', edge_width=3)
    
    plt.tight_layout()
    plt.savefig('DIAGRAM_3_MANUAL_PRODUCTION.png', dpi=300, bbox_inches='tight')
    print("✓ Created: DIAGRAM_3_MANUAL_PRODUCTION.png")
    plt.close()


# ========== DIAGRAM 4: ODOO PRODUCTION (5 DEPT AUTOMATED) ==========
def diagram_4_odoo_production():
    """Diagram 4: Odoo Production 5 Departments (Automated - solutions)"""
    fig, ax = plt.subplots(figsize=(16, 22))
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 26)
    ax.axis('off')
    
    # Title
    ax.text(8, 25, 'PRODUCTION WORKFLOW: ODOO (AUTOMATED)', 
            ha='center', fontsize=18, weight='bold', color='darkgreen')
    ax.text(8, 24.3, '5 Departments - System Coordinated', 
            ha='center', fontsize=12, style='italic')
    
    y = 23
    
    # MO AUTO!
    create_box(ax, 3, y, 10, 1.5, 
               '✓ MO AUTO-CREATE + 5 WO!\n' +
               'System koordinasi semua dept, target auto-calculated!',
               'lightgreen', fontsize=10, bold=True, edge_color='darkgreen', edge_width=3)
    create_arrow(ax, 8, y, 8, y-0.5, color='green')
    y -= 2.3
    
    # Dept 1: Cutting
    create_box(ax, 1, y, 7, 2.5, 
               'DEPT 1: CUTTING\n' +
               '✓ Material consumption: AUTO-BACKFLUSH!\n' +
               '✓ Stock deduct automatic (no manual input!)\n' +
               '✓ Daily output: System record automatic\n' +
               '✓ Production: 1050 pcs → System track',
               'lightgreen', fontsize=8, bold=True, edge_color='darkgreen', edge_width=2)
    create_box(ax, 9, y, 6, 2.5, 
               'QC CHECKPOINT 1\n' +
               '✓ QC integrated ke MO!\n' +
               '✓ Defect: 30, Pass: 1050\n' +
               '✓ Rework: TRACKED!\n' +
               '✓ Traceable to batch!',
               'lightcyan', fontsize=8, edge_color='darkgreen', edge_width=2)
    ax.text(15.8, y+1.25, 'AUTO-\nBACKFLUSH!', ha='center', fontsize=7, 
            weight='bold', color='green', bbox=dict(boxstyle='round', facecolor='lightgreen'))
    create_arrow(ax, 4, y, 8, y-3, color='green')
    y -= 3.5
    
    # Transfer Auto!
    create_box(ax, 3, y, 10, 1, 
               'Transfer Cutting → Embroidery: AUTO-VALIDATED! (100% match!)',
               'lightcyan', fontsize=8, edge_color='darkgreen', edge_width=2)
    create_arrow(ax, 8, y, 8, y-0.3, color='green')
    y -= 1.5
    
    # Dept 2: Embroidery
    create_box(ax, 1, y, 7, 2, 
               'DEPT 2: EMBROIDERY\n' +
               '✓ WIP validated automatic!\n' +
               '✓ Production: 1060 pcs → System track\n' +
               '✓ Tahu sisa WIP Cutting REAL-TIME!',
               'lightgreen', fontsize=8, bold=True, edge_color='darkgreen', edge_width=2)
    ax.text(15.8, y+1, 'REAL-TIME\nWIP!', ha='center', fontsize=7, 
            weight='bold', color='green', bbox=dict(boxstyle='round', facecolor='lightgreen'))
    create_arrow(ax, 4, y, 8, y-2.3, color='green')
    y -= 2.8
    
    # Transfer Auto!
    create_box(ax, 3, y, 10, 1, 
               'Transfer Embroidery → Sewing: INSTANT sync! (no delay!)',
               'lightcyan', fontsize=8, edge_color='darkgreen', edge_width=2)
    create_arrow(ax, 8, y, 8, y-0.3, color='green')
    y -= 1.5
    
    # Dept 3: Sewing (AUTO!)
    create_box(ax, 1, y, 7, 3, 
               'DEPT 3: SEWING (38 LINES AUTO!)\n' +
               '✓ 38 lines: AUTO-TRACKED INSTANT!\n' +
               '✓ Per-line performance: REAL-TIME!\n' +
               '✓ Admin time: ZERO! (vs 2-3 jam!)\n' +
               '✓ Aggregate output: 1010 pcs automatic\n' +
               '✓ Tahu order IKEA mana (MO reference!)',
               'lightgreen', fontsize=8, bold=True, edge_color='darkgreen', edge_width=3)
    create_box(ax, 9, y, 6, 3, 
               'QC CHECKPOINT 2\n' +
               '✓ QC integrated ke MO!\n' +
               '✓ Defect: 30, Pass: 1010\n' +
               '✓ Defect by LINE tracked!\n' +
               '✓ Pattern analysis ready!\n' +
               '✓ Line performance: REAL-TIME!\n' +
               '✓ Rework: TRACKED!',
               'lightcyan', fontsize=8, edge_color='darkgreen', edge_width=2)
    ax.text(15.8, y+1.5, 'ZERO\nADMIN!', ha='center', fontsize=7, 
            weight='bold', color='green', bbox=dict(boxstyle='round', facecolor='lightgreen'))
    create_arrow(ax, 4, y, 8, y-3.5, color='green')
    y -= 4
    
    # Transfer Auto!
    create_box(ax, 3, y, 10, 1, 
               'Transfer Sewing → Finishing: AUTO-RECORDED! (never forget!)',
               'lightcyan', fontsize=8, edge_color='darkgreen', edge_width=2)
    create_arrow(ax, 8, y, 8, y-0.3, color='green')
    y -= 1.5
    
    # Dept 4: Finishing
    create_box(ax, 1, y, 7, 3, 
               'DEPT 4: FINISHING (2-STAGE)\n' +
               '✓ Stage 1 (Stuffing): Intermediate TRACKED!\n' +
               '✓ Stage 2 (Closing): 1010 pcs\n' +
               '✓ Label info: AUTO-DISPLAY dari PO Label!\n' +
               '✓ SYSTEM LOCKED! (cannot change!)\n' +
               '✓ ZERO SALAH LIHAT! (no human error!)',
               'lightgreen', fontsize=8, bold=True, edge_color='darkgreen', edge_width=3)
    create_box(ax, 9, y, 6, 3, 
               'QC CHECKPOINT 3\n' +
               '✓ QC integrated ke MO!\n' +
               '✓ Defect: 10, Pass: 1000\n' +
               '✓ Defect by STAGE tracked!\n' +
               '✓ Pattern analysis ready!\n' +
               '✓ Rework: TRACKED!',
               'lightcyan', fontsize=8, edge_color='darkgreen', edge_width=2)
    ax.text(15.8, y+1.5, 'LABEL\nLOCKED!', ha='center', fontsize=7, 
            weight='bold', color='green', bbox=dict(boxstyle='round', facecolor='lightgreen'))
    create_arrow(ax, 4, y, 8, y-3.5, color='green')
    y -= 4
    
    # Transfer Auto (SECURED!)
    create_box(ax, 3, y, 10, 1.2, 
               'Transfer Finishing → Packing: LABEL INFO CORRECT! (ZERO MIX LABEL!)',
               'lightgreen', fontsize=8, bold=True, edge_color='darkgreen', edge_width=3)
    create_arrow(ax, 8, y, 8, y-0.3, color='green')
    y -= 1.8
    
    # Dept 5: Packing (SECURED!)
    create_box(ax, 1, y, 7, 3.2, 
               'DEPT 5: PACKING\n' +
               '✓ Label info: AUTO-INHERIT dari PO Label!\n' +
               '✓ SYSTEM LOCKED! (cannot change!)\n' +
               '✓ QTY VALIDATION: System BLOCK if missing!\n' +
               '✓ Packing: Group automatic by Week & Dest\n' +
               '✓ ZERO MIX LABEL! (impossible!)\n' +
               '✓ ZERO QTY KURANG! (system validate!)',
               'lightgreen', fontsize=8, bold=True, edge_color='darkgreen', edge_width=3)
    create_box(ax, 9, y, 6, 3.2, 
               'QC CHECKPOINT 4 (FG)\n' +
               '✓ QC integrated ke MO!\n' +
               '✓ Unit: PER PALLET\n' +
               '✓ Barcode scan validation!\n' +
               '✓ Double-check Label auto!\n' +
               '✓ Pass: 15 pallet\n' +
               '✓ Defect: 2 pallet tracked!\n' +
               '✓ Admin QC: Dashboard easy!',
               'lightcyan', fontsize=8, edge_color='darkgreen', edge_width=2)
    ax.text(15.8, y+1.6, 'ZERO\nMIX!', ha='center', fontsize=7, 
            weight='bold', color='green', bbox=dict(boxstyle='round', facecolor='lightgreen'))
    
    # BENEFITS BOX
    y -= 4
    create_box(ax, 1, y, 14, 3.5, 
               'KEY BENEFITS:\n' +
               '✓ MO AUTO + 5 WO! System koordinasi semua dept (sinkron 100%!)\n' +
               '✓ 38 sewing lines: AUTO-TRACKED! Admin time: 2-3 jam → ZERO!\n' +
               '✓ Material consumption: AUTO-BACKFLUSH! Reconciliation: AUTOMATIC!\n' +
               '✓ QC integrated: 4 checkpoints terintegrasi ke MO! (IKEA audit ready!)\n' +
               '✓ ZERO MIX LABEL! (auto-inherit + locked + validation!)\n' +
               '✓ ZERO QTY KURANG! (system block if mismatch!)\n' +
               '✓ Rework: 100% TRACKED! (cost analysis + pattern detection ready!)\n' +
               '✓ Admin time: -60% to -90%! Reconciliation: 2-4 jam → AUTOMATIC!',
               'honeydew', fontsize=9, bold=True, edge_color='darkgreen', edge_width=3)
    
    plt.tight_layout()
    plt.savefig('DIAGRAM_4_ODOO_PRODUCTION.png', dpi=300, bbox_inches='tight')
    print("✓ Created: DIAGRAM_4_ODOO_PRODUCTION.png")
    plt.close()


# ========== DIAGRAM 5: SIDE-BY-SIDE COMPARISON (VISUAL FLOWCHART) ==========
def diagram_5_comparison():
    """Diagram 5: Side-by-side Comparison (Manual vs Odoo)"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 24))
    
    # === LEFT: MANUAL (RED) ===
    ax1.set_xlim(0, 9)
    ax1.set_ylim(0, 28)
    ax1.axis('off')
    
    ax1.text(4.5, 27, 'MANUAL SYSTEM', 
             ha='center', fontsize=16, weight='bold', color='darkred')
    ax1.text(4.5, 26.3, '(Current - Excel-based)', 
             ha='center', fontsize=10, style='italic', color='darkred')
    
    y1 = 25
    
    # Manual steps (simplified)
    manual_steps = [
        ('IKEA Order', 'Manual input', 'lightcoral', 1.2),
        ('BOM Explosion', '30 MIN manual!\nExcel lookup\n478 SKU nightmare', 'lightcoral', 2),
        ('UOM Convert', 'MANUAL calc\nERROR frequent!', 'lightcoral', 1.8),
        ('Pallet Calc', 'MANUAL formula\nComplex IKEA rules', 'lightcoral', 1.8),
        ('Stock Check', 'DELAY 1-2 JAM!\nExcel outdated', 'lightcoral', 1.8),
        ('Create PO', 'Manual Excel\nCopy-paste TYPO!', 'lightcoral', 1.8),
        ('Track PO', 'Email manual\nSuplier overwhelmed', 'lightcoral', 1.8),
        ('Material In', 'End-of-day entry\nSalah entry!', 'lightcoral', 1.5),
        ('Production', 'NO MO!\nTiap dept sendiri', 'red', 1.5),
        ('38 Lines', '2-3 JAM admin!\nManual aggregate', 'red', 1.8),
        ('QC Data', '4 checkpoints\nExcel TERPISAH!', 'lightcoral', 1.8),
        ('Label Info', 'Manual lihat\nSALAH LIHAT!', 'red', 1.8),
        ('Packing', 'MIX LABEL!\nQTY KURANG!', 'red', 1.8),
        ('Reconcile', 'Meeting 2-4 jam\nData tidak match!', 'lightcoral', 1.8),
    ]
    
    for i, (title, desc, color, height) in enumerate(manual_steps):
        create_box(ax1, 1, y1, 7, height, 
                   f'{title}\n{desc}', 
                   color, fontsize=8, edge_color='red', edge_width=2)
        if i < len(manual_steps) - 1:
            create_arrow(ax1, 4.5, y1, 4.5, y1-0.3, color='red')
        y1 -= (height + 0.5)
    
    # === RIGHT: ODOO (GREEN) ===
    ax2.set_xlim(0, 9)
    ax2.set_ylim(0, 28)
    ax2.axis('off')
    
    ax2.text(4.5, 27, 'ODOO SYSTEM', 
             ha='center', fontsize=16, weight='bold', color='darkgreen')
    ax2.text(4.5, 26.3, '(2026 - Automated)', 
             ha='center', fontsize=10, style='italic', color='darkgreen')
    
    y2 = 25
    
    # Odoo steps (simplified)
    odoo_steps = [
        ('IKEA Order', 'Input to Odoo', 'lightgreen', 1.2),
        ('BOM Explosion', 'INSTANT!\nAuto-calculate\n478 SKU automatic', 'lightgreen', 2),
        ('UOM Convert', 'AUTOMATIC!\nZERO ERROR!', 'lightgreen', 1.8),
        ('Pallet Calc', 'AUTOMATIC!\n100% accurate', 'lightgreen', 1.8),
        ('Stock Check', 'REAL-TIME!\nNo delay!', 'lightgreen', 1.8),
        ('Create PO', 'Auto-generate\nEmail auto-send!', 'lightgreen', 1.8),
        ('Track PO', 'Dashboard auto\nNotification auto!', 'lightgreen', 1.8),
        ('Material In', 'Stock INSTANT!\nNo manual entry', 'lightgreen', 1.5),
        ('Production', 'MO AUTO!\nAll dept coordinated', 'lightgreen', 1.5),
        ('38 Lines', 'AUTO-TRACKED!\nZERO admin time!', 'lightgreen', 1.8),
        ('QC Data', '4 checkpoints\nINTEGRATED!', 'lightgreen', 1.8),
        ('Label Info', 'AUTO-INHERIT!\nSYSTEM LOCKED!', 'lightgreen', 1.8),
        ('Packing', 'ZERO MIX LABEL!\nQTY VALIDATED!', 'lightgreen', 1.8),
        ('Reconcile', 'AUTOMATIC!\n0 jam meeting!', 'lightgreen', 1.8),
    ]
    
    for i, (title, desc, color, height) in enumerate(odoo_steps):
        create_box(ax2, 1, y2, 7, height, 
                   f'{title}\n{desc}', 
                   color, fontsize=8, bold=True, edge_color='darkgreen', edge_width=2)
        if i < len(odoo_steps) - 1:
            create_arrow(ax2, 4.5, y2, 4.5, y2-0.3, color='green')
        y2 -= (height + 0.5)
    
    plt.tight_layout()
    plt.savefig('DIAGRAM_5_COMPARISON_SIDE_BY_SIDE.png', dpi=300, bbox_inches='tight')
    print("✓ Created: DIAGRAM_5_COMPARISON_SIDE_BY_SIDE.png")
    plt.close()


def main():
    """Generate all IMPROVED workflow diagrams"""
    print("\n=== GENERATING IMPROVED WORKFLOW DIAGRAMS ===\n")
    
    diagram_1_manual_purchasing()
    diagram_2_odoo_purchasing()
    diagram_3_manual_production()
    diagram_4_odoo_production()
    diagram_5_comparison()
    
    print("\n✓ All diagrams generated successfully!")
    print("\nFiles created:")
    print("  1. DIAGRAM_1_MANUAL_PURCHASING.png - Purchasing Manual (with pain points)")
    print("  2. DIAGRAM_2_ODOO_PURCHASING.png - Purchasing Odoo (automated)")
    print("  3. DIAGRAM_3_MANUAL_PRODUCTION.png - Production 5 dept Manual (with pain points)")
    print("  4. DIAGRAM_4_ODOO_PRODUCTION.png - Production 5 dept Odoo (automated)")
    print("  5. DIAGRAM_5_COMPARISON_SIDE_BY_SIDE.png - Side-by-side comparison flowchart")
    print("\n✓ READY for management presentation!")
    print("\nKey improvements:")
    print("  • Clear MANUAL vs ODOO comparison")
    print("  • Visual flowcharts (not just text)")
    print("  • Pain points highlighted (red badges)")
    print("  • Benefits emphasized (green theme)")
    print("  • Better layout and spacing")

if __name__ == '__main__':
    main()
