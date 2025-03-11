from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

load_dotenv()


class Settings(BaseSettings):
    database_url: str
    openai_secret_key: str
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int
    refresh_token_expire_days: int
    verification_token_expire_hours: int

    class Config:
        env_file = ".env"
        extra = "allow"


settings = Settings()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

