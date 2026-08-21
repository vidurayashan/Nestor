from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
    
    openai_api_key: str
    database_url: str = "sqlite:///./comarking.db"
    upload_dir: Path = Path("./uploads")
    
    # OpenAI models
    whisper_model: str = "whisper-1"
    gpt_model: str = "gpt-4o"
    
    # Processing defaults
    default_frame_interval: int = 25  # seconds
    max_video_frames: int = 50


settings = Settings()

# Ensure upload directory exists
settings.upload_dir.mkdir(parents=True, exist_ok=True)
