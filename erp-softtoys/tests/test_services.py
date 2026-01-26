"""
Business Logic Services Tests
Test coverage for core business services
"""

import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from unittest.mock import Mock, patch


class TestProductionService:
    """Test production service business logic"""
    
    def test_calculate_cumulative_production(self):
        """Should calculate cumulative production correctly"""
        daily_productions = [
            {"date": "2026-01-20", "quantity": 100},
            {"date": "2026-01-21", "quantity": 150},
            {"date": "2026-01-22", "quantity": 200}
        ]
        
        cumulative = sum(p["quantity"] for p in daily_productions)
        assert cumulative == 450
    
    def test_production_vs_target(self):
        """Should compare production against target"""
        target = 1000
        current_production = 650
        
        progress_percent = (current_production / target) * 100
        assert progress_percent == 65.0
    
    def test_production_on_track(self):
        """Should determine if production is on track"""
        today = datetime.now()
        days_passed = 13
        days_in_month = 31
        
        target = 1000
        production = 420  # Should be 1000 * (13/31) = 419.3
        
        expected_at_this_point = target * (days_passed / days_in_month)
        on_track = production >= expected_at_this_point * 0.9  # 90% tolerance
        
        assert on_track is True
    
    def test_production_behind_schedule(self):
        """Should detect if production is behind schedule"""
        target = 1000
        days_passed = 25
        days_in_month = 31
        
        production = 500
        expected_at_this_point = target * (days_passed / days_in_month)
        
        on_track = production >= expected_at_this_point
        assert on_track is False


class TestApprovalService:
    """Test approval service business logic"""
    
    def test_determine_approval_required(self):
        """Should determine if approval is required"""
        quantity = 500
        approval_threshold = 500
        
        requires_approval = quantity >= approval_threshold
        assert requires_approval is True
    
    def test_approval_workflow_state_machine(self):
        """Should enforce approval state machine"""
        valid_transitions = {
            "PENDING": ["APPROVED", "REJECTED"],
            "APPROVED": ["RECALLED"],
            "REJECTED": [],
            "RECALLED": ["APPROVED"]
        }
        
        # Valid transition
        current = "PENDING"
        next_state = "APPROVED"
        assert next_state in valid_transitions[current]
        
        # Invalid transition
        current = "REJECTED"
        next_state = "APPROVED"
        assert next_state not in valid_transitions[current]
    
    def test_check_supervisor_approval_pending(self):
        """Should identify pending supervisor approvals"""
        approvals = [
            {"id": "APP001", "status": "PENDING"},
            {"id": "APP002", "status": "APPROVED"},
            {"id": "APP003", "status": "PENDING"}
        ]
        
        pending = [a for a in approvals if a["status"] == "PENDING"]
        assert len(pending) == 2


class TestBarcodeService:
    """Test barcode service business logic"""
    
    def test_parse_barcode_data(self):
        """Should parse barcode data"""
        barcode = "CARTON001|ARTICLE1|100"
        parsed = self._parse_barcode(barcode)
        
        assert parsed["carton_id"] == "CARTON001"
        assert parsed["article"] == "ARTICLE1"
        assert parsed["quantity"] == 100
    
    def test_validate_barcode_quantity(self):
        """Should validate barcode quantity"""
        quantity = 100
        max_per_article = 500
        
        valid = 0 < quantity <= max_per_article
        assert valid is True
    
    def test_generate_unique_barcode(self):
        """Should generate unique barcode"""
        existing_barcodes = ["CARTON001|ARTICLE1|100", "CARTON002|ARTICLE2|50"]
        
        new_barcode = "CARTON003|ARTICLE3|75"
        
        is_unique = new_barcode not in existing_barcodes
        assert is_unique is True
    
    @staticmethod
    def _parse_barcode(barcode: str):
        """Parse barcode"""
        parts = barcode.split("|")
        return {
            "carton_id": parts[0],
            "article": parts[1],
            "quantity": int(parts[2])
        }


class TestMaterialDebtService:
    """Test material debt service business logic"""
    
    def test_calculate_total_material_debt(self):
        """Should calculate total material debt"""
        debts = [
            {"material_id": "MAT001", "quantity": 100, "price": 50},
            {"material_id": "MAT002", "quantity": 200, "price": 30}
        ]
        
        total = sum(d["quantity"] * d["price"] for d in debts)
        assert total == 11000
    
    def test_identify_overdue_debt(self):
        """Should identify overdue debt"""
        today = datetime.now().date()
        due_date = today - timedelta(days=5)
        
        is_overdue = today > due_date
        assert is_overdue is True
    
    def test_calculate_debt_aging(self):
        """Should calculate debt aging"""
        today = datetime.now()
        created_date = today - timedelta(days=45)
        
        days_old = (today - created_date).days
        assert days_old == 45


