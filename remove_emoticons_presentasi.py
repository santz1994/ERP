#!/usr/bin/env python3
"""
Remove ALL emoticons from Markdown files in presentasi Odoo folder
"""
import re
import os
from pathlib import Path

# Emoticon to professional text mapping
EMOJI_REPLACEMENTS = {
    # Common check marks and status indicators
    '✅': '[OK]',
    '✓': '[OK]',
    '❌': '[X]',
    '✕': '[X]',
    '⚠️': '[WARNING]',
    '⚠': '[WARNING]',
    
    # Arrows
    '→': '->',
    '←': '<-',
    '↓': '|',
    '↑': '|',
    '⬆️': '^',
    '⬇️': 'v',
    '➡️': '->',
    '⬅️': '<-',
    '↗️': '/',
    '↘️': '\\',
    '↖️': '\\',
    '↙️': '/',
    
    # Process & Flow
    '🔄': '[Refresh]',
    '🔀': '[Switch]',
    '🔁': '[Repeat]',
    '🔂': '[Loop]',
    
    # Media controls
    '▶️': '[Play]',
    '⏸️': '[Pause]',
    '⏹️': '[Stop]',
    '⏺️': '[Record]',
    '⏭️': '[Next]',
    '⏮️': '[Previous]',
    '⏯️': '[Play/Pause]',
    '⏏️': '[Eject]',
    '🔼': '[Up]',
    '🔽': '[Down]',
    '◀️': '[Left]',
    
    # Dots and bullets
    '🟢': '●',
    '🔵': '●',
    '🟡': '●',
    '🔴': '●',
    '⚫': '●',
    '⬜': '□',
    '⬛': '■',
    '🟩': '■',
    '🟥': '■',
    '🟦': '■',
    '🟨': '■',
    
    # Others
    '🙏': '', # Remove thanking hands
    '⭐': '*',
    '🔥': '[Hot]',
    '💡': '[Tip]',
    '📊': '[Chart]',
    '📈': '[Up]',
    '📉': '[Down]',
    '🎯': '[Target]',
    '🚀': '[Launch]',
    '⚡': '[Fast]',
}

def remove_emoticons_from_file(filepath: Path):
    """Remove emoticons from a single file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        modified = False
        
        # Replace each emoticon with professional text
        for emoji, replacement in EMOJI_REPLACEMENTS.items():
            if emoji in content:
                content = content.replace(emoji, replacement)
                modified = True
                print(f"  Replaced '{emoji}' with '{replacement}'")
        
        # Remove any remaining emoticons (Unicode ranges)
        # This is a comprehensive Unicode emoticon range
        emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"  # emoticons
            "\U0001F300-\U0001F5FF"  # symbols & pictographs
            "\U0001F680-\U0001F6FF"  # transport & map symbols
            "\U0001F1E0-\U0001F1FF"  # flags
            "\U00002702-\U000027B0"
            "\U000024C2-\U0001F251"
            "\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
            "\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
            "]+",
            flags=re.UNICODE
        )
        
        remaining_emojis = emoji_pattern.findall(content)
        if remaining_emojis:
            content = emoji_pattern.sub('', content)
            modified = True
            print(f"  Removed remaining emojis: {remaining_emojis}")
        
        if modified:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"[OK] Cleaned: {filepath.name}")
            return True
        else:
            print(f"[SKIP] No emoticons found: {filepath.name}")
        return False
    
    except Exception as e:
        print(f"[ERROR] Error processing {filepath}: {e}")
        return False

def main():
    PROJECT_ROOT = Path(__file__).parent
    target_folder = PROJECT_ROOT / 'docs' / 'Odoo Project' / 'presentasi Odoo'
    
    if not target_folder.exists():
        print(f"Error: {target_folder} not found")
        return
    
    print("=" * 60)
    print("EMOTICON REMOVAL TOOL - Presentasi Odoo")
    print("=" * 60)
    print(f"Target directory: {target_folder}")
    print()
    
    # Find all MD files
    md_files = list(target_folder.glob('*.md'))
    
    print(f"Found {len(md_files)} Markdown files")
    print()
    
    cleaned_count = 0
    for filepath in sorted(md_files):
        print(f"\nProcessing: {filepath.name}")
        if remove_emoticons_from_file(filepath):
            cleaned_count += 1
    
    print()
    print("=" * 60)
    print(f"SUMMARY: Cleaned {cleaned_count} / {len(md_files)} files")
    print("=" * 60)

if __name__ == '__main__':
    main()
