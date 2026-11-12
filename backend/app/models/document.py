from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models._mixins import TimestampMixin
from app.models.user import User


class Document(TimestampMixin, Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    # Sanitized HTML produced by the editor (see services/sanitizer.py).
    content_html: Mapped[str] = mapped_column(Text, default="")
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    # Optimistic concurrency: every successful write increments this.
    version: Mapped[int] = mapped_column(Integer, default=1)
    # Set when the document was created from an uploaded file.
    source_filename: Mapped[str | None] = mapped_column(String(255), nullable=True)

    owner: Mapped[User] = relationship(lazy="joined")
    shares: Mapped[list["DocumentShare"]] = relationship(  # noqa: F821
        back_populates="document", cascade="all, delete-orphan"
    )
