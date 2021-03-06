from functools import wraps
from typing import Optional

import aiohttp
import aioredis
import jwt
from fastapi import FastAPI, Query, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache
from tortoise.contrib.fastapi import register_tortoise

from .config import settings
from .models import UserPydantic, Users, UserLoginModel, MsgResponseModel, LoginResponseModel
from .utils import api_get_weather, authenticate_user, create_user

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=['HS256'])
        user = await Users.get(id=payload.get('id'))
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid username or password'
        )

    return await UserPydantic.from_tortoise_orm(user)


def base_exception_handler(view):
    """Base exception handler to prevent server internal error from unhandled exceptions"""

    @wraps(view)
    async def wrapper(*args, **kwargs):
        try:
            res = await view(*args, **kwargs)
        except HTTPException:
            # HTTPException is handled by FastAPI, resulting in response with error details
            raise
        except Exception as e:
            # Using  HTTPException to create response with error details
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        return res

    return wrapper


@app.post('/signup', response_model=MsgResponseModel)
@base_exception_handler
async def signup(user_data: UserLoginModel):
    """
    Creates a new user with provided username and password
    """
    user = await create_user(user_data.username, user_data.password)
    if not user:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, detail="user already exists")

    return MsgResponseModel(msg="user created")


@app.post('/login', response_model=LoginResponseModel)
@base_exception_handler
async def login(login_form: OAuth2PasswordRequestForm = Depends()):
    """
    Performs login with username and password, returns access_token
    """
    username = login_form.username
    password = login_form.password
    authenticated_user = await authenticate_user(username, password)
    if authenticated_user:
        payload = {
            'id': authenticated_user.id,
            'username': authenticated_user.username
        }

        token = jwt.encode(payload, settings.JWT_SECRET, algorithm="HS256")

        return LoginResponseModel(access_token=token, token_type="bearer")

    raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")


@app.get('/forecast')
@base_exception_handler
@cache(expire=60)
async def get_forecast(city: str, units: Optional[str] = Query(..., regex='^[mf]$'),
                       current_user: UserPydantic = Depends(get_current_user)):
    """
    Returns weather forecast JSON for specified city,
    with temperature in Celsius (units=m) or Fahrenheit (units=f)
    """
    # current_user injection for preventing non-authenticated requests
    result = await api_get_weather(settings.WEATHER_API_KEY, city, units, app.client_session)
    error_msg = result.get('error')
    if error_msg:
        raise HTTPException(404, detail=error_msg)
    return result


@app.on_event('startup')
async def handle_startup():
    """Setup redis cache and client session for weather API requests"""
    redis = await aioredis.create_redis_pool(settings.REDIS_URL, encoding="utf8")
    FastAPICache.init(RedisBackend(redis), prefix="weather-app-cache")
    app.client_session = aiohttp.ClientSession()


@app.on_event('shutdown')
async def handle_shutdown():
    """Cleanup client session"""
    await app.client_session.close()


# setup Postgres database and Tortoise ORM
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
                'models': ['app.models'],
                'default_connection': 'default',
            }
        }
    },
    generate_schemas=True,
    add_exception_handlers=True,
)
