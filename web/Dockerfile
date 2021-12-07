# Dockerfile

# pull the official docker image
FROM tiangolo/uvicorn-gunicorn:python3.8-slim

# set work directory
WORKDIR /app

RUN apt-get update && apt-get install -y netcat

# install dependencies
COPY requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt

# copy project
COPY . .