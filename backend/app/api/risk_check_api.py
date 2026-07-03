from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import require_permission
from app.core.database import get_db
from app.core.response import ok
from app.schemas.risk_check import RiskCheckRequest
from app.services.risk_check_service import RiskCheckService

router = APIRouter(prefix="/api/risk", tags=["risk-check"])
service = RiskCheckService()


@router.post("/check", dependencies=[Depends(require_permission("risk:check"))])
def check(req: RiskCheckRequest, db: Session = Depends(get_db)):
    return ok(service.check(db, req))
