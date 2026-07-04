from datetime import datetime, timedelta

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.risk_assessment import RiskAssessment
from app.models.risk_case import RiskCase
from app.models.risk_event import RiskEvent
from app.models.risk_rule import RiskRule
from app.models.rule_hit import RuleHit
from app.services.effective_risk_service import EffectiveRiskService


class DashboardService:
    def __init__(self):
        self.effective_risk_service = EffectiveRiskService()

    def dashboard(self, db: Session, start_date=None, end_date=None):
        start = self._parse(start_date) or (datetime.now() - timedelta(days=30))
        end = self._parse(end_date) or datetime.now()
        event_total = db.query(RiskEvent).filter(RiskEvent.created_at >= start, RiskEvent.created_at <= end).count()
        assessments = db.query(RiskAssessment).filter(RiskAssessment.created_at >= start, RiskAssessment.created_at <= end).all()
        effective_assessments = [self.effective_risk_service.effective_assessment(db, item) for item in assessments]
        high_count = sum(1 for a in effective_assessments if a["risk_level"] == "high")
        case_total = db.query(RiskCase).filter(RiskCase.created_at >= start, RiskCase.created_at <= end).count()
        resolved_case_total = db.query(RiskCase).filter(RiskCase.case_status.in_(["approved", "rejected"]), RiskCase.created_at >= start, RiskCase.created_at <= end).count()
        dist = {}
        for item in effective_assessments:
            dist[item["risk_level"]] = dist.get(item["risk_level"], 0) + 1
        ranking_rows = (
            db.query(RiskRule.rule_name, RiskRule.rule_code, func.count(RuleHit.id))
            .join(RuleHit, RuleHit.rule_id == RiskRule.id)
            .filter(RuleHit.created_at >= start, RuleHit.created_at <= end, RiskRule.rule_status == 1)
            .group_by(RiskRule.rule_name, RiskRule.rule_code)
            .order_by(func.count(RuleHit.id).desc())
            .limit(10)
            .all()
        )
        return {
            "event_total": event_total,
            "high_risk_rate": round(high_count / len(effective_assessments), 4) if effective_assessments else 0,
            "case_total": case_total,
            "resolved_case_total": resolved_case_total,
            "avg_case_process_hours": 0,
            "risk_level_distribution": [{"name": k, "value": v} for k, v in dist.items()],
            "rule_hit_ranking": [{"rule_name": n, "rule_code": c, "hit_count": count} for n, c, count in ranking_rows],
            "blacklist_hit_count": sum(count for _, c, count in ranking_rows if "BLACKLIST" in c),
            "risk_event_trend": [],
        }

    def _parse(self, value):
        if not value:
            return None
        try:
            return datetime.fromisoformat(value)
        except ValueError:
            return None
