FROM python:3.10

ENV POETRY_VIRTUALENVS_CREATE false
ENV PYTHONUNBUFFERED 1

WORKDIR /usr/src/app

COPY . /usr/src/app

RUN pip install poetry
RUN poetry lock
RUN poetry install
