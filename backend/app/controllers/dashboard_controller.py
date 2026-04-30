from fastapi import APIRouter
from fastapi import Query
from app.database import SessionDep
from app.services.dashboard_service import get_dashboard

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("")
def dashboard(
    session: SessionDep,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100),
):
    return get_dashboard(session, offset=offset, limit=limit)