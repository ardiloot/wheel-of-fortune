
# (Metrics) server setup

## Overview

The aim of this server is to collect logs & telemetry and provide VPN network for Wheel of Fortune:
 1. Server for logs (Loki)
 2. Server for storing telemetry (Influx)
 3. Dashboards for logs and telemetry (Grafana)
 4. VPN network for remote access (WireGuard)

Following services are exposed through Traefik reverse proxy:
  * https://traefik.int.example.com - Traefik internal dasboard (basic HTTP auth)
  * https://influxdb.int.example.com - Influxdb admin panel
  * https://loki.int.example.com - Loki API
  * https://grafana.int.example.com - Grafana dashboards
  * https://librespeed.int.example.com - Speedtest for testing connection

Throughout this document, `example.com` is use as a example domain name.

## Setup compute instance

One option is to use Oracle Cloud free instance:

  * Instance name: wheelmetrics
  * Shape: ARM Ampere A1 (VM.Standard.A1.Flex), 1 OCPU, 6 GB RAM
  * Image: Canonical Ubuntu 22.04 Minimal aarch64
  * Networking: public IPv4 address
  * SSH keys: add your public SSH key
  * Boot volume: 47 GB
  
Could use any other cloud provider or local compute.

## Setup domain name

Setup DNS A-type records to point your domain name (`example.com`) to public IP (`a.b.c.d`) of the instance:

```
a.b.c.d     A       example.com
a.b.c.d     A       *.example.com
```

## Install docker engine:

Follow steps in: [Installing docker on Ubuntu](https://docs.docker.com/engine/install/ubuntu)

## Setup VPN

Follow steps from [Digital Ocean](https://www.digitalocean.com/community/tutorials/how-to-set-up-wireguard-on-ubuntu-22-04) tutorial.

Remember to allow WireGuard port (`51820/udp`) through firewall and allow traffic from developer VPN clients to Wheel of Fourtune for remote access.

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
```

Subdomain `*.int.example.com` correspond to resources accesible over VPN.

## Setup metrics stack

Download / Clone metrics stack to `/docker/stacks`:

```bash
cd ~
git clone https://github.com/ardiloot/wheel-of-fortune.git

```

Copy environment file from the example and fill in values:
```bash
cd ~/docker/stacks/metrics
cp env.example .env
nano .env
```

Start stack:
```bash
docker compose up -d
```

## Configure influxdb

https://influxdb.int.example.com/

Username: admin
Organization: wheelmetrics
Bucket name: telegraf

Add API token for telegraf: Generate API token -> Custom API token 
  * Description: Server's telegraf write token
  * Permissions: Add write permissions to telegraf bucket
Add generated token to `.env` file.

Add API token for Grafana: Generate API token -> Custom API token 
  * Description: Grafana all read
  * Permissions: Read all buckets.


## Configure Grafana

https://grafana.int.example.com

Default user/password: admin/admin

Add influxdb data source: Administration -> Data sources -> Add data source -> InfluxDB:
  * Name: Telegraf
  * Query language: InfluxQL
  * URL: http://influxdb:8086
  * Custom HTTP Headers, select Add Header. Set header to `Authorization` and value to `Token [token]` (previously generated read Token for Grafana)
  * Database: telegraf

More info at: https://docs.influxdata.com/influxdb/v2.0/tools/grafana/?t=InfluxQL#configure-grafana-to-use-influxql

Add dashboards for Telegraf metrics. For example: https://grafana.com/grafana/dashboards/928-telegraf-system-dashboard/

Add influxdb data source: Administration -> Data sources -> Add data source -> Loki:

  * Name: Loki
  * URL: http://loki:3100



