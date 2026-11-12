"""Document use cases: list, create, update, delete."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.errors import ConflictError, PayloadTooLargeError
from app.models import Document, DocumentShare, ShareRole, User
from app.schemas.document import DocumentUpdate
from app.services.access import AccessLevel, require_edit
from app.services.sanitizer import sanitize_html


def list_documents(
    db: Session, user: User
) -> tuple[list[Document], list[tuple[Document, AccessLevel]]]:
    owned = db.scalars(
        select(Document).where(Document.owner_id == user.id).order_by(Document.updated_at.desc())
    ).all()

    shared_rows = db.execute(
        select(Document, DocumentShare.role)
        .join(DocumentShare, DocumentShare.document_id == Document.id)
        .where(DocumentShare.user_id == user.id)
        .order_by(Document.updated_at.desc())
    ).all()
    shared = [
        (doc, AccessLevel.EDITOR if role == ShareRole.EDITOR else AccessLevel.VIEWER)
        for doc, role in shared_rows
    ]
    return list(owned), shared


def create_document(
    db: Session,
    owner: User,
    title: str,
    content_html: str = "",
    source_filename: str | None = None,
) -> Document:
    document = Document(
        title=title,
        content_html=sanitize_html(content_html),
        owner_id=owner.id,
        source_filename=source_filename,
    )
    db.add(document)
    db.commit()
    db.refresh(document)
    return document


def update_document(
    db: Session, document: Document, level: AccessLevel, payload: DocumentUpdate
) -> Document:
    require_edit(level)

    if payload.version != document.version:
        raise ConflictError(
            "This document was changed by someone else. Reload to get the latest version."
        )

    if payload.title is not None:
        document.title = payload.title

    if payload.content_html is not None:
        if len(payload.content_html.encode()) > get_settings().max_content_bytes:
            raise PayloadTooLargeError("Document is too large to save.")
        document.content_html = sanitize_html(payload.content_html)

    document.version += 1
    db.commit()
    db.refresh(document)
    return document


def delete_document(db: Session, document: Document) -> None:
    db.delete(document)
    db.commit()
