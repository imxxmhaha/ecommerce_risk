from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class AiRuleGenerateRequest(BaseModel):
    description: str
    expected_score: Optional[float] = 20
    scene: Optional[str] = "order_create"


class AiRuleExplainRequest(BaseModel):
    condition_json: Dict[str, Any]


class AiRuleValidateRequest(BaseModel):
    condition_json: Dict[str, Any]
    score: Optional[float] = None
    priority: Optional[int] = None


class AiRuleOverlapRequest(BaseModel):
    condition_json: Dict[str, Any]
    rule_code: Optional[str] = None


class AiRuleTestCaseRequest(BaseModel):
    condition_json: Dict[str, Any]
    scene: Optional[str] = "order_create"


class AiCaseExplainRequest(BaseModel):
    assessment: Dict[str, Any]
    rule_hits: List[Dict[str, Any]]
    feature_snapshot: Dict[str, Any]


class AiDashboardAnalyzeRequest(BaseModel):
    dashboard_data: Dict[str, Any]
    start_date: Optional[str] = None
    end_date: Optional[str] = None
