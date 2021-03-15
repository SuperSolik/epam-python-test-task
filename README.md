# epam-python-test-task

## Requirements
Python3.9, PostgreSQL, Redis 

## Setup

**Env variables**

```dotenv
REDIS_URL="redis://your-redis-url"
POSTGRES_HOST="postgres-host"
POSTGRES_USER="postgres-user"
POSTGRES_PASSWORD="postgres-password"
POSTGRES_DB="postgres-db-name"
WEATHER_API_KEY="API key for https://weatherstack.com/"
WEATHER_JWT_SECRET="your-jwt-secret"
```

plus for Docker configuration (useful when deploy to Heroku for exampple)

```dotenv
PORT=<port-inside-docker> 
```

env file also supported:

- `.env` for manual start
- `docker.env` for Docker start

**Databases**
- `test` - for tests  
- `$POSTGRES_DB` - for main app

## Run tests
```python3
pip install -r requirements.txt
python -m pytest
```

## Run app


### Manual

```python3
pip install -r requirements.txt
uvicorn app:app
```

App would be available at http://127.0.0.1:8000 by default, to specify host and port:
```python
uvicorn app:app --host <host> --port <port>
```

### Docker

```python3
docker-compose up -d
```

App would be available at http://127.0.0.1:3030 by default, but it can be changed using docker-compose.yml

### API

`POST /login` login using JSON: `{"username": "<your-username>", {"password": "<your-password>"}`.  
Returns `{"msg": "user created"}` on success or json with details on failure

`POST /auth/token` authorize using form data: `username=<your-username>&password=<your-password>`.  
Returns `{"access_token": "<your-auth-token>", "token_type": "bearere""}` on success or json with details on failure

`GET /forecast` get forecast for specified city, only for authorized users, else returns `401 Not authorized`.  
Returns json with current weather and forecast (for current day, because of the limits of weather API free plan) on
success or json with details on failure. Query params:

* `city` - required, name of the city for weather report
* `units` - required, degrees type for temperature values: m - for Celsius (metric), f - for Fahrenheit (imperial)

`GET /docs` - full automatically generated documentation

