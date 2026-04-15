"""AbuseIPDB integration — IP reputation and abuse reporting."""
from typing import Any

import httpx

from app.integrations.base import BaseIntegration, IntegrationRegistry

BASE_URL = "https://api.abuseipdb.com/api/v2"


@IntegrationRegistry.register
class AbuseIPDBIntegration(BaseIntegration):
    name = "abuseipdb"
    description = "AbuseIPDB — IP reputation and abuse report database"
    rate_limit = 60  # 1000/day, but safe to set 60/min
    cache_ttl = 3600

    def _headers(self) -> dict[str, str]:
        return {"Key": self.api_key, "Accept": "application/json"}

    async def search(self, query: str, query_type: str = "ip") -> list[dict[str, Any]]:
        async with httpx.AsyncClient(timeout=15) as client:
            if query_type == "ip":
                resp = await client.get(
                    f"{BASE_URL}/check",
                    headers=self._headers(),
                    params={"ipAddress": query, "maxAgeInDays": 90, "verbose": "true"},
                )
                resp.raise_for_status()
                return [resp.json().get("data", {})]
            elif query_type == "reports":
                resp = await client.get(
                    f"{BASE_URL}/reports",
                    headers=self._headers(),
                    params={"ipAddress": query, "maxAgeInDays": 30, "perPage": 25},
                )
                resp.raise_for_status()
                return resp.json().get("data", {}).get("results", [])
            return []

    async def check_health(self) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(
                f"{BASE_URL}/check",
                headers=self._headers(),
                params={"ipAddress": "8.8.8.8", "maxAgeInDays": 1},
            )
            return {"status": "ok" if resp.status_code == 200 else "error", "code": resp.status_code}
