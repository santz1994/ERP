"""
Initialize Database - Create all tables
Usage: python init_db.py
"""
from app.core.database import engine, Base
from app.core.models import *  # Import all models

def init_database():
    """Create all database tables"""
    try:
        print("\n" + "="*70)
        print("INITIALIZING DATABASE")
        print("="*70 + "\n")
        
        print("Creating all tables...")
        Base.metadata.create_all(bind=engine)
        
        print("\n✅ Database initialized successfully!")
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    init_database()
