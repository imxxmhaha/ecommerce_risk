class DecisionService:
    def effective_hit(self, hits):
        if not hits:
            return None
        priorities = [item.get("priority") for item in hits if item.get("priority") is not None]
        if not priorities:
            return max(hits, key=lambda item: float(item.get("hit_score") or 0))
        highest_priority = max(priorities)
        same_priority_hits = [item for item in hits if item.get("priority") == highest_priority]
        return max(same_priority_hits, key=lambda item: float(item.get("hit_score") or 0))

    def effective_hits(self, hits):
        effective_hit = self.effective_hit(hits)
        if not effective_hit:
            return []
        return [effective_hit]

    def mark_effective_hit(self, hits):
        effective_hit = self.effective_hit(hits)
        return [
            {
                **item,
                "is_effective": item is effective_hit,
            }
            for item in hits
        ]

    def calculate_score(self, hits):
        effective_hit = self.effective_hit(hits)
        score = float(effective_hit["hit_score"]) if effective_hit else 0.0
        return min(score, 100.0)

    def calculate_level(self, score: float) -> str:
        if score < 30:
            return "low"
        if score < 70:
            return "medium"
        return "high"

    def calculate_decision(self, score: float, risk_level: str, hits) -> str:
        effective_hit = self.effective_hit(hits)
        if effective_hit and effective_hit.get("rule_code") in {"USER_BLACKLIST", "ORDER_BLACKLIST"}:
            return "reject"
        if risk_level == "low":
            return "pass"
        return "manual_review"
