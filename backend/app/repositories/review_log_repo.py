from sqlalchemy.orm import Session

from app.models.review_log import ReviewLog


class ReviewLogRepo:
    @staticmethod
    def list_by_case(db: Session, case_id: int):
        return db.query(ReviewLog).filter(ReviewLog.case_id == case_id).order_by(ReviewLog.created_at.asc()).all()

    @staticmethod
    def create(db: Session, **kwargs):
        obj = ReviewLog(**kwargs)
        db.add(obj)
        db.flush()
        return obj
