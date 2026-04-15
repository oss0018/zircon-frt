"""Have I Been Pwned (HIBP) integration."""
from typing import Any

import httpx

from app.integrations.base import BaseIntegration, IntegrationRegistry

BASE_URL = "https://haveibeenpwned.com/api/v3"


@IntegrationRegistry.register
class HIBPIntegration(BaseIntegration):
    name = "hibp"
    description = "Have I Been Pwned — breach and paste monitoring"
    rate_limit = 10  # per minute
    cache_ttl = 3600

    def _headers(self) -> dict[str, str]:
        return {
            "hibp-api-key": self.api_key,
            "User-Agent": "Zircon-FRT/1.0",
        }

    async def search(self, query: str, query_type: str = "email") -> list[dict[str, Any]]:
        async with httpx.AsyncClient(timeout=15) as client:
            if query_type in ("email", "domain"):
                resp = await client.get(
                    f"{BASE_URL}/breachedaccount/{query}",
                    headers=self._headers(),
                    params={"truncateResponse": "false"},
                )
                if resp.status_code == 404:
                    return []
                resp.raise_for_status()
                return resp.json()
            elif query_type == "breach":
                resp = await client.get(
                    f"{BASE_URL}/breach/{query}",
                    headers=self._headers(),
                )
                if resp.status_code == 404:
                    return []
                resp.raise_for_status()
                return [resp.json()]
            return []

    async def check_health(self) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(
                f"{BASE_URL}/breaches",
                headers=self._headers(),
                params={"truncateResponse": "true"},
            )
            return {"status": "ok" if resp.status_code == 200 else "error", "code": resp.status_code}
