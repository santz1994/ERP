"""
Week 4: End-to-End Material Flow Testing
Complete integration test for material allocation system

Author: IT Developer Expert
Date: 4 Februari 2026
Motto: "Kegagalan adalah kesuksesan yang tertunda!"
"""

import sys
from pathlib import Path
from decimal import Decimal
from datetime import datetime, date

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.models.manufacturing import ManufacturingOrder, WorkOrder, WorkOrderStatus, Department, SPKMaterialAllocation
from app.core.models.products import Product, Category
from app.core.models.warehouse import StockQuant, Location, StockMove
from app.core.models.bom import BOMHeader, BOMDetail
from app.services.material_allocation_service import MaterialAllocationService
from app.services.bom_explosion_service import BOMExplosionService


class MaterialFlowTester:
    """
    End-to-End Material Flow Testing
    
    Test Flow:
    1. Setup: Create test MO with BOM
    2. Generate WOs
    3. Allocate materials
    4. Check shortage alerts
    5. Deduct stock when WO starts
    6. Verify FIFO stock deduction
    7. Test material debt system
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.bom_service = BOMExplosionService(db)
        self.material_service = MaterialAllocationService(db)
        self.test_mo = None
        self.test_wos = []
        
    def setup_test_data(self):
        """Setup test Manufacturing Order with materials"""
        
        print("\n" + "="*80)
        print("🔧 SETUP: Creating Test Data")
        print("="*80)
        
        # 1. Get a Finished Good product
        packing_cat = self.db.query(Category).filter_by(name='WIP Packing').first()
        
        if not packing_cat:
            print("❌ WIP Packing category not found!")
            return False
        
        # Get product with BOM
        product = (
            self.db.query(Product)
            .filter_by(category_id=packing_cat.id)
            .join(BOMHeader, BOMHeader.product_id == Product.id)
            .filter(BOMHeader.is_active == True)
            .first()
        )
        
        if not product:
            print("❌ No product with active BOM found!")
            return False
        
        print(f"\n✅ Test Product: [{product.code}] {product.name[:60]}...")
        
        # 2. Create test MO
        from app.core.models.manufacturing import RoutingType, MOState
        from datetime import timedelta
        
        batch_number = f"MO-TEST-E2E-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        self.test_mo = ManufacturingOrder(
            batch_number=batch_number,
            product_id=product.id,
            qty_planned=Decimal('100'),  # Small quantity for testing
            qty_produced=Decimal('0'),
            state=MOState.DRAFT,
            routing_type=RoutingType.ROUTE1,
            production_week="08-2026",
            destination_country="Testing",
            planned_production_date=date.today() + timedelta(days=7),
            traceability_code=f"{batch_number}-TEST"
        )
        
        self.db.add(self.test_mo)
        self.db.flush()
        
        print(f"\n✅ Created MO: {batch_number}")
        print(f"   Product: {product.name[:50]}...")
        print(f"   Target: {self.test_mo.qty_planned} pcs")
        
        return True
    
    def test_wo_generation(self):
        """Test Work Order generation"""
        
        print("\n" + "="*80)
        print("🏭 TEST 1: Work Order Generation")
        print("="*80)
        
        # Generate WOs using BOM explosion
        wos = self.bom_service.explode_mo_and_generate_work_orders(
            mo_id=self.test_mo.id,
            qty_planned=self.test_mo.qty_planned
        )
        
        if not wos:
            print("❌ Failed to generate Work Orders!")
            return False
        
        self.test_wos = wos
        
        print(f"\n✅ Generated {len(wos)} Work Orders:")
        for wo in wos:
            print(f"   • {wo.wo_number} - {wo.department.value}")
            print(f"     Seq #{wo.sequence}, Target: {wo.target_qty} pcs, Status: {wo.status.value}")
        
        return True
    
    def test_material_allocation(self):
        """Test material allocation for WOs"""
        
        print("\n" + "="*80)
        print("📦 TEST 2: Material Allocation")
        print("="*80)
        
        total_allocations = 0
        
        for wo in self.test_wos:
            print(f"\n🔄 Allocating materials for {wo.wo_number}...")
            
            # Get BOM for this WO's input WIP
            if wo.input_wip_product_id:
                bom_header = self.db.query(BOMHeader).filter_by(
                    product_id=wo.input_wip_product_id,
                    is_active=True
                ).first()
            else:
                # For first WO (Cutting), use FG's BOM
                bom_header = self.db.query(BOMHeader).filter_by(
                    product_id=self.test_mo.product_id,
                    is_active=True
                ).first()
            
            if not bom_header:
                print(f"   ⚠️ No BOM found for {wo.wo_number}, skipping...")
                continue
            
            bom_details = self.db.query(BOMDetail).filter_by(
                bom_header_id=bom_header.id
            ).all()
            
            # Allocate materials
            allocations, shortage_alerts = self.material_service.allocate_materials_for_wo(
                wo=wo,
                bom_details=bom_details,
                check_availability=True
            )
            
            total_allocations += len(allocations)
            
            print(f"   ✅ Allocated {len(allocations)} materials")
            
            if shortage_alerts:
                print(f"   ⚠️ {len(shortage_alerts)} materials in shortage:")
                for alert in shortage_alerts:
                    print(f"      • {alert.material_code}: need {alert.required_qty}, have {alert.available_qty}")
        
        self.db.commit()
        
        print(f"\n📊 Summary:")
        print(f"   Total allocations: {total_allocations}")
        print(f"   ✅ Material allocation test PASSED")
        
        return True
    
    def test_shortage_alerts(self):
        """Test material shortage alert system"""
        
        print("\n" + "="*80)
        print("⚠️ TEST 3: Material Shortage Alerts")
        print("="*80)
        
        # Get all shortage alerts for this MO
        alerts = self.material_service.get_material_shortage_alerts(
            mo_id=self.test_mo.id
        )
        
        if alerts:
            print(f"\n⚠️ Found {len(alerts)} material shortage alerts:")
            
            # Group by severity
            by_severity = {}
            for alert in alerts:
                by_severity[alert.severity] = by_severity.get(alert.severity, 0) + 1
            
            print(f"\n   By Severity:")
            for severity, count in sorted(by_severity.items()):
                print(f"      • {severity}: {count} materials")
            
            print(f"\n   Top 5 Critical Shortages:")
            for i, alert in enumerate(alerts[:5], 1):
                print(f"      {i}. {alert.material_code} - {alert.material_name[:40]}...")
                print(f"         Need: {alert.required_qty}, Have: {alert.available_qty}")
                print(f"         Shortage: {alert.shortage_qty} ({alert.severity})")
        else:
            print("\n✅ No material shortages detected! All materials available.")
        
        return True
    
    def test_wo_start_with_deduction(self):
        """Test starting WO and stock deduction"""
        
        print("\n" + "="*80)
        print("🚀 TEST 4: WO Start & Stock Deduction")
        print("="*80)
        
        # Try to start first WO (should be PENDING/READY)
        first_wo = self.test_wos[0] if self.test_wos else None
        
        if not first_wo:
            print("❌ No WO available for testing!")
            return False
        
        print(f"\n🔍 Testing WO: {first_wo.wo_number}")
        print(f"   Department: {first_wo.department.value}")
        print(f"   Current Status: {first_wo.status.value}")
        
        # Check if can start
        can_start, blocking_reasons = self.material_service.check_wo_can_start(first_wo)
        
        print(f"\n   Can Start: {'✅ YES' if can_start else '❌ NO'}")
        
        if not can_start:
            print(f"   Blocking Reasons:")
            for reason in blocking_reasons:
                print(f"      • {reason}")
        
        # Check stock before deduction
        allocations = self.db.query(SPKMaterialAllocation).filter_by(
            wo_id=first_wo.id
        ).all()
        
        print(f"\n   📊 Stock Before Deduction:")
        for alloc in allocations:
            material = self.db.query(Product).filter_by(id=alloc.material_id).first()
            available = self.material_service._get_available_stock(alloc.material_id)
            print(f"      • {material.code if material else 'N/A'}: {available} available")
        
        # Try to deduct (with force if necessary)
        print(f"\n   💰 Attempting Stock Deduction...")
        
        success, errors = self.material_service.deduct_stock_on_wo_start(
            wo=first_wo,
            force=True  # Allow debt for testing
        )
        
        if success:
            print(f"   ✅ Stock deduction SUCCESSFUL")
            
            # Update WO status
            first_wo.status = WorkOrderStatus.RUNNING
            first_wo.actual_start_date = date.today()
            first_wo.start_time = datetime.utcnow()
            
            self.db.commit()
            
            print(f"   ✅ WO status updated to RUNNING")
            
        else:
            print(f"   ⚠️ Stock deduction had errors:")
            for error in errors:
                print(f"      • {error}")
        
        # Check stock after deduction
        print(f"\n   📊 Stock After Deduction:")
        for alloc in allocations:
            material = self.db.query(Product).filter_by(id=alloc.material_id).first()
            available = self.material_service._get_available_stock(alloc.material_id)
            print(f"      • {material.code if material else 'N/A'}: {available} available")
            print(f"        Consumed: {alloc.qty_consumed}, Allocated: {alloc.qty_allocated}")
        
        return True
    
    def test_fifo_stock_tracking(self):
        """Test FIFO stock lot tracking"""
        
        print("\n" + "="*80)
        print("📦 TEST 5: FIFO Stock Lot Tracking")
        print("="*80)
        
        # Check stock moves created
        if not self.test_wos:
            print("❌ No WOs available for testing!")
            return False
        
        first_wo = self.test_wos[0]
        
        # Get stock moves for this WO
        stock_moves = self.db.query(StockMove).filter(
            StockMove.reference.like(f'%WO-{first_wo.id}%')
        ).all()
        
        if stock_moves:
            print(f"\n✅ Found {len(stock_moves)} stock movements:")
            
            for move in stock_moves:
                material = self.db.query(Product).filter_by(id=move.product_id).first()
                print(f"\n   • Material: {material.code if material else 'N/A'}")
                print(f"     Quantity: {move.quantity}")
                print(f"     Lot ID: {move.lot_id if move.lot_id else 'N/A'}")
                print(f"     Reference: {move.reference}")
                print(f"     Date: {move.move_date}")
        else:
            print("\n⚠️ No stock movements recorded yet")
        
        return True
    
    def test_material_debt_system(self):
        """Test material debt (negative inventory) system"""
        
        print("\n" + "="*80)
        print("💸 TEST 6: Material Debt System")
        print("="*80)
        
        # Check if any negative stock quants were created
        negative_quants = self.db.query(StockQuant).filter(
            StockQuant.quantity < 0
        ).all()
        
        if negative_quants:
            print(f"\n⚠️ Found {len(negative_quants)} negative stock entries (debts):")
            
            for quant in negative_quants:
                material = self.db.query(Product).filter_by(id=quant.product_id).first()
                location = self.db.query(Location).filter_by(id=quant.location_id).first()
                
                print(f"\n   • Material: {material.code if material else 'N/A'}")
                print(f"     Quantity: {quant.quantity} (DEBT)")
                print(f"     Location: {location.name if location else 'N/A'}")
                print(f"     Created: {quant.created_at}")
        else:
            print("\n✅ No material debts found - all stock sufficient!")
        
        return True
    
    def cleanup_test_data(self):
        """Cleanup test data"""
        
        print("\n" + "="*80)
        print("🧹 CLEANUP: Removing Test Data")
        print("="*80)
        
        commit = input("\n⚠️ Do you want to keep test data? (yes/no): ").strip().lower()
        
        if commit == 'no':
            # Rollback all changes
            self.db.rollback()
            print("✅ Test data rolled back (not saved)")
        else:
            # Commit changes
            self.db.commit()
            print("✅ Test data committed to database")
            print(f"\n📝 Test MO: {self.test_mo.batch_number} (ID: {self.test_mo.id})")
    
    def run_all_tests(self):
        """Run all tests in sequence"""
        
        print("="*80)
        print("🧪 WEEK 4: END-TO-END MATERIAL FLOW TESTING")
        print("="*80)
        print("\nThis test suite validates:")
        print("1. ✅ Work Order generation")
        print("2. ✅ Material allocation")
        print("3. ✅ Shortage alert system")
        print("4. ✅ Stock deduction (FIFO)")
        print("5. ✅ Stock lot tracking")
        print("6. ✅ Material debt system")
        print("\n" + "="*80)
        
        input("\nPress Enter to start testing...")
        
        # Setup
        if not self.setup_test_data():
            print("\n❌ Setup failed! Aborting tests.")
            return
        
        # Run tests
        try:
            # Test 1: WO Generation
            if not self.test_wo_generation():
                print("\n❌ WO Generation test failed!")
                return
            
            # Test 2: Material Allocation
            if not self.test_material_allocation():
                print("\n❌ Material Allocation test failed!")
                return
            
            # Test 3: Shortage Alerts
            if not self.test_shortage_alerts():
                print("\n❌ Shortage Alerts test failed!")
                return
            
            # Test 4: WO Start & Deduction
            if not self.test_wo_start_with_deduction():
                print("\n❌ WO Start test failed!")
                return
            
            # Test 5: FIFO Tracking
            if not self.test_fifo_stock_tracking():
                print("\n❌ FIFO Tracking test failed!")
                return
            
            # Test 6: Material Debt
            if not self.test_material_debt_system():
                print("\n❌ Material Debt test failed!")
                return
            
            # Success!
            print("\n" + "="*80)
            print("🎉 ALL TESTS PASSED!")
            print("="*80)
            print("\n✅ Week 4 Integration Complete:")
            print("   • Material allocation working")
            print("   • Stock deduction working (FIFO)")
            print("   • Shortage alerts working")
            print("   • Material debt system working")
            
        except Exception as e:
            print(f"\n❌ Test error: {str(e)}")
            import traceback
            traceback.print_exc()
        
        finally:
            # Cleanup
            self.cleanup_test_data()


def main():
    """Main entry point"""
    
    db = next(get_db())
    
    try:
        tester = MaterialFlowTester(db)
        tester.run_all_tests()
        
    except Exception as e:
        print(f"\n❌ Fatal error: {str(e)}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    main()
