from math import radians, sin, cos, sqrt, atan2

from fastapi import HTTPException

from app.services.geocoding_service import GeocodingService


class DeliveryHelperService:
    def __init__(self):
        self.geocoding_service = GeocodingService()

    def normalize_address(self, address: str, country_code: str = "vn"):
        geo_result = self.geocoding_service.search_address(
            query=address,
            limit=1,
            country_code=country_code,
        )

        results = geo_result.get("results", [])
        if not results:
            raise HTTPException(
                status_code=404,
                detail="Không tìm thấy địa chỉ phù hợp",
            )

        best_match = results[0]

        return {
            "success": True,
            "original_address": address,
            "normalized_address": best_match["display_name"],
            "lat": best_match["lat"],
            "lon": best_match["lon"],
            "source": best_match["source"],
        }

    def estimate_delivery(
        self,
        pickup_lat: float,
        pickup_lon: float,
        dropoff_lat: float,
        dropoff_lon: float,
    ):
        distance_km = self._haversine_km(
            pickup_lat,
            pickup_lon,
            dropoff_lat,
            dropoff_lon,
        )

        estimated_minutes = self._estimate_minutes(distance_km)
        suggested_shipping_fee = self._suggest_shipping_fee(distance_km)

        return {
            "success": True,
            "distance_km": round(distance_km, 2),
            "estimated_minutes": estimated_minutes,
            "suggested_shipping_fee": suggested_shipping_fee,
            "calculation_mode": "mock_haversine",
        }

    def _haversine_km(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        earth_radius_km = 6371.0

        dlat = radians(lat2 - lat1)
        dlon = radians(lon2 - lon1)

        a = (
            sin(dlat / 2) ** 2
            + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
        )
        c = 2 * atan2(sqrt(a), sqrt(1 - a))

        return earth_radius_km * c

    def _estimate_minutes(self, distance_km: float) -> int:
        base_minutes = 10
        speed_km_per_hour = 20

        travel_minutes = int((distance_km / speed_km_per_hour) * 60)

        if travel_minutes < 5:
            travel_minutes = 5

        return base_minutes + travel_minutes

    def _suggest_shipping_fee(self, distance_km: float) -> float:
        base_fee = 15000
        extra_fee_per_km = 4000

        if distance_km <= 2:
            return float(base_fee)

        extra_distance = distance_km - 2
        fee = base_fee + (extra_distance * extra_fee_per_km)

        return round(fee, 0)