"""
Generate workflow flowchart diagrams using matplotlib
Creates visual PNG images for each workflow
"""
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import os

# Set font
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
    
    # Add text
    weight = 'bold' if bold else 'normal'
    ax.text(x + width/2, y + height/2, text, 
            ha='center', va='center', 
            fontsize=fontsize, weight=weight,
            wrap=True)

def create_arrow(ax, x1, y1, x2, y2, label=''):
    """Create an arrow between two points"""
    arrow = FancyArrowPatch((x1, y1), (x2, y2),
                           arrowstyle='->', 
                           mutation_scale=20, 
                           linewidth=2,
                           color='black')
    ax.add_patch(arrow)
    
    if label:
        # Add label near arrow
        mid_x = (x1 + x2) / 2
        mid_y = (y1 + y2) / 2
        ax.text(mid_x + 0.3, mid_y, label, 
                fontsize=8, style='italic',
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

def diagram_1_purchasing_workflow():
    """Diagram 1: Purchasing Department Workflow Only"""
    fig, ax = plt.subplots(figsize=(12, 16))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 20)
    ax.axis('off')
    
    # Title
    ax.text(5, 19, 'WORKFLOW: PURCHASING DEPARTMENT', 
            ha='center', fontsize=16, weight='bold')
    ax.text(5, 18.5, 'PT Quty Karunia - Odoo ERP 2026', 
            ha='center', fontsize=12)
    
    y = 17
    
    # Step 1: IKEA Order Input
    create_box(ax, 1, y, 8, 1.2, 
               'STEP 1: IKEA Order Input\n' +
               'SKU, Quantity, Delivery Date',
               'lightgreen', fontsize=10, bold=True)
    create_arrow(ax, 5, y, 5, y-0.5)
    y -= 2
    
    # Step 2: BOM Explosion
    create_box(ax, 1, y, 8, 1.5, 
               'STEP 2: BOM EXPLOSION AUTOMATIC\n' +
               '478 SKU calculated INSTANT!\n' +
               'Multi-unit conversion automatic',
               'lightblue', fontsize=9, bold=True)
    create_arrow(ax, 5, y, 5, y-0.5)
    y -= 2.5
    
    # Step 3: Pallet Calculation
    create_box(ax, 1, y, 8, 1.5, 
               'STEP 3: PALLET CALCULATION\n' +
               'IKEA genap rules AUTOMATIC!\n' +
               'Example: 1523 pcs → 4 pallet',
               'lightyellow', fontsize=9, bold=True)
    create_arrow(ax, 5, y, 5, y-0.5)
    y -= 2.5
    
    # Step 4: Stock Check
    create_box(ax, 1, y, 8, 1.5, 
               'STEP 4: STOCK CHECK REAL-TIME\n' +
               'Warehouse + In-Transit + Reserved\n' +
               'Alert: "15 material need order"',
               'lightcoral', fontsize=9, bold=True)
    create_arrow(ax, 5, y, 5, y-0.5)
    y -= 2.5
    
    # Step 5A: PO Fabric
    create_box(ax, 0.5, y, 4, 1.8, 
               'STEP 5A: PO FABRIC\n' +
               '(Week 0)\n' +
               'Trigger: Cutting + Embroidery\n' +
               'Email auto-send!',
               'lightgreen', fontsize=8, bold=True)
    
    # Step 5B: PO Label
    create_box(ax, 5.5, y, 4, 1.8, 
               'STEP 5B: PO LABEL\n' +
               '(Week +2)\n' +
               'Label Info LOCKED\n' +
               'Auto-inherit to ALL dept!',
               'orange', fontsize=8, bold=True)
    
    create_arrow(ax, 2.5, y-0.2, 5, y-2.5)
    create_arrow(ax, 7.5, y-0.2, 5, y-2.5)
    y -= 3.5
    
    # Step 6: PO Tracking
    create_box(ax, 1, y, 8, 1.5, 
               'STEP 6: PO TRACKING DASHBOARD\n' +
               'Real-time status per PO\n' +
               'Email notification automatic',
               'lavender', fontsize=9, bold=True)
    
    # Benefits box
    y -= 2.5
    create_box(ax, 0.5, y, 9, 2, 
               'KEY BENEFITS:\n' +
               '• BOM explosion: 30 min → INSTANT\n' +
               '• Stock visibility: REAL-TIME (vs 1-2 jam delay)\n' +
               '• Pallet calc: 100% accurate (vs manual error)\n' +
               '• Efficiency: ~95% faster per order!',
               'lightgray', fontsize=9)
    
    plt.tight_layout()
    plt.savefig('DIAGRAM_1_PURCHASING_WORKFLOW.png', dpi=300, bbox_inches='tight')
    print("✓ Created: DIAGRAM_1_PURCHASING_WORKFLOW.png")
    plt.close()

