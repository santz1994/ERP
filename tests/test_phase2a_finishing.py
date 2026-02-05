"""Phase 2A - Warehouse Finishing 2-Stage Tests

Test suite for warehouse finishing operations:
- Stage 1 (Stuffing): KAIN input → Stuffed bodies
- Stage 2 (Closing): Stuffed bodies → Finished dolls

Author: IT Developer Expert
Date: 5 February 2026
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'erp-softtoys'))

import pytest
from decimal import Decimal
from datetime import date

from app.core.database import SessionLocal
from app.core.models.manufacturing import (
    ManufacturingOrder,
    SPK,
    Department,
    MOState,
)
from app.core.models.finishing import (
    WarehouseFinishingStock,
    FinishingStage,
    FinishingInputOutput,
)
from app.modules.finishing.finishing_service import FinishingService
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


class TestStage1Creation:
    """Test Stage 1 SPK creation"""

    def test_create_stage1_spk_basic(self, db: Session, sample_mo):
        """Create basic Stage 1 SPK"""
        service = FinishingService(db)
        spk = service.create_stage1_spk(
            mo_id=sample_mo.id,
            target_qty=Decimal("1000"),
            buffer_pct=Decimal("0"),
        )

        assert spk is not None
        assert spk.mo_id == sample_mo.id
        assert spk.department == Department.FINISHING
        assert spk.target_qty == 1000
        assert spk.original_qty == 1000
        assert spk.production_status == "NOT_STARTED"

    def test_create_stage1_spk_with_buffer(self, db: Session, sample_mo):
        """Create Stage 1 SPK with buffer"""
        service = FinishingService(db)
        spk = service.create_stage1_spk(
            mo_id=sample_mo.id,
            target_qty=Decimal("1000"),
            buffer_pct=Decimal("10"),
        )

        # Target should be 1000 * (1 + 10/100) = 1100
        assert spk.target_qty == 1100
        assert spk.buffer_percentage == Decimal("10")

    def test_create_stage1_spk_invalid_mo(self, db: Session):
        """Create Stage 1 SPK with invalid MO"""
        service = FinishingService(db)

        with pytest.raises(ValueError, match="MO .* not found"):
            service.create_stage1_spk(
                mo_id=9999,
                target_qty=Decimal("1000"),
                buffer_pct=Decimal("0"),
            )


class TestStage1Input:
    """Test Stage 1 input/output recording"""

    def test_input_stage1_result_basic(self, db: Session, sample_mo):
        """Record basic Stage 1 result"""
        service = FinishingService(db)

        # Create Stage 1 SPK first
        spk = service.create_stage1_spk(
            mo_id=sample_mo.id,
            target_qty=Decimal("1000"),
            buffer_pct=Decimal("0"),
        )

        # Record Stage 1 output
        io = service.input_stage1_result(
            spk_id=spk.id,
            input_qty=Decimal("1000"),
            good_qty=Decimal("950"),
            defect_qty=Decimal("30"),
            rework_qty=Decimal("20"),
            filling_consumed=Decimal("15.5"),
            operator_id=3,
        )

        assert io is not None
        assert io.spk_id == spk.id
        assert io.stage == FinishingStage.STAGE_1_STUFFING
        assert io.good_qty == Decimal("950")
        assert io.defect_qty == Decimal("30")
        assert io.yield_rate == pytest.approx(95.0, 0.1)  # 950/1000*100

    def test_input_stage1_result_updates_spk(self, db: Session, sample_mo):
        """Stage 1 input updates SPK status"""
        service = FinishingService(db)

        spk = service.create_stage1_spk(
            mo_id=sample_mo.id,
            target_qty=Decimal("1000"),
            buffer_pct=Decimal("0"),
        )

        service.input_stage1_result(
            spk_id=spk.id,
            input_qty=Decimal("1000"),
            good_qty=Decimal("950"),
            defect_qty=Decimal("30"),
            rework_qty=Decimal("20"),
            filling_consumed=Decimal("15.5"),
            operator_id=3,
        )

        # Refresh SPK from DB
        db.refresh(spk)

        assert spk.good_qty == Decimal("950")
        assert spk.defect_qty == Decimal("30")
        assert spk.production_status == "COMPLETED"

    def test_input_stage1_result_invalid_spk(self, db: Session):
        """Record Stage 1 result with invalid SPK"""
        service = FinishingService(db)

        with pytest.raises(ValueError, match="SPK .* not found"):
            service.input_stage1_result(
                spk_id=9999,
                input_qty=Decimal("1000"),
                good_qty=Decimal("950"),
                defect_qty=Decimal("30"),
                rework_qty=Decimal("20"),
                filling_consumed=Decimal("15.5"),
                operator_id=3,
            )

    def test_input_stage1_result_yield_calculation(self, db: Session, sample_mo):
        """Stage 1 yield rate calculation"""
        service = FinishingService(db)

        spk = service.create_stage1_spk(
            mo_id=sample_mo.id,
            target_qty=Decimal("1000"),
            buffer_pct=Decimal("0"),
        )

        # Test various yields
        test_cases = [
            (100, 80, 15, 5, 80.0),  # 80/100 = 80%
            (1000, 900, 50, 50, 90.0),  # 900/1000 = 90%
            (500, 500, 0, 0, 100.0),  # 500/500 = 100%
        ]

        for input_qty, good_qty, defect_qty, rework_qty, expected_yield in test_cases:
            spk_temp = service.create_stage1_spk(
                mo_id=sample_mo.id,
                target_qty=Decimal(str(input_qty)),
                buffer_pct=Decimal("0"),
            )

            io = service.input_stage1_result(
                spk_id=spk_temp.id,
                input_qty=Decimal(str(input_qty)),
                good_qty=Decimal(str(good_qty)),
                defect_qty=Decimal(str(defect_qty)),
                rework_qty=Decimal(str(rework_qty)),
                filling_consumed=Decimal("0"),
                operator_id=3,
            )

            assert io.yield_rate == pytest.approx(expected_yield, 0.1)


class TestStage2Creation:
    """Test Stage 2 SPK creation"""

    def test_create_stage2_spk_basic(self, db: Session, sample_mo):
        """Create basic Stage 2 SPK"""
        service = FinishingService(db)

        # Create Stage 1 first
        spk1 = service.create_stage1_spk(
            mo_id=sample_mo.id,
            target_qty=Decimal("1000"),
            buffer_pct=Decimal("0"),
        )

        # Create Stage 2
        spk2 = service.create_stage2_spk(
            stage1_spk_id=spk1.id,
            target_qty=Decimal("950"),
        )

        assert spk2 is not None
        assert spk2.mo_id == sample_mo.id
        assert spk2.department == Department.FINISHING
        assert spk2.target_qty == 950
        assert spk2.original_qty == 950
        assert spk2.production_status == "NOT_STARTED"

    def test_create_stage2_spk_invalid_stage1(self, db: Session):
        """Create Stage 2 SPK with invalid Stage 1"""
        service = FinishingService(db)

        with pytest.raises(ValueError, match="Stage 1 SPK .* not found"):
            service.create_stage2_spk(
                stage1_spk_id=9999,
                target_qty=Decimal("950"),
            )

    def test_stage2_linked_to_stage1(self, db: Session, sample_mo):
        """Stage 2 SPK linked to Stage 1 in metadata"""
        service = FinishingService(db)

        spk1 = service.create_stage1_spk(
            mo_id=sample_mo.id,
            target_qty=Decimal("1000"),
            buffer_pct=Decimal("0"),
        )

        spk2 = service.create_stage2_spk(
            stage1_spk_id=spk1.id,
            target_qty=Decimal("950"),
        )

        # Check metadata contains Stage 1 reference
        assert f"prev_spk_id" in spk2.extra_metadata
        assert str(spk1.id) in spk2.extra_metadata


class TestStage2Input:
    """Test Stage 2 input/output recording"""

    def test_input_stage2_result_basic(self, db: Session, sample_mo):
        """Record basic Stage 2 result"""
        service = FinishingService(db)

        # Create Stage 2 SPK
        spk1 = service.create_stage1_spk(
            mo_id=sample_mo.id,
            target_qty=Decimal("1000"),
            buffer_pct=Decimal("0"),
        )

        spk2 = service.create_stage2_spk(
            stage1_spk_id=spk1.id,
            target_qty=Decimal("950"),
        )

        # Record Stage 2 output
        io = service.input_stage2_result(
            spk_id=spk2.id,
            input_qty=Decimal("950"),
            good_qty=Decimal("920"),
            defect_qty=Decimal("20"),
            rework_qty=Decimal("10"),
            thread_consumed=Decimal("2850.5"),
            operator_id=4,
        )

        assert io is not None
        assert io.spk_id == spk2.id
        assert io.stage == FinishingStage.STAGE_2_CLOSING
        assert io.good_qty == Decimal("920")
        assert io.defect_qty == Decimal("20")
        assert io.yield_rate == pytest.approx(96.842, 0.1)  # 920/950*100

    def test_input_stage2_result_updates_spk(self, db: Session, sample_mo):
        """Stage 2 input updates SPK status"""
        service = FinishingService(db)

        spk1 = service.create_stage1_spk(
            mo_id=sample_mo.id,
            target_qty=Decimal("1000"),
            buffer_pct=Decimal("0"),
        )

        spk2 = service.create_stage2_spk(
            stage1_spk_id=spk1.id,
            target_qty=Decimal("950"),
        )

        service.input_stage2_result(
            spk_id=spk2.id,
            input_qty=Decimal("950"),
            good_qty=Decimal("920"),
            defect_qty=Decimal("20"),
            rework_qty=Decimal("10"),
            thread_consumed=Decimal("2850.5"),
            operator_id=4,
        )

        # Refresh SPK from DB
        db.refresh(spk2)

        assert spk2.good_qty == Decimal("920")
        assert spk2.defect_qty == Decimal("20")
        assert spk2.production_status == "COMPLETED"


class TestEndToEndFlow:
    """Test complete Stuffing → Closing flow"""

    def test_complete_finishing_flow(self, db: Session, sample_mo):
        """Complete flow: Create Stage 1 → Input → Create Stage 2 → Input"""
        service = FinishingService(db)

        # Stage 1: Stuffing
        spk1 = service.create_stage1_spk(
            mo_id=sample_mo.id,
            target_qty=Decimal("1000"),
            buffer_pct=Decimal("5"),  # 5% buffer → target 1050
        )

        io1 = service.input_stage1_result(
            spk_id=spk1.id,
            input_qty=Decimal("1050"),
            good_qty=Decimal("950"),
            defect_qty=Decimal("50"),
            rework_qty=Decimal("50"),
            filling_consumed=Decimal("15.5"),
            operator_id=3,
        )

        assert io1.yield_rate == pytest.approx(90.476, 0.1)

        # Stage 2: Closing based on good output
        spk2 = service.create_stage2_spk(
            stage1_spk_id=spk1.id,
            target_qty=Decimal("950"),
        )

        io2 = service.input_stage2_result(
            spk_id=spk2.id,
            input_qty=Decimal("950"),
            good_qty=Decimal("920"),
            defect_qty=Decimal("20"),
            rework_qty=Decimal("10"),
            thread_consumed=Decimal("2850.5"),
            operator_id=4,
        )

        assert io2.yield_rate == pytest.approx(96.842, 0.1)

        # Verify final output
        assert spk1.good_qty == Decimal("950")
        assert spk2.good_qty == Decimal("920")

    def test_finishing_with_different_operators(self, db: Session, sample_mo):
        """Finishing uses different operators per stage"""
        service = FinishingService(db)

        spk1 = service.create_stage1_spk(
            mo_id=sample_mo.id,
            target_qty=Decimal("100"),
            buffer_pct=Decimal("0"),
        )

        io1 = service.input_stage1_result(
            spk_id=spk1.id,
            input_qty=Decimal("100"),
            good_qty=Decimal("95"),
            defect_qty=Decimal("5"),
            rework_qty=Decimal("0"),
            filling_consumed=Decimal("1.5"),
            operator_id=10,  # Operator 10
        )

        spk2 = service.create_stage2_spk(
            stage1_spk_id=spk1.id,
            target_qty=Decimal("95"),
        )

        io2 = service.input_stage2_result(
            spk_id=spk2.id,
            input_qty=Decimal("95"),
            good_qty=Decimal("92"),
            defect_qty=Decimal("3"),
            rework_qty=Decimal("0"),
            thread_consumed=Decimal("285"),
            operator_id=11,  # Different operator
        )

        assert io1.operator_id == 10
        assert io2.operator_id == 11

    @pytest.mark.parametrize(
        "input_qty,good_qty,defect_qty,rework_qty",
        [
            (1000, 900, 50, 50),
            (500, 450, 30, 20),
            (100, 95, 3, 2),
        ],
    )
    def test_finishing_multiple_scenarios(
        self, db: Session, sample_mo, input_qty, good_qty, defect_qty, rework_qty
    ):
        """Test multiple finishing scenarios"""
        service = FinishingService(db)

        spk = service.create_stage1_spk(
            mo_id=sample_mo.id,
            target_qty=Decimal(str(input_qty)),
            buffer_pct=Decimal("0"),
        )

        io = service.input_stage1_result(
            spk_id=spk.id,
            input_qty=Decimal(str(input_qty)),
            good_qty=Decimal(str(good_qty)),
            defect_qty=Decimal(str(defect_qty)),
            rework_qty=Decimal(str(rework_qty)),
            filling_consumed=Decimal("0"),
            operator_id=3,
        )

        # Verify totals
        assert (
            int(good_qty) + int(defect_qty) + int(rework_qty) == input_qty
        ), "Output sum must equal input"
        assert io.yield_rate > 0, "Yield should be positive"
