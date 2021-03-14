# epam-python-test-task

## Requirements
Python3.9, PostgreSQL, Redis 

## Run tests
```python3
pip install -r requirements.txt
python -m pytest
```

## Run app
### Environment variables

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

Or use env file to setup:
- `.env` for manual start
- `docker.env` for Docker start 


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

