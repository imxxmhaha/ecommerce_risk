from sqlalchemy.orm import Session

from app.models.risk_rule import RiskRule
from app.models.rule_hit import RuleHit
from app.services.decision_service import DecisionService


class EffectiveRiskService:
    def __init__(self):
        self.decision_service = DecisionService()

    def active_rule_hits(self, db: Session, assessment_id: int):
        rows = (
            db.query(RuleHit, RiskRule)
            .join(RiskRule, RuleHit.rule_id == RiskRule.id)
            .filter(
                RuleHit.assessment_id == assessment_id,
                RiskRule.rule_status == 1,
            )
            .order_by(RiskRule.priority.desc(), RiskRule.id.asc())
            .all()
        )
        return [
            {
                "rule_code": rule.rule_code,
                "rule_name": rule.rule_name,
                "priority": rule.priority,
                "hit_score": float(rule.score),
                "original_hit_score": float(hit.hit_score),
                "hit_message": rule.description or hit.hit_message or rule.rule_name,
            }
            for hit, rule in rows
        ]

    def summarize(self, rule_hits: list[dict]):
        score = self.decision_service.calculate_score(rule_hits)
        level = self.decision_service.calculate_level(score)
        decision = self.decision_service.calculate_decision(score, level, rule_hits)
        return {
            "risk_score": score,
            "risk_level": level,
            "decision": decision,
        }

    def effective_assessment(self, db: Session, assessment):
        rule_hits = self.active_rule_hits(db, assessment.id)
        marked_rule_hits = self.decision_service.mark_effective_hit(rule_hits)
        summary = self.summarize(rule_hits)
        return {
            "id": assessment.id,
            "event_id": assessment.event_id,
            "risk_score": summary["risk_score"],
            "risk_level": summary["risk_level"],
            "decision": summary["decision"],
            "assessment_status": assessment.assessment_status,
            "created_at": assessment.created_at,
            "rule_hits": marked_rule_hits,
        }
