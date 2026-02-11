"""
Masterdata Import from docs/Masterdata Excel Files
Imports real production data from Excel files

Import Order:
1. Materials (from DATABASE MATERIAL ALL.xlsx)
2. Articles (from Article.xlsx)
3. BOMs - Production (from BOM Production/*.xlsx: Cutting, Embo, Sewing, Finishing, Packing)
4. Cartons (from Karton/Carton.xlsx)

Features:
- Excel file reading with pandas
- Data validation and cleaning
- Transaction-safe imports
- Detailed progress reporting
"""

import sys
import os
from pathlib import Path
from typing import List, Dict, Tuple
import pandas as pd
from decimal import Decimal
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from sqlalchemy.orm import Session
from sqlalchemy import inspect
from app.core.database import SessionLocal
from app.core.models.products import Product, ProductType, UOM, Category
from app.core.models.bom import BOMHeader, BOMDetail, BOMType


class MasterdataImporter:
    """Import masterdata from Excel files."""
    
    def __init__(self, db: Session, base_path: str = "../docs/Masterdata"):
        self.db = db
        self.base_path = Path(base_path)
        self.stats = {
            "materials_imported": 0,
            "articles_imported": 0,
            "boms_imported": 0,
            "cartons_imported": 0,
            "errors": []
        }
    
    def log(self, message: str, level: str = "INFO"):
        """Log message with timestamp."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        prefix = {
            "INFO": "ℹ️",
            "SUCCESS": "✅",
            "WARNING": "⚠️",
            "ERROR": "❌"
        }.get(level, "ℹ️")
        print(f"[{timestamp}] {prefix} {message}")
    
    def get_or_create_category(self, category_name: str) -> int:
        """Get or create product category."""
        category = self.db.query(Category).filter(Category.name == category_name).first()
        if not category:
            category = Category(name=category_name, description=f"Auto-created: {category_name}")
            self.db.add(category)
            self.db.flush()
            self.log(f"Created category: {category_name}", "SUCCESS")
        return category.id
    
    def parse_uom(self, uom_str: str) -> str:
        """Parse UOM string to enum value."""
        uom_map = {
            "PCS": "Pcs",
            "METER": "Meter",
            "YARD": "Yard",
            "KG": "Kg",
            "ROLL": "Roll",
            "CM": "Cm",
            "M": "Meter",
            "YD": "Yard",
            "PIECE": "Pcs",
            "PIECES": "Pcs",
        }
        normalized = str(uom_str).upper().strip()
        return uom_map.get(normalized, "Pcs")  # Default to Pcs
    
    def import_materials(self) -> int:
        """Import materials from DATABASE MATERIAL ALL.xlsx"""
        self.log("=" * 80)
        self.log("IMPORTING MATERIALS FROM EXCEL", "INFO")
        self.log("=" * 80)
        
        file_path = self.base_path / "Material" / "DATABASE MATERIAL ALL.xlsx"
        
        if not file_path.exists():
            self.log(f"File not found: {file_path}", "ERROR")
            return 0
        
        self.log(f"Reading file: {file_path}")
        
        try:
            # Read Excel file
            df = pd.read_excel(file_path)
            self.log(f"Loaded {len(df)} rows from Excel", "SUCCESS")
            self.log(f"Columns: {', '.join(df.columns.tolist())}")
            
            # Display first few rows for inspection
            print("\n📊 Sample data (first 3 rows):")
            print(df.head(3).to_string())
            print()
            
            # Expected columns (adjust based on actual file)
            # Common columns: Code, Name, Type, UOM, Category, Min Stock, etc.
            
            imported_count = 0
            skipped_count = 0
            
            for idx, row in df.iterrows():
                try:
                    # Extract material data - try to find code and name from any column
                    material_code = None
                    material_name = None
                    material_type = "RAW_MATERIAL"
                    uom = "Pcs"
                    category_name = "Materials"
                    min_stock = 0
                    
                    # Get first non-null value as code (usually first column)
                    for col in df.columns:
                        val = row[col]
                        if pd.notna(val) and str(val).strip() and not material_code:
                            material_code = str(val).strip()
                            break
                    
                    # Get second non-null value as name (usually second column)
                    found_first = False
                    for col in df.columns:
                        val = row[col]
                        if pd.notna(val) and str(val).strip():
                            if found_first and not material_name:
                                material_name = str(val).strip()
                                break
                            elif not found_first:
                                found_first = True
                    
                    # Try to extract category and UOM from other columns
                    for col in df.columns:
                        col_lower = str(col).lower().strip()
                        val = row[col]
                        if not pd.notna(val):
                            continue
                        
                        # UOM detection
                        if 'uom' in col_lower or 'satuan' in col_lower or 'unit' in col_lower:
                            uom = self.parse_uom(val)
                        # Category detection
                        elif 'category' in col_lower or 'kategori' in col_lower or 'type' in col_lower:
                            if pd.notna(val) and str(val).strip():
                                category_name = str(val).strip()
                        # Min stock detection
                        elif 'min' in col_lower and 'stock' in col_lower:
                            try:
                                min_stock = float(val)
                            except:
                                min_stock = 0
                    
                    # Validate required fields
                    if not material_code or not material_name or len(material_name) < 2:
                        skipped_count += 1
                        continue
                    
                    # Check if material already exists
                    existing = self.db.query(Product).filter(Product.code == material_code).first()
                    if existing:
                        self.log(f"Material {material_code} already exists, skipping", "WARNING")
                        skipped_count += 1
                        continue
                    
                    # Get or create category
                    category_id = self.get_or_create_category(category_name)
                    
                    # Create material
                    material = Product(
                        code=material_code,
                        name=material_name,
                        type=ProductType.RAW_MATERIAL,
                        uom=getattr(UOM, uom.upper(), UOM.PCS),
                        category_id=category_id,
                        min_stock=Decimal(str(min_stock)),
                        is_active=True
                    )
                    
                    self.db.add(material)
                    imported_count += 1
                    
                    if imported_count % 50 == 0:
                        self.db.flush()
                        self.log(f"Progress: {imported_count} materials imported...")
                
                except Exception as e:
                    self.log(f"Row {idx+2}: Error - {str(e)}", "ERROR")
                    self.stats["errors"].append(f"Material import row {idx+2}: {str(e)}")
                    continue
            
            # Commit transaction
            self.db.commit()
            
            self.log("=" * 80)
            self.log(f"✅ Materials Import Complete!", "SUCCESS")
            self.log(f"   Imported: {imported_count}")
            self.log(f"   Skipped: {skipped_count}")
            self.log("=" * 80)
            
            self.stats["materials_imported"] = imported_count
            return imported_count
            
        except Exception as e:
            self.log(f"Fatal error importing materials: {str(e)}", "ERROR")
            self.db.rollback()
            import traceback
            traceback.print_exc()
            return 0
    
    def import_articles(self) -> int:
        """Import articles from Article.xlsx"""
        self.log("=" * 80)
        self.log("IMPORTING ARTICLES (FINISHED GOODS) FROM EXCEL", "INFO")
        self.log("=" * 80)
        
        file_path = self.base_path / "Article" / "Article.xlsx"
        
        if not file_path.exists():
            self.log(f"File not found: {file_path}", "ERROR")
            return 0
        
        self.log(f"Reading file: {file_path}")
        
        try:
            df = pd.read_excel(file_path)
            self.log(f"Loaded {len(df)} rows from Excel", "SUCCESS")
            self.log(f"Columns: {', '.join(df.columns.tolist())}")
            
            print("\n📊 Sample data (first 3 rows):")
            print(df.head(3).to_string())
            print()
            
            imported_count = 0
            skipped_count = 0
            
            # Get or create "Finished Goods" category
            fg_category_id = self.get_or_create_category("Finished Goods")
            
            for idx, row in df.iterrows():
                try:
                    article_code = None
                    article_name = None
                    pcs_per_carton = 60  # Default value
                    destination = None
                    
                    # Get first non-null value as article code
                    for col in df.columns:
                        val = row[col]
                        if pd.notna(val) and str(val).strip() and not article_code:
                            # Convert to string and clean
                            code_str = str(val).strip()
                            # Handle numeric codes (like 40551542)
                            if code_str.replace('.', '').replace('-', '').isdigit():
                                article_code = code_str.replace('.0', '')  # Remove trailing .0
                            else:
                                article_code = code_str
                            break
                    
                    # Get second non-null value as article name
                    found_first = False
                    for col in df.columns:
                        val = row[col]
                        if pd.notna(val) and str(val).strip():
                            if found_first and not article_name:
                                article_name = str(val).strip()
                                break
                            elif not found_first:
                                found_first = True
                    
                    # Try to get destination or other metadata
                    for col in df.columns:
                        col_lower = str(col).lower().strip()
                        val = row[col]
                        if not pd.notna(val):
                            continue
                        
                        if 'destination' in col_lower or 'dest' in col_lower:
                            destination = str(val).strip()
                        elif 'pcs' in col_lower and 'carton' in col_lower:
                            try:
                                pcs_per_carton = int(val)
                            except:
                                pcs_per_carton = 60
                    
                    if not article_code or not article_name or len(article_name) < 5:
                        skipped_count += 1
                        continue
                    
                    # Check if exists
                    existing = self.db.query(Product).filter(Product.code == article_code).first()
                    if existing:
                        self.log(f"Article {article_code} already exists, skipping", "WARNING")
                        skipped_count += 1
                        continue
                    
                    # Create article
                    article = Product(
                        code=article_code,
                        name=article_name,
                        type=ProductType.FINISH_GOOD,
                        uom=UOM.PCS,
                        category_id=fg_category_id,
                        pcs_per_carton=pcs_per_carton,
                        cartons_per_pallet=8,  # Default value
                        min_stock=Decimal("0"),
                        is_active=True
                    )
                    
                    self.db.add(article)
                    imported_count += 1
                    
                    if imported_count % 20 == 0:
                        self.db.flush()
                        self.log(f"Progress: {imported_count} articles imported...")
                
                except Exception as e:
                    self.log(f"Row {idx+2}: Error - {str(e)}", "ERROR")
                    self.stats["errors"].append(f"Article import row {idx+2}: {str(e)}")
                    continue
            
            self.db.commit()
            
            self.log("=" * 80)
            self.log(f"✅ Articles Import Complete!", "SUCCESS")
            self.log(f"   Imported: {imported_count}")
            self.log(f"   Skipped: {skipped_count}")
            self.log("=" * 80)
            
            self.stats["articles_imported"] = imported_count
            return imported_count
            
        except Exception as e:
            self.log(f"Fatal error importing articles: {str(e)}", "ERROR")
            self.db.rollback()
            import traceback
            traceback.print_exc()
            return 0
    
    def import_all(self):
        """Import all masterdata in correct order."""
        self.log("=" * 80)
        self.log("🚀 STARTING COMPREHENSIVE MASTERDATA IMPORT")
        self.log("=" * 80)
        self.log(f"Base path: {self.base_path.absolute()}")
        print()
        
        # Step 1: Import Materials
        self.import_materials()
        print()
        
        # Step 2: Import Articles
        self.import_articles()
        print()
        
        # Step 3: BOMs (future - requires more complex parsing)
        self.log("=" * 80)
        self.log("📋 BOM Import - PENDING (Complex multi-stage BOM structure)")
        self.log("=" * 80)
        self.log("BOM files found:")
        bom_path = self.base_path / "BOM Production"
        if bom_path.exists():
            for bom_file in bom_path.glob("*.xlsx"):
                self.log(f"   - {bom_file.name}")
        self.log("Note: BOM import requires custom parsing per department")
        print()
        
        # Final Summary
        self.log("=" * 80)
        self.log("📊 IMPORT SUMMARY")
        self.log("=" * 80)
        self.log(f"✅ Materials Imported: {self.stats['materials_imported']}")
        self.log(f"✅ Articles Imported: {self.stats['articles_imported']}")
        self.log(f"✅ BOMs Imported: {self.stats['boms_imported']} (pending)")
        self.log(f"❌ Errors: {len(self.stats['errors'])}")
        
        if self.stats['errors']:
            self.log("\n⚠️ Error Details:")
            for error in self.stats['errors'][:10]:  # Show first 10 errors
                self.log(f"   {error}")
        
        self.log("=" * 80)
        self.log("✅ MASTERDATA IMPORT COMPLETE!", "SUCCESS")
        self.log("=" * 80)


def main():
    """Main execution."""
    print()
    print("=" * 80)
    print("📦 MASTERDATA IMPORTER")
    print("=" * 80)
    print("This script imports real production data from Excel files:")
    print("  - Materials (DATABASE MATERIAL ALL.xlsx)")
    print("  - Articles (Article.xlsx)")
    print("  - BOMs (BOM Production/*.xlsx) - Pending")
    print("=" * 80)
    print()
    
    response = input("❓ Continue with import? (yes/no): ")
    if response.lower() != 'yes':
        print("❌ Import cancelled.")
        return
    
    db = SessionLocal()
    try:
        importer = MasterdataImporter(db)
        importer.import_all()
    except KeyboardInterrupt:
        print("\n\n❌ Import interrupted by user.")
        db.rollback()
    except Exception as e:
        print(f"\n❌ FATAL ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    main()
