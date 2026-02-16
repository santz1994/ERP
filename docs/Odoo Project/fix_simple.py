"""
Fix all encoding issues in PRESENTASI_ODOO_SALES.md
Simple ASCII replacement only
"""

def fix_markdown_file():
    input_file = 'PRESENTASI_ODOO_SALES.md'
    
    # Read with error handling
    try:
        with open(input_file, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
        print(f"Read file: {input_file}")
    except Exception as e:
        print(f"Error reading: {e}")
        return
    
    # Count original problematic chars
    box_chars = ['┌', '┐', '└', '┘', '─', '│', '├', '┤', '┬', '┴', '┼']
    count = sum(content.count(c) for c in box_chars)
    print(f"Found {count} box drawing characters")
    
    # Simple ASCII replacements
    content = (content
        .replace('┌', '+').replace('┐', '+').replace('└', '+').replace('┘', '+')
        .replace('─', '-').replace('│', '|')
        .replace('├', '+').replace('┤', '+').replace('┬', '+').replace('┴', '+').replace('┼', '+')
        .replace('║', '|').replace('═', '=')
        .replace('╔', '+').replace('╗', '+').replace('╚', '+').replace('╝', '+')
        .replace('╠', '+').replace('╣', '+').replace('╦', '+').replace('╩', '+').replace('╬', '+')
        .replace('▶', '>').replace('◀', '<').replace('▲', '^').replace('▼', 'v')
    )
    
    # Write back
    try:
        with open(input_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Fixed and saved: {input_file}")
    except Exception as e:
        print(f"Error writing: {e}")
        return
    
    # Verify
    count_after = sum(content.count(c) for c in box_chars)
    print(f"Remaining box chars: {count_after}")
    print(f"Replaced: {count - count_after} characters")

if __name__ == '__main__':
    print("=" * 60)
    print("FIXING ENCODING ISSUES")
    print("=" * 60)
    fix_markdown_file()
    print("\nDone! All box drawings replaced with ASCII:")
    print("  +---+")
    print("  |   |")
    print("  +---+")
