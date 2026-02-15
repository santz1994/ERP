"""
Generate BEFORE vs AFTER comparison diagrams
Side-by-side comparison for easy presentation
"""
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, Rectangle

plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans']

def create_comparison_purchasing():
    """Purchasing: BEFORE vs AFTER"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 10))
    
    # === LEFT: MANUAL (BEFORE) ===
    ax1.set_xlim(0, 10)
    ax1.set_ylim(0, 12)
    ax1.axis('off')
    
    # Title
    ax1.text(5, 11.5, 'BEFORE: MANUAL', ha='center', fontsize=14, weight='bold', color='red')
    ax1.add_patch(Rectangle((0, 0), 10, 12, facecolor='mistyrose', alpha=0.3))
    
    y = 10.5
    steps = [
        ('Excel BOM Manual', '30 MENIT per order!', 'red'),
        ('Calculator Multi-unit', 'ERROR PRONE!', 'red'),
        ('Pallet Calculation', 'SERING SALAH!', 'red'),
        ('Call Warehouse', 'Delay 1-2 JAM!', 'red'),
        ('Create PO Manual', 'TYPO RISK!', 'red'),
        ('Email Manual', 'Manual track Excel', 'red')
    ]
    
    for step, problem, color in steps:
        # Step box
        box = FancyBboxPatch((1, y-0.8), 8, 0.7, 
                            boxstyle="round,pad=0.05", 
                            edgecolor='black', 
                            facecolor='lightcoral', 
                            linewidth=2)
        ax1.add_patch(box)
        ax1.text(5, y-0.45, step, ha='center', va='center', fontsize=9, weight='bold')
        
        # Problem badge
        ax1.text(9.5, y-0.45, problem, 
                ha='center', va='center',
                fontsize=7, weight='bold',
                bbox=dict(boxstyle='round', facecolor=color, alpha=0.7),
                color='white')
        
        # Arrow
        ax1.arrow(5, y-0.85, 0, -0.5, head_width=0.3, head_length=0.15, fc='black', ec='black')
        y -= 1.5
    
    # Summary
    ax1.text(5, 0.8, 'TOTAL: 3-4 JAM!', 
            ha='center', fontsize=12, weight='bold',
            bbox=dict(boxstyle='round', facecolor='red', alpha=0.8),
            color='white')
    
    # === RIGHT: ODOO (AFTER) ===
    ax2.set_xlim(0, 10)
    ax2.set_ylim(0, 12)
    ax2.axis('off')
    
    # Title
    ax2.text(5, 11.5, 'AFTER: ODOO ERP', ha='center', fontsize=14, weight='bold', color='green')
    ax2.add_patch(Rectangle((0, 0), 10, 12, facecolor='lightgreen', alpha=0.2))
    
    y = 10.5
    steps_odoo = [
        ('BOM Explosion', '1 KLIK! 2 detik!', 'green'),
        ('Multi-unit Auto', 'Zero error!', 'green'),
        ('Pallet Auto', 'Rules engine!', 'green'),
        ('Stock Real-time', 'Instant!', 'green'),
        ('PO Auto-create', 'Zero typo!', 'green'),
        ('Email Auto + Track', 'Dashboard real-time', 'green')
    ]
    
    for step, benefit, color in steps_odoo:
        # Step box
        box = FancyBboxPatch((1, y-0.8), 8, 0.7, 
                            boxstyle="round,pad=0.05", 
                            edgecolor='black', 
                            facecolor='lightgreen', 
                            linewidth=2)
        ax2.add_patch(box)
        ax2.text(5, y-0.45, step, ha='center', va='center', fontsize=9, weight='bold')
        
        # Benefit badge
        ax2.text(9.5, y-0.45, benefit, 
                ha='center', va='center',
                fontsize=7, weight='bold',
                bbox=dict(boxstyle='round', facecolor=color, alpha=0.7),
                color='white')
        
        # Arrow
        ax2.arrow(5, y-0.85, 0, -0.5, head_width=0.3, head_length=0.15, fc='black', ec='black')
        y -= 1.5
    
    # Summary
    ax2.text(5, 0.8, 'TOTAL: 5-10 MENIT!', 
            ha='center', fontsize=12, weight='bold',
            bbox=dict(boxstyle='round', facecolor='green', alpha=0.8),
            color='white')
    
    # Overall improvement
    fig.text(0.5, 0.02, 'IMPROVEMENT: 95% FASTER + ZERO ERROR!', 
            ha='center', fontsize=14, weight='bold',
            bbox=dict(boxstyle='round', facecolor='gold', alpha=0.8))
    
    plt.tight_layout()
    plt.savefig('COMPARISON_1_PURCHASING.png', dpi=300, bbox_inches='tight')
    print("✓ Created: COMPARISON_1_PURCHASING.png")
    plt.close()

def create_comparison_production():
    """Production: BEFORE vs AFTER"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 12))
    
    # === LEFT: MANUAL (BEFORE) ===
    ax1.set_xlim(0, 10)
    ax1.set_ylim(0, 14)
    ax1.axis('off')
    
    ax1.text(5, 13.5, 'BEFORE: MANUAL', ha='center', fontsize=14, weight='bold', color='red')
    ax1.add_patch(Rectangle((0, 0), 10, 14, facecolor='mistyrose', alpha=0.3))
    
    y = 12.5
    
    # No MO/WO
    box = FancyBboxPatch((1, y-1), 8, 0.9, 
                        boxstyle="round,pad=0.05", 
                        edgecolor='black', 
                        facecolor='red', 
                        linewidth=3)
    ax1.add_patch(box)
    ax1.text(5, y-0.55, 'TIDAK ADA MO/WO!\nHanya Excel terpisah', 
            ha='center', va='center', fontsize=9, weight='bold', color='white')
    ax1.arrow(5, y-1.05, 0, -0.4, head_width=0.3, head_length=0.15, fc='black', ec='black')
    y -= 2
    
    # 5 Departments problems
    depts = [
        'Cutting: Form kertas',
        'Embroidery: No validation',
        'Sewing 38: Manual 2-3 jam!',
        'Finishing: Mix Label risk!',
        'Packing: Qty missing!'
    ]
    
    for dept in depts:
        box = FancyBboxPatch((1.5, y-0.6), 7, 0.55, 
                            boxstyle="round,pad=0.05", 
                            edgecolor='black', 
                            facecolor='lightcoral', 
                            linewidth=2)
        ax1.add_patch(box)
        ax1.text(5, y-0.325, dept, ha='center', va='center', fontsize=8, weight='bold')
        ax1.arrow(5, y-0.65, 0, -0.3, head_width=0.3, head_length=0.1, fc='black', ec='black')
        y -= 1.1
    
    # QC separate
    box = FancyBboxPatch((1, y-0.8), 8, 0.75, 
                        boxstyle="round,pad=0.05", 
                        edgecolor='black', 
                        facecolor='mistyrose', 
                        linewidth=2)
    ax1.add_patch(box)
    ax1.text(5, y-0.425, 'QC: Excel TERPISAH!\n1 Admin OVERWHELMED!', 
            ha='center', va='center', fontsize=8, weight='bold')
    
    # Summary
    y = 1.5
    ax1.text(5, y, 'Admin: 7-10 JAM/hari\nMeeting: 2-4 JAM manual\nIKEA AUDIT RISK!', 
            ha='center', va='top', fontsize=9, weight='bold',
            bbox=dict(boxstyle='round', facecolor='red', alpha=0.8),
            color='white')
    
    # === RIGHT: ODOO (AFTER) ===
    ax2.set_xlim(0, 10)
    ax2.set_ylim(0, 14)
    ax2.axis('off')
    
    ax2.text(5, 13.5, 'AFTER: ODOO ERP', ha='center', fontsize=14, weight='bold', color='green')
    ax2.add_patch(Rectangle((0, 0), 10, 14, facecolor='lightgreen', alpha=0.2))
    
    y = 12.5
    
    # MO/WO formal
    box = FancyBboxPatch((1, y-1), 8, 0.9, 
                        boxstyle="round,pad=0.05", 
                        edgecolor='black', 
                        facecolor='green', 
                        linewidth=3)
    ax2.add_patch(box)
    ax2.text(5, y-0.55, 'MO/WO FORMAL!\n1-klik create + track', 
            ha='center', va='center', fontsize=9, weight='bold', color='white')
    ax2.arrow(5, y-1.05, 0, -0.4, head_width=0.3, head_length=0.15, fc='black', ec='black')
    y -= 2
    
    # 5 Departments solutions
    depts_odoo = [
        'Cutting: Auto backflush',
        'Embroidery: Auto validation',
        'Sewing 38: Real-time auto!',
        'Finishing: Label LOCKED!',
        'Packing: System blocks Mix!'
    ]
    
    for dept in depts_odoo:
        box = FancyBboxPatch((1.5, y-0.6), 7, 0.55, 
                            boxstyle="round,pad=0.05", 
                            edgecolor='black', 
                            facecolor='lightgreen', 
                            linewidth=2)
        ax2.add_patch(box)
        ax2.text(5, y-0.325, dept, ha='center', va='center', fontsize=8, weight='bold')
        ax2.arrow(5, y-0.65, 0, -0.3, head_width=0.3, head_length=0.1, fc='black', ec='black')
        y -= 1.1
    
    # QC integrated
    box = FancyBboxPatch((1, y-0.8), 8, 0.75, 
                        boxstyle="round,pad=0.05", 
                        edgecolor='black', 
                        facecolor='lightgreen', 
                        linewidth=2)
    ax2.add_patch(box)
    ax2.text(5, y-0.425, 'QC: TERINTEGRASI!\n4 checkpoints automatic!', 
            ha='center', va='center', fontsize=8, weight='bold')
    
    # Summary
    y = 1.5
    ax2.text(5, y, 'Admin: 2-3 JAM/hari\nMeeting: TIDAK PERLU!\nZERO Mix Label!', 
            ha='center', va='top', fontsize=9, weight='bold',
            bbox=dict(boxstyle='round', facecolor='green', alpha=0.8),
            color='white')
    
    # Overall improvement
    fig.text(0.5, 0.02, 'IMPROVEMENT: 70% FASTER + ZERO MIX LABEL + IKEA COMPLIANCE!', 
            ha='center', fontsize=14, weight='bold',
            bbox=dict(boxstyle='round', facecolor='gold', alpha=0.8))
    
    plt.tight_layout()
    plt.savefig('COMPARISON_2_PRODUCTION.png', dpi=300, bbox_inches='tight')
    print("✓ Created: COMPARISON_2_PRODUCTION.png")
    plt.close()

