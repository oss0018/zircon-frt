"""Hudson Rock Cavalier integration — infostealer log monitoring."""
from typing import Any

import httpx

from app.integrations.base import BaseIntegration, IntegrationRegistry

BASE_URL = "https://cavalier.hudsonrock.com/api/json/v2"


@IntegrationRegistry.register
class HudsonRockIntegration(BaseIntegration):
    name = "hudsonrock"
    description = "Hudson Rock — infostealer log and credential compromise monitoring"
    rate_limit = 10
    cache_ttl = 3600

    def _headers(self) -> dict[str, str]:
        return {"api-key": self.api_key}

    async def search(self, query: str, query_type: str = "email") -> list[dict[str, Any]]:
        async with httpx.AsyncClient(timeout=15) as client:
            if query_type == "email":
                resp = await client.get(
                    f"{BASE_URL}/search-by-login/osint-tools",
                    headers=self._headers(),
                    params={"login": query},
                )
            elif query_type == "domain":
                resp = await client.get(
                    f"{BASE_URL}/search-by-domain/osint-tools",
                    headers=self._headers(),
                    params={"domain": query},
                )
            elif query_type == "username":
                resp = await client.get(
                    f"{BASE_URL}/search-by-login/osint-tools",
                    headers=self._headers(),
                    params={"login": query},
                )
            else:
                return []
            if resp.status_code == 404:
                return []
            resp.raise_for_status()
            data = resp.json()
            return data if isinstance(data, list) else [data]

    async def check_health(self) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(
                f"{BASE_URL}/search-by-domain/osint-tools",
                headers=self._headers(),
                params={"domain": "example.com"},
            )
            return {"status": "ok" if resp.status_code in (200, 404) else "error", "code": resp.status_code}
