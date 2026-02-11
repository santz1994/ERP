"""Extract real suppliers and import BOMs - Direct DB version."""
import pandas as pd
from pathlib import Path
from sqlalchemy import create_engine, Column, String, Integer, ForeignKey, Float, Boolean, Enum as SQLEnum, TEXT, Date, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.sql import func
import enum

# Database connection
DATABASE_URL = "postgresql://postgres:password123@localhost:5432/erp_quty_karunia"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# Enums
class PartnerType(str, enum.Enum):
    CUSTOMER = "Customer"
    SUPPLIER = "Supplier"
    SUBCON = "Subcon"

class ProductType(str, enum.Enum):
    RAW_MATERIAL = "Raw Material"
    WIP = "WIP"
    FINISH_GOOD = "Finish Good"
    SERVICE = "Service"

class BOMType(str, enum.Enum):
    MANUFACTURING = "Manufacturing"
    KIT_PHANTOM = "Kit/Phantom"

# Models (simplified)
class Partner(Base):
    __tablename__ = "partners"
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    type = Column(SQLEnum(PartnerType), nullable=False)
    address = Column(TEXT)
    contact_person = Column(String(100))
    phone = Column(String(20))
    email = Column(String(100))

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True)
    code = Column(String(100))
    name = Column(String(255))
    type = Column(SQLEnum(ProductType))

class BOMHeader(Base):
    __tablename__ = "bom_headers"
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    bom_type = Column(SQLEnum(BOMType))
    qty_output = Column(Float, default=1.0)
    is_active = Column(Boolean)

class BOMDetail(Base):
    __tablename__ = "bom_details"
    id = Column(Integer, primary_key=True)
    bom_header_id = Column(Integer, ForeignKey("bom_headers.id"))
    component_id = Column(Integer, ForeignKey("products.id"))
    qty_needed = Column(Float)
    wastage_percent = Column(Float)

# Functions
def extract_suppliers():
    """Extract real suppliers from material database."""
    print("🔍 Extracting suppliers from material database...")
    
    df = pd.read_excel('docs/Masterdata/Material/DATABASE MATERIAL ALL.xlsx')
    suppliers = df['PROODUCER MATERIAL'].dropna().unique()
    
    print(f"\n📊 Found {len(suppliers)} unique suppliers:")
    for s in suppliers[:10]:
        print(f"   - {s}")
    if len(suppliers) > 10:
        print(f"   ... and {len(suppliers) - 10} more")
    
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
    
    # Show final count
    total = db.query(Partner).filter(Partner.type == PartnerType.SUPPLIER).count()
    print(f"📊 Total suppliers in database: {total}")

def import_bom_from_file(db, file_path, bom_type):
    """Import BOM from an Excel file."""
    print(f"\n📋 Processing: {file_path.name} (Type: {bom_type.value})")
    
    df = pd.read_excel(file_path)
    
    # Process each product and its components
    current_product_code = None
    current_article = None
    bom_header = None
    components_added = 0
    boms_created = 0
    
    for idx, row in df.iterrows():
        product_full = row.get('Product')
        
        # New product detected
        if pd.notna(product_full) and product_full:
            # Save previous BOM if exists
            if bom_header and components_added > 0:
                db.commit()
                print(f"   ✅ {current_product_code}: {components_added} components")
                boms_created += 1
            
            # Extract article name (first part before underscore)
            product_parts = str(product_full).split('_')
            if product_parts:
                product_name = product_parts[0].strip()
                
                # Find article in database by name match
                current_article = db.query(Product).filter(
                    Product.name.ilike(f"%{product_name}%"),
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
                            qty_output=1.0,
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
            code_str = str(component_code)
            if '[' in code_str and ']' in code_str:
                code = code_str.split('[')[1].split(']')[0]
            else:
                code = code_str
            
            # Find material in database by code
            material = db.query(Product).filter(
                Product.code == code,
                Product.type == ProductType.RAW_MATERIAL
            ).first()
            
            if material:
                # Check if component already exists
                existing = db.query(BOMDetail).filter(
                    BOMDetail.bom_header_id == bom_header.id,
                    BOMDetail.component_id == material.id
                ).first()
                
                if not existing:
                    detail = BOMDetail(
                        bom_header_id=bom_header.id,
                        component_id=material.id,
                        qty_needed=float(component_qty),
                        wastage_percent=5.0  # Default 5%
                    )
                    db.add(detail)
                    components_added += 1
    
    # Save last BOM
    if bom_header and components_added > 0:
        db.commit()
        print(f"   ✅ {current_product_code}: {components_added} components")
        boms_created += 1
    
    print(f"   📊 Created {boms_created} BOMs from {file_path.name}")
    return boms_created

def import_all_boms(db):
    """Import all BOM files."""
    print("\n" + "=" * 80)
    print("📦 IMPORTING REAL BOM DATA")
    print("=" * 80)
    
    bom_path = Path("docs/Masterdata/BOM Production")
    bom_files = [
        "Cutting.xlsx",
        "Embo.xlsx",
        "Sewing.xlsx",
        "Finishing.xlsx",
        "Packing.xlsx",
        "Finishing Goods.xlsx"
    ]
    
    # All BOM files imported as Manufacturing type
    # (Database BOMType enum only has Manufacturing and Kit/Phantom)
    bom_type = BOMType.MANUFACTURING
    
    total_boms = 0
    for filename in bom_files:
        file_path = bom_path / filename
        if file_path.exists():
            try:
                count = import_bom_from_file(db, file_path, bom_type)
                total_boms += count
            except Exception as e:
                print(f"   ❌ Error: {e}")
                import traceback
                traceback.print_exc()
                db.rollback()  # Rollback after error to continue
    
    print(f"\n✅ Total BOMs created: {total_boms}")
    return total_boms

def main():
    print("\n" + "=" * 80)
    print("🚀 REAL DATA IMPORT - SUPPLIERS & BOMS")
    print("=" * 80)
    print("This script will:")
    print("1. Extract real suppliers from material database")
    print("2. Import suppliers to Partners table")
    print("3. Import real BOM data from all 6 Excel files")
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
        total_boms = import_all_boms(db)
        
        # Summary
        supplier_count = db.query(Partner).filter(Partner.type == PartnerType.SUPPLIER).count()
        bom_count = db.query(BOMHeader).count()
        detail_count = db.query(BOMDetail).count()
        
        print("\n" + "=" * 80)
        print("✅ IMPORT COMPLETE!")
        print("=" * 80)
        print(f"   Suppliers: {supplier_count}")
        print(f"   BOM Headers: {bom_count}")
        print(f"   BOM Details: {detail_count}")
        print("=" * 80)
        print("\n🎯 Now you can test AUTO mode with real BOM data!")
    
    except Exception as e:
        db.rollback()
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    main()
