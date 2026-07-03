from sqlalchemy import BigInteger, Column, DateTime, JSON, String, func

from app.core.database import Base


class RiskEvent(Base):
    __tablename__ = "risk_events"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    event_type = Column(String(64), nullable=False)
    source_id = Column(String(64), nullable=False, unique=True)
    user_id = Column(String(64), nullable=False)
    order_id = Column(String(64), nullable=True)
    event_payload_json = Column(JSON, nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
