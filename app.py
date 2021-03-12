from typing import Optional

import aiohttp
import aioredis
from fastapi import FastAPI, Query
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache
from tortoise.contrib.fastapi import register_tortoise
from models import Users, UserPydantic

from config import settings
from utils import api_get_weather, DegType

app = FastAPI()

register_tortoise(
    app,
    config={
        'connections': {
            'default': {
                'engine': 'tortoise.backends.asyncpg',
                'credentials': {
                    'host': settings.PG_HOST,
                    'port': settings.PG_PORT,
                    'user': settings.PG_USER,
                    'password': settings.PG_PASSWORD,
                    'database': settings.PG_DBNAME,
                }
            },
        },
        'apps': {
            'models': {
                'models': ['models'],
                # If no default_connection specified, defaults to 'default'
                'default_connection': 'default',
            }
        }
    },
    generate_schemas=True,
    add_exception_handlers=True,
)


@app.get('/signup')
async def signup():
    pass


@app.get('/auth/token')
async def login():
    pass


@app.get('/forecast')
@cache(expire=60)
async def get_forecast(city: str, deg: Optional[str] = Query('c', regex='[cf]')):
    return await api_get_weather(city, DegType.CELSIUS if deg == 'c' else DegType.FAHRENHEIT, app.client_session)


@app.on_event('startup')
async def handle_startup():
    redis = await aioredis.create_redis_pool(settings.REDIS_URL, encoding="utf8")
    FastAPICache.init(RedisBackend(redis), prefix="weather-app-cache")
    app.client_session = aiohttp.ClientSession()


@app.on_event('shutdown')
async def handle_shutdown():
    await app.client_session.close()
