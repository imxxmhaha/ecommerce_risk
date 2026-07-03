from sqlalchemy import BigInteger, Column, DateTime, JSON, func

from app.core.database import Base


class FeatureSnapshot(Base):
    __tablename__ = "feature_snapshots"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    assessment_id = Column(BigInteger, nullable=False, unique=True)
    feature_json = Column(JSON, nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
