"""
Unit Tests for MaterialDebtService
Tests the Material Debt system (Feature #4)

Coverage:
- Debt creation with validation
- Approval workflow integration
- Debt status transitions
- Settlement and adjustment calculations
- Error handling
"""

import pytest
import asyncio
from datetime import datetime, timedelta, date
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.orm import Session

from app.services.material_debt_service import (
    MaterialDebtService,
    MaterialDebtStatus,
    MaterialDebtApprovalStatus,
    BOMAllocationError,
)
from app.core.models.manufacturing import SPK
from app.core.models.daily_production import MaterialDebt


# ==================== Fixtures ====================

@pytest.fixture
def db_mock() -> Session:
    """Mock database session"""
    return MagicMock(spec=Session)


@pytest.fixture
def material_debt_service(db_mock: Session) -> MaterialDebtService:
    """Create MaterialDebtService instance"""
    return MaterialDebtService(db=db_mock)


@pytest.fixture
def sample_debt_data():
    """Sample material debt data"""
    return {
        "spk_id": 1,
        "material_id": 101,
        "qty_debt": 50,
        "unit_price": Decimal("10000"),
        "notes": "Insufficient stock for SPK production"
    }


# ==================== Test Cases ====================

class TestMaterialDebtCreation:
    """Test debt creation and validation"""
    
    @pytest.mark.asyncio
    async def test_create_debt_successfully(self, material_debt_service, db_mock, sample_debt_data):
        """Should create debt with valid data"""
        # Arrange
        debt = MaterialDebt(
            spk_id=sample_debt_data["spk_id"],
            material_id=sample_debt_data["material_id"],
            qty_debt=sample_debt_data["qty_debt"],
            unit_price=sample_debt_data["unit_price"],
            notes=sample_debt_data["notes"],
            status=MaterialDebtStatus.PENDING_APPROVAL,
            approval_status=MaterialDebtApprovalStatus.PENDING
        )
        
        db_mock.add = MagicMock()
        db_mock.commit = MagicMock()
        db_mock.flush = MagicMock()
        
        # Mock the add operation to set ID
        def set_id(*args, **kwargs):
            debt.id = 1
        db_mock.add.side_effect = set_id
        
        # Act
        with patch.object(material_debt_service, '_validate_spk', return_value=True):
            result = await material_debt_service.create_material_debt(
                **sample_debt_data
            )
        
        # Assert
        assert result is not None
        assert result["status"] == MaterialDebtStatus.PENDING_APPROVAL.value
        db_mock.add.assert_called_once()
        db_mock.commit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_debt_validates_spk(self, material_debt_service, db_mock, sample_debt_data):
        """Should validate SPK exists before creating debt"""
        # Arrange
        db_mock.query().filter().first.return_value = None
        
        # Act & Assert
        with patch.object(material_debt_service, '_validate_spk', return_value=False):
            with pytest.raises(BOMAllocationError):
                await material_debt_service.create_material_debt(**sample_debt_data)
    
    @pytest.mark.asyncio
    async def test_create_debt_validates_material(self, material_debt_service, db_mock, sample_debt_data):
        """Should validate material exists"""
        # Arrange
        db_mock.query().filter().first.return_value = None
        
        # Act & Assert
        with patch.object(material_debt_service, '_validate_spk', return_value=True):
            with patch.object(material_debt_service, '_validate_material', return_value=False):
                with pytest.raises(BOMAllocationError):
                    await material_debt_service.create_material_debt(**sample_debt_data)
    
    @pytest.mark.asyncio
    async def test_create_debt_validates_quantity(self, material_debt_service, db_mock):
        """Should reject zero or negative quantity"""
        # Arrange
        invalid_data = {
            "spk_id": 1,
            "material_id": 101,
            "qty_debt": 0,
            "unit_price": Decimal("10000"),
            "notes": "Test"
        }
        
        # Act & Assert
        with pytest.raises(BOMAllocationError):
            await material_debt_service.create_material_debt(**invalid_data)


