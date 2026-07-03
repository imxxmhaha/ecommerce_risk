from sqlalchemy import BigInteger, Column, DateTime, String, Text, func

from app.core.database import Base


class Blacklist(Base):
    __tablename__ = "blacklists"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    blacklist_type = Column(String(64), nullable=False)
    blacklist_value = Column(String(128), nullable=False)
    remark = Column(Text, nullable=True)
    status = Column(String(32), nullable=False, default="active")
    created_by = Column(String(64), nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
