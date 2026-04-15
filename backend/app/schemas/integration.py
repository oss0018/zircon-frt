from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class IntegrationCreate(BaseModel):
    service_name: str
    api_key: str | None = None
    settings: dict[str, Any] | None = None


class IntegrationUpdate(BaseModel):
    api_key: str | None = None
    is_active: bool | None = None
    settings: dict[str, Any] | None = None


class IntegrationResponse(BaseModel):
    id: int
    service_name: str
    is_active: bool
    rate_limit_remaining: int | None
    last_check: datetime | None

    model_config = {"from_attributes": True}


class IntegrationDetailResponse(IntegrationResponse):
    created_at: datetime
    updated_at: datetime | None = None


class ServiceCatalogueEntry(BaseModel):
    name: str
    display_name: str = ""
    description: str = ""
    category: str = ""
    website: str = ""
    query_types: list[str] = Field(default_factory=list)
    rate_limit: int = 60
    docs_url: str = ""
    is_configured: bool = False
    is_active: bool = False


class UnifiedSearchRequest(BaseModel):
    query: str
    query_type: str = "domain"
    services: list[str] | None = None  # None means all active
    use_cache: bool = True


class UnifiedSearchResult(BaseModel):
    service: str
    display_name: str
    results: list[dict[str, Any]]
    error: str | None = None
    cached: bool = False
    duration_ms: float = 0.0


class UnifiedSearchResponse(BaseModel):
    query: str
    query_type: str
    results: list[UnifiedSearchResult]
    total_services: int
    successful_services: int


class UsageStatsEntry(BaseModel):
    service: str
    today: int
    this_week: int
    this_month: int
    total: int


class TestConnectionResponse(BaseModel):
    service: str
    status: str  # ok | error
    message: str
    details: dict[str, Any] | None = None
