from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.auth import get_current_user
from app.db.session import get_db
from app.models.integration import Integration
from app.models.user import User
from app.services.crypto import CryptoService

router = APIRouter(prefix="/integrations", tags=["integrations"])


class IntegrationCreate(BaseModel):
    service_name: str
    api_key: str | None = None


class IntegrationResponse(BaseModel):
    id: int
    service_name: str
    is_active: bool
    rate_limit_remaining: int | None

    model_config = {"from_attributes": True}


@router.get("/", response_model=list[IntegrationResponse])
async def list_integrations(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[IntegrationResponse]:
    result = await db.execute(
        select(Integration).where(Integration.user_id == current_user.id)
    )
    integrations = result.scalars().all()
    return [IntegrationResponse.model_validate(i) for i in integrations]


@router.post("/", response_model=IntegrationResponse, status_code=status.HTTP_201_CREATED)
async def create_integration(
    request: IntegrationCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> IntegrationResponse:
    crypto = CryptoService()
    encrypted_key = crypto.encrypt(request.api_key) if request.api_key else None
    integration = Integration(
        service_name=request.service_name,
        api_key_encrypted=encrypted_key,
        user_id=current_user.id,
    )
    db.add(integration)
    await db.flush()
    await db.refresh(integration)
    return IntegrationResponse.model_validate(integration)


@router.delete("/{integration_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_integration(
    integration_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    result = await db.execute(
        select(Integration).where(
            Integration.id == integration_id, Integration.user_id == current_user.id
        )
    )
    integration = result.scalar_one_or_none()
    if not integration:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Integration not found")
    await db.delete(integration)
