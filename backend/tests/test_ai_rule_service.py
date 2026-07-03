from types import SimpleNamespace

from app.services.ai_rule_service import AiRuleService


def test_generate_rule_test_cases():
    service = AiRuleService()
    condition_json = {
        "operator": "and",
        "conditions": [
            {"feature": "user_register_days", "operator": "<", "value": 7},
            {"feature": "order_amount", "operator": ">", "value": 5000},
        ],
    }

    result = service.generate_test_cases(condition_json, "order_create")

    assert result["passed"] is True
    assert len(result["cases"]) == 2
    assert result["cases"][0]["event_payload"]["user_register_days"] == 6
    assert result["cases"][0]["event_payload"]["order_amount"] == 5001


def test_explain_case_uses_effective_rule():
    service = AiRuleService()
    req = SimpleNamespace(
        assessment={"risk_score": 60, "decision": "manual_review"},
        rule_hits=[
            {"rule_name": "low priority rule", "priority": 20, "hit_score": 80, "is_effective": False},
            {"rule_name": "final rule", "priority": 100, "hit_score": 60, "is_effective": True, "hit_message": "final reason"},
        ],
        feature_snapshot={"order_amount": 6000, "user_register_days": 3},
    )

    result = service.explain_case(req)

    assert "final rule" in result["summary"]
    assert result["effective_rule_explanation"] == "final reason"
    assert result["review_suggestion"] == "人工复核"


def test_analyze_dashboard_returns_trend_summary():
    service = AiRuleService()
    req = SimpleNamespace(
        start_date="2026-07-01",
        end_date="2026-07-03",
        dashboard_data={
            "event_total": 100,
            "high_risk_rate": 0.35,
            "case_total": 20,
            "resolved_case_total": 10,
            "blacklist_hit_count": 3,
            "rule_hit_ranking": [
                {"rule_name": "设备关联用户过多", "rule_code": "DEVICE_MULTI_USER", "hit_count": 12},
                {"rule_name": "支付方式风险较高", "rule_code": "PAYMENT_METHOD_RISK", "hit_count": 8},
            ],
        },
    )

    result = service.analyze_dashboard(req)

    assert "风险事件 100 起" in result["summary"]
    assert result["insights"]
    assert result["suggestions"]
    assert "设备关联用户过多" in result["risk_focus"]
