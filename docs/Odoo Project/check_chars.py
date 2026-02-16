"""
Check what box characters actually exist in the file
"""

with open('PRESENTASI_ODOO_SALES.md', 'r', encoding='utf-8') as f:
    content = f.read()

# Find all unique box-like characters
box_chars = set()
for char in content:
    if ord(char) > 127:  # Non-ASCII
        # Check if it's a box drawing or special character
        code = ord(char)
        if (0x2500 <= code <= 0x257F) or \
           (0x2580 <= code <= 0x259F) or \
           (0x25A0 <= code <= 0x25FF) or \
           (0x2190 <= code <= 0x21FF) or \
           (0x2600 <= code <= 0x26FF) or \
           (0x1F300 <= code <= 0x1F9FF):
            box_chars.add((char, hex(code), code))

print(f"Found {len(box_chars)} unique special characters:")
for char, hex_code, dec_code in sorted(box_chars, key=lambda x: x[2]):
    print(f"  '{char}' = {hex_code} = {dec_code}")
    
# Count occurrences
print("\nTop 10 most common:")
from collections import Counter
counts = Counter([c for c in content if ord(c) > 127 and 
                  ((0x2500 <= ord(c) <= 0x257F) or 
                   (0x2190 <= ord(c) <= 0x21FF) or
                   (0x2600 <= ord(c) <= 0x26FF) or
                   (0x1F300 <= ord(c) <= 0x1F9FF))])
for char, count in counts.most_common(10):
    print(f"  '{char}' (U+{ord(char):04X}): {count} times")
