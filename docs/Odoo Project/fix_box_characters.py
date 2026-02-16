"""
Fix box drawing characters to simple ASCII for better DOCX compatibility
"""

def fix_box_characters(filename):
    """Replace Unicode box drawing with simple ASCII"""
    
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Box drawing characters
    replacements = {
        '┌': '+',
        '└': '+',
        '┐': '+',
        '┘': '+',
        '─': '-',
        '│': '|',
        '├': '+',
        '┤': '+',
        '┬': '+',
        '┴': '+',
        '┼': '+',
        '▼': 'v',
        '↓': '|',
        '→': '->',
        '←': '<-',
        # Progress bars
        '█': '#',
        '▒': ':',
        '░': '.',
        # Checkmarks and symbols
        '✅': '[OK]',
        '❌': '[X]',
        '⚠️': '[!]',
        '🔄': '[>>]',
        '⏸️': '[..]',
        '📊': '[Chart]',
        '🔍': '[Find]',
        '📦': '[Box]',
        'ℹ️': '[i]',
        '✔': '[v]',
        '✓': '[v]',
    }
    
    for old, new in replacements.items():
        content = content.replace(old, new)
    
    # Save back
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✓ Fixed box drawing characters in {filename}")
    print(f"  Replaced {len(replacements)} character types")

if __name__ == '__main__':
    fix_box_characters('PRESENTASI_ODOO_SALES.md')
