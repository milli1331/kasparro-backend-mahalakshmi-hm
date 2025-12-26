import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database (We will use a default for local testing)
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://user:password@db:5432/kasparro_db")
    
    # API Keys (You will set these in your environment later)
    COINPAPRIKA_API_KEY: str = os.getenv("COINPAPRIKA_API_KEY", "")
    COINGECKO_API_KEY: str = os.getenv("COINGECKO_API_KEY", "")

settings = Settings()