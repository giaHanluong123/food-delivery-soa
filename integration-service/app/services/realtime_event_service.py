import anyio

from app.websockets.connection_manager import manager


class RealtimeEventService:
    def publish_event(
        self,
        order_id: int | str,
        event_type: str,
        source_service: str,
        status: str,
        message: str | None = None,
        metadata: dict | None = None,
    ) -> dict:
        payload = {
            "event_type": event_type,
            "order_id": str(order_id),
            "source_service": source_service,
            "status": status,
            "message": message,
            "metadata": metadata or {},
        }

        # orchestration router đang chạy sync trong threadpool,
        # nên dùng anyio.from_thread.run để gọi async broadcast an toàn
        anyio.from_thread.run(
            manager.broadcast_to_order,
            str(order_id),
            payload,
        )

        return payload