from typing import Optional

import aiohttp
import aioredis
from fastapi import FastAPI, Query
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache

from config import settings
from utils import api_get_weather, DegType

app = FastAPI()


@app.get('/forecast')
@cache(expire=60)
async def get_weather(city: str, deg: Optional[str] = Query('c', regex='[cf]')):
    return await api_get_weather(city, DegType.CELSIUS if deg == 'c' else DegType.FAHRENHEIT, app.client_session)


@app.on_event('startup')
async def handle_startup():
    redis = await aioredis.create_redis_pool(settings.REDIS_URL, encoding="utf8")
    FastAPICache.init(RedisBackend(redis), prefix="weather-app-cache")
    app.client_session = aiohttp.ClientSession()


@app.on_event('shutdown')
async def handle_shutdown():
    await app.client_session.close()
