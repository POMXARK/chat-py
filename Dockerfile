ARG PYTHON_VERSION

FROM python:3.10-slim-buster as build

ENV TZ=Europe/Moscow
ENV POETRY_VERSION=1.3.2
ENV PIP_DISABLE_PIP_VERSION_CHECK=on
ENV PIP_NO_CACHE_DIR=off
ENV PYTHONDONTWRITEBYTECODE=on
ENV PYTHONFAULTHANDLER=on
ENV PYTHONUNBUFFERED=on
ENV PIP_DEFAULT_TIMEOUT=100

RUN apt-get update
RUN apt-get install -y --no-install-recommends build-essential gcc curl

WORKDIR /app

RUN pip install "poetry==$POETRY_VERSION"

RUN python -m venv .venv

COPY pyproject.toml .
COPY poetry.lock .

RUN poetry export -f requirements.txt | .venv/bin/pip install -r /dev/stdin


FROM python:3.10-slim

WORKDIR /app

# Install curl for healthchecking
RUN apt-get -y update && apt-get install -y --no-install-recommends curl

RUN groupadd -g 999 python && \
    useradd -r -u 999 -g python python
USER 999

# Copy installed packages
COPY --from=build /app/.venv .venv
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app"
# Copy application
COPY . /app