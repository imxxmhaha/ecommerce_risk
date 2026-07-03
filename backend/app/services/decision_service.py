class DecisionService:
    def effective_hits(self, hits):
        if not hits:
            return []
        priorities = [item.get("priority") for item in hits if item.get("priority") is not None]
        if not priorities:
            return hits
        highest_priority = min(priorities)
        return [item for item in hits if item.get("priority") == highest_priority]

    def calculate_score(self, hits):
        effective_hits = self.effective_hits(hits)
        score = sum(float(item["hit_score"]) for item in effective_hits)
        return min(score, 100.0)

    def calculate_level(self, score: float) -> str:
        if score < 30:
            return "low"
        if score < 70:
            return "medium"
        return "high"

    def calculate_decision(self, score: float, risk_level: str, hits) -> str:
        effective_hits = self.effective_hits(hits)
        hit_codes = {item.get("rule_code") for item in effective_hits}
        if {"USER_BLACKLIST", "ORDER_BLACKLIST"} & hit_codes:
            return "reject"
        if risk_level == "low":
            return "pass"
        return "manual_review"
