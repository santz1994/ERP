"""
Generate MANUAL (BEFORE) workflow diagrams
Shows current manual system problems
"""
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans']

def create_box(ax, x, y, width, height, text, color='lightblue', fontsize=9, bold=False):
    """Create a rounded box with text"""
    box = FancyBboxPatch((x, y), width, height, 
                          boxstyle="round,pad=0.05", 
                          edgecolor='black', 
                          facecolor=color, 
                          linewidth=2)
    ax.add_patch(box)
    
    weight = 'bold' if bold else 'normal'
    ax.text(x + width/2, y + height/2, text, 
            ha='center', va='center', 
            fontsize=fontsize, weight=weight,
            wrap=True)

def create_arrow(ax, x1, y1, x2, y2, label=''):
    """Create an arrow"""
    arrow = FancyArrowPatch((x1, y1), (x2, y2),
                           arrowstyle='->', 
                           mutation_scale=20, 
                           linewidth=2,
                           color='black')
    ax.add_patch(arrow)
    
    if label:
        mid_x = (x1 + x2) / 2
        mid_y = (y1 + y2) / 2
        ax.text(mid_x + 0.3, mid_y, label, 
                fontsize=8, style='italic',
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

def create_problem_badge(ax, x, y, text):
    """Create a problem badge"""
    ax.text(x, y, text, 
            ha='center', va='center',
            fontsize=7, weight='bold',
            bbox=dict(boxstyle='round', facecolor='red', alpha=0.7, edgecolor='darkred'),
            color='white')

def diagram_manual_purchasing():
    """MANUAL Purchasing Workflow (BEFORE)"""
    fig, ax = plt.subplots(figsize=(12, 18))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 22)
    ax.axis('off')
    
    # Title
    ax.text(5, 21, 'MANUAL PURCHASING WORKFLOW (BEFORE)', 
            ha='center', fontsize=16, weight='bold', color='red')
    ax.text(5, 20.3, 'Current System - PT Quty Karunia', 
            ha='center', fontsize=12)
    
    y = 19
    
    # Step 1: Order Input
    create_box(ax, 1, y, 8, 1.2, 
               'STEP 1: Terima Order IKEA\n' +
               'Buka Excel, catat SKU, quantity, deadline',
               'lightyellow', fontsize=9)
    create_arrow(ax, 5, y, 5, y-0.5)
    y -= 2
    
    # Step 2: BOM Manual
    create_box(ax, 1, y, 8, 1.8, 
               'STEP 2: BOM EXPLOSION MANUAL!\n' +
               'Buka Excel BOM untuk tiap SKU (478 SKU!)\n' +
               'Calculate material satu-satu (30 MENIT!)',
               'lightcoral', fontsize=9, bold=True)
    create_problem_badge(ax, 9.5, y+0.9, 'PROBLEM:\n30 menit!')
    create_arrow(ax, 5, y, 5, y-0.5)
    y -= 2.5
    
    # Step 3: Multi-unit Manual
    create_box(ax, 1, y, 8, 2, 
               'STEP 3: Multi-Unit Conversion MANUAL!\n' +
               'Fabric: ROLL → PCS (pakai kalkulator!)\n' +
               'Filling: KG → GRAM\n' +
               'ERROR PRONE! Sering salah conversion!',
               'lightcoral', fontsize=8, bold=True)
    create_problem_badge(ax, 9.5, y+1, 'PROBLEM:\nError prone!')
    create_arrow(ax, 5, y, 5, y-0.5)
    y -= 2.8
    
    # Step 4: Pallet Manual
    create_box(ax, 1, y, 8, 2.2, 
               'STEP 4: Pallet Calculation MANUAL!\n' +
               'IKEA rules: Karton per pallet HARUS GENAP!\n' +
               'Admin calculate pakai Excel formula\n' +
               'Example: 1523 pcs → ??? pallet\n' +
               'SERING SALAH CALCULATION!',
               'lightcoral', fontsize=8, bold=True)
    create_problem_badge(ax, 9.5, y+1.1, 'PROBLEM:\nSering salah!')
    create_arrow(ax, 5, y, 5, y-0.5)
    y -= 3
    
    # Step 5: Stock Check Manual
    create_box(ax, 1, y, 8, 1.8, 
               'STEP 5: Check Stock MANUAL!\n' +
               'Telepon/WA ke Warehouse: "Stock ada?"\n' +
               'Warehouse cek manual → Delay 1-2 JAM!\n' +
               'Data NOT REAL-TIME!',
               'lightcoral', fontsize=8, bold=True)
    create_problem_badge(ax, 9.5, y+0.9, 'PROBLEM:\nDelay 1-2 jam!')
    create_arrow(ax, 5, y, 5, y-0.5)
    y -= 2.5
    
    # Step 6: PO Manual
    create_box(ax, 1, y, 8, 2, 
               'STEP 6: Create PO MANUAL!\n' +
               'Ketik manual di Excel PO\n' +
               'Copy-paste material (RESIKO TYPO!)\n' +
               'Email manual ke supplier\n' +
               'Track delivery: Manual Excel + Email',
               'lightcoral', fontsize=8, bold=True)
    create_problem_badge(ax, 9.5, y+1, 'PROBLEM:\nTypo + Manual!')
    
    # PROBLEMS Summary
    y -= 3
    create_box(ax, 0.5, y, 9, 3.2, 
               'CRITICAL PROBLEMS:\n\n' +
               '1. BOM explosion: 30 MENIT manual!\n' +
               '2. Multi-unit: ERROR PRONE (salah conversion)\n' +
               '3. Pallet calc: SERING SALAH (complex IKEA rules)\n' +
               '4. Stock check: DELAY 1-2 JAM (not real-time)\n' +
               '5. PO creation: MANUAL + TYPO RISK\n' +
               '6. PO tracking: MANUAL Excel (sering lupa update)\n\n' +
               'TOTAL TIME: 3-4 JAM per order!',
               'mistyrose', fontsize=8, bold=True)
    
    plt.tight_layout()
    plt.savefig('DIAGRAM_MANUAL_1_PURCHASING.png', dpi=300, bbox_inches='tight')
    print("✓ Created: DIAGRAM_MANUAL_1_PURCHASING.png")
    plt.close()

