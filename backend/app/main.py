import logging
from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.core.middleware import RequestLoggingMiddleware

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# WebSocket connection manager for real-time notifications
_ws_connections: dict[int, list[WebSocket]] = {}


class ConnectionManager:
    async def connect(self, websocket: WebSocket, user_id: int) -> None:
        await websocket.accept()
        _ws_connections.setdefault(user_id, []).append(websocket)

    def disconnect(self, websocket: WebSocket, user_id: int) -> None:
        conns = _ws_connections.get(user_id, [])
        if websocket in conns:
            conns.remove(websocket)

    async def send_to_user(self, user_id: int, data: dict) -> None:
        import json

        for ws in list(_ws_connections.get(user_id, [])):
            try:
                await ws.send_text(json.dumps(data))
            except Exception:
                self.disconnect(ws, user_id)


ws_manager = ConnectionManager()


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
from app.api.v1 import auth, files, search, dashboard, integrations, monitoring, notifications, brand_protection, export  # noqa: E402

app.include_router(auth.router, prefix="/api/v1")
app.include_router(files.router, prefix="/api/v1")
app.include_router(search.router, prefix="/api/v1")
app.include_router(dashboard.router, prefix="/api/v1")
app.include_router(integrations.router, prefix="/api/v1")
app.include_router(monitoring.router, prefix="/api/v1")
app.include_router(notifications.router, prefix="/api/v1")
app.include_router(brand_protection.router, prefix="/api/v1")
app.include_router(export.router, prefix="/api/v1")


@app.websocket("/ws/notifications")
async def websocket_notifications(
    websocket: WebSocket,
    token: str = Query(...),
) -> None:
    """WebSocket endpoint for real-time notification push. Authenticated via JWT token."""
    from app.core.security import decode_token
    from app.db.session import AsyncSessionLocal
    from sqlalchemy import select
    from app.models.user import User

    try:
        payload = decode_token(token)
        user_id = int(payload.get("sub", 0))
    except Exception:
        await websocket.close(code=4001)
        return

    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

    if not user or not user.is_active:
        await websocket.close(code=4001)
        return

    await ws_manager.connect(websocket, user_id)
    logger.info("WebSocket connected for user %d", user_id)
    try:
        while True:
            await websocket.receive_text()  # keep connection alive
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket, user_id)
        logger.info("WebSocket disconnected for user %d", user_id)


@app.get("/health")
async def health() -> dict:
    return {"status": "ok", "version": settings.VERSION}