def diagram_2_production_workflow():
    """Diagram 2: Production 5 Departments Workflow"""
    fig, ax = plt.subplots(figsize=(14, 18))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 22)
    ax.axis('off')
    
    # Title
    ax.text(6, 21, 'WORKFLOW: PRODUCTION 5 DEPARTMENTS', 
            ha='center', fontsize=16, weight='bold')
    ax.text(6, 20.5, 'PT Quty Karunia - Odoo ERP 2026', 
            ha='center', fontsize=12)
    
    y = 19
    
    # MO Creation
    create_box(ax, 2, y, 8, 1.5, 
               'MO AUTO-CREATE\n' +
               'Manufacturing Order coordinates all 5 WO\n' +
               'Target auto-calculated per dept',
               'gold', fontsize=10, bold=True)
    create_arrow(ax, 6, y, 6, y-0.5)
    y -= 2.5
    
    # Dept 1: Cutting
    create_box(ax, 1, y, 5, 1.8, 
               'DEPT 1: CUTTING\n' +
               '• Material: AUTO-BACKFLUSH\n' +
               '• QC integrated\n' +
               '• Transfer automatic',
               'lightblue', fontsize=8)
    create_box(ax, 7, y, 4, 1.8, 
               'QC CHECKPOINT 1\n' +
               'Pass/Rework/Reject\n' +
               'Traceable!',
               'lightcoral', fontsize=8)
    create_arrow(ax, 3.5, y-0.2, 6, y-2.3)
    y -= 2.8
    
    # Dept 2: Embroidery  
    create_box(ax, 1, y, 5, 1.5, 
               'DEPT 2: EMBROIDERY\n' +
               '• WIP validated\n' +
               '• Real-time tracking',
               'lightgreen', fontsize=8)
    create_arrow(ax, 3.5, y-0.2, 6, y-2)
    y -= 2.5
    
    # Dept 3: Sewing (38 lines!)
    create_box(ax, 1, y, 5, 1.8, 
               'DEPT 3: SEWING (38 LINES!)\n' +
               '• 38 lines AUTOMATIC tracking\n' +
               '• Per-line performance\n' +
               '• Bottleneck detection',
               'lightyellow', fontsize=8, bold=True)
    create_box(ax, 7, y, 4, 1.8, 
               'QC CHECKPOINT 2\n' +
               'Defect by LINE\n' +
               'Analysis ready!',
               'lightcoral', fontsize=8)
    create_arrow(ax, 3.5, y-0.2, 6, y-2.3)
    y -= 2.8
    
    # Dept 4: Finishing (2-stage)
    create_box(ax, 1, y, 5, 2, 
               'DEPT 4: FINISHING (2-STAGE)\n' +
               '• Stage 1: Stuffed Body TRACKED\n' +
               '• Stage 2: Closing\n' +
               '• LABEL INFO AUTO-DISPLAY!',
               'lightblue', fontsize=8, bold=True)
    create_box(ax, 7, y, 4, 2, 
               'QC CHECKPOINT 3\n' +
               'Stage 2 inspection\n' +
               'Rework tracked',
               'lightcoral', fontsize=8)
    create_arrow(ax, 3.5, y-0.2, 6, y-2.5)
    y -= 3
    
    # Dept 5: Packing (CRITICAL!)
    create_box(ax, 1, y, 5, 2.2, 
               'DEPT 5: PACKING\n' +
               '• LABEL INFO: AUTO-INHERIT!\n' +
               '• SYSTEM LOCKED!\n' +
               '• QTY VALIDATION: BLOCK if missing!\n' +
               '• ZERO MIX LABEL RISK!',
               'orange', fontsize=8, bold=True)
    create_box(ax, 7, y, 4, 2.2, 
               'QC CHECKPOINT 4 (FG)\n' +
               'DOUBLE-CHECK!\n' +
               'Scan barcode\n' +
               'Validate Label\n' +
               'ZERO MIX LABEL!',
               'red', fontsize=8, bold=True)
    create_arrow(ax, 6, y-0.2, 6, y-2.5)
    y -= 3.2
    
    # Finished Goods
    create_box(ax, 2, y, 8, 1.5, 
               'WAREHOUSE FG: READY FOR DISPATCH\n' +
               'Traceability complete • Label validated 100%\n' +
               'Qty reconciled 100%',
               'lightgreen', fontsize=9, bold=True)
    
    # Benefits
    y -= 2.5
    create_box(ax, 1, y, 10, 2.2, 
               'KEY BENEFITS:\n' +
               '• 38 sewing lines: AUTO (vs 2-3 jam manual!)\n' +
               '• Material consumption: AUTO-BACKFLUSH\n' +
               '• ZERO MIX LABEL (auto-inherit + locked)\n' +
               '• QTY VALIDATION (system block if mismatch)\n' +
               '• Admin time: -60% to -90%!',
               'lightgray', fontsize=9)
    
    plt.tight_layout()
    plt.savefig('DIAGRAM_2_PRODUCTION_5_DEPT.png', dpi=300, bbox_inches='tight')
    print("✓ Created: DIAGRAM_2_PRODUCTION_5_DEPT.png")
    plt.close()

