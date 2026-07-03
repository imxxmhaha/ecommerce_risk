from fastapi import Depends, Header
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.errors import BizError, UNAUTHORIZED
from app.core.security import verify_access_token
from app.models.system import SysUser
from app.services.auth_service import AuthService

auth_service = AuthService()


def get_current_user(authorization: str | None = Header(None), db: Session = Depends(get_db)) -> SysUser:
    if not authorization or not authorization.startswith("Bearer "):
        raise BizError(UNAUTHORIZED, "missing token")
    user_id = verify_access_token(authorization.removeprefix("Bearer ").strip())
    return auth_service.get_user_by_id(db, user_id)


def require_permission(permission_code: str):
    def checker(user: SysUser = Depends(get_current_user), db: Session = Depends(get_db)):
        return auth_service.assert_permission(db, user, permission_code)

    return checker
