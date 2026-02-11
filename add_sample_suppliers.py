"""Add sample suppliers to Partners table for testing."""
import sys
from pathlib import Path

# Add erp-softtoys to sys.path
sys.path.insert(0, str(Path(__file__).parent / "erp-softtoys"))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.models.products import Partner, PartnerType

# Database connection
DATABASE_URL = "postgresql://postgres:SantZ1994--@localhost:5432/erp_quty_karunia"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def add_suppliers():
    db = SessionLocal()
    try:
        # Check existing suppliers
        existing = db.query(Partner).filter(Partner.type == PartnerType.SUPPLIER).count()
        print(f"📊 Existing suppliers: {existing}")
        
        if existing > 0:
            print("✅ Suppliers already exist. Skipping...")
            return
        
        # Sample suppliers for soft toys manufacturing
        suppliers_data = [
            {
                "name": "PT Kain Berkah - Fabric Supplier",
                "type": PartnerType.SUPPLIER,
                "address": "Jl. Industri No. 45, Bandung, Jawa Barat",
                "contact_person": "Budi Santoso",
                "phone": "+62-22-7234567",
                "email": "budi@kainberkah.co.id"
            },
            {
                "name": "CV Label Sejahtera - Label Supplier",
                "type": PartnerType.SUPPLIER,
                "address": "Jl. Raya Cikarang No. 12, Bekasi, Jawa Barat",
                "contact_person": "Siti Aminah",
                "phone": "+62-21-89012345",
                "email": "siti@labelsejahtera.co.id"
            },
            {
                "name": "PT Aksesori Prima - Accessories Supplier",
                "type": PartnerType.SUPPLIER,
                "address": "Jl. Gatot Subroto No. 78, Jakarta Selatan",
                "contact_person": "Ahmad Rizki",
                "phone": "+62-21-5234567",
                "email": "ahmad@aksesoripri ma.co.id"
            },
            {
                "name": "CV Benang Jaya - Thread Supplier",
                "type": PartnerType.SUPPLIER,
                "address": "Jl. Soekarno Hatta No. 90, Surabaya, Jawa Timur",
                "contact_person": "Dewi Lestari",
                "phone": "+62-31-7123456",
                "email": "dewi@benangjaya.co.id"
            },
            {
                "name": "PT Packaging Makmur - Packaging Supplier",
                "type": PartnerType.SUPPLIER,
                "address": "Jl. Raya Bogor KM 25, Cibinong, Jawa Barat",
                "contact_person": "Eko Prasetyo",
                "phone": "+62-21-87654321",
                "email": "eko@packagingmakmur.co.id"
            }
        ]
        
        # Insert suppliers
        for data in suppliers_data:
            supplier = Partner(**data)
            db.add(supplier)
        
        db.commit()
        print(f"✅ Added {len(suppliers_data)} sample suppliers")
        
        # Verify
        all_suppliers = db.query(Partner).filter(Partner.type == PartnerType.SUPPLIER).all()
        print("\n📋 Suppliers in database:")
        for s in all_suppliers:
            print(f"   - {s.name} (ID: {s.id})")
    
    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    print("🚀 Adding sample suppliers...")
    add_suppliers()
    print("\n✅ DONE! Suppliers ready for testing.")
