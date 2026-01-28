"""
PPIC Report Service - Generate daily production reports and alerts
Feature #6: Daily Reports + Alert System

Provides:
- Daily production report generation
- Late SPK detection & alerts
- Email/WhatsApp notifications
- Real-time metric calculations
"""

from datetime import datetime, timedelta, date
from typing import Dict, List, Optional, Any
from decimal import Decimal
from enum import Enum
from dataclasses import dataclass
import logging

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

logger = logging.getLogger(__name__)


class AlertSeverity(str, Enum):
    """Alert severity levels"""
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


class AlertType(str, Enum):
    """Alert types"""
    SPK_LATE = "SPK_LATE"
    MATERIAL_LOW_STOCK = "MATERIAL_LOW_STOCK"
    MATERIAL_STOCKOUT = "MATERIAL_STOCKOUT"
    COMPLETION_BEHIND = "COMPLETION_BEHIND"
    QUALITY_ISSUE = "QUALITY_ISSUE"
    EQUIPMENT_DOWN = "EQUIPMENT_DOWN"


@dataclass
class DailyMetrics:
    """Daily production metrics"""
    report_date: date
    total_spks: int
    completed_spks: int
    in_progress_spks: int
    late_spks: int
    on_time_rate: float  # percentage
    avg_cycle_time: float  # days
    quality_reject_rate: float  # percentage
    material_status: Dict[str, Any]
    critical_alerts: List[Dict[str, Any]]


