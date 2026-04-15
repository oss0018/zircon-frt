from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.search import SearchHit, SearchRequest, SearchResponse
from app.services.indexer import search_files


class SearchService:
    async def search(self, request: SearchRequest, user_id: int, db: AsyncSession) -> SearchResponse:
        result = await search_files(
            query=request.query,
            user_id=user_id,
            file_type=request.filters.file_type,
            project_id=request.filters.project_id,
            date_from=request.filters.date_from,
            date_to=request.filters.date_to,
            page=request.page,
            per_page=request.per_page,
        )

        total = result.get("hits", {}).get("total", {}).get("value", 0)
        took = result.get("took", 0)
        raw_hits = result.get("hits", {}).get("hits", [])

        hits = []
        for hit in raw_hits:
            source = hit.get("_source", {})
            highlights_raw = hit.get("highlight", {})
            highlights: list[str] = []
            for fragments in highlights_raw.values():
                highlights.extend(fragments)

            hits.append(SearchHit(
                file_id=source.get("file_id", 0),
                filename=source.get("filename", ""),
                file_type=source.get("file_type"),
                score=hit.get("_score", 0.0),
                highlights=highlights,
                created_at=source.get("created_at"),
            ))

        return SearchResponse(
            total=total,
            page=request.page,
            per_page=request.per_page,
            hits=hits,
            took_ms=took,
        )
