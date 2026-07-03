from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import require_permission
from app.core.database import get_db
from app.core.response import ok
from app.services.profile_service import ProfileService

router = APIRouter(prefix="/api/risk/users", tags=["profile"])
service = ProfileService()


@router.get("/{user_id}/profile", dependencies=[Depends(require_permission("profile:read"))])
def profile(user_id: str, db: Session = Depends(get_db)):
    return ok(service.get_profile(db, user_id))
