"""
Complete Seed Data Creator - Session 50
Creates comprehensive test data for ERP system

Creates:
1. Suppliers (5)
2. Materials/Products (20 raw materials + 5 finished goods)
3. BOMs (5 active BOMs)
4. Manufacturing Orders (5 MOs)
5. Work Orders (15-20 WOs across departments)
6. Warehouse Locations (5 locations)
7. Initial stock quantities

Run with: python create_seed_data_complete.py
"""

import sys
import os
from datetime import datetime, timedelta
from decimal import Decimal
from typing import List

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.core.models.manufacturing import (
    ManufacturingOrder, WorkOrder, Department,
    MOState, WorkOrderStatus, RoutingType
)
from app.core.models.products import Product, ProductType, UOM, Partner, PartnerType
from app.core.models.bom import BOMHeader, BOMDetail
from app.core.models.warehouse import Location, StockQuant


def create_suppliers(db: Session) -> List[Partner]:
    """Create 5 suppliers."""
    print("\n" + "=" * 60)
    print("STEP 1: Creating Suppliers")
    print("=" * 60)
    
    suppliers_data = [
        {"code": "SUP-FABRIC-001", "name": "PT Kain Tekstil Jaya", "type": PartnerType.SUPPLIER, "phone": "021-12345678"},
        {"code": "SUP-THREAD-001", "name": "CV Benang Berkah", "type": PartnerType.SUPPLIER, "phone": "021-23456789"},
        {"code": "SUP-FILLING-001", "name": "PT Kapas Indonesia", "type": PartnerType.SUPPLIER, "phone": "021-34567890"},
        {"code": "SUP-LABEL-001", "name": "PT Label Printing", "type": PartnerType.SUPPLIER, "phone": "021-45678901"},
        {"code": "SUP-CARTON-001", "name": "CV Kardus Packaging", "type": PartnerType.SUPPLIER, "phone": "021-56789012"},
    ]
    
    suppliers = []
    for data in suppliers_data:
        # Check if exists
        existing = db.query(Partner).filter(Partner.code == data["code"]).first()
        if existing:
            print(f"   ⚠️  Supplier {data['code']} already exists, skipping...")
            suppliers.append(existing)
            continue
        
        supplier = Partner(
            code=data["code"],
            name=data["name"],
            type=data["type"],
            phone=data["phone"],
            email=f"{data['code'].lower()}@example.com",
            address="Jakarta, Indonesia",
            is_active=True
        )
        db.add(supplier)
        suppliers.append(supplier)
        print(f"   ✅ Created: {data['name']}")
    
    db.flush()
    print(f"\n✅ Total suppliers: {len(suppliers)}")
    return suppliers


