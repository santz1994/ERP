"""Check if emojis exist in docx files"""
from docx import Document
import re
import os

def check_emojis_in_docx(filename):
    """Check for emojis in a docx file"""
    doc = Document(filename)
    all_text = '\n'.join([p.text for p in doc.paragraphs])
    
    # Common emojis to check
    common_emojis = ['✅', '⚠️', '❌', '🔴', '🟡', '🟢', '📋', '📅', '🔄', '⏳']
    found_emojis = []
    
    for emoji in common_emojis:
        if emoji in all_text:
            count = all_text.count(emoji)
            found_emojis.append(f"{emoji} ({count}x)")
    
    return found_emojis

# Check all docx files
docx_files = [f for f in os.listdir('.') if f.endswith('.docx')]

print("Checking for emojis in .docx files...\n")

total_emojis = 0
for docx_file in docx_files:
    emojis = check_emojis_in_docx(docx_file)
    if emojis:
        print(f"❌ {docx_file}:")
        for e in emojis:
            print(f"   {e}")
        total_emojis += len(emojis)
    else:
        print(f"✓ {docx_file}: No emojis found")

print(f"\nTotal emoji types found: {total_emojis}")
if total_emojis == 0:
    print("✓ All files are emoji-free!")
