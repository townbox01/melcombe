
from dotenv import load_dotenv
load_dotenv()  # must be before settings = Settings()
from pydantic_settings import BaseSettings
import os



class Settings(BaseSettings):
    DATABASE_URL: str
    GOOGLE_API_KEY: str
    CLOCKIN_RADIUS_METERS: float = 100

    class Config:
        env_file = ".env"

settings = Settings()




BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")

# Ensure directory exists at startup
os.makedirs(UPLOAD_DIR, exist_ok=True)



