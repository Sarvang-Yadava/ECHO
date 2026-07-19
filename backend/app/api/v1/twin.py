from fastapi import APIRouter

from app.api.deps import CurrentUser, DbSession
from app.services.insights import build_twin_snapshot

router = APIRouter(tags=["twin"])


@router.get("/twin")
def get_twin(current_user: CurrentUser, db: DbSession):
    return build_twin_snapshot(db, current_user)