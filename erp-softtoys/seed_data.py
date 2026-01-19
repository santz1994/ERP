"""
Test Data Seeding Script
Populate database with sample data for development and testing
"""

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.core.security import PasswordUtils
from app.core.models.users import User, UserRole
from app.core.models.products import Product, Category, ProductType, UOM
from app.core.models.warehouse import Location, StockQuant, StockLot
from decimal import Decimal
from datetime import datetime


def create_test_users(db: Session):
    """Create test users with different roles"""
    print("Creating test users...")
    
    # Get or create roles
    roles_data = [
        ("admin", "System Administrator"),
        ("ppic_manager", "Production Planning Manager"),
        ("spv_cutting", "Cutting Supervisor"),
        ("spv_sewing", "Sewing Supervisor"),
        ("spv_finishing", "Finishing Supervisor"),
        ("operator_cutting", "Cutting Operator"),
        ("operator_sewing", "Sewing Operator"),
        ("operator_finishing", "Finishing Operator"),
        ("qc_inspector", "QC Inspector"),
        ("warehouse_admin", "Warehouse Administrator"),
    ]
    
    roles = {}
    for role_name, role_desc in roles_data:
        role = db.query(UserRole).filter(UserRole.name == role_name).first()
        if not role:
            role = UserRole(name=role_name, description=role_desc)
            db.add(role)
        roles[role_name] = role
    db.commit()
    
    # Create test users
    test_users = [
        {
            "username": "admin",
            "email": "admin@qutykarunia.com",
            "full_name": "Admin User",
            "password": "Admin123456",
            "roles": ["admin"]
        },
        {
            "username": "ppic_user",
            "email": "ppic@qutykarunia.com",
            "full_name": "PPIC Manager",
            "password": "Ppic123456",
            "roles": ["ppic_manager"]
        },
        {
            "username": "spv_cutting",
            "email": "spv.cutting@qutykarunia.com",
            "full_name": "SPV Cutting",
            "password": "SpvCut123456",
            "roles": ["spv_cutting"]
        },
        {
            "username": "op_cutting",
            "email": "operator.cutting@qutykarunia.com",
            "full_name": "Operator Cutting",
            "password": "OpCut123456",
            "roles": ["operator_cutting"]
        },
        {
            "username": "warehouse",
            "email": "warehouse@qutykarunia.com",
            "full_name": "Warehouse Admin",
            "password": "Warehouse123456",
            "roles": ["warehouse_admin"]
        },
    ]
    
    for user_data in test_users:
        existing = db.query(User).filter(User.username == user_data["username"]).first()
        if not existing:
            user = User(
                username=user_data["username"],
                email=user_data["email"],
                full_name=user_data["full_name"],
                password_hash=PasswordUtils.hash_password(user_data["password"]),
                is_active=True
            )
            for role_name in user_data["roles"]:
                user.roles.append(roles[role_name])
            db.add(user)
    db.commit()
    print("✓ Test users created")


def create_test_categories(db: Session):
    """Create product categories"""
    print("Creating product categories...")
    
    categories_data = [
        ("Fabric", "Raw materials - Fabrics"),
        ("Accessory", "Raw materials - Accessories (buttons, eyes, etc)"),
        ("WIP Cut", "Work in progress - Cutting department"),
        ("WIP Embo", "Work in progress - Embroidery department"),
        ("WIP Sew", "Work in progress - Sewing department"),
        ("Finish Good", "Finished products ready for shipment"),
    ]
    
    for name, description in categories_data:
        existing = db.query(Category).filter(Category.name == name).first()
        if not existing:
            category = Category(name=name, description=description)
            db.add(category)
    db.commit()
    print("✓ Product categories created")


