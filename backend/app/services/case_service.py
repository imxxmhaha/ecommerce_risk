from sqlalchemy.orm import Session

from app.core.errors import BizError, NOT_FOUND, PARAM_ERROR
from app.models.feature_snapshot import FeatureSnapshot
from app.models.review_log import ReviewLog
from app.models.risk_assessment import RiskAssessment
from app.models.risk_case import RiskCase
from app.models.risk_rule import RiskRule
from app.models.rule_hit import RuleHit


def case_to_dict(case: RiskCase):
    return {
        "id": case.id,
        "assessment_id": case.assessment_id,
        "user_id": case.user_id,
        "order_id": case.order_id,
        "case_status": case.case_status,
        "reviewer_id": case.reviewer_id,
        "review_result": case.review_result,
        "review_remark": case.review_remark,
        "created_at": case.created_at,
        "updated_at": case.updated_at,
    }


class CaseService:
    def list_cases(self, db: Session, case_status=None, user_id=None, order_id=None, page=1, page_size=20):
        query = db.query(RiskCase)
        if case_status:
            query = query.filter(RiskCase.case_status == case_status)
        if user_id:
            query = query.filter(RiskCase.user_id == user_id)
        if order_id:
            query = query.filter(RiskCase.order_id == order_id)
        total = query.count()
        items = query.order_by(RiskCase.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
        return {"items": [case_to_dict(x) for x in items], "total": total, "page": page, "page_size": page_size}

    def detail(self, db: Session, case_id: int):
        case = db.query(RiskCase).filter(RiskCase.id == case_id).first()
        if not case:
            raise BizError(NOT_FOUND, "case not found")
        assessment = db.query(RiskAssessment).filter(RiskAssessment.id == case.assessment_id).first()
        snapshot = db.query(FeatureSnapshot).filter(FeatureSnapshot.assessment_id == case.assessment_id).first()
        hits = db.query(RuleHit, RiskRule).join(RiskRule, RuleHit.rule_id == RiskRule.id).filter(RuleHit.assessment_id == case.assessment_id).all()
        logs = db.query(ReviewLog).filter(ReviewLog.case_id == case.id).order_by(ReviewLog.created_at.asc()).all()
        return {
            "case": case_to_dict(case),
            "assessment": {
                "id": assessment.id,
                "risk_score": float(assessment.risk_score),
                "risk_level": assessment.risk_level,
                "decision": assessment.decision,
                "created_at": assessment.created_at,
            } if assessment else None,
            "feature_snapshot": snapshot.feature_json if snapshot else {},
            "rule_hits": [
                {"rule_code": r.rule_code, "rule_name": r.rule_name, "hit_score": float(h.hit_score), "hit_message": h.hit_message}
                for h, r in hits
            ],
            "review_logs": [
                {"id": log.id, "operator_id": log.operator_id, "action_type": log.action_type, "from_status": log.from_status, "to_status": log.to_status, "action_remark": log.action_remark, "created_at": log.created_at}
                for log in logs
            ],
        }

    def review(self, db: Session, req):
        case = db.query(RiskCase).filter(RiskCase.id == req.case_id).first()
        if not case:
            raise BizError(NOT_FOUND, "case not found")
        if case.case_status != "pending":
            raise BizError(PARAM_ERROR, f"案件已审核，当前状态: {case.case_status}，不可重复审核")
        old_status = case.case_status
        case.case_status = req.review_result
        case.reviewer_id = req.operator_id
        case.review_result = req.review_result
        case.review_remark = req.review_remark
        db.add(ReviewLog(case_id=case.id, operator_id=req.operator_id, action_type="review", from_status=old_status, to_status=req.review_result, action_remark=req.review_remark))
        db.commit()
        return case_to_dict(case)
