from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class RiskCheckRequest(BaseModel):
    event_type: str
    source_id: str
    user_id: str
    order_id: Optional[str] = None
    event_payload: Dict[str, Any] = Field(default_factory=dict)


class RuleHitView(BaseModel):
    rule_code: str
    rule_name: str
    priority: Optional[int] = None
    hit_score: float
    is_effective: bool = False
    hit_message: Optional[str] = None


class RiskCheckResult(BaseModel):
    assessment_id: int
    event_id: int
    risk_score: float
    risk_level: str
    decision: str
    case_id: Optional[int] = None
    rule_hits: List[RuleHitView]
    feature_snapshot: Dict[str, Any]
