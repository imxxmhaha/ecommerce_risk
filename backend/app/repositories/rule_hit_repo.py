from sqlalchemy.orm import Session

from app.models.rule_hit import RuleHit


class RuleHitRepo:
    @staticmethod
    def list_by_assessment(db: Session, assessment_id: int):
        return db.query(RuleHit).filter(RuleHit.assessment_id == assessment_id).all()

    @staticmethod
    def create(db: Session, **kwargs):
        obj = RuleHit(**kwargs)
        db.add(obj)
        db.flush()
        return obj
