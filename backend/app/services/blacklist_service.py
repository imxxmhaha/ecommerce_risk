from sqlalchemy.orm import Session

from app.core.errors import BizError, CONFLICT, NOT_FOUND
from app.models.blacklist import Blacklist


def blacklist_to_dict(item: Blacklist):
    return {
        "id": item.id,
        "blacklist_type": item.blacklist_type,
        "blacklist_value": item.blacklist_value,
        "remark": item.remark,
        "status": item.status,
        "deleted": item.deleted,
        "created_by": item.created_by,
        "created_at": item.created_at,
        "updated_at": item.updated_at,
    }


class BlacklistService:
    def list_items(self, db: Session, blacklist_type=None, status=None, keyword=None, page=1, page_size=20):
        query = db.query(Blacklist).filter(Blacklist.deleted == 0)
        if blacklist_type:
            query = query.filter(Blacklist.blacklist_type == blacklist_type)
        if status is not None and status != '':
            query = query.filter(Blacklist.status == int(status))
        if keyword:
            query = query.filter(Blacklist.blacklist_value.like(f"%{keyword}%"))
        total = query.count()
        items = query.order_by(Blacklist.updated_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
        return {"items": [blacklist_to_dict(x) for x in items], "total": total, "page": page, "page_size": page_size}

    def create(self, db: Session, req):
        existing = db.query(Blacklist).filter(Blacklist.blacklist_type == req.blacklist_type, Blacklist.blacklist_value == req.blacklist_value, Blacklist.deleted == 0).first()
        if existing:
            raise BizError(CONFLICT, "blacklist already exists")
        item = Blacklist(**req.model_dump(), status=0, deleted=0)
        db.add(item)
        db.commit()
        db.refresh(item)
        return blacklist_to_dict(item)

    def set_status(self, db: Session, item_id: int, status: int):
        item = db.query(Blacklist).filter(Blacklist.id == item_id, Blacklist.deleted == 0).first()
        if not item:
            raise BizError(NOT_FOUND, "blacklist not found")
        item.status = status
        db.commit()
        return blacklist_to_dict(item)

    def delete(self, db: Session, item_id: int):
        item = db.query(Blacklist).filter(Blacklist.id == item_id, Blacklist.deleted == 0).first()
        if not item:
            raise BizError(NOT_FOUND, "blacklist not found")
        item.deleted = 1
        db.commit()
        return {"deleted": True}
