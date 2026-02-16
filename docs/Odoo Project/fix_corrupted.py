"""
Fix corrupted box characters and symbols in markdown
"""

def fix_file():
    filename = 'PRESENTASI_ODOO_SALES.md'
    
    # Read file
    with open(filename, 'r', encoding='utf-8', errors='replace') as f:
        content = f.read()
    
    print(f"Original size: {len(content)} chars")
    
    # Fix corrupted sequences
    replacements = {
        # Box drawing corrupted chars
        'v"Œ': '+',   # Top left corner
        'v"': '+',   # Top right corner
        'v""': '+',   # Bottom left corner
        'v"˜': '+',   # Bottom right corner
        'v"€': '-',   # Horizontal line
        'v"‚': '|',   # Vertical line
        'v"œ': '+',   # Left T
        'v"¤': '+',   # Right T
        'v"¬': '+',   # Top T
        'v"´': '+',   # Bottom T
        'v"¼': '+',   # Cross
        
        # Double line boxes
        'v"•': '=',
        'v"" ': '+ ',
        'v"œ ': '+ ',
        'v"š': '+',
        'v"š ': '+ ',
        
        # Arrows
        'v†'': '->',
        'v†': '->',
        'v†œ': '<-',
        'vâ†'': '->',
        'vâ†': '<-',
        
        # Symbols
        'vœ…': '[OK]',
        'vâœ…': '[OK]',
        'vœ"': '[OK]',
        'vš': '[!]',
        'vâš ï¸': '[!]',
        'vš ï¸': '[!]',
        'vâš¡': '[!]',
        'vâ': '[X]',
        'vâŒ': '[X]',
        'ðŸ"Š': '[CHART]',
        'ðŸ"‹': '[LIST]',
        'ðŸ"': '[INFO]',
        'ðŸ"¦': '[BOX]',
        'ðŸš¨': '[ALERT]',
        'ðŸŽ¯': '[TARGET]',
        'â˜': '[!]',
        'âœ': '[OK]',
    }
    
    # Apply replacements
    for old, new in replacements.items():
        if old in content:
            count = content.count(old)
            content = content.replace(old, new)
            print(f"Replaced '{old}' -> '{new}' ({count} times)")
    
    # Write back
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"\nFixed size: {len(content)} chars")
    print(f"Saved to: {filename}")

if __name__ == '__main__':
    print("=" * 60)
    print("FIXING CORRUPTED CHARACTERS")
    print("=" * 60)
    fix_file()
    print("\n" + "=" * 60)
    print("DONE!")
    print("=" * 60)
