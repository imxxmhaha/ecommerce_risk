from dataclasses import dataclass, field
from typing import Any, Dict, List, Set


@dataclass
class ValidationResult:
    passed: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


class RuleEngine:
    SIMPLE_OPERATORS = {">", "<", "=", "in"}
    GROUP_OPERATORS = {"and", "or"}

    def evaluate(self, condition_json: Dict[str, Any], feature_json: Dict[str, Any]) -> bool:
        operator = condition_json.get("operator")
        if operator in self.GROUP_OPERATORS:
            return self.evaluate_group_condition(condition_json, feature_json)
        return self.evaluate_simple_condition(condition_json, feature_json)

    def evaluate_group_condition(self, condition: Dict[str, Any], feature_json: Dict[str, Any]) -> bool:
        operator = condition.get("operator")
        children = condition.get("conditions") or []
        results = [self.evaluate(child, feature_json) for child in children]
        if operator == "and":
            return all(results)
        if operator == "or":
            return any(results)
        return False

    def evaluate_simple_condition(self, condition: Dict[str, Any], feature_json: Dict[str, Any]) -> bool:
        feature = condition.get("feature")
        operator = condition.get("operator")
        expected = condition.get("value")
        actual = feature_json.get(feature)
        try:
            if operator == ">":
                return float(actual) > float(expected)
            if operator == "<":
                return float(actual) < float(expected)
            if operator == "=":
                return actual == expected
            if operator == "in":
                if isinstance(expected, list):
                    return actual in expected
                if isinstance(actual, list):
                    return expected in actual
        except (TypeError, ValueError):
            return False
        return False

    def validate_condition(self, condition_json: Dict[str, Any], allowed_features: Set[str]) -> ValidationResult:
        errors: List[str] = []
        self._validate_node(condition_json, allowed_features, errors, "root")
        return ValidationResult(passed=not errors, errors=errors, warnings=[])

    def _validate_node(self, node: Dict[str, Any], allowed_features: Set[str], errors: List[str], path: str):
        operator = node.get("operator")
        if operator in self.GROUP_OPERATORS:
            conditions = node.get("conditions")
            if not isinstance(conditions, list) or not conditions:
                errors.append(f"{path}: group condition requires non-empty conditions")
                return
            for idx, child in enumerate(conditions):
                self._validate_node(child, allowed_features, errors, f"{path}.conditions[{idx}]")
            return
        if operator not in self.SIMPLE_OPERATORS:
            errors.append(f"{path}: unsupported operator {operator}")
        feature = node.get("feature")
        if not feature:
            errors.append(f"{path}: feature is required")
        elif feature not in allowed_features:
            errors.append(f"{path}: unknown feature {feature}")
        if "value" not in node:
            errors.append(f"{path}: value is required")
