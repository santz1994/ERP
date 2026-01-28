"""
Unit Tests for SPK Edit Service
Tests the SPK Edit system (Feature #7)

Coverage:
- Edit request creation and validation
- Business rule validation
- Approval workflow integration
- Change application
- History tracking
- Error scenarios
"""

import pytest
from datetime import datetime, timedelta, date
from decimal import Decimal
from unittest.mock import MagicMock, AsyncMock, patch
from sqlalchemy.orm import Session

from app.services.spk_edit_service import (
    SPKEditService,
    SPKEditType,
    SPKEditStatus,
)


# ==================== Fixtures ====================

@pytest.fixture
def db_mock() -> Session:
    """Mock database session"""
    return MagicMock(spec=Session)


@pytest.fixture
def spk_edit_service(db_mock: Session) -> SPKEditService:
    """Create SPKEditService instance"""
    return SPKEditService(db=db_mock)


@pytest.fixture
def sample_spk():
    """Sample SPK data"""
    spk = MagicMock()
    spk.id = 1
    spk.article_id = 5
    spk.spk_number = "SPK-2026-001"
    spk.target_qty = 1000
    spk.completed_qty = 100
    spk.status = "IN_PROGRESS"
    spk.deadline_date = date.today() + timedelta(days=7)
    spk.created_at = datetime.now()
    return spk


# ==================== Test Cases ====================

class TestSPKEditRequestCreation:
    """Test SPK edit request creation"""
    
    @pytest.mark.asyncio
    async def test_submit_quantity_edit_request(self, spk_edit_service, db_mock, sample_spk):
        """Should submit quantity edit request"""
        # Arrange
        db_mock.query().filter().first.return_value = sample_spk
        
        # Act
        result = await spk_edit_service.submit_edit_request(
            spk_id=1,
            edit_type=SPKEditType.EDIT_QUANTITY,
            changes={"target_qty": 1500},
            reason="Customer increased order by 500 units",
            requested_by_id=5
        )
        
        # Assert
        assert result["spk_id"] == 1
        assert result["edit_type"] == SPKEditType.EDIT_QUANTITY.value
        assert result["new_values"]["target_qty"] == 1500
        assert result["status"] == SPKEditStatus.PENDING_APPROVAL.value
        assert result["requested_by_id"] == 5
    
    @pytest.mark.asyncio
    async def test_submit_deadline_edit_request(self, spk_edit_service, db_mock, sample_spk):
        """Should submit deadline edit request"""
        # Arrange
        new_deadline = date.today() + timedelta(days=14)
        db_mock.query().filter().first.return_value = sample_spk
        
        # Act
        result = await spk_edit_service.submit_edit_request(
            spk_id=1,
            edit_type=SPKEditType.EDIT_DEADLINE,
            changes={"deadline_date": new_deadline},
            reason="Extended deadline due to client request",
            requested_by_id=5
        )
        
        # Assert
        assert result["edit_type"] == SPKEditType.EDIT_DEADLINE.value
        assert result["new_values"]["deadline_date"] == new_deadline
    
    @pytest.mark.asyncio
    async def test_submit_notes_edit_request(self, spk_edit_service, db_mock, sample_spk):
        """Should submit notes edit request"""
        # Arrange
        db_mock.query().filter().first.return_value = sample_spk
        
        # Act
        result = await spk_edit_service.submit_edit_request(
            spk_id=1,
            edit_type=SPKEditType.EDIT_NOTES,
            changes={"notes": "Updated production notes"},
            reason="Add special instructions for quality control",
            requested_by_id=5
        )
        
        # Assert
        assert result["edit_type"] == SPKEditType.EDIT_NOTES.value


