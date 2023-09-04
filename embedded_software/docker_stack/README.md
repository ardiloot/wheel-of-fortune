
# Docker Stack for Wheel of Fortune

## Overview

This docker-compose stack provides a convenient way to run the Wheel of Fortune software on embedded computers, such as OrangePi 3 LTS. The stack consists of two containers:
  1. **Wheel of Fortune Container**: This container includes the Wheel of Fortune software.
  2. **Traefik Container**: Traefik is utilized as a reverse proxy to expose the user interface (UI) and the WLED interface. Traefik also provides authentication via Basic HTTP authentication.

## Usage

### Data folder

Copy example data from `wheel-of-fortune/example-data` to `~/data/wheel-of-fortune`. Make necessary changes to the data files.

### Docker stack

Copy/Link `wheel-of-fortune/embedded_software/docker_stack` to `~/docker_stack`.

Add `~/docker_stack/.env` file using following example:

```bash
DOMAIN_NAME=wheel.example.com
DATA_DIR=/home/orangepi/data

# Variables for Letsencrypt ACME DNS challenge (Cloudflare in this example)
LETSENCRYPT_EMAIL=
CLOUDFLARE_EMAIL=
CLOUDFLARE_DNS_API_TOKEN=

# Wheel of Fortune configuration
WHEEL_NAME=test-wheel
WHEEL_DISPLAY_NAME="Wheel of Fortune"
WHEEL_WLED_URL=
WHEEL_WLED_SEGMENTS='[
    {"name": "ambilight", "start": 0, "stop": 133},
    {"name": "logo", "start": 133, "stop": 170},
    {"name": "wheel", "start": 170, "stop": 205}
]'

# Wheel influxdb metrics
WHEEL_INFLUXDB_URL=https://influxdb.int.example.com
WHEEL_INFLUXDB_TOKEN=
WHEEL_INFLUXDB_ORG=wheelmetrics
WHEEL_INFLUXDB_BUCKET=wheel-of-fortune

# Traefik influxdb metrics
TRAEFIK_INFLUXDB_URL=https://influxdb.int.example.com
TRAEFIK_INFLUXDB_TOKEN=
TRAEFIK_INFLUXDB_ORG=wheelmetrics
TRAEFIK_INFLUXDB_BUCKET=traefik
```

Fill in any missing values and/or make necessary changes to `docker-compose.yml` file.

Add `usersfile` to `config/traefik` folder to list Basic Auth users.
For more information see https://doc.traefik.io/traefik/middlewares/http/basicauth/#usersfile

### Deploy

Start docker stack by

```bash
cd ~/docker_stack
docker compose up -d
```

