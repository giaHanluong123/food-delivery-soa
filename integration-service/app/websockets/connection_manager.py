from collections import defaultdict
from typing import Dict, List

from fastapi import WebSocket


class RealtimeConnectionManager:
    def __init__(self) -> None:
        self.order_connections: Dict[str, List[WebSocket]] = defaultdict(list)

    async def connect(self, order_id: str, websocket: WebSocket) -> None:
        await websocket.accept()
        self.order_connections[order_id].append(websocket)

    def disconnect(self, order_id: str, websocket: WebSocket) -> None:
        if order_id not in self.order_connections:
            return

        if websocket in self.order_connections[order_id]:
            self.order_connections[order_id].remove(websocket)

        if not self.order_connections[order_id]:
            del self.order_connections[order_id]

    async def broadcast_to_order(self, order_id: str, message: dict) -> None:
        if order_id not in self.order_connections:
            return

        dead_connections: List[WebSocket] = []

        for connection in self.order_connections[order_id]:
            try:
                await connection.send_json(message)
            except Exception:
                dead_connections.append(connection)

        for dead_ws in dead_connections:
            self.disconnect(order_id, dead_ws)

    def stats(self) -> dict:
        return {
            "tracked_orders": len(self.order_connections),
            "total_connections": sum(len(v) for v in self.order_connections.values()),
        }


manager = RealtimeConnectionManager()