# 电商风控系统

基于 **FastAPI + Vue 3** 的电商风控系统，支持多业务事件风险评估、规则引擎、案件审核、用户画像和运营看板等功能。

## 技术栈

### 后端

| 技术 | 说明 |
|------|------|
| **FastAPI** | 高性能异步 Web 框架 |
| **SQLAlchemy** | ORM 框架 |
| **MySQL 8.0** | 关系型数据库 |
| **LangChain** | LLM 应用开发框架 |
| **通义千问** | AI 大模型（规则生成） |
| **Pydantic** | 数据校验和序列化 |
| **JWT** | 用户认证 |
| **RBAC** | 基于角色的权限控制 |

### 前端

| 技术 | 说明 |
|------|------|
| **Vue 3** | 渐进式 JavaScript 框架 |
| **TypeScript** | 类型安全的 JavaScript 超集 |
| **Vite** | 前端构建工具 |
| **Element Plus** | UI 组件库 |
| **ECharts** | 数据可视化图表 |
| **Pinia** | 状态管理 |
| **Vue Router** | 路由管理 |

### 部署

| 技术 | 说明 |
|------|------|
| **Docker** | 容器化部署 |
| **Docker Compose** | 多容器编排 |
| **Nginx** | 前端静态资源服务 |

### 测试

| 技术 | 说明 |
|------|------|
| **pytest** | Python 单元测试框架 |
| **httpx** | HTTP 测试客户端 |

## 项目结构

```
ecommerce_risk/
├── backend/                    # 后端服务
│   ├── app/
│   │   ├── api/               # API 路由层
│   │   │   ├── risk_check_api.py    # 风险检查
│   │   │   ├── rule_api.py          # 规则管理
│   │   │   ├── case_api.py          # 案件管理
│   │   │   ├── blacklist_api.py     # 黑名单管理
│   │   │   ├── ai_rule_api.py       # AI规则辅助
│   │   │   ├── dashboard_api.py     # 运营看板
│   │   │   ├── profile_api.py       # 用户画像
│   │   │   └── system_api.py        # 系统管理
│   │   ├── core/              # 核心配置
│   │   │   ├── config.py            # 环境配置
│   │   │   ├── database.py          # 数据库连接
│   │   │   ├── security.py          # JWT认证
│   │   │   └── errors.py            # 错误码定义
│   │   ├── models/            # 数据模型
│   │   ├── schemas/           # 请求/响应模型
│   │   ├── services/          # 业务逻辑层
│   │   │   ├── risk_check_service.py  # 风险检查核心
│   │   │   ├── rule_engine.py         # 规则引擎
│   │   │   ├── decision_service.py    # 决策服务
│   │   │   ├── feature_service.py     # 特征工程
│   │   │   └── ai_rule_service.py     # AI规则生成
│   │   └── utils/             # 工具函数
│   ├── sql/                   # 数据库脚本
│   ├── tests/                 # 测试用例
│   └── .env                   # 环境变量
├── frontend/                  # 前端应用
│   ├── src/
│   │   ├── api/               # API 接口
│   │   ├── components/        # 公共组件
│   │   ├── views/             # 页面视图
│   │   ├── router/            # 路由配置
│   │   ├── stores/            # 状态管理
│   │   └── types/             # TypeScript 类型
│   └── package.json
├── docker-compose.yaml        # Docker编排
├── deploy.sh                  # 部署脚本
└── README.md
```

## 核心功能

### 1. 风险检查
- 支持4类业务事件：订单创建、订单支付、售后申请、物流投诉
- 实时计算25维特征指标
- 规则引擎动态评估风险分值
- 自动生成风险等级（低/中/高）和处理建议（通过/人工审核/拒绝）

### 2. 规则引擎
- 支持 `and`/`or` 组合条件
- 支持 `>`/`<`/`=`/`in` 操作符
- 规则启停用管理
- 规则命中统计

### 3. AI规则辅助（LangChain + 通义千问）
- 自然语言生成风控规则
- 规则条件智能解释
- 规则合理性分析

### 4. 案件管理
- 高风险自动创建案件
- 人工审核（通过/拒绝）
- 审核日志追踪

### 5. 黑名单管理
- 支持6类黑名单：用户、订单、手机号、设备、IP、地址
- 黑名单命中自动拒绝

### 6. 用户画像
- 用户风险等级评估
- 历史事件统计
- 关联案件查询

### 7. 运营看板
- 风险检查总览
- 风险趋势图表
- 规则命中排行

## 快速开始

### Docker Compose 部署（推荐）

```bash
# 克隆项目
git clone <repository-url>
cd ecommerce_risk

# 启动服务
docker compose up -d --build

# 查看日志
docker compose logs -f
```

访问地址：
- 前端：http://localhost:8080
- 后端接口：http://localhost:9400
- 接口文档：http://localhost:9400/docs
- 数据库：localhost:13307

### 本地开发

#### 后端

```bash
cd backend

# 创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
# 或使用 uv
uv sync

# 配置环境变量
cp .env.example .env
# 编辑 .env 填入数据库配置

# 初始化数据库
mysql -uroot -p < sql/ecommerce_risk_schema.sql
mysql -uroot -p < sql/ecommerce_risk_seed_data.sql

# 启动服务
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### 前端

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

访问：http://localhost:5173

## 默认账号

| 账号 | 密码 | 角色 |
|------|------|------|
| risk_admin | 123456 | 风险管理员（全部权限） |
| risk_auditor | 123456 | 审核员（案件审核） |
| data_viewer | 123456 | 数据查看者（只读） |

> 生产环境请及时修改默认密码

## 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| DB_HOST | 数据库地址 | localhost |
| DB_PORT | 数据库端口 | 3306 |
| DB_USER | 数据库用户名 | root |
| DB_PASSWORD | 数据库密码 | root |
| DB_NAME | 数据库名称 | ecommerce_risk_control |
| AI_MOCK | AI模式（true=模拟） | true |
| LLM_MODEL | 大模型名称 | qwen-plus |
| LLM_BASE_URL | 大模型API地址 | https://dashscope.aliyuncs.com/compatible-mode/v1 |
| LLM_API_KEY | 大模型API密钥 | - |
| AUTH_SECRET | JWT密钥 | - |
| ACCESS_TOKEN_EXPIRE_MINUTES | Token过期时间 | 480 |

## 运行测试

```bash
cd backend

# 运行所有验收测试
pytest tests/test_acceptance.py -v

# 运行特定测试类
pytest tests/test_acceptance.py::TestRuleManagement -v
```

测试覆盖9项验收标准，共38个测试用例。

## 部署脚本

```bash
# 部署（跳过mysql重建）
./deploy.sh

# 部署并清理mysql数据卷
./deploy.sh -v
```

## 演示链路

1. **登录系统** → 使用 risk_admin/123456 登录
2. **风险检查** → 提交订单创建事件
3. **查看结果** → 评分、等级、命中规则、特征快照
4. **案件审核** → 高风险自动创建案件，人工审核
5. **规则管理** → 新增/编辑/启停用规则
6. **黑名单** → 添加黑名单用户，验证拦截效果
7. **用户画像** → 查看用户风险档案
8. **运营看板** → 查看风险统计和趋势

## 许可证

MIT License
