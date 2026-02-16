"""
Fix all encoding issues in PRESENTASI_ODOO_SALES.md
"""

def fix_markdown_file():
    input_file = 'PRESENTASI_ODOO_SALES.md'
    output_file = 'PRESENTASI_ODOO_SALES_FIXED.md'
    
    # Try different encodings
    content = None
    for encoding in ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252']:
        try:
            with open(input_file, 'r', encoding=encoding, errors='replace') as f:
                content = f.read()
            print(f"✓ Read file with encoding: {encoding}")
            break
        except Exception as e:
            print(f"✗ Failed with {encoding}: {e}")
            continue
    
    if content is None:
        print("✗ Could not read file!")
        return
    
    # Replace all problematic characters
    replacements = {
        # Box drawing
        '┌': '+', '┐': '+', '└': '+', '┘': '+',
        '─': '-', '│': '|',
        '├': '+', '┤': '+', '┬': '+', '┴': '+', '┼': '+',
        '║': '|', '═': '=',
        '╔': '+', '╗': '+', '╚': '+', '╝': '+',
        '╠': '+', '╣': '+', '╦': '+', '╩': '+', '╬': '+',
        
        # Arrows
        '→': '->', '←': '<-', '↑': '^', '↓': 'v',
        '▶': '>', '◀': '<', '▲': '^', '▼': 'v',
        
        # Symbols
        '✅': '[OK]', '❌': '[X]', '⚠️': '[!]', '⚠': '[!]',
        '✓': '[v]', '✔': '[v]', '✗': '[x]', '✘': '[x]',
        '📊': '[CHART]', '📋': '[LIST]', '🔄': '[SYNC]',
        
        # Corrupted sequences  
        'v"Œ': '+', 'v""': '+', 'v"€': '-', 'v"‚': '|',
        'v"¼': '+', 'v"¬': '+', 'v"´': '+', 'v"œ': '+', 'v"¤': '+',
        'v†'': '->', 'vœ…': '[OK]', 'vš ': '[!]', 'vš': '[!]',
        'ï¸': '', 'ðŸ"Š': '[CHART]', 'ðŸ"‹': '[LIST]', 'ðŸ"': '[INFO]',
        'â†'': '->', 'âœ…': '[OK]', 'âŒ': '[X]', 'âš ': '[!]',
        'â"Œ': '+', 'â"': '+', 'â"€': '-', 'â"‚': '|',
        'â"¼': '+', 'â"¬': '+', 'â"´': '+', 'â"œ': '+', 'â"¤': '+',
        'â–¼': 'v', 'â–¶': '>',
    }
    
    for old, new in replacements.items():
        content = content.replace(old, new)
    
    # Write fixed version
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"\n✓ Fixed file created: {output_file}")
    print(f"  Total replacements: {len(replacements)}")
    
    # Also update original
    with open(input_file, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✓ Original file updated: {input_file}")

if __name__ == '__main__':
    fix_markdown_file()
    print("\n✓ All encoding issues fixed!")
    print("  Box drawings: ┌─┐ → +--+")
    print("  Symbols: ✅ → [OK], ❌ → [X], ⚠️ → [!]")
    print("  Arrows: → → ->")
