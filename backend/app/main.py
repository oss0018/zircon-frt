import logging
from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.core.middleware import RequestLoggingMiddleware

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    logger.info("Starting Zircon FRT...")
    try:
        from app.services.indexer import ensure_index
        await ensure_index()
    except Exception as e:
        logger.warning("Elasticsearch not available on startup: %s", e)
    yield
    logger.info("Shutting down Zircon FRT...")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RequestLoggingMiddleware)

# Register API routers
from app.api.v1 import auth, files, search, dashboard, integrations, monitoring  # noqa: E402

app.include_router(auth.router, prefix="/api/v1")
app.include_router(files.router, prefix="/api/v1")
app.include_router(search.router, prefix="/api/v1")
app.include_router(dashboard.router, prefix="/api/v1")
app.include_router(integrations.router, prefix="/api/v1")
app.include_router(monitoring.router, prefix="/api/v1")


@app.get("/health")
async def health() -> dict:
    return {"status": "ok", "version": settings.VERSION}
