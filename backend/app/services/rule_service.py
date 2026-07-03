from sqlalchemy.orm import Session

from app.core.errors import BizError, CONFLICT, NOT_FOUND, RULE_VALIDATE_ERROR
from app.models.risk_rule import RiskRule
from app.models.rule_hit import RuleHit
from app.services.feature_service import ALLOWED_FEATURES
from app.services.rule_engine import RuleEngine


def rule_to_dict(rule: RiskRule, effective_hit_count=None):
    return {
        "id": rule.id,
        "rule_code": rule.rule_code,
        "rule_name": rule.rule_name,
        "rule_status": rule.rule_status,
        "priority": rule.priority,
        "score": float(rule.score),
        "condition_json": rule.condition_json,
        "description": rule.description,
        "hit_count": effective_hit_count if effective_hit_count is not None else rule.hit_count,
        "created_at": rule.created_at,
        "updated_at": rule.updated_at,
    }


class RuleService:
    def __init__(self):
        self.engine = RuleEngine()

    def enabled_rules(self, db: Session):
        return db.query(RiskRule).filter(RiskRule.rule_status == "enabled").order_by(RiskRule.priority.desc(), RiskRule.id.asc()).all()

    def list_rules(self, db: Session, rule_status=None, keyword=None, page=1, page_size=20):
        query = db.query(RiskRule)
        if rule_status:
            query = query.filter(RiskRule.rule_status == rule_status)
        if keyword:
            like = f"%{keyword}%"
            query = query.filter((RiskRule.rule_name.like(like)) | (RiskRule.rule_code.like(like)))
        total = query.count()
        items = query.order_by(RiskRule.updated_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
        rule_ids = [item.id for item in items]
        hit_counts = {}
        if rule_ids:
            rows = db.query(RuleHit.rule_id, RiskRule.rule_status).join(RiskRule, RuleHit.rule_id == RiskRule.id).filter(RuleHit.rule_id.in_(rule_ids)).all()
            for rule_id, status in rows:
                if status == "enabled":
                    hit_counts[rule_id] = hit_counts.get(rule_id, 0) + 1
        return {"items": [rule_to_dict(x, hit_counts.get(x.id, 0) if x.rule_status == "enabled" else 0) for x in items], "total": total, "page": page, "page_size": page_size}

    def create_rule(self, db: Session, req):
        if db.query(RiskRule).filter(RiskRule.rule_code == req.rule_code).first():
            raise BizError(CONFLICT, "rule_code already exists")
        validation = self.engine.validate_condition(req.condition_json, ALLOWED_FEATURES)
        if not validation.passed:
            raise BizError(RULE_VALIDATE_ERROR, "; ".join(validation.errors))
        rule = RiskRule(**req.model_dump())
        db.add(rule)
        db.commit()
        db.refresh(rule)
        return rule_to_dict(rule)

    def update_rule(self, db: Session, req):
        rule = db.query(RiskRule).filter(RiskRule.id == req.id).first()
        if not rule:
            raise BizError(NOT_FOUND, "rule not found")
        data = req.model_dump(exclude_unset=True)
        data.pop("id", None)
        if "condition_json" in data:
            validation = self.engine.validate_condition(data["condition_json"], ALLOWED_FEATURES)
            if not validation.passed:
                raise BizError(RULE_VALIDATE_ERROR, "; ".join(validation.errors))
        for key, value in data.items():
            setattr(rule, key, value)
        db.commit()
        db.refresh(rule)
        return rule_to_dict(rule)

    def set_status(self, db: Session, req):
        rule = db.query(RiskRule).filter(RiskRule.id == req.id).first()
        if not rule:
            raise BizError(NOT_FOUND, "rule not found")
        rule.rule_status = req.rule_status
        db.commit()
        return rule_to_dict(rule)

    def delete_rule(self, db: Session, rule_id: int):
        rule = db.query(RiskRule).filter(RiskRule.id == rule_id).first()
        if not rule:
            raise BizError(NOT_FOUND, "rule not found")
        db.delete(rule)
        db.commit()
        return {"deleted": True}