def create_products(db: Session) -> tuple:
    """Create 20 raw materials + 5 finished goods."""
    print("\n" + "=" * 60)
    print("STEP 2: Creating Products (Materials + Finished Goods)")
    print("=" * 60)
    
    # Raw Materials (20 items)
    raw_materials_data = [
        # Fabrics (5)
        {"code": "IKHR504", "name": "KOHAIR 7MM RECYCLE D.BROWN", "type": ProductType.RAW, "uom": UOM.YARD},
        {"code": "IJBR105", "name": "JS BOA RECYCLE BROWN", "type": ProductType.RAW, "uom": UOM.YARD},
        {"code": "INYR002", "name": "NYLEX RECYCLE BLACK", "type": ProductType.RAW, "uom": UOM.YARD},
        {"code": "IPPR351", "name": "POLYESTER PRINT WHITE", "type": ProductType.RAW, "uom": UOM.YARD},
        {"code": "IPR301", "name": "POLYESTER WHITE", "type": ProductType.RAW, "uom": UOM.YARD},
        
        # Threads (5)
        {"code": "THR-001", "name": "Thread Brown 40s", "type": ProductType.RAW, "uom": UOM.CONE},
        {"code": "THR-002", "name": "Thread Black 40s", "type": ProductType.RAW, "uom": UOM.CONE},
        {"code": "THR-003", "name": "Thread White 40s", "type": ProductType.RAW, "uom": UOM.CONE},
        {"code": "THR-004", "name": "Thread Blue 40s", "type": ProductType.RAW, "uom": UOM.CONE},
        {"code": "THR-005", "name": "Thread Gray 40s", "type": ProductType.RAW, "uom": UOM.CONE},
        
        # Filling & Accessories (5)
        {"code": "IKP20157", "name": "RECYCLE HCS Filling", "type": ProductType.RAW, "uom": UOM.KG},
        {"code": "ALB40011", "name": "HANG TAG GUNTING", "type": ProductType.RAW, "uom": UOM.PCE},
        {"code": "ALL40030", "name": "LABEL EU", "type": ProductType.RAW, "uom": UOM.PCE},
        {"code": "AUL20220", "name": "STICKER ULL", "type": ProductType.RAW, "uom": UOM.PCE},
        {"code": "ALS40012", "name": "STICKER MIA", "type": ProductType.RAW, "uom": UOM.PCE},
        
        # Packing Materials (5)
        {"code": "ACB30104", "name": "CARTON 570X375X450", "type": ProductType.RAW, "uom": UOM.PCE},
        {"code": "ACB30121", "name": "PALLET", "type": ProductType.RAW, "uom": UOM.PCE},
        {"code": "ACB30132", "name": "PAD", "type": ProductType.RAW, "uom": UOM.PCE},
        {"code": "PKG-TAPE", "name": "Packing Tape", "type": ProductType.RAW, "uom": UOM.ROLL},
        {"code": "PKG-SHRINK", "name": "Shrink Wrap", "type": ProductType.RAW, "uom": UOM.ROLL},
    ]
    
    # Finished Goods (5 IKEA soft toys)
    finished_goods_data = [
        {"code": "40551542", "name": "AFTONSPARV soft toy w astronaut suit 28 bear", "type": ProductType.FINISH_GOOD, "uom": UOM.PCE},
        {"code": "40551543", "name": "BLAHAJ Shark 100cm", "type": ProductType.FINISH_GOOD, "uom": UOM.PCE},
        {"code": "40551544", "name": "KRAMIG Tiger Soft Toy", "type": ProductType.FINISH_GOOD, "uom": UOM.PCE},
        {"code": "40551545", "name": "DJUNGELSKOG Lion 100cm", "type": ProductType.FINISH_GOOD, "uom": UOM.PCE},
        {"code": "40551546", "name": "GOSIG GOLDEN Dog 70cm", "type": ProductType.FINISH_GOOD, "uom": UOM.PCE},
    ]
    
    raw_materials = []
    finished_goods = []
    
    print("\n📦 Raw Materials:")
    for data in raw_materials_data:
        existing = db.query(Product).filter(Product.code == data["code"]).first()
        if existing:
            print(f"   ⚠️  {data['code']} already exists, skipping...")
            raw_materials.append(existing)
            continue
        
        product = Product(
            code=data["code"],
            name=data["name"],
            type=data["type"],
            uom=data["uom"],
            is_active=True,
            standard_price=Decimal("10000"),  # Default price
            minimum_stock=Decimal("100")
        )
        db.add(product)
        raw_materials.append(product)
        print(f"   ✅ {data['code']}: {data['name']}")
    
    print("\n🧸 Finished Goods:")
    for data in finished_goods_data:
        existing = db.query(Product).filter(Product.code == data["code"]).first()
        if existing:
            print(f"   ⚠️  {data['code']} already exists, skipping...")
            finished_goods.append(existing)
            continue
        
        product = Product(
            code=data["code"],
            name=data["name"],
            type=data["type"],
            uom=data["uom"],
            is_active=True,
            standard_price=Decimal("150000"),  # FG price higher
            minimum_stock=Decimal("50")
        )
        db.add(product)
        finished_goods.append(product)
        print(f"   ✅ {data['code']}: {data['name']}")
    
    db.flush()
    print(f"\n✅ Total raw materials: {len(raw_materials)}")
    print(f"✅ Total finished goods: {len(finished_goods)}")
    
    return raw_materials, finished_goods


