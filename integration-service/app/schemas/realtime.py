from typing import Any, Dict, Optional

from pydantic import BaseModel


class RealtimeEvent(BaseModel):
    event_type: str
    order_id: str
    source_service: str
    status: str
    message: Optional[str] = None
    metadata: Dict[str, Any] = {}