from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # API Keys
    NEWS_API_KEY: str
    
    # Risk Parameters
    RISK_FREE_RATE: float = 0.045
    
    # Broker Credentials
    WEALTHSIMPLE_CLIENT_ID: Optional[str] = None
    WEALTHSIMPLE_CLIENT_SECRET: Optional[str] = None
    
    QUESTRADE_CLIENT_ID: Optional[str] = None
    QUESTRADE_REFRESH_TOKEN: Optional[str] = None
    
    IBKR_CLIENT_ID: Optional[str] = None
    IBKR_CLIENT_SECRET: Optional[str] = None
    
    # Server Config
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
