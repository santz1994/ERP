"""
Audit Trail Utilities
Helper functions for logging audit events
"""
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional, Dict, Any
from app.core.models.audit import AuditLog, AuditAction, AuditModule, UserActivityLog, SecurityLog
from app.core.models.users import User


class AuditLogger:
    """Centralized audit logging utility"""
    
    @staticmethod
    def log_action(
        db: Session,
        user: Optional[User],
        action: AuditAction,
        module: AuditModule,
        description: str,
        entity_type: Optional[str] = None,
        entity_id: Optional[int] = None,
        old_values: Optional[Dict[str, Any]] = None,
        new_values: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        request_method: Optional[str] = None,
        request_path: Optional[str] = None,
        response_status: Optional[int] = None
    ):
        """
        Log an audit event
        
        Args:
            db: Database session
            user: User performing the action (None for system actions)
            action: Type of action (CREATE, UPDATE, DELETE, etc.)
            module: System module where action occurred
            description: Human-readable description
            entity_type: Type of entity affected (e.g., "ManufacturingOrder")
            entity_id: ID of affected record
            old_values: Previous values (for UPDATE)
            new_values: New values (for CREATE/UPDATE)
            ip_address: User's IP address
            request_method: HTTP method
            request_path: Request URL path
            response_status: HTTP response status code
        """
        log = AuditLog(
            user_id=user.id if user else None,
            username=user.username if user else "System",
            user_role=user.role.value if user else "System",
            ip_address=ip_address,
            action=action,
            module=module,
            entity_type=entity_type,
            entity_id=entity_id,
            description=description,
            old_values=old_values,
            new_values=new_values,
            request_method=request_method,
            request_path=request_path,
            response_status=response_status
        )
        
        db.add(log)
        db.commit()
        
        return log
    
    @staticmethod
    def log_create(
        db: Session,
        user: User,
        module: AuditModule,
        entity_type: str,
        entity_id: int,
        values: Dict[str, Any],
        description: Optional[str] = None
    ):
        """Log creation of new record"""
        if not description:
            description = f"Created {entity_type} #{entity_id}"
        
        return AuditLogger.log_action(
            db=db,
            user=user,
            action=AuditAction.CREATE,
            module=module,
            description=description,
            entity_type=entity_type,
            entity_id=entity_id,
            new_values=values
        )
    
    @staticmethod
    def log_update(
        db: Session,
        user: User,
        module: AuditModule,
        entity_type: str,
        entity_id: int,
        old_values: Dict[str, Any],
        new_values: Dict[str, Any],
        description: Optional[str] = None
    ):
        """Log update of existing record"""
        if not description:
            changed_fields = list(new_values.keys())
            description = f"Updated {entity_type} #{entity_id}: {', '.join(changed_fields)}"
        
        return AuditLogger.log_action(
            db=db,
            user=user,
            action=AuditAction.UPDATE,
            module=module,
            description=description,
            entity_type=entity_type,
            entity_id=entity_id,
            old_values=old_values,
            new_values=new_values
        )
    
    @staticmethod
    def log_delete(
        db: Session,
        user: User,
        module: AuditModule,
        entity_type: str,
        entity_id: int,
        values: Dict[str, Any],
        description: Optional[str] = None
    ):
        """Log deletion of record"""
        if not description:
            description = f"Deleted {entity_type} #{entity_id}"
        
        return AuditLogger.log_action(
            db=db,
            user=user,
            action=AuditAction.DELETE,
            module=module,
            description=description,
            entity_type=entity_type,
            entity_id=entity_id,
            old_values=values
        )
    
    @staticmethod
    def log_transfer(
        db: Session,
        user: User,
        module: AuditModule,
        from_dept: str,
        to_dept: str,
        article_code: str,
        qty: int,
        transfer_id: int
    ):
        """Log department transfer"""
        description = f"Transfer {qty} units of {article_code} from {from_dept} to {to_dept}"
        
        return AuditLogger.log_action(
            db=db,
            user=user,
            action=AuditAction.TRANSFER,
            module=module,
            description=description,
            entity_type="TransferLog",
            entity_id=transfer_id,
            new_values={
                "from_dept": from_dept,
                "to_dept": to_dept,
                "article_code": article_code,
                "qty": qty
            }
        )
    
    @staticmethod
    def log_approval(
        db: Session,
        user: User,
        module: AuditModule,
        entity_type: str,
        entity_id: int,
        description: str
    ):
        """Log approval action"""
        return AuditLogger.log_action(
            db=db,
            user=user,
            action=AuditAction.APPROVE,
            module=module,
            description=description,
            entity_type=entity_type,
            entity_id=entity_id
        )
    
    @staticmethod
    def log_login(
        db: Session,
        user: User,
        ip_address: str,
        success: bool = True
    ):
        """Log user login attempt"""
        if success:
            description = f"User {user.username} logged in successfully"
            action = AuditAction.LOGIN
        else:
            description = f"Failed login attempt for user {user.username}"
            action = AuditAction.LOGIN
            
            # Also log to security log
            SecurityLogger.log_failed_login(
                db=db,
                username=user.username,
                ip_address=ip_address
            )
        
        return AuditLogger.log_action(
            db=db,
            user=user if success else None,
            action=action,
            module=AuditModule.AUTH,
            description=description,
            ip_address=ip_address
        )
    
    @staticmethod
    def log_export(
        db: Session,
        user: User,
        module: AuditModule,
        export_type: str,
        filters: Dict[str, Any]
    ):
        """Log data export"""
        description = f"Exported {export_type} data"
        
        return AuditLogger.log_action(
            db=db,
            user=user,
            action=AuditAction.EXPORT,
            module=module,
            description=description,
            entity_type=export_type,
            new_values=filters
        )