def diagram_3_full_integrated():
    """Diagram 3: Full Integrated Workflow (Purchasing to Production)"""
    fig, ax = plt.subplots(figsize=(14, 20))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 24)
    ax.axis('off')
    
    # Title
    ax.text(6, 23, 'FULL INTEGRATED WORKFLOW', 
            ha='center', fontsize=16, weight='bold')
    ax.text(6, 22.5, 'Purchasing → Warehouse → Production (End-to-End)', 
            ha='center', fontsize=12)
    
    y = 21
    
    # === PURCHASING PHASE ===
    create_box(ax, 1, y, 10, 0.8, 'PURCHASING PHASE', 'darkgray', fontsize=11, bold=True)
    y -= 1.5
    
    create_box(ax, 2, y, 8, 1.2, 
               'IKEA Order Input → BOM Explosion → Pallet Calc',
               'lightgreen', fontsize=9)
    create_arrow(ax, 6, y, 6, y-0.5)
    y -= 2
    
    create_box(ax, 2, y, 3.5, 1, 
               'PO FABRIC\n(Week 0)',
               'lightblue', fontsize=8)
    create_box(ax, 6.5, y, 3.5, 1, 
               'PO LABEL\n(Week +2)',
               'orange', fontsize=8)
    create_arrow(ax, 3.75, y-0.2, 6, y-1.3)
    create_arrow(ax, 8.25, y-0.2, 6, y-1.3)
    y -= 2
    
    # === WAREHOUSE PHASE ===
    create_box(ax, 1, y, 10, 0.8, 'WAREHOUSE PHASE', 'darkgray', fontsize=11, bold=True)
    y -= 1.5
    
    create_box(ax, 2, y, 8, 1.2, 
               'Material Received → Stock UPDATE REAL-TIME!\n' +
               'Notification to Purchasing + Production',
               'lightcoral', fontsize=9)
    create_arrow(ax, 6, y, 6, y-0.5)
    y -= 2
    
    # === PRODUCTION PHASE ===
    create_box(ax, 1, y, 10, 0.8, 'PRODUCTION PHASE (5 DEPT)', 'darkgray', fontsize=11, bold=True)
    y -= 1.5
    
    create_box(ax, 2, y, 8, 1, 'MO Auto-Create + 5 WO', 'gold', fontsize=9, bold=True)
    create_arrow(ax, 6, y, 6, y-0.5)
    y -= 1.8
    
    # 5 Departments compact
    dept_names = ['Cutting', 'Embroidery', 'Sewing\n(38 lines!)', 'Finishing\n(2-stage)', 'Packing\n(ZERO MIX!)']
    dept_colors = ['lightblue', 'lightgreen', 'lightyellow', 'lightblue', 'orange']
    
    for i, (name, color) in enumerate(zip(dept_names, dept_colors)):
        create_box(ax, 2, y, 8, 0.8, f'DEPT {i+1}: {name}', color, fontsize=8)
        if i < 4:  # No arrow after last dept
            create_arrow(ax, 6, y, 6, y-0.3)
            y -= 1.1
    
    y -= 1
    
    # === FINISHED GOODS ===
    create_box(ax, 2, y, 8, 1.2, 
               'WAREHOUSE FG: READY DISPATCH\n' +
               'Traceability COMPLETE • IKEA Ready',
               'lightgreen', fontsize=9, bold=True)
    
    # Key Integration Points
    y -= 2
    create_box(ax, 0.5, y, 11, 2.5, 
               'KEY INTEGRATION POINTS:\n' +
               '1. Purchasing ↔ Warehouse: PO → Stock update real-time\n' +
               '2. Warehouse ↔ Production: Material ready → MO trigger\n' +
               '3. PO Label → ALL Dept: Auto-inherit (ZERO MIX LABEL!)\n' +
               '4. Production ↔ QC: 4 checkpoints integrated\n' +
               '5. Inter-dept: WIP auto-validated (NO MISMATCH!)',
               'lavender', fontsize=8)
    
    plt.tight_layout()
    plt.savefig('DIAGRAM_3_FULL_INTEGRATED.png', dpi=300, bbox_inches='tight')
    print("✓ Created: DIAGRAM_3_FULL_INTEGRATED.png")
    plt.close()

