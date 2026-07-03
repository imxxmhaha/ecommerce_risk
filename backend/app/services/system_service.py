from sqlalchemy.orm import Session

from app.core.errors import BizError, CONFLICT, NOT_FOUND
from app.core.security import hash_password
from app.models.system import SysPermission, SysRole, SysUser, sys_role_permissions, sys_user_roles
from app.services.auth_service import user_to_dict


class SystemService:
    def list_users(self, db: Session, keyword=None, status=None, page=1, page_size=20):
        query = db.query(SysUser)
        if keyword:
            like = f"%{keyword}%"
            query = query.filter((SysUser.username.like(like)) | (SysUser.real_name.like(like)))
        if status:
            query = query.filter(SysUser.status == status)
        total = query.count()
        users = query.order_by(SysUser.id.asc()).offset((page - 1) * page_size).limit(page_size).all()
        return {"items": [user_to_dict(user, self._role_codes(db, user.id), self._permission_codes(db, user.id)) for user in users], "total": total, "page": page, "page_size": page_size}

    def create_user(self, db: Session, req):
        if db.query(SysUser).filter(SysUser.username == req.username).first():
            raise BizError(CONFLICT, "username already exists")
        roles = db.query(SysRole).filter(SysRole.role_code.in_(req.role_codes), SysRole.status == "enabled").all()
        if len(roles) != len(set(req.role_codes)):
            raise BizError(NOT_FOUND, "role not found")
        user = SysUser(username=req.username, password_hash=hash_password(req.password), real_name=req.real_name, status=req.status)
        db.add(user)
        db.flush()
        for role in roles:
            db.execute(sys_user_roles.insert().values(user_id=user.id, role_id=role.id))
        db.commit()
        db.refresh(user)
        return user_to_dict(user, self._role_codes(db, user.id), self._permission_codes(db, user.id))

    def set_user_status(self, db: Session, req):
        user = db.query(SysUser).filter(SysUser.id == req.user_id).first()
        if not user:
            raise BizError(NOT_FOUND, "user not found")
        user.status = req.status
        db.commit()
        return user_to_dict(user, self._role_codes(db, user.id), self._permission_codes(db, user.id))

    def reset_password(self, db: Session, req):
        user = db.query(SysUser).filter(SysUser.id == req.user_id).first()
        if not user:
            raise BizError(NOT_FOUND, "user not found")
        user.password_hash = hash_password(req.password)
        db.commit()
        return {"updated": True}

    def list_roles(self, db: Session):
        roles = db.query(SysRole).order_by(SysRole.id.asc()).all()
        return [
            {
                "id": role.id,
                "role_code": role.role_code,
                "role_name": role.role_name,
                "description": role.description,
                "status": role.status,
                "permissions": self._role_permissions(db, role.id),
                "created_at": role.created_at,
            }
            for role in roles
        ]

    def create_role(self, db: Session, req):
        if db.query(SysRole).filter(SysRole.role_code == req.role_code).first():
            raise BizError(CONFLICT, "role_code already exists")
        permissions = db.query(SysPermission).filter(SysPermission.permission_code.in_(req.permission_codes)).all()
        if len(permissions) != len(set(req.permission_codes)):
            raise BizError(NOT_FOUND, "permission not found")
        role = SysRole(role_code=req.role_code, role_name=req.role_name, description=req.description, status=req.status)
        db.add(role)
        db.flush()
        for permission in permissions:
            db.execute(sys_role_permissions.insert().values(role_id=role.id, permission_id=permission.id))
        db.commit()
        db.refresh(role)
        return {"id": role.id, "role_code": role.role_code, "role_name": role.role_name, "permissions": self._role_permissions(db, role.id)}

    def list_permissions(self, db: Session):
        permissions = db.query(SysPermission).order_by(SysPermission.permission_code.asc()).all()
        return [
            {
                "id": item.id,
                "permission_code": item.permission_code,
                "permission_name": item.permission_name,
                "permission_type": item.permission_type,
                "description": item.description,
            }
            for item in permissions
        ]

    def _role_codes(self, db: Session, user_id: int):
        rows = db.query(SysRole.role_code).join(sys_user_roles, SysRole.id == sys_user_roles.c.role_id).filter(sys_user_roles.c.user_id == user_id).all()
        return [row[0] for row in rows]

    def _permission_codes(self, db: Session, user_id: int):
        rows = (
            db.query(SysPermission.permission_code)
            .join(sys_role_permissions, SysPermission.id == sys_role_permissions.c.permission_id)
            .join(sys_user_roles, sys_role_permissions.c.role_id == sys_user_roles.c.role_id)
            .filter(sys_user_roles.c.user_id == user_id)
            .distinct()
            .all()
        )
        return [row[0] for row in rows]

    def _role_permissions(self, db: Session, role_id: int):
        rows = (
            db.query(SysPermission.permission_code)
            .join(sys_role_permissions, SysPermission.id == sys_role_permissions.c.permission_id)
            .filter(sys_role_permissions.c.role_id == role_id)
            .all()
        )
        return [row[0] for row in rows]
