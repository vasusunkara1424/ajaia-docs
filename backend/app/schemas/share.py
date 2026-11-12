from pydantic import BaseModel, ConfigDict, EmailStr

from app.models.share import ShareRole
from app.schemas.auth import UserOut
from app.schemas.types import UTCDateTime


class ShareRequest(BaseModel):
    email: EmailStr
    role: ShareRole = ShareRole.VIEWER


class ShareOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user: UserOut
    role: ShareRole
    created_at: UTCDateTime
