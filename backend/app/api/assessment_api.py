from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import require_permission
from app.core.database import get_db
from app.core.errors import BizError, NOT_FOUND
from app.core.response import ok
from app.models.feature_snapshot import FeatureSnapshot
from app.models.risk_assessment import RiskAssessment
from app.models.risk_rule import RiskRule
from app.models.rule_hit import RuleHit

router = APIRouter(prefix="/api/risk/assessments", tags=["assessments"])


@router.get("/{assessment_id}", dependencies=[Depends(require_permission("risk:assessment:read"))])
def detail(assessment_id: int, db: Session = Depends(get_db)):
    assessment = db.query(RiskAssessment).filter(RiskAssessment.id == assessment_id).first()
    if not assessment:
        raise BizError(NOT_FOUND, "assessment not found")
    snapshot = db.query(FeatureSnapshot).filter(FeatureSnapshot.assessment_id == assessment_id).first()
    hits = db.query(RuleHit, RiskRule).join(RiskRule, RuleHit.rule_id == RiskRule.id).filter(RuleHit.assessment_id == assessment_id).all()
    return ok({
        "assessment_id": assessment.id,
        "event_id": assessment.event_id,
        "risk_score": float(assessment.risk_score),
        "risk_level": assessment.risk_level,
        "decision": assessment.decision,
        "assessment_status": assessment.assessment_status,
        "feature_snapshot": snapshot.feature_json if snapshot else {},
        "rule_hits": [
            {"rule_code": r.rule_code, "rule_name": r.rule_name, "hit_score": float(h.hit_score), "hit_message": h.hit_message}
            for h, r in hits
        ],
    })
