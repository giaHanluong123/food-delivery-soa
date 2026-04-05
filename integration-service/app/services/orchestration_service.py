from fastapi import HTTPException

from app.core.config import (
    CORE_SERVICE_URL,
    DELIVERY_SERVICE_URL,
    NOTIFICATION_SERVICE_URL,
    PAYMENT_SERVICE_URL,
)
from app.services.http_client import ServiceHttpClient
from app.services.realtime_event_service import RealtimeEventService


class OrchestrationService:
    def __init__(self):
        self.client = ServiceHttpClient()
        self.realtime = RealtimeEventService()

    def create_order_flow(self, payload: dict):
        # 1) Lấy địa chỉ từ core-service nếu client không truyền delivery_address
        address_detail = self.client.request(
            "GET",
            f"{CORE_SERVICE_URL}/addresses/{payload['address_id']}",
        )

        resolved_delivery_address = payload.get("delivery_address") or ", ".join(
            filter(
                None,
                [
                    address_detail.get("address_line"),
                    address_detail.get("ward"),
                    address_detail.get("district"),
                    address_detail.get("city"),
                ],
            )
        )

        # 2) Tạo order đúng contract của core-service
        core_order_payload = {
            "user_id": payload["user_id"],
            "restaurant_id": payload["restaurant_id"],
            "address_id": payload["address_id"],
            "note": payload.get("note"),
            "shipping_fee": payload.get("shipping_fee", 0),
            "items": [
                {
                    "menu_item_id": item["menu_item_id"],
                    "quantity": item["quantity"],
                    "toppings": item.get("toppings", []),
                }
                for item in payload["items"]
            ],
        }

        created_order = self.client.request(
            "POST",
            f"{CORE_SERVICE_URL}/orders/create-full",
            json=core_order_payload,
        )

        order_id = created_order["id"]
        total_amount = created_order["total_amount"]

        # 3) Tạo payment
        payment_payload = {
            "order_id": order_id,
            "user_id": payload["user_id"],
            "amount": total_amount,
            "payment_method": payload["payment_method"],
        }

        created_payment = self.client.request(
            "POST",
            f"{PAYMENT_SERVICE_URL}/payments/create",
            json=payment_payload,
        )

        # 4) Tạo delivery
        delivery_payload = {
            "order_id": order_id,
            "user_id": payload["user_id"],
            "restaurant_id": payload["restaurant_id"],
            "pickup_address": f"Restaurant #{payload['restaurant_id']}",
            "dropoff_address": resolved_delivery_address,
            "shipping_fee": payload.get("shipping_fee", 0),
            "note": payload.get("note"),
        }

        created_delivery = self.client.request(
            "POST",
            f"{DELIVERY_SERVICE_URL}/deliveries",
            json=delivery_payload,
        )

        # 5) Tạo notification
        notification_payload = {
            "user_id": payload["user_id"],
            "notification_type": "order_created",
            "title": "Đơn hàng đã được tạo",
            "message": f"Đơn hàng #{order_id} đã được tạo thành công",
            "reference_type": "order",
            "reference_id": order_id,
            "order_id": order_id,
        }
        created_notification = self.client.request(
            "POST",
            f"{NOTIFICATION_SERVICE_URL}/notifications",
            json=notification_payload,
        )

        # 6) Bắn realtime event
        realtime_event = self.realtime.publish_event(
            order_id=order_id,
            event_type="order_created",
            source_service="integration-service",
            status=created_order.get("order_status", "pending"),
            message=f"Đơn hàng #{order_id} đã được tạo thành công",
            metadata={
                "payment_status": created_order.get("payment_status"),
                "delivery_status": created_order.get("delivery_status"),
                "total_amount": created_order.get("total_amount"),
                "payment_id": created_payment.get("id"),
                "delivery_id": created_delivery.get("id"),
                "notification_id": created_notification.get("id"),
            },
        )

        return {
            "order": created_order,
            "payment": created_payment,
            "delivery": created_delivery,
            "notification": created_notification,
            "realtime_event": realtime_event,
        }

    def payment_callback_flow(self, payload: dict):
        callback_result = self.client.request(
            "POST",
            f"{PAYMENT_SERVICE_URL}/payments/{payload['payment_id']}/callback",
            json={
                "payment_status": payload["payment_status"],
                "gateway_transaction_id": payload.get("gateway_transaction_id"),
                "callback_message": payload.get("callback_message"),
            },
        )

        order_detail = self.client.request(
            "GET",
            f"{CORE_SERVICE_URL}/orders/{payload['order_id']}",
        )

        order_update_result = None
        notification_result = None
        realtime_events = []

        if payload["payment_status"] == "paid":
            order_update_result = self.client.request(
                "PUT",
                f"{CORE_SERVICE_URL}/orders/{payload['order_id']}/status",
                json={
                    "order_status": "confirmed",
                    "payment_status": "paid",
                    "delivery_status": order_detail["delivery_status"],
                },
            )

            notification_result = self.client.request(
                "POST",
                f"{NOTIFICATION_SERVICE_URL}/notifications",
                json={
                    "user_id": payload["user_id"],
                    "notification_type": "payment_paid",
                    "title": "Thanh toán thành công",
                    "message": f"Đơn hàng #{payload['order_id']} đã thanh toán thành công",
                    "reference_type": "payment",
                    "reference_id": payload["payment_id"],
                    "order_id": payload["order_id"],
                },
            )
            realtime_events.append(
                self.realtime.publish_event(
                    order_id=payload["order_id"],
                    event_type="payment_paid",
                    source_service="integration-service",
                    status="paid",
                    message=f"Thanh toán đơn hàng #{payload['order_id']} thành công",
                    metadata={
                        "payment_id": payload["payment_id"],
                        "gateway_transaction_id": payload.get("gateway_transaction_id"),
                    },
                )
            )

            realtime_events.append(
                self.realtime.publish_event(
                    order_id=payload["order_id"],
                    event_type="order_confirmed",
                    source_service="integration-service",
                    status="confirmed",
                    message=f"Đơn hàng #{payload['order_id']} đã được xác nhận",
                    metadata={
                        "payment_status": "paid",
                        "delivery_status": order_detail["delivery_status"],
                    },
                )
            )

        elif payload["payment_status"] == "failed":
            order_update_result = self.client.request(
                "PUT",
                f"{CORE_SERVICE_URL}/orders/{payload['order_id']}/status",
                json={
                    "order_status": order_detail["order_status"],
                    "payment_status": "failed",
                    "delivery_status": order_detail["delivery_status"],
                },
            )

            notification_result = self.client.request(
                "POST",
                f"{NOTIFICATION_SERVICE_URL}/notifications",
                json={
                    "user_id": payload["user_id"],
                    "notification_type": "payment_failed",
                    "title": "Thanh toán thất bại",
                    "message": f"Thanh toán cho đơn hàng #{payload['order_id']} thất bại",
                    "reference_type": "payment",
                    "reference_id": payload["payment_id"],
                    "order_id": payload["order_id"],
                },
            )
            realtime_events.append(
                self.realtime.publish_event(
                    order_id=payload["order_id"],
                    event_type="payment_failed",
                    source_service="integration-service",
                    status="failed",
                    message=f"Thanh toán cho đơn hàng #{payload['order_id']} thất bại",
                    metadata={
                        "payment_id": payload["payment_id"],
                        "gateway_transaction_id": payload.get("gateway_transaction_id"),
                    },
                )
            )
        else:
            raise HTTPException(
                status_code=400,
                detail="Unsupported payment_status for orchestration flow",
            )

        return {
            "payment_callback": callback_result,
            "order_update": order_update_result,
            "notification": notification_result,
            "realtime_events": realtime_events,
        }

    def delivery_delivered_flow(self, payload: dict):
        delivery_update_result = self.client.request(
            "PUT",
            f"{DELIVERY_SERVICE_URL}/deliveries/{payload['delivery_id']}/status",
            json={"delivery_status": "delivered"},
        )

        order_detail = self.client.request(
            "GET",
            f"{CORE_SERVICE_URL}/orders/{payload['order_id']}",
        )

        order_update_result = self.client.request(
            "PUT",
            f"{CORE_SERVICE_URL}/orders/{payload['order_id']}/status",
            json={
                "order_status": "delivered",
                "payment_status": order_detail["payment_status"],
                "delivery_status": "delivered",
            },
        )

        notification_result = self.client.request(
            "POST",
            f"{NOTIFICATION_SERVICE_URL}/notifications",
            json={
                "user_id": payload["user_id"],
                "notification_type": "delivery_delivered",
                "title": "Đơn hàng đã giao thành công",
                "message": f"Đơn hàng #{payload['order_id']} đã được giao thành công",
                "reference_type": "delivery",
                "reference_id": payload["delivery_id"],
                "order_id": payload["order_id"],
            },
        )
        realtime_events = [
            self.realtime.publish_event(
                order_id=payload["order_id"],
                event_type="delivery_delivered",
                source_service="integration-service",
                status="delivered",
                message=f"Giao hàng cho đơn #{payload['order_id']} thành công",
                metadata={
                    "delivery_id": payload["delivery_id"],
                },
            ),
            self.realtime.publish_event(
                order_id=payload["order_id"],
                event_type="order_delivered",
                source_service="integration-service",
                status="delivered",
                message=f"Đơn hàng #{payload['order_id']} đã hoàn tất",
                metadata={
                    "payment_status": order_detail["payment_status"],
                    "delivery_status": "delivered",
                },
            ),
        ]

        return {
            "delivery_update": delivery_update_result,
            "order_update": order_update_result,
            "notification": notification_result,
            "realtime_events": realtime_events,
        }