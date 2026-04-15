"""LeakIX integration."""
from typing import Any

import httpx

from app.integrations.base import BaseIntegration, IntegrationRegistry

BASE_URL = "https://leakix.net"


@IntegrationRegistry.register
class LeakIXIntegration(BaseIntegration):
    name = "leakix"
    description = "LeakIX — compromised device and data leak indexing"
    rate_limit = 30
    cache_ttl = 1800

    def _headers(self) -> dict[str, str]:
        return {"api-key": self.api_key, "Accept": "application/json"}

    async def search(self, query: str, query_type: str = "ip") -> list[dict[str, Any]]:
        async with httpx.AsyncClient(timeout=15) as client:
            if query_type == "ip":
                resp = await client.get(f"{BASE_URL}/host/{query}", headers=self._headers())
            elif query_type == "domain":
                resp = await client.get(
                    f"{BASE_URL}/search",
                    headers=self._headers(),
                    params={"q": f"host:{query}", "scope": "leak", "page": 0},
                )
            else:
                resp = await client.get(
                    f"{BASE_URL}/search",
                    headers=self._headers(),
                    params={"q": query, "scope": "leak", "page": 0},
                )
            if resp.status_code == 404:
                return []
            resp.raise_for_status()
            data = resp.json()
            return data if isinstance(data, list) else [data]

    async def check_health(self) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(f"{BASE_URL}/search", headers=self._headers(), params={"q": "test", "scope": "leak", "page": 0})
            return {"status": "ok" if resp.status_code in (200, 404) else "error", "code": resp.status_code}
