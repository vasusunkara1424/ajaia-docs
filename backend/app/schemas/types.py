from datetime import UTC, datetime
from typing import Annotated

from pydantic import AfterValidator


def _as_utc(value: datetime) -> datetime:
    # SQLite drops tzinfo on read; all stored timestamps are UTC, so make that explicit
    # in the API so browsers don't misread them as local time.
    return value.replace(tzinfo=UTC) if value.tzinfo is None else value.astimezone(UTC)


UTCDateTime = Annotated[datetime, AfterValidator(_as_utc)]
