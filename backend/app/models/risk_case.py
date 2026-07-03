from sqlalchemy import BigInteger, Column, DateTime, String, Text, func

from app.core.database import Base


class RiskCase(Base):
    __tablename__ = "risk_cases"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    assessment_id = Column(BigInteger, nullable=False, unique=True)
    user_id = Column(String(64), nullable=False)
    order_id = Column(String(64), nullable=True)
    case_status = Column(String(32), nullable=False, default="pending")
    reviewer_id = Column(String(64), nullable=True)
    review_result = Column(Text, nullable=True)
    review_remark = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
