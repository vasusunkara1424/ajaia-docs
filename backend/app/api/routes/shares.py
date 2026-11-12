from fastapi import APIRouter, Response, status

from app.api.deps import CurrentUser, DbSession
from app.schemas.share import ShareOut, ShareRequest
from app.services import sharing as sharing_service
from app.services.access import get_document_for, require_owner

router = APIRouter(prefix="/documents/{document_id}/shares", tags=["sharing"])


@router.get("", response_model=list[ShareOut])
def list_shares(document_id: int, db: DbSession, user: CurrentUser):
    document, _ = get_document_for(db, document_id, user)  # any collaborator can see who has access
    return sharing_service.list_shares(db, document)


@router.put("", response_model=ShareOut)
def grant_access(document_id: int, body: ShareRequest, db: DbSession, user: CurrentUser):
    document, access = get_document_for(db, document_id, user)
    require_owner(access)
    return sharing_service.grant_access(db, document, body.email, body.role)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def revoke_access(document_id: int, user_id: int, db: DbSession, user: CurrentUser) -> Response:
    document, access = get_document_for(db, document_id, user)
    require_owner(access)
    sharing_service.revoke_access(db, document, user_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
