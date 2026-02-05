"""Phase 2B - Rework & QC System Tests

Test suite for rework and quality control operations:
- Defect categorization
- Rework request creation and workflow
- QC approval process
- Rework execution and completion
- Final verification

Author: IT Developer Expert
Date: 5 February 2026
"""

import pytest
from decimal import Decimal
from datetime import datetime

from app.core.database import SessionLocal
from app.core.models.manufacturing import (
    ManufacturingOrder,
    SPK,
    Department,
    MOState,
    DefectCategory,
    DefectType,
    DefectSeverity,
    ReworkRequest,
    ReworkStatus,
)
from app.modules.manufacturing.rework_service import ReworkService
from sqlalchemy.orm import Session


@pytest.fixture
def db():
    """Database session for tests"""
    session = SessionLocal()
    yield session
    session.close()


@pytest.fixture
def sample_mo(db: Session):
    """Create sample Manufacturing Order"""
    mo = ManufacturingOrder(
        article_id=1,
        quantity=1000,
        target_quantity=Decimal("1000"),
        production_quantity=Decimal("0"),
        buffer_percentage=Decimal("0"),
        mo_status=MOState.DRAFT,
        extra_metadata="{}",
    )
    db.add(mo)
    db.commit()
    return mo


@pytest.fixture
def sample_spk(db: Session, sample_mo):
    """Create sample SPK"""
    spk = SPK(
        mo_id=sample_mo.id,
        department=Department.SEWING,
        original_qty=1000,
        buffer_percentage=Decimal("0"),
        target_qty=1000,
        production_status="IN_PROGRESS",
        good_qty=Decimal("950"),
        defect_qty=Decimal("30"),
        extra_metadata="{}",
    )
    db.add(spk)
    db.commit()
    return spk


@pytest.fixture
def sample_defect_category(db: Session):
    """Create sample defect category"""
    category = DefectCategory(
        code="DFC-001",
        name="Broken Stitch",
        defect_type=DefectType.STITCHING,
        description="Broken or skipped stitches",
        severity=DefectSeverity.MINOR,
        default_rework_hours=1,
    )
    db.add(category)
    db.commit()
    return category


class TestDefectCategoryManagement:
    """Test defect category handling"""

    def test_create_defect_category(self, db: Session):
        """Create a defect category"""
        category = DefectCategory(
            code="DFC-002",
            name="Wrong Color",
            defect_type=DefectType.MATERIAL,
            description="Material dyed wrong color",
            severity=DefectSeverity.CRITICAL,
            default_rework_hours=0,  # Cannot rework, discard
        )
        db.add(category)
        db.commit()

        assert category.id is not None
        assert category.code == "DFC-002"
        assert category.severity == DefectSeverity.CRITICAL

    def test_defect_categories_are_unique(self, db: Session, sample_defect_category):
        """Defect category codes are unique"""
        duplicate = DefectCategory(
            code="DFC-001",  # Duplicate code
            name="Different Name",
            defect_type=DefectType.FILLING,
            description="Different category",
            severity=DefectSeverity.MAJOR,
            default_rework_hours=2,
        )
        db.add(duplicate)

        with pytest.raises(Exception):  # IntegrityError
            db.commit()


class TestReworkRequestCreation:
    """Test rework request creation"""

    def test_create_rework_request_basic(self, db: Session, sample_spk, sample_defect_category):
        """Create basic rework request"""
        service = ReworkService(db)
        rework = service.create_rework_request(
            spk_id=sample_spk.id,
            defect_qty=Decimal("30"),
            defect_category_id=sample_defect_category.id,
            defect_notes="30 pieces with broken stitches",
            requested_by_id=1,
        )

        assert rework is not None
        assert rework.spk_id == sample_spk.id
        assert rework.defect_qty == Decimal("30")
        assert rework.status == ReworkStatus.PENDING

    def test_create_rework_request_invalid_spk(self, db: Session, sample_defect_category):
        """Create rework request with invalid SPK"""
        service = ReworkService(db)

        with pytest.raises(ValueError, match="SPK .* not found"):
            service.create_rework_request(
                spk_id=9999,
                defect_qty=Decimal("30"),
                defect_category_id=sample_defect_category.id,
                defect_notes="Invalid SPK",
                requested_by_id=1,
            )

    def test_create_rework_request_invalid_category(self, db: Session, sample_spk):
        """Create rework request with invalid defect category"""
        service = ReworkService(db)

        with pytest.raises(ValueError, match="DefectCategory .* not found"):
            service.create_rework_request(
                spk_id=sample_spk.id,
                defect_qty=Decimal("30"),
                defect_category_id=9999,
                defect_notes="Invalid category",
                requested_by_id=1,
            )


