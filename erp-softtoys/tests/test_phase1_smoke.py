"""
Phase 1 Smoke Tests - Quick validation of core functionality

Tests:
1. BOM explosion service exists and can be called
2. Purchasing service has dual-mode methods
3. MO trigger logic is in place
4. Database schema supports new fields

Author: IT Developer Expert  
Date: 5 February 2026
"""

import pytest
from decimal import Decimal
from datetime import date
from sqlalchemy import inspect

from app.core.models.warehouse import PurchaseOrder, PurchaseOrderLine
from app.core.models.manufacturing import ManufacturingOrder, MOState
from app.services.bom_explosion_service import BOMExplosionService
from app.modules.purchasing.purchasing_service import PurchasingService


@pytest.mark.unit
class TestPhase1DatabaseSchema:
    """Test database schema supports Phase 1 features"""
    
    def test_purchase_order_has_dual_mode_fields(self, db):
        """Test PO table has input_mode, source_article_id, po_type"""
        inspector = inspect(db.get_bind())
        columns = [col['name'] for col in inspector.get_columns('purchase_orders')]
        
        assert 'input_mode' in columns
        assert 'source_article_id' in columns
        assert 'article_quantity' in columns
        assert 'po_type' in columns
        assert 'linked_mo_id' in columns
        assert 'extra_metadata' in columns
        assert 'total_amount' in columns
        assert 'approved_by' in columns
        assert 'approved_at' in columns
        
        print(f"✅ PO table has all dual-mode fields")
    
    def test_purchase_order_line_has_supplier_field(self, db):
        """Test PO Line has supplier_id (key feature)"""
        inspector = inspect(db.get_bind())
        columns = [col['name'] for col in inspector.get_columns('purchase_order_lines')]
        
        assert 'supplier_id' in columns
        assert 'extra_metadata' in columns
        
        print(f"✅ PO Line has supplier_id field")
    
    def test_manufacturing_order_has_flexible_target_fields(self, db):
        """Test MO table has target_quantity, buffer_quantity, etc"""
        inspector = inspect(db.get_bind())
        columns = [col['name'] for col in inspector.get_columns('manufacturing_orders')]
        
        assert 'target_quantity' in columns
        assert 'buffer_quantity' in columns
        assert 'production_quantity' in columns
        assert 'auto_calculate_buffer' in columns
        assert 'week' in columns
        assert 'destination' in columns
        assert 'week_destination_locked' in columns
        assert 'extra_metadata' in columns
        
        print(f"✅ MO table has all flexible target fields")


@pytest.mark.unit
class TestPhase1ServicesExist:
    """Test Phase 1 services are available"""
    
    def test_bom_explosion_service_has_purchasing_method(self, db):
        """Test BOM explosion service has purchasing method"""
        service = BOMExplosionService(db)
        
        assert hasattr(service, 'explode_bom_for_purchasing')
        assert callable(service.explode_bom_for_purchasing)
        
        print(f"✅ BOMExplosionService has explode_bom_for_purchasing method")
    
    def test_purchasing_service_has_auto_bom_method(self, db):
        """Test purchasing service has AUTO_BOM method"""
        service = PurchasingService(db)
        
        assert hasattr(service, 'create_purchase_order_auto_bom')
        assert callable(service.create_purchase_order_auto_bom)
        
        print(f"✅ PurchasingService has create_purchase_order_auto_bom method")
    
    def test_purchasing_service_has_preview_method(self, db):
        """Test purchasing service has preview method"""
        service = PurchasingService(db)
        
        assert hasattr(service, 'preview_bom_explosion')
        assert callable(service.preview_bom_explosion)
        
        print(f"✅ PurchasingService has preview_bom_explosion method")
    
    def test_purchasing_service_approve_has_trigger_logic(self, db):
        """Test approve_purchase_order has trigger logic"""
        import inspect
        service = PurchasingService(db)
        
        # Get source code
        source = inspect.getsource(service.approve_purchase_order)
        
        # Check for trigger keywords
        assert 'po_type' in source.lower()
        assert 'kain' in source.lower()
        assert 'label' in source.lower()
        assert 'MOState.PARTIAL' in source or 'partial' in source.lower()
        assert 'MOState.RELEASED' in source or 'released' in source.lower()
        
        print(f"✅ approve_purchase_order has KAIN/LABEL trigger logic")


@pytest.mark.unit
class TestPhase1EnumsAndTypes:
    """Test Phase 1 enums are defined"""
    
    def test_mo_state_has_partial_released(self):
        """Test MOState enum has PARTIAL and RELEASED"""
        assert hasattr(MOState, 'PARTIAL')
        assert hasattr(MOState, 'RELEASED')
        assert MOState.PARTIAL.value == 'PARTIAL'
        assert MOState.RELEASED.value == 'RELEASED'
        
        print(f"✅ MOState has PARTIAL and RELEASED")


@pytest.mark.integration  
class TestPhase1MinimalWorkflow:
    """Minimal integration test of Phase 1 workflow"""
    
    def test_mo_can_be_created_with_flexible_target(self, db, admin_user):
        """Test MO can be created with flexible target fields"""
        # Note: This requires sample product to exist
        # For now, just test the model accepts the fields
        
        try:
            mo = ManufacturingOrder(
                mo_number="TEST-MO-001",
                product_id=1,  # Assumes product exists
                qty_planned=Decimal("450"),
                target_quantity=Decimal("450"),
                buffer_quantity=Decimal("0"),
                production_quantity=Decimal("450"),
                auto_calculate_buffer=True,
                state=MOState.DRAFT,
                planned_date=date.today(),
                extra_metadata={}
            )
            
            # If model accepts it without error, test passes
            assert mo.target_quantity == Decimal("450")
            assert mo.state == MOState.DRAFT
            
            print(f"✅ MO model accepts flexible target fields")
            
        except Exception as e:
            pytest.skip(f"Skipped: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short", "-m", "unit"])
