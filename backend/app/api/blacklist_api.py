from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import require_permission
from app.core.database import get_db
from app.core.response import ok
from app.models.system import SysUser
from app.schemas.blacklist import BlacklistCreateRequest, BlacklistDeleteRequest, BlacklistStatusRequest
from app.services.blacklist_service import BlacklistService

router = APIRouter(prefix="/api/risk/blacklists", tags=["blacklists"])
service = BlacklistService()


@router.get("", dependencies=[Depends(require_permission("blacklist:read"))])
def list_items(blacklist_type: str = None, status: str = None, keyword: str = None, page: int = 1, page_size: int = 20, db: Session = Depends(get_db)):
    return ok(service.list_items(db, blacklist_type, status, keyword, page, page_size))


@router.post("")
def create(req: BlacklistCreateRequest, user: SysUser = Depends(require_permission("blacklist:write")), db: Session = Depends(get_db)):
    req.created_by = str(user.id)
    return ok(service.create(db, req))


@router.post("/status", dependencies=[Depends(require_permission("blacklist:write"))])
def set_status(req: BlacklistStatusRequest, db: Session = Depends(get_db)):
    return ok(service.set_status(db, req.id, req.status))


@router.post("/delete", dependencies=[Depends(require_permission("blacklist:write"))])
def delete(req: BlacklistDeleteRequest, db: Session = Depends(get_db)):
    return ok(service.delete(db, req.id))
