from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import require_permission
from app.core.database import get_db
from app.core.errors import BizError, NOT_FOUND
from app.core.response import ok
from app.models.feature_snapshot import FeatureSnapshot
from app.models.risk_assessment import RiskAssessment
from app.services.effective_risk_service import EffectiveRiskService

router = APIRouter(prefix="/api/risk/assessments", tags=["assessments"])
effective_risk_service = EffectiveRiskService()


@router.get("/{assessment_id}", dependencies=[Depends(require_permission("risk:assessment:read"))])
def detail(assessment_id: int, db: Session = Depends(get_db)):
    assessment = db.query(RiskAssessment).filter(RiskAssessment.id == assessment_id).first()
    if not assessment:
        raise BizError(NOT_FOUND, "assessment not found")
    snapshot = db.query(FeatureSnapshot).filter(FeatureSnapshot.assessment_id == assessment_id).first()
    effective = effective_risk_service.effective_assessment(db, assessment)
    return ok({
        "assessment_id": effective["id"],
        "event_id": effective["event_id"],
        "risk_score": effective["risk_score"],
        "risk_level": effective["risk_level"],
        "decision": effective["decision"],
        "assessment_status": effective["assessment_status"],
        "feature_snapshot": snapshot.feature_json if snapshot else {},
        "rule_hits": effective["rule_hits"],
    })
