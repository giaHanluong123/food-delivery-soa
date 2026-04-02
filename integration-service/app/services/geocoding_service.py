import httpx
from fastapi import HTTPException

from app.core.config import (
    DEFAULT_GEOCODING_COUNTRY,
    HTTP_TIMEOUT,
    NOMINATIM_BASE_URL,
    NOMINATIM_USER_AGENT,
    USE_MOCK_GEOCODING,
)


class GeocodingService:
    def __init__(self):
        self.base_url = NOMINATIM_BASE_URL.rstrip("/")
        self.user_agent = NOMINATIM_USER_AGENT
        self.timeout = HTTP_TIMEOUT
        self.use_mock = USE_MOCK_GEOCODING

    def search_address(self, query: str, limit: int = 5, country_code: str = "vn"):
        if self.use_mock:
            return {
                "success": True,
                "mode": "mock",
                "query": query,
                "results": self._mock_results(query, limit),
            }

        params = {
            "q": query,
            "format": "jsonv2",
            "limit": limit,
            "addressdetails": 1,
            "countrycodes": (country_code or DEFAULT_GEOCODING_COUNTRY).lower(),
        }

        headers = {
            "User-Agent": self.user_agent,
            "Accept": "application/json",
            "Accept-Language": "vi,en-US;q=0.9,en;q=0.8",
        }

        url = f"{self.base_url}/search"

        print("=== NOMINATIM REQUEST START ===")
        print("URL:", url)
        print("Params:", params)
        print("Headers:", headers)

        try:
            with httpx.Client(timeout=self.timeout, headers=headers, follow_redirects=True) as client:
                response = client.get(url, params=params)

                print("Status code:", response.status_code)
                print("Response headers:", dict(response.headers))
                print("Response text:", response.text[:1000])
                print("=== NOMINATIM REQUEST END ===")

                response.raise_for_status()
                raw_data = response.json()

        except httpx.HTTPStatusError as exc:
            raise HTTPException(
                status_code=502,
                detail={
                    "service": "nominatim",
                    "message": "Failed to call geocoding provider",
                    "status_code": exc.response.status_code,
                    "request_url": str(exc.request.url),
                    "response_text": exc.response.text[:1000],
                },
            )
        except httpx.HTTPError as exc:
            raise HTTPException(
                status_code=502,
                detail={
                    "service": "nominatim",
                    "message": "Failed to call geocoding provider",
                    "error": str(exc),
                },
            )

        results = []
        for item in raw_data:
            results.append(
                {
                    "display_name": item.get("display_name", ""),
                    "lat": float(item.get("lat")),
                    "lon": float(item.get("lon")),
                    "source": "nominatim",
                    "place_id": str(item.get("place_id")) if item.get("place_id") else None,
                }
            )

        return {
            "success": True,
            "mode": "real",
            "query": query,
            "results": results,
        }

    def _mock_results(self, query: str, limit: int):
        base_results = [
            {
                "display_name": "227 Nguyen Van Cu, Quan 5, Ho Chi Minh City, Vietnam",
                "lat": 10.762622,
                "lon": 106.660172,
                "source": "mock",
                "place_id": "mock-1",
            },
            {
                "display_name": "1 Vo Van Ngan, Thu Duc, Ho Chi Minh City, Vietnam",
                "lat": 10.850000,
                "lon": 106.770000,
                "source": "mock",
                "place_id": "mock-2",
            },
            {
                "display_name": f"Mock result for: {query}",
                "lat": 10.7756587,
                "lon": 106.7004238,
                "source": "mock",
                "place_id": "mock-3",
            },
        ]
        return base_results[:limit]