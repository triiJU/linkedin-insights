from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "LinkedIn Insights Microservice"
    VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Database
    MONGODB_URL: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "linkedin_insights"
    

    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    CACHE_TTL: int = 300
    ENABLE_CACHE: bool = True
    
    # Scraping
    SCRAPER_TIMEOUT: int = 30
    MAX_POSTS_PER_PAGE: int = 20
   
    DEFAULT_PAGE_SIZE: int = 10
    MAX_PAGE_SIZE: int = 100
    
    class Config:
        env_file = ".env"
settings = Settings()
