FROM python:3.11.2-slim

RUN apt-get update \
    && apt-get install -y libglib2.0-0 libasound2 iputils-ping dnsutils net-tools build-essential git htop --no-install-recommends \
    && rm -rf \
        /tmp/* \
        /var/{cache,log}/* \
        /var/lib/apt/lists/*

RUN mkdir /workspace && mkdir /workspace/backend
WORKDIR /workspace/backend

RUN groupadd -g 1000 -o user \
    && groupadd -g 1001 -o gpio \
    && useradd -m -u 1000 -g user -G 20,gpio,audio -o -s /bin/bash user \
    && chown -R user:user /workspace/backend
USER user

COPY requirements.txt setup.py MANIFEST.in ./
RUN pip install --user -r requirements.txt --no-cache-dir

COPY wheel_of_fortune/ wheel_of_fortune/
RUN pip install --user -e . --no-cache-dir

EXPOSE 8000
ENV PYTHONUNBUFFERED=1
CMD python -u -m wheel_of_fortune
