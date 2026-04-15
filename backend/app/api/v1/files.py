import os
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import FileResponse as FastAPIFileResponse
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.auth import get_current_user
from app.db.session import get_db
from app.models.file import File as FileModel
from app.models.user import User
from app.schemas.file import FileListResponse, FileRenameRequest, FileResponse
from app.services.file_service import FileService
from app.tasks.file_tasks import process_uploaded_file

router = APIRouter(prefix="/files", tags=["files"])


@router.post("/upload", response_model=FileResponse, status_code=status.HTTP_201_CREATED)
async def upload_file(
    file: UploadFile = File(...),
    project_id: int | None = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> FileResponse:
    service = FileService()
    db_file = await service.save_upload(file, current_user.id, project_id, db)
    # Trigger async processing
    try:
        process_uploaded_file.delay(db_file.id)
    except Exception:
        pass  # Celery might not be available in dev
    return FileResponse.model_validate(db_file)


@router.get("/", response_model=FileListResponse)
async def list_files(
    page: int = 1,
    per_page: int = 20,
    project_id: int | None = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> FileListResponse:
    query = select(FileModel).where(FileModel.user_id == current_user.id)
    if project_id:
        query = query.where(FileModel.project_id == project_id)

    count_result = await db.execute(
        select(func.count()).select_from(query.subquery())
    )
    total = count_result.scalar_one()

    result = await db.execute(
        query.order_by(FileModel.created_at.desc()).offset((page - 1) * per_page).limit(per_page)
    )
    files = result.scalars().all()
    return FileListResponse(total=total, items=[FileResponse.model_validate(f) for f in files])


@router.get("/{file_id}", response_model=FileResponse)
async def get_file(
    file_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> FileResponse:
    result = await db.execute(
        select(FileModel).where(FileModel.id == file_id, FileModel.user_id == current_user.id)
    )
    file = result.scalar_one_or_none()
    if not file:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
    return FileResponse.model_validate(file)


@router.get("/{file_id}/download")
async def download_file(
    file_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> FastAPIFileResponse:
    result = await db.execute(
        select(FileModel).where(FileModel.id == file_id, FileModel.user_id == current_user.id)
    )
    file = result.scalar_one_or_none()
    if not file:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
    if not os.path.exists(file.filepath):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found on disk")
    return FastAPIFileResponse(file.filepath, filename=file.filename)


@router.patch("/{file_id}/rename", response_model=FileResponse)
async def rename_file(
    file_id: int,
    request: FileRenameRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> FileResponse:
    result = await db.execute(
        select(FileModel).where(FileModel.id == file_id, FileModel.user_id == current_user.id)
    )
    file = result.scalar_one_or_none()
    if not file:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
    file.filename = request.filename
    await db.flush()
    await db.refresh(file)
    return FileResponse.model_validate(file)


@router.delete("/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_file(
    file_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    result = await db.execute(
        select(FileModel).where(FileModel.id == file_id, FileModel.user_id == current_user.id)
    )
    file = result.scalar_one_or_none()
    if not file:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
    service = FileService()
    await service.delete_file(file, db)
