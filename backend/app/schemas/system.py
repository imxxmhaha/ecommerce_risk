from typing import List, Optional

from pydantic import BaseModel


class SystemUserCreateRequest(BaseModel):
    username: str
    password: str
    real_name: str
    role_codes: List[str]
    status: str = "enabled"


class SystemUserStatusRequest(BaseModel):
    user_id: int
    status: str


class SystemUserPasswordRequest(BaseModel):
    user_id: int
    password: str


class SystemRoleCreateRequest(BaseModel):
    role_code: str
    role_name: str
    description: Optional[str] = None
    permission_codes: List[str] = []
    status: str = "enabled"
