"""WebSocket API Endpoints for Real-time Notifications."""
import logging

from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect

from app.core.dependencies import get_current_user_ws
from app.core.websocket import ws_manager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ws", tags=["WebSocket"])


@router.websocket("/notifications")
async def websocket_notifications(
    websocket: WebSocket,
    token: str = Query(..., description="JWT access token")
):
    """WebSocket endpoint for real-time notifications.

    **Connection**: ws://localhost:8000/api/v1/ws/notifications?token=<JWT_TOKEN>

    **Message Types Received**:
    - `connection`: Connection status
    - `alert`: Critical/warning alerts (line clearance, segregation, QC failure)
    - `notification`: Info notifications (work order updates, transfers)

    **Alert Types**:
    - `LINE_CLEARANCE_REQUIRED`: Line must be cleared before transfer
    - `SEGREGATION_ALARM`: Article mixing detected (CRITICAL)
    - `QC_FAILURE`: Quality control test failed
    - `SHORTAGE_ALERT`: Material shortage detected

    **Notification Types**:
    - `WORK_ORDER_UPDATE`: Work order status changed
    - `TRANSFER_RECEIVED`: Transfer accepted by department
    """
    user = None
    try:
        # Validate token and get user
        user = await get_current_user_ws(token)

        # Connect websocket
        await ws_manager.connect(
            websocket=websocket,
            user_id=user.id,
            department=user.department
        )

        logger.info(f"WebSocket connected: User {user.username} ({user.department})")

        # Keep connection alive and handle incoming messages
        while True:
            try:
                # Wait for client messages (e.g., acknowledgements)
                data = await websocket.receive_json()

                # Handle client acknowledgements
                if data.get("type") == "acknowledgement":
                    logger.info(f"Alert acknowledged by {user.username}: {data.get('alert_id')}")
                    # You can log this to alert_logs table

                elif data.get("type") == "ping":
                    # Respond to keepalive ping
                    await websocket.send_json({
                        "type": "pong",
                        "timestamp": data.get("timestamp")
                    })

            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error(f"Error processing websocket message: {e}")
                break

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected: User {user.username if user else 'Unknown'}")
    except Exception as e:
        logger.error(f"WebSocket connection error: {e}")
    finally:
        if user:
            ws_manager.disconnect(
                websocket=websocket,
                user_id=user.id,
                department=user.department
            )


@router.websocket("/department/{department}")
async def websocket_department(
    websocket: WebSocket,
    department: str,
    token: str = Query(..., description="JWT access token")
):
    """WebSocket endpoint for department-specific notifications.

    **Departments**: Cutting, Embroidery, Sewing, Finishing, Packing, QC, Warehouse, PPIC
    """
    user = None
    try:
        # Validate token and get user
        user = await get_current_user_ws(token)

        # Verify user has access to this department
        if user.department != department and user.role not in ['Admin', 'PPIC Manager']:
            await websocket.close(code=1008, reason="Unauthorized department access")
            return

        # Connect websocket
        await ws_manager.connect(
            websocket=websocket,
            user_id=user.id,
            department=department
        )

        logger.info(f"WebSocket connected to {department}: User {user.username}")

        # Keep connection alive
        while True:
            try:
                data = await websocket.receive_json()

                if data.get("type") == "ping":
                    await websocket.send_json({"type": "pong"})

            except WebSocketDisconnect:
                break

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected from {department}: User {user.username if user else 'Unknown'}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        if user:
            ws_manager.disconnect(websocket, user.id, department)
