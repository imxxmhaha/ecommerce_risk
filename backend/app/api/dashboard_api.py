from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import require_permission
from app.core.database import get_db
from app.core.response import ok
from app.services.dashboard_service import DashboardService

router = APIRouter(prefix="/api/risk", tags=["dashboard"])
service = DashboardService()


@router.get("/dashboard", dependencies=[Depends(require_permission("dashboard:read"))])
def dashboard(start_date: str = None, end_date: str = None, db: Session = Depends(get_db)):
    return ok(service.dashboard(db, start_date, end_date))
