from sqlalchemy import BigInteger, Column, DateTime, DECIMAL, String, func

from app.core.database import Base


class RiskAssessment(Base):
    __tablename__ = "risk_assessments"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    event_id = Column(BigInteger, nullable=False)
    risk_score = Column(DECIMAL(5, 2), nullable=False, default=0)
    risk_level = Column(String(32), nullable=False)
    decision = Column(String(32), nullable=False)
    assessment_status = Column(String(32), nullable=False, default="completed")
    created_at = Column(DateTime, nullable=False, server_default=func.now())
