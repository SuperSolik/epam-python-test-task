import aiohttp
import pytest

from app import api_get_weather
from app.config import settings as test_settings


@pytest.fixture
@pytest.mark.asyncio
async def client_session():
    session = aiohttp.ClientSession()
    yield session
    await session.close()


@pytest.mark.asyncio
async def test_celsius(client_session):
    # ok request for celsius degrees
    res = await api_get_weather(test_settings.WEATHER_API_KEY, 'London', 'm', client_session)
    assert 'error' not in res


@pytest.mark.asyncio
async def test_fahrenheit(client_session):
    # ok request for fahrenheit degrees
    res = await api_get_weather(test_settings.WEATHER_API_KEY, 'London', 'f', client_session)
    assert 'error' not in res


@pytest.mark.asyncio
async def test_bad_units(client_session):
    # bad request: unsupported degrees type
    res = await api_get_weather(test_settings.WEATHER_API_KEY, 'London', 'some_units', client_session)
    assert 'error' in res


@pytest.mark.asyncio
async def test_bad_city(client_session):
    # bad request: city name doesn't exist
    res = await api_get_weather(test_settings.WEATHER_API_KEY, '12j3i1l23n123', 'm', client_session)
    assert 'error' in res


@pytest.mark.asyncio
async def test_bad_city_and_units(client_session):
    res = await api_get_weather(test_settings.WEATHER_API_KEY, 'UnknownCity', 'some_units', client_session)
    assert 'error' in res