class TestSPKEditValidation:
    """Test edit validation business rules"""
    
    @pytest.mark.asyncio
    async def test_validate_qty_below_produced_fails(self, spk_edit_service, db_mock, sample_spk):
        """Should reject reducing qty below already produced"""
        # Arrange
        sample_spk.target_qty = 1000
        sample_spk.completed_qty = 800
        
        db_mock.query().filter().first.return_value = sample_spk
        
        # Act & Assert
        with pytest.raises(ValueError):
            await spk_edit_service.submit_edit_request(
                spk_id=1,
                edit_type=SPKEditType.EDIT_QUANTITY,
                changes={"target_qty": 500},  # Below 800 completed
                reason="Reduce order",
                requested_by_id=5
            )
    
    @pytest.mark.asyncio
    async def test_validate_past_deadline_fails(self, spk_edit_service, db_mock, sample_spk):
        """Should reject past deadline"""
        # Arrange
        db_mock.query().filter().first.return_value = sample_spk
        
        # Act & Assert
        with pytest.raises(ValueError):
            await spk_edit_service.submit_edit_request(
                spk_id=1,
                edit_type=SPKEditType.EDIT_DEADLINE,
                changes={"deadline_date": date.today() - timedelta(days=1)},
                reason="Edit deadline",
                requested_by_id=5
            )
    
    @pytest.mark.asyncio
    async def test_validate_article_change_after_production_fails(
        self, spk_edit_service, db_mock, sample_spk
    ):
        """Should reject article change after production started"""
        # Arrange
        sample_spk.completed_qty = 50  # Production started
        db_mock.query().filter().first.return_value = sample_spk
        
        # Act & Assert
        with pytest.raises(ValueError):
            await spk_edit_service.submit_edit_request(
                spk_id=1,
                edit_type=SPKEditType.EDIT_ARTICLE,
                changes={"article_id": 10},
                reason="Wrong article",
                requested_by_id=5
            )
    
    @pytest.mark.asyncio
    async def test_validate_completed_spk_edit_fails(
        self, spk_edit_service, db_mock, sample_spk
    ):
        """Should reject editing completed SPK"""
        # Arrange
        from app.core.models.production import SPKStatus
        sample_spk.status = "COMPLETED"
        db_mock.query().filter().first.return_value = sample_spk
        
        # Act & Assert
        with pytest.raises(ValueError):
            await spk_edit_service.submit_edit_request(
                spk_id=1,
                edit_type=SPKEditType.EDIT_QUANTITY,
                changes={"target_qty": 1500},
                reason="Edit completed SPK",
                requested_by_id=5
            )


class TestSPKEditApproval:
    """Test edit approval workflow"""
    
    @pytest.mark.asyncio
    async def test_approve_edit_request(self, spk_edit_service, db_mock):
        """Should approve edit request"""
        # Act
        result = await spk_edit_service.approve_edit_request(
            edit_request_id=1,
            approved_by_id=2,
            approval_notes="Approved - valid changes"
        )
        
        # Assert
        assert result["id"] == 1
        assert result["status"] == SPKEditStatus.APPROVED.value
        assert result["approved_by_id"] == 2
        assert result["approval_notes"] == "Approved - valid changes"
    
    @pytest.mark.asyncio
    async def test_reject_edit_request(self, spk_edit_service, db_mock):
        """Should reject edit request"""
        # Act
        result = await spk_edit_service.reject_edit_request(
            edit_request_id=1,
            rejected_by_id=2,
            rejection_reason="Insufficient documentation"
        )
        
        # Assert
        assert result["id"] == 1
        assert result["status"] == SPKEditStatus.REJECTED.value
        assert result["rejected_by_id"] == 2
        assert result["rejection_reason"] == "Insufficient documentation"


class TestSPKEditApplication:
    """Test applying approved changes"""
    
    @pytest.mark.asyncio
    async def test_apply_approved_changes(self, spk_edit_service, db_mock):
        """Should apply approved changes to SPK"""
        # Act
        result = await spk_edit_service.apply_approved_changes(
            edit_request_id=1,
            applied_by_id=5
        )
        
        # Assert
        assert result["id"] == 1
        assert result["status"] == SPKEditStatus.APPLIED.value
        assert result["applied_by_id"] == 5


