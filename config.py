import os
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseSettings

PROJECT_DIR = Path(__file__).absolute().parent
ENV_PATH = PROJECT_DIR / ".env"
load_dotenv(dotenv_path=ENV_PATH, verbose=True)


class Settings(BaseSettings):
    WEATHER_API_ENDPOINT = "https://api.weatherapi.com/v1/forecast.json?key={key}&q={city}&days=3&aqi=no&alerts=no"
    WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
    REDIS_URL = os.getenv("REDIS_URL") or "redis://localhost"
    PG_HOST = os.getenv("PG_HOST")
    PG_PORT = os.getenv("PG_PORT") or "5432"
    PG_PASSWORD = os.getenv("PG_PASSWORD")
    PG_USER = os.getenv("PG_USER")
    PG_DBNAME = os.getenv("PG_DBNAME") or "weather_app_db"
    JWT_SECRET = os.getenv("WEATHER_JWT_SECRET")


settings = Settings()
