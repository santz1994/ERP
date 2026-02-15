"""
Remove time estimates from markdown files
Replace with general descriptions in Bahasa Indonesia
"""
import re
import os

# File paths
files_to_process = [
    "1_CURRENT_MANUAL_WORKFLOW_PAIN_POINTS.md",
    "2_PLANNED_ODOO_WORKFLOW.md",
    "3_WORKFLOW_FULL_PURCHASING_TO_PRODUCTION.md",
    "4_WORKFLOW_PURCHASING_ONLY.md",
    "5_WORKFLOW_PRODUCTION_ONLY.md"
]

# Replacement patterns (order matters!)
replacements = [
    # Specific long phrases first
    (r'Admin time wasted 2-3 jam/hari', 'Waktu admin terbuang untuk tugas manual'),
    (r'Admin time: -60% \(2-3 jam → 1 jam data entry\)', 'Efisiensi waktu admin: pengurangan signifikan'),
    (r'Admin overwhelmed', 'Beban kerja admin berlebihan'),
    (r'data delay 1-2 jam!', 'data tidak real-time!'),
    (r'delay 1-2 jam dari actual WH', 'data tidak update real-time dari warehouse'),
    (r'Delay jawaban 1-2 jam', 'Delay jawaban signifikan'),
    (r'tidak delay 1-2 jam!', 'real-time!'),
    (r'Reconcile: Warehouse stock vs Production usage \(2-4 jam!\)', 'Reconcile: Warehouse vs Production usage (proses manual lama!)'),
    (r'tidak perlu meeting 2-4 jam!', 'tidak perlu meeting panjang!'),
    (r'tidak meeting 2-4 jam!', 'tidak perlu meeting panjang!'),
    (r'Meeting 2-4 jam', 'Meeting panjang untuk reconcile'),
    (r'no meeting 2-4 jam lagi!', 'tidak perlu meeting panjang lagi!'),
    (r'tidak perlu meeting 2-4 jam', 'tidak perlu meeting panjang'),
    (r'30 MIN per order', 'Proses manual yang lama per order'),
    (r'30 MENIT manual', 'Proses manual yang lama'),
    (r'HARUS calculate dari PALLET basis!', 'Harus calculate dari basis pallet!'),
    (r'scroll cari data \(10 menit\)', 'scroll cari data (proses manual)'),
    
    # General time patterns
    (r'\d+-\d+\s*jam', 'waktu yang lama'),
    (r'\d+\s*jam', 'waktu tunggu'),
    (r'\d+-\d+\s*JAM', 'waktu yang lama'),
    (r'\d+\s*JAM', 'waktu tunggu'),
    (r'\d+\s*menit', 'beberapa saat'),
    (r'\d+\s*MENIT', 'beberapa saat'),
    (r'\d+\s*MIN', 'waktu'),
    
    # Context-specific replacements
    (r'Tidak ada MO \(Manufacturing Order\)', 'Tidak ada MO (Manufacturing Order)'),
    (r'telegram berlebihan', 'beban berlebihan'),
]

def remove_time_estimates(content):
    """Remove time estimates from content"""
    original = content
    
    for pattern, replacement in replacements:
        content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)
    
    if content != original:
        print(f"  ✓ Replaced time estimates")
    
    return content

def process_file(filepath):
    """Process a single markdown file"""
    print(f"\nProcessing: {filepath}")
    
    if not os.path.exists(filepath):
        print(f"  ✗ File not found!")
        return False
    
    # Read file
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remove time estimates
    new_content = remove_time_estimates(content)
    
    # Write back if changed
    if new_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"  ✓ File updated successfully")
        return True
    else:
        print(f"  • No changes needed")
        return False

def main():
    """Main function"""
    print("=" * 60)
    print("REMOVING TIME ESTIMATES FROM MARKDOWN FILES")
    print("=" * 60)
    
    updated_count = 0
    
    for filename in files_to_process:
        if process_file(filename):
            updated_count += 1
    
    print("\n" + "=" * 60)
    print(f"✓ Complete! Updated {updated_count} file(s)")
    print("=" * 60)

if __name__ == '__main__':
    main()
