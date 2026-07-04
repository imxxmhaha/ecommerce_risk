from sqlalchemy.orm import Session

from app.models.risk_rule import RiskRule


class RuleRepo:
    @staticmethod
    def enabled_rules(db: Session):
        return db.query(RiskRule).filter(RiskRule.rule_status == 1).order_by(RiskRule.priority.desc(), RiskRule.id.asc()).all()

    @staticmethod
    def get(db: Session, rule_id: int):
        return db.query(RiskRule).filter(RiskRule.id == rule_id).first()
