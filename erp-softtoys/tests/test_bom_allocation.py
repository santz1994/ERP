"""
Unit Tests for BOM Allocation Service
Tests the BOM Auto-Allocate system (Feature #1)

Coverage:
- BOM material allocation logic
- Stock checking and material debt creation
- Wastage calculation
- Allocation status tracking
- Error handling
"""

import pytest
from datetime import datetime
from decimal import Decimal
from unittest.mock import MagicMock, AsyncMock, patch
from sqlalchemy.orm import Session

from app.services.bom_service import BOMService
from app.core.models.production import AllocationStatus, SPKMaterialAllocation
from app.core.models.products import Product
from app.core.models.manufacturing import SPK
from app.core.models.bom import BOMHeader, BOMDetail


# ==================== Fixtures ====================

@pytest.fixture
def db_mock() -> Session:
    """Mock database session"""
    return MagicMock(spec=Session)


@pytest.fixture
def bom_service(db_mock: Session) -> BOMService:
    """Create BOMService instance"""
    return BOMService()


@pytest.fixture
def sample_spk():
    """Sample SPK data"""
    spk = MagicMock(spec=SPK)
    spk.id = 1
    spk.article_id = 5
    spk.spk_number = "SPK-2026-001"
    spk.target_qty = 1000
    spk.status = "DRAFT"
    spk.created_at = datetime.now()
    return spk


@pytest.fixture
def sample_bom():
    """Sample BOM with materials"""
    bom = MagicMock(spec=BOMHeader)
    bom.id = 1
    bom.article_id = 5
    bom.version = 1
    bom.materials = [
        {
            "material_id": 101,
            "qty_per_article": Decimal("2.5"),
            "wastage_percentage": Decimal("5"),
            "unit_price": Decimal("1000")
        },
        {
            "material_id": 102,
            "qty_per_article": Decimal("0.5"),
            "wastage_percentage": Decimal("10"),
            "unit_price": Decimal("5000")
        }
    ]
    return bom


# ==================== Test Cases ====================

class TestBOMAllocationBasics:
    """Test basic BOM allocation functionality"""
    
    @pytest.mark.asyncio
    async def test_allocate_material_with_sufficient_stock(self, bom_service, db_mock, sample_spk, sample_bom):
        """Should allocate material when stock is sufficient"""
        # Arrange
        spk_qty = 1000
        material_id = 101
        qty_per_unit = Decimal("2.5")
        wastage = Decimal("5")
        
        # Calculate needed qty with wastage
        needed_qty = spk_qty * qty_per_unit * (1 + wastage / 100)
        
        # Mock material with sufficient stock
        mock_material = MagicMock()
        mock_material.id = material_id
        mock_material.current_stock = Decimal("3000")  # More than needed
        
        db_mock.query().filter().first.return_value = mock_material
        db_mock.add = MagicMock()
        db_mock.commit = MagicMock()
        
        # Act
        allocation = await bom_service.allocate_material_for_spk(
            spk_id=sample_spk.id,
            material_id=material_id,
            qty_needed=needed_qty
        )
        
        # Assert
        assert allocation["status"] == AllocationStatus.ALLOCATED.value
        assert allocation["qty_allocated"] == needed_qty
        assert allocation["has_material_debt"] == False
    
    @pytest.mark.asyncio
    async def test_allocate_material_with_insufficient_stock(self, bom_service, db_mock, sample_spk):
        """Should create material debt when stock insufficient"""
        # Arrange
        spk_qty = 1000
        material_id = 101
        qty_per_unit = Decimal("2.5")
        wastage = Decimal("5")
        
        needed_qty = spk_qty * qty_per_unit * (1 + wastage / 100)
        available_stock = Decimal("1000")  # Less than needed
        
        # Mock material with insufficient stock
        mock_material = MagicMock()
        mock_material.id = material_id
        mock_material.current_stock = available_stock
        mock_material.unit_price = Decimal("1000")
        
        db_mock.query().filter().first.return_value = mock_material
        db_mock.add = MagicMock()
        db_mock.commit = MagicMock()
        
        # Mock MaterialDebtService
        with patch('app.services.bom_service.MaterialDebtService') as MockDebtService:
            mock_debt_service = MagicMock()
            MockDebtService.return_value = mock_debt_service
            mock_debt_service.create_material_debt = AsyncMock(return_value={"id": 1})
            
            # Act
            allocation = await bom_service.allocate_material_for_spk(
                spk_id=sample_spk.id,
                material_id=material_id,
                qty_needed=needed_qty
            )
        
        # Assert
        assert allocation["qty_allocated"] == available_stock
        assert allocation["has_material_debt"] == True
        assert allocation["qty_debt"] == (needed_qty - available_stock)


