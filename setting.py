# setting.py

from pydantic_settings import BaseSettings
from pydantic import computed_field

class Settings(BaseSettings):
    """
    Application settings class that reads environment variables from .env file.
    """
    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_PORT: int = 5432
    SECRET_KEY: str

    @computed_field
    @property
    def ASYNC_DATABASE_URI(self) -> str:
        """
        Constructs the asynchronous database URI from components.
        """
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    class Config:
        env_file = ".env"

# Create a single instance of the settings to be used throughout the application
settings = Settings()
