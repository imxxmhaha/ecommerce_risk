from pydantic import BaseModel


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    token: str
    token_type: str = "Bearer"


class BootstrapAdminRequest(BaseModel):
    bootstrap_token: str
    username: str
    password: str
    real_name: str
