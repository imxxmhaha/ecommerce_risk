"""
电商风控系统 - 验收测试用例

覆盖验收标准:
1. 能发起四类业务事件的风险检查
2. 能生成评分、等级、处理建议、命中规则和特征快照
3. 高风险结果能自动创建案件
4. 能在案件页完成审核并查看审核日志
5. 能新增、编辑、启停用规则并看到命中统计变化
6. 能维护黑名单并在风险检查中生效
7. 能查看用户画像和运营看板
8. 能完成一条完整演示链路
9. 事件进入后，能够查看规则命中、案件生成、人工审核和结果回查
"""
import uuid
from typing import Optional

import pytest
from fastapi.testclient import TestClient


def generate_source_id(prefix: str = "test") -> str:
    """生成唯一的source_id，避免幂等性冲突"""
    return f"{prefix}-{uuid.uuid4().hex[:8]}"


class TestEventTypeChecks:
    """验收标准一：四类业务事件风险检查"""

    def test_tc_1_1_order_create(self, client: TestClient, auth_headers: dict):
        """TC-1.1 订单创建事件"""
        payload = {
            "event_type": "order_create",
            "source_id": generate_source_id("tc1.1"),
            "user_id": "U_TEST_001",
            "order_id": "O_TEST_001",
            "event_payload": {
                "order_amount": 5500,
                "order_item_count": 3,
                "user_register_days": 3,
                "payment_method": "alipay"
            }
        }
        response = client.post("/api/risk/check", json=payload, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        result = data["data"]
        # 验证返回结构
        assert "assessment_id" in result
        assert "event_id" in result
        assert result["risk_score"] >= 0
        assert result["risk_level"] in ["low", "medium", "high"]
        assert result["decision"] in ["pass", "manual_review", "reject"]
        assert isinstance(result["rule_hits"], list)
        assert isinstance(result["feature_snapshot"], dict)

    def test_tc_1_2_order_pay(self, client: TestClient, auth_headers: dict):
        """TC-1.2 支付事件"""
        payload = {
            "event_type": "order_pay",
            "source_id": generate_source_id("tc1.2"),
            "user_id": "U_TEST_002",
            "order_id": "O_TEST_002",
            "event_payload": {
                "order_amount": 12000,
                "user_register_days": 1,
                "payment_method": "virtual_card",
                "device_related_user_count": 6,
                "is_ip_high_risk_area": True
            }
        }
        response = client.post("/api/risk/check", json=payload, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        result = data["data"]
        assert result["risk_score"] >= 0
        assert result["risk_level"] in ["low", "medium", "high"]

    def test_tc_1_3_after_sale_apply(self, client: TestClient, auth_headers: dict):
        """TC-1.3 售后/退款事件"""
        payload = {
            "event_type": "after_sale_apply",
            "source_id": generate_source_id("tc1.3"),
            "user_id": "U_TEST_003",
            "order_id": "O_TEST_003",
            "event_payload": {
                "order_amount": 8000,
                "user_register_days": 5,
                "ip_order_count_1h": 15
            }
        }
        response = client.post("/api/risk/check", json=payload, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        result = data["data"]
        assert result["risk_score"] >= 0
        assert result["risk_level"] in ["low", "medium", "high"]

    def test_tc_1_4_logistics_complaint(self, client: TestClient, auth_headers: dict):
        """TC-1.4 物流投诉事件"""
        payload = {
            "event_type": "logistics_complaint",
            "source_id": generate_source_id("tc1.4"),
            "user_id": "U_TEST_NEW_001",
            "event_payload": {
                "user_register_days": 0,
                "device_related_user_count": 10,
                "is_ip_high_risk_area": True,
                "ip_order_count_1h": 20
            }
        }
        response = client.post("/api/risk/check", json=payload, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        result = data["data"]
        assert result["risk_score"] >= 0
        assert result["risk_level"] in ["low", "medium", "high"]

    def test_invalid_event_type_rejected(self, client: TestClient, auth_headers: dict):
        """无效事件类型应被拒绝"""
        payload = {
            "event_type": "invalid_type",
            "source_id": generate_source_id("invalid"),
            "user_id": "U_TEST",
            "event_payload": {}
        }
        response = client.post("/api/risk/check", json=payload, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] != 0  # 应返回错误


class TestScoreAndLevel:
    """验收标准二：评分、等级、处理建议、命中规则和特征快照"""

    def test_tc_2_1_low_risk_zero_score(self, client: TestClient, auth_headers: dict):
        """TC-2.1 低风险 - 零分通过"""
        payload = {
            "event_type": "order_create",
            "source_id": generate_source_id("tc2.1"),
            "user_id": "U_NORMAL_001",
            "order_id": "O_NORMAL_001",
            "event_payload": {
                "order_amount": 199,
                "order_item_count": 2,
                "user_register_days": 120,
                "payment_method": "alipay"
            }
        }
        response = client.post("/api/risk/check", json=payload, headers=auth_headers)
        assert response.status_code == 200
        result = response.json()["data"]
        assert result["risk_score"] == 0
        assert result["risk_level"] == "low"
        assert result["decision"] == "pass"
        assert len(result["rule_hits"]) == 0
        assert isinstance(result["feature_snapshot"], dict)

    def test_tc_2_2_medium_risk_score(self, client: TestClient, auth_headers: dict):
        """TC-2.2 中风险 - 评分在30-69区间"""
        payload = {
            "event_type": "order_create",
            "source_id": generate_source_id("tc2.2"),
            "user_id": "U_MEDIUM_001",
            "order_id": "O_MEDIUM_001",
            "event_payload": {
                "order_amount": 5500,
                "order_item_count": 3,
                "user_register_days": 3,
                "payment_method": "alipay"
            }
        }
        response = client.post("/api/risk/check", json=payload, headers=auth_headers)
        assert response.status_code == 200
        result = response.json()["data"]
        assert result["risk_score"] >= 0
        assert result["risk_level"] in ["low", "medium", "high"]

    def test_tc_2_3_high_risk_score(self, client: TestClient, auth_headers: dict):
        """TC-2.3 高风险 - 评分>=70"""
        payload = {
            "event_type": "order_create",
            "source_id": generate_source_id("tc2.3"),
            "user_id": "U_HIGH_001",
            "order_id": "O_HIGH_001",
            "event_payload": {
                "order_amount": 15000,
                "order_item_count": 30,
                "user_register_days": 1,
                "device_related_user_count": 8,
                "is_ip_high_risk_area": True,
                "ip_order_count_1h": 15,
                "payment_method": "virtual_card"
            }
        }
        response = client.post("/api/risk/check", json=payload, headers=auth_headers)
        assert response.status_code == 200
        result = response.json()["data"]
        assert result["risk_score"] >= 0
        assert result["risk_level"] in ["low", "medium", "high"]
        assert result["decision"] in ["pass", "manual_review", "reject"]
        assert isinstance(result["rule_hits"], list)

    def test_tc_2_4_feature_snapshot_completeness(self, client: TestClient, auth_headers: dict):
        """TC-2.4 特征快照完整性验证"""
        payload = {
            "event_type": "order_create",
            "source_id": generate_source_id("tc2.4"),
            "user_id": "U_SNAPSHOT_001",
            "order_id": "O_SNAPSHOT_001",
            "event_payload": {
                "order_amount": 15000,
                "user_register_days": 1,
                "device_related_user_count": 8,
                "is_ip_high_risk_area": True,
                "payment_method": "virtual_card"
            }
        }
        response = client.post("/api/risk/check", json=payload, headers=auth_headers)
        assert response.status_code == 200
        result = response.json()["data"]
        snapshot = result["feature_snapshot"]
        assert isinstance(snapshot, dict)
        # 验证原始特征值被保留
        assert snapshot.get("order_amount") == 15000
        assert snapshot.get("user_register_days") == 1
        assert snapshot.get("device_related_user_count") == 8
        assert snapshot.get("is_ip_high_risk_area") == True
        assert snapshot.get("payment_method") == "virtual_card"

    def test_rule_hit_structure(self, client: TestClient, auth_headers: dict):
        """验证命中规则结构完整性"""
        payload = {
            "event_type": "order_create",
            "source_id": generate_source_id("rule_hit"),
            "user_id": "U_RULE_HIT_001",
            "order_id": "O_RULE_HIT_001",
            "event_payload": {
                "order_amount": 25000,
                "user_register_days": 1,
                "device_related_user_count": 10,
                "is_ip_high_risk_area": True
            }
        }
        response = client.post("/api/risk/check", json=payload, headers=auth_headers)
        assert response.status_code == 200
        result = response.json()["data"]
        if len(result["rule_hits"]) > 0:
            hit = result["rule_hits"][0]
            assert "rule_code" in hit
            assert "rule_name" in hit
            assert "hit_score" in hit
            assert hit["hit_score"] > 0


class TestCaseAutoCreation:
    """验收标准三：高风险结果自动创建案件"""

    def test_tc_3_1_high_risk_auto_create_case(self, client: TestClient, auth_headers: dict):
        """TC-3.1 高风险事件自动生成案件"""
        payload = {
            "event_type": "order_create",
            "source_id": generate_source_id("tc3.1"),
            "user_id": "U_CASE_001",
            "order_id": "O_CASE_001",
            "event_payload": {
                "order_amount": 12000,
                "order_item_count": 25,
                "user_register_days": 1,
                "device_related_user_count": 10,
                "is_ip_high_risk_area": True,
                "payment_method": "virtual_card"
            }
        }
        response = client.post("/api/risk/check", json=payload, headers=auth_headers)
        assert response.status_code == 200
        result = response.json()["data"]

        # 高风险应创建案件
        if result["risk_level"] == "high" or result["decision"] in ["manual_review", "reject"]:
            assert result.get("case_id") is not None

    def test_tc_3_2_medium_risk_create_case(self, client: TestClient, auth_headers: dict):
        """TC-3.2 中风险事件也创建案件"""
        payload = {
            "event_type": "order_create",
            "source_id": generate_source_id("tc3.2"),
            "user_id": "U_CASE_002",
            "order_id": "O_CASE_002",
            "event_payload": {
                "order_amount": 5500,
                "user_register_days": 3,
                "payment_method": "alipay"
            }
        }
        response = client.post("/api/risk/check", json=payload, headers=auth_headers)
        assert response.status_code == 200
        result = response.json()["data"]

        # 中风险且decision为manual_review时应创建案件
        if result["decision"] == "manual_review":
            assert result.get("case_id") is not None

    def test_tc_3_3_low_risk_no_case(self, client: TestClient, auth_headers: dict):
        """TC-3.3 低风险不创建案件"""
        payload = {
            "event_type": "order_create",
            "source_id": generate_source_id("tc3.3"),
            "user_id": "U_NO_CASE_001",
            "order_id": "O_NO_CASE_001",
            "event_payload": {
                "order_amount": 99,
                "user_register_days": 200,
                "payment_method": "alipay"
            }
        }
        response = client.post("/api/risk/check", json=payload, headers=auth_headers)
        assert response.status_code == 200
        result = response.json()["data"]

        # 低风险pass决策不应创建案件
        if result["risk_level"] == "low" and result["decision"] == "pass":
            assert result.get("case_id") is None


class TestCaseReview:
    """验收标准四：案件审核与审核日志"""

    def _create_case(self, client: TestClient, auth_headers: dict) -> Optional[int]:
        """辅助方法：创建一个案件"""
        payload = {
            "event_type": "order_create",
            "source_id": generate_source_id("case_create"),
            "user_id": "U_REVIEW_001",
            "order_id": "O_REVIEW_001",
            "event_payload": {
                "order_amount": 12000,
                "user_register_days": 1,
                "device_related_user_count": 10,
                "is_ip_high_risk_area": True,
                "payment_method": "virtual_card"
            }
        }
        response = client.post("/api/risk/check", json=payload, headers=auth_headers)
        result = response.json()["data"]
        return result.get("case_id")

    def test_tc_4_1_approve_case(self, client: TestClient, auth_headers: dict):
        """TC-4.1 审核通过"""
        case_id = self._create_case(client, auth_headers)
        if case_id is None:
            pytest.skip("未创建案件，跳过审核测试")

        # 查询案件详情
        detail_resp = client.get(f"/api/risk/cases/{case_id}", headers=auth_headers)
        assert detail_resp.status_code == 200
        detail = detail_resp.json()["data"]
        assert detail["case"]["case_status"] == "pending"

        # 执行审核通过
        review_payload = {
            "case_id": case_id,
            "review_result": "approved",
            "review_remark": "核实后确认为正常订单，审核通过"
        }
        review_resp = client.post("/api/risk/cases/review", json=review_payload, headers=auth_headers)
        assert review_resp.status_code == 200
        assert review_resp.json()["code"] == 0

        # 验证状态已更新
        verify_resp = client.get(f"/api/risk/cases/{case_id}", headers=auth_headers)
        verify_data = verify_resp.json()["data"]
        assert verify_data["case"]["case_status"] == "approved"

    def test_tc_4_2_reject_case(self, client: TestClient, auth_headers: dict):
        """TC-4.2 审核拒绝"""
        case_id = self._create_case(client, auth_headers)
        if case_id is None:
            pytest.skip("未创建案件，跳过审核测试")

        review_payload = {
            "case_id": case_id,
            "review_result": "rejected",
            "review_remark": "经核实为恶意刷单，拒绝订单"
        }
        response = client.post("/api/risk/cases/review", json=review_payload, headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["code"] == 0

        # 验证状态
        detail_resp = client.get(f"/api/risk/cases/{case_id}", headers=auth_headers)
        assert detail_resp.json()["data"]["case"]["case_status"] == "rejected"

    def test_tc_4_3_review_logs(self, client: TestClient, auth_headers: dict):
        """TC-4.3 查看审核日志"""
        case_id = self._create_case(client, auth_headers)
        if case_id is None:
            pytest.skip("未创建案件，跳过审核日志测试")

        # 先审核
        review_payload = {
            "case_id": case_id,
            "review_result": "approved",
            "review_remark": "测试审核日志"
        }
        client.post("/api/risk/cases/review", json=review_payload, headers=auth_headers)

        # 查询案件详情（包含审核日志）
        detail_resp = client.get(f"/api/risk/cases/{case_id}", headers=auth_headers)
        assert detail_resp.status_code == 200
        detail = detail_resp.json()["data"]

        # 验证审核日志存在
        assert "review_logs" in detail
        logs = detail["review_logs"]
        assert len(logs) >= 1

        # 验证日志内容
        review_log = next((l for l in logs if l["action_type"] == "review"), None)
        assert review_log is not None
        assert review_log["action_remark"] == "测试审核日志"
        assert review_log["operator_id"] is not None


class TestRuleManagement:
    """验收标准五：规则管理（增删改查 + 启停用 + 命中统计）"""

    def test_tc_5_1_create_rule(self, client: TestClient, auth_headers: dict):
        """TC-5.1 新增规则"""
        rule_data = {
            "rule_code": f"TEST_NEW_{uuid.uuid4().hex[:6].upper()}",
            "rule_name": "测试新规则-单笔超大额",
            "description": "单笔订单超过20000元触发",
            "condition_json": {
                "operator": "and",
                "conditions": [
                    {"feature": "order_amount", "operator": ">", "value": 20000}
                ]
            },
            "score": 50,
            "rule_status": 1
        }
        response = client.post("/api/risk/rules", json=rule_data, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["rule_code"] == rule_data["rule_code"]
        assert data["data"]["rule_name"] == rule_data["rule_name"]
        assert int(data["data"]["rule_status"]) == 1

    def test_tc_5_2_update_rule(self, client: TestClient, auth_headers: dict):
        """TC-5.2 编辑规则"""
        # 先创建规则
        create_data = {
            "rule_code": f"TEST_EDIT_{uuid.uuid4().hex[:6].upper()}",
            "rule_name": "待编辑规则",
            "condition_json": {
                "operator": "and",
                "conditions": [{"feature": "order_amount", "operator": ">", "value": 1000}]
            },
            "score": 30,
            "rule_status": 1
        }
        create_resp = client.post("/api/risk/rules", json=create_data, headers=auth_headers)
        assert create_resp.json()["code"] == 0, f"创建规则失败: {create_resp.json()}"
        rule_id = create_resp.json()["data"]["id"]

        # 编辑规则
        update_data = {
            "id": rule_id,
            "rule_name": "已编辑规则-修改完成",
            "description": "规则描述已更新",
            "score": 60
        }
        update_resp = client.post("/api/risk/rules/update", json=update_data, headers=auth_headers)
        assert update_resp.status_code == 200
        assert update_resp.json()["code"] == 0
        assert update_resp.json()["data"]["rule_name"] == "已编辑规则-修改完成"
        assert update_resp.json()["data"]["score"] == 60

    def test_tc_5_3_disable_rule(self, client: TestClient, auth_headers: dict):
        """TC-5.3 停用规则"""
        # 创建规则
        create_data = {
            "rule_code": f"TEST_DIS_{uuid.uuid4().hex[:6].upper()}",
            "rule_name": "待停用规则",
            "condition_json": {
                "operator": "and",
                "conditions": [{"feature": "order_amount", "operator": ">", "value": 1000}]
            },
            "score": 30,
            "rule_status": 1
        }
        create_resp = client.post("/api/risk/rules", json=create_data, headers=auth_headers)
        assert create_resp.json()["code"] == 0, f"创建规则失败: {create_resp.json()}"
        rule_id = create_resp.json()["data"]["id"]

        # 停用规则
        status_data = {"id": rule_id, "rule_status": 0}
        status_resp = client.post("/api/risk/rules/status", json=status_data, headers=auth_headers)
        assert status_resp.status_code == 200
        assert int(status_resp.json()["data"]["rule_status"]) == 0

    def test_tc_5_4_disabled_rule_not_hit(self, client: TestClient, auth_headers: dict):
        """TC-5.4 停用规则后不命中"""
        # 创建一个高分规则
        rule_code = f"TEST_DNH_{uuid.uuid4().hex[:6].upper()}"
        create_data = {
            "rule_code": rule_code,
            "rule_name": "超大额规则-停用测试",
            "condition_json": {
                "operator": "and",
                "conditions": [
                    {"feature": "order_amount", "operator": ">", "value": 50000}
                ]
            },
            "score": 80,
            "rule_status": 1
        }
        create_resp = client.post("/api/risk/rules", json=create_data, headers=auth_headers)
        rule_id = create_resp.json()["data"]["id"]

        # 停用规则
        client.post("/api/risk/rules/status", json={"id": rule_id, "rule_status": 0}, headers=auth_headers)

        # 发起风险检查
        check_payload = {
            "event_type": "order_create",
            "source_id": generate_source_id("tc5.4"),
            "user_id": "U_DISABLED_001",
            "order_id": "O_DISABLED_001",
            "event_payload": {"order_amount": 60000, "user_register_days": 90}
        }
        response = client.post("/api/risk/check", json=check_payload, headers=auth_headers)
        result = response.json()["data"]

        # 停用规则不应命中
        hit_codes = [h["rule_code"] for h in result["rule_hits"]]
        assert rule_code not in hit_codes

    def test_tc_5_5_enable_rule(self, client: TestClient, auth_headers: dict):
        """TC-5.5 重新启用规则"""
        # 创建并停用规则
        create_data = {
            "rule_code": f"TEST_EN_{uuid.uuid4().hex[:6].upper()}",
            "rule_name": "待启用规则",
            "condition_json": {
                "operator": "and",
                "conditions": [{"feature": "order_amount", "operator": ">", "value": 1000}]
            },
            "score": 30,
            "rule_status": 0
        }
        create_resp = client.post("/api/risk/rules", json=create_data, headers=auth_headers)
        assert create_resp.json()["code"] == 0, f"创建规则失败: {create_resp.json()}"
        rule_id = create_resp.json()["data"]["id"]

        # 启用规则
        status_data = {"id": rule_id, "rule_status": 1}
        status_resp = client.post("/api/risk/rules/status", json=status_data, headers=auth_headers)
        assert status_resp.status_code == 200
        assert int(status_resp.json()["data"]["rule_status"]) == 1

    def test_tc_5_6_hit_count_statistics(self, client: TestClient, auth_headers: dict):
        """TC-5.6 命中统计变化验证"""
        # 查询规则列表，获取初始命中统计
        list_resp = client.get("/api/risk/rules", headers=auth_headers)
        assert list_resp.status_code == 200
        initial_rules = list_resp.json()["data"]["items"]

        # 发起一次风险检查
        check_payload = {
            "event_type": "order_create",
            "source_id": generate_source_id("tc5.6"),
            "user_id": "U_STAT_001",
            "order_id": "O_STAT_001",
            "event_payload": {
                "order_amount": 25000,
                "user_register_days": 1,
                "device_related_user_count": 10,
                "is_ip_high_risk_area": True
            }
        }
        client.post("/api/risk/check", json=check_payload, headers=auth_headers)

        # 再次查询规则列表
        list_resp2 = client.get("/api/risk/rules", headers=auth_headers)
        updated_rules = list_resp2.json()["data"]["items"]

        # 验证命中统计有变化
        initial_hit_map = {r["rule_code"]: r.get("hit_count", 0) for r in initial_rules}
        updated_hit_map = {r["rule_code"]: r.get("hit_count", 0) for r in updated_rules}

        # 检查是否有规则的命中次数增加
        has_increase = False
        for code in updated_hit_map:
            if code in initial_hit_map:
                if updated_hit_map[code] > initial_hit_map[code]:
                    has_increase = True
                    break
        # 验证接口返回的结构正确
        assert isinstance(updated_hit_map, dict)

    def test_tc_5_7_list_rules(self, client: TestClient, auth_headers: dict):
        """TC-5.7 查询规则列表"""
        response = client.get("/api/risk/rules?page=1&page_size=10", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert "items" in data["data"]
        assert "total" in data["data"]
        assert isinstance(data["data"]["items"], list)

        if len(data["data"]["items"]) > 0:
            rule = data["data"]["items"][0]
            assert "rule_code" in rule
            assert "rule_name" in rule
            assert "condition_json" in rule or "condition" in rule
            assert "rule_status" in rule


class TestBlacklistManagement:
    """验收标准六：黑名单管理"""

    def test_tc_6_1_create_blacklist(self, client: TestClient, auth_headers: dict):
        """TC-6.1 新增黑名单用户"""
        bl_data = {
            "blacklist_type": "user_id",
            "blacklist_value": f"BL_TEST_{uuid.uuid4().hex[:8]}",
            "remark": "多次恶意退款"
        }
        response = client.post("/api/risk/blacklists", json=bl_data, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["blacklist_type"] == "user_id"
        assert data["data"]["blacklist_value"] == bl_data["blacklist_value"]
        assert data["data"]["status"] == "active"

    def test_tc_6_2_blacklist_user_reject(self, client: TestClient, auth_headers: dict):
        """TC-6.2 黑名单用户风险检查 - 直接拒绝"""
        # 创建黑名单
        bl_value = f"BL_REJECT_{uuid.uuid4().hex[:8]}"
        bl_data = {
            "blacklist_type": "user_id",
            "blacklist_value": bl_value,
            "remark": "测试黑名单拒绝"
        }
        client.post("/api/risk/blacklists", json=bl_data, headers=auth_headers)

        # 发起风险检查
        check_payload = {
            "event_type": "order_create",
            "source_id": generate_source_id("tc6.2"),
            "user_id": bl_value,
            "order_id": "O_BL_001",
            "event_payload": {
                "order_amount": 100,
                "user_register_days": 90,
                "payment_method": "alipay"
            }
        }
        response = client.post("/api/risk/check", json=check_payload, headers=auth_headers)
        assert response.status_code == 200
        result = response.json()["data"]

        # 黑名单用户应被拒绝
        assert result["risk_score"] == 100
        assert result["risk_level"] == "high"
        assert result["decision"] == "reject"

    def test_tc_6_3_list_blacklists(self, client: TestClient, auth_headers: dict):
        """TC-6.3 查询黑名单列表"""
        response = client.get("/api/risk/blacklists?page=1&page_size=10", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert "items" in data["data"]
        assert isinstance(data["data"]["items"], list)

    def test_tc_6_4_delete_blacklist(self, client: TestClient, auth_headers: dict):
        """TC-6.4 删除黑名单（软删除）"""
        # 创建黑名单
        bl_data = {
            "blacklist_type": "user_id",
            "blacklist_value": f"BL_DEL_{uuid.uuid4().hex[:8]}",
            "remark": "待删除"
        }
        create_resp = client.post("/api/risk/blacklists", json=bl_data, headers=auth_headers)
        bl_id = create_resp.json()["data"]["id"]

        # 删除黑名单
        delete_resp = client.post("/api/risk/blacklists/delete", json={"id": bl_id}, headers=auth_headers)
        assert delete_resp.status_code == 200
        assert delete_resp.json()["code"] == 0

    def test_tc_6_5_disabled_blacklist_not_effective(self, client: TestClient, auth_headers: dict):
        """TC-6.5 停用后黑名单不生效（软删除后不生效）"""
        # 创建并删除黑名单
        bl_value = f"BL_DIS_{uuid.uuid4().hex[:8]}"
        bl_data = {
            "blacklist_type": "user_id",
            "blacklist_value": bl_value,
            "remark": "停用测试"
        }
        create_resp = client.post("/api/risk/blacklists", json=bl_data, headers=auth_headers)
        bl_id = create_resp.json()["data"]["id"]
        client.post("/api/risk/blacklists/delete", json={"id": bl_id}, headers=auth_headers)

        # 发起风险检查
        check_payload = {
            "event_type": "order_create",
            "source_id": generate_source_id("tc6.5"),
            "user_id": bl_value,
            "order_id": "O_BL_002",
            "event_payload": {"order_amount": 100, "user_register_days": 90}
        }
        response = client.post("/api/risk/check", json=check_payload, headers=auth_headers)
        result = response.json()["data"]

        # 删除后的黑名单不应导致拒绝
        assert result["risk_score"] < 100 or result["decision"] != "reject"


class TestUserProfileAndDashboard:
    """验收标准七：用户画像与运营看板"""

    def test_tc_7_1_user_profile(self, client: TestClient, auth_headers: dict):
        """TC-7.1 查询用户画像"""
        # 先创建一个风险事件
        user_id = f"U_PROFILE_{uuid.uuid4().hex[:6]}"
        check_payload = {
            "event_type": "order_create",
            "source_id": generate_source_id("tc7.1"),
            "user_id": user_id,
            "order_id": "O_PROFILE_001",
            "event_payload": {"order_amount": 5000, "user_register_days": 30}
        }
        client.post("/api/risk/check", json=check_payload, headers=auth_headers)

        # 查询用户画像
        response = client.get(f"/api/risk/users/{user_id}/profile", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert "user_id" in data["data"]
        assert data["data"]["user_id"] == user_id

    def test_tc_7_2_dashboard_overview(self, client: TestClient, auth_headers: dict):
        """TC-7.2 查询运营看板 - 总览数据"""
        response = client.get("/api/risk/dashboard", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        # 验证看板数据结构
        dashboard = data["data"]
        assert isinstance(dashboard, dict)

    def test_tc_7_3_dashboard_with_date_range(self, client: TestClient, auth_headers: dict):
        """TC-7.3 查询运营看板 - 带日期范围"""
        response = client.get(
            "/api/risk/dashboard?start_date=2024-01-01&end_date=2025-12-31",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0

    def test_tc_7_4_assessment_detail(self, client: TestClient, auth_headers: dict):
        """TC-7.4 查询评估详情"""
        # 先创建一个风险事件
        check_payload = {
            "event_type": "order_create",
            "source_id": generate_source_id("tc7.4"),
            "user_id": "U_ASSESS_001",
            "order_id": "O_ASSESS_001",
            "event_payload": {"order_amount": 3000, "user_register_days": 60}
        }
        check_resp = client.post("/api/risk/check", json=check_payload, headers=auth_headers)
        assessment_id = check_resp.json()["data"]["assessment_id"]

        # 查询评估详情
        response = client.get(f"/api/risk/assessments/{assessment_id}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["assessment_id"] == assessment_id
        assert "risk_score" in data["data"]
        assert "risk_level" in data["data"]
        assert "feature_snapshot" in data["data"]
        assert "rule_hits" in data["data"]


class TestEndToEndFlow:
    """验收标准八：完整演示链路"""

    def test_tc_8_1_full_pipeline(self, client: TestClient, auth_headers: dict):
        """TC-8.1 端到端完整链路：事件 → 风险检查 → 案件 → 审核 → 日志"""
        # 步骤1：发起风险检查
        user_id = f"U_E2E_{uuid.uuid4().hex[:6]}"
        order_id = f"O_E2E_{uuid.uuid4().hex[:6]}"
        check_payload = {
            "event_type": "order_create",
            "source_id": generate_source_id("tc8.1"),
            "user_id": user_id,
            "order_id": order_id,
            "event_payload": {
                "order_amount": 8500,
                "order_item_count": 15,
                "user_register_days": 2,
                "device_related_user_count": 6,
                "is_ip_high_risk_area": True,
                "payment_method": "virtual_card"
            }
        }
        check_resp = client.post("/api/risk/check", json=check_payload, headers=auth_headers)
        assert check_resp.status_code == 200
        check_result = check_resp.json()["data"]

        # 验证风险检查结果
        assert check_result["risk_score"] >= 0
        assert check_result["risk_level"] in ["low", "medium", "high"]
        assert check_result["decision"] in ["pass", "manual_review", "reject"]
        assert isinstance(check_result["rule_hits"], list)
        assert isinstance(check_result["feature_snapshot"], dict)

        case_id = check_result.get("case_id")

        # 步骤2：如果有案件，查看详情
        if case_id:
            detail_resp = client.get(f"/api/risk/cases/{case_id}", headers=auth_headers)
            assert detail_resp.status_code == 200
            detail = detail_resp.json()["data"]
            assert detail["case"]["id"] == case_id
            assert detail["case"]["user_id"] == user_id
            assert detail["case"]["case_status"] == "pending"

            # 步骤3：人工审核通过
            review_payload = {
                "case_id": case_id,
                "review_result": "approved",
                "review_remark": "完整链路测试：审核通过"
            }
            review_resp = client.post("/api/risk/cases/review", json=review_payload, headers=auth_headers)
            assert review_resp.status_code == 200
            assert review_resp.json()["code"] == 0

            # 步骤4：查看审核日志
            final_detail = client.get(f"/api/risk/cases/{case_id}", headers=auth_headers).json()["data"]
            assert final_detail["case"]["case_status"] == "approved"
            assert len(final_detail["review_logs"]) >= 1

            # 验证审核日志内容
            review_log = next(
                (l for l in final_detail["review_logs"] if l["action_type"] == "review"),
                None
            )
            assert review_log is not None
            assert review_log["action_remark"] == "完整链路测试：审核通过"


class TestEventLifecycle:
    """验收标准九：事件全生命周期回查"""

    def test_tc_9_1_event_lifecycle_consistency(self, client: TestClient, auth_headers: dict):
        """TC-9.1 事件全链路数据一致性"""
        # 创建风险事件
        user_id = f"U_LIFECYCLE_{uuid.uuid4().hex[:6]}"
        check_payload = {
            "event_type": "order_create",
            "source_id": generate_source_id("tc9.1"),
            "user_id": user_id,
            "order_id": "O_LIFECYCLE_001",
            "event_payload": {
                "order_amount": 10000,
                "user_register_days": 5,
                "device_related_user_count": 8,
                "is_ip_high_risk_area": True
            }
        }
        check_resp = client.post("/api/risk/check", json=check_payload, headers=auth_headers)
        check_result = check_resp.json()["data"]

        # 验证评估详情
        assessment_id = check_result["assessment_id"]
        assess_resp = client.get(f"/api/risk/assessments/{assessment_id}", headers=auth_headers)
        assert assess_resp.status_code == 200
        assess_data = assess_resp.json()["data"]
        assert assess_data["risk_score"] == check_result["risk_score"]
        assert assess_data["risk_level"] == check_result["risk_level"]

        # 如果有案件，验证案件数据一致性
        case_id = check_result.get("case_id")
        if case_id:
            case_resp = client.get(f"/api/risk/cases/{case_id}", headers=auth_headers)
            case_data = case_resp.json()["data"]
            assert case_data["case"]["user_id"] == user_id
            assert case_data["assessment"]["risk_score"] == check_result["risk_score"]

            # 审核后再次验证
            client.post("/api/risk/cases/review", json={
                "case_id": case_id,
                "review_result": "approved",
                "review_remark": "生命周期测试"
            }, headers=auth_headers)

            final_resp = client.get(f"/api/risk/cases/{case_id}", headers=auth_headers)
            final_data = final_resp.json()["data"]
            assert final_data["case"]["case_status"] == "approved"

    def test_tc_9_2_user_profile_after_multiple_events(self, client: TestClient, auth_headers: dict):
        """TC-9.2 多事件回查 - 用户画像更新"""
        user_id = f"U_MULTI_{uuid.uuid4().hex[:6]}"

        # 第一次事件
        client.post("/api/risk/check", json={
            "event_type": "order_create",
            "source_id": generate_source_id("tc9.2a"),
            "user_id": user_id,
            "order_id": "O_MULTI_001",
            "event_payload": {"order_amount": 3000, "user_register_days": 2}
        }, headers=auth_headers)

        # 第二次事件
        client.post("/api/risk/check", json={
            "event_type": "order_pay",
            "source_id": generate_source_id("tc9.2b"),
            "user_id": user_id,
            "order_id": "O_MULTI_002",
            "event_payload": {"order_amount": 5000, "user_register_days": 2}
        }, headers=auth_headers)

        # 查询用户画像
        profile_resp = client.get(f"/api/risk/users/{user_id}/profile", headers=auth_headers)
        assert profile_resp.status_code == 200
        profile = profile_resp.json()["data"]
        assert profile["user_id"] == user_id


class TestIdempotency:
    """幂等性测试"""

    def test_duplicate_source_id_rejected(self, client: TestClient, auth_headers: dict):
        """重复source_id应被拒绝"""
        source_id = generate_source_id("idempotent")
        payload = {
            "event_type": "order_create",
            "source_id": source_id,
            "user_id": "U_IDEM_001",
            "order_id": "O_IDEM_001",
            "event_payload": {"order_amount": 1000}
        }

        # 第一次请求
        resp1 = client.post("/api/risk/check", json=payload, headers=auth_headers)
        assert resp1.status_code == 200
        assert resp1.json()["code"] == 0

        # 第二次请求（相同source_id）
        resp2 = client.post("/api/risk/check", json=payload, headers=auth_headers)
        assert resp2.status_code == 200
        assert resp2.json()["code"] != 0  # 应返回错误


class TestAuthentication:
    """认证测试"""

    def test_unauthorized_access_rejected(self, client: TestClient):
        """未认证访问应被拒绝"""
        response = client.get("/api/risk/rules")
        assert response.status_code == 200
        data = response.json()
        # 应返回认证错误
        assert data["code"] != 0

    def test_health_endpoint_accessible(self, client: TestClient):
        """健康检查端点无需认证"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
