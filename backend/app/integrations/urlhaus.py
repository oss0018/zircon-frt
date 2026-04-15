"""URLhaus integration — malicious URL database by abuse.ch."""
from typing import Any

import httpx

from app.integrations.base import BaseIntegration, IntegrationRegistry

BASE_URL = "https://urlhaus-api.abuse.ch/v1"


@IntegrationRegistry.register
class URLhausIntegration(BaseIntegration):
    name = "urlhaus"
    description = "URLhaus — malicious URL tracking by abuse.ch"
    rate_limit = 60
    cache_ttl = 1800

    async def search(self, query: str, query_type: str = "url") -> list[dict[str, Any]]:
        async with httpx.AsyncClient(timeout=15) as client:
            if query_type == "url":
                resp = await client.post(f"{BASE_URL}/url/", data={"url": query})
            elif query_type in ("domain", "ip", "host"):
                resp = await client.post(f"{BASE_URL}/host/", data={"host": query})
            elif query_type == "hash":
                resp = await client.post(f"{BASE_URL}/payload/", data={"md5_hash": query})
            else:
                return []
            resp.raise_for_status()
            data = resp.json()
            if data.get("query_status") in ("no_results", "invalid_url", "invalid_host"):
                return []
            return [data]

    async def check_health(self) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(f"{BASE_URL}/url/", data={"url": "http://example.com"})
            return {"status": "ok" if resp.status_code == 200 else "error", "code": resp.status_code}
