from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.schemas.realtime import RealtimeEvent
from app.websockets.connection_manager import manager

router = APIRouter(prefix="/realtime", tags=["Realtime"])


@router.websocket("/ws/orders/{order_id}")
async def order_realtime_ws(websocket: WebSocket, order_id: str):
    await manager.connect(order_id=order_id, websocket=websocket)

    try:
        await websocket.send_json(
            {
                "event_type": "connected",
                "order_id": order_id,
                "source_service": "integration-service",
                "status": "CONNECTED",
                "message": f"Subscribed realtime for order {order_id}",
                "metadata": {},
            }
        )

        while True:
            incoming_message = await websocket.receive_text()

            if incoming_message == "ping":
                await websocket.send_json(
                    {
                        "event_type": "pong",
                        "order_id": order_id,
                        "source_service": "integration-service",
                        "status": "ALIVE",
                        "message": "heartbeat_ack",
                        "metadata": {},
                    }
                )
                continue

    except WebSocketDisconnect:
        manager.disconnect(order_id=order_id, websocket=websocket)
    except Exception:
        manager.disconnect(order_id=order_id, websocket=websocket)


@router.post("/publish")
async def publish_realtime_event(payload: RealtimeEvent):
    await manager.broadcast_to_order(
        order_id=payload.order_id,
        message=payload.model_dump(),
    )

    return {
        "success": True,
        "message": "Realtime event published",
        "order_id": payload.order_id,
        "event_type": payload.event_type,
        "status": payload.status,
    }


@router.get("/stats")
def get_realtime_stats():
    return {
        "service": "integration-service",
        "realtime": manager.stats(),
    }