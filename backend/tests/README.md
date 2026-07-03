# 验收测试说明

## 测试覆盖范围

本测试套件覆盖电商风控系统的9项验收标准，共 **38个测试用例**：

| 编号 | 验收标准 | 测试类 | 用例数 |
|------|----------|--------|--------|
| 1 | 四类业务事件风险检查 | `TestEventTypeChecks` | 5 |
| 2 | 评分、等级、处理建议、命中规则和特征快照 | `TestScoreAndLevel` | 6 |
| 3 | 高风险结果自动创建案件 | `TestCaseAutoCreation` | 3 |
| 4 | 案件审核与审核日志 | `TestCaseReview` | 3 |
| 5 | 规则管理（增删改查 + 启停用 + 命中统计） | `TestRuleManagement` | 7 |
| 6 | 黑名单管理 | `TestBlacklistManagement` | 5 |
| 7 | 用户画像与运营看板 | `TestUserProfileAndDashboard` | 4 |
| 8 | 完整演示链路 | `TestEndToEndFlow` | 1 |
| 9 | 事件全生命周期回查 | `TestEventLifecycle` | 2 |
| - | 幂等性测试 | `TestIdempotency` | 1 |
| - | 认证测试 | `TestAuthentication` | 2 |

## 运行测试

### 前置条件

1. 安装测试依赖：
```bash
cd backend
pip install -e ".[test]"
```

2. 确保MySQL数据库已启动并配置正确（`.env` 文件）

3. 确保数据库已初始化（执行 `sql/ecommerce_risk_schema.sql` 种子数据）

4. 默认测试账号：`risk_admin / 123456`

### 运行所有验收测试

```bash
cd backend
pytest tests/test_acceptance.py -v
```

### 运行特定测试类

```bash
# 运行四类事件测试
pytest tests/test_acceptance.py::TestEventTypeChecks -v

# 运行评分等级测试
pytest tests/test_acceptance.py::TestScoreAndLevel -v

# 运行完整链路测试
pytest tests/test_acceptance.py::TestEndToEndFlow -v
```

### 运行单个测试用例

```bash
pytest tests/test_acceptance.py::TestEventTypeChecks::test_tc_1_1_order_create -v
```

## 测试用例清单

### 一、四类业务事件风险检查
- TC-1.1 订单创建事件 (order_create)
- TC-1.2 支付事件 (order_pay)
- TC-1.3 售后/退款事件 (after_sale_apply)
- TC-1.4 物流投诉事件 (logistics_complaint)

### 二、评分与等级生成
- TC-2.1 低风险 - 零分通过
- TC-2.2 中风险 - 评分在30-69区间
- TC-2.3 高风险 - 评分≥70
- TC-2.4 特征快照完整性验证

### 三、高风险自动创建案件
- TC-3.1 高风险事件自动生成案件
- TC-3.2 中风险事件也创建案件
- TC-3.3 低风险不创建案件

### 四、案件审核与审核日志
- TC-4.1 审核通过
- TC-4.2 审核拒绝
- TC-4.3 查看审核日志

### 五、规则管理
- TC-5.1 新增规则
- TC-5.2 编辑规则
- TC-5.3 停用规则
- TC-5.4 停用规则后不命中
- TC-5.5 重新启用规则
- TC-5.6 命中统计变化验证
- TC-5.7 查询规则列表

### 六、黑名单管理
- TC-6.1 新增黑名单用户
- TC-6.2 黑名单用户直接拒绝
- TC-6.3 查询黑名单列表
- TC-6.4 删除黑名单
- TC-6.5 停用后黑名单不生效

### 七、用户画像与运营看板
- TC-7.1 查询用户画像
- TC-7.2 运营看板总览数据
- TC-7.3 运营看板带日期范围
- TC-7.4 查询评估详情

### 八、完整演示链路
- TC-8.1 端到端完整链路

### 九、事件全生命周期回查
- TC-9.1 事件全链路数据一致性
- TC-9.2 多事件回查

## 注意事项

1. **数据库**：测试直接连接MySQL数据库，数据会写入真实数据库
2. **幂等性测试**：每个测试用例使用唯一的 `source_id`，避免幂等性冲突
3. **认证**：测试使用种子数据中的 `risk_admin / 123456` 账号
4. **测试数据**：测试会创建风险事件、评估、案件、规则、黑名单等数据

## 测试结果示例

```
============================= 38 passed in 3.46s ==============================
```
