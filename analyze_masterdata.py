"""
Analyze Masterdata structure for Dual-BOM implementation
"""
import pandas as pd
from pathlib import Path

def analyze_articles():
    print("="*80)
    print("ARTICLE MASTERDATA ANALYSIS")
    print("="*80)
    df = pd.read_excel('docs/Masterdata/Article/Article.xlsx')
    print(f"\nTotal Articles: {len(df)}")
    print(f"\nColumns: {list(df.columns)}")
    print(f"\nDestination breakdown:")
    print(df['Destination '].value_counts())
    print(f"\nSample articles:")
    print(df.head(10).to_string(index=False))

def analyze_materials():
    print("\n" + "="*80)
    print("MATERIAL MASTERDATA ANALYSIS")
    print("="*80)
    df = pd.read_excel('docs/Masterdata/Material/DATABASE MATERIAL ALL.xlsx')
    print(f"\nTotal Materials: {len(df)}")
    print(f"\nColumns: {list(df.columns)}")
    print(f"\nCategory breakdown:")
    print(df['CATEGORY'].value_counts())
    print(f"\nSample materials by category:")
    for cat in df['CATEGORY'].unique()[:8]:
        print(f"\n--- {cat} ---")
        sample = df[df['CATEGORY']==cat].head(3)
        print(sample[['KODE BARANG', 'NAMA BARANG', 'UoM']].to_string(index=False))

def analyze_bom_production():
    print("\n" + "="*80)
    print("BOM PRODUCTION ANALYSIS (by Department)")
    print("="*80)
    
    departments = ['Cutting', 'Embo', 'Sewing', 'Finishing', 'Finishing Goods', 'Packing']
    
    for dept in departments:
        file_path = f'docs/Masterdata/BOM Production/{dept}.xlsx'
        if Path(file_path).exists():
            df = pd.read_excel(file_path)
            print(f"\n--- {dept.upper()} ---")
            print(f"Total BOM Lines: {len(df)}")
            print(f"Columns: {list(df.columns)}")
            print(f"\nSample BOM lines:")
            print(df.head(5).to_string(index=False))
        else:
            print(f"\n--- {dept.upper()} --- FILE NOT FOUND")

if __name__ == "__main__":
    analyze_articles()
    analyze_materials()
    analyze_bom_production()
    
    print("\n" + "="*80)
    print("ANALYSIS COMPLETE")
    print("="*80)
    print("\nCONCLUSION:")
    print("- BOM Production: Process-oriented (by department/step)")
    print("- BOM Purchasing: Should aggregate RAW materials only")
    print("- Need to implement dual-BOM database structure")
