"""Extract real suppliers from material database and import BOMs."""
import sys
from pathlib import Path
import pandas as pd

# Add erp-softtoys to sys.path
sys.path.insert(0, str(Path(__file__).parent / "erp-softtoys"))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.models.products import Partner, PartnerType, Product, ProductType
from app.core.models.bom import BOMHeader, BOMDetail, BOMType

# Database connection
DATABASE_URL = "postgresql://postgres:SantZ1994--@localhost:5432/erp_quty_karunia"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def extract_suppliers():
    """Extract real suppliers from material database."""
    print("🔍 Extracting suppliers from material database...")
    
    df = pd.read_excel('docs/Masterdata/Material/DATABASE MATERIAL ALL.xlsx')
    suppliers = df['PROODUCER MATERIAL'].dropna().unique()
    
    print(f"\n📊 Found {len(suppliers)} unique suppliers:")
    for s in suppliers:
        print(f"   - {s}")
    
    return list(suppliers)

def import_suppliers(db, supplier_names):
    """Import suppliers to database."""
    print(f"\n💾 Importing {len(supplier_names)} suppliers...")
    
    existing = db.query(Partner).filter(Partner.type == PartnerType.SUPPLIER).count()
    print(f"   Existing suppliers in DB: {existing}")
    
    imported = 0
    skipped = 0
    
    for name in supplier_names:
        # Check if exists
        exists = db.query(Partner).filter(
            Partner.name == name,
            Partner.type == PartnerType.SUPPLIER
        ).first()
        
        if exists:
            skipped += 1
            continue
        
        # Create supplier
        supplier = Partner(
            name=name,
            type=PartnerType.SUPPLIER,
            address=None,
            contact_person=None,
            phone=None,
            email=None
        )
        db.add(supplier)
        imported += 1
    
    db.commit()
    print(f"✅ Imported: {imported}, Skipped: {skipped} (already exists)")

def import_bom_from_file(db, file_path, bom_type):
    """Import BOM from an Excel file."""
    print (f"\n📋 Processing: {file_path.name} (Type: {bom_type.value})")
    
    df = pd.read_excel(file_path)
    
    # Process each product and its components
    current_product_code = None
    current_article = None
    bom_header = None
    components_added = 0
    
    for idx, row in df.iterrows():
        product_full = row['Product']
        
        # New product detected
        if pd.notna(product_full) and product_full:
            # Save prev BOM if exists
            if bom_header and components_added > 0:
                db.commit()
                print(f"   ✅ {current_product_code}: {components_added} components")
            
            # Extract article code (first part before underscore)
            product_parts = product_full.split('_')
            if product_parts:
                product_name = product_parts[0].strip()
                
                # Find article in database
                current_article = db.query(Product).filter(
                    Product.name.ilike(f"%{product_name}%"),
                    Product.type == ProductType.FINISH_GOOD
                ).first()
                
                if not current_article:
                    # Try finding by partial match
                    current_article = db.query(Product).filter(
                        Product.type == ProductType.FINISH_GOOD
                    ).first()
                
                if current_article:
                    current_product_code = current_article.code
                    
                    # Check if BOM already exists
                    existing_bom = db.query(BOMHeader).filter(
                        BOMHeader.product_id == current_article.id,
                        BOMHeader.bom_type == bom_type
                    ).first()
                    
                    if existing_bom:
                        bom_header = existing_bom
                        components_added = 0
                    else:
                        # Create new BOM header
                        bom_header = BOMHeader(
                            product_id=current_article.id,
                            bom_type=bom_type,
                            quantity=1,
                            is_active=True
                        )
                        db.add(bom_header)
                        db.flush()
                        components_added = 0
                else:
                    bom_header = None
                    current_product_code = None
        
        # Component line
        component_code = row.get('BoM Lines/Component')
        component_qty = row.get('BoM Lines/Quantity')
        
        if pd.notna(component_code) and pd.notna(component_qty) and bom_header:
            # Extract code from [CODE] format
            if '[' in component_code and ']' in component_code:
                code = component_code.split('[')[1].split(']')[0]
            else:
                code = component_code
            
            # Find material in database
            material = db.query(Product).filter(
                Product.code == code,
                Product.type == ProductType.RAW
            ).first()
            
            if material:
                # Check if component already exists
                existing = db.query(BOMDetail).filter(
                    BOMDetail.bom_header_id == bom_header.id,
                    BOMDetail.material_id == material.id
                ).first()
                
                if not existing:
                    detail = BOMDetail(
                        bom_header_id=bom_header.id,
                        material_id=material.id,
                        quantity=float(component_qty),
                        wastage_percentage=5.0  # Default 5%
                    )
                    db.add(detail)
                    components_added += 1
    
    # Save last BOM
    if bom_header and components_added > 0:
        db.commit()
        print(f"   ✅ {current_product_code}: {components_added} components")

def import_all_boms(db):
    """Import all BOM files."""
    print("\n" + "=" * 80)
    print("📦 IMPORTING REAL BOM DATA")
    print("=" * 80)
    
    bom_path = Path("docs/Masterdata/BOM Production")
    bom_files = {
        "Cutting.xlsx": BOMType.CUTTING,
        "Embo.xlsx": BOMType.EMBROIDERY,
        "Sewing.xlsx": BOMType.SEWING,
        "Finishing.xlsx": BOMType.FINISHING,
        "Packing.xlsx": BOMType.PACKING,
        "Finishing Goods.xlsx": BOMType.ASSEMBLY
    }
    
    total_boms = 0
    for filename, bom_type in bom_files.items():
        file_path = bom_path / filename
        if file_path.exists():
            try:
                import_bom_from_file(db, file_path, bom_type)
                total_boms += 1
            except Exception as e:
                print(f"   ❌ Error: {e}")
    
    print(f"\n✅ Processed {total_boms}/{len(bom_files)} BOM files")

def main():
    print("\n" + "=" * 80)
    print("🚀 REAL DATA IMPORT - SUPPLIERS & BOMS")
    print("=" * 80)
    print("This script will:")
    print("1. Extract real suppliers from material database")
    print("2. Import suppliers to Partners table")
    print("3. Import real BOM data from all Excel files")
    print("=" * 80)
    
    response = input("\n❓ Continue? (yes/no): ")
    if response.lower() != 'yes':
        print("❌ Cancelled.")
        return
    
    db = SessionLocal()
    try:
        # Step 1: Extract and import suppliers
        supplier_names = extract_suppliers()
        import_suppliers(db, supplier_names)
        
        # Step 2: Import BOMs
        import_all_boms(db)
        
        # Summary
        supplier_count = db.query(Partner).filter(Partner.type == PartnerType.SUPPLIER).count()
        bom_count = db.query(BOMHeader).count()
        
        print("\n" + "=" * 80)
        print("✅ IMPORT COMPLETE!")
        print("=" * 80)
        print(f"   Suppliers: {supplier_count}")
        print(f"   BOMs: {bom_count}")
        print("=" * 80)
    
    except Exception as e:
        db.rollback()
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    main()
