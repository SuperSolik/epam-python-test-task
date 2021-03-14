from typing import Optional

import aiohttp
from aiohttp.client_exceptions import ClientConnectionError, InvalidURL, ClientResponseError
from passlib.hash import bcrypt

from .config import settings
from .models import Users


async def api_get_weather(api_key: str, city: str, units: str, client_session: aiohttp.ClientSession):
    """
    Calls weather API and returns it's JSON response, or {"error": "<error msg>"} if request failed
    :param api_key
    :param city
    :param units
    :param client_session
    :return dict
    """
    url = settings.WEATHER_API_ENDPOINT.format(key=api_key, city=city, units=units)
    try:
        async with client_session.get(url, raise_for_status=True) as resp:
            result = await resp.json()
    except(ClientConnectionError, InvalidURL, ClientResponseError) as e:
        return {"error": str(e)}

    return result


async def authenticate_user(username: str, password: str) -> Optional[Users]:
    """
    Performs authentication for given username and password
    :param username
    :param password
    :return Users: Tortoise model object for authenticated user or None
    """
    user = await Users.get_or_none(username=username)
    if user and bcrypt.verify(password, user.password_hash):
        return user
    return None


async def create_user(username: str, password: str) -> Optional[Users]:
    """
    Creates a user with given username and password
    Stored password is being hashed
    :param username
    :param password
    :return Users: Tortoise model object for created user or None
    """
    existing_user = await Users.get_or_none(username=username)
    if existing_user is None:
        user = await Users.create(username=username, password_hash=bcrypt.hash(password))
        return user
    return None
