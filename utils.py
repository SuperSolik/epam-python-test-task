from enum import Enum
from enum import auto
from logging import getLogger

import aiohttp
from aiohttp.client_exceptions import ClientConnectionError, InvalidURL, ClientResponseError
from fastapi import HTTPException

from config import settings

log = getLogger(__name__)


class DegType(Enum):
    CELSIUS = auto(),
    FAHRENHEIT = auto()


async def api_get_weather(city: str, degrees: DegType, client_session: aiohttp.ClientSession):
    url = settings.WEATHER_API_ENDPOINT.format(key=settings.WEATHER_API_KEY, city=city)
    try:
        async with client_session.get(url, raise_for_status=True) as resp:
            result = await resp.json()
    except(ClientConnectionError, InvalidURL, ClientResponseError) as e:
        raise HTTPException(404, str(e))

    return result