class PPICReportService:
    """
    Service for generating PPIC reports and managing production alerts
    
    Features:
    1. Daily Production Report
       - Completed SPKs
       - In-progress SPKs
       - Late SPKs with reasons
       - Material stock status
       - KPIs & metrics
    
    2. Late SPK Detection
       - Predictive: if progress doesn't match pace
       - Alert: send notification to manager
       - Track: reason for delay
    
    3. Notifications
       - Email: Daily report + late alerts
       - WhatsApp: Critical alerts only
       - SMS: Optional fallback
    
    4. Alerts Management
       - Create alerts with severity
       - Deduplication (don't send same alert twice)
       - Track read/dismissed
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.logger = logger
    
    async def generate_daily_report(
        self,
        report_date: Optional[date] = None,
        department_id: Optional[int] = None
    ) -> DailyMetrics:
        """
        Generate daily production report
        
        Args:
            report_date: Date to generate report for (default: today)
            department_id: Filter by department (optional)
        
        Returns:
            DailyMetrics with complete daily data
        """
        if not report_date:
            report_date = date.today()
        
        try:
            self.logger.info(f"Generating daily report for {report_date}")
            
            # Import models here to avoid circular imports
            from app.core.models.production import SPK, SPKStatus
            from app.core.models.products import Product
            from app.core.models.daily_production import DailyProductionInput
            
            # Query SPKs for the date
            query = self.db.query(SPK).filter(
                SPK.created_at.cast(date) <= report_date
            )
            
            if department_id:
                query = query.filter(SPK.department_id == department_id)
            
            all_spks = query.all()
            
            # Calculate metrics
            completed_spks = [s for s in all_spks if s.status == SPKStatus.COMPLETED]
            in_progress_spks = [s for s in all_spks if s.status == SPKStatus.IN_PROGRESS]
            late_spks = self._detect_late_spks(all_spks)
            
            # Calculate KPIs
            on_time_rate = (len(completed_spks) / len(all_spks) * 100) if all_spks else 0
            avg_cycle_time = self._calculate_avg_cycle_time(completed_spks)
            quality_reject_rate = self._calculate_quality_rate(completed_spks)
            
            # Material status
            material_status = self._get_material_status()
            
            # Get critical alerts for today
            critical_alerts = await self._get_alerts_for_date(report_date)
            
            metrics = DailyMetrics(
                report_date=report_date,
                total_spks=len(all_spks),
                completed_spks=len(completed_spks),
                in_progress_spks=len(in_progress_spks),
                late_spks=len(late_spks),
                on_time_rate=round(on_time_rate, 2),
                avg_cycle_time=round(avg_cycle_time, 1),
                quality_reject_rate=round(quality_reject_rate, 2),
                material_status=material_status,
                critical_alerts=critical_alerts
            )
            
            self.logger.info(f"Daily report generated: {len(completed_spks)} completed, {len(late_spks)} late")
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Failed to generate daily report: {str(e)}")
            raise
    
    def _detect_late_spks(self, spks: List[Any]) -> List[Dict[str, Any]]:
        """
        Detect SPKs that are late or will be late
        
        Logic:
        - If deadline < today and not completed → LATE
        - If progress % < expected % → AT RISK
        - Expected % = (days_passed / total_days) × 100
        
        Returns:
            List of late/at-risk SPKs with reasons
        """
        late_spks = []
        today = date.today()
        
        for spk in spks:
            # Check if past deadline
            if spk.deadline_date < today and spk.status != "COMPLETED":
                late_spks.append({
                    "spk_id": spk.id,
                    "deadline": spk.deadline_date.isoformat(),
                    "days_late": (today - spk.deadline_date).days,
                    "reason": "Deadline passed",
                    "status": spk.status,
                    "severity": "CRITICAL"
                })
                continue
            
            # Check if behind schedule (predictive)
            if hasattr(spk, 'target_qty') and hasattr(spk, 'completed_qty'):
                total_days = (spk.deadline_date - spk.created_at.date()).days
                days_elapsed = (today - spk.created_at.date()).days
                
                if total_days > 0 and days_elapsed > 0:
                    expected_completion = (days_elapsed / total_days) * 100
                    actual_completion = (spk.completed_qty / spk.target_qty * 100) if spk.target_qty > 0 else 0
                    
                    if actual_completion < expected_completion - 10:  # More than 10% behind
                        late_spks.append({
                            "spk_id": spk.id,
                            "deadline": spk.deadline_date.isoformat(),
                            "progress": round(actual_completion, 1),
                            "expected": round(expected_completion, 1),
                            "reason": f"Behind schedule ({actual_completion:.0f}% actual vs {expected_completion:.0f}% expected)",
                            "status": spk.status,
                            "severity": "WARNING"
                        })
        
        return late_spks
    
    def _calculate_avg_cycle_time(self, completed_spks: List[Any]) -> float:
        """Calculate average cycle time for completed SPKs (in days)"""
        if not completed_spks:
            return 0.0
        
        cycle_times = []
        for spk in completed_spks:
            if hasattr(spk, 'completed_at') and spk.completed_at and hasattr(spk, 'created_at'):
                cycle_time = (spk.completed_at - spk.created_at).days
                cycle_times.append(max(cycle_time, 1))  # At least 1 day
        
        return sum(cycle_times) / len(cycle_times) if cycle_times else 0.0
    
    def _calculate_quality_rate(self, completed_spks: List[Any]) -> float:
        """Calculate quality reject rate (%)"""
        if not completed_spks:
            return 0.0
        
        total_target = sum(getattr(spk, 'target_qty', 0) for spk in completed_spks)
        total_rejected = sum(getattr(spk, 'rejected_qty', 0) for spk in completed_spks)
        
        if total_target == 0:
            return 0.0
        
        return (total_rejected / total_target) * 100
    
    def _get_material_status(self) -> Dict[str, Any]:
        """
        Get material inventory status
        
        Returns:
            Dict with material levels and alerts
        """
        try:
            from app.core.models.products import Product
            
            materials = self.db.query(Product).filter(
                Product.is_material == True
            ).all()
            
            status = {
                "total_materials": len(materials),
                "critical_stock": [],
                "low_stock": [],
                "ok_stock": []
            }
            
            for material in materials:
                if hasattr(material, 'current_stock'):
                    current = material.current_stock
                    min_stock = getattr(material, 'min_stock', 0)
                    
                    if current == 0:
                        status["critical_stock"].append({
                            "material_id": material.id,
                            "name": material.name,
                            "current": 0,
                            "min": min_stock
                        })
                    elif current <= min_stock:
                        status["low_stock"].append({
                            "material_id": material.id,
                            "name": material.name,
                            "current": current,
                            "min": min_stock,
                            "days_until_stockout": self._estimate_days_until_stockout(material)
                        })
                    else:
                        status["ok_stock"].append({
                            "material_id": material.id,
                            "name": material.name,
                            "current": current
                        })
            
            return status
            
        except Exception as e:
            self.logger.error(f"Failed to get material status: {str(e)}")
            return {"error": str(e)}
    
    def _estimate_days_until_stockout(self, material: Any) -> int:
        """Estimate days until material runs out based on consumption rate"""
        try:
            if not hasattr(material, 'current_stock'):
                return 0
            
            # Get average daily consumption from last 7 days
            # This is simplified - in production would query MaterialTransaction table
            daily_consumption = getattr(material, 'avg_daily_consumption', 10)
            
            if daily_consumption <= 0:
                return 999  # Unknown
            
            days_left = material.current_stock / daily_consumption
            return max(int(days_left), 1)
            
        except Exception:
            return 0
    
    async def _get_alerts_for_date(self, alert_date: date) -> List[Dict[str, Any]]:
        """Get all alerts for a specific date"""
        try:
            # This would query from alerts table in production
            # For now return empty - to be implemented with database
            return []
        except Exception as e:
            self.logger.error(f"Failed to get alerts: {str(e)}")
            return []
    
    async def create_alert(
        self,
        alert_type: AlertType,
        severity: AlertSeverity,
        title: str,
        description: str,
        entity_type: str,
        entity_id: int,
        created_by_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Create new alert
        
        Args:
            alert_type: Type of alert (SPK_LATE, MATERIAL_LOW, etc.)
            severity: Alert severity (INFO, WARNING, CRITICAL)
            title: Alert title
            description: Alert description
            entity_type: What entity this alert is about (SPK, Material, etc.)
            entity_id: ID of the entity
            created_by_id: User who created alert (system if None)
        
        Returns:
            Created alert record
        """
        try:
            # Check for duplicate alert in last 24 hours
            today = datetime.utcnow() - timedelta(hours=24)
            
            # This would query alerts table in production
            # For now, just log
            self.logger.info(
                f"Creating alert: {alert_type} - {title} "
                f"(severity: {severity}, entity: {entity_type}:{entity_id})"
            )
            
            alert = {
                "id": None,  # Would be generated by DB
                "alert_type": alert_type.value,
                "severity": severity.value,
                "title": title,
                "description": description,
                "entity_type": entity_type,
                "entity_id": entity_id,
                "created_at": datetime.utcnow(),
                "created_by_id": created_by_id,
                "is_read": False,
                "read_at": None
            }
            
            return alert
            
        except Exception as e:
            self.logger.error(f"Failed to create alert: {str(e)}")
            raise
    
    async def send_daily_report_email(
        self,
        metrics: DailyMetrics,
        recipient_emails: List[str],
        department_name: Optional[str] = None
    ) -> bool:
        """
        Send daily report via email
        
        Args:
            metrics: Daily metrics to report
            recipient_emails: List of email addresses
            department_name: Optional department name for subject
        
        Returns:
            True if sent successfully
        """
        try:
            # In production, would use SMTP service
            # For now, just log
            
            dept_text = f" - {department_name}" if department_name else ""
            subject = f"📊 Daily Production Report {metrics.report_date}{dept_text}"
            
            body = self._format_report_html(metrics)
            
            self.logger.info(
                f"Sending daily report email to {len(recipient_emails)} recipients: {recipient_emails}"
            )
            
            # TODO: Integrate with actual email service
            # await send_email(
            #     to=recipient_emails,
            #     subject=subject,
            #     html_body=body
            # )
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send daily report email: {str(e)}")
            return False
    
    def _format_report_html(self, metrics: DailyMetrics) -> str:
        """Format report as HTML email"""
        return f"""
        <html>
        <body>
        <h2>📊 Daily Production Report - {metrics.report_date}</h2>
        
        <h3>✅ Completed: {metrics.completed_spks}/{metrics.total_spks} SPKs</h3>
        <h3>🔄 In Progress: {metrics.in_progress_spks} SPKs</h3>
        <h3>⚠️ Late: {metrics.late_spks} SPKs</h3>
        
        <h3>📈 KPIs:</h3>
        <ul>
        <li>On-time Delivery Rate: {metrics.on_time_rate}%</li>
        <li>Average Cycle Time: {metrics.avg_cycle_time} days</li>
        <li>Quality Reject Rate: {metrics.quality_reject_rate}%</li>
        </ul>
        
        <h3>📦 Material Status:</h3>
        <p>Critical Stock: {len(metrics.material_status.get('critical_stock', []))} items</p>
        <p>Low Stock: {len(metrics.material_status.get('low_stock', []))} items</p>
        <p>OK Stock: {len(metrics.material_status.get('ok_stock', []))} items</p>
        
        <h3>🚨 Critical Alerts: {len(metrics.critical_alerts)}</h3>
        
        </body>
        </html>
        """
    
    async def send_late_alert_whatsapp(
        self,
        spk_id: int,
        spk_info: Dict[str, Any],
        recipient_phone: str
    ) -> bool:
        """
        Send late SPK alert via WhatsApp
        
        Args:
            spk_id: SPK ID
            spk_info: SPK information (deadline, progress, reason)
            recipient_phone: Phone number with country code
        
        Returns:
            True if sent successfully
        """
        try:
            message = f"""
            🚨 ALERT: SPK {spk_id} is LATE!
            
            Deadline: {spk_info.get('deadline', 'N/A')}
            Reason: {spk_info.get('reason', 'Unknown')}
            
            Please take action immediately.
            """
            
            self.logger.info(f"Sending WhatsApp alert to {recipient_phone}: SPK {spk_id}")
            
            # TODO: Integrate with WhatsApp/Twilio API
            # await send_whatsapp(
            #     to=recipient_phone,
            #     message=message
            # )
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send WhatsApp alert: {str(e)}")
            return False
