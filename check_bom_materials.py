"""Check all material codes from BOM files."""
import pandas as pd
from pathlib import Path
from collections import Counter

print("📊 EXTRACTING MATERIAL CODES FROM ALL BOM FILES")
print("=" * 80)

bom_path = Path("docs/Masterdata/BOM Production")
bom_files = [
    "Cutting.xlsx",
    "Embo.xlsx", 
    "Sewing.xlsx",
    "Finishing.xlsx",
    "Packing.xlsx",
    "Finishing Goods.xlsx"
]

all_components = []
all_codes = []

for filename in bom_files:
    file_path = bom_path / filename
    if file_path.exists():
        print(f"\n📋 {filename}:")
        df = pd.read_excel(file_path)
        
        # Get all components
        components = df['BoM Lines/Component'].dropna()
        print(f"   Total component entries: {len(components)}")
        
        # Extract codes
        for comp in components:
            comp_str = str(comp)
            if '[' in comp_str and ']' in comp_str:
                code = comp_str.split('[')[1].split(']')[0]
                all_codes.append(code)
                all_components.append(comp_str)
                
        # Show sample
        print(f"   Sample entries:")
        for comp in components.head(3):
            if '[' in str(comp) and ']' in str(comp):
                code = str(comp).split('[')[1].split(']')[0]
                print(f"      [{code}] {str(comp)[:80]}")

print("\n" + "=" * 80)
print("📊 SUMMARY")
print("=" * 80)
print(f"Total material entries across all BOMs: {len(all_codes)}")
print(f"Unique material codes: {len(set(all_codes))}")

# Show top 20 most used materials
print(f"\n🔝 Top 20 most frequently used materials:")
code_counts = Counter(all_codes)
for code, count in code_counts.most_common(20):
    # Find full name
    full_name = next((c for c in all_components if f'[{code}]' in c), code)
    print(f"   {count:3d}x [{code}] {full_name[:70]}")

# Show all unique codes
print(f"\n📋 All {len(set(all_codes))} unique material codes:")
for code in sorted(set(all_codes))[:50]:
    print(f"   {code}")
if len(set(all_codes)) > 50:
    print(f"   ... and {len(set(all_codes)) - 50} more")

# Save to file for reference
with open('bom_material_codes.txt', 'w', encoding='utf-8') as f:
    f.write("All unique material codes from BOM files:\n")
    f.write("=" * 80 + "\n\n")
    for code in sorted(set(all_codes)):
        # Find full name
        full_name = next((c for c in all_components if f'[{code}]' in c), code)
        f.write(f"[{code}] {full_name}\n")

print(f"\n💾 Full list saved to: bom_material_codes.txt")
