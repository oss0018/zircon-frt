"""urlscan.io integration — URL scanning and screenshot service."""
from typing import Any

import httpx

from app.integrations.base import BaseIntegration, IntegrationRegistry

BASE_URL = "https://urlscan.io/api/v1"


@IntegrationRegistry.register
class URLScanIntegration(BaseIntegration):
    name = "urlscan"
    description = "urlscan.io — web page scanning, screenshots and analysis"
    rate_limit = 60
    cache_ttl = 3600

    def _headers(self) -> dict[str, str]:
        return {"API-Key": self.api_key, "Content-Type": "application/json"}

    async def search(self, query: str, query_type: str = "url") -> list[dict[str, Any]]:
        async with httpx.AsyncClient(timeout=30) as client:
            if query_type == "url":
                # Submit scan
                resp = await client.post(
                    f"{BASE_URL}/scan/",
                    headers=self._headers(),
                    json={"url": query, "visibility": "public"},
                )
                if resp.status_code in (200, 201):
                    return [resp.json()]
                resp.raise_for_status()
                return []
            elif query_type in ("domain", "ip"):
                field = "domain" if query_type == "domain" else "ip"
                resp = await client.get(
                    f"{BASE_URL}/search/",
                    headers=self._headers(),
                    params={"q": f"page.{field}:{query}", "size": 50},
                )
                resp.raise_for_status()
                return resp.json().get("results", [])
            return []

    async def check_health(self) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(
                f"{BASE_URL}/search/",
                headers=self._headers(),
                params={"q": "domain:example.com", "size": 1},
            )
            return {"status": "ok" if resp.status_code == 200 else "error", "code": resp.status_code}
