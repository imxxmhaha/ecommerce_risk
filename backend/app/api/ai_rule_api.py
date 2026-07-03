from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import require_permission
from app.core.database import get_db
from app.core.response import ok
from app.schemas.ai_rule import (
    AiCaseExplainRequest,
    AiDashboardAnalyzeRequest,
    AiRuleExplainRequest,
    AiRuleGenerateRequest,
    AiRuleOverlapRequest,
    AiRuleTestCaseRequest,
    AiRuleValidateRequest,
)
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


@router.post("/overlap", dependencies=[Depends(require_permission("rule:ai"))])
def overlap(req: AiRuleOverlapRequest, db: Session = Depends(get_db)):
    return ok(service.analyze_overlap(db, req.condition_json, req.rule_code))


@router.post("/test-cases", dependencies=[Depends(require_permission("rule:ai"))])
def test_cases(req: AiRuleTestCaseRequest):
    return ok(service.generate_test_cases(req.condition_json, req.scene))


@router.post("/case-explain", dependencies=[Depends(require_permission("rule:ai"))])
def case_explain(req: AiCaseExplainRequest):
    return ok(service.explain_case(req))


@router.post("/dashboard-analyze", dependencies=[Depends(require_permission("dashboard:read"))])
def dashboard_analyze(req: AiDashboardAnalyzeRequest):
    return ok(service.analyze_dashboard(req))
