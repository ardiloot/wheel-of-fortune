FROM node:20.5.0-slim AS node_builder
WORKDIR /app
COPY wheel_of_fortune/frontend/ /app
RUN npm ci
RUN npm run build


FROM python:3.11.4-slim as python_builder
RUN apt-get update \
    && apt-get install -y libglib2.0-0 libasound2 build-essential git --no-install-recommends \
    && rm -rf \
        /tmp/* \
        /var/{cache,log}/* \
        /var/lib/apt/lists/*
WORKDIR /app

ARG PUID=1000
ARG PGID=1000
RUN groupadd -g ${PGID} -o user \
    && useradd -m -u ${PUID} -g user -o -s /bin/bash user \
    && chown -R user:user /app
USER user

COPY --chown=user:user ./ ./
COPY --from=node_builder --chown=user:user /app/dist/ wheel_of_fortune/frontend/dist/
RUN pip install --user --no-cache-dir build \
    && python -m build
RUN pip install --user -r requirements.txt --no-cache-dir
RUN pip install --user --no-cache-dir dist/*.whl


FROM python:3.11.4-slim
WORKDIR /app

RUN apt-get update \
    && apt-get install -y libglib2.0-0 libasound2 --no-install-recommends \
    && rm -rf \
        /tmp/* \
        /var/{cache,log}/* \
        /var/lib/apt/lists/*

ARG PUID=1000
ARG PGID=1000
RUN groupadd -g ${PGID} -o user \
    && groupadd -g 1001 -o gpio \
    && useradd -m -u ${PUID} -g user -G 20,gpio,audio -o -s /bin/bash user \
    && chown -R user:user /app
USER user

COPY --from=python_builder /home/user/.local/ /home/user/.local/

EXPOSE 8000
ENV PYTHONUNBUFFERED=1
CMD python -u -m wheel_of_fortune
