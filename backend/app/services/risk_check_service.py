from sqlalchemy.orm import Session

from app.core.errors import BizError, CONFLICT, PARAM_ERROR
from app.models.feature_snapshot import FeatureSnapshot
from app.models.review_log import ReviewLog
from app.models.risk_assessment import RiskAssessment
from app.models.risk_case import RiskCase
from app.models.risk_event import RiskEvent
from app.models.rule_hit import RuleHit
from app.services.decision_service import DecisionService
from app.services.feature_service import FeatureService
from app.services.rule_engine import RuleEngine
from app.services.rule_service import RuleService

VALID_EVENT_TYPES = {"order_create", "order_pay", "after_sale_apply", "logistics_complaint"}


class RiskCheckService:
    def __init__(self):
        self.feature_service = FeatureService()
        self.rule_engine = RuleEngine()
        self.rule_service = RuleService()
        self.decision_service = DecisionService()

    def check(self, db: Session, req):
        if req.event_type not in VALID_EVENT_TYPES:
            raise BizError(PARAM_ERROR, "event_type is invalid")
        if db.query(RiskEvent).filter(RiskEvent.source_id == req.source_id).first():
            raise BizError(CONFLICT, "source_id already exists")
        try:
            event = RiskEvent(
                event_type=req.event_type,
                source_id=req.source_id,
                user_id=req.user_id,
                order_id=req.order_id,
                event_payload_json=req.event_payload,
            )
            db.add(event)
            db.flush()

            features = self.feature_service.build_features(db, event, req.event_payload)
            enabled_rules = self.rule_service.enabled_rules(db)
            hit_views = []
            hit_rules = []
            for rule in enabled_rules:
                if self.rule_engine.evaluate(rule.condition_json, features):
                    hit_views.append({
                        "rule_id": rule.id,
                        "rule_code": rule.rule_code,
                        "rule_name": rule.rule_name,
                        "priority": rule.priority,
                        "hit_score": float(rule.score),
                        "hit_message": rule.description or rule.rule_name,
                    })
                    hit_rules.append(rule)

            score = self.decision_service.calculate_score(hit_views)
            level = self.decision_service.calculate_level(score)
            decision = self.decision_service.calculate_decision(score, level, hit_views)

            assessment = RiskAssessment(
                event_id=event.id,
                risk_score=score,
                risk_level=level,
                decision=decision,
                assessment_status="completed",
            )
            db.add(assessment)
            db.flush()

            db.add(FeatureSnapshot(assessment_id=assessment.id, feature_json=features))
            for hit in hit_views:
                db.add(RuleHit(
                    assessment_id=assessment.id,
                    rule_id=hit["rule_id"],
                    hit_score=hit["hit_score"],
                    hit_message=hit["hit_message"],
                ))
            for rule in hit_rules:
                rule.hit_count = (rule.hit_count or 0) + 1

            case_id = None
            if level == "high" or decision in {"manual_review", "reject"}:
                case = RiskCase(assessment_id=assessment.id, user_id=event.user_id, order_id=event.order_id, case_status="pending")
                db.add(case)
                db.flush()
                case_id = case.id
                db.add(ReviewLog(
                    case_id=case.id,
                    operator_id="system",
                    action_type="create",
                    from_status=None,
                    to_status="pending",
                    action_remark="风险评估结果触发自动建案",
                ))

            db.commit()
            return {
                "assessment_id": assessment.id,
                "event_id": event.id,
                "risk_score": float(score),
                "risk_level": level,
                "decision": decision,
                "case_id": case_id,
                "rule_hits": [{k: v for k, v in hit.items() if k != "rule_id"} for hit in hit_views],
                "feature_snapshot": features,
            }
        except Exception:
            db.rollback()
            raise
