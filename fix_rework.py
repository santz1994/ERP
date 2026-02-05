"""Fix rework_service.py - remove audit calls and fix types"""

with open('erp-softtoys/app/modules/manufacturing/rework_service.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
skip_until_blank = False
paren_depth = 0

for i, line in enumerate(lines):
    # Check if this is the start of a log_audit call
    if 'if user_id:' in line and i + 1 < len(lines) and 'log_audit' in lines[i+1]:
        skip_until_blank = True
        paren_depth = 0
        continue
    
    if skip_until_blank:
        # Count parentheses to know when log_audit call ends
        paren_depth += line.count('(') - line.count(')')
        if paren_depth <= 0 and ')' in line:
            skip_until_blank = False
        continue
    
    # Fix imports
    if 'from app.shared.audit import log_audit' in line:
        continue
    
    # Add Optional import
    if 'from datetime import datetime' in line:
        new_lines.append('from datetime import datetime\n')
        new_lines.append('from typing import Optional\n')
        continue
    
    # Fix type hints
    line = line.replace(': str = None', ': Optional[str] = None')
    line = line.replace(': int = None', ': Optional[int] = None')
    line = line.replace(': list[dict] = None', ': Optional[list[dict]] = None')
    
    # Fix long lines
    if 'category = self.db.query(DefectCategory).filter_by(id=defect_category_id).first()' in line:
        indent = len(line) - len(line.lstrip())
        new_lines.append(' ' * indent + 'category = (\n')
        new_lines.append(' ' * (indent + 4) + 'self.db.query(DefectCategory)\n')
        new_lines.append(' ' * (indent + 4) + '.filter_by(id=defect_category_id)\n')
        new_lines.append(' ' * (indent + 4) + '.first()\n')
        new_lines.append(' ' * indent + ')\n')
        continue
    
    new_lines.append(line)

with open('erp-softtoys/app/modules/manufacturing/rework_service.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("✅ Fixed rework_service.py")
