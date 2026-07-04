from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import require_permission
from app.core.database import get_db
from app.core.response import ok
from app.schemas.rule import RuleCreateRequest, RuleDeleteRequest, RuleStatusRequest, RuleUpdateRequest
from app.services.rule_service import RuleService

router = APIRouter(prefix="/api/risk/rules", tags=["rules"])
service = RuleService()


@router.get("", dependencies=[Depends(require_permission("rule:read"))])
def list_rules(rule_status: str = None, keyword: str = None, page: int = 1, page_size: int = 20, sort_by: str = None, sort_order: str = None, db: Session = Depends(get_db)):
    # 转换为整数，空字符串视为None
    status = int(rule_status) if rule_status and rule_status.strip() != '' else None
    return ok(service.list_rules(db, status, keyword, page, page_size, sort_by, sort_order))


@router.post("", dependencies=[Depends(require_permission("rule:write"))])
def create_rule(req: RuleCreateRequest, db: Session = Depends(get_db)):
    return ok(service.create_rule(db, req))


@router.post("/update", dependencies=[Depends(require_permission("rule:write"))])
def update_rule(req: RuleUpdateRequest, db: Session = Depends(get_db)):
    return ok(service.update_rule(db, req))


@router.post("/status", dependencies=[Depends(require_permission("rule:write"))])
def set_status(req: RuleStatusRequest, db: Session = Depends(get_db)):
    return ok(service.set_status(db, req))


@router.post("/delete", dependencies=[Depends(require_permission("rule:write"))])
def delete_rule(req: RuleDeleteRequest, db: Session = Depends(get_db)):
    return ok(service.delete_rule(db, req.id))
