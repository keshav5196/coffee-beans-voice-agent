"""Configuration module for CoffeeBeans Voice Agent."""

import os
from pathlib import Path
from dotenv import load_dotenv
from pydantic import Field, AliasChoices
from pydantic_settings import BaseSettings, SettingsConfigDict

# Load environment variables
load_dotenv()


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Groq Configuration (replacing OpenAI)
    groq_api_key: str = Field(..., env='GROQ_API_KEY')
    groq_model: str = Field(default='llama-3.1-70b-versatile', env='GROQ_MODEL')
    
    # Google Cloud Configuration
    google_credentials_path: str = Field(
        default='',
        validation_alias=AliasChoices('GOOGLE_APPLICATION_CREDENTIALS', 'google_application_credentials')
    )
    google_project_id: str = Field(
        default='',
        validation_alias=AliasChoices('GOOGLE_CLOUD_PROJECT_ID', 'google_cloud_project_id')
    )
    google_api_key: str = Field(
        default='',
        validation_alias=AliasChoices('GOOGLE_CLOUD_API_KEY', 'google_cloud_api_key')
    )
    
    # Google Speech Configuration
    google_tts_voice: str = Field(default='en-US-Neural2-D', env='GOOGLE_TTS_VOICE')
    google_stt_language: str = Field(default='en-US', env='GOOGLE_STT_LANGUAGE')
    
    # Twilio Configuration
    twilio_account_sid: str = Field(..., env='TWILIO_ACCOUNT_SID')
    twilio_auth_token: str = Field(..., env='TWILIO_AUTH_TOKEN')
    twilio_phone_number: str = Field(..., env='TWILIO_PHONE_NUMBER')
    
    # Server Configuration
    host: str = Field(default='localhost', env='HOST')
    port: int = Field(default=8000, env='PORT')
    websocket_path: str = Field(default='/media-stream', env='WEBSOCKET_PATH')
    
    # Voice Agent Configuration
    temperature: float = Field(default=0.8, env='TEMPERATURE')
    max_response_tokens: int = Field(default=300, env='MAX_RESPONSE_TOKENS')
    
    # Performance
    enable_streaming: bool = Field(default=True, env='ENABLE_STREAMING')
    
    # Logging
    log_level: str = Field(default='INFO', env='LOG_LEVEL')
    
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        case_sensitive=False,
        extra='ignore'
    )


# Create global settings instance
settings = Settings()
print("Loaded settings fields:", settings.model_dump())

# Ensure required directories exist
BASE_DIR = Path(__file__).parent.parent
LOGS_DIR = BASE_DIR / "logs"
LOGS_DIR.mkdir(exist_ok=True)

# Set Google credentials if path provided
if settings.google_credentials_path and Path(settings.google_credentials_path).exists():
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = settings.google_credentials_path