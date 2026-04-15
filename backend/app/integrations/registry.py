"""Integration registry — auto-loads all built-in adapters and exposes helpers."""
from __future__ import annotations

import importlib
import logging
from typing import TYPE_CHECKING

from app.integrations.base import BaseIntegration, IntegrationRegistry as _Registry

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

# Built-in integration modules to auto-register
_BUILTIN_MODULES = [
    "app.integrations.hibp",
    "app.integrations.intelx",
    "app.integrations.leakix",
    "app.integrations.hudsonrock",
    "app.integrations.virustotal",
    "app.integrations.urlhaus",
    "app.integrations.phishtank",
    "app.integrations.urlscan",
    "app.integrations.shodan_client",
    "app.integrations.censys_client",
    "app.integrations.securitytrails",
    "app.integrations.abuseipdb",
    "app.integrations.alienvault_otx",
]

# Metadata catalogue (name -> display info)
_CATALOGUE: dict[str, dict] = {
    "hibp": {
        "display_name": "Have I Been Pwned",
        "description": "Breach and paste monitoring",
        "category": "breach",
        "website": "https://haveibeenpwned.com",
        "query_types": ["email", "domain", "breach"],
        "rate_limit": 10,
        "docs_url": "https://haveibeenpwned.com/API/v3",
    },
    "intelx": {
        "display_name": "Intelligence X",
        "description": "Dark web and leak search engine",
        "category": "breach",
        "website": "https://intelx.io",
        "query_types": ["email", "domain", "ip", "bitcoin", "cidr"],
        "rate_limit": 30,
        "docs_url": "https://intelx.io/product",
    },
    "leakix": {
        "display_name": "LeakIX",
        "description": "Compromised device and data leak indexing",
        "category": "breach",
        "website": "https://leakix.net",
        "query_types": ["ip", "domain"],
        "rate_limit": 30,
        "docs_url": "https://leakix.net/api",
    },
    "hudsonrock": {
        "display_name": "Hudson Rock",
        "description": "Infostealer log and credential compromise monitoring",
        "category": "breach",
        "website": "https://hudsonrock.com",
        "query_types": ["email", "domain", "username"],
        "rate_limit": 10,
        "docs_url": "https://cavalier.hudsonrock.com/docs",
    },
    "virustotal": {
        "display_name": "VirusTotal",
        "description": "Malware and threat intelligence analysis",
        "category": "phishing",
        "website": "https://virustotal.com",
        "query_types": ["url", "domain", "ip", "hash"],
        "rate_limit": 4,
        "docs_url": "https://developers.virustotal.com/reference",
    },
    "urlhaus": {
        "display_name": "URLhaus",
        "description": "Malicious URL tracking by abuse.ch",
        "category": "phishing",
        "website": "https://urlhaus.abuse.ch",
        "query_types": ["url", "domain", "ip", "host", "hash"],
        "rate_limit": 60,
        "docs_url": "https://urlhaus-api.abuse.ch",
    },
    "phishtank": {
        "display_name": "PhishTank",
        "description": "Community phishing database verification",
        "category": "phishing",
        "website": "https://phishtank.org",
        "query_types": ["url"],
        "rate_limit": 30,
        "docs_url": "https://www.phishtank.com/api_info.php",
    },
    "urlscan": {
        "display_name": "urlscan.io",
        "description": "Web page scanning, screenshots and analysis",
        "category": "phishing",
        "website": "https://urlscan.io",
        "query_types": ["url", "domain", "ip"],
        "rate_limit": 60,
        "docs_url": "https://urlscan.io/docs/api/",
    },
    "shodan": {
        "display_name": "Shodan",
        "description": "IoT and infrastructure search engine",
        "category": "infrastructure",
        "website": "https://shodan.io",
        "query_types": ["ip", "domain", "hostname"],
        "rate_limit": 60,
        "docs_url": "https://developer.shodan.io/api",
    },
    "censys": {
        "display_name": "Censys",
        "description": "Global host and certificate transparency monitoring",
        "category": "infrastructure",
        "website": "https://censys.io",
        "query_types": ["ip", "domain", "certificate"],
        "rate_limit": 60,
        "docs_url": "https://search.censys.io/api",
    },
    "securitytrails": {
        "display_name": "SecurityTrails",
        "description": "DNS history, WHOIS, and subdomain discovery",
        "category": "infrastructure",
        "website": "https://securitytrails.com",
        "query_types": ["domain", "subdomain", "ip", "whois"],
        "rate_limit": 50,
        "docs_url": "https://docs.securitytrails.com/docs",
    },
    "abuseipdb": {
        "display_name": "AbuseIPDB",
        "description": "IP reputation and abuse report database",
        "category": "threat_intel",
        "website": "https://abuseipdb.com",
        "query_types": ["ip", "reports"],
        "rate_limit": 60,
        "docs_url": "https://docs.abuseipdb.com",
    },
    "alienvault_otx": {
        "display_name": "AlienVault OTX",
        "description": "Open Threat Exchange threat intelligence",
        "category": "threat_intel",
        "website": "https://otx.alienvault.com",
        "query_types": ["ip", "domain", "url", "hash"],
        "rate_limit": 100,
        "docs_url": "https://otx.alienvault.com/api",
    },
}


def _load_all() -> None:
    """Import all built-in modules so their @register decorators fire."""
    for module_path in _BUILTIN_MODULES:
        try:
            importlib.import_module(module_path)
        except Exception as exc:  # pragma: no cover
            logger.warning("Failed to load integration module %s: %s", module_path, exc)


_load_all()


def get_integration(name: str, api_key: str) -> BaseIntegration | None:
    """Instantiate an integration by name with the given API key."""
    cls = _Registry.get(name)
    if cls is None:
        return None
    return cls(api_key=api_key)


def list_available() -> list[dict]:
    """Return metadata for all registered integrations."""
    result = []
    for name in _Registry.list_all():
        info = _CATALOGUE.get(name, {})
        result.append({"name": name, **info})
    return result


def get_catalogue_entry(name: str) -> dict:
    """Return catalogue metadata for a single integration."""
    return _CATALOGUE.get(name, {})