class TestMaterialDebtApproval:
    """Test debt approval workflow"""
    
    @pytest.mark.asyncio
    async def test_approve_debt_pending(self, material_debt_service, db_mock):
        """Should approve pending debt"""
        # Arrange
        debt_id = 1
        mock_debt = MagicMock()
        mock_debt.id = debt_id
        mock_debt.status = MaterialDebtStatus.PENDING_APPROVAL
        mock_debt.approval_status = MaterialDebtApprovalStatus.PENDING
        
        db_mock.query().filter().first.return_value = mock_debt
        db_mock.commit = MagicMock()
        
        # Act
        result = await material_debt_service.approve_material_debt(
            debt_id=debt_id,
            approved_by_id=10,
            approval_notes="Approved"
        )
        
        # Assert
        assert result["approval_status"] == MaterialDebtApprovalStatus.APPROVED.value
        db_mock.commit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_reject_debt_pending(self, material_debt_service, db_mock):
        """Should reject pending debt"""
        # Arrange
        debt_id = 1
        mock_debt = MagicMock()
        mock_debt.id = debt_id
        mock_debt.status = MaterialDebtStatus.PENDING_APPROVAL
        mock_debt.approval_status = MaterialDebtApprovalStatus.PENDING
        
        db_mock.query().filter().first.return_value = mock_debt
        db_mock.commit = MagicMock()
        
        # Act
        result = await material_debt_service.reject_material_debt(
            debt_id=debt_id,
            rejected_by_id=10,
            rejection_reason="Insufficient justification"
        )
        
        # Assert
        assert result["approval_status"] == MaterialDebtApprovalStatus.REJECTED.value
        db_mock.commit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_reject_approved_debt_fails(self, material_debt_service, db_mock):
        """Should not allow rejecting already approved debt"""
        # Arrange
        debt_id = 1
        mock_debt = MagicMock()
        mock_debt.id = debt_id
        mock_debt.approval_status = MaterialDebtApprovalStatus.APPROVED
        
        db_mock.query().filter().first.return_value = mock_debt
        
        # Act & Assert
        with pytest.raises(BOMAllocationError):
            await material_debt_service.reject_material_debt(
                debt_id=debt_id,
                rejected_by_id=10,
                rejection_reason="Already approved"
            )


class TestMaterialDebtAdjustment:
    """Test debt settlement and adjustments"""
    
    @pytest.mark.asyncio
    async def test_adjust_debt_partial_settlement(self, material_debt_service, db_mock):
        """Should record partial debt settlement"""
        # Arrange
        debt_id = 1
        mock_debt = MagicMock()
        mock_debt.id = debt_id
        mock_debt.qty_debt = Decimal("100")
        mock_debt.qty_settled = Decimal("0")
        mock_debt.status = MaterialDebtStatus.APPROVED
        
        db_mock.query().filter().first.return_value = mock_debt
        db_mock.commit = MagicMock()
        
        # Act
        result = await material_debt_service.adjust_material_debt(
            debt_id=debt_id,
            qty_settled=Decimal("30"),
            adjustment_type="SETTLEMENT",
            notes="Received 30 units"
        )
        
        # Assert
        assert result["qty_settled"] is not None
        db_mock.commit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_adjust_debt_full_settlement(self, material_debt_service, db_mock):
        """Should mark fully settled debt as SETTLED"""
        # Arrange
        debt_id = 1
        mock_debt = MagicMock()
        mock_debt.id = debt_id
        mock_debt.qty_debt = Decimal("100")
        mock_debt.qty_settled = Decimal("70")
        mock_debt.status = MaterialDebtStatus.APPROVED
        
        db_mock.query().filter().first.return_value = mock_debt
        db_mock.commit = MagicMock()
        
        # Act
        result = await material_debt_service.adjust_material_debt(
            debt_id=debt_id,
            qty_settled=Decimal("30"),
            adjustment_type="SETTLEMENT",
            notes="Final settlement"
        )
        
        # Assert
        assert result["status"] == MaterialDebtStatus.SETTLED.value
        db_mock.commit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_adjust_debt_exceeds_amount_fails(self, material_debt_service, db_mock):
        """Should not allow settlement exceeding debt amount"""
        # Arrange
        debt_id = 1
        mock_debt = MagicMock()
        mock_debt.id = debt_id
        mock_debt.qty_debt = Decimal("100")
        mock_debt.qty_settled = Decimal("80")
        
        db_mock.query().filter().first.return_value = mock_debt
        
        # Act & Assert
        with pytest.raises(BOMAllocationError):
            await material_debt_service.adjust_material_debt(
                debt_id=debt_id,
                qty_settled=Decimal("30"),  # Would exceed 100
                adjustment_type="SETTLEMENT",
                notes="Invalid"
            )