class TestReworkApprovalWorkflow:
    """Test QC approval workflow"""

    def test_approve_rework_request(self, db: Session, sample_spk, sample_defect_category):
        """Approve rework request (QC manager action)"""
        service = ReworkService(db)

        # Create request
        rework = service.create_rework_request(
            spk_id=sample_spk.id,
            defect_qty=Decimal("30"),
            defect_category_id=sample_defect_category.id,
            defect_notes="Broken stitches",
            requested_by_id=1,
        )

        # Approve
        approved = service.approve_rework(
            rework_id=rework.id,
            qc_approval_notes="Approved for rework",
            user_id=2,  # QC manager
        )

        assert approved.status == ReworkStatus.APPROVED
        assert approved.qc_reviewed_by_id == 2
        assert approved.qc_reviewed_at is not None

    def test_reject_rework_request(self, db: Session, sample_spk, sample_defect_category):
        """Reject rework request (discard instead)"""
        service = ReworkService(db)

        # Create request
        rework = service.create_rework_request(
            spk_id=sample_spk.id,
            defect_qty=Decimal("30"),
            defect_category_id=sample_defect_category.id,
            defect_notes="Severe damage",
            requested_by_id=1,
        )

        # Reject
        rejected = service.reject_rework(
            rework_id=rework.id,
            rejection_reason="Damage too severe, not economical to rework",
            user_id=2,
        )

        assert rejected.status == ReworkStatus.REJECTED
        assert rejected.qc_reviewed_by_id == 2

    def test_cannot_approve_already_approved_rework(self, db: Session, sample_spk, sample_defect_category):
        """Cannot approve already approved rework"""
        service = ReworkService(db)

        rework = service.create_rework_request(
            spk_id=sample_spk.id,
            defect_qty=Decimal("30"),
            defect_category_id=sample_defect_category.id,
            defect_notes="Test",
            requested_by_id=1,
        )

        service.approve_rework(rework.id, user_id=2)

        # Try to approve again
        with pytest.raises(ValueError, match="Cannot approve rework"):
            service.approve_rework(rework.id, user_id=2)


class TestReworkExecution:
    """Test rework execution by operators"""

    def test_start_rework_process(self, db: Session, sample_spk, sample_defect_category):
        """Start rework process (operator action)"""
        service = ReworkService(db)

        # Create and approve
        rework = service.create_rework_request(
            spk_id=sample_spk.id,
            defect_qty=Decimal("30"),
            defect_category_id=sample_defect_category.id,
            defect_notes="Broken stitches",
            requested_by_id=1,
        )
        service.approve_rework(rework.id, user_id=2)

        # Start rework
        started = service.start_rework(
            rework_id=rework.id,
            operator_id=3,  # Operator doing rework
            user_id=3,
        )

        assert started.status == ReworkStatus.IN_PROGRESS
        assert started.rework_operator_id == 3
        assert started.rework_started_at is not None

    def test_complete_rework_process(self, db: Session, sample_spk, sample_defect_category):
        """Complete rework process"""
        service = ReworkService(db)

        # Create → Approve → Start
        rework = service.create_rework_request(
            spk_id=sample_spk.id,
            defect_qty=Decimal("30"),
            defect_category_id=sample_defect_category.id,
            defect_notes="Broken stitches",
            requested_by_id=1,
        )
        service.approve_rework(rework.id, user_id=2)
        service.start_rework(rework.id, operator_id=3, user_id=3)

        # Complete
        completed = service.complete_rework(
            rework_id=rework.id,
            rework_notes="Fixed all broken stitches",
            material_cost=Decimal("5000"),
            labor_cost=Decimal("10000"),
            user_id=3,
        )

        assert completed.status == ReworkStatus.COMPLETED
        assert completed.rework_completed_at is not None
        assert completed.total_cost == Decimal("15000")

    def test_cannot_start_unapproved_rework(self, db: Session, sample_spk, sample_defect_category):
        """Cannot start rework without approval"""
        service = ReworkService(db)

        rework = service.create_rework_request(
            spk_id=sample_spk.id,
            defect_qty=Decimal("30"),
            defect_category_id=sample_defect_category.id,
            defect_notes="Test",
            requested_by_id=1,
        )

        with pytest.raises(ValueError, match="Cannot start rework"):
            service.start_rework(rework.id, operator_id=3)


