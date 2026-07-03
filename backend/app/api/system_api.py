from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import require_permission
from app.core.database import get_db
from app.core.response import ok
from app.schemas.system import SystemRoleCreateRequest, SystemUserCreateRequest, SystemUserPasswordRequest, SystemUserStatusRequest
from app.services.system_service import SystemService

router = APIRouter(prefix="/api/system", tags=["system"])
service = SystemService()


@router.get("/users", dependencies=[Depends(require_permission("system:user:read"))])
def list_users(keyword: str = None, status: str = None, page: int = 1, page_size: int = 20, db: Session = Depends(get_db)):
    return ok(service.list_users(db, keyword, status, page, page_size))


@router.post("/users", dependencies=[Depends(require_permission("system:user:write"))])
def create_user(req: SystemUserCreateRequest, db: Session = Depends(get_db)):
    return ok(service.create_user(db, req))


@router.post("/users/status", dependencies=[Depends(require_permission("system:user:write"))])
def set_user_status(req: SystemUserStatusRequest, db: Session = Depends(get_db)):
    return ok(service.set_user_status(db, req))


@router.post("/users/password", dependencies=[Depends(require_permission("system:user:write"))])
def reset_password(req: SystemUserPasswordRequest, db: Session = Depends(get_db)):
    return ok(service.reset_password(db, req))


@router.get("/roles", dependencies=[Depends(require_permission("system:role:read"))])
def list_roles(db: Session = Depends(get_db)):
    return ok(service.list_roles(db))


@router.post("/roles", dependencies=[Depends(require_permission("system:role:write"))])
def create_role(req: SystemRoleCreateRequest, db: Session = Depends(get_db)):
    return ok(service.create_role(db, req))


@router.get("/permissions", dependencies=[Depends(require_permission("system:permission:read"))])
def list_permissions(db: Session = Depends(get_db)):
    return ok(service.list_permissions(db))
