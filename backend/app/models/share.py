from enum import StrEnum

from sqlalchemy import Enum, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models._mixins import TimestampMixin
from app.models.document import Document
from app.models.user import User


class ShareRole(StrEnum):
    VIEWER = "viewer"
    EDITOR = "editor"


class DocumentShare(TimestampMixin, Base):
    """Grants a non-owner user access to a document with a given role."""

    __tablename__ = "document_shares"
    __table_args__ = (UniqueConstraint("document_id", "user_id", name="uq_share_doc_user"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    document_id: Mapped[int] = mapped_column(
        ForeignKey("documents.id", ondelete="CASCADE"), index=True
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    role: Mapped[ShareRole] = mapped_column(
        Enum(ShareRole, native_enum=False, length=16, values_callable=lambda e: [m.value for m in e])
    )

    document: Mapped[Document] = relationship(back_populates="shares")
    user: Mapped[User] = relationship(lazy="joined")
