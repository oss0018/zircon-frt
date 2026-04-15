"""AlienVault OTX integration — Open Threat Exchange IOC platform."""
from typing import Any

import httpx

from app.integrations.base import BaseIntegration, IntegrationRegistry

BASE_URL = "https://otx.alienvault.com/api/v1"


@IntegrationRegistry.register
class AlienVaultOTXIntegration(BaseIntegration):
    name = "alienvault_otx"
    description = "AlienVault OTX — Open Threat Exchange threat intelligence"
    rate_limit = 100
    cache_ttl = 1800

    def _headers(self) -> dict[str, str]:
        return {"X-OTX-API-KEY": self.api_key}

    async def search(self, query: str, query_type: str = "ip") -> list[dict[str, Any]]:
        async with httpx.AsyncClient(timeout=15) as client:
            if query_type == "ip":
                resp = await client.get(
                    f"{BASE_URL}/indicators/IPv4/{query}/general",
                    headers=self._headers(),
                )
            elif query_type == "domain":
                resp = await client.get(
                    f"{BASE_URL}/indicators/domain/{query}/general",
                    headers=self._headers(),
                )
            elif query_type == "url":
                resp = await client.get(
                    f"{BASE_URL}/indicators/url/{query}/general",
                    headers=self._headers(),
                )
            elif query_type == "hash":
                resp = await client.get(
                    f"{BASE_URL}/indicators/file/{query}/general",
                    headers=self._headers(),
                )
            else:
                return []
            if resp.status_code == 404:
                return []
            resp.raise_for_status()
            return [resp.json()]

    async def check_health(self) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(f"{BASE_URL}/user/me", headers=self._headers())
            return {"status": "ok" if resp.status_code == 200 else "error", "code": resp.status_code}
