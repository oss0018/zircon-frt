from datetime import datetime
from pydantic import BaseModel


class SearchFilters(BaseModel):
    file_type: str | None = None
    project_id: int | None = None
    date_from: datetime | None = None
    date_to: datetime | None = None


class SearchRequest(BaseModel):
    query: str
    filters: SearchFilters = SearchFilters()
    page: int = 1
    per_page: int = 20


class SearchHit(BaseModel):
    file_id: int
    filename: str
    file_type: str | None
    score: float
    highlights: list[str] = []
    created_at: str | None = None


class SearchResponse(BaseModel):
    total: int
    page: int
    per_page: int
    hits: list[SearchHit]
    took_ms: int
