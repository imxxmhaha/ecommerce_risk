from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import require_permission
from app.core.database import get_db
from app.core.response import ok
from app.models.system import SysUser
from app.schemas.case import CaseReviewRequest
from app.services.case_service import CaseService

router = APIRouter(prefix="/api/risk/cases", tags=["cases"])
service = CaseService()


@router.get("", dependencies=[Depends(require_permission("case:read"))])
def list_cases(case_status: str = None, user_id: str = None, order_id: str = None, page: int = 1, page_size: int = 20, db: Session = Depends(get_db)):
    return ok(service.list_cases(db, case_status, user_id, order_id, page, page_size))


@router.get("/{case_id}", dependencies=[Depends(require_permission("case:read"))])
def detail(case_id: int, db: Session = Depends(get_db)):
    return ok(service.detail(db, case_id))


@router.post("/review")
def review(req: CaseReviewRequest, user: SysUser = Depends(require_permission("case:review")), db: Session = Depends(get_db)):
    req.operator_id = str(user.id)
    return ok(service.review(db, req))
