import os
from pathlib import Path
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load root .env
root_dir = Path(__file__).resolve().parent.parent.parent.parent
env_path = root_dir / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)


class Settings(BaseSettings):
    PROJECT_NAME: str = "OmniSpec AI"
    PROJECT_TAGLINE: str = "Autonomous Product Intelligence for Industrial Commerce"
    API_V1_STR: str = "/api/v1"
    
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL_NAME: str = os.getenv("OPENAI_MODEL_NAME", "gpt-4o-mini")
    
    PORT: int = int(os.getenv("PORT", 8000))
    HOST: str = os.getenv("HOST", "0.0.0.0")
    
    ROOT_DIR: Path = root_dir
    DOCS_DIR: Path = root_dir / "docs"
    DATASET_DIR: Path = root_dir / "docs" / "dataset"
    DATA_DIR: Path = root_dir / "data"
    
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    class Config:
        case_sensitive = True


settings = Settings()
