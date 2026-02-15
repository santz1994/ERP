"""Remove ALL emojis from markdown source files"""
import os
import re

# All emojis to remove
EMOJIS_TO_REMOVE = [
    '✅', '⚠️', '❌', '🔴', '🟡', '🟢', '📋', '📅', '🔄', '⏳',
    '🚀', '💡', '📂', '📄', '📌', '🎯', '✨', '🎨', '🔍', '💻',
    '🏭', '📊', '⚙️', '🛠️', '📈', '📉', '🎉', '👥', '🏢', '🔥',
    '💰', '🎁', '📱', '⭐', '🌟', '💪', '👍', '👎', '🙏', '🤝',
    '▼', '▲', '►', '◄', '→', '←', '↑', '↓', '⇒', '⇐', '✓'
]

def remove_all_emojis(text):
    """Remove all emojis from text"""
    # Remove specific emojis
    for emoji in EMOJIS_TO_REMOVE:
        text = text.replace(emoji, '')
    
    # Remove emoji unicode ranges
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map
        "\U0001F1E0-\U0001F1FF"  # flags
        "\U00002702-\U000027B0"
        "\U000024C2-\U0001F251"
        "\U0001F900-\U0001F9FF"
        "\U0001FA00-\U0001FA6F"
        "\U00002600-\U000026FF"  # misc symbols
        "]+",
        flags=re.UNICODE
    )
    text = emoji_pattern.sub('', text)
    
    # Clean up multiple spaces
    text = re.sub(r' +', ' ', text)
    # Clean up multiple empty lines
    text = re.sub(r'\n\n\n+', '\n\n', text)
    
    return text

def process_md_file(filename):
    """Remove emojis from markdown file"""
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_length = len(content)
    cleaned = remove_all_emojis(content)
    
    # Count emojis removed
    emojis_removed = sum(content.count(emoji) for emoji in EMOJIS_TO_REMOVE)
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(cleaned)
    
    return emojis_removed

# Process all markdown files
md_files = [f for f in os.listdir('.') if f.endswith('.md')]

print("Removing emojis from markdown source files...\n")

total_removed = 0
for md_file in md_files:
    removed = process_md_file(md_file)
    if removed > 0:
        print(f"  {md_file}: {removed} emojis removed")
        total_removed += removed
    else:
        print(f"  {md_file}: Already clean")

print(f"\nTotal emojis removed from source: {total_removed}")
print("\nNow re-converting to .docx...")
