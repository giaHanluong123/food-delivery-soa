from fastapi import HTTPException

from app.core.config import (
    CORE_SERVICE_URL,
    DELIVERY_SERVICE_URL,
    NOTIFICATION_SERVICE_URL,
    PAYMENT_SERVICE_URL,
)
from app.services.http_client import ServiceHttpClient


class OrchestrationService:
    def __init__(self):
        self.client = ServiceHttpClient()

    def create_order_flow(self, payload: dict):
        created_order = None
        created_payment = None
        created_delivery = None
        created_notification = None

        items_payload = []
        subtotal = 0.0

        for item in payload["items"]:
            item_total = item["unit_price"] * item["quantity"]
            subtotal += item_total

            items_payload.append(
                {
                    "menu_item_id": item["menu_item_id"],
                    "quantity": item["quantity"],
                    "unit_price": item["unit_price"],
                    "note": item.get("note"),
                    "toppings": item.get("toppings", []),
                }
            )

        total_amount = subtotal + payload.get("shipping_fee", 0)

        core_order_payload = {
            "user_id": payload["user_id"],
            "restaurant_id": payload["restaurant_id"],
            "delivery_address": payload["delivery_address"],
            "note": payload.get("note"),
            "shipping_fee": payload.get("shipping_fee", 0),
            "total_amount": total_amount,
            "items": items_payload,
        }

        created_order = self.client.request(
            "POST",
            f"{CORE_SERVICE_URL}/orders/full",
            json=core_order_payload,
        )

        order_id = created_order["id"]

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

        delivery_payload = {
            "order_id": order_id,
            "user_id": payload["user_id"],
            "restaurant_id": payload["restaurant_id"],
            "pickup_address": f"Restaurant #{payload['restaurant_id']}",
            "dropoff_address": payload["delivery_address"],
            "shipping_fee": payload.get("shipping_fee", 0),
            "note": payload.get("note"),
        }

        created_delivery = self.client.request(
            "POST",
            f"{DELIVERY_SERVICE_URL}/deliveries",
            json=delivery_payload,
        )

        notification_payload = {
            "user_id": payload["user_id"],
            "notification_type": "order_created",
            "title": "Đơn hàng đã được tạo",
            "message": f"Đơn hàng #{order_id} đã được tạo thành công",
            "reference_type": "order",
            "reference_id": order_id,
        }

        created_notification = self.client.request(
            "POST",
            f"{NOTIFICATION_SERVICE_URL}/notifications",
            json=notification_payload,
        )

        return {
            "order": created_order,
            "payment": created_payment,
            "delivery": created_delivery,
            "notification": created_notification,
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

        order_update_result = None
        notification_result = None

        if payload["payment_status"] == "paid":
            order_update_result = self.client.request(
                "PUT",
                f"{CORE_SERVICE_URL}/orders/{payload['order_id']}/status",
                json={"order_status": "confirmed"},
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
                },
            )

        elif payload["payment_status"] == "failed":
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
                },
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
        }

    def delivery_delivered_flow(self, payload: dict):
        delivery_update_result = self.client.request(
            "PUT",
            f"{DELIVERY_SERVICE_URL}/deliveries/{payload['delivery_id']}/status",
            json={"delivery_status": "delivered"},
        )

        order_update_result = self.client.request(
            "PUT",
            f"{CORE_SERVICE_URL}/orders/{payload['order_id']}/status",
            json={"order_status": "delivered"},
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
            },
        )

        return {
            "delivery_update": delivery_update_result,
            "order_update": order_update_result,
            "notification": notification_result,
        }