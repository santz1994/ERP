"""
BOM Import Script - Import 6 Excel files to Database
Import BOM per department dengan WIP product structure

Author: IT Developer Expert
Date: 3 Februari 2026
"""

import pandas as pd
import sys
from pathlib import Path
from sqlalchemy.orm import Session
from decimal import Decimal

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.database import get_db, engine
from app.core.models.products import Product, Category, ProductType
from app.core.models.bom import BOMHeader, BOMDetail, BOMType, BOMVariant, BOMVariantType
from sqlalchemy import create_engine, text

# Configuration
BOM_FILES = {
    'CUTTING': 'd:/Project/ERP2026/docs/BOM/Cutting.xlsx',
    'EMBO': 'd:/Project/ERP2026/docs/BOM/Embo.xlsx',
    'SEWING': 'd:/Project/ERP2026/docs/BOM/Sewing.xlsx',
    'FINISHING': 'd:/Project/ERP2026/docs/BOM/Finishing.xlsx',
    'PACKING': 'd:/Project/ERP2026/docs/BOM/Packing.xlsx',
    'FINISHING_GOODS': 'd:/Project/ERP2026/docs/BOM/Finishing Goods.xlsx'
}


class BOMImporter:
    """BOM Importer - Import dari Excel ke database"""
    
    def __init__(self, db: Session):
        self.db = db
        self.stats = {
            'categories_created': 0,
            'products_created': 0,
            'bom_headers_created': 0,
            'bom_details_created': 0,
            'errors': []
        }
        
        # Cache untuk product lookup (speed optimization)
        self.product_cache = {}
        self.category_cache = {}
    
    def run_import(self):
        """Main import process"""
        print("="*80)
        print("🚀 STARTING BOM IMPORT FROM EXCEL")
        print("="*80)
        
        try:
            # Step 1: Create WIP categories
            self._create_categories()
            
            # Step 2: Import each department BOM
            for dept, file_path in BOM_FILES.items():
                print(f"\n{'='*80}")
                print(f"📦 Importing {dept} BOM from: {file_path}")
                print("="*80)
                self._import_department_bom(dept, file_path)
            
            # Step 3: Show statistics
            self._print_statistics()
            
            print("\n✅ BOM IMPORT COMPLETED SUCCESSFULLY!")
            
        except Exception as e:
            print(f"\n❌ ERROR during import: {str(e)}")
            import traceback
            traceback.print_exc()
            self.db.rollback()
            raise
    
    def _create_categories(self):
        """Create product categories for WIP and RAW materials"""
        print("\n📂 Creating product categories...")
        
        # Category model only has: id, name, description (NO CODE field)
        categories_to_create = [
            {'name': 'Raw Materials', 'description': 'Fabric, Thread, Filling, etc'},
            {'name': 'WIP Cutting', 'description': 'Work In Progress - Cutting Department'},
            {'name': 'WIP Embroidery', 'description': 'Work In Progress - Embroidery Department'},
            {'name': 'WIP Sewing', 'description': 'Work In Progress - Sewing Department'},
            {'name': 'WIP Finishing', 'description': 'Work In Progress - Finishing Department'},
            {'name': 'WIP Packing', 'description': 'Work In Progress - Packing Department'},
            {'name': 'Finished Goods', 'description': 'Final products ready for sale'},
            {'name': 'Accessories', 'description': 'Labels, Hang Tags, Carton, etc'}
        ]
        
        for cat_data in categories_to_create:
            # Check if exists by name
            existing = self.db.query(Category).filter_by(name=cat_data['name']).first()
            if not existing:
                category = Category(**cat_data)
                self.db.add(category)
                self.db.flush()  # Get ID
                self.stats['categories_created'] += 1
                print(f"  ✅ Created category: {cat_data['name']}")
                self.category_cache[cat_data['name']] = category
            else:
                print(f"  ⏭️  Category exists: {cat_data['name']}")
                self.category_cache[cat_data['name']] = existing
        
        self.db.commit()
        print(f"📂 Categories ready: {self.stats['categories_created']} new, {len(categories_to_create) - self.stats['categories_created']} existing")
    
    def _import_department_bom(self, department: str, file_path: str):
        """Import BOM for specific department"""
        try:
            # Read Excel file
            df = pd.read_excel(file_path)
            print(f"📄 Loaded {len(df)} rows from Excel")
            
            # Get unique products (WIP products for this department)
            unique_products = df['Product'].dropna().unique()
            print(f"🎯 Found {len(unique_products)} unique WIP products")
            
            # Process each WIP product
            for idx, product_code in enumerate(unique_products, 1):
                try:
                    self._process_wip_product(department, product_code, df)
                    
                    # Progress indicator
                    if idx % 10 == 0:
                        print(f"  ⏳ Progress: {idx}/{len(unique_products)} products processed")
                
                except Exception as e:
                    error_msg = f"Error processing {product_code}: {str(e)}"
                    print(f"  ❌ {error_msg}")
                    self.stats['errors'].append(error_msg)
            
            print(f"✅ Completed {department}: {idx} WIP products imported")
            
        except Exception as e:
            print(f"❌ Failed to import {department}: {str(e)}")
            raise
    
    def _process_wip_product(self, department: str, product_code: str, df: pd.DataFrame):
        """Process single WIP product and its BOM"""
        
        # Get product data
        product_rows = df[df['Product'] == product_code]
        if product_rows.empty:
            return
        
        first_row = product_rows.iloc[0]
        product_name = first_row['Product/Name']
        bom_type = first_row.get('BoM Type', 'Manufacture this product')
        
        # Step 1: Create or get WIP product
        wip_product = self._get_or_create_product(
            default_code=product_code,
            name=product_name,
            category_code=f'WIP_{department}',
            product_type='wip'
        )
        
        # Step 2: Create BOM Header for this WIP product
        bom_header = self._get_or_create_bom_header(
            product_id=wip_product.id,
            bom_type_str=bom_type
        )
        
        # Step 3: Create BOM Details (materials for this WIP)
        material_rows = product_rows[product_rows['BoM Lines/Component'].notna()]
        
        for _, material_row in material_rows.iterrows():
            try:
                self._create_bom_detail(
                    bom_header_id=bom_header.id,
                    material_row=material_row,
                    department=department
                )
            except Exception as e:
                print(f"    ⚠️  Skip material line: {str(e)}")
    
    def _get_or_create_product(self, default_code: str, name: str, category_code: str, product_type: str = 'wip'):
        """Get existing product or create new one"""
        
        # Check cache first
        if default_code in self.product_cache:
            return self.product_cache[default_code]
        
        # Check database
        product = self.db.query(Product).filter_by(code=default_code).first()
        
        if not product:
            # Map category code to category name
            category_name_mapping = {
                'RAW': 'Raw Materials',
                'WIP_CUTTING': 'WIP Cutting',
                'WIP_EMBO': 'WIP Embroidery',
                'WIP_SEWING': 'WIP Sewing',
                'WIP_FINISHING': 'WIP Finishing',
                'WIP_PACKING': 'WIP Packing',
                'FINISHED_GOOD': 'Finished Goods',
                'ACCESSORIES': 'Accessories'
            }
            
            category_name = category_name_mapping.get(category_code, 'Raw Materials')
            
            # Get category from cache or database
            if category_name in self.category_cache:
                category = self.category_cache[category_name]
            else:
                category = self.db.query(Category).filter_by(name=category_name).first()
            
            if not category:
                raise ValueError(f"Category {category_name} (mapped from {category_code}) not found!")
            
            # Map product_type string to ProductType enum
            # Script uses: 'wip', 'consu'
            # Enum expects: RAW_MATERIAL, WIP, FINISH_GOOD, SERVICE
            product_type_mapping = {
                'wip': 'WIP',
                'consu': 'RAW_MATERIAL',
                'raw_material': 'RAW_MATERIAL',
                'finished_good': 'FINISH_GOOD',
                'service': 'SERVICE'
            }
            
            product_type_enum = product_type_mapping.get(product_type.lower(), 'RAW_MATERIAL')
            
            # Map to UOM enum (default to PCS not PCE!)
            uom_value = 'PCS'  # Valid values: PCS, METER, YARD, KG, ROLL, CM
            
            # Create product with CORRECT field names
            product = Product(
                code=default_code,  # NOT default_code!
                name=name,
                category_id=category.id,  # NOT categ_id!
                type=product_type_enum,  # Enum value
                uom=uom_value,  # Required field
                min_stock=0
            )
            self.db.add(product)
            self.db.flush()  # Get ID without committing
            
            self.stats['products_created'] += 1
            print(f"    ✨ Created product: {default_code}")
        
        # Add to cache
        self.product_cache[default_code] = product
        
        return product
    
    def _get_or_create_bom_header(self, product_id: int, bom_type_str: str):
        """Get existing BOM header or create new one"""
        
        # Check if BOM exists
        existing = self.db.query(BOMHeader).filter_by(product_id=product_id, is_active=True).first()
        
        if existing:
            return existing
        
        # Create new BOM header
        bom_type = BOMType.MANUFACTURING if 'manufactur' in bom_type_str.lower() else BOMType.KIT_PHANTOM
        
        bom_header = BOMHeader(
            product_id=product_id,
            bom_type=bom_type,
            qty_output=Decimal('1.0'),
            is_active=True,
            supports_multi_material=False  # Will detect and enable if variants found
        )
        
        self.db.add(bom_header)
        self.db.flush()
        
        self.stats['bom_headers_created'] += 1
        
        return bom_header
    
    def _create_bom_detail(self, bom_header_id: int, material_row: pd.Series, department: str):
        """Create BOM detail line (material requirement)"""
        
        component_code = material_row['BoM Lines/Component']
        component_name = material_row.get('BoM Lines/Component/Name', component_code)
        qty_needed = material_row.get('BoM Lines/Quantity', 0)
        uom = material_row.get('BoM Lines/Product Unit of Measure', 'PCE')
        
        # Skip if qty is 0
        if pd.isna(qty_needed) or qty_needed == 0:
            return
        
        # Determine material category
        material_category = self._detect_material_category(component_code, component_name, department)
        
        # Create or get material product
        material_product = self._get_or_create_product(
            default_code=component_code,
            name=component_name,
            category_code=material_category,
            product_type='consu'  # Consumable (material)
        )
        
        # Check if detail already exists
        existing_detail = self.db.query(BOMDetail).filter_by(
            bom_header_id=bom_header_id,
            component_id=material_product.id
        ).first()
        
        if existing_detail:
            return  # Skip duplicate
        
        # Create BOM detail
        bom_detail = BOMDetail(
            bom_header_id=bom_header_id,
            component_id=material_product.id,
            qty_needed=Decimal(str(qty_needed)),
            wastage_percent=Decimal('0'),
            has_variants=False
        )
        
        self.db.add(bom_detail)
        self.db.flush()
        
        self.stats['bom_details_created'] += 1
    
    def _detect_material_category(self, component_code: str, component_name: str, department: str) -> str:
        """Detect material category based on code/name patterns"""
        
        code_upper = component_code.upper()
        name_upper = component_name.upper()
        
        # WIP detection (from previous department)
        if '_WIP_' in code_upper:
            # Determine which WIP category
            if 'WIP_CUTTING' in code_upper:
                return 'WIP_CUTTING'
            elif 'WIP_EMBO' in code_upper:
                return 'WIP_EMBO'
            elif 'WIP_SEWING' in code_upper or 'WIP_SKIN' in code_upper or 'WIP_BAJU' in code_upper:
                return 'WIP_SEWING'
            elif 'WIP_FINISHING' in code_upper or 'WIP_BONEKA' in code_upper:
                return 'WIP_FINISHING'
            elif 'WIP_PACKING' in code_upper:
                return 'WIP_PACKING'
        
        # Fabric materials
        if any(x in name_upper for x in ['KOHAIR', 'POLYESTER', 'NYLEX', 'BOA', 'FABRIC', 'KAIN']):
            return 'RAW'
        
        # Thread materials
        if any(x in name_upper for x in ['THREAD', 'BENANG', 'ASTRA', 'NILON', 'NYLON']):
            return 'RAW'
        
        # Filling materials
        if any(x in name_upper for x in ['FILLING', 'KAPAS', 'HCS', 'STUFFING']):
            return 'RAW'
        
        # Accessories (labels, tags, etc)
        if any(x in name_upper for x in ['LABEL', 'HANG TAG', 'TAG', 'STICKER', 'CARTON', 'PALLET', 'PAD', 'BOX']):
            return 'ACCESSORIES'
        
        # Default to RAW
        return 'RAW'
    
    def _print_statistics(self):
        """Print import statistics"""
        print("\n" + "="*80)
        print("📊 IMPORT STATISTICS")
        print("="*80)
        print(f"Categories created: {self.stats['categories_created']}")
        print(f"Products created: {self.stats['products_created']}")
        print(f"BOM Headers created: {self.stats['bom_headers_created']}")
        print(f"BOM Details created: {self.stats['bom_details_created']}")
        print(f"Errors: {len(self.stats['errors'])}")
        
        if self.stats['errors']:
            print("\n❌ Errors encountered:")
            for error in self.stats['errors'][:10]:  # Show first 10 errors
                print(f"  - {error}")
            if len(self.stats['errors']) > 10:
                print(f"  ... and {len(self.stats['errors']) - 10} more errors")


def main():
    """Main entry point"""
    print("\n" + "="*80)
    print("🎯 BOM IMPORT SCRIPT - From Excel to Database")
    print("="*80)
    print(f"Files to import: {len(BOM_FILES)}")
    for dept, path in BOM_FILES.items():
        print(f"  - {dept}: {path}")
    
    # Confirm
    confirm = input("\n⚠️  This will import BOM data to database. Continue? (yes/no): ")
    if confirm.lower() != 'yes':
        print("❌ Import cancelled by user")
        return
    
    # Start import
    db = next(get_db())
    try:
        importer = BOMImporter(db)
        importer.run_import()
        
        # Commit all changes
        db.commit()
        print("\n✅ All changes committed to database")
        
    except Exception as e:
        print(f"\n❌ Import failed: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
