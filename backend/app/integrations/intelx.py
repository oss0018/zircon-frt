"""Intelligence X (IntelX) integration."""
from typing import Any

import httpx

from app.integrations.base import BaseIntegration, IntegrationRegistry

BASE_URL = "https://2.intelx.io"


@IntegrationRegistry.register
class IntelXIntegration(BaseIntegration):
    name = "intelx"
    description = "Intelligence X — dark web and leak search engine"
    rate_limit = 30
    cache_ttl = 1800

    def _headers(self) -> dict[str, str]:
        return {"x-key": self.api_key}

    async def search(self, query: str, query_type: str = "email") -> list[dict[str, Any]]:
        async with httpx.AsyncClient(timeout=30) as client:
            # Start search
            resp = await client.post(
                f"{BASE_URL}/intelligent/search",
                headers=self._headers(),
                json={"term": query, "buckets": [], "lookuplevel": 0, "maxresults": 100, "timeout": 5,
                      "datefrom": "", "dateto": "", "sort": 4, "media": 0, "terminate": []},
            )
            resp.raise_for_status()
            data = resp.json()
            search_id = data.get("id")
            if not search_id:
                return []

            # Fetch results
            result_resp = await client.get(
                f"{BASE_URL}/intelligent/search/result",
                headers=self._headers(),
                params={"id": search_id, "limit": 100, "offset": 0},
            )
            result_resp.raise_for_status()
            return result_resp.json().get("records", [])

    async def check_health(self) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(f"{BASE_URL}/authenticate/info", headers=self._headers())
            return {"status": "ok" if resp.status_code == 200 else "error", "code": resp.status_code}
