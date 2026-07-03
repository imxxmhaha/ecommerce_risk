"""
验收测试配置 - 直接连接MySQL数据库
注意：测试数据会直接写入数据库，测试后需要手动清理或使用独立测试库
"""
from typing import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings
from app.core.database import get_db
from app.main import app

# 创建数据库连接
settings = get_settings()
engine = create_engine(settings.database_url, pool_pre_ping=True, pool_recycle=3600)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db() -> Generator[Session, None, None]:
    """数据库会话"""
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(scope="function")
def client(db: Session) -> Generator[TestClient, None, None]:
    """FastAPI测试客户端，注入测试数据库"""

    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def admin_token(client: TestClient, db: Session) -> str:
    """获取管理员Token，用于认证测试"""
    # 使用种子数据中的默认账号登录
    # 种子数据: risk_admin / 123456
    login_data = {"username": "risk_admin", "password": "123456"}
    response = client.post("/api/auth/login", json=login_data)
    if response.status_code == 200:
        data = response.json()
        if data.get("code") == 0:
            return data["data"]["token"]

    # 如果登录失败，返回空token
    return ""


@pytest.fixture
def auth_headers(admin_token: str) -> dict:
    """认证请求头"""
    return {"Authorization": f"Bearer {admin_token}"}
