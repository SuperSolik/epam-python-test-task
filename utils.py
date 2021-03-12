from enum import Enum
from enum import auto
from typing import Optional

import aiohttp
from aiohttp.client_exceptions import ClientConnectionError, InvalidURL, ClientResponseError
from fastapi import HTTPException
from passlib.hash import bcrypt

from config import settings
from models import Users


class DegType(Enum):
    CELSIUS = auto(),
    FAHRENHEIT = auto()


async def api_get_weather(city: str, degrees: DegType, client_session: aiohttp.ClientSession) -> Optional[dict]:
    url = settings.WEATHER_API_ENDPOINT.format(key=settings.WEATHER_API_KEY, city=city)
    try:
        async with client_session.get(url, raise_for_status=True) as resp:
            result = await resp.json()
    except(ClientConnectionError, InvalidURL, ClientResponseError) as e:
        raise HTTPException(404, str(e))

    return result


async def authenticate_user(username: str, password: str) -> Optional[Users]:
    user = await Users.get_or_none(username=username)
    if user and bcrypt.verify(password, user.password_hash):
        return user
    return None


async def create_user(username: str, password: str) -> Optional[Users]:
    existing_user = await Users.get_or_none(username=username)
    if existing_user is None:
        user = await Users.create(username=username, password_hash=bcrypt.hash(password))
        print('here')
        return user
    return None
