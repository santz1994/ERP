"""
Re-extract sections from clean source and create separate files
"""

# Read clean source
with open('PRESENTASI_ODOO_SALES_CLEAN.md', 'r', encoding='utf-8') as f:
    content = f.read()

lines = content.split('\n')

print("Extracting sections from clean source...\n")

# File 1: Pain Points + Current Manual Workflow (lines 135-700)
file1_lines = lines[134:700]  # 0-indexed
with open('1_CURRENT_MANUAL_WORKFLOW_PAIN_POINTS.md', 'w', encoding='utf-8') as f:
    f.write('\n'.join(file1_lines))
print("✓ Created: 1_CURRENT_MANUAL_WORKFLOW_PAIN_POINTS.md")

# File 2: Planned Odoo Workflow (lines 230-445 + 706-900)
file2_part1 = lines[229:445]
file2_part2 = lines[705:900]
with open('2_PLANNED_ODOO_WORKFLOW.md', 'w', encoding='utf-8') as f:
    f.write('\n'.join(file2_part1 + ['\n---\n'] + file2_part2))
print("✓ Created: 2_PLANNED_ODOO_WORKFLOW.md")

# File 3: Full Workflow (extract relevant workflow sections)
file3_lines = lines[134:300] + ['\n---\n'] + lines[445:900]
with open('3_WORKFLOW_FULL_PURCHASING_TO_PRODUCTION.md', 'w', encoding='utf-8') as f:
    f.write('\n'.join(file3_lines))
print("✓ Created: 3_WORKFLOW_FULL_PURCHASING_TO_PRODUCTION.md")

# File 4: Purchasing only (lines 230-445)
file4_lines = ['# WORKFLOW: PURCHASING DEPARTMENT\n'] + lines[229:445]
with open('4_WORKFLOW_PURCHASING_ONLY.md', 'w', encoding='utf-8') as f:
    f.write('\n'.join(file4_lines))
print("✓ Created: 4_WORKFLOW_PURCHASING_ONLY.md")

# File 5: Production only (lines 706-900)
file5_lines = ['# WORKFLOW: PRODUCTION 5 DEPARTMENTS\n'] + lines[705:900]
with open('5_WORKFLOW_PRODUCTION_ONLY.md', 'w', encoding='utf-8') as f:
    f.write('\n'.join(file5_lines))
print("✓ Created: 5_WORKFLOW_PRODUCTION_ONLY.md")

print("\n✓ All files extracted successfully from clean source")