def diagram_manual_production():
    """MANUAL Production Workflow (BEFORE)"""
    fig, ax = plt.subplots(figsize=(14, 20))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 24)
    ax.axis('off')
    
    # Title
    ax.text(6, 23, 'MANUAL PRODUCTION WORKFLOW (BEFORE)', 
            ha='center', fontsize=16, weight='bold', color='red')
    ax.text(6, 22.3, 'Current System - 5 Departments', 
            ha='center', fontsize=12)
    
    y = 21
    
    # NO MO/WO
    create_box(ax, 2, y, 8, 1.5, 
               'TIDAK ADA MO/WO FORMAL!\n' +
               'Hanya verbal meeting + Excel note terpisah\n' +
               'Tidak ada koordinasi tertulis antar dept!',
               'red', fontsize=9, bold=True)
    create_problem_badge(ax, 11, y+0.75, 'CRITICAL!')
    create_arrow(ax, 6, y, 6, y-0.5)
    y -= 2.5
    
    # Dept 1: Cutting
    create_box(ax, 1, y, 5, 2, 
               'DEPT 1: CUTTING\n' +
               '• Ambil material: Surat jalan KERTAS\n' +
               '• Material consumption: TIDAK DICATAT!\n' +
               '• QC data: Excel TERPISAH!\n' +
               '• Transfer: Form kertas manual',
               'lightcoral', fontsize=8)
    create_box(ax, 7, y, 4, 2, 
               'QC MANUAL\n' +
               'Excel terpisah\n' +
               'Tidak traceable\n' +
               'IKEA audit risk!',
               'mistyrose', fontsize=7)
    create_problem_badge(ax, 11.5, y+1, 'Form kertas!')
    create_arrow(ax, 3.5, y-0.2, 6, y-2.3)
    y -= 3
    
    # Dept 2: Embroidery
    create_box(ax, 1, y, 5, 1.5, 
               'DEPT 2: EMBROIDERY\n' +
               '• Receive: Tidak ada validasi qty!\n' +
               '• WIP: Tidak tercatat real-time!',
               'lightcoral', fontsize=8)
    create_problem_badge(ax, 11.5, y+0.75, 'No validation!')
    create_arrow(ax, 3.5, y-0.2, 6, y-2)
    y -= 2.5
    
    # Dept 3: Sewing (38 LINES!)
    create_box(ax, 1, y, 5, 2.2, 
               'DEPT 3: SEWING (38 LINES!)\n' +
               '• 38 lines tracking: MANUAL!\n' +
               '• Admin aggregate: 2-3 JAM!\n' +
               '• Bottleneck: Tidak ketahuan!\n' +
               '• Per-line performance: TIDAK TAHU!',
               'lightcoral', fontsize=8, bold=True)
    create_box(ax, 7, y, 4, 2.2, 
               'QC MANUAL\n' +
               'Excel terpisah\n' +
               'Tidak tahu defect\n' +
               'per line!',
               'mistyrose', fontsize=7)
    create_problem_badge(ax, 11.5, y+1.1, 'CRITICAL:\n2-3 JAM!')
    create_arrow(ax, 3.5, y-0.2, 6, y-2.7)
    y -= 3.2
    
    # Dept 4: Finishing
    create_box(ax, 1, y, 5, 2.2, 
               'DEPT 4: FINISHING (2-STAGE)\n' +
               '• Stuffed Body: TIDAK TERCATAT!\n' +
               '• Label info: MANUAL lihat Email/Excel\n' +
               '• SALAH LIHAT Week/Destination!\n' +
               '• Mix Label START HERE!',
               'red', fontsize=8, bold=True)
    create_box(ax, 7, y, 4, 2.2, 
               'QC MANUAL\n' +
               'Excel terpisah\n' +
               'Rework tidak\n' +
               'tercatat!',
               'mistyrose', fontsize=7)
    create_problem_badge(ax, 11.5, y+1.1, 'Mix Label\nRISK!')
    create_arrow(ax, 3.5, y-0.2, 6, y-2.7)
    y -= 3.2
    
    # Dept 5: Packing (CRITICAL!)
    create_box(ax, 1, y, 5, 2.5, 
               'DEPT 5: PACKING\n' +
               '• Label info: MANUAL lihat Excel!\n' +
               '• SALAH LIHAT FREQUENT!\n' +
               '• No validation system!\n' +
               '• Qty missing: SERING!\n' +
               '• Tidak ketahuan sampai akhir!\n' +
               '• MIX LABEL RISK TINGGI!',
               'red', fontsize=8, bold=True)
    create_box(ax, 7, y, 4, 2.5, 
               'QC FG MANUAL\n' +
               '1 Admin\n' +
               'OVERWHELMED!\n' +
               'Per pallet check\n' +
               'Excel terpisah!',
               'mistyrose', fontsize=7)
    create_problem_badge(ax, 11.5, y+1.25, 'IKEA\nREJECT!')
    
    # PROBLEMS Summary
    y -= 3.5
    create_box(ax, 0.5, y, 11, 3.8, 
               'CRITICAL PROBLEMS:\n\n' +
               '1. TIDAK ADA MO/WO formal! (hanya verbal + Excel terpisah)\n' +
               '2. Material consumption: TIDAK DICATAT automatic!\n' +
               '3. 38 sewing lines: Manual aggregate 2-3 JAM!\n' +
               '4. WIP tracking: Form kertas (delay 1-2 jam)\n' +
               '5. QC data: Excel TERPISAH (tidak terintegrasi!)\n' +
               '6. Stuffed Body: TIDAK TERCATAT (intermediate stock hilang!)\n' +
               '7. MIX LABEL: FREQUENT! (salah lihat Email Week/Destination)\n' +
               '8. Qty missing: SERING! (tidak ada validation system)\n' +
               '9. Reconciliation: Meeting 2-4 JAM manual!\n' +
               '10. Admin overwhelmed: 7-10 JAM per day!',
               'mistyrose', fontsize=7, bold=True)
    
    plt.tight_layout()
    plt.savefig('DIAGRAM_MANUAL_2_PRODUCTION.png', dpi=300, bbox_inches='tight')
    print("✓ Created: DIAGRAM_MANUAL_2_PRODUCTION.png")
    plt.close()

