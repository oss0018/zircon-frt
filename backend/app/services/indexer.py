import logging
from datetime import datetime

from elasticsearch import AsyncElasticsearch, NotFoundError

from app.config import settings

logger = logging.getLogger(__name__)

INDEX_NAME = "zircon_files"

INDEX_MAPPINGS = {
    "mappings": {
        "properties": {
            "file_id": {"type": "integer"},
            "filename": {"type": "text", "analyzer": "standard", "fields": {"keyword": {"type": "keyword"}}},
            "content": {"type": "text", "analyzer": "standard"},
            "file_type": {"type": "keyword"},
            "project_id": {"type": "integer"},
            "user_id": {"type": "integer"},
            "size_bytes": {"type": "long"},
            "created_at": {"type": "date"},
        }
    },
    "settings": {
        "number_of_shards": 1,
        "number_of_replicas": 0,
    },
}


def get_es_client() -> AsyncElasticsearch:
    return AsyncElasticsearch([settings.ELASTICSEARCH_URL])


async def ensure_index() -> None:
    es = get_es_client()
    try:
        exists = await es.indices.exists(index=INDEX_NAME)
        if not exists:
            await es.indices.create(index=INDEX_NAME, body=INDEX_MAPPINGS)
            logger.info("Created Elasticsearch index: %s", INDEX_NAME)
    except Exception as e:
        logger.error("Failed to create index: %s", e)
    finally:
        await es.close()


async def index_file(
    file_id: int,
    filename: str,
    content: str,
    file_type: str | None,
    project_id: int | None,
    user_id: int,
    size_bytes: int | None,
    created_at: datetime | None,
) -> None:
    es = get_es_client()
    try:
        doc = {
            "file_id": file_id,
            "filename": filename,
            "content": content,
            "file_type": file_type,
            "project_id": project_id,
            "user_id": user_id,
            "size_bytes": size_bytes,
            "created_at": created_at.isoformat() if created_at else None,
        }
        await es.index(index=INDEX_NAME, id=str(file_id), document=doc)
        logger.info("Indexed file %d", file_id)
    except Exception as e:
        logger.error("Failed to index file %d: %s", file_id, e)
    finally:
        await es.close()


async def delete_from_index(file_id: int) -> None:
    es = get_es_client()
    try:
        await es.delete(index=INDEX_NAME, id=str(file_id))
    except NotFoundError:
        pass
    except Exception as e:
        logger.error("Failed to delete file %d from index: %s", file_id, e)
    finally:
        await es.close()


async def search_files(
    query: str,
    user_id: int,
    file_type: str | None = None,
    project_id: int | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    page: int = 1,
    per_page: int = 20,
) -> dict:
    es = get_es_client()
    try:
        must = [{"term": {"user_id": user_id}}]

        # Parse query for operators
        if '"' in query:
            # Exact phrase search
            must.append({"multi_match": {"query": query.strip('"'), "fields": ["content", "filename"], "type": "phrase"}})
        else:
            must.append({
                "multi_match": {
                    "query": query,
                    "fields": ["content^1", "filename^2"],
                    "operator": "or" if " OR " in query else "and",
                    "fuzziness": "AUTO",
                }
            })

        if file_type:
            must.append({"term": {"file_type": file_type}})
        if project_id:
            must.append({"term": {"project_id": project_id}})
        if date_from or date_to:
            date_range: dict = {}
            if date_from:
                date_range["gte"] = date_from.isoformat()
            if date_to:
                date_range["lte"] = date_to.isoformat()
            must.append({"range": {"created_at": date_range}})

        body = {
            "query": {"bool": {"must": must}},
            "highlight": {
                "fields": {"content": {"fragment_size": 150, "number_of_fragments": 3}, "filename": {}},
                "pre_tags": ["<mark>"],
                "post_tags": ["</mark>"],
            },
            "from": (page - 1) * per_page,
            "size": per_page,
        }

        response = await es.search(index=INDEX_NAME, body=body)
        return response.body
    except Exception as e:
        logger.error("Search failed: %s", e)
        return {"hits": {"total": {"value": 0}, "hits": []}, "took": 0}
    finally:
        await es.close()
