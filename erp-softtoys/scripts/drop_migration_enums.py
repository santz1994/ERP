"""Drop existing enum types if they exist (for fresh migration)"""
from sqlalchemy import create_engine, text
from app.core.config import settings

def drop_enums():
    """Drop existing enum types to allow fresh migration"""
    engine = create_engine(settings.DATABASE_URL)
    
    enums_to_drop = [
        'spk_material_allocation_status',
        'work_order_status'
    ]
    
    with engine.connect() as conn:
        for enum_name in enums_to_drop:
            try:
                print(f"Dropping enum type: {enum_name}...")
                conn.execute(text(f"DROP TYPE IF EXISTS {enum_name} CASCADE"))
                print(f"  ✅ {enum_name} dropped")
            except Exception as e:
                print(f"  ⚠️  Could not drop {enum_name}: {e}")
        
        conn.commit()
        print("\n✅ All enums dropped successfully!")

if __name__ == '__main__':
    drop_enums()
