"""Shodan integration — Internet device and infrastructure search engine."""
from typing import Any

import httpx

from app.integrations.base import BaseIntegration, IntegrationRegistry

BASE_URL = "https://api.shodan.io"


@IntegrationRegistry.register
class ShodanIntegration(BaseIntegration):
    name = "shodan"
    description = "Shodan — IoT and infrastructure search engine"
    rate_limit = 60  # 1 req/sec, 60/min
    cache_ttl = 3600

    async def search(self, query: str, query_type: str = "ip") -> list[dict[str, Any]]:
        async with httpx.AsyncClient(timeout=30) as client:
            if query_type == "ip":
                resp = await client.get(
                    f"{BASE_URL}/shodan/host/{query}",
                    params={"key": self.api_key},
                )
            elif query_type in ("domain", "hostname"):
                resp = await client.get(
                    f"{BASE_URL}/dns/resolve",
                    params={"key": self.api_key, "hostnames": query},
                )
            else:
                resp = await client.get(
                    f"{BASE_URL}/shodan/host/search",
                    params={"key": self.api_key, "query": query, "facets": "port,country"},
                )
            if resp.status_code == 404:
                return []
            resp.raise_for_status()
            data = resp.json()
            return data if isinstance(data, list) else [data]

    async def check_health(self) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(f"{BASE_URL}/api-info", params={"key": self.api_key})
            return {"status": "ok" if resp.status_code == 200 else "error", "code": resp.status_code}
