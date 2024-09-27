FROM python:3.10-slim-buster as app

RUN mkdir -p /app

WORKDIR /app

ADD . /app

RUN pip install -r requirements.txt

