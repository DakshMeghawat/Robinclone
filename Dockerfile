FROM python:3.9.13-slim AS base
WORKDIR /app
ADD . /app


RUN pip3 install --trusted-host pypi.python.org Flask pymongo requests


CMD ["python", "app.py"]