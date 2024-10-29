FROM pytorch/pytorch:2.0.1-cuda11.7-cudnn8-runtime

ENV TZ=UTC DEBIAN_FRONTEND=noninteractive

WORKDIR /app

ENV POETRY_VERSION=1.8.3

RUN pip install --no-cache-dir poetry==${POETRY_VERSION}

ENV POETRY_CACHE_DIR=/tmp/poetry_cache
ENV POETRY_NO_INTERACTION=1
ENV POETRY_VIRTUALENVS_IN_PROJECT=true
ENV POETRY_VIRTUALENVS_CREATE=true
ENV POETRY_REQUESTS_TIMEOUT=15

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc g++ libc-dev libffi-dev libgmp-dev libmpfr-dev libmpc-dev \
    ffmpeg \
    sox

RUN apt clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

COPY ./viettts /app/viettts
COPY ./samples /app/samples
COPY ./web /app/web
COPY ./pyproject.toml /app/
COPY ./README.md /app/

RUN pip install -e . && pip cache purge