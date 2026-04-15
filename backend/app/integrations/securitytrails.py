"""SecurityTrails integration — DNS history, WHOIS, and subdomain enumeration."""
from typing import Any

import httpx

from app.integrations.base import BaseIntegration, IntegrationRegistry

BASE_URL = "https://api.securitytrails.com/v1"


@IntegrationRegistry.register
class SecurityTrailsIntegration(BaseIntegration):
    name = "securitytrails"
    description = "SecurityTrails — DNS history, WHOIS, and subdomain discovery"
    rate_limit = 50
    cache_ttl = 3600

    def _headers(self) -> dict[str, str]:
        return {"APIKEY": self.api_key, "Accept": "application/json"}

    async def search(self, query: str, query_type: str = "domain") -> list[dict[str, Any]]:
        async with httpx.AsyncClient(timeout=15) as client:
            if query_type == "domain":
                resp = await client.get(f"{BASE_URL}/domain/{query}", headers=self._headers())
                if resp.status_code == 404:
                    return []
                resp.raise_for_status()
                return [resp.json()]
            elif query_type == "subdomain":
                resp = await client.get(
                    f"{BASE_URL}/domain/{query}/subdomains",
                    headers=self._headers(),
                    params={"children_only": "false"},
                )
                resp.raise_for_status()
                return resp.json().get("subdomains", [])
            elif query_type == "ip":
                resp = await client.get(
                    f"{BASE_URL}/ips/nearby/{query}",
                    headers=self._headers(),
                )
                resp.raise_for_status()
                return resp.json().get("blocks", [])
            elif query_type == "whois":
                resp = await client.get(f"{BASE_URL}/domain/{query}/whois", headers=self._headers())
                if resp.status_code == 404:
                    return []
                resp.raise_for_status()
                return [resp.json()]
            return []

    async def check_health(self) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(f"{BASE_URL}/ping", headers=self._headers())
            return {"status": "ok" if resp.status_code == 200 else "error", "code": resp.status_code}
