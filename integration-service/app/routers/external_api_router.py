from fastapi import APIRouter

from app.schemas.external_api import GeocodeSearchRequest, GeocodeSearchResponse
from app.services.geocoding_service import GeocodingService

router = APIRouter(prefix="/external", tags=["External APIs"])

geocoding_service = GeocodingService()


@router.post("/geocode/search", response_model=GeocodeSearchResponse)
def geocode_search(payload: GeocodeSearchRequest):
    return geocoding_service.search_address(
        query=payload.query,
        limit=payload.limit,
        country_code=payload.country_code or "vn",
    )