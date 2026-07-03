from sqlalchemy import BigInteger, Column, DateTime, DECIMAL, Integer, JSON, String, Text, func

from app.core.database import Base


class RiskRule(Base):
    __tablename__ = "risk_rules"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    rule_code = Column(String(64), nullable=False, unique=True)
    rule_name = Column(String(128), nullable=False)
    rule_status = Column(String(32), nullable=False, default="enabled")
    priority = Column(Integer, nullable=False, default=100)
    score = Column(DECIMAL(5, 2), nullable=False, default=0)
    condition_json = Column(JSON, nullable=False)
    description = Column(Text, nullable=True)
    hit_count = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
