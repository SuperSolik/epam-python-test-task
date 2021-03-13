FROM python:3.9-slim-buster

RUN apt-get update && apt-get upgrade -y && apt-get install -y build-essential

WORKDIR /weather_app

COPY ./requirements.txt /weather_app/requirements.txt
RUN pip install -U pip setuptools && pip install -r /weather_app/requirements.txt

COPY app /weather_app/app

CMD gunicorn app:app --bind=0.0.0.0:$PORT -w 4 -k uvicorn.workers.UvicornH11Worker