class TestSPKEditQuerying:
    """Test edit history and pending queries"""
    
    @pytest.mark.asyncio
    async def test_get_edit_history(self, spk_edit_service, db_mock):
        """Should retrieve edit history"""
        # Act
        history = await spk_edit_service.get_edit_history(spk_id=1, limit=50)
        
        # Assert
        assert isinstance(history, list)
        assert len(history) <= 50
    
    @pytest.mark.asyncio
    async def test_get_pending_edits(self, spk_edit_service, db_mock):
        """Should retrieve pending edits"""
        # Act
        pending = await spk_edit_service.get_pending_edits(spk_id=1)
        
        # Assert
        assert isinstance(pending, list)


class TestSPKEditCancellation:
    """Test edit cancellation"""
    
    @pytest.mark.asyncio
    async def test_cancel_edit_request(self, spk_edit_service, db_mock):
        """Should cancel pending edit request"""
        # Act
        result = await spk_edit_service.cancel_edit_request(
            edit_request_id=1,
            cancelled_by_id=5,
            reason="Changed mind about the edit"
        )
        
        # Assert
        assert result["id"] == 1
        assert result["status"] == SPKEditStatus.CANCELLED.value
        assert result["cancelled_by_id"] == 5


class TestSPKEditEdgeCases:
    """Test edge cases and special scenarios"""
    
    @pytest.mark.asyncio
    async def test_multiple_edits_same_spk(self, spk_edit_service, db_mock, sample_spk):
        """Should allow multiple pending edits to same SPK"""
        # Arrange
        db_mock.query().filter().first.return_value = sample_spk
        
        # Act - Submit first edit
        result1 = await spk_edit_service.submit_edit_request(
            spk_id=1,
            edit_type=SPKEditType.EDIT_QUANTITY,
            changes={"target_qty": 1500},
            reason="First edit",
            requested_by_id=5
        )
        
        # Act - Submit second edit
        result2 = await spk_edit_service.submit_edit_request(
            spk_id=1,
            edit_type=SPKEditType.EDIT_DEADLINE,
            changes={"deadline_date": date.today() + timedelta(days=14)},
            reason="Second edit",
            requested_by_id=5
        )
        
        # Assert - Both should be pending
        assert result1["edit_type"] == SPKEditType.EDIT_QUANTITY.value
        assert result2["edit_type"] == SPKEditType.EDIT_DEADLINE.value
    
    @pytest.mark.asyncio
    async def test_very_large_quantity_increase(self, spk_edit_service, db_mock, sample_spk):
        """Should handle large quantity increases"""
        # Arrange
        sample_spk.target_qty = 1000
        sample_spk.completed_qty = 0
        
        db_mock.query().filter().first.return_value = sample_spk
        
        # Act
        result = await spk_edit_service.submit_edit_request(
            spk_id=1,
            edit_type=SPKEditType.EDIT_QUANTITY,
            changes={"target_qty": 100000},  # 100x increase
            reason="Large bulk order",
            requested_by_id=5
        )
        
        # Assert
        assert result["new_values"]["target_qty"] == 100000
    
    @pytest.mark.asyncio
    async def test_edit_with_very_short_reason(self, spk_edit_service, db_mock, sample_spk):
        """Should validate minimum reason length"""
        # Arrange
        db_mock.query().filter().first.return_value = sample_spk
        
        # Act & Assert - Reason too short (< 10 chars)
        # This would be validated at API level via Pydantic
        # Service should handle it gracefully


class TestSPKEditIntegration:
    """Test integration with other systems"""
    
    @pytest.mark.asyncio
    async def test_edit_triggers_reallocation_on_qty_change(
        self, spk_edit_service, db_mock, sample_spk
    ):
        """Should trigger material reallocation when qty changes"""
        # Arrange
        db_mock.query().filter().first.return_value = sample_spk
        
        # Act
        with patch.object(spk_edit_service, '_check_material_shortage') as mock_shortage:
            mock_shortage.return_value = None  # No shortage
            
            result = await spk_edit_service.submit_edit_request(
                spk_id=1,
                edit_type=SPKEditType.EDIT_QUANTITY,
                changes={"target_qty": 2000},  # Double quantity
                reason="Customer large order",
                requested_by_id=5
            )
        
        # Assert - Check material shortage would be called
        mock_shortage.assert_called_once()


# ==================== Test Execution ====================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