def create_boms(db: Session, raw_materials: List[Product], finished_goods: List[Product]) -> List[BOMHeader]:
    """Create 5 BOMs for finished goods."""
    print("\n" + "=" * 60)
    print("STEP 3: Creating BOMs")
    print("=" * 60)
    
    boms = []
    
    for fg in finished_goods:
        # Check if BOM exists
        existing = db.query(BOMHeader).filter(
            BOMHeader.product_id == fg.id,
            BOMHeader.is_active == True
        ).first()
        
        if existing:
            print(f"\n   ⚠️  BOM for {fg.code} already exists, skipping...")
            boms.append(existing)
            continue
        
        # Create BOM Header
        bom_header = BOMHeader(
            product_id=fg.id,
            bom_name=f"BOM-{fg.code}",
            version="1.0",
            is_active=True,
            notes=f"Standard BOM for {fg.name}"
        )
        db.add(bom_header)
        db.flush()
        
        print(f"\n✅ BOM for: {fg.code} - {fg.name}")
        
        # Create BOM Lines (use first 5-8 raw materials)
        materials_to_use = raw_materials[:8]  # First 8 materials
        
        for idx, material in enumerate(materials_to_use, start=1):
            # Varied quantities based on material type
            if material.uom == UOM.YARD:
                qty = Decimal("0.15")  # 0.15 yards per piece
            elif material.uom == UOM.KG:
                qty = Decimal("0.054")  # 54 grams = 0.054 kg
            elif material.uom == UOM.CONE:
                qty = Decimal("0.05")  # 5% of a cone
            else:
                qty = Decimal("1")  # 1 piece
            
            bom_line = BOMDetail(
                bom_header_id=bom_header.id,
                product_id=material.id,
                quantity=qty,
                sequence=idx,
                waste_percent=Decimal("5.0")  # 5% waste allowance
            )
            db.add(bom_line)
            print(f"   └─ {material.code}: {qty} {material.uom.value}")
        
        boms.append(bom_header)
    
    db.flush()
    print(f"\n✅ Total BOMs created: {len(boms)}")
    return boms


def create_locations(db: Session) -> List[Location]:
    """Create 5 warehouse locations."""
    print("\n" + "=" * 60)
    print("STEP 4: Creating Warehouse Locations")
    print("=" * 60)
    
    locations_data = [
        {"code": "WH-MAIN", "name": "Warehouse Main", "type": "MATERIAL"},
        {"code": "WH-FIN", "name": "Warehouse Finishing", "type": "WIP"},
        {"code": "WH-FG", "name": "Warehouse Finished Goods", "type": "FINISHED_GOODS"},
        {"code": "PROD-CUT", "name": "Production Cutting", "type": "PRODUCTION"},
        {"code": "PROD-SEW", "name": "Production Sewing", "type": "PRODUCTION"},
    ]
    
    locations = []
    for data in locations_data:
        existing = db.query(Location).filter(Location.code == data["code"]).first()
        if existing:
            print(f"   ⚠️  Location {data['code']} already exists, skipping...")
            locations.append(existing)
            continue
        
        location = Location(
            code=data["code"],
            name=data["name"],
            type=data["type"],
            is_active=True
        )
        db.add(location)
        locations.append(location)
        print(f"   ✅ {data['code']}: {data['name']}")
    
    db.flush()
    print(f"\n✅ Total locations: {len(locations)}")
    return locations


def create_stock(db: Session, products: List[Product], locations: List[Location]) -> None:
    """Create initial stock for products."""
    print("\n" + "=" * 60)
    print("STEP 5: Creating Initial Stock")
    print("=" * 60)
    
    # Get main warehouse location
    main_wh = next((loc for loc in locations if loc.code == "WH-MAIN"), None)
    if not main_wh:
        print("   ⚠️  Main warehouse not found, skipping stock creation")
        return
    
    stock_count = 0
    for product in products[:15]:  # Stock first 15 raw materials
        existing = db.query(StockQuant).filter(
            StockQuant.product_id == product.id,
            StockQuant.location_id == main_wh.id
        ).first()
        
        if existing:
            continue
        
        stock = StockQuant(
            product_id=product.id,
            location_id=main_wh.id,
            qty_on_hand=Decimal("1000"),  # Start with 1000 units
            qty_reserved=Decimal("0")
        )
        db.add(stock)
        stock_count += 1
        print(f"   ✅ {product.code}: 1000 {product.uom.value}")
    
    db.flush()
    print(f"\n✅ Total stock records: {stock_count}")


