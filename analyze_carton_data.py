"""
Analyze Carton.xlsx to extract pcs_per_carton specifications
"""

import pandas as pd
import re

def analyze_carton_data():
    """Extract carton specifications from Carton.xlsx"""
    
    file_path = 'docs/Masterdata/Karton/Carton.xlsx'
    
    print("=" * 80)
    print("📦 CARTON SPECIFICATIONS ANALYSIS")
    print("=" * 80)
    print()
    
    # Try reading with different configurations
    try:
        df = pd.read_excel(file_path, skiprows=1)
        print(f"✅ File loaded: {len(df)} rows")
        print(f"📋 Columns: {df.columns.tolist()}")
        print()
        
        # Display raw data
        print("=" * 80)
        print("RAW DATA STRUCTURE")
        print("=" * 80)
        for idx, row in df.head(20).iterrows():
            print(f"Row {idx}: {[str(x)[:50] if pd.notna(x) else 'NaN' for x in row.tolist()]}")
        print()
        
        # Try to extract article names and pcs per carton from REMARK column
        print("=" * 80)
        print("EXTRACTING PCS PER CARTON FROM REMARK")
        print("=" * 80)
        print()
        
        # Get REMARK column (usually last column or named 'REMARK')
        remark_col = None
        for col in df.columns:
            if 'REMARK' in str(col).upper():
                remark_col = col
                break
        
        if remark_col is None:
            # Try last column
            remark_col = df.columns[-1]
        
        print(f"Using column for remarks: {remark_col}")
        print()
        
        # Extract pcs per carton patterns
        carton_specs = []
        
        for idx, row in df.iterrows():
            article_name = None
            pcs_per_carton = None
            
            # Try to find article name (usually in column 1 or 2)
            if pd.notna(row.iloc[1]):
                article_name = str(row.iloc[1]).strip()
            
            # Extract pcs per carton from remark
            remark = str(row[remark_col])
            
            # Pattern: "1CT : 10PCS" or "1CT : 84PCS" etc
            match = re.search(r'1CT\s*:\s*(\d+)\s*PCS', remark, re.IGNORECASE)
            if match:
                pcs_per_carton = int(match.group(1))
                
                if article_name and article_name not in ['nan', 'TOTAL', '']:
                    carton_specs.append({
                        'article_name': article_name,
                        'pcs_per_carton': pcs_per_carton,
                        'remark': remark
                    })
        
        # Display extracted specs
        if carton_specs:
            print("✅ EXTRACTED CARTON SPECIFICATIONS:")
            print()
            print(f"{'Article Name':<60} | {'Pcs/Carton':<12} | {'Remark':<20}")
            print("-" * 100)
            
            for spec in carton_specs:
                print(f"{spec['article_name']:<60} | {spec['pcs_per_carton']:<12} | {spec['remark']:<20}")
        else:
            print("⚠️ No carton specifications found in expected format")
        
        print()
        print("=" * 80)
        print("💡 INSIGHTS")
        print("=" * 80)
        print()
        print("• Format: '1CT : XXX PCS' indicates pcs per carton")
        print("• Found in REMARK column")
        print("• Common values: 10, 12, 24, 36, 48, 60, 84 pcs per carton")
        print()
        
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    analyze_carton_data()
