"""Single source of truth for "who can do what" on a document.

Every route resolves access through `resolve_access` and then asks a
`require_*` helper. Keeping this in one module makes the policy easy to
read, review and test (see tests/test_access_control.py).

Policy
------
owner   view, edit, share, delete
editor  view, edit
viewer  view
none    nothing; reported as 404 so we never reveal that a document exists
"""

from enum import StrEnum

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import NotFoundError, PermissionDeniedError
from app.models import Document, DocumentShare, ShareRole, User


class AccessLevel(StrEnum):
    OWNER = "owner"
    EDITOR = "editor"
    VIEWER = "viewer"
    NONE = "none"


_EDIT_LEVELS = {AccessLevel.OWNER, AccessLevel.EDITOR}


def resolve_access(db: Session, document: Document, user: User) -> AccessLevel:
    if document.owner_id == user.id:
        return AccessLevel.OWNER
    role = db.scalar(
        select(DocumentShare.role).where(
            DocumentShare.document_id == document.id, DocumentShare.user_id == user.id
        )
    )
    if role is None:
        return AccessLevel.NONE
    return AccessLevel.EDITOR if role == ShareRole.EDITOR else AccessLevel.VIEWER


def can_edit(level: AccessLevel) -> bool:
    return level in _EDIT_LEVELS


def can_manage(level: AccessLevel) -> bool:
    return level == AccessLevel.OWNER


def get_document_for(db: Session, document_id: int, user: User) -> tuple[Document, AccessLevel]:
    """Load a document the user can at least view, or raise NotFoundError."""
    document = db.get(Document, document_id)
    if document is None:
        raise NotFoundError("Document not found.")
    level = resolve_access(db, document, user)
    if level == AccessLevel.NONE:
        raise NotFoundError("Document not found.")
    return document, level


def require_edit(level: AccessLevel) -> None:
    if not can_edit(level):
        raise PermissionDeniedError("You have view-only access to this document.")


def require_owner(level: AccessLevel) -> None:
    if not can_manage(level):
        raise PermissionDeniedError("Only the document owner can do this.")
