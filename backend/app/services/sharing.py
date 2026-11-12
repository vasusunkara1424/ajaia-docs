"""Sharing use cases: list, grant/update, revoke."""

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.errors import NotFoundError, ValidationFailedError
from app.models import Document, DocumentShare, ShareRole, User


def list_shares(db: Session, document: Document) -> list[DocumentShare]:
    return list(
        db.scalars(
            select(DocumentShare)
            .where(DocumentShare.document_id == document.id)
            .order_by(DocumentShare.created_at)
        ).all()
    )


def grant_access(db: Session, document: Document, email: str, role: ShareRole) -> DocumentShare:
    """Share with a user, or change their role if already shared (idempotent)."""
    target = db.scalar(select(User).where(func.lower(User.email) == email.lower()))
    if target is None:
        raise NotFoundError(f"No user found with email {email}.")
    if target.id == document.owner_id:
        raise ValidationFailedError("The owner already has full access.")

    share = db.scalar(
        select(DocumentShare).where(
            DocumentShare.document_id == document.id, DocumentShare.user_id == target.id
        )
    )
    if share is None:
        share = DocumentShare(document_id=document.id, user_id=target.id, role=role)
        db.add(share)
    else:
        share.role = role
    db.commit()
    db.refresh(share)
    return share


def revoke_access(db: Session, document: Document, user_id: int) -> None:
    share = db.scalar(
        select(DocumentShare).where(
            DocumentShare.document_id == document.id, DocumentShare.user_id == user_id
        )
    )
    if share is None:
        raise NotFoundError("This user does not have access.")
    db.delete(share)
    db.commit()
