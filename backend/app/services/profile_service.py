from sqlalchemy.orm import Session

from app.models.risk_assessment import RiskAssessment
from app.models.risk_case import RiskCase
from app.models.risk_event import RiskEvent
from app.models.risk_rule import RiskRule
from app.models.rule_hit import RuleHit
from app.services.effective_risk_service import EffectiveRiskService


class ProfileService:
    def __init__(self):
        self.effective_risk_service = EffectiveRiskService()

    def get_profile(self, db: Session, user_id: str):
        events = db.query(RiskEvent).filter(RiskEvent.user_id == user_id).order_by(RiskEvent.created_at.desc()).limit(20).all()
        event_ids = [e.id for e in events]
        assessments = db.query(RiskAssessment).filter(RiskAssessment.event_id.in_(event_ids)).order_by(RiskAssessment.created_at.desc()).limit(20).all() if event_ids else []
        effective_assessments = [self.effective_risk_service.effective_assessment(db, item) for item in assessments]
        cases = db.query(RiskCase).filter(RiskCase.user_id == user_id).order_by(RiskCase.created_at.desc()).limit(20).all()
        high_count = sum(1 for a in effective_assessments if a["risk_level"] == "high")
        reject_count = sum(1 for a in effective_assessments if a["decision"] == "reject")
        assessment_ids = [a.id for a in assessments]
        top_rules = []
        if assessment_ids:
            rows = (
                db.query(RiskRule.rule_name, RiskRule.rule_code, RuleHit.rule_id)
                .join(RuleHit, RuleHit.rule_id == RiskRule.id)
                .filter(RuleHit.assessment_id.in_(assessment_ids), RiskRule.rule_status == "enabled")
                .all()
            )
            counter = {}
            for name, code, _ in rows:
                counter[(name, code)] = counter.get((name, code), 0) + 1
            top_rules = [{"rule_name": k[0], "rule_code": k[1], "hit_count": v} for k, v in sorted(counter.items(), key=lambda x: x[1], reverse=True)[:10]]
        return {
            "user_id": user_id,
            "summary": {"event_count": len(events), "high_risk_count": high_count, "case_count": len(cases), "reject_count": reject_count},
            "recent_events": [{"id": e.id, "event_type": e.event_type, "source_id": e.source_id, "order_id": e.order_id, "created_at": e.created_at} for e in events],
            "recent_assessments": [{"id": a["id"], "risk_score": a["risk_score"], "risk_level": a["risk_level"], "decision": a["decision"], "created_at": a["created_at"]} for a in effective_assessments],
            "related_cases": [{"id": c.id, "order_id": c.order_id, "case_status": c.case_status, "review_result": c.review_result, "created_at": c.created_at} for c in cases],
            "top_hit_rules": top_rules,
        }