def diagram_4_before_after():
    """Diagram 4: Before vs After Comparison"""
    fig, ax = plt.subplots(figsize=(14, 10))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 12)
    ax.axis('off')
    
    # Title
    ax.text(7, 11, 'BEFORE vs AFTER ODOO', 
            ha='center', fontsize=16, weight='bold')
    
    # BEFORE (Manual)
    ax.text(3.5, 10, 'BEFORE (Manual System)', 
            ha='center', fontsize=12, weight='bold', color='red')
    
    y = 9
    problems = [
        'BOM explosion: MANUAL (30 min)',
        'Pallet calc: MANUAL (error prone!)',
        'Stock: Delay 1-2 jam',
        'WIP tracking: Form kertas (2-3 jam)',
        '38 lines: Manual aggregate (2-3 jam!)',
        'Mix Label: FREQUENT!',
        'Qty missing: SERING!',
        'Reconciliation: Meeting 2-4 jam',
        'Admin overwhelmed!'
    ]
    
    for problem in problems:
        create_box(ax, 0.5, y, 6, 0.6, problem, 'lightcoral', fontsize=7)
        y -= 0.7
    
    # AFTER (Odoo)
    ax.text(10.5, 10, 'AFTER (Odoo ERP)', 
            ha='center', fontsize=12, weight='bold', color='green')
    
    y = 9
    solutions = [
        'BOM explosion: INSTANT!',
        'Pallet calc: AUTOMATIC (100% accurate)',
        'Stock: REAL-TIME!',
        'WIP tracking: AUTOMATIC dashboard',
        '38 lines: AUTOMATIC (instant!)',
        'Mix Label: ZERO! (auto-inherit)',
        'Qty missing: ZERO! (system block)',
        'Reconciliation: AUTOMATIC (0 jam)',
        'Admin time: -60% to -90%!'
    ]
    
    for solution in solutions:
        create_box(ax, 7.5, y, 6, 0.6, solution, 'lightgreen', fontsize=7, bold=True)
        y -= 0.7
    
    # Bottom summary
    create_box(ax, 1, 0.5, 12, 1, 
               'RESULT: 95% FASTER + ZERO ERRORS + IKEA COMPLIANCE READY!',
               'gold', fontsize=11, bold=True)
    
    plt.tight_layout()
    plt.savefig('DIAGRAM_4_BEFORE_AFTER.png', dpi=300, bbox_inches='tight')
    print("✓ Created: DIAGRAM_4_BEFORE_AFTER.png")
    plt.close()

def main():
    """Generate all workflow diagrams"""
    print("\n=== GENERATING WORKFLOW DIAGRAMS ===\n")
    
    diagram_1_purchasing_workflow()
    diagram_2_production_workflow()
    diagram_3_full_integrated()
    diagram_4_before_after()
    
    print("\n✓ All diagrams generated successfully!")
    print("\nFiles created:")
    print("  1. DIAGRAM_1_PURCHASING_WORKFLOW.png")
    print("  2. DIAGRAM_2_PRODUCTION_5_DEPT.png")
    print("  3. DIAGRAM_3_FULL_INTEGRATED.png")
    print("  4. DIAGRAM_4_BEFORE_AFTER.png")
    print("\nReady to insert into PowerPoint or Word documents!")

if __name__ == '__main__':
    main()
