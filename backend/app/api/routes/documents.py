from fastapi import APIRouter, File, Response, UploadFile, status

from app.api.deps import CurrentUser, DbSession
from app.core.config import get_settings
from app.core.errors import PayloadTooLargeError
from app.models import Document
from app.schemas.auth import UserOut
from app.schemas.document import (
    DocumentCreate,
    DocumentDetail,
    DocumentListResponse,
    DocumentPermissions,
    DocumentSummary,
    DocumentUpdate,
)
from app.services import documents as document_service
from app.services.access import AccessLevel, can_edit, can_manage, get_document_for, require_owner
from app.services.exporter import html_to_markdown, safe_filename
from app.services.importer import import_file

router = APIRouter(prefix="/documents", tags=["documents"])


def _summary(document: Document, access: AccessLevel) -> DocumentSummary:
    return DocumentSummary(
        id=document.id,
        title=document.title,
        owner=UserOut.model_validate(document.owner),
        access=access,
        updated_at=document.updated_at,
        source_filename=document.source_filename,
    )


def _detail(document: Document, access: AccessLevel) -> DocumentDetail:
    return DocumentDetail(
        **_summary(document, access).model_dump(),
        content_html=document.content_html,
        version=document.version,
        permissions=DocumentPermissions(
            can_edit=can_edit(access),
            can_share=can_manage(access),
            can_delete=can_manage(access),
        ),
    )


@router.get("", response_model=DocumentListResponse)
def list_documents(db: DbSession, user: CurrentUser) -> DocumentListResponse:
    owned, shared = document_service.list_documents(db, user)
    return DocumentListResponse(
        owned=[_summary(doc, AccessLevel.OWNER) for doc in owned],
        shared=[_summary(doc, access) for doc, access in shared],
    )


@router.post("", response_model=DocumentDetail, status_code=status.HTTP_201_CREATED)
def create_document(body: DocumentCreate, db: DbSession, user: CurrentUser) -> DocumentDetail:
    document = document_service.create_document(db, user, title=body.title)
    return _detail(document, AccessLevel.OWNER)


@router.post("/import", response_model=DocumentDetail, status_code=status.HTTP_201_CREATED)
async def import_document(
    db: DbSession, user: CurrentUser, file: UploadFile = File(...)
) -> DocumentDetail:
    """Create a new editable document from a .txt, .md or .docx upload."""
    max_bytes = get_settings().max_upload_bytes
    data = await file.read(max_bytes + 1)  # read at most limit+1 bytes; never the whole stream
    if len(data) > max_bytes:
        raise PayloadTooLargeError(f"File is larger than {max_bytes // (1024 * 1024)} MB.")
    imported = import_file(file.filename or "", data)
    document = document_service.create_document(
        db,
        user,
        title=imported.title,
        content_html=imported.content_html,
        source_filename=imported.source_filename,
    )
    return _detail(document, AccessLevel.OWNER)


@router.get("/{document_id}", response_model=DocumentDetail)
def get_document(document_id: int, db: DbSession, user: CurrentUser) -> DocumentDetail:
    document, access = get_document_for(db, document_id, user)
    return _detail(document, access)


@router.patch("/{document_id}", response_model=DocumentDetail)
def update_document(
    document_id: int, body: DocumentUpdate, db: DbSession, user: CurrentUser
) -> DocumentDetail:
    document, access = get_document_for(db, document_id, user)
    document = document_service.update_document(db, document, access, body)
    return _detail(document, access)


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(document_id: int, db: DbSession, user: CurrentUser) -> Response:
    document, access = get_document_for(db, document_id, user)
    require_owner(access)
    document_service.delete_document(db, document)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/{document_id}/export/markdown")
def export_markdown(document_id: int, db: DbSession, user: CurrentUser) -> Response:
    document, _ = get_document_for(db, document_id, user)
    body = f"# {document.title}\n\n{html_to_markdown(document.content_html)}"
    filename = safe_filename(document.title, "md")
    return Response(
        content=body,
        media_type="text/markdown; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
