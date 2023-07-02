# multiple stage build

FROM python:3.10.1 as base
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
ENV DOCKER_BUILDKIT=1
WORKDIR /build

FROM base as poetry
RUN pip install poetry==1.5.1
COPY poetry.lock pyproject.toml /build/
RUN poetry export -o requirements.txt

FROM base as build
COPY --from=poetry /build/requirements.txt /tmp/requirements.txt
RUN python -m venv .venv && \
    .venv/bin/pip install 'wheel==0.36.2' && \
    .venv/bin/pip install -r /tmp/requirements.txt

FROM python:3.10.1-slim as runtime
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
WORKDIR /build
ENV PATH=/build/.venv/bin:$PATH
COPY --from=build /build/.venv /build/.venv
COPY . /build