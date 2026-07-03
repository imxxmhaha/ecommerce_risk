# 电商风控系统后端

## 启动步骤

1. 创建 MySQL 数据库并执行 `01_笔记/01.数据实体详细设计/ecommerce_risk_schema.sql`。
2. 复制 `.env.example` 为 `.env`，修改数据库配置。
3. 使用 `uv` 创建虚拟环境并安装依赖：

```bash
uv sync
```

4. 启动服务：

```bash
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

5. 访问接口文档：`http://localhost:8000/docs`

## 依赖管理

后端使用 `uv` 管理 Python 环境和依赖：

```bash
uv sync          # 根据 pyproject.toml/uv.lock 安装依赖
uv run python -c "import app.main"
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

`requirements.txt` 仅作为兼容参考，日常开发以 `pyproject.toml` 和 `uv.lock` 为准。

## 登录与首个管理员

系统使用 `Authorization: Bearer <token>` 做接口鉴权，角色、权限、菜单数据由 `ecommerce_risk_schema.sql` 初始化。

默认不会创建可登录账号。首次部署时，在 `.env` 中设置：

```bash
AUTH_SECRET=change-me-to-a-random-secret
BOOTSTRAP_ADMIN_TOKEN=change-me-once
```

启动后调用 `POST /api/auth/bootstrap-admin` 创建首个管理员。该接口只在系统没有任何后台用户时可用，且必须提供正确的 `BOOTSTRAP_ADMIN_TOKEN`。

## 演示链路

1. 调用 `POST /api/risk/check` 发起风险检查。
2. 高风险或需人工审核时自动创建案件。
3. 调用案件详情接口查看评估、命中规则、特征快照和日志。
4. 调用 `POST /api/risk/cases/review` 提交审核。
5. 查看用户画像和运营看板。