class SecurityLogger:
    """Security event logging"""
    
    @staticmethod
    def log_failed_login(
        db: Session,
        username: str,
        ip_address: str,
        user_id: Optional[int] = None
    ):
        """Log failed login attempt"""
        log = SecurityLog(
            ip_address=ip_address,
            event_type="failed_login",
            severity="warning",
            user_id=user_id,
            username_attempted=username,
            description=f"Failed login attempt for username: {username}"
        )
        
        db.add(log)
        db.commit()
        
        # Check if account should be locked
        from datetime import timedelta
        recent_failures = db.query(SecurityLog).filter(
            SecurityLog.username_attempted == username,
            SecurityLog.event_type == "failed_login",
            SecurityLog.timestamp >= datetime.now() - timedelta(minutes=15)
        ).count()
        
        if recent_failures >= 5:
            log.action_taken = "account_locked"
            db.commit()
        
        return log
    
    @staticmethod
    def log_unauthorized_access(
        db: Session,
        user: User,
        ip_address: str,
        attempted_action: str,
        resource: str
    ):
        """Log unauthorized access attempt"""
        log = SecurityLog(
            ip_address=ip_address,
            event_type="unauthorized_access",
            severity="critical",
            user_id=user.id,
            username_attempted=user.username,
            description=f"User {user.username} attempted unauthorized action: {attempted_action} on {resource}",
            action_taken="access_denied"
        )
        
        db.add(log)
        db.commit()
        
        return log


class ActivityLogger:
    """User activity tracking"""
    
    @staticmethod
    def log_activity(
        db: Session,
        user: User,
        activity_type: str,
        details: Optional[str] = None,
        session_id: Optional[str] = None,
        ip_address: Optional[str] = None
    ):
        """Log user activity"""
        log = UserActivityLog(
            user_id=user.id,
            activity_type=activity_type,
            activity_details=details,
            session_id=session_id,
            ip_address=ip_address
        )
        
        db.add(log)
        db.commit()
        
        return log


# Alias for backward compatibility
log_audit = AuditLogger.log_action