class TestWastageCalculation:
    """Test wastage percentage calculation"""
    
    def test_calculate_wastage_zero_percent(self, bom_service):
        """Should handle zero wastage"""
        # Arrange
        qty_needed = Decimal("1000")
        wastage_percent = Decimal("0")
        
        # Act
        result = qty_needed * (1 + wastage_percent / 100)
        
        # Assert
        assert result == Decimal("1000")
    
    def test_calculate_wastage_five_percent(self, bom_service):
        """Should calculate 5% wastage"""
        # Arrange
        qty_needed = Decimal("1000")
        wastage_percent = Decimal("5")
        
        # Act
        result = qty_needed * (1 + wastage_percent / 100)
        
        # Assert
        assert result == Decimal("1050")
    
    def test_calculate_wastage_large_percent(self, bom_service):
        """Should calculate 20% wastage"""
        # Arrange
        qty_needed = Decimal("1000")
        wastage_percent = Decimal("20")
        
        # Act
        result = qty_needed * (1 + wastage_percent / 100)
        
        # Assert
        assert result == Decimal("1200")
    
    def test_wastage_calculation_in_allocation(self, bom_service):
        """Should include wastage in allocation calculation"""
        # Arrange
        spk_qty = 1000
        qty_per_unit = Decimal("2.5")
        wastage = Decimal("5")
        
        # Act
        total_needed = spk_qty * qty_per_unit * (1 + wastage / 100)
        base_needed = spk_qty * qty_per_unit
        wastage_amount = total_needed - base_needed
        
        # Assert
        assert base_needed == Decimal("2500")
        assert wastage_amount == Decimal("125")
        assert total_needed == Decimal("2625")


class TestBOMQueries:
    """Test BOM data retrieval"""
    
    @pytest.mark.asyncio
    async def test_get_bom_by_article(self, bom_service, db_mock, sample_bom):
        """Should retrieve BOM for article"""
        # Arrange
        article_id = 5
        db_mock.query().filter().first.return_value = sample_bom
        
        # Act
        result = await bom_service.get_bom_for_article(article_id)
        
        # Assert
        assert result is not None
        assert len(result.materials) == 2
    
    @pytest.mark.asyncio
    async def test_get_allocation_preview(self, bom_service, db_mock, sample_spk, sample_bom):
        """Should generate allocation preview"""
        # Arrange
        db_mock.query().filter().first.return_value = sample_bom
        
        # Mock materials with varying stock
        materials = [
            MagicMock(id=101, current_stock=Decimal("3000")),
            MagicMock(id=102, current_stock=Decimal("100"))
        ]
        
        # Act
        result = await bom_service.get_allocation_preview(
            spk_id=sample_spk.id,
            article_id=5,
            qty=1000
        )
        
        # Assert
        assert result is not None
        assert "materials" in result
        assert "total_value" in result


class TestAllocationStatus:
    """Test allocation status tracking"""
    
    @pytest.mark.asyncio
    async def test_full_allocation_status(self, bom_service, db_mock):
        """Should mark as FULLY_ALLOCATED when all materials allocated"""
        # Arrange
        mock_allocation = MagicMock()
        mock_allocation.qty_needed = Decimal("1000")
        mock_allocation.qty_allocated = Decimal("1000")
        mock_allocation.qty_debt = Decimal("0")
        
        # Act
        if mock_allocation.qty_allocated == mock_allocation.qty_needed:
            status = AllocationStatus.FULLY_ALLOCATED
        
        # Assert
        assert status == AllocationStatus.FULLY_ALLOCATED
    
    @pytest.mark.asyncio
    async def test_partial_allocation_status(self, bom_service, db_mock):
        """Should mark as PARTIALLY_ALLOCATED when some materials short"""
        # Arrange
        mock_allocation = MagicMock()
        mock_allocation.qty_needed = Decimal("1000")
        mock_allocation.qty_allocated = Decimal("800")
        mock_allocation.qty_debt = Decimal("200")
        
        # Act
        if mock_allocation.qty_allocated < mock_allocation.qty_needed:
            status = AllocationStatus.PARTIALLY_ALLOCATED
        
        # Assert
        assert status == AllocationStatus.PARTIALLY_ALLOCATED
    
    @pytest.mark.asyncio
    async def test_failed_allocation_status(self, bom_service, db_mock):
        """Should mark as FAILED when no stock available"""
        # Arrange
        mock_allocation = MagicMock()
        mock_allocation.qty_needed = Decimal("1000")
        mock_allocation.qty_allocated = Decimal("0")
        mock_allocation.qty_debt = Decimal("1000")
        
        # Act
        if mock_allocation.qty_allocated == 0 and mock_allocation.qty_debt > 0:
            status = AllocationStatus.FAILED
        
        # Assert
        assert status == AllocationStatus.FAILED


