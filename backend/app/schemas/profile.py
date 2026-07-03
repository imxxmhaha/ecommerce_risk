from pydantic import BaseModel


class UserProfileQuery(BaseModel):
    user_id: str
