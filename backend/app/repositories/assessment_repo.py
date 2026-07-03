from sqlalchemy.orm import Session

from app.models.risk_assessment import RiskAssessment


class AssessmentRepo:
    @staticmethod
    def get(db: Session, assessment_id: int):
        return db.query(RiskAssessment).filter(RiskAssessment.id == assessment_id).first()

    @staticmethod
    def create(db: Session, **kwargs):
        obj = RiskAssessment(**kwargs)
        db.add(obj)
        db.flush()
        return obj