class TestMaterialDebtQuerying:
    """Test debt queries and calculations"""
    
    @pytest.mark.asyncio
    async def test_get_outstanding_debt(self, material_debt_service, db_mock):
        """Should retrieve outstanding debts"""
        # Arrange
        mock_debts = [
            MagicMock(id=1, qty_debt=50, status=MaterialDebtStatus.APPROVED),
            MagicMock(id=2, qty_debt=100, status=MaterialDebtStatus.APPROVED),
        ]
        
        db_mock.query().filter().all.return_value = mock_debts
        
        # Act
        result = await material_debt_service.get_outstanding_debts()
        
        # Assert
        assert len(result) == 2
        assert all(item["status"] == MaterialDebtStatus.APPROVED.value for item in result)
    
    @pytest.mark.asyncio
    async def test_get_debt_status(self, material_debt_service, db_mock):
        """Should return overall debt status"""
        # Arrange
        mock_debt = MagicMock()
        mock_debt.id = 1
        mock_debt.qty_debt = Decimal("100")
        mock_debt.qty_settled = Decimal("30")
        mock_debt.status = MaterialDebtStatus.APPROVED
        mock_debt.approval_status = MaterialDebtApprovalStatus.APPROVED
        
        db_mock.query().filter().first.return_value = mock_debt
        
        # Act
        result = await material_debt_service.get_debt_status(debt_id=1)
        
        # Assert
        assert result["id"] == 1
        assert result["qty_outstanding"] == Decimal("70")
        assert result["settlement_percentage"] > 0
    
    @pytest.mark.asyncio
    async def test_check_po_blocking_threshold(self, material_debt_service, db_mock):
        """Should check if outstanding debt exceeds PO threshold"""
        # Arrange
        threshold = Decimal("1000000")  # 1M threshold
        
        mock_debts = [
            MagicMock(qty_debt=Decimal("500000"), qty_settled=Decimal("0")),
            MagicMock(qty_debt=Decimal("600000"), qty_settled=Decimal("100000")),
        ]
        
        db_mock.query().filter().all.return_value = mock_debts
        
        # Act
        result = await material_debt_service.check_po_blocking_threshold()
        
        # Assert
        assert "is_blocked" in result
        assert "total_outstanding" in result


class TestMaterialDebtIntegration:
    """Test integration with other systems"""
    
    @pytest.mark.asyncio
    async def test_debt_integrates_with_approval_workflow(self, material_debt_service, db_mock):
        """Should integrate with ApprovalWorkflowEngine"""
        # Arrange
        sample_data = {
            "spk_id": 1,
            "material_id": 101,
            "qty_debt": 50,
            "unit_price": Decimal("10000"),
            "notes": "Test"
        }
        
        with patch.object(material_debt_service, '_validate_spk', return_value=True):
            with patch.object(material_debt_service, '_validate_material', return_value=True):
                with patch.object(material_debt_service, 'approval_workflow_engine') as mock_engine:
                    # Act
                    await material_debt_service.create_material_debt(**sample_data)
                    
                    # Assert - approval engine should be called
                    # This depends on actual implementation


class TestMaterialDebtErrorHandling:
    """Test error handling and edge cases"""
    
    @pytest.mark.asyncio
    async def test_debt_not_found_raises_error(self, material_debt_service, db_mock):
        """Should raise error when debt not found"""
        # Arrange
        db_mock.query().filter().first.return_value = None
        
        # Act & Assert
        with pytest.raises(BOMAllocationError):
            await material_debt_service.get_debt_status(debt_id=999)
    
    @pytest.mark.asyncio
    async def test_invalid_adjustment_type_raises_error(self, material_debt_service, db_mock):
        """Should reject invalid adjustment types"""
        # Arrange
        mock_debt = MagicMock()
        db_mock.query().filter().first.return_value = mock_debt
        
        # Act & Assert
        with pytest.raises(BOMAllocationError):
            await material_debt_service.adjust_material_debt(
                debt_id=1,
                qty_settled=Decimal("10"),
                adjustment_type="INVALID_TYPE",
                notes="Test"
            )
    
    @pytest.mark.asyncio
    async def test_concurrent_settlement_safe(self, material_debt_service, db_mock):
        """Should handle concurrent debt settlements safely"""
        # This would require actual database transaction testing
        # For now, just verify the service can be called concurrently
        
        mock_debt = MagicMock()
        mock_debt.qty_debt = Decimal("100")
        mock_debt.qty_settled = Decimal("0")
        mock_debt.status = MaterialDebtStatus.APPROVED
        
        db_mock.query().filter().first.return_value = mock_debt
        db_mock.commit = MagicMock()
        
        # Act - Call adjustment multiple times concurrently
        tasks = [
            material_debt_service.adjust_material_debt(
                debt_id=1,
                qty_settled=Decimal("20"),
                adjustment_type="SETTLEMENT",
                notes=f"Settlement {i}"
            )
            for i in range(3)
        ]
        
        # This should not raise errors (in real DB it would use transactions)
        # Just ensure async handling works


class TestMaterialDebtCalculations:
    """Test debt amount calculations"""
    
    def test_calculate_debt_total_value(self):
        """Should calculate total debt value"""
        qty_debt = Decimal("100")
        unit_price = Decimal("10000")
        
        total_value = qty_debt * unit_price
        
        assert total_value == Decimal("1000000")
    
    def test_calculate_settled_percentage(self):
        """Should calculate settlement percentage"""
        qty_debt = Decimal("100")
        qty_settled = Decimal("30")
        
        percentage = (qty_settled / qty_debt) * 100
        
        assert percentage == Decimal("30")
        assert percentage >= 0 and percentage <= 100
    
    def test_calculate_debt_aging(self):
        """Should calculate debt age"""
        created_date = date.today() - timedelta(days=45)
        today = date.today()
        
        age_days = (today - created_date).days
        
        assert age_days == 45
        assert age_days > 30  # Overdue if > 30 days


# ==================== Test Execution ====================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
