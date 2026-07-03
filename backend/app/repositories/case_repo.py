from sqlalchemy.orm import Session

from app.models.risk_case import RiskCase


class CaseRepo:
    @staticmethod
    def get(db: Session, case_id: int):
        return db.query(RiskCase).filter(RiskCase.id == case_id).first()

    @staticmethod
    def create(db: Session, **kwargs):
        obj = RiskCase(**kwargs)
        db.add(obj)
        db.flush()
        return obj
