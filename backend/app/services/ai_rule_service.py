import json
import re

from app.core.config import get_settings
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
