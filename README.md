# 电商风控系统代码

本目录包含电商风控系统的前后端代码：

- `backend`：FastAPI + SQLAlchemy + MySQL
- `frontend`：Vue 3 + TypeScript + Vite + Element Plus + ECharts

## 数据库初始化

本地手动部署时执行：

```bash
mysql -uroot -p < backend/sql/ecommerce_risk_schema.sql
mysql -uroot -p < backend/sql/ecommerce_risk_seed_data.sql
```

Docker Compose 部署会自动初始化这两个脚本。

## Docker Compose 部署

```bash
docker compose up -d --build
```

访问地址：

- 前端：`http://localhost:8080`
- 后端接口文档：`http://localhost:8000/docs`
- MySQL：`localhost:3306`

MySQL 初始化脚本：

- `backend/sql/ecommerce_risk_schema.sql`
- `backend/sql/ecommerce_risk_seed_data.sql`

如果需要重新初始化数据库，先删除数据卷：

```bash
docker compose down -v
docker compose up -d --build
```

## 后端启动

```bash
cd backend
copy .env.example .env
uv sync
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

接口文档：`http://localhost:8000/docs`

## 默认账号

SQL 初始化脚本会创建三个默认后台账号：

```text
risk_admin / 123456
risk_auditor / 123456
data_viewer / 123456
```

登录后可在“用户权限”页面维护用户、角色和权限。生产环境请及时修改默认密码。

## 前端启动

```bash
cd frontend
npm install
npm run dev
```

访问：`http://localhost:5173`

## 演示链路

1. 登录后台。
2. 在风险检查页提交默认事件。
3. 查看评分、风险等级、命中规则和特征快照。
4. 高风险结果自动生成案件。
5. 在案件详情页提交审核。
6. 在用户画像和运营看板查看聚合结果。

## AI 辅助规则

当前实现为 mock LLM 模式，可在无外部 API Key 的情况下演示自然语言规则生成、规则解释和规则校验。
