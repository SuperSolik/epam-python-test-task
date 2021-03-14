import asyncio
from typing import Generator

import pytest
from fastapi.testclient import TestClient
from tortoise.contrib.test import finalizer, initializer

from app import app, Users
from app.config import settings


@pytest.fixture(scope='module')
def client() -> Generator:
    # setup test database and test client
    initializer(["app.models"],
                db_url=f'postgres://{settings.PG_USER}:{settings.PG_PASSWORD}@{settings.PG_HOST}:{settings.PG_PORT}/test',
                app_label='app')
    with TestClient(app) as c:
        yield c
    # drop test database
    finalizer()


@pytest.fixture(scope="module")
def event_loop() -> Generator:
    # event loop for running coroutines
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


async def get_user_from_db(username):
    return await Users.get_or_none(username=username)


def test_signup(client: TestClient, event_loop: asyncio.AbstractEventLoop):
    response = client.post("/signup", json={"username": "test", "password": "test"})
    assert response.status_code == 200
    assert response.json() == {'msg': 'user created'}

    user = event_loop.run_until_complete(get_user_from_db(username='test'))
    # usernames are unique, so to check if user is created, we check if user exists
    assert user is not None


def test_duplicate_login(client: TestClient):
    # test db is up for all test cases, so user 'test' is already exists
    response = client.post("/signup", json={"username": "test", "password": "test"})
    assert response.status_code == 422


def test_auth_not_existing_user(client: TestClient):
    response = client.post("/auth/token", data={"username": "not_existing_user", "password": "123"})
    assert response.status_code == 401


def test_auth_wrong_password(client: TestClient):
    response = client.post("/auth/token", data={"username": "test", "password": "not_a_test"})
    assert response.status_code == 401


def test_request_no_auth(client: TestClient):
    response = client.get("/forecast?city=London&units=m")
    assert response.status_code == 401


def test_ok_auth(client: TestClient, event_loop: asyncio.AbstractEventLoop):
    user = event_loop.run_until_complete(get_user_from_db(username='test'))
    response = client.post("/auth/token", data={"username": "test", "password": "test"})
    assert response.status_code == 200
    assert 'access_token' in response.json()


def test_request_auth(client: TestClient):
    auth_data = client.post("/auth/token", data={"username": "test", "password": "test"}).json()
    response = client.get("/forecast?city=London&units=m",
                          headers={'Authorization': f'{auth_data["token_type"]} {auth_data["access_token"]}'})
    assert response.status_code == 200


def test_request_wrong_city(client: TestClient):
    auth_data = client.post("/auth/token", data={"username": "test", "password": "test"}).json()
    response = client.get("/forecast?city=UnknownCity&units=m",
                          headers={'Authorization': f'{auth_data["token_type"]} {auth_data["access_token"]}'})
    assert response.status_code == 404  # api failed to get forecast for this city


def test_request_wrong_units(client: TestClient):
    auth_data = client.post("/auth/token", data={"username": "test", "password": "test"}).json()
    response = client.get("/forecast?city=London&units=wrong_units",
                          headers={'Authorization': f'{auth_data["token_type"]} {auth_data["access_token"]}'})
    assert response.status_code == 422  # units query param validation results in 422