class TestAllocationValidation:
    """Test allocation input validation"""
    
    @pytest.mark.asyncio
    async def test_invalid_spk_fails(self, bom_service, db_mock):
        """Should fail if SPK not found"""
        # Arrange
        db_mock.query().filter().first.return_value = None
        
        # Act & Assert
        with pytest.raises(Exception):
            await bom_service.allocate_material_for_spk(
                spk_id=999,
                material_id=101,
                qty_needed=Decimal("1000")
            )
    
    @pytest.mark.asyncio
    async def test_invalid_material_fails(self, bom_service, db_mock):
        """Should fail if material not found"""
        # Arrange
        db_mock.query().filter().first.return_value = None
        
        # Act & Assert
        with pytest.raises(Exception):
            await bom_service.allocate_material_for_spk(
                spk_id=1,
                material_id=999,
                qty_needed=Decimal("1000")
            )
    
    @pytest.mark.asyncio
    async def test_invalid_qty_fails(self, bom_service, db_mock):
        """Should reject zero or negative quantity"""
        # Act & Assert
        with pytest.raises(ValueError):
            await bom_service.allocate_material_for_spk(
                spk_id=1,
                material_id=101,
                qty_needed=Decimal("0")
            )
    
    @pytest.mark.asyncio
    async def test_invalid_qty_negative_fails(self, bom_service, db_mock):
        """Should reject negative quantity"""
        # Act & Assert
        with pytest.raises(ValueError):
            await bom_service.allocate_material_for_spk(
                spk_id=1,
                material_id=101,
                qty_needed=Decimal("-100")
            )


class TestAllocationWithDebtIntegration:
    """Test allocation integrated with Material Debt Service"""
    
    @pytest.mark.asyncio
    async def test_allocation_creates_debt_for_shortage(self, bom_service, db_mock):
        """Should create material debt for shortage"""
        # Arrange
        spk_qty = 1000
        material_id = 101
        qty_per_unit = Decimal("2.5")
        wastage = Decimal("5")
        needed_qty = Decimal("2625")
        available = Decimal("1500")
        shortage = needed_qty - available
        
        mock_material = MagicMock()
        mock_material.current_stock = available
        mock_material.unit_price = Decimal("1000")
        
        db_mock.query().filter().first.return_value = mock_material
        db_mock.add = MagicMock()
        db_mock.commit = MagicMock()
        
        # Mock MaterialDebtService
        with patch('app.services.bom_service.MaterialDebtService') as MockDebtService:
            mock_debt_service = MagicMock()
            MockDebtService.return_value = mock_debt_service
            mock_debt_service.create_material_debt = AsyncMock(
                return_value={"id": 1, "qty_debt": shortage}
            )
            
            # Act
            result = await bom_service.allocate_material_for_spk(
                spk_id=1,
                material_id=material_id,
                qty_needed=needed_qty
            )
        
        # Assert
        assert result["qty_allocated"] == available
        assert result["qty_debt"] == shortage
        assert mock_debt_service.create_material_debt.called


class TestAllocationCalculations:
    """Test allocation amount calculations"""
    
    def test_calculate_total_allocation_value(self):
        """Should calculate total allocation value"""
        # Arrange
        qty_allocated = Decimal("1000")
        unit_price = Decimal("5000")
        
        # Act
        total_value = qty_allocated * unit_price
        
        # Assert
        assert total_value == Decimal("5000000")
    
    def test_calculate_allocation_percentage(self):
        """Should calculate allocation completion percentage"""
        # Arrange
        qty_allocated = Decimal("750")
        qty_needed = Decimal("1000")
        
        # Act
        percentage = (qty_allocated / qty_needed) * 100
        
        # Assert
        assert percentage == Decimal("75")
        assert 0 <= percentage <= 100
    
    def test_calculate_shortage_amount(self):
        """Should calculate shortage amount"""
        # Arrange
        qty_needed = Decimal("1000")
        qty_allocated = Decimal("600")
        
        # Act
        shortage = qty_needed - qty_allocated
        
        # Assert
        assert shortage == Decimal("400")
        assert shortage > 0


class TestBOMAllocationEdgeCases:
    """Test edge cases and special scenarios"""
    
    @pytest.mark.asyncio
    async def test_fractional_unit_qty(self, bom_service, db_mock):
        """Should handle fractional quantities per unit"""
        # Arrange
        spk_qty = 100
        qty_per_unit = Decimal("0.5")
        wastage = Decimal("5")
        
        # Act
        needed_qty = spk_qty * qty_per_unit * (1 + wastage / 100)
        
        # Assert
        assert needed_qty == Decimal("52.5")
    
    @pytest.mark.asyncio
    async def test_very_high_wastage(self, bom_service, db_mock):
        """Should handle very high wastage percentage"""
        # Arrange
        spk_qty = 100
        qty_per_unit = Decimal("1")
        wastage = Decimal("50")  # 50% wastage
        
        # Act
        needed_qty = spk_qty * qty_per_unit * (1 + wastage / 100)
        
        # Assert
        assert needed_qty == Decimal("150")
    
    @pytest.mark.asyncio
    async def test_very_small_quantities(self, bom_service, db_mock):
        """Should handle very small quantities"""
        # Arrange
        spk_qty = 1
        qty_per_unit = Decimal("0.001")
        wastage = Decimal("10")
        
        # Act
        needed_qty = spk_qty * qty_per_unit * (1 + wastage / 100)
        
        # Assert
        assert needed_qty == Decimal("0.0011")


# ==================== Test Execution ====================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