def diagram_manual_full_integrated():
    """MANUAL Full Integrated (BEFORE)"""
    fig, ax = plt.subplots(figsize=(14, 18))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 22)
    ax.axis('off')
    
    # Title
    ax.text(6, 21, 'MANUAL FULL WORKFLOW (BEFORE)', 
            ha='center', fontsize=16, weight='bold', color='red')
    ax.text(6, 20.3, 'Current Manual System - End to End', 
            ha='center', fontsize=12)
    
    y = 19
    
    # === PURCHASING PHASE ===
    create_box(ax, 1, y, 10, 0.8, 'PURCHASING PHASE', 'darkgray', fontsize=11, bold=True)
    y -= 1.5
    
    create_box(ax, 2, y, 8, 1.5, 
               'Excel BOM Manual (30 min!) → Calculator\n' +
               'Pallet calc manual (error!) → Call Warehouse\n' +
               'Stock check delay 1-2 jam → Create PO manual',
               'lightcoral', fontsize=8)
    create_problem_badge(ax, 11, y+0.75, '3-4 JAM!')
    create_arrow(ax, 6, y, 6, y-0.5)
    y -= 2.5
    
    # === NO INTEGRATION ===
    create_box(ax, 2, y, 8, 1.2, 
               'TIDAK ADA INTEGRATION!\n' +
               'Purchasing → Warehouse: Manual telepon/WA\n' +
               'Warehouse → Production: Form kertas',
               'red', fontsize=9, bold=True)
    create_problem_badge(ax, 11, y+0.6, 'NOT CONNECTED!')
    create_arrow(ax, 6, y, 6, y-0.5)
    y -= 2
    
    # === PRODUCTION PHASE ===
    create_box(ax, 1, y, 10, 0.8, 'PRODUCTION PHASE', 'darkgray', fontsize=11, bold=True)
    y -= 1.5
    
    create_box(ax, 2, y, 8, 1.2, 
               'TIDAK ADA MO/WO! Hanya verbal + Excel terpisah',
               'red', fontsize=9, bold=True)
    create_arrow(ax, 6, y, 6, y-0.5)
    y -= 2
    
    # 5 Departments
    dept_problems = [
        ('Cutting', 'Form kertas + No material tracking'),
        ('Embroidery', 'No qty validation'),
        ('Sewing 38 lines', 'Manual 2-3 jam aggregate!'),
        ('Finishing', 'Manual lihat Label → Mix Label risk!'),
        ('Packing', 'No validation → Qty missing + Mix Label!')
    ]
    
    for i, (name, problem) in enumerate(dept_problems):
        create_box(ax, 2, y, 8, 0.9, f'{name}: {problem}', 'lightcoral', fontsize=7)
        if i < 4:
            create_arrow(ax, 6, y, 6, y-0.3)
            y -= 1.2
    
    y -= 1.5
    
    # QC Separate
    create_box(ax, 2, y, 8, 1, 
               'QC: Excel TERPISAH (4 checkpoints tidak terintegrasi!)\n' +
               '1 Admin QC OVERWHELMED!',
               'mistyrose', fontsize=8, bold=True)
    create_problem_badge(ax, 11, y+0.5, 'IKEA AUDIT RISK!')
    
    # DISCONNECT Summary
    y -= 2
    create_box(ax, 0.5, y, 11, 3, 
               'SYSTEM DISCONNECT EVERYWHERE:\n\n' +
               '• Purchasing ↔ Warehouse: Manual telepon (delay 1-2 jam)\n' +
               '• Warehouse ↔ Production: Form kertas (no real-time)\n' +
               '• Production ↔ QC: Excel terpisah (tidak terintegrasi)\n' +
               '• Inter-dept: Form kertas (mismatch frequent!)\n' +
               '• Label info: Manual lihat Email (MIX LABEL RISK!)\n' +
               '• Reconciliation: Meeting 2-4 JAM manual!\n\n' +
               'RESULT: SLOW + ERROR PRONE + IKEA COMPLIANCE RISK!',
               'mistyrose', fontsize=8, bold=True)
    
    plt.tight_layout()
    plt.savefig('DIAGRAM_MANUAL_3_FULL_INTEGRATED.png', dpi=300, bbox_inches='tight')
    print("✓ Created: DIAGRAM_MANUAL_3_FULL_INTEGRATED.png")
    plt.close()

def main():
    """Generate all MANUAL (BEFORE) workflow diagrams"""
    print("\n=== GENERATING MANUAL (BEFORE) WORKFLOW DIAGRAMS ===\n")
    
    diagram_manual_purchasing()
    diagram_manual_production()
    diagram_manual_full_integrated()
    
    print("\n✓ All MANUAL diagrams generated successfully!")
    print("\nFiles created:")
    print("  1. DIAGRAM_MANUAL_1_PURCHASING.png")
    print("  2. DIAGRAM_MANUAL_2_PRODUCTION.png")
    print("  3. DIAGRAM_MANUAL_3_FULL_INTEGRATED.png")
    print("\nThese show CURRENT MANUAL SYSTEM (BEFORE Odoo)")
    print("Use together with ODOO diagrams for comparison!")

if __name__ == '__main__':
    main()
