"""SQLAlchemy Event Listeners for Audit Trail
Automatically logs changes to critical business entities.

ISO 27001 A.12.4.1: Event Logging
SOX 404: Financial Transaction Traceability
"""
from datetime import datetime
from typing import Any

from sqlalchemy import event


def get_model_dict(instance, exclude_fields=None) -> dict[str, Any]:
    """Convert SQLAlchemy model to dict for audit logging."""
    if exclude_fields is None:
        exclude_fields = ['_sa_instance_state', 'created_at', 'updated_at']

    result = {}
    for column in instance.__table__.columns:
        field_name = column.name
        if field_name not in exclude_fields:
            value = getattr(instance, field_name)
            # Convert datetime to string for JSON serialization
            if isinstance(value, datetime):
                value = value.isoformat()
            result[field_name] = value

    return result


def get_changed_fields(instance) -> dict[str, Any]:
    """Get only changed fields from SQLAlchemy instance."""
    from sqlalchemy.inspect import inspect

    changed = {}
    insp = inspect(instance)

    for attr in insp.attrs:
        hist = attr.load_history()
        if hist.has_changes():
            field_name = attr.key
            if field_name not in ['_sa_instance_state', 'created_at', 'updated_at']:
                old_value = hist.deleted[0] if hist.deleted else None
                new_value = hist.added[0] if hist.added else None

                # Convert datetime to string
                if isinstance(old_value, datetime):
                    old_value = old_value.isoformat()
                if isinstance(new_value, datetime):
                    new_value = new_value.isoformat()

                changed[field_name] = {
                    'old': old_value,
                    'new': new_value
                }

    return changed


