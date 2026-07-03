from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, Integer, String, Table, Text, func

from app.core.database import Base


sys_user_roles = Table(
    "sys_user_roles",
    Base.metadata,
    Column("user_id", BigInteger, ForeignKey("sys_users.id"), primary_key=True),
    Column("role_id", BigInteger, ForeignKey("sys_roles.id"), primary_key=True),
    Column("created_at", DateTime, nullable=False, server_default=func.now()),
)


sys_role_permissions = Table(
    "sys_role_permissions",
    Base.metadata,
    Column("role_id", BigInteger, ForeignKey("sys_roles.id"), primary_key=True),
    Column("permission_id", BigInteger, ForeignKey("sys_permissions.id"), primary_key=True),
    Column("created_at", DateTime, nullable=False, server_default=func.now()),
)


class SysUser(Base):
    __tablename__ = "sys_users"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    username = Column(String(64), nullable=False, unique=True)
    password_hash = Column(String(255), nullable=False)
    real_name = Column(String(64), nullable=False)
    status = Column(String(32), nullable=False, default="enabled")
    last_login_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())


class SysRole(Base):
    __tablename__ = "sys_roles"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    role_code = Column(String(64), nullable=False, unique=True)
    role_name = Column(String(64), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(32), nullable=False, default="enabled")
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())


class SysPermission(Base):
    __tablename__ = "sys_permissions"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    permission_code = Column(String(128), nullable=False, unique=True)
    permission_name = Column(String(128), nullable=False)
    permission_type = Column(String(32), nullable=False, default="api")
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())


class SysMenu(Base):
    __tablename__ = "sys_menus"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    menu_code = Column(String(64), nullable=False, unique=True)
    menu_name = Column(String(64), nullable=False)
    route_path = Column(String(128), nullable=False)
    permission_code = Column(String(128), nullable=True)
    icon = Column(String(64), nullable=True)
    sort_order = Column(Integer, nullable=False, default=100)
    status = Column(String(32), nullable=False, default="enabled")
    created_at = Column(DateTime, nullable=False, server_default=func.now())


class SysLoginLog(Base):
    __tablename__ = "sys_login_logs"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, nullable=True)
    username = Column(String(64), nullable=False)
    login_status = Column(String(32), nullable=False)
    login_message = Column(String(255), nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