def create_comparison_benefits():
    """Overall benefits comparison"""
    fig, ax = plt.subplots(figsize=(16, 10))
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 12)
    ax.axis('off')
    
    # Title
    ax.text(8, 11.5, 'ODOO ERP IMPLEMENTATION BENEFITS', 
            ha='center', fontsize=16, weight='bold')
    ax.text(8, 11, 'PT Quty Karunia - Soft Toys Manufacturing', 
            ha='center', fontsize=12)
    
    # Left column: BEFORE (Problems)
    ax.text(4, 10, 'BEFORE: Manual System', 
            ha='center', fontsize=13, weight='bold', color='red')
    
    problems = [
        ('Time Efficiency', 'Purchasing: 3-4 JAM\nProduction: 7-10 JAM admin/hari\nReconciliation: 2-4 JAM meeting', 'red'),
        ('Data Accuracy', 'BOM: Manual 30 menit (error prone)\nMulti-unit: Calculator (ERROR!)\nPallet: Sering salah calculation', 'red'),
        ('Process Integration', 'TIDAK TERINTEGRASI!\nPurchasing ↔ Warehouse: Telepon\nWarehouse ↔ Production: Form kertas\nQC: Excel TERPISAH!', 'red'),
        ('Quality Control', 'Excel terpisah (4 checkpoints)\n1 Admin OVERWHELMED!\nTidak traceable → IKEA audit risk!', 'red'),
        ('Label Management', 'Manual lihat Email/Excel\nSALAH LIHAT FREQUENT!\nMIX LABEL RISK TINGGI!', 'red'),
    ]
    
    y = 9
    for title, desc, color in problems:
        box = FancyBboxPatch((0.5, y-1.2), 7, 1.15, 
                            boxstyle="round,pad=0.05", 
                            edgecolor='darkred', 
                            facecolor='mistyrose', 
                            linewidth=2)
        ax.add_patch(box)
        ax.text(4, y-0.3, title, ha='center', va='top', 
                fontsize=10, weight='bold', color=color)
        ax.text(4, y-0.65, desc, ha='center', va='top', 
                fontsize=7, style='italic')
        y -= 1.4
    
    # Right column: AFTER (Benefits)
    ax.text(12, 10, 'AFTER: Odoo ERP', 
            ha='center', fontsize=13, weight='bold', color='green')
    
    benefits = [
        ('Time Efficiency', 'Purchasing: 5-10 MENIT! (95% faster)\nProduction: 2-3 JAM! (70% faster)\nReconciliation: REAL-TIME!', 'green'),
        ('Data Accuracy', 'BOM: 1-KLIK 2 detik! (ZERO error)\nMulti-unit: AUTO! (ZERO error)\nPallet: Rules engine! (100% akurat)', 'green'),
        ('Process Integration', 'FULLY INTEGRATED!\nPurchasing → Warehouse: Real-time\nWarehouse → Production: Automatic\nQC: TERINTEGRASI sistem!', 'green'),
        ('Quality Control', '4 checkpoints integrated!\nDashboard automatic!\nFull traceable → IKEA compliance!', 'green'),
        ('Label Management', 'Auto-inherit + LOCKED!\nSystem validation!\nZERO Mix Label risk!', 'green'),
    ]
    
    y = 9
    for title, desc, color in benefits:
        box = FancyBboxPatch((8.5, y-1.2), 7, 1.15, 
                            boxstyle="round,pad=0.05", 
                            edgecolor='darkgreen', 
                            facecolor='lightgreen', 
                            linewidth=2)
        ax.add_patch(box)
        ax.text(12, y-0.3, title, ha='center', va='top', 
                fontsize=10, weight='bold', color=color)
        ax.text(12, y-0.65, desc, ha='center', va='top', 
                fontsize=7, style='italic')
        y -= 1.4
    
    # Bottom summary
    summary_box = FancyBboxPatch((1, 0.3), 14, 1, 
                                boxstyle="round,pad=0.1", 
                                edgecolor='black', 
                                facecolor='gold', 
                                linewidth=3)
    ax.add_patch(summary_box)
    ax.text(8, 0.8, 'OVERALL IMPACT: 80% TIME REDUCTION + ZERO ERROR + IKEA COMPLIANCE + SCALABLE!', 
            ha='center', va='center', 
            fontsize=11, weight='bold')
    
    plt.tight_layout()
    plt.savefig('COMPARISON_3_BENEFITS_OVERVIEW.png', dpi=300, bbox_inches='tight')
    print("✓ Created: COMPARISON_3_BENEFITS_OVERVIEW.png")
    plt.close()

def main():
    """Generate all comparison diagrams"""
    print("\n=== GENERATING BEFORE vs AFTER COMPARISON DIAGRAMS ===\n")
    
    create_comparison_purchasing()
    create_comparison_production()
    create_comparison_benefits()
    
    print("\n✓ All comparison diagrams generated successfully!")
    print("\nFiles created:")
    print("  1. COMPARISON_1_PURCHASING.png")
    print("  2. COMPARISON_2_PRODUCTION.png")
    print("  3. COMPARISON_3_BENEFITS_OVERVIEW.png")
    print("\nThese show BEFORE vs AFTER side-by-side for easy comparison!")

if __name__ == '__main__':
    main()
