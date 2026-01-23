"""WebSocket Manager for Real-time Notifications
Handles real-time alerts, line clearance notifications, and system events
"""
from datetime import datetime
from typing import Any, Set

from fastapi import WebSocket, status


class ConnectionManager:
    """Manages WebSocket connections for real-time notifications"""

    def __init__(self):
        # Active connections by user_id
        self.active_connections: dict[int, list[WebSocket]] = {}
        # Connections by department
        self.dept_connections: dict[str, set[WebSocket]] = {
            'Cutting': set(),
            'Embroidery': set(),
            'Sewing': set(),
            'Finishing': set(),
            'Packing': set(),
            'QC': set(),
            'Warehouse': set(),
            'PPIC': set(),
            'Admin': set()
        }
        # Global broadcast connections
        self.broadcast_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket, user_id: int, department: str = None):
        """Connect a new WebSocket client"""
        await websocket.accept()

        # Add to user connections
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(websocket)

        # Add to department connections if specified
        if department and department in self.dept_connections:
            self.dept_connections[department].add(websocket)

        # Add to broadcast
        self.broadcast_connections.add(websocket)

        # Send connection confirmation
        await websocket.send_json({
            "type": "connection",
            "status": "connected",
            "timestamp": datetime.now().isoformat(),
            "message": "WebSocket connection established"
        })

    def disconnect(self, websocket: WebSocket, user_id: int, department: str = None):
        """Disconnect a WebSocket client"""
        # Remove from user connections
        if user_id in self.active_connections:
            if websocket in self.active_connections[user_id]:
                self.active_connections[user_id].remove(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]

        # Remove from department connections
        if department and department in self.dept_connections:
            self.dept_connections[department].discard(websocket)

        # Remove from broadcast
        self.broadcast_connections.discard(websocket)

    async def send_to_user(self, user_id: int, message: dict):
        """Send message to specific user (all their connections)"""
        if user_id in self.active_connections:
            disconnected = []
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_json(message)
                except:
                    disconnected.append(connection)

            # Clean up disconnected
            for conn in disconnected:
                self.active_connections[user_id].remove(conn)

    async def send_to_department(self, department: str, message: dict):
        """Send message to all users in a department"""
        if department in self.dept_connections:
            disconnected = []
            for connection in self.dept_connections[department]:
                try:
                    await connection.send_json(message)
                except:
                    disconnected.append(connection)

            # Clean up disconnected
            for conn in disconnected:
                self.dept_connections[department].discard(conn)

    async def broadcast(self, message: dict):
        """Broadcast message to all connected clients"""
        disconnected = []
        for connection in self.broadcast_connections:
            try:
                await connection.send_json(message)
            except:
                disconnected.append(connection)

        # Clean up disconnected
        for conn in disconnected:
            self.broadcast_connections.discard(conn)

    async def notify_line_clearance_required(self, department: str, details: dict):
        """Send line clearance alert to department"""
        message = {
            "type": "alert",
            "alert_type": "LINE_CLEARANCE_REQUIRED",
            "severity": "WARNING",
            "department": department,
            "timestamp": datetime.now().isoformat(),
            "details": details,
            "requires_action": True
        }
        await self.send_to_department(department, message)

    async def notify_segregation_alarm(self, department: str, details: dict):
        """Send segregation alarm (critical priority)"""
        message = {
            "type": "alert",
            "alert_type": "SEGREGATION_ALARM",
            "severity": "CRITICAL",
            "department": department,
            "timestamp": datetime.now().isoformat(),
            "details": details,
            "requires_action": True,
            "audio_alarm": True
        }
        # Send to department and broadcast to supervisors
        await self.send_to_department(department, message)
        await self.send_to_department('PPIC', message)
        await self.send_to_department('Admin', message)

    async def notify_qc_failure(self, department: str, details: dict):
        """Send QC failure notification"""
        message = {
            "type": "alert",
            "alert_type": "QC_FAILURE",
            "severity": "CRITICAL" if details.get('test_type') == 'Metal Detector' else "WARNING",
            "department": department,
            "timestamp": datetime.now().isoformat(),
            "details": details,
            "requires_action": True
        }
        await self.send_to_department(department, message)
        await self.send_to_department('QC', message)

    async def notify_shortage_alert(self, department: str, details: dict):
        """Send material shortage alert"""
        message = {
            "type": "alert",
            "alert_type": "SHORTAGE_ALERT",
            "severity": "WARNING",
            "department": department,
            "timestamp": datetime.now().isoformat(),
            "details": details,
            "requires_action": True
        }
        await self.send_to_department(department, message)
        await self.send_to_department('Warehouse', message)

    async def notify_work_order_update(self, department: str, work_order_id: int, status: str):
        """Notify work order status change"""
        message = {
            "type": "notification",
            "notification_type": "WORK_ORDER_UPDATE",
            "severity": "INFO",
            "department": department,
            "timestamp": datetime.now().isoformat(),
            "details": {
                "work_order_id": work_order_id,
                "status": status
            }
        }
        await self.send_to_department(department, message)

    async def notify_transfer_received(self, department: str, details: dict):
        """Notify department of incoming transfer"""
        message = {
            "type": "notification",
            "notification_type": "TRANSFER_RECEIVED",
            "severity": "INFO",
            "department": department,
            "timestamp": datetime.now().isoformat(),
            "details": details
        }
        await self.send_to_department(department, message)


# Global WebSocket manager instance
ws_manager = ConnectionManager()
