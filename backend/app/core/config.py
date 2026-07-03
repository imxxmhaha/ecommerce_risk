from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    db_host: str = Field("localhost", alias="DB_HOST")
    db_port: int = Field(3306, alias="DB_PORT")
    db_user: str = Field("root", alias="DB_USER")
    db_password: str = Field("123456", alias="DB_PASSWORD")
    db_name: str = Field("ecommerce_risk_control", alias="DB_NAME")
    ai_mock: bool = Field(True, alias="AI_MOCK")
    llm_api_key: str = Field("", alias="LLM_API_KEY")
    auth_secret: str = Field("ecommerce-risk-control-demo-secret", alias="AUTH_SECRET")
    access_token_expire_minutes: int = Field(480, alias="ACCESS_TOKEN_EXPIRE_MINUTES")
    bootstrap_admin_token: str = Field("", alias="BOOTSTRAP_ADMIN_TOKEN")

    class Config:
        env_file = ".env"
        populate_by_name = True

    @property
    def database_url(self) -> str:
        return (
            f"mysql+pymysql://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}?charset=utf8mb4"
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()