def create_manufacturing_orders(db: Session, finished_goods: List[Product]) -> List[ManufacturingOrder]:
    """Create 5 Manufacturing Orders."""
    print("\n" + "=" * 60)
    print("STEP 6: Creating Manufacturing Orders")
    print("=" * 60)
    
    mos = []
    batch_base = datetime.now().strftime("%Y%m%d")
    
    for idx, product in enumerate(finished_goods, start=1):
        batch_number = f"BATCH-{batch_base}-{idx:03d}"
        
        existing = db.query(ManufacturingOrder).filter(
            ManufacturingOrder.batch_number == batch_number
        ).first()
        
        if existing:
            print(f"\n   ⚠️  MO {batch_number} already exists, skipping...")
            mos.append(existing)
            continue
        
        # Alternate routing types
        if idx % 3 == 0:
            routing = RoutingType.ROUTE1  # Full process
        elif idx % 3 == 1:
            routing = RoutingType.ROUTE2  # Direct sewing
        else:
            routing = RoutingType.ROUTE3  # Subcon
        
        mo = ManufacturingOrder(
            product_id=product.id,
            qty_planned=Decimal(500 + (idx * 50)),  # 550, 600, 650, 700, 750
            qty_produced=Decimal(0),
            routing_type=routing.value,
            batch_number=batch_number,
            state=MOState.DRAFT,
            created_at=datetime.utcnow(),
            due_date=datetime.utcnow() + timedelta(days=14)
        )
        
        db.add(mo)
        db.flush()
        mos.append(mo)
        
        print(f"\n✅ MO #{mo.id}: {product.code}")
        print(f"   Batch: {batch_number}")
        print(f"   Qty: {mo.qty_planned} pcs")
        print(f"   Routing: {routing.value}")
        
        # Create Work Orders based on routing
        departments = []
        if routing == RoutingType.ROUTE1:
            departments = [Department.CUTTING, Department.EMBROIDERY, Department.SEWING, Department.FINISHING, Department.PACKING]
        elif routing == RoutingType.ROUTE2:
            departments = [Department.SEWING, Department.FINISHING, Department.PACKING]
        else:
            departments = [Department.FINISHING, Department.PACKING]
        
        for seq, dept in enumerate(departments, start=1):
            wo = WorkOrder(
                mo_id=mo.id,
                product_id=product.id,
                department=dept,
                sequence=seq,
                status=WorkOrderStatus.PENDING,
                input_qty=mo.qty_planned,
                output_qty=Decimal(0),
                reject_qty=Decimal(0),
                notes=f"Auto-generated for {dept.value}"
            )
            db.add(wo)
            print(f"   └─ WO {seq}: {dept.value}")
    
    db.flush()
    print(f"\n✅ Total MOs created: {len(mos)}")
    return mos


def main():
    """Main execution."""
    print("\n" + "=" * 60)
    print("COMPLETE SEED DATA CREATOR - SESSION 50")
    print("=" * 60)
    print("\nThis will create comprehensive test data:")
    print("  • 5 Suppliers")
    print("  • 25 Products (20 raw materials + 5 finished goods)")
    print("  • 5 BOMs with material breakdown")
    print("  • 5 Warehouse locations")
    print("  • Initial stock for 15 materials")
    print("  • 5 Manufacturing Orders")
    print("  • 15-20 Work Orders across departments")
    print("\n" + "=" * 60)
    
    db = SessionLocal()
    try:
        # Execute steps
        suppliers = create_suppliers(db)
        raw_materials, finished_goods = create_products(db)
        boms = create_boms(db, raw_materials, finished_goods)
        locations = create_locations(db)
        create_stock(db, raw_materials, locations)
        mos = create_manufacturing_orders(db, finished_goods)
        
        # Commit all
        db.commit()
        
        print("\n" + "=" * 60)
        print("✅ SUCCESS! ALL SEED DATA CREATED")
        print("=" * 60)
        
        print("\n📊 SUMMARY:")
        print(f"   Suppliers: {len(suppliers)}")
        print(f"   Raw Materials: {len(raw_materials)}")
        print(f"   Finished Goods: {len(finished_goods)}")
        print(f"   BOMs: {len(boms)}")
        print(f"   Locations: {len(locations)}")
        print(f"   Manufacturing Orders: {len(mos)}")
        
        total_wos = db.query(WorkOrder).filter(
            WorkOrder.mo_id.in_([mo.id for mo in mos])
        ).count()
        print(f"   Work Orders: {total_wos}")
        
        print("\n✅ Database is now populated with test data!")
        print("   You can test:")
        print("   1. Dashboard - View KPIs and metrics")
        print("   2. PPIC Page - See MOs and WOs")
        print("   3. Production Pages - Process WOs per department")
        print("   4. Warehouse - Check stock levels")
        print("   5. Masterdata - Browse products, suppliers, BOMs")
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    main()
