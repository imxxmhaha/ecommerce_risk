import json
import re

from app.core.config import get_settings
from app.models.risk_rule import RiskRule
from app.services.feature_service import ALLOWED_FEATURES
from app.services.rule_engine import RuleEngine


class AiRuleService:
    def __init__(self):
        self.engine = RuleEngine()
        self.settings = get_settings()
        self._llm = None

    @property
    def llm(self):
        """懒加载 LLM 实例"""
        if self._llm is None:
            from langchain_openai import ChatOpenAI

            self._llm = ChatOpenAI(
                model=self.settings.llm_model,
                base_url=self.settings.llm_base_url,
                api_key=self.settings.llm_api_key,
                temperature=0.7,
                max_tokens=2000,
            )
        return self._llm

    def _call_llm(self, system_prompt: str, user_prompt: str) -> str:
        """调用 LLM API"""
        try:
            from langchain_core.messages import HumanMessage, SystemMessage

            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt),
            ]
            response = self.llm.invoke(messages)
            return response.content
        except Exception as e:
            return f"LLM调用失败: {str(e)}"

    def _extract_json(self, text: str) -> dict:
        """从 LLM 响应中提取 JSON"""
        # 尝试直接解析
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # 尝试提取 ```json ... ``` 块
        match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                pass

        # 尝试提取第一个 JSON 对象
        match = re.search(r"\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                pass

        return {}

    def generate_rule(self, req):
        """生成规则"""
        if self.settings.ai_mock:
            return self._generate_rule_mock(req)

        system_prompt = f"""你是一个电商风控规则专家。根据用户描述的业务场景，生成风控规则。

可用的特征字段:
{json.dumps(sorted(list(ALLOWED_FEATURES)), ensure_ascii=False, indent=2)}

规则条件JSON格式:
{{
  "operator": "and" | "or",
  "conditions": [
    {{"feature": "特征字段名", "operator": ">" | "<" | "=" | "in", "value": 值}}
  ]
}}

请严格按照以下JSON格式返回，不要包含其他内容:
{{
  "rule_code": "规则编码(大写英文)",
  "rule_name": "规则名称",
  "rule_status": "disabled",
  "score": 分值(0-100),
  "priority": 优先级(数值越大越优先),
  "condition_json": 规则条件JSON,
  "description": "规则描述",
  "hit_message_template": "命中提示模板"
}}"""

        user_prompt = f"""业务场景: {req.scene}
规则描述: {req.description}
期望分值: {req.expected_score or 20}

请生成对应的风控规则。"""

        response = self._call_llm(system_prompt, user_prompt)
        result = self._extract_json(response)

        if not result:
            # 降级到 mock
            return self._generate_rule_mock(req)

        # 验证生成的条件
        if "condition_json" in result:
            validation = self.engine.validate_condition(result["condition_json"], ALLOWED_FEATURES)
            result["validation"] = validation.__dict__
        else:
            result["validation"] = {"passed": False, "errors": ["未生成有效条件"], "warnings": []}

        return result

    def explain_rule(self, condition_json):
        """解释规则"""
        if self.settings.ai_mock:
            return self._explain_rule_mock(condition_json)

        system_prompt = """你是一个电商风控规则专家。请用通俗易懂的语言解释风控规则的含义，并给出优化建议。

请严格按照以下JSON格式返回:
{
  "explanation": "规则的详细解释",
  "hit_message_template": "命中时的提示信息",
  "optimization_suggestions": ["优化建议1", "优化建议2"]
}"""

        user_prompt = f"""规则条件JSON:
```json
{json.dumps(condition_json, ensure_ascii=False, indent=2)}
```

请解释这个规则的含义并给出优化建议。"""

        response = self._call_llm(system_prompt, user_prompt)
        result = self._extract_json(response)

        if not result:
            return self._explain_rule_mock(condition_json)

        return result

    def validate_rule(self, condition_json, score=None, priority=None):
        """验证规则"""
        result = self.engine.validate_condition(condition_json, ALLOWED_FEATURES)
        warnings = list(result.warnings)

        if score is not None and (score < 0 or score > 100):
            result.errors.append("score must be between 0 and 100")
            result.passed = False
        if priority is not None and priority < 0:
            result.errors.append("priority must be greater than or equal to 0")
            result.passed = False

        # AI_MOCK=false 时，调用 LLM 提供更详细的验证反馈
        if not self.settings.ai_mock and result.passed:
            system_prompt = """你是一个电商风控规则专家。请分析这个规则是否合理，是否存在潜在问题。

请严格按照以下JSON格式返回:
{
  "analysis": "规则分析",
  "potential_issues": ["潜在问题1", "潜在问题2"],
  "suggestions": ["建议1", "建议2"]
}"""

            user_prompt = f"""规则条件:
```json
{json.dumps(condition_json, ensure_ascii=False, indent=2)}
```
分值: {score}
优先级: {priority}

请分析这个规则是否合理。"""

            response = self._call_llm(system_prompt, user_prompt)
            ai_analysis = self._extract_json(response)

            if ai_analysis:
                warnings.extend(ai_analysis.get("potential_issues", []))
                warnings.extend([f"建议: {s}" for s in ai_analysis.get("suggestions", [])])

        return {"passed": result.passed, "errors": result.errors, "warnings": warnings}

    def analyze_overlap(self, db, condition_json, rule_code=None):
        validation = self.engine.validate_condition(condition_json, ALLOWED_FEATURES)
        if not validation.passed:
            return {
                "passed": False,
                "errors": validation.errors,
                "overlaps": [],
                "summary": "规则条件不合法，无法进行重叠检测",
            }

        rules = db.query(RiskRule).filter(RiskRule.rule_status == "enabled").all()
        new_constraints = self._extract_constraints(condition_json)
        overlaps = []
        for rule in rules:
            if rule_code and rule.rule_code == rule_code:
                continue
            relation = self._overlap_relation(new_constraints, self._extract_constraints(rule.condition_json))
            if relation:
                overlaps.append({
                    "rule_id": rule.id,
                    "rule_code": rule.rule_code,
                    "rule_name": rule.rule_name,
                    "priority": rule.priority,
                    "score": float(rule.score),
                    "relation": relation,
                    "suggestion": self._overlap_suggestion(relation, rule),
                })

        return {
            "passed": True,
            "errors": [],
            "overlaps": overlaps,
            "summary": f"发现 {len(overlaps)} 条可能重叠的启用规则" if overlaps else "未发现明显重叠规则",
        }

    def generate_test_cases(self, condition_json, scene="order_create"):
        validation = self.engine.validate_condition(condition_json, ALLOWED_FEATURES)
        if not validation.passed:
            return {"passed": False, "errors": validation.errors, "cases": []}

        hit_payload = self._base_event_payload()
        miss_payload = self._base_event_payload()
        self._fill_payloads_for_condition(condition_json, hit_payload, miss_payload)
        return {
            "passed": True,
            "errors": [],
            "cases": [
                {
                    "name": "should_hit",
                    "description": "应命中该规则的事件样例",
                    "event_type": scene,
                    "event_payload": hit_payload,
                },
                {
                    "name": "should_not_hit",
                    "description": "不应命中该规则的事件样例",
                    "event_type": scene,
                    "event_payload": miss_payload,
                },
            ],
        }

    def explain_case(self, req):
        if self.settings.ai_mock:
            return self._explain_case_mock(req.assessment, req.rule_hits, req.feature_snapshot)

        system_prompt = """你是电商风控审核助手。请基于评估结果、命中规则和特征快照，输出简洁、可审计的中文案件解释。
严格返回 JSON:
{
  "summary": "一句话风险摘要",
  "effective_rule_explanation": "最终生效规则说明",
  "review_suggestion": "审核建议",
  "key_evidence": ["证据1", "证据2"]
}"""
        user_prompt = json.dumps({
            "assessment": req.assessment,
            "rule_hits": req.rule_hits,
            "feature_snapshot": req.feature_snapshot,
        }, ensure_ascii=False, indent=2)
        response = self._call_llm(system_prompt, user_prompt)
        result = self._extract_json(response)
        return result or self._explain_case_mock(req.assessment, req.rule_hits, req.feature_snapshot)

    # ========== Mock 实现 ==========

    def _generate_rule_mock(self, req):
        """Mock: 生成规则"""
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
            "rule_status": "disabled",
            "score": float(req.expected_score or 20),
            "priority": 20,
            "condition_json": condition,
            "description": "注册时间较短的新用户产生高额订单，存在风险",
            "hit_message_template": f"用户注册天数小于{days}天且订单金额大于{amount}元",
            "validation": validation.__dict__,
        }

    def _explain_rule_mock(self, condition_json):
        """Mock: 解释规则"""
        explanation = self._explain_node(condition_json)
        return {
            "explanation": explanation,
            "hit_message_template": explanation,
            "optimization_suggestions": ["可结合用户历史退款率降低误伤率", "可增加黑名单或设备维度作为组合条件"],
        }

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

    def _extract_constraints(self, condition_json):
        if not condition_json:
            return []
        operator = condition_json.get("operator")
        if operator in {"and", "or"}:
            constraints = []
            for child in condition_json.get("conditions", []):
                constraints.extend(self._extract_constraints(child))
            return constraints
        return [{
            "feature": condition_json.get("feature"),
            "operator": operator,
            "value": condition_json.get("value"),
        }]

    def _overlap_relation(self, new_constraints, old_constraints):
        new_by_feature = {item["feature"]: item for item in new_constraints if item.get("feature")}
        old_by_feature = {item["feature"]: item for item in old_constraints if item.get("feature")}
        shared_features = set(new_by_feature) & set(old_by_feature)
        if not shared_features:
            return None

        implied_new_to_old = []
        implied_old_to_new = []
        compatible_count = 0
        for feature in shared_features:
            relation = self._constraint_relation(new_by_feature[feature], old_by_feature[feature])
            if relation:
                compatible_count += 1
            if relation in {"new_implies_old", "same"}:
                implied_new_to_old.append(feature)
            if relation in {"old_implies_new", "same"}:
                implied_old_to_new.append(feature)

        if compatible_count == 0:
            return None
        if len(implied_new_to_old) == len(old_by_feature):
            return "new_rule_subset_of_existing"
        if len(implied_old_to_new) == len(new_by_feature):
            return "existing_rule_subset_of_new"
        return "partial_overlap"

    def _constraint_relation(self, new_item, old_item):
        new_op, old_op = new_item.get("operator"), old_item.get("operator")
        new_val, old_val = new_item.get("value"), old_item.get("value")
        if new_op != old_op:
            return None
        if new_val == old_val:
            return "same"
        try:
            new_num = float(new_val)
            old_num = float(old_val)
        except (TypeError, ValueError):
            new_num = old_num = None

        if new_op == ">" and new_num is not None:
            return "new_implies_old" if new_num > old_num else "old_implies_new"
        if new_op == "<" and new_num is not None:
            return "new_implies_old" if new_num < old_num else "old_implies_new"
        if new_op == "in" and isinstance(new_val, list) and isinstance(old_val, list):
            new_set, old_set = set(new_val), set(old_val)
            if new_set <= old_set:
                return "new_implies_old"
            if old_set <= new_set:
                return "old_implies_new"
            if new_set & old_set:
                return "partial_overlap"
        return None

    def _overlap_suggestion(self, relation, rule):
        if relation == "new_rule_subset_of_existing":
            return f"新规则覆盖范围更窄，若风险更严重，建议 priority 高于 {rule.priority} 或提高分值"
        if relation == "existing_rule_subset_of_new":
            return "新规则覆盖范围更宽，建议确认是否会稀释原规则风险含义"
        return "存在部分条件重叠，建议检查优先级和最终生效规则是否符合预期"

    def _base_event_payload(self):
        return {
            "order_amount": 100,
            "order_item_count": 1,
            "user_register_days": 90,
            "payment_method": "alipay",
            "is_coupon_used": False,
            "coupon_discount_rate": 0,
            "is_first_order": False,
        }

    def _fill_payloads_for_condition(self, condition, hit_payload, miss_payload):
        operator = condition.get("operator")
        if operator in {"and", "or"}:
            children = condition.get("conditions", [])
            for child in children:
                self._fill_payloads_for_condition(child, hit_payload, miss_payload)
            return

        feature = condition.get("feature")
        expected = condition.get("value")
        if not feature:
            return
        if operator == ">":
            hit_payload[feature] = float(expected) + 1
            miss_payload[feature] = float(expected)
        elif operator == "<":
            hit_payload[feature] = float(expected) - 1
            miss_payload[feature] = float(expected)
        elif operator == "=":
            hit_payload[feature] = expected
            miss_payload[feature] = not expected if isinstance(expected, bool) else f"not_{expected}"
        elif operator == "in":
            values = expected if isinstance(expected, list) else [expected]
            hit_payload[feature] = values[0] if values else None
            miss_payload[feature] = "__not_in_list__"

    def _explain_case_mock(self, assessment, rule_hits, feature_snapshot):
        effective = next((item for item in rule_hits if item.get("is_effective")), None)
        if not effective and rule_hits:
            effective = max(rule_hits, key=lambda item: (item.get("priority") or 0, float(item.get("hit_score") or 0)))
        if not effective:
            return {
                "summary": "当前事件未命中风险规则，建议直接通过",
                "effective_rule_explanation": "无最终生效规则",
                "review_suggestion": "通过",
                "key_evidence": [],
            }

        feature_evidence = []
        for key, value in feature_snapshot.items():
            if value not in (0, 0.0, False, "", None, "alipay", "wechat_pay"):
                feature_evidence.append(f"{key}={value}")
            if len(feature_evidence) >= 5:
                break

        return {
            "summary": f"最终按照 {effective.get('rule_name')} 判定，风险分 {assessment.get('risk_score')}",
            "effective_rule_explanation": effective.get("hit_message") or effective.get("rule_name"),
            "review_suggestion": "拒绝" if assessment.get("decision") == "reject" else "人工复核" if assessment.get("decision") == "manual_review" else "通过",
            "key_evidence": feature_evidence,
        }
