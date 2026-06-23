from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    typhoon_api_key: str = Field(default="mock_key")
    typhoon_api_base: str = Field(default="https://api.opentyphoon.ai/v1")
    typhoon_model_vision: str = Field(default="typhoon-v1.5-vision-instruct")
    typhoon_model_text: str = Field(default="typhoon-v1.5-instruct")
    chroma_db_dir: str = Field(default="./chroma_db")
    
    # Allow loading from environment variables or .env file
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