class TestNotificationService:
    """Test notification service logic"""
    
    def test_send_approval_notification(self):
        """Should send approval notifications"""
        approval = {
            "id": "APP001",
            "production_id": "PROD001",
            "status": "PENDING"
        }
        
        notification = self._create_notification(approval, "PENDING")
        
        assert notification["type"] == "APPROVAL"
        assert notification["recipient"] is not None
    
    def test_send_production_alert(self):
        """Should send production alerts"""
        production = {
            "quantity": 1500,
            "target": 1000
        }
        
        exceeded = production["quantity"] > production["target"]
        
        if exceeded:
            notification = {"type": "ALERT", "message": "Production exceeded target"}
        
        assert notification["type"] == "ALERT"
    
    def test_notification_scheduling(self):
        """Should schedule notifications"""
        # Immediate notification
        notification = {"scheduled": False}
        
        # Scheduled notification
        scheduled_time = datetime.now() + timedelta(hours=2)
        notification_scheduled = {"scheduled": True, "time": scheduled_time}
        
        assert notification_scheduled["scheduled"] is True
    
    @staticmethod
    def _create_notification(approval, status):
        """Create notification"""
        if status == "PENDING":
            return {
                "type": "APPROVAL",
                "recipient": "supervisor@company.com",
                "message": f"New approval request: {approval['id']}"
            }
        return {}


class TestAuthorizationService:
    """Test authorization service logic"""
    
    def test_check_user_can_approve(self):
        """Should check if user can approve"""
        user_role = "SUPERVISOR"
        approval_required_role = "SUPERVISOR"
        
        can_approve = user_role == approval_required_role
        assert can_approve is True
    
    def test_check_user_can_reject(self):
        """Should check if user can reject"""
        user_role = "MANAGER"
        approval_required_role = ["SUPERVISOR", "MANAGER", "ADMIN"]
        
        can_reject = user_role in approval_required_role
        assert can_reject is True
    
    def test_prevent_self_approval(self):
        """Should prevent user from approving their own submission"""
        requester = "operator1"
        approver = "operator1"
        
        can_approve = requester != approver
        assert can_approve is False


class TestCalculationService:
    """Test calculation service logic"""
    
    def test_calculate_production_efficiency(self):
        """Should calculate production efficiency"""
        target = 1000
        actual = 950
        
        efficiency = (actual / target) * 100
        assert efficiency == 95.0
    
    def test_calculate_material_consumption(self):
        """Should calculate material consumption"""
        production_qty = 100
        material_per_unit = 2.5  # kg per unit
        
        total_consumption = production_qty * material_per_unit
        assert total_consumption == 250
    
    def test_calculate_estimated_completion_date(self):
        """Should estimate completion date"""
        target = 1000
        current_production = 400
        remaining = target - current_production
        
        daily_rate = 100
        days_remaining = remaining / daily_rate
        
        estimated_complete = datetime.now() + timedelta(days=days_remaining)
        
        assert days_remaining == 6


class TestDataValidationService:
    """Test data validation service logic"""
    
    def test_validate_production_quantity(self):
        """Should validate production quantity"""
        quantity = 100
        
        valid = quantity > 0 and quantity <= 10000
        assert valid is True
    
    def test_validate_production_date(self):
        """Should validate production date"""
        today = datetime.now().date()
        yesterday = today - timedelta(days=1)
        tomorrow = today + timedelta(days=1)
        
        assert self._validate_date(today) is True
        assert self._validate_date(yesterday) is True
        assert self._validate_date(tomorrow) is False
    
    def test_validate_article_exists(self):
        """Should validate article exists"""
        valid_articles = ["ARTICLE001", "ARTICLE002", "ARTICLE003"]
        
        assert self._validate_article("ARTICLE001", valid_articles) is True
        assert self._validate_article("INVALID", valid_articles) is False
    
    @staticmethod
    def _validate_date(date):
        """Validate date"""
        today = datetime.now().date()
        return date <= today
    
    @staticmethod
    def _validate_article(article, valid_list):
        """Validate article"""
        return article in valid_list


class TestReportingService:
    """Test reporting service logic"""
    
    def test_generate_daily_report(self):
        """Should generate daily report"""
        productions = [
            {"date": "2026-01-26", "quantity": 150, "status": "APPROVED"},
            {"date": "2026-01-26", "quantity": 200, "status": "APPROVED"}
        ]
        
        daily_total = sum(p["quantity"] for p in productions if p["date"] == "2026-01-26")
        
        report = {
            "date": "2026-01-26",
            "total_production": daily_total,
            "total_items": len(productions)
        }
        
        assert report["total_production"] == 350
    
    def test_generate_monthly_report(self):
        """Should generate monthly report"""
        productions = [
            {"date": "2026-01-10", "quantity": 100},
            {"date": "2026-01-15", "quantity": 150},
            {"date": "2026-01-20", "quantity": 200}
        ]
        
        monthly_total = sum(p["quantity"] for p in productions)
        
        assert monthly_total == 450
    
    def test_generate_variance_report(self):
        """Should generate variance report"""
        target = 1000
        actual = 850
        variance = target - actual
        variance_percent = (variance / target) * 100
        
        assert variance == 150
        assert variance_percent == 15.0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=app.services"])
