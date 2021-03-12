from typing import Optional

import aiohttp
import aioredis
from fastapi import FastAPI, Query, HTTPException, status, Depends
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache
from tortoise.contrib.fastapi import register_tortoise

from config import settings
from models import UserPydantic
from utils import api_get_weather, DegType, authenticate_user, create_user

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")
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
                'default_connection': 'default',
            }
        }
    },
    generate_schemas=True,
    add_exception_handlers=True,
)


@app.get('/signup')
async def signup(user_data: UserPydantic):
    user = create_user(user_data.username, user_data.password_hash)
    if not user:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, detail="user already exists")
    return RedirectResponse("/auth/token")


@app.get('/auth/token')
async def login(login_form: OAuth2PasswordRequestForm = Depends()):
    username = login_form.username
    password = login_form.password
    if authenticate_user(username, password):
        return {
            "access_token": "test",
            "token_type": "bearer",
        }
    raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="wrong username or password")


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
