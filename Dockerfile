FROM node:20.5.0-slim AS node_builder
WORKDIR /app
COPY wheel_of_fortune/frontend/package.json wheel_of_fortune/frontend/package-lock.json /app/
RUN npm ci
COPY wheel_of_fortune/frontend/ /app
RUN npm run build


FROM python:3.11.5-slim as python_builder
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

COPY --chown=user:user requirements.txt ./
RUN pip install --user -r requirements.txt --no-cache-dir --no-warn-script-location \
    && pip install --user --no-cache-dir --no-warn-script-location build

COPY --chown=user:user ./ ./
COPY --from=node_builder --chown=user:user /app/dist/ wheel_of_fortune/frontend/dist/
RUN python -m build --wheel \
    && pip install --user --no-cache-dir --no-warn-script-location dist/*.whl


FROM python:3.11.5-slim
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
    && useradd -m -u ${PUID} -g user -G 20,audio -o -s /bin/bash user \
    && chown -R user:user /app
USER user

EXPOSE 8000
ENV PYTHONUNBUFFERED=1

COPY --from=python_builder /home/user/.local/ /home/user/.local/
CMD python -u -m wheel_of_fortune
