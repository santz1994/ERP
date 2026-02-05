#!/usr/bin/env python3
"""
Remove ALL emoticons from TypeScript/TSX files
Replace with professional text equivalents
"""
import re
import os
from pathlib import Path

# Emoticon to professional text mapping
EMOJI_REPLACEMENTS = {
    # Navigation & Actions
    '📥': '[Import]',
    '📤': '[Export]',
    '📦': '[Package]',
    '🚢': '[Ship]',
    '📷': '[Scan]',
    '🔄': '[Refresh]',
    '🔍': '[Search]',
    '➕': '[Add]',
    '📋': '[List]',
    
    # Status indicators
    '✅': '[OK]',
    '❌': '[Error]',
    '⚠️': '[Warning]',
    '🟢': '●',  # Green dot
    '🔵': '●',  # Blue dot
    '🟡': '●',  # Yellow dot
    '🔴': '●',  # Red dot
    '⚫': '●',  # Black dot
    
    # Process & Flow
    '🚀': '[Launch]',
    '🔒': '[Hold]',
    '🚦': '[Status]',
    '🔑': '[Key]',
    '🧵': '[Thread]',
    '🏷️': '[Label]',
    
    # Celebration & Success
    '🎉': '[Success]',
    
    # Tools & Actions
    '🔧': '[Fix]',
    '📱': '[Mobile]',
    '💡': '[Tip]',
    '💰': '[Cost]',
    
    # Reports & Analytics
    '📈': '[Trend]',
    '📊': '[Report]',
    '📅': '[Calendar]',
    
    # Alerts
    '🚨': '[Alert]',
    '🚫': '[Stop]',
    '📍': '[Location]',
    
    # Others
    '📄': '[File]',
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
            print(f"✓ Cleaned: {filepath.relative_to(PROJECT_ROOT)}")
            return True
        return False
    
    except Exception as e:
        print(f"✗ Error processing {filepath}: {e}")
        return False

def main():
    global PROJECT_ROOT
    PROJECT_ROOT = Path(__file__).parent
    frontend_src = PROJECT_ROOT / 'erp-ui' / 'frontend' / 'src'
    
    if not frontend_src.exists():
        print(f"Error: {frontend_src} not found")
        return
    
    print("=" * 60)
    print("EMOTICON REMOVAL TOOL")
    print("=" * 60)
    print(f"Target directory: {frontend_src}")
    print()
    
    # Find all TSX and TS files
    tsx_files = list(frontend_src.glob('**/*.tsx'))
    ts_files = list(frontend_src.glob('**/*.ts'))
    all_files = tsx_files + ts_files
    
    print(f"Found {len(all_files)} TypeScript files")
    print()
    
    cleaned_count = 0
    for filepath in all_files:
        if remove_emoticons_from_file(filepath):
            cleaned_count += 1
    
    print()
    print("=" * 60)
    print(f"SUMMARY: Cleaned {cleaned_count} / {len(all_files)} files")
    print("=" * 60)

if __name__ == '__main__':
    main()
