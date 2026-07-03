from sqlalchemy import BigInteger, Column, DateTime, String, Text, func

from app.core.database import Base


class ReviewLog(Base):
    __tablename__ = "review_logs"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    case_id = Column(BigInteger, nullable=False)
    operator_id = Column(String(64), nullable=False)
    action_type = Column(String(64), nullable=False)
    from_status = Column(String(32), nullable=True)
    to_status = Column(String(32), nullable=True)
    action_remark = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
