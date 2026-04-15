"""Tests for OSINT integration adapters and registry."""
import pytest

from app.integrations.registry import get_catalogue_entry, get_integration, list_available
from app.integrations.base import IntegrationRegistry


def test_list_available_returns_all_services():
    services = list_available()
    names = [s["name"] for s in services]
    expected = [
        "hibp", "intelx", "leakix", "hudsonrock",
        "virustotal", "urlhaus", "phishtank", "urlscan",
        "shodan", "censys", "securitytrails", "abuseipdb", "alienvault_otx",
    ]
    for name in expected:
        assert name in names, f"Expected service '{name}' not in registry"


def test_list_available_has_metadata():
    services = list_available()
    for svc in services:
        assert "display_name" in svc
        assert "description" in svc
        assert "category" in svc
        assert "query_types" in svc
        assert svc["rate_limit"] > 0


def test_get_catalogue_entry():
    entry = get_catalogue_entry("virustotal")
    assert entry["display_name"] == "VirusTotal"
    assert "url" in entry["query_types"]


def test_get_integration_returns_instance():
    adapter = get_integration("hibp", "test-key-123")
    assert adapter is not None
    assert adapter.api_key == "test-key-123"
    assert adapter.name == "hibp"


def test_get_integration_unknown_returns_none():
    adapter = get_integration("nonexistent_service", "key")
    assert adapter is None


def test_all_adapters_have_required_attributes():
    """Verify each registered adapter class has required class attributes."""
    for name in IntegrationRegistry.list_all():
        cls = IntegrationRegistry.get(name)
        assert cls is not None
        assert hasattr(cls, "name"), f"{cls} missing 'name'"
        assert hasattr(cls, "description"), f"{cls} missing 'description'"
        assert hasattr(cls, "rate_limit"), f"{cls} missing 'rate_limit'"
        assert hasattr(cls, "cache_ttl"), f"{cls} missing 'cache_ttl'"
        assert cls.rate_limit > 0, f"{cls}.rate_limit must be > 0"
        assert cls.cache_ttl > 0, f"{cls}.cache_ttl must be > 0"


def test_adapter_instantiation():
    """Verify all adapters can be instantiated with an API key."""
    for name in IntegrationRegistry.list_all():
        adapter = get_integration(name, "test-api-key")
        assert adapter is not None
        assert adapter.api_key == "test-api-key"
