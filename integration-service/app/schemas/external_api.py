from typing import List, Optional
from pydantic import BaseModel, Field


class GeocodeSearchRequest(BaseModel):
    query: str = Field(..., min_length=3, max_length=255)
    limit: int = Field(default=5, ge=1, le=10)
    country_code: Optional[str] = Field(default="vn", min_length=2, max_length=2)


class GeocodeResult(BaseModel):
    display_name: str
    lat: float
    lon: float
    source: str
    place_id: Optional[str] = None


class GeocodeSearchResponse(BaseModel):
    success: bool
    mode: str
    query: str
    results: List[GeocodeResult]