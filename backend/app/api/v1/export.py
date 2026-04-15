"""Export endpoints: CSV, JSON, PDF for search results and brand alerts."""
import csv
import io
import json
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response, StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.auth import get_current_user
from app.db.session import get_db
from app.models.brand import BrandAlert, BrandWatch
from app.models.user import User

router = APIRouter(prefix="/export", tags=["export"])


def _csv_response(rows: list[dict], filename: str) -> StreamingResponse:
    if not rows:
        content = ""
    else:
        buf = io.StringIO()
        writer = csv.DictWriter(buf, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
        content = buf.getvalue()
    return StreamingResponse(
        iter([content]),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


def _json_response(data: object, filename: str) -> Response:
    content = json.dumps(data, ensure_ascii=False, indent=2, default=str)
    return Response(
        content=content,
        media_type="application/json",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


def _pdf_response(title: str, headers: list[str], rows: list[list], filename: str) -> Response:
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib.units import cm
        from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

        buf = io.BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=landscape(A4), leftMargin=1.5 * cm, rightMargin=1.5 * cm)
        styles = getSampleStyleSheet()
        story = [
            Paragraph(title, styles["Title"]),
            Paragraph(f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}", styles["Normal"]),
            Spacer(1, 0.5 * cm),
        ]
        table_data = [headers] + rows
        t = Table(table_data, repeatRows=1)
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0e7490")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f0f9ff")]),
            ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#e2e8f0")),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        story.append(t)
        doc.build(story)
        buf.seek(0)
        return Response(
            content=buf.read(),
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )
    except ImportError:
        return Response(content="PDF export requires reportlab", status_code=500)


# ── Search results export ───────────────────────────────────────────────────

@router.get("/search")
async def export_search(
    q: str = Query(..., description="Search query"),
    fmt: str = Query("csv", description="Format: csv|json|pdf"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Response:
    from app.services.search_service import SearchService
    from app.schemas.search import SearchRequest

    svc = SearchService()
    resp = await svc.search(SearchRequest(query=q, per_page=1000), current_user.id, db)
    now = datetime.now(timezone.utc)
    ts = now.strftime("%Y%m%d_%H%M%S")

    if fmt == "json":
        return _json_response(
            {"query": q, "total": resp.total, "exported_at": now.isoformat(), "hits": [h.model_dump() for h in resp.hits]},
            f"search_results_{ts}.json",
        )
    if fmt == "pdf":
        headers = ["File ID", "Filename", "Type", "Score", "Date"]
        rows = [[str(h.file_id), h.filename, h.file_type or "", f"{h.score:.2f}", h.created_at or ""] for h in resp.hits]
        return _pdf_response(f'Search Results: "{q}"', headers, rows, f"search_results_{ts}.pdf")
    # default: CSV
    rows_dicts = [{"file_id": h.file_id, "filename": h.filename, "file_type": h.file_type, "score": round(h.score, 4), "created_at": h.created_at} for h in resp.hits]
    return _csv_response(rows_dicts, f"search_results_{ts}.csv")


# ── Brand alerts export ──────────────────────────────────────────────────────

@router.get("/brand/{watch_id}/alerts")
async def export_brand_alerts(
    watch_id: int,
    fmt: str = Query("csv", description="Format: csv|json|pdf"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Response:
    result = await db.execute(
        select(BrandWatch).where(BrandWatch.id == watch_id, BrandWatch.user_id == current_user.id)
    )
    watch = result.scalar_one_or_none()
    if not watch:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Brand watch not found")

    alerts_result = await db.execute(
        select(BrandAlert).where(BrandAlert.brand_watch_id == watch_id).order_by(BrandAlert.created_at.desc())
    )
    alerts = list(alerts_result.scalars().all())
    now = datetime.now(timezone.utc)
    ts = now.strftime("%Y%m%d_%H%M%S")

    if fmt == "json":
        return _json_response(
            {
                "brand": watch.name,
                "original_url": watch.original_url,
                "exported_at": now.isoformat(),
                "alerts": [
                    {"id": a.id, "found_domain": a.found_domain, "similarity_score": a.similarity_score,
                     "status": a.status, "created_at": a.created_at.isoformat() if a.created_at else None}
                    for a in alerts
                ],
            },
            f"brand_alerts_{watch.name}_{ts}.json",
        )
    if fmt == "pdf":
        headers = ["Found Domain", "Similarity %", "Status", "Detected At"]
        rows = [[a.found_domain, f"{a.similarity_score:.1f}", a.status, a.created_at.strftime("%Y-%m-%d") if a.created_at else ""] for a in alerts]
        return _pdf_response(f"Brand Alerts: {watch.name}", headers, rows, f"brand_alerts_{watch.name}_{ts}.pdf")
    # default: CSV
    rows_dicts = [{"found_domain": a.found_domain, "similarity_score": a.similarity_score, "status": a.status, "created_at": a.created_at} for a in alerts]
    return _csv_response(rows_dicts, f"brand_alerts_{watch.name}_{ts}.csv")


# ── Monitoring / watchlist export ────────────────────────────────────────────

@router.get("/monitoring/watchlist")
async def export_watchlist(
    fmt: str = Query("csv", description="Format: csv|json"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Response:
    from app.models.watchlist import WatchlistItem

    result = await db.execute(select(WatchlistItem).where(WatchlistItem.user_id == current_user.id))
    items = list(result.scalars().all())
    now = datetime.now(timezone.utc)
    ts = now.strftime("%Y%m%d_%H%M%S")

    if fmt == "json":
        return _json_response(
            {"exported_at": now.isoformat(), "items": [
                {"id": i.id, "type": i.item_type, "value": i.value, "is_active": i.is_active}
                for i in items
            ]},
            f"watchlist_{ts}.json",
        )
    rows = [{"id": i.id, "type": i.item_type, "value": i.value, "is_active": i.is_active} for i in items]
    return _csv_response(rows, f"watchlist_{ts}.csv")
