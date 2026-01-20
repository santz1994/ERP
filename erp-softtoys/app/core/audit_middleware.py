"""
Audit Context Middleware
Attaches user context to database models for automatic audit logging

This middleware intercepts API requests and attaches user information
to model instances, so SQLAlchemy event listeners can log who made changes.
"""
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable
import contextvars

# Context variable to store current user info
audit_context = contextvars.ContextVar('audit_context', default=None)


class AuditContextMiddleware(BaseHTTPMiddleware):
    """
    Middleware to attach user context for audit trail
    
    Captures user info from JWT token and stores in context variable
    accessible by SQLAlchemy event listeners.
    """
    
    async def dispatch(self, request: Request, call_next: Callable):
        # Extract user info from request state (set by JWT dependency)
        user_info = {
            'user_id': None,
            'username': 'Anonymous',
            'user_role': None,
            'ip_address': request.client.host if request.client else None,
            'request_method': request.method,
            'request_path': request.url.path
        }
        
        # If user is authenticated, request.state.user will be set by get_current_user
        if hasattr(request.state, 'user'):
            user = request.state.user
            user_info['user_id'] = user.id
            user_info['username'] = user.username
            user_info['user_role'] = user.role.value if hasattr(user.role, 'value') else str(user.role)
        
        # Store in context variable
        audit_context.set(user_info)
        
        # Process request
        response = await call_next(request)
        
        return response


def get_audit_context():
    """Get current audit context (user info)"""
    return audit_context.get()


def attach_audit_context(instance):
    """
    Attach audit context to model instance
    Call this before commit() to enable automatic audit logging
    
    Usage in API endpoint:
        po = PurchaseOrder(...)
        attach_audit_context(po)
        db.add(po)
        db.commit()  # Event listener will log with user info
    """
    context = get_audit_context()
    if context:
        instance._audit_user_id = context['user_id']
        instance._audit_username = context['username']
        instance._audit_user_role = context['user_role']
        instance._audit_ip_address = context['ip_address']
