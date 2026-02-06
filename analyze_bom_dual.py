"""
Analyze BOM structure to design Dual-BOM system
"""
import pandas as pd
import os

def analyze_bom_department(dept_name, file_path):
    """Analyze single department BOM file"""
    if not os.path.exists(file_path):
        print(f"\n{dept_name}: FILE NOT FOUND")
        return None
    
    df = pd.read_excel(file_path)
    print(f"\n{'='*80}")
    print(f"{dept_name.upper()} BOM ANALYSIS")
    print(f"{'='*80}")
    print(f"Total BOM Lines: {len(df)}")
    print(f"\nColumns: {df.columns.tolist()}")
    
    # Get unique products
    products = df['Product'].dropna().unique()
    print(f"\nUnique Products (Articles): {len(products)}")
    print(f"Sample products: {products[:3].tolist()}")
    
    # Sample BOM lines
    print(f"\nSample BOM Lines (First 5):")
    cols_to_show = ['Product', 'BoM Lines/Component', 'BoM Lines/Component/Name', 
                    'BoM Lines/Quantity', 'BoM Lines/Product Unit of Measure']
    print(df[cols_to_show].head(5).to_string(index=False))
    
    return df

def compare_bom_structures():
    """Compare BOM across all departments to understand the pattern"""
    print("\n" + "="*80)
    print("DUAL-BOM SYSTEM ANALYSIS")
    print("="*80)
    
    departments = {
        'Cutting': 'docs/Masterdata/BOM Production/Cutting.xlsx',
        'Embroidery': 'docs/Masterdata/BOM Production/Embo.xlsx',
        'Sewing': 'docs/Masterdata/BOM Production/Sewing.xlsx',
        'Finishing': 'docs/Masterdata/BOM Production/Finishing.xlsx',
        'FinishingGoods': 'docs/Masterdata/BOM Production/Finishing Goods.xlsx',
        'Packing': 'docs/Masterdata/BOM Production/Packing.xlsx',
    }
    
    all_materials = set()
    
    for dept, path in departments.items():
        df = analyze_bom_department(dept, path)
        if df is not None:
            # Collect all materials used
            materials = df['BoM Lines/Component'].dropna().unique()
            all_materials.update(materials)
    
    print(f"\n{'='*80}")
    print("OVERALL STATISTICS")
    print(f"{'='*80}")
    print(f"Total Unique Materials across all departments: {len(all_materials)}")
    print(f"\nSample materials: {list(all_materials)[:10]}")
    
    print(f"\n{'='*80}")
    print("DUAL-BOM CONCEPT")
    print(f"{'='*80}")
    print("""
BOM PRODUCTION (Process-Oriented):
- Split by department/manufacturing stage
- Shows step-by-step transformation
- Input: Materials/WIP from previous stage
- Output: WIP/Finished Goods for next stage
- Purpose: Track production flow, labor routing, operator tasks

BOM PURCHASING (Material-Oriented):
- Consolidated view of RAW materials only
- Aggregates all material requirements from all departments
- Filters out WIP/internal components
- Purpose: Calculate procurement needs, PO generation, inventory planning

IMPLEMENTATION:
1. Database: Create 2 separate BOM tables
   - bom_production (linked to work_orders, departments, routing)
   - bom_purchasing (linked to purchase_orders, suppliers, materials)

2. Relationship:
   - 1 Article has MULTIPLE BOM Production entries (one per dept)
   - 1 Article has 1 BOM Purchasing (consolidated raw materials)

3. Sync Logic:
   - BOM Purchasing is AUTO-CALCULATED from BOM Production
   - When BOM Production changes → regenerate BOM Purchasing
   - Filter: Only include material_type = 'RAW_MATERIAL'
   - Aggregate: Sum quantities across all departments
    """)

if __name__ == "__main__":
    compare_bom_structures()
    
    print(f"\n{'='*80}")
    print("NEXT STEPS")
    print(f"{'='*80}")
    print("""
1. Update database schema:
   - Rename current bom_headers → bom_production_headers
   - Rename current bom_details → bom_production_details
   - Create new tables: bom_purchasing_headers, bom_purchasing_details

2. Update documentation:
   - prompt.md: Add dual-BOM concept
   - Rencana Tampilan.md: Update PPIC and Purchasing modules
   - PRESENTASI_MANAGEMENT: Add dual-BOM benefit section

3. Implement bulk import:
   - Import all 6 department BOM Production files
   - Auto-generate BOM Purchasing from aggregation
   - Validate material codes against Material masterdata

4. Update business logic:
   - Purchasing uses bom_purchasing for PO calculation
   - PPIC uses bom_production for MO/SPK explosion
   - Material allocation uses bom_production (dept-specific)
    """)
