"""PhishTank integration — community phishing URL database."""
from typing import Any

import httpx

from app.integrations.base import BaseIntegration, IntegrationRegistry

BASE_URL = "https://checkurl.phishtank.com/checkurl/"


@IntegrationRegistry.register
class PhishTankIntegration(BaseIntegration):
    name = "phishtank"
    description = "PhishTank — community phishing database verification"
    rate_limit = 30
    cache_ttl = 1800

    async def search(self, query: str, query_type: str = "url") -> list[dict[str, Any]]:
        if query_type not in ("url",):
            return []
        import urllib.parse
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(
                BASE_URL,
                data={
                    "url": urllib.parse.quote(query, safe=""),
                    "format": "json",
                    "app_key": self.api_key,
                },
            )
            resp.raise_for_status()
            data = resp.json()
            results = data.get("results", {})
            if not results.get("in_database"):
                return []
            return [results]

    async def check_health(self) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=10) as client:
            import urllib.parse
            resp = await client.post(
                BASE_URL,
                data={
                    "url": urllib.parse.quote("http://example.com", safe=""),
                    "format": "json",
                    "app_key": self.api_key,
                },
            )
            return {"status": "ok" if resp.status_code == 200 else "error", "code": resp.status_code}
