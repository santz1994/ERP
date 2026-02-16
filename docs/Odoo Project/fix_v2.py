"""
Fix corrupted box characters - simple version
"""

def fix_file():
    filename = 'PRESENTASI_ODOO_SALES.md'
    
    # Read file
    with open(filename, 'r', encoding='utf-8', errors='replace') as f:
        content = f.read()
    
    print(f"Original size: {len(content)} chars")
    
    # Simple text replacements - only common corrupted patterns
    # Box corners and lines
    content = content.replace('v"Œ', '+')  # Top left
   content = content.replace('v"', '+')   # Top right  
    content = content.replace('v""', '+')  # Bottom left
    content = content.replace('v"˜', '+')  # Bottom right
    content = content.replace('v"€', '-')  # Horizontal
    content = content.replace('v"‚', '|')  # Vertical
    content = content.replace('v"œ', '+')  # Left T
    content = content.replace('v"¤', '+')  # Right T
    content = content.replace('v"¬', '+')  # Top T
    content = content.replace('v"´', '+')  # Bottom T
    content = content.replace('v"¼', '+')  # Cross
    
    # Double lines
    content = content.replace('v"•', '=')
    content = content.replace('v"š', '+')
    
    # Arrows - multi-char sequences
    content = content.replace('v†', '->')
    
    # Symbols - multi-char sequences
    content = content.replace('vœ…', '[OK]')
    content = content.replace('vœ"', '[OK]')
    content = content.replace('vš', '[!]')
    
    # Emoji sequences (common corrupted emojis)
    if 'ðŸ' in content:
        content = content.replace('ðŸ"Š', '[CHART]')
        content = content.replace('ðŸ"‹', '[LIST]')
        content = content.replace('ðŸ"', '[INFO]')
        content = content.replace('ðŸ"¦', '[BOX]')
        content = content.replace('ðŸš¨', '[ALERT]')
        content = content.replace('ðŸŽ¯', '[TARGET]')
    
    # Write back
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Fixed size: {len(content)} chars")
    print(f"Saved to: {filename}")

if __name__ == '__main__':
    print("=" * 60)
    print("FIXING CORRUPTED CHARACTERS")
    print("=" * 60)
    fix_file()
    print("\nDONE!")
