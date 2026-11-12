from typing import Annotated

from pydantic import BaseModel, ConfigDict, StringConstraints

from app.schemas.auth import UserOut
from app.schemas.types import UTCDateTime
from app.services.access import AccessLevel

Title = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=200)]


class DocumentPermissions(BaseModel):
    can_edit: bool
    can_share: bool
    can_delete: bool


class DocumentSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    owner: UserOut
    access: AccessLevel
    updated_at: UTCDateTime
    source_filename: str | None = None


class DocumentListResponse(BaseModel):
    owned: list[DocumentSummary]
    shared: list[DocumentSummary]


class DocumentDetail(DocumentSummary):
    content_html: str
    version: int
    permissions: DocumentPermissions


class DocumentCreate(BaseModel):
    title: Title = "Untitled document"


class DocumentUpdate(BaseModel):
    """Partial update. `version` must match the server's current version (optimistic locking)."""

    version: int
    title: Title | None = None
    content_html: str | None = None
