"""
Fix Unicode box drawing characters to simple ASCII
"""
import os

def fix_box_characters(input_file, output_file=None):
    """Replace Unicode box drawing with ASCII"""
    if output_file is None:
        output_file = input_file
    
    # Read with UTF-8 encoding
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace box drawing characters with ASCII
    replacements = {
        '┌': '+',
        '┐': '+',
        '└': '+',
        '┘': '+',
        '─': '-',
        '│': '|',
        '├': '+',
        '┤': '+',
        '┬': '+',
        '┴': '+',
        '┼': '+',
        '▼': 'v',
        '▶': '>',
        '◀': '<',
        '▲': '^',
        '║': '|',
        '═': '=',
        '╔': '+',
        '╗': '+',
        '╚': '+',
        '╝': '+',
        '╠': '+',
        '╣': '+',
        '╦': '+',
        '╩': '+',
        '╬': '+',
    }
    
    for unicode_char, ascii_char in replacements.items():
        content = content.replace(unicode_char, ascii_char)
    
    # Write back with UTF-8 encoding
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✓ Fixed box characters in: {os.path.basename(input_file)}")
    print(f"  Output: {os.path.basename(output_file)}")

if __name__ == '__main__':
    input_file = 'PRESENTASI_ODOO_SALES.md'
    
    if not os.path.exists(input_file):
        print(f"✗ File not found: {input_file}")
    else:
        fix_box_characters(input_file)
        print("\n✓ All box characters replaced with ASCII!")
        print("  ┌─┐ → +--+")
        print("  │ │ → |  |")
        print("  └─┘ → +--+")
