"""
Analyze Packing & Pallet System Requirements
Based on user's insight about fixed carton/pallet quantities
"""

import pandas as pd
import os

def analyze_packing_specifications():
    """Analyze Packing.xlsx to extract carton and pallet specifications"""
    
    file_path = 'docs/Masterdata/BOM Production/Packing.xlsx'
    
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return
    
    print("=" * 80)
    print("📦 PACKING & PALLET SYSTEM ANALYSIS")
    print("=" * 80)
    print()
    
    # Read the Excel file
    df = pd.read_excel(file_path)
    
    print(f"📊 Total rows in Packing BOM: {len(df)}")
    print(f"📋 Columns: {df.columns.tolist()}")
    print()
    
    # Extract unique articles
    articles = df['Product'].dropna().unique()
    # Filter out any remaining NaN and convert to list
    articles = [a for a in articles if pd.notna(a) and str(a).strip()]
    
    print(f"🎯 Total unique articles: {len(articles)}")
    if len(articles) > 0:
        print(f"   Sample articles: {list(articles[:3])}")
    print()
    
    # Analyze packing materials (CARTON, PALLET, PAD)
    print("=" * 80)
    print("📦 PACKING MATERIAL ANALYSIS")
    print("=" * 80)
    print()
    
    # Filter for carton materials
    carton_materials = df[df['BoM Lines/Component/Name'].str.contains('CARTON', case=False, na=False)]
    print(f"🗃️  CARTON Materials: {len(carton_materials)} records")
    
    if len(carton_materials) > 0:
        print("\n   Sample CARTON specifications:")
        for idx, row in carton_materials.head(10).iterrows():
            article = str(row['Product']) if pd.notna(row['Product']) else "N/A"
            component = row['BoM Lines/Component']
            name = row['BoM Lines/Component/Name']
            qty = row['BoM Lines/Quantity']
            uom = row['BoM Lines/Product Unit of Measure']
            
            # Calculate pcs per carton (inverse of carton ratio)
            if qty > 0 and qty < 1:
                pcs_per_carton = int(1 / qty)
            else:
                pcs_per_carton = int(qty)
            
            print(f"   • {component}: {name}")
            print(f"     Article: {article[:60]}...")
            print(f"     Ratio: {qty} {uom} → {pcs_per_carton} pcs per carton")
            print()
    
    # Filter for pallet materials
    pallet_materials = df[df['BoM Lines/Component/Name'].str.contains('PALLET', case=False, na=False)]
    print(f"📦 PALLET Materials: {len(pallet_materials)} records")
    
    if len(pallet_materials) > 0:
        print("\n   Sample PALLET specifications:")
        for idx, row in pallet_materials.head(10).iterrows():
            article = str(row['Product']) if pd.notna(row['Product']) else "N/A"
            component = row['BoM Lines/Component']
            name = row['BoM Lines/Component/Name']
            qty = row['BoM Lines/Quantity']
            uom = row['BoM Lines/Product Unit of Measure']
            
            # Calculate pcs per pallet (inverse of pallet ratio)
            if qty > 0 and qty < 1:
                pcs_per_pallet = int(1 / qty)
            else:
                pcs_per_pallet = int(qty)
            
            print(f"   • {component}: {name}")
            print(f"     Article: {article[:60]}...")
            print(f"     Ratio: {qty} {uom} → {pcs_per_pallet} pcs per pallet")
            print()
    
    # Generate packing specifications summary
    print("=" * 80)
    print("📋 PACKING SPECIFICATIONS EXTRACTION")
    print("=" * 80)
    print()
    
    # Group by article to get packing specs
    packing_specs = []
    
    for article in articles[:10]:  # Analyze first 10 articles
        article_data = df[df['Product'] == article]
        
        # Find carton spec
        carton_row = article_data[article_data['BoM Lines/Component/Name'].str.contains('CARTON', case=False, na=False)]
        pallet_row = article_data[article_data['BoM Lines/Component/Name'].str.contains('PALLET', case=False, na=False)]
        
        if len(carton_row) > 0 and len(pallet_row) > 0:
            carton_qty = carton_row.iloc[0]['BoM Lines/Quantity']
            pallet_qty = pallet_row.iloc[0]['BoM Lines/Quantity']
            
            # Calculate specs
            pcs_per_carton = int(1 / carton_qty) if carton_qty < 1 else int(carton_qty)
            pcs_per_pallet = int(1 / pallet_qty) if pallet_qty < 1 else int(pallet_qty)
            cartons_per_pallet = pcs_per_pallet // pcs_per_carton
            
            spec = {
                'article': article[:60],
                'pcs_per_carton': pcs_per_carton,
                'cartons_per_pallet': cartons_per_pallet,
                'pcs_per_pallet': pcs_per_pallet,
                'carton_ratio': carton_qty,
                'pallet_ratio': pallet_qty
            }
            
            packing_specs.append(spec)
    
    # Display packing specs
    if packing_specs:
        print("📊 PACKING SPECIFICATIONS (First 10 articles):")
        print()
        print(f"{'Article':<60} | {'Pcs/CTN':<8} | {'CTN/PLT':<8} | {'Pcs/PLT':<8}")
        print("-" * 100)
        
        for spec in packing_specs:
            print(f"{spec['article']:<60} | {spec['pcs_per_carton']:<8} | {spec['cartons_per_pallet']:<8} | {spec['pcs_per_pallet']:<8}")
    
    print()
    print("=" * 80)
    print("💡 KEY INSIGHTS FROM USER")
    print("=" * 80)
    print()
    print("1. 🎯 FIXED QUANTITIES (Critical Constraint):")
    print("   • Pcs per carton: FIXED (cannot be more or less)")
    print("   • Cartons per pallet: FIXED (cannot be more or less)")
    print("   • Must pack EXACTLY to specification")
    print()
    print("2. 📦 PACKING FLOW:")
    print("   Finishing → Packing (receive in PCS)")
    print("   Packing → Pack into CARTONS (fixed qty per carton)")
    print("   Packing → Stack CARTONS on PALLETS (fixed qty per pallet)")
    print("   Packing → Transfer to FG Warehouse (receive in PALLETS)")
    print()
    print("3. 💰 PO CALCULATION LOGIC:")
    print("   • PO quantities must be MULTIPLES of pcs_per_pallet")
    print("   • Example: If 1 pallet = 480 pcs (8 CTN × 60 pcs)")
    print("   •          Then PO = 480, 960, 1440, 1920... (no partial pallets)")
    print("   • Purchasing creates PO → specifies # of pallets to produce")
    print()
    print("4. 🔄 SYSTEM CHANGES REQUIRED:")
    print("   a. Database Schema:")
    print("      • Add to products/articles table:")
    print("        - pcs_per_carton (INTEGER, NOT NULL)")
    print("        - cartons_per_pallet (INTEGER, NOT NULL)")
    print("        - pcs_per_pallet (COMPUTED: pcs_per_carton × cartons_per_pallet)")
    print()
    print("   b. PO Kain Creation:")
    print("      • Add field: target_pallets (INTEGER)")
    print("      • Calculate MO quantity: target_pallets × pcs_per_pallet")
    print("      • Validate: PO qty MUST be multiple of pcs_per_pallet")
    print()
    print("   c. Packing Module:")
    print("      • Receive from Finishing: PCS")
    print("      • Pack into cartons: Validate exact pcs_per_carton")
    print("      • Stack on pallets: Validate exact cartons_per_pallet")
    print("      • Transfer to FG: PALLET unit (with pcs/cartons breakdown)")
    print()
    print("   d. FG Warehouse Receiving:")
    print("      • Receive in: PALLETS")
    print("      • Auto-calculate: pcs = pallets × pcs_per_pallet")
    print("      • Auto-calculate: cartons = pallets × cartons_per_pallet")
    print()
    print("5. 📊 DISPLAY FORMAT:")
    print("   FG Stock should show:")
    print("   • Primary: X pallets (physical unit)")
    print("   • Secondary: Y cartons = pallets × cartons_per_pallet")
    print("   • Tertiary: Z pcs = pallets × pcs_per_pallet")
    print()
    print("   Example: 3 pallets → 24 CTN → 1,440 pcs")
    print()
    print("=" * 80)
    print("✅ ANALYSIS COMPLETE")
    print("=" * 80)
    print()
    print("📝 NEXT STEPS:")
    print("   1. Update database schema (add pallet specifications to products)")
    print("   2. Import pallet specs from Packing.xlsx")
    print("   3. Update PO Kain creation UI (add pallet calculator)")
    print("   4. Update Packing module (validate exact quantities)")
    print("   5. Update FG receiving (pallet → carton → pcs conversion)")
    print("   6. Update documentation (prompt.md, Rencana Tampilan.md)")
    print()

if __name__ == "__main__":
    analyze_packing_specifications()
