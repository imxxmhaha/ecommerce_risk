import re

from app.services.feature_service import ALLOWED_FEATURES
from app.services.rule_engine import RuleEngine


class AiRuleService:
    def __init__(self):
        self.engine = RuleEngine()

    def generate_rule(self, req):
        amount = self._number_after(req.description, "金额") or 3000
        days = self._number_after(req.description, "注册") or 7
        condition = {
            "operator": "and",
            "conditions": [
                {"feature": "user_register_days", "operator": "<", "value": days},
                {"feature": "order_amount", "operator": ">", "value": amount},
            ],
        }
        validation = self.engine.validate_condition(condition, ALLOWED_FEATURES)
        return {
            "rule_code": "AI_NEW_USER_HIGH_AMOUNT",
            "rule_name": "AI生成-新用户高额订单",
            "rule_status": "enabled",
            "score": float(req.expected_score or 20),
            "priority": 20,
            "condition_json": condition,
            "description": "注册时间较短的新用户产生高额订单，存在风险",
            "hit_message_template": f"用户注册天数小于{days}天且订单金额大于{amount}元",
            "validation": validation.__dict__,
        }

    def explain_rule(self, condition_json):
        explanation = self._explain_node(condition_json)
        return {
            "explanation": explanation,
            "hit_message_template": explanation,
            "optimization_suggestions": ["可结合用户历史退款率降低误伤率", "可增加黑名单或设备维度作为组合条件"],
        }

    def validate_rule(self, condition_json, score=None, priority=None):
        result = self.engine.validate_condition(condition_json, ALLOWED_FEATURES)
        warnings = list(result.warnings)
        if score is not None and (score < 0 or score > 100):
            result.errors.append("score must be between 0 and 100")
            result.passed = False
        if priority is not None and priority < 0:
            result.errors.append("priority must be greater than or equal to 0")
            result.passed = False
        return {"passed": result.passed, "errors": result.errors, "warnings": warnings}

    def _number_after(self, text, keyword):
        idx = text.find(keyword)
        target = text[idx:] if idx >= 0 else text
        match = re.search(r"(\d+)", target)
        return int(match.group(1)) if match else None

    def _explain_node(self, node):
        operator = node.get("operator")
        if operator in {"and", "or"}:
            sep = " 且 " if operator == "and" else " 或 "
            return sep.join(self._explain_node(item) for item in node.get("conditions", []))
        return f"当 {node.get('feature')} {operator} {node.get('value')} 时命中"
