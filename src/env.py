from pydantic_settings import BaseSettings
import os


class Settings(BaseSettings):
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str

    class Config:
        env_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.env"))


settings = Settings()
