class DecisionService:
    def calculate_score(self, hits):
        score = sum(float(item["hit_score"]) for item in hits)
        return min(score, 100.0)

    def calculate_level(self, score: float) -> str:
        if score < 30:
            return "low"
        if score < 70:
            return "medium"
        return "high"

    def calculate_decision(self, score: float, risk_level: str, hits) -> str:
        hit_codes = {item.get("rule_code") for item in hits}
        if {"USER_BLACKLIST", "ORDER_BLACKLIST"} & hit_codes:
            return "reject"
        if risk_level == "low":
            return "pass"
        return "manual_review"
