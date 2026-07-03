from sqlalchemy.orm import Session

from app.models.risk_event import RiskEvent


class RiskEventRepo:
    @staticmethod
    def get_by_source_id(db: Session, source_id: str):
        return db.query(RiskEvent).filter(RiskEvent.source_id == source_id).first()

    @staticmethod
    def create(db: Session, **kwargs):
        obj = RiskEvent(**kwargs)
        db.add(obj)
        db.flush()
        return obj
