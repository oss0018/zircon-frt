"""Censys integration — host and certificate transparency search."""
from typing import Any

import httpx

from app.integrations.base import BaseIntegration, IntegrationRegistry

BASE_URL = "https://search.censys.io/api"


@IntegrationRegistry.register
class CensysIntegration(BaseIntegration):
    name = "censys"
    description = "Censys — global host and certificate transparency monitoring"
    rate_limit = 60
    cache_ttl = 3600

    def _auth(self) -> tuple[str, str]:
        # api_key format: "api_id:api_secret"
        parts = self.api_key.split(":", 1)
        if len(parts) == 2:
            return parts[0], parts[1]
        return self.api_key, ""

    async def search(self, query: str, query_type: str = "ip") -> list[dict[str, Any]]:
        auth = self._auth()
        async with httpx.AsyncClient(timeout=30, auth=auth) as client:
            if query_type == "ip":
                resp = await client.get(f"{BASE_URL}/v2/hosts/{query}")
                if resp.status_code == 404:
                    return []
                resp.raise_for_status()
                return [resp.json().get("result", {})]
            elif query_type in ("domain", "certificate"):
                resp = await client.post(
                    f"{BASE_URL}/v2/hosts/search",
                    json={"q": query, "per_page": 50},
                )
                resp.raise_for_status()
                return resp.json().get("result", {}).get("hits", [])
            return []

    async def check_health(self) -> dict[str, Any]:
        auth = self._auth()
        async with httpx.AsyncClient(timeout=10, auth=auth) as client:
            resp = await client.get(f"{BASE_URL}/v1/account")
            return {"status": "ok" if resp.status_code == 200 else "error", "code": resp.status_code}
