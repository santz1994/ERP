"""FastAPI v1 API Module."""
from . import admin, auth, import_export, kanban, ppic, reports, websocket, warehouse_endpoints

# Create warehouse alias for backward compatibility
warehouse = warehouse_endpoints

__all__ = ["auth", "admin", "ppic", "warehouse", "websocket", "kanban", "reports", "import_export", "warehouse_endpoints"]
