from pydantic import BaseModel


class MessageResponse(BaseModel):
    message: str


class PaginatedResponse(BaseModel):
    total: int
    page: int
    per_page: int
    items: list
