# (Metrics) server setup

## Overview

The aim of this server is to collect logs & telemetry and provide VPN network for Wheel of Fortune:

1.  Server for logs (Loki)
2.  Server for storing telemetry (Influx)
3.  Dashboards for logs and telemetry (Grafana)
4.  VPN network for remote access (WireGuard)

Following services are exposed through Traefik reverse proxy:

- https://traefik.int.example.com - Traefik internal dashboard (basic HTTP auth)
- https://influxdb.int.example.com - Influxdb admin panel
- https://loki.int.example.com - Loki API
- https://grafana.int.example.com - Grafana dashboards
- https://librespeed.int.example.com - Speedtest for testing connection

Throughout this document, `example.com` is use as a example domain name. All services are accessible only over VPN.

## Setup compute instance

One option is to use Oracle Cloud free instance:

- Instance name: wheelmetrics
- Shape: ARM Ampere A1 (VM.Standard.A1.Flex), 1 OCPU, 6 GB RAM
- Image: Canonical Ubuntu 22.04 Minimal aarch64
- Networking: public IPv4 address
- SSH keys: add your public SSH key
- Boot volume: 47 GB

Could use any other cloud provider or local compute.

## Setup domain name

Setup DNS A-type records to point your domain name (`example.com`) to public IP (`a.b.c.d`) of the instance:

```
a.b.c.d     A       example.com
a.b.c.d     A       *.example.com
```

## Setup firewall

Follow steps: https://www.digitalocean.com/community/tutorials/how-to-set-up-a-firewall-with-ufw-on-ubuntu-22-04

## Setup VPN

Follow steps from [Digital Ocean](https://www.digitalocean.com/community/tutorials/how-to-set-up-wireguard-on-ubuntu-22-04) tutorial.

Remember to allow WireGuard port (`51820/udp`) through firewall(s) and allow traffic from developer VPN clients to Wheel of Fortune for remote access:

```bash
sudo ufw allow 51820/udp
sudo ufw route allow in on wg0 out on wg0 to 192.168.241.2
```

As an example, WireGuard could use subnet `192.168.241.0/24`:

1. `192.168.241.1` - current server
2. `192.168.241.2` - Wheel of Fortune (OrangePi)
3. `192.168.241.3` - developer access #1
4. `192.168.241.4` - developer access #2
5. ...

Add DNS records for the server (`int.example.com`) and for Wheel of Fortune VPN ip-address (`wheel.int.example.com`):

```dns
int.example.com             A   192.168.241.1
*.int.example.com           A   192.168.241.1
wheel.int.example.com       A   192.168.241.2
*.wheel.int.example.com     A   192.168.241.2
```

Subdomain `*.int.example.com` correspond to resources accessible over VPN (everything in this case).

## Install docker engine:

Follow steps in: [Installing docker on Ubuntu](https://docs.docker.com/engine/install/ubuntu)

Redirect logging to `journald` for easier scaping by promtail. Create file

```bash
sudo nano /etc/docker/daemon.json
```

with contents

```json
{
   "log-driver": "journald"
}
```

## Setup metrics stack

Clone repository:

```bash
cd ~
git clone https://github.com/ardiloot/wheel-of-fortune.git
```

Copy environment file from the example and fill in values :

```bash
cd ~/wheel-of-fortune/server/metrics
cp env.example .env
nano .env
```

PS: `TELEGRAF_INFLUXDB_*` variables can be filled in later

Start metrics stack:

```bash
docker compose up -d
```

If getting permission errors from Grafana or Loki, run to fix permissions:

```bash
sudo chown 10001:10001  ~/data/loki/
sudo chown 472:472  ~/data/grafana/
```

## Configure influxdb

https://influxdb.int.example.com/

Initial setup:

- Username: admin
- Organization: wheelmetrics
- Bucket name: telegraf

API token for telegraf: (Generate API token -> Custom API token)

- Description: Server's telegraf write token
- Permissions: Add write permissions to telegraf bucket

Create bucket for Wheel of Fortune telemetry: (Buckets -> Create bucket)

- Name: wheel-of-fortune

API token for Wheel of Fortune: (Generate API token -> Custom API token)

- Description: Wheel of Fortune write token
- Permissions: Add write permissions to wheel-of-fortune bucket

Create bucket for Traefik telemetry: (Buckets -> Create bucket)

- Name: traefik

API token for Traefik: (Generate API token -> Custom API token)

- Description: Traefik write token
- Permissions: Add write permissions to traefik bucket

API token for Grafana: (Generate API token -> Custom API token)

- Description: Grafana read all token
- Permissions: Read all buckets

Add generated telegraf token to `.env` file (`TELEGRAF_INFLUXDB_TOKEN`) and restart docker stack `docker compose up -d`.

## Configure Grafana

https://grafana.int.example.com

Default user/password: admin/admin

Add telegraf data source: Administration -> Data sources -> Add data source -> InfluxDB:

- Name: Telegraf
- Query language: InfluxQL
- URL: http://influxdb:8086
- Custom HTTP Headers, select Add Header. Set header to `Authorization` and value to `Token [token]` (previously generated read Token for Grafana)
- Database: telegraf

Add Wheel of Fortune data source: Administration -> Data sources -> Add data source -> InfluxDB:

- Name: Wheel of Fortune
- Query language: InfluxQL
- URL: http://influxdb:8086
- Custom HTTP Headers, select Add Header. Set header to `Authorization` and value to `Token [token]` (previously generated read Token for Grafana)
- Database: wheel-of-fortune

Add Traefik data source: Administration -> Data sources -> Add data source -> InfluxDB:

- Name: Traefik
- Query language: InfluxQL
- URL: http://influxdb:8086
- Custom HTTP Headers, select Add Header. Set header to `Authorization` and value to `Token [token]` (previously generated read Token for Grafana)
- Database: traefik

Add dashboards for Telegraf metrics. For example: https://grafana.com/grafana/dashboards/928-telegraf-system-dashboard/

Add Loki data source: Administration -> Data sources -> Add data source -> Loki:

- Name: Loki
- URL: http://loki:3100

## Configure kopia

For the first start, add `--tls-generate-cert` option to the command to automatically generate TLS certs.

Create repository:

```bash
docker exec -it kopia kopia repository create filesystem --path=/repository
```

Add user for Wheel of Fortune:

```bash
docker exec -it kopia kopia server user add root@wheel-of-fortune
```

Dashboard is located at https://int.example.com:51515