def create_test_products(db: Session):
    """Create test products (parent and child articles)"""
    print("Creating test products...")
    
    # Get categories
    fabric_cat = db.query(Category).filter(Category.name == "Fabric").first()
    wip_cut_cat = db.query(Category).filter(Category.name == "WIP Cut").first()
    wip_embo_cat = db.query(Category).filter(Category.name == "WIP Embo").first()
    wip_sew_cat = db.query(Category).filter(Category.name == "WIP Sew").first()
    fg_cat = db.query(Category).filter(Category.name == "Finish Good").first()
    
    # Create parent article (IKEA product)
    parent_product = db.query(Product).filter(Product.code == "BLAHAJ-100").first()
    if not parent_product:
        parent_product = Product(
            code="BLAHAJ-100",
            name="BLAHAJ - Blue Shark 100cm",
            type=ProductType.FINISH_GOOD,
            uom=UOM.PCS,
            category_id=fg_cat.id if fg_cat else None,
            min_stock=Decimal("100")
        )
        db.add(parent_product)
        db.commit()
        db.refresh(parent_product)
    
    # Create child articles (internal articles for each department)
    child_articles = [
        {
            "code": "CUT-BLA-01",
            "name": "Cutting Pattern - BLAHAJ Blue Shark",
            "type": ProductType.WIP,
            "category_id": wip_cut_cat.id if wip_cut_cat else None,
            "parent_article_id": parent_product.id,
            "min_stock": Decimal("0")
        },
        {
            "code": "EMB-BLA-01",
            "name": "Embroidery Panel - BLAHAJ Blue Shark",
            "type": ProductType.WIP,
            "category_id": wip_embo_cat.id if wip_embo_cat else None,
            "parent_article_id": parent_product.id,
            "min_stock": Decimal("0")
        },
        {
            "code": "SEW-BLA-01",
            "name": "Sewing Skin - BLAHAJ Blue Shark",
            "type": ProductType.WIP,
            "category_id": wip_sew_cat.id if wip_sew_cat else None,
            "parent_article_id": parent_product.id,
            "min_stock": Decimal("0")
        },
        {
            "code": "PAC-BLA-01",
            "name": "Packing Unit - BLAHAJ Blue Shark",
            "type": ProductType.FINISH_GOOD,
            "category_id": fg_cat.id if fg_cat else None,
            "parent_article_id": parent_product.id,
            "min_stock": Decimal("50")
        },
    ]
    
    for article_data in child_articles:
        existing = db.query(Product).filter(Product.code == article_data["code"]).first()
        if not existing:
            product = Product(**article_data, uom=UOM.PCS)
            db.add(product)
    
    # Create raw materials
    raw_materials = [
        {
            "code": "FAB-BLU-SHARK",
            "name": "Fabric - Blue Shark Pattern",
            "type": ProductType.RAW_MATERIAL,
            "category_id": fabric_cat.id if fabric_cat else None,
            "min_stock": Decimal("1000"),
            "uom": UOM.METER
        },
        {
            "code": "ACC-EYES-BLK",
            "name": "Accessories - Black Eyes",
            "type": ProductType.RAW_MATERIAL,
            "category_id": fabric_cat.id if fabric_cat else None,
            "min_stock": Decimal("5000"),
            "uom": UOM.PCS
        },
        {
            "code": "ACC-THREAD-BLU",
            "name": "Accessories - Blue Thread",
            "type": ProductType.RAW_MATERIAL,
            "category_id": fabric_cat.id if fabric_cat else None,
            "min_stock": Decimal("500"),
            "uom": UOM.ROLL
        },
    ]
    
    for material_data in raw_materials:
        existing = db.query(Product).filter(Product.code == material_data["code"]).first()
        if not existing:
            product = Product(**material_data)
            db.add(product)
    
    db.commit()
    print("✓ Test products created")


def create_test_locations(db: Session):
    """Create warehouse locations"""
    print("Creating warehouse locations...")
    
    locations_data = [
        ("Gudang Bahan Baku", "Raw Material Warehouse"),
        ("Line Cutting", "Cutting Department Line"),
        ("Line Embroidery", "Embroidery Department Line"),
        ("Line Sewing", "Sewing Department Line"),
        ("Line Finishing", "Finishing Department Line"),
        ("Line Packing", "Packing Department Line"),
        ("Finished Good Storage", "Finished Good Warehouse"),
    ]
    
    for name, description in locations_data:
        existing = db.query(Location).filter(Location.name == name).first()
        if not existing:
            location = Location(
                name=name,
                type="inventory",
                description=description
            )
            db.add(location)
    db.commit()
    print("✓ Warehouse locations created")


def create_test_stock(db: Session):
    """Create test stock data"""
    print("Creating test stock data...")
    
    # Get products and locations
    raw_material = db.query(Product).filter(Product.code == "FAB-BLU-SHARK").first()
    warehouse = db.query(Location).filter(Location.name == "Gudang Bahan Baku").first()
    
    if raw_material and warehouse:
        # Create stock lot
        existing_lot = db.query(StockLot).filter(StockLot.lot_number == "LOT-2026-001").first()
        if not existing_lot:
            stock_lot = StockLot(
                lot_number="LOT-2026-001",
                product_id=raw_material.id,
                qty_total=Decimal("10000"),
                qty_available=Decimal("10000"),
                receipt_date=datetime.utcnow()
            )
            db.add(stock_lot)
            db.commit()
            db.refresh(stock_lot)
        else:
            stock_lot = existing_lot
        
        # Create stock quant
        existing_quant = db.query(StockQuant).filter(
            (StockQuant.product_id == raw_material.id) &
            (StockQuant.location_id == warehouse.id)
        ).first()
        if not existing_quant:
            stock_quant = StockQuant(
                product_id=raw_material.id,
                location_id=warehouse.id,
                lot_id=stock_lot.id,
                qty_on_hand=Decimal("10000"),
                qty_reserved=Decimal("0")
            )
            db.add(stock_quant)
            db.commit()
    
    print("✓ Test stock created")


def seed_database():
    """Main seeding function"""
    db = SessionLocal()
    try:
        print("\n" + "="*50)
        print("SEEDING TEST DATA")
        print("="*50 + "\n")
        
        create_test_users(db)
        create_test_categories(db)
        create_test_products(db)
        create_test_locations(db)
        create_test_stock(db)
        
        print("\n" + "="*50)
        print("SEEDING COMPLETED SUCCESSFULLY ✓")
        print("="*50)
        print("\nTest Users:")
        print("  - admin / Admin123456")
        print("  - ppic_user / Ppic123456")
        print("  - spv_cutting / SpvCut123456")
        print("  - op_cutting / OpCut123456")
        print("  - warehouse / Warehouse123456")
        print("\n")
        
    except Exception as e:
        print(f"\n❌ Error seeding database: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
