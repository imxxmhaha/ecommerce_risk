from sqlalchemy.orm import Session

from app.models.feature_snapshot import FeatureSnapshot


class FeatureSnapshotRepo:
    @staticmethod
    def get_by_assessment(db: Session, assessment_id: int):
        return db.query(FeatureSnapshot).filter(FeatureSnapshot.assessment_id == assessment_id).first()

    @staticmethod
    def create(db: Session, **kwargs):
        obj = FeatureSnapshot(**kwargs)
        db.add(obj)
        db.flush()
        return obj
