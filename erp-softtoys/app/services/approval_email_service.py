"""
Email notification service for approval workflow
Sends email notifications when approval action is needed
"""

from typing import Dict, List, Any
from datetime import datetime
from jinja2 import Template
import asyncio
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class ApprovalEmailService:
    """Service to send approval-related emails"""

    def __init__(self, smtp_config: Dict[str, Any]):
        """
        Initialize email service
        
        Args:
            smtp_config: Dict with keys:
                - smtp_host: SMTP server hostname
                - smtp_port: SMTP server port
                - smtp_user: SMTP authentication user
                - smtp_password: SMTP authentication password
                - from_email: Email address to send from
                - from_name: Display name for sender
        """
        self.smtp_config = smtp_config
        self.template_dir = Path(__file__).parent.parent / "templates" / "emails"

    async def send_approval_request_email(
        self,
        approver_email: str,
        approver_name: str,
        entity_type: str,
        entity_type_label: str,
        approval_request_id: str,
        submitted_by_name: str,
        submitted_by_email: str,
        submitted_at: str,
        reason: str,
        changes: Dict[str, Any],
        approval_chain: List[str],
        current_step: int,
        approve_url: str,
        reject_url: str,
        dashboard_url: str,
        priority: str = "NORMAL",
        deadline: str = None,
    ) -> bool:
        """
        Send approval request email
        
        Args:
            approver_email: Email of the approver
            approver_name: Name of the approver
            entity_type: Type of entity (SPK_CREATE, etc)
            entity_type_label: Label for entity type (e.g., "Buat SPK")
            approval_request_id: UUID of approval request
            submitted_by_name: Name of person who submitted
            submitted_by_email: Email of person who submitted
            submitted_at: ISO datetime of submission
            reason: Reason for change
            changes: Dict of changes
            approval_chain: List of approval roles
            current_step: Current step index (0-based)
            approve_url: URL to approve
            reject_url: URL to reject
            dashboard_url: URL to dashboard
            priority: NORMAL, HIGH, URGENT
            deadline: Optional deadline datetime
        
        Returns:
            True if email sent successfully, False otherwise
        """
        try:
            # Load template
            template_path = self.template_dir / "ppic_approval_request.html"
            if not template_path.exists():
                logger.error(f"Email template not found: {template_path}")
                return False

            with open(template_path, 'r', encoding='utf-8') as f:
                template_content = f.read()

            # Prepare context
            context = {
                'approver_name': approver_name,
                'entity_type': entity_type,
                'entity_type_label': entity_type_label,
                'approval_request_id': approval_request_id,
                'submitted_by_name': submitted_by_name,
                'submitted_by_email': submitted_by_email,
                'submitted_at': submitted_at,
                'reason': reason,
                'changes': changes,
                'approval_chain': approval_chain,
                'current_step': current_step,
                'approve_url': approve_url,
                'reject_url': reject_url,
                'dashboard_url': dashboard_url,
                'priority': priority,
                'deadline': deadline,
                'format_datetime': self._format_datetime,
                'enumerate': enumerate,
            }

            # Render template
            template = Template(template_content)
            html_content = template.render(**context)

            # Send email asynchronously
            asyncio.create_task(
                self._send_smtp_email(
                    to_email=approver_email,
                    to_name=approver_name,
                    subject=f"Persetujuan Dibutuhkan: {entity_type_label}",
                    html_content=html_content,
                )
            )

            logger.info(f"Approval email queued for {approver_email}")
            return True

        except Exception as e:
            logger.error(f"Error sending approval email: {str(e)}")
            return False

    async def send_approval_decision_email(
        self,
        submitter_email: str,
        submitter_name: str,
        entity_type_label: str,
        decision: str,  # APPROVED or REJECTED
        approver_name: str,
        decision_notes: str,
        approval_request_id: str,
        next_step: str = None,
        view_url: str = None,
    ) -> bool:
        """
        Send approval decision email to submitter
        
        Args:
            submitter_email: Email of person who submitted
            submitter_name: Name of person who submitted
            entity_type_label: Label for entity type
            decision: APPROVED or REJECTED
            approver_name: Name of approver
            decision_notes: Notes/reason for decision
            approval_request_id: UUID of approval request
            next_step: Next approval step (if approved)
            view_url: URL to view status
        
        Returns:
            True if email sent successfully
        """
        try:
            # Prepare email content
            if decision == "APPROVED":
                subject = f"✅ Persetujuan Diterima: {entity_type_label}"
                status_color = "green"
                status_text = "DISETUJUI"
            else:
                subject = f"❌ Persetujuan Ditolak: {entity_type_label}"
                status_color = "red"
                status_text = "DITOLAK"

            # Simple HTML content (could be enhanced with full template)
            html_content = f"""
            <html>
            <body style="font-family: Arial; background-color: #f5f5f5; margin: 0; padding: 20px;">
                <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 8px;">
                    <h2 style="color: {'#10b981' if decision == 'APPROVED' else '#ef4444'}; margin-bottom: 20px;">
                        {subject}
                    </h2>
                    
                    <p>Halo <strong>{submitter_name}</strong>,</p>
                    
                    <p>Persetujuan Anda untuk <strong>{entity_type_label}</strong> (ID: <code>{approval_request_id}</code>) telah <strong style="color: {'#10b981' if decision == 'APPROVED' else '#ef4444'}">{status_text}</strong> oleh <strong>{approver_name}</strong>.</p>
                    
                    <div style="background-color: {'#f0fdf4' if decision == 'APPROVED' else '#fef2f2'}; padding: 15px; border-left: 4px solid {'#10b981' if decision == 'APPROVED' else '#ef4444'}; margin: 20px 0; border-radius: 4px;">
                        <p style="margin: 0; font-weight: 600; color: {'#065f46' if decision == 'APPROVED' else '#7f1d1d'};">Catatan Approver:</p>
                        <p style="margin: 10px 0 0 0;">{decision_notes}</p>
                    </div>
                    
                    {'<p style="font-size: 14px; color: #666; margin: 20px 0;"><strong>Langkah Selanjutnya:</strong> Permintaan Anda telah diteruskan ke ' + next_step + ' untuk persetujuan lanjutan.</p>' if next_step else ''}
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{view_url}" style="display: inline-block; padding: 12px 30px; background-color: #667eea; color: white; text-decoration: none; border-radius: 6px; font-weight: 600;">Lihat Status Lengkap</a>
                    </div>
                    
                    <hr style="border: none; border-top: 1px solid #e5e5e5; margin: 30px 0;">
                    <p style="font-size: 12px; color: #999; margin: 0;">
                        ERP Quty Karunia | Sistem Manajemen Produksi<br/>
                        Email ini dikirim secara otomatis.
                    </p>
                </div>
            </body>
            </html>
            """

            # Send email asynchronously
            asyncio.create_task(
                self._send_smtp_email(
                    to_email=submitter_email,
                    to_name=submitter_name,
                    subject=subject,
                    html_content=html_content,
                )
            )

            logger.info(f"Decision email sent to {submitter_email}")
            return True

        except Exception as e:
            logger.error(f"Error sending decision email: {str(e)}")
            return False

    async def _send_smtp_email(
        self,
        to_email: str,
        to_name: str,
        subject: str,
        html_content: str,
    ) -> bool:
        """
        Send email via SMTP (runs asynchronously)
        
        Args:
            to_email: Recipient email
            to_name: Recipient name
            subject: Email subject
            html_content: HTML email body
        
        Returns:
            True if sent successfully
        """
        try:
            import aiosmtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart
            from email.header import Header

            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = f"{self.smtp_config['from_name']} <{self.smtp_config['from_email']}>"
            msg['To'] = f"{to_name} <{to_email}>"
            msg['Subject'] = Header(subject, 'utf-8')

            # Attach HTML
            html_part = MIMEText(html_content, 'html', 'utf-8')
            msg.attach(html_part)

            # Send via SMTP
            async with aiosmtplib.SMTP(
                hostname=self.smtp_config['smtp_host'],
                port=self.smtp_config['smtp_port'],
            ) as smtp:
                if self.smtp_config.get('smtp_use_tls', True):
                    await smtp.starttls()

                await smtp.login(
                    self.smtp_config['smtp_user'],
                    self.smtp_config['smtp_password']
                )

                await smtp.send_message(msg)
                logger.info(f"Email sent to {to_email}: {subject}")
                return True

        except Exception as e:
            logger.error(f"SMTP error: {str(e)}")
            return False

    @staticmethod
    def _format_datetime(dt_str: str, format_str: str = "%d %B %Y %H:%M") -> str:
        """Format datetime string"""
        try:
            dt = datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
            return dt.strftime(format_str)
        except:
            return dt_str


# Singleton instance
_email_service: ApprovalEmailService = None


def init_approval_email_service(smtp_config: Dict[str, Any]) -> ApprovalEmailService:
    """Initialize the email service (call once on app startup)"""
    global _email_service
    _email_service = ApprovalEmailService(smtp_config)
    return _email_service


def get_approval_email_service() -> ApprovalEmailService:
    """Get the email service instance"""
    if _email_service is None:
        raise RuntimeError("Email service not initialized. Call init_approval_email_service first.")
    return _email_service
