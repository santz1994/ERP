"""
Careful emoji removal - preserve all formatting and spacing
"""
import os
import re

def remove_emoji_carefully(text):
    """Remove emojis but preserve all spacing and formatting"""
    
    # List of emojis to remove
    emojis = [
        '✅', '⚠️', '❌', '🔴', '🟡', '🟢', '📋', '📅', '🔄', '⏳',
        '🚀', '💡', '📂', '📄', '📌', '🎯', '✨', '🎨', '🔍', '💻',
        '🏭', '📊', '⚙️', '🛠️', '📈', '📉', '🎉', '👥', '🏢', '🔥',
        '💰', '🎁', '📱', '⭐', '🌟', '💪', '👍', '👎', '🙏', '🤝',
    ]
    
    # Remove each emoji individually - preserve adjacent spaces
    for emoji in emojis:
        # Remove emoji but keep the space structure
        text = text.replace(emoji + ' ', '')  # emoji followed by space
        text = text.replace(' ' + emoji, '')  # space followed by emoji
        text = text.replace(emoji, '')  # emoji alone
    
    # Remove unicode emojis using regex
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"
        "\U0001F300-\U0001F5FF"
        "\U0001F680-\U0001F6FF"
        "\U0001F1E0-\U0001F1FF"
        "\U00002600-\U000027BF"
        "\U0001F900-\U0001F9FF"
        "\U0001FA00-\U0001FA6F"
        "]+",
        flags=re.UNICODE
    )
    text = emoji_pattern.sub('', text)
    
    # Only clean up if there are 3+ consecutive spaces (not 2!)
    text = re.sub(r'   +', '  ', text)
    
    return text

# Read original source
print("Reading original source file...")
with open('../PRESENTASI_ODOO_SALES.md', 'r', encoding='utf-8') as f:
    source = f.read()

print(f"Original size: {len(source)} characters")

# Remove emojis carefully
cleaned = remove_emoji_carefully(source)

print(f"After cleaning: {len(cleaned)} characters")
print(f"Characters removed: {len(source) - len(cleaned)}")

# Save cleaned version
with open('PRESENTASI_ODOO_SALES_CLEAN.md', 'w', encoding='utf-8') as f:
    f.write(cleaned)

print("\nSaved: PRESENTASI_ODOO_SALES_CLEAN.md")
print("This file has emojis removed but formatting preserved")
