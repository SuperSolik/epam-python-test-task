import os

from pydantic import BaseSettings


class Settings(BaseSettings):
    WEATHER_API_ENDPOINT = "https://api.weatherapi.com/v1/forecast.json?key={key}&q={city}&days=3&aqi=no&alerts=no"
    WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
    REDIS_URL = os.getenv("REDIS_URL")


settings = Settings()
