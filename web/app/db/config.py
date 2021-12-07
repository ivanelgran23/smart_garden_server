import os

from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    db_url: str = Field(
        f"postgresql://{os.getenv('POSTGRES_USER')}:\
{os.getenv('POSTGRES_PASSWORD')}@database:5432/{os.getenv('POSTGRES_DB')}",
    )


settings = Settings()
