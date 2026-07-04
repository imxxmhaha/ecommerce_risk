from typing import Optional

from pydantic import BaseModel


class BlacklistCreateRequest(BaseModel):
    blacklist_type: str
    blacklist_value: str
    remark: Optional[str] = None
    created_by: Optional[str] = None


class BlacklistDeleteRequest(BaseModel):
    id: int


class BlacklistStatusRequest(BaseModel):
    id: int
    status: int
