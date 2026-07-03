from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.core.response import ok
from app.models.system import SysUser
from app.schemas.auth import BootstrapAdminRequest, LoginRequest
from app.services.auth_service import AuthService

router = APIRouter(prefix="/api/auth", tags=["auth"])
service = AuthService()


@router.post("/login")
def login(req: LoginRequest, db: Session = Depends(get_db)):
    return ok(service.login(db, req.username, req.password))


@router.post("/bootstrap-admin")
def bootstrap_admin(req: BootstrapAdminRequest, db: Session = Depends(get_db)):
    return ok(service.bootstrap_admin(db, req))


@router.get("/me")
def me(user: SysUser = Depends(get_current_user), db: Session = Depends(get_db)):
    return ok(service.me(db, user))


@router.get("/menus")
def menus(user: SysUser = Depends(get_current_user), db: Session = Depends(get_db)):
    user_info = service.me(db, user)
    return ok(user_info["menus"])
