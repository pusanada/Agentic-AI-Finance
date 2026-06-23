from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

# Base directories for ESG analyst data
BASE_DIR = Path(__file__).resolve().parent.parent
ESG_DATA_DIR = BASE_DIR / "esg_data"
ESG_PDF_DIR = ESG_DATA_DIR / "pdfs"
ESG_AUDIO_DIR = ESG_DATA_DIR / "audio"
ESG_DB_DIR = ESG_DATA_DIR / "vector_db"
ESG_CACHE_DIR = ESG_DATA_DIR / "cache"

# Create directories if they do not exist
ESG_PDF_DIR.mkdir(parents=True, exist_ok=True)
ESG_AUDIO_DIR.mkdir(parents=True, exist_ok=True)
ESG_DB_DIR.mkdir(parents=True, exist_ok=True)
ESG_CACHE_DIR.mkdir(parents=True, exist_ok=True)

class Settings(BaseSettings):
    typhoon_api_key: str = Field(default="mock_key")
    typhoon_api_base: str = Field(default="https://api.opentyphoon.ai/v1")
    typhoon_model_vision: str = Field(default="typhoon-v1.5-vision-instruct")
    typhoon_model_text: str = Field(default="typhoon-v1.5-instruct")
    chroma_db_dir: str = Field(default="./chroma_db")
    esg_analyst_api_url: str = Field(default="http://localhost:8001")
    
    # ESG Analyst specific configurations
    anthropic_api_key: str = Field(default="", validation_alias="ANTHROPIC_API_KEY")
    esg_pdf_dir: Path = Field(default=ESG_PDF_DIR)
    esg_audio_dir: Path = Field(default=ESG_AUDIO_DIR)
    esg_db_dir: Path = Field(default=ESG_DB_DIR)
    esg_cache_dir: Path = Field(default=ESG_CACHE_DIR)
    
    scraping_enabled: bool = Field(default=True, validation_alias="SCRAPING_ENABLED")
    cache_ttl_hours: int = Field(default=24, validation_alias="CACHE_TTL_HOURS")
    
    weight_cgr: float = Field(default=0.30)
    weight_sec: float = Field(default=0.20)
    weight_cvup_align: float = Field(default=0.30)
    weight_audio_cred: float = Field(default=0.20)
    
    # Allow loading from environment variables or .env file
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()

