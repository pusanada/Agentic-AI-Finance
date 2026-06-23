import os
from pathlib import Path
from pydantic_settings import BaseSettings

# Base directories
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "esg_data"
PDF_DIR = DATA_DIR / "pdfs"
AUDIO_DIR = DATA_DIR / "audio"
DB_DIR = DATA_DIR / "vector_db"
CACHE_DIR = DATA_DIR / "cache"

# Create directories if they do not exist
PDF_DIR.mkdir(parents=True, exist_ok=True)
AUDIO_DIR.mkdir(parents=True, exist_ok=True)
DB_DIR.mkdir(parents=True, exist_ok=True)
CACHE_DIR.mkdir(parents=True, exist_ok=True)

class Settings(BaseSettings):
    # API Keys
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    TYPHOON_API_KEY: str = os.getenv("TYPHOON_API_KEY", "")
    
    # Paths
    PDF_DIR: Path = PDF_DIR
    AUDIO_DIR: Path = AUDIO_DIR
    DB_DIR: Path = DB_DIR
    CACHE_DIR: Path = CACHE_DIR
    
    # Web scraping settings
    SCRAPING_ENABLED: bool = True
    CACHE_TTL_HOURS: int = 24
    
    # Backend server settings
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    
    # Weight settings for scoring (customizable)
    WEIGHT_CGR: float = 0.30
    WEIGHT_SEC: float = 0.20
    WEIGHT_CVUP_ALIGN: float = 0.30
    WEIGHT_AUDIO_CRED: float = 0.20

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

settings = Settings()
