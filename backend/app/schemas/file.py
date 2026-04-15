from datetime import datetime
from pydantic import BaseModel


class FileResponse(BaseModel):
    id: int
    filename: str
    file_type: str | None
    size_bytes: int | None
    project_id: int | None
    user_id: int
    indexed: bool
    quarantined: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class FileRenameRequest(BaseModel):
    filename: str


class FileListResponse(BaseModel):
    total: int
    items: list[FileResponse]
