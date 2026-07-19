from fastapi import APIRouter

from app.api.deps import CurrentUser, DbSession
from app.services.insights import build_dashboard_snapshot

router = APIRouter(tags=["dashboard"])


@router.get("/dashboard")
def get_dashboard(current_user: CurrentUser, db: DbSession):
    return build_dashboard_snapshot(db, current_user)