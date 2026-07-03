from datetime import datetime

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.errors import BizError, FORBIDDEN, PARAM_ERROR, UNAUTHORIZED
from app.core.security import create_access_token, hash_password, verify_password
from app.models.system import SysLoginLog, SysMenu, SysPermission, SysRole, SysUser, sys_role_permissions, sys_user_roles


def user_to_dict(user: SysUser, roles=None, permissions=None):
    return {
        "id": user.id,
        "username": user.username,
        "real_name": user.real_name,
        "status": user.status,
        "roles": roles or [],
        "permissions": permissions or [],
        "last_login_at": user.last_login_at,
        "created_at": user.created_at,
    }


class AuthService:
    def bootstrap_admin(self, db: Session, req):
        settings = get_settings()
        if not settings.bootstrap_admin_token:
            raise BizError(PARAM_ERROR, "bootstrap token is not configured")
        if req.bootstrap_token != settings.bootstrap_admin_token:
            raise BizError(UNAUTHORIZED, "invalid bootstrap token")
        if db.query(SysUser).count() > 0:
            raise BizError(PARAM_ERROR, "system user already exists")
        role = db.query(SysRole).filter(SysRole.role_code == "risk_admin", SysRole.status == "enabled").first()
        if not role:
            raise BizError(PARAM_ERROR, "risk_admin role is not initialized")
        user = SysUser(username=req.username, password_hash=hash_password(req.password), real_name=req.real_name, status="enabled")
        db.add(user)
        db.flush()
        db.execute(sys_user_roles.insert().values(user_id=user.id, role_id=role.id))
        db.commit()
        db.refresh(user)
        return user_to_dict(user, self.role_codes(db, user.id), self.permission_codes(db, user.id))

    def get_user_by_id(self, db: Session, user_id: int) -> SysUser:
        user = db.query(SysUser).filter(SysUser.id == user_id).first()
        if not user or user.status != "enabled":
            raise BizError(UNAUTHORIZED, "user is not available")
        return user

    def login(self, db: Session, username: str, password: str):
        user = db.query(SysUser).filter(SysUser.username == username).first()
        if not user or user.status != "enabled" or not verify_password(password, user.password_hash):
            db.add(SysLoginLog(username=username, user_id=user.id if user else None, login_status="failed", login_message="用户名或密码错误"))
            db.commit()
            raise BizError(UNAUTHORIZED, "用户名或密码错误")

        user.last_login_at = datetime.now()
        db.add(SysLoginLog(username=username, user_id=user.id, login_status="success", login_message="登录成功"))
        db.commit()
        token = create_access_token(user.id)
        permissions = self.permission_codes(db, user.id)
        roles = self.role_codes(db, user.id)
        return {
            "token": token,
            "token_type": "Bearer",
            "user": user_to_dict(user, roles, permissions),
            "permissions": permissions,
            "menus": self.menus(db, permissions),
        }

    def role_codes(self, db: Session, user_id: int):
        rows = (
            db.query(SysRole.role_code)
            .join(sys_user_roles, SysRole.id == sys_user_roles.c.role_id)
            .filter(sys_user_roles.c.user_id == user_id, SysRole.status == "enabled")
            .all()
        )
        return [row[0] for row in rows]

    def permission_codes(self, db: Session, user_id: int):
        rows = (
            db.query(SysPermission.permission_code)
            .join(sys_role_permissions, SysPermission.id == sys_role_permissions.c.permission_id)
            .join(sys_user_roles, sys_role_permissions.c.role_id == sys_user_roles.c.role_id)
            .join(SysRole, SysRole.id == sys_user_roles.c.role_id)
            .filter(sys_user_roles.c.user_id == user_id, SysRole.status == "enabled")
            .distinct()
            .all()
        )
        return [row[0] for row in rows]

    def menus(self, db: Session, permissions: list[str]):
        query = db.query(SysMenu).filter(SysMenu.status == "enabled").order_by(SysMenu.sort_order.asc(), SysMenu.id.asc())
        menus = query.all()
        return [
            {
                "menu_code": menu.menu_code,
                "menu_name": menu.menu_name,
                "route_path": menu.route_path,
                "permission_code": menu.permission_code,
                "icon": menu.icon,
                "sort_order": menu.sort_order,
            }
            for menu in menus
            if not menu.permission_code or menu.permission_code in permissions
        ]

    def me(self, db: Session, user: SysUser):
        permissions = self.permission_codes(db, user.id)
        roles = self.role_codes(db, user.id)
        return {
            "user": user_to_dict(user, roles, permissions),
            "permissions": permissions,
            "menus": self.menus(db, permissions),
        }

    def assert_permission(self, db: Session, user: SysUser, permission_code: str):
        if permission_code not in self.permission_codes(db, user.id):
            raise BizError(FORBIDDEN, "permission denied")
        return user
