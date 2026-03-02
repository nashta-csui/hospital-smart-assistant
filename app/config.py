from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = Field(
        default="sqlite:///./hospital.db",
        description="Database URL untuk SQLAlchemy"
    )

settings = Settings()