def setup_audit_listeners():
    """Initialize all audit event listeners
    Call this during application startup.
    """
    # Import here to avoid circular imports
    from app.core.database import SessionLocal
    from app.core.models.audit import AuditAction, AuditLog, AuditModule
    from app.core.models.manufacturing import ManufacturingOrder, WorkOrder
    from app.core.models.transfer import TransferLog
    from app.core.models.warehouse import PurchaseOrder, StockQuant

    # ============================================================================
    # PURCHASE ORDER AUDIT (Financial Transactions - SOX 404 Compliance)
    # ============================================================================

    @event.listens_for(PurchaseOrder, 'after_insert')
    def log_purchase_order_create(mapper, connection, target):
        """Log PO creation - Critical for Segregation of Duties."""
        try:
            db = SessionLocal()

            values = get_model_dict(target)

            # Get supplier name for description (supplier_id links to Partner)
            supplier_name = f"Supplier#{target.supplier_id}"

            audit_log = AuditLog(
                user_id=getattr(target, '_audit_user_id', None),
                username=getattr(target, '_audit_username', 'System'),
                user_role=getattr(target, '_audit_user_role', None),
                ip_address=getattr(target, '_audit_ip_address', None),
                action=AuditAction.CREATE,
                module=AuditModule.WAREHOUSE,
                entity_type='PurchaseOrder',
                entity_id=target.id,
                description=f"Created Purchase Order #{target.po_number} for {supplier_name}",
                new_values=values,
                request_method='POST',
                request_path='/api/v1/purchasing/purchase-order'
            )

            db.add(audit_log)
            db.commit()
            db.close()
        except Exception:
            pass


    @event.listens_for(PurchaseOrder, 'after_update')
    def log_purchase_order_update(mapper, connection, target):
        """Log PO updates - Track status changes and approvals."""
        try:
            db = SessionLocal()

            changed = get_changed_fields(target)
            if not changed:
                return

            # Special handling for approval
            if 'status' in changed and changed['status']['new'] == 'approved':
                action = AuditAction.APPROVE
                description = f"Approved Purchase Order #{target.po_number}"
            else:
                action = AuditAction.UPDATE
                description = f"Updated Purchase Order #{target.po_number}: {', '.join(changed.keys())}"

            audit_log = AuditLog(
                user_id=getattr(target, '_audit_user_id', None),
                username=getattr(target, '_audit_username', 'System'),
                user_role=getattr(target, '_audit_user_role', None),
                ip_address=getattr(target, '_audit_ip_address', None),
                action=action,
                module=AuditModule.WAREHOUSE,
                entity_type='PurchaseOrder',
                entity_id=target.id,
                description=description,
                old_values={k: v['old'] for k, v in changed.items()},
                new_values={k: v['new'] for k, v in changed.items()},
                request_method='PUT',
                request_path=f'/api/v1/purchasing/purchase-order/{target.id}'
            )

            db.add(audit_log)
            db.commit()
            db.close()
        except Exception:
            pass


    @event.listens_for(PurchaseOrder, 'after_delete')
    def log_purchase_order_delete(mapper, connection, target):
        """Log PO deletion - Critical financial event."""
        try:
            db = SessionLocal()

            values = get_model_dict(target)

            audit_log = AuditLog(
                user_id=getattr(target, '_audit_user_id', None),
                username=getattr(target, '_audit_username', 'System'),
                user_role=getattr(target, '_audit_user_role', None),
                ip_address=getattr(target, '_audit_ip_address', None),
                action=AuditAction.DELETE,
                module=AuditModule.WAREHOUSE,
                entity_type='PurchaseOrder',
                entity_id=target.id,
                description=f"Deleted Purchase Order #{target.po_number}",
                old_values=values,
                request_method='DELETE',
                request_path=f'/api/v1/purchasing/purchase-order/{target.id}'
            )

            db.add(audit_log)
            db.commit()
            db.close()
        except Exception:
            pass


    # ============================================================================
    # STOCK MOVEMENT AUDIT (Inventory Traceability - FIFO Compliance)
    # ============================================================================

    @event.listens_for(StockQuant, 'after_update')
    def log_stock_update(mapper, connection, target):
        """Log stock quantity changes - Critical for FIFO traceability."""
        try:
            db = SessionLocal()

            changed = get_changed_fields(target)
            if not changed or 'qty_on_hand' not in changed:
                return

            old_qty = changed['qty_on_hand']['old']
            new_qty = changed['qty_on_hand']['new']
            qty_diff = new_qty - old_qty

            # Get product code and location name for description
            product_code = target.product.code if target.product else f"Product#{target.product_id}"
            location_name = target.location.name if target.location else f"Location#{target.location_id}"

            audit_log = AuditLog(
                user_id=getattr(target, '_audit_user_id', None),
                username=getattr(target, '_audit_username', 'System'),
                user_role=getattr(target, '_audit_user_role', None),
                ip_address=getattr(target, '_audit_ip_address', None),
                action=AuditAction.UPDATE,
                module=AuditModule.WAREHOUSE,
                entity_type='StockQuant',
                entity_id=target.id,
                description=f"Stock adjusted for {product_code} in {location_name}: {old_qty} → {new_qty} ({qty_diff:+d})",
                old_values={k: v['old'] for k, v in changed.items()},
                new_values={k: v['new'] for k, v in changed.items()},
                request_method='PUT',
                request_path='/api/v1/warehouse/stock'
            )

            db.add(audit_log)
            db.commit()
            db.close()
        except Exception:
            pass


    @event.listens_for(TransferLog, 'after_insert')
    def log_transfer_create(mapper, connection, target):
        """Log inter-departmental transfers - QT-09 protocol compliance."""
        try:
            db = SessionLocal()

            values = get_model_dict(target)

            audit_log = AuditLog(
                user_id=getattr(target, '_audit_user_id', None),
                username=getattr(target, '_audit_username', 'System'),
                user_role=getattr(target, '_audit_user_role', None),
                ip_address=getattr(target, '_audit_ip_address', None),
                action=AuditAction.TRANSFER,
                module=AuditModule.WAREHOUSE,
                entity_type='TransferLog',
                entity_id=target.id,
                description=f"Transfer {target.qty_transferred} units of {target.article_code} from {target.from_dept} to {target.to_dept}",
                new_values=values,
                request_method='POST',
                request_path='/api/v1/warehouse/transfer'
            )

            db.add(audit_log)
            db.commit()
            db.close()
        except Exception:
            pass


    # ============================================================================
    # MANUFACTURING ORDER AUDIT (Production Traceability)
    # ============================================================================

    @event.listens_for(ManufacturingOrder, 'after_insert')
    def log_mo_create(mapper, connection, target):
        """Log MO creation."""
        try:
            db = SessionLocal()

            values = get_model_dict(target)

            # Get product code for description
            product_code = target.product.code if target.product else f"Product#{target.product_id}"

            audit_log = AuditLog(
                user_id=getattr(target, '_audit_user_id', None),
                username=getattr(target, '_audit_username', 'System'),
                user_role=getattr(target, '_audit_user_role', None),
                ip_address=getattr(target, '_audit_ip_address', None),
                action=AuditAction.CREATE,
                module=AuditModule.PPIC,
                entity_type='ManufacturingOrder',
                entity_id=target.id,
                description=f"Created Manufacturing Order for {product_code} ({target.qty_planned} units)",
                new_values=values,
                request_method='POST',
                request_path='/api/v1/ppic/manufacturing-orders'
            )

            db.add(audit_log)
            db.commit()
            db.close()
        except Exception:
            pass


    @event.listens_for(ManufacturingOrder, 'after_update')
    def log_mo_update(mapper, connection, target):
        """Log MO status changes - Track production progress."""
        try:
            db = SessionLocal()

            changed = get_changed_fields(target)
            if not changed:
                return

            # Get product code for description
            product_code = target.product.code if target.product else f"Product#{target.product_id}"

            # Special handling for status changes
            if 'state' in changed:
                status_change = f"{changed['state']['old']} → {changed['state']['new']}"
                description = f"Manufacturing Order {product_code} status: {status_change}"
            else:
                description = f"Updated Manufacturing Order {product_code}: {', '.join(changed.keys())}"

            audit_log = AuditLog(
                user_id=getattr(target, '_audit_user_id', None),
                username=getattr(target, '_audit_username', 'System'),
                user_role=getattr(target, '_audit_user_role', None),
                ip_address=getattr(target, '_audit_ip_address', None),
                action=AuditAction.UPDATE,
                module=AuditModule.PPIC,
                entity_type='ManufacturingOrder',
                entity_id=target.id,
                description=description,
                old_values={k: v['old'] for k, v in changed.items()},
                new_values={k: v['new'] for k, v in changed.items()},
                request_method='PUT',
                request_path=f'/api/v1/ppic/manufacturing-orders/{target.id}'
            )

            db.add(audit_log)
            db.commit()
            db.close()
        except Exception:
            pass


    # ============================================================================
    # WORK ORDER AUDIT (Production Line Traceability - All Departments)
    # ============================================================================

    @event.listens_for(WorkOrder, 'after_insert')
    def log_work_order_create(mapper, connection, target):
        """Log work order creation for all departments."""
        try:
            db = SessionLocal()

            values = get_model_dict(target)

            audit_log = AuditLog(
                user_id=getattr(target, '_audit_user_id', None),
                username=getattr(target, '_audit_username', 'System'),
                user_role=getattr(target, '_audit_user_role', None),
                ip_address=getattr(target, '_audit_ip_address', None),
                action=AuditAction.CREATE,
                module=AuditModule.PPIC,
                entity_type='WorkOrder',
                entity_id=target.id,
                description=f"Created {target.department.value} Work Order #{target.id} (Input: {target.input_qty} units)",
                new_values=values,
                request_method='POST',
                request_path='/api/v1/production/work-orders'
            )

            db.add(audit_log)
            db.commit()
            db.close()
        except Exception:
            pass


    @event.listens_for(WorkOrder, 'after_update')
    def log_work_order_update(mapper, connection, target):
        """Log work order status changes for all departments."""
        try:
            db = SessionLocal()

            changed = get_changed_fields(target)
            if not changed:
                return

            # Track status changes
            if 'status' in changed:
                description = f"{target.department.value} WO #{target.id} status: {changed['status']['old']} → {changed['status']['new']}"
            elif 'output_qty' in changed:
                description = f"{target.department.value} WO #{target.id} completed: {changed['output_qty']['new']} units"
            else:
                description = f"Updated {target.department.value} WO #{target.id}: {', '.join(changed.keys())}"

            audit_log = AuditLog(
                user_id=getattr(target, '_audit_user_id', None),
                username=getattr(target, '_audit_username', 'System'),
                user_role=getattr(target, '_audit_user_role', None),
                ip_address=getattr(target, '_audit_ip_address', None),
                action=AuditAction.UPDATE,
                module=AuditModule.PPIC,
                entity_type='WorkOrder',
                entity_id=target.id,
                description=description,
                old_values={k: v['old'] for k, v in changed.items()},
                new_values={k: v['new'] for k, v in changed.items()},
                request_method='PUT',
                request_path=f'/api/v1/production/work-orders/{target.id}'
            )

            db.add(audit_log)
            db.commit()
            db.close()
        except Exception:
            pass


