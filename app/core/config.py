from pydantic_settings import BaseSettings # type: ignore

class Settings(BaseSettings):
    APP_NAME: str = "Hiring Assessment System"
    DEBUG: bool = True
    API_V1_STR: str = "/api/v1"
    
    class Config:
        case_sensitive = True

settings = Settings() 