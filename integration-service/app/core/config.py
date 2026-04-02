CORE_SERVICE_URL = "http://core-service:8001"
PAYMENT_SERVICE_URL = "http://payment-service:8003"
DELIVERY_SERVICE_URL = "http://delivery-service:8002"
NOTIFICATION_SERVICE_URL = "http://notification-service:8004"

import os

CORE_SERVICE_URL = os.getenv("CORE_SERVICE_URL", "http://core-service:8001")
DELIVERY_SERVICE_URL = os.getenv("DELIVERY_SERVICE_URL", "http://delivery-service:8002")
PAYMENT_SERVICE_URL = os.getenv("PAYMENT_SERVICE_URL", "http://payment-service:8003")
NOTIFICATION_SERVICE_URL = os.getenv("NOTIFICATION_SERVICE_URL", "http://notification-service:8004")

NOMINATIM_BASE_URL = os.getenv("NOMINATIM_BASE_URL", "https://nominatim.openstreetmap.org")
NOMINATIM_USER_AGENT = os.getenv(
    "NOMINATIM_USER_AGENT",
    "food-delivery-soa-demo/1.0 (student project; contact: luonggiahan2005@gmail.com)"
)
DEFAULT_GEOCODING_COUNTRY = os.getenv("DEFAULT_GEOCODING_COUNTRY", "vn")
USE_MOCK_GEOCODING = os.getenv("USE_MOCK_GEOCODING", "false").lower() == "true"
HTTP_TIMEOUT = float(os.getenv("HTTP_TIMEOUT", "10"))