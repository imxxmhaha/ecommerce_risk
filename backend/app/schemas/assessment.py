from typing import Any, Dict, List

from pydantic import BaseModel

from app.schemas.risk_check import RuleHitView


class AssessmentDetail(BaseModel):
    assessment_id: int
    event_id: int
    risk_score: float
    risk_level: str
    decision: str
    assessment_status: str
    feature_snapshot: Dict[str, Any]
    rule_hits: List[RuleHitView]
