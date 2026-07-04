from sqlalchemy.orm import Session

from app.models.blacklist import Blacklist


class BlacklistRepo:
    @staticmethod
    def active_match(db: Session, blacklist_type: str, blacklist_value: str):
        if not blacklist_value:
            return None
        return db.query(Blacklist).filter(
            Blacklist.blacklist_type == blacklist_type,
            Blacklist.blacklist_value == str(blacklist_value),
            Blacklist.status == 1,
            Blacklist.deleted == 0,
        ).first()
