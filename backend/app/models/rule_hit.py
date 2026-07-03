from sqlalchemy import BigInteger, Column, DateTime, DECIMAL, Text, func

from app.core.database import Base


class RuleHit(Base):
    __tablename__ = "rule_hits"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    assessment_id = Column(BigInteger, nullable=False)
    rule_id = Column(BigInteger, nullable=False)
    hit_score = Column(DECIMAL(5, 2), nullable=False, default=0)
    hit_message = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
