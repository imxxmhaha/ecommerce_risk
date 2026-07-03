# 电商风控系统代码

本目录包含电商风控系统的前后端代码：

- `backend`：FastAPI + SQLAlchemy + MySQL
- `frontend`：Vue 3 + TypeScript + Vite + Element Plus + ECharts

## 数据库初始化

执行笔记目录中的 SQL：

```bash
mysql -uroot -p < ../01_笔记/01.数据实体详细设计/ecommerce_risk_schema.sql
```

## 后端启动

```bash
cd backend
copy .env.example .env
uv sync
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

接口文档：`http://localhost:8000/docs`

## 首个管理员

系统不会内置默认账号。首次启动前，在 `.env` 中设置 `BOOTSTRAP_ADMIN_TOKEN`，启动后调用：

```bash
curl -X POST http://localhost:8000/api/auth/bootstrap-admin ^
  -H "Content-Type: application/json" ^
  -d "{\"bootstrap_token\":\"change-me-once\",\"username\":\"admin\",\"password\":\"你的强密码\",\"real_name\":\"风控管理员\"}"
```

创建完成后使用该账号登录前端，再在“用户权限”页面维护审核员、数据查看人等账号。

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
