from fastapi import APIRouter, Depends

from app.api.deps import require_permission
from app.core.response import ok
from app.schemas.ai_rule import AiRuleExplainRequest, AiRuleGenerateRequest, AiRuleValidateRequest
from app.services.ai_rule_service import AiRuleService

router = APIRouter(prefix="/api/risk/ai/rules", tags=["ai-rules"])
service = AiRuleService()


@router.post("/generate", dependencies=[Depends(require_permission("rule:ai"))])
def generate(req: AiRuleGenerateRequest):
    return ok(service.generate_rule(req))


@router.post("/explain", dependencies=[Depends(require_permission("rule:ai"))])
def explain(req: AiRuleExplainRequest):
    return ok(service.explain_rule(req.condition_json))


@router.post("/validate", dependencies=[Depends(require_permission("rule:ai"))])
def validate(req: AiRuleValidateRequest):
    return ok(service.validate_rule(req.condition_json, req.score, req.priority))
