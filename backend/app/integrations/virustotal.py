"""VirusTotal integration — URL, domain, IP, and file hash analysis."""
from typing import Any

import httpx

from app.integrations.base import BaseIntegration, IntegrationRegistry

BASE_URL = "https://www.virustotal.com/api/v3"


@IntegrationRegistry.register
class VirusTotalIntegration(BaseIntegration):
    name = "virustotal"
    description = "VirusTotal — malware and threat intelligence analysis"
    rate_limit = 4  # free tier; premium is 500/min
    cache_ttl = 3600

    def _headers(self) -> dict[str, str]:
        return {"x-apikey": self.api_key}

    async def search(self, query: str, query_type: str = "url") -> list[dict[str, Any]]:
        async with httpx.AsyncClient(timeout=30) as client:
            if query_type == "url":
                import base64
                url_id = base64.urlsafe_b64encode(query.encode()).decode().rstrip("=")
                resp = await client.get(f"{BASE_URL}/urls/{url_id}", headers=self._headers())
            elif query_type == "domain":
                resp = await client.get(f"{BASE_URL}/domains/{query}", headers=self._headers())
            elif query_type == "ip":
                resp = await client.get(f"{BASE_URL}/ip_addresses/{query}", headers=self._headers())
            elif query_type == "hash":
                resp = await client.get(f"{BASE_URL}/files/{query}", headers=self._headers())
            else:
                return []
            if resp.status_code == 404:
                return []
            resp.raise_for_status()
            return [resp.json().get("data", {})]

    async def check_health(self) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(f"{BASE_URL}/users/current/overall_quotas", headers=self._headers())
            return {"status": "ok" if resp.status_code == 200 else "error", "code": resp.status_code}
