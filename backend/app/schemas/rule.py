from typing import Any, Dict, Optional

from pydantic import BaseModel


class RuleCreateRequest(BaseModel):
    rule_code: str
    rule_name: str
    rule_status: str = "enabled"
    priority: int = 100
    score: float = 0
    condition_json: Dict[str, Any]
    description: Optional[str] = None


class RuleUpdateRequest(BaseModel):
    id: int
    rule_code: Optional[str] = None
    rule_name: Optional[str] = None
    rule_status: Optional[str] = None
    priority: Optional[int] = None
    score: Optional[float] = None
    condition_json: Optional[Dict[str, Any]] = None
    description: Optional[str] = None


class RuleStatusRequest(BaseModel):
    id: int
    rule_status: str


class RuleDeleteRequest(BaseModel):
    id: int