class TestReworkVerification:
    """Test final QC verification"""

    def test_verify_rework_all_good(self, db: Session, sample_spk, sample_defect_category):
        """Verify rework - all units passed"""
        service = ReworkService(db)

        # Complete rework workflow
        rework = service.create_rework_request(
            spk_id=sample_spk.id,
            defect_qty=Decimal("30"),
            defect_category_id=sample_defect_category.id,
            defect_notes="Test",
            requested_by_id=1,
        )
        service.approve_rework(rework.id, user_id=2)
        service.start_rework(rework.id, operator_id=3)
        service.complete_rework(
            rework_id=rework.id,
            material_cost=Decimal("5000"),
            labor_cost=Decimal("10000"),
            user_id=3,
        )

        # Verify - all 30 passed
        verified = service.verify_rework(
            rework_id=rework.id,
            verified_good_qty=Decimal("30"),
            verified_failed_qty=Decimal("0"),
            user_id=2,
        )

        assert verified.status == ReworkStatus.VERIFIED
        assert verified.verified_good_qty == Decimal("30")
        assert verified.verified_failed_qty == Decimal("0")

    def test_verify_rework_partial_fail(self, db: Session, sample_spk, sample_defect_category):
        """Verify rework - some units still bad"""
        service = ReworkService(db)

        # Complete workflow
        rework = service.create_rework_request(
            spk_id=sample_spk.id,
            defect_qty=Decimal("30"),
            defect_category_id=sample_defect_category.id,
            defect_notes="Test",
            requested_by_id=1,
        )
        service.approve_rework(rework.id, user_id=2)
        service.start_rework(rework.id, operator_id=3)
        service.complete_rework(
            rework_id=rework.id,
            material_cost=Decimal("5000"),
            labor_cost=Decimal("10000"),
            user_id=3,
        )

        # Verify - 28 good, 2 still bad
        verified = service.verify_rework(
            rework_id=rework.id,
            verified_good_qty=Decimal("28"),
            verified_failed_qty=Decimal("2"),
            user_id=2,
        )

        assert verified.verified_good_qty == Decimal("28")
        assert verified.verified_failed_qty == Decimal("2")

    def test_verify_rework_quantity_mismatch(self, db: Session, sample_spk, sample_defect_category):
        """Verify rework - quantities don't match defect qty"""
        service = ReworkService(db)

        rework = service.create_rework_request(
            spk_id=sample_spk.id,
            defect_qty=Decimal("30"),
            defect_category_id=sample_defect_category.id,
            defect_notes="Test",
            requested_by_id=1,
        )
        service.approve_rework(rework.id, user_id=2)
        service.start_rework(rework.id, operator_id=3)
        service.complete_rework(rework_id=rework.id, user_id=3)

        # Try to verify with wrong quantities (28 + 1 = 29, but defect_qty = 30)
        with pytest.raises(ValueError, match="must equal defect quantity"):
            service.verify_rework(
                rework_id=rework.id,
                verified_good_qty=Decimal("28"),
                verified_failed_qty=Decimal("1"),
                user_id=2,
            )


class TestReworkMaterialTracking:
    """Test material consumption tracking"""

    def test_add_rework_material(self, db: Session, sample_spk, sample_defect_category):
        """Add material consumed during rework"""
        service = ReworkService(db)

        rework = service.create_rework_request(
            spk_id=sample_spk.id,
            defect_qty=Decimal("30"),
            defect_category_id=sample_defect_category.id,
            defect_notes="Test",
            requested_by_id=1,
        )

        material = service.add_rework_material(
            rework_id=rework.id,
            product_id=1,  # Thread
            qty_used=Decimal("500"),  # 500 meters
            uom="METERS",
            unit_cost=Decimal("100"),
            user_id=3,
        )

        assert material.rework_request_id == rework.id
        assert material.qty_used == Decimal("500")
        assert material.total_cost == Decimal("50000")

    def test_multiple_materials_per_rework(self, db: Session, sample_spk, sample_defect_category):
        """Add multiple materials to single rework"""
        service = ReworkService(db)

        rework = service.create_rework_request(
            spk_id=sample_spk.id,
            defect_qty=Decimal("30"),
            defect_category_id=sample_defect_category.id,
            defect_notes="Test",
            requested_by_id=1,
        )

        # Add thread
        material1 = service.add_rework_material(
            rework_id=rework.id,
            product_id=1,
            qty_used=Decimal("500"),
            uom="METERS",
            unit_cost=Decimal("100"),
            user_id=3,
        )

        # Add fabric patch
        material2 = service.add_rework_material(
            rework_id=rework.id,
            product_id=2,
            qty_used=Decimal("30"),
            uom="PIECES",
            unit_cost=Decimal("5000"),
            user_id=3,
        )

        assert len(rework.materials) == 2
        assert material1.total_cost == Decimal("50000")
        assert material2.total_cost == Decimal("150000")


