from typing import Any, Dict, Optional

import httpx
from fastapi import HTTPException


class ServiceHttpClient:
    def __init__(self, timeout: float = 20.0):
        self.timeout = timeout

    def request(
        self,
        method: str,
        url: str,
        json: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.request(method=method, url=url, json=json)

            if response.status_code >= 400:
                try:
                    detail = response.json()
                except Exception:
                    detail = {"detail": response.text}

                raise HTTPException(
                    status_code=response.status_code,
                    detail={
                        "service_url": url,
                        "error": detail,
                    },
                )

            if response.content:
                return response.json()

            return {}

        except httpx.RequestError as exc:
            raise HTTPException(
                status_code=502,
                detail={
                    "service_url": url,
                    "error": f"Cannot connect to downstream service: {str(exc)}",
                },
            )