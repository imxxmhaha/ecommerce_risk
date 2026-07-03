from typing import Any, Dict, Optional

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