class TestEndToEndReworkFlow:
    """Test complete rework workflow"""

    def test_complete_rework_workflow(self, db: Session, sample_spk, sample_defect_category):
        """Complete workflow: Create → Approve → Execute → Verify"""
        service = ReworkService(db)

        # 1. Create request
        rework = service.create_rework_request(
            spk_id=sample_spk.id,
            defect_qty=Decimal("30"),
            defect_category_id=sample_defect_category.id,
            defect_notes="30 pieces with broken stitches",
            requested_by_id=1,  # QC Inspector
        )
        assert rework.status == ReworkStatus.PENDING

        # 2. QC Manager approval
        approved = service.approve_rework(
            rework_id=rework.id,
            qc_approval_notes="Approved, economical to rework",
            user_id=2,  # QC Manager
        )
        assert approved.status == ReworkStatus.APPROVED

        # 3. Operator starts rework
        started = service.start_rework(
            rework_id=rework.id,
            operator_id=3,  # Sewing operator
            user_id=3,
        )
        assert started.status == ReworkStatus.IN_PROGRESS

        # 4. Operator completes rework
        completed = service.complete_rework(
            rework_id=rework.id,
            rework_notes="Fixed all broken stitches",
            material_cost=Decimal("5000"),
            labor_cost=Decimal("10000"),
            user_id=3,
        )
        assert completed.status == ReworkStatus.COMPLETED
        assert completed.total_cost == Decimal("15000")

        # 5. Final QC verification
        verified = service.verify_rework(
            rework_id=rework.id,
            verified_good_qty=Decimal("28"),  # 28 passed verification
            verified_failed_qty=Decimal("2"),  # 2 still bad, discard
            user_id=2,  # QC Manager
        )
        assert verified.status == ReworkStatus.VERIFIED

    def test_rework_rejection_flow(self, db: Session, sample_spk, sample_defect_category):
        """Workflow: Create → Reject (discard instead)"""
        service = ReworkService(db)

        # Create request
        rework = service.create_rework_request(
            spk_id=sample_spk.id,
            defect_qty=Decimal("5"),
            defect_category_id=sample_defect_category.id,
            defect_notes="Severe damage",
            requested_by_id=1,
        )

        # QC Manager rejects (decides to discard)
        rejected = service.reject_rework(
            rework_id=rework.id,
            rejection_reason="Damage too severe, not economical to rework",
            user_id=2,
        )

        assert rejected.status == ReworkStatus.REJECTED
        assert "Damage too severe" in rejected.qc_approval_notes

    @pytest.mark.parametrize(
        "good_qty,failed_qty",
        [
            (30, 0),  # All good
            (28, 2),  # Some failed
            (15, 15),  # Half failed
        ],
    )
    def test_various_verification_results(
        self, db: Session, sample_spk, sample_defect_category, good_qty, failed_qty
    ):
        """Test various verification outcomes"""
        service = ReworkService(db)

        rework = service.create_rework_request(
            spk_id=sample_spk.id,
            defect_qty=Decimal("30"),
            defect_category_id=sample_defect_category.id,
            defect_notes="Test",
            requested_by_id=1,
        )
        service.approve_rework(rework.id, user_id=2)
        service.start_rework(rework.id, operator_id=3)
        service.complete_rework(rework.id, user_id=3)

        verified = service.verify_rework(
            rework_id=rework.id,
            verified_good_qty=Decimal(str(good_qty)),
            verified_failed_qty=Decimal(str(failed_qty)),
            user_id=2,
        )

        assert verified.verified_good_qty == Decimal(str(good_qty))
        assert verified.verified_failed_qty == Decimal(str(failed_qty))
        assert (verified.verified_good_qty + verified.verified_failed_qty) == Decimal("30")
