# Embedded software

## Orange Pi 3 LTS setup

### Burn image to SD card

Follow steps outlined in User Manual (chapters 2.4 - 2.5) to burn Ubuntu server image (`Orangepi3-lts_3.0.8_ubuntu_jammy_server_linux5.16.17.7z`) to SD card.

[Manual and downloads](http://www.orangepi.org/html/hardWare/computerAndMicrocontrollers/service-and-support/Orange-pi-3-LTS.html)

### Initial configuration

Install SD card and power on the Orange Pi board.
To complete initial config, monitor and keyboard must be connected (or Ethernet cable for SSH access). Login using default username & password: orangepi/orangepi

1. Change user password (`passwd`)
2. Connect to WiFi (User Manual chapter 3.8.2)

```bash
nmcli dev wifi
nmcli dev wifi connect [wifi_name] password [wifi_passwd]
```

3. Install updates

```bash
sudo apt-get update
sudo apt-get upgrade
```

4. Add your public SSH key to `~/.ssh/authorized_keys`
5. Disable password login (`sudo nano /etc/ssh/sshd_config`, edit relevant line to `PasswordAuthentication no`)
6. Reboot (`sudo reboot`)

This concludes initial configuration, rest of the configuration can be done over SSH.

### Install WiringOP

Install utilities for controlling GPIO. For more information see User Manual chapter "3.18 How to install wiringOP".

```bash
git clone https://github.com/orangepi-xunlong/wiringOP
cd wiringOP
sudo ./build clean
sudo ./build
```

Test GPIO (should see a table with GPIO current status):

```bash
gpio readall
```

### Set static IP to Ethernet interface

Ethernet port is used to connect to Olimex ESP32 POE running WLED software.
WLED and Ethernet interface should have IP addresses from the same subnet.
In this example, WLED is configured to have static IP `192.168.242.3/24`
and Orange PI's Ethernet port to `192.168.242.2/24`.

```bash
nmcli con mod "Wired connection 1" ipv4.addresses "192.168.242.2/24" ipv4.method "manual"
```

Reboot the system for changes to take effect.

### GPIO permissions

Modify udev rules to allow acces of non-root users to GPIO. Create file

```bash
sudo nano /etc/udev/rules.d/99-gpio.rules
```

with following contents:

```bash
SUBSYSTEM=="gpio", KERNEL=="gpiochip*", ACTION=="add", PROGRAM="/bin/sh -c 'chown root:orangepi /sys/class/gpio/export /sys/class/gpio/unexport ; chmod 220 /sys/class/gpio/export /sys/class/gpio/unexport'"
SUBSYSTEM=="gpio", KERNEL=="gpio*", ACTION=="add", PROGRAM="/bin/sh -c 'chown root:orangepi /sys%p/active_low /sys%p/direction /sys%p/edge /sys%p/value ; chmod 660 /sys%p/active_low /sys%p/direction /sys%p/edge /sys%p/value'"
```

Reboot the system for changes to take effect.

### Install Docker

Install Docker following the instructions from the Docker's home page:
[instructions](https://docs.docker.com/engine/install/ubuntu/#install-using-the-repository).

Also complete [linux postinstall](https://docs.docker.com/engine/install/linux-postinstall/) steps.

By default Docker logs to disk and causes SD card wear.
To avoid that, redirect logging to `journald`. Create file

```bash
sudo nano /etc/docker/daemon.json
```

with contents

```json
{
   "log-driver": "journald"
}
```

## GPIO poweroff service

This service listens GPIO port for shutdown signal (physical poweroff switch).
Only use this service, if poweroff switch is installed. 
For installation, follow instructions from [gpio_poweroff/README.md](gpio_poweroff/README.md).


## Setup VPN (optional)

Follow instructions starting from:
[here] (https://www.digitalocean.com/community/tutorials/how-to-set-up-wireguard-on-ubuntu-22-04#step-7-configuring-a-wireguard-peer)


Use following configuration:

```bash
sudo nano /etc/wireguard/wg0.conf
```

```
[Interface]
Address = 192.168.241.2
PrivateKey = !REPLACE!

[Peer]
PublicKey = !REPLACE!
Endpoint = example.com:51820
AllowedIPs = 192.168.241.0/24
PersistentKeepalive = 25
```

Configure VPN to always restart:

`sudo systemctl edit wg-quick@wg0.service`

```
[Unit]
StartLimitIntervalSec=0
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
Restart=always
RestartSec=5s
```

## Setup telegraf (optional)

https://docs.influxdata.com/telegraf/v1.21/introduction/getting-started/


1. Install `sudo apt-get install lm-sensors`
1. Enable `outputs.influxdb_v2`
2. Enable `inputs.sensors`

## Setup promtail (optional)

To send logs to Loki, configure promtail to scrape journald.

First, install promtail:

```bash
wget https://github.com/grafana/loki/releases/download/v2.8.4/promtail-linux-arm64.zip
unzip promtail-linux-arm64.zip
rm promtail-linux-arm64.zip
sudo mv promtail-linux-amd64 /usr/local/bin/promtail
# Verify
promtail --version
```

Create configuration file

```bash
sudo mkdir -p /etc/promtail
sudo mkdir -p /var/lib/promtail/
sudo nano /etc/promtail/config.yaml
```

with contents (replace server and auth info).

```yaml
server:
  disable: true

positions:
  filename: /var/lib/promtail/positions.yaml

clients:
  - url: https://[replace]/loki/api/v1/push
    basic_auth:
      username: [replace]
      password: [replace]

scrape_configs:
  - job_name: journal
    journal:
      max_age: 12h
      json: false
      labels:
        job: systemd-journal
    # see https://www.freedesktop.org/software/systemd/man/systemd.journal-fields.html#Trusted%20Journal%20Fields
    # see https://grafana.com/docs/loki/latest/clients/promtail/scraping/#journal-scraping-linux-only
    # NB use `journalctl -n 1 -o json | jq .` to see an actual journal log message (including metadata).
    # NB use `journalctl -n 1 -o json CONTAINER_NAME=date-ticker | jq .` to see a container log message.
    relabel_configs:
      - source_labels: [__journal__hostname]
        target_label: host
      - source_labels: [__journal__systemd_unit]
        target_label: source
      - source_labels: [__journal_container_name]
        target_label: container_name
      - source_labels: [__journal_image_name]
        target_label: image_name
      - source_labels: [__journal_workflow_id]
        target_label: workflow_id
      - source_labels: [__journal__boot_id]
        target_label: boot
      - source_labels: [__journal_priority]
        target_label: priority
    pipeline_stages:
      - template:
          source: priority
          template: '{{ if eq .Value "0" }}{{ Replace .Value "0" "emerg" 1 }}{{ else if eq .Value "1" }}{{ Replace .Value "1" "alert" 1 }}{{ else if eq .Value "2" }}{{ Replace .Value "2" "crit" 1 }}{{ else if eq .Value "3" }}{{ Replace .Value "3" "err" 1 }}{{ else if eq .Value "4" }}{{ Replace .Value "4" "warning" 1 }}{{ else if eq .Value "5" }}{{ Replace .Value "5" "notice" 1 }}{{ else if eq .Value "6" }}{{ Replace .Value "6" "info" 1 }}{{ else if eq .Value "7" }}{{ Replace .Value "7" "debug" 1 }}{{ end }}'
      - labels:
          priority:
```

To start promtail automatically, create a systemd service

```
sudo nano /etc/systemd/system/promtail.service
```

with content:

```
[Unit] 
Description=Promtail service 
After=network-online.target
Wants=network-online.target 

[Service] 
Type=simple 
User=root 
ExecStart=/usr/local/bin/promtail -config.expand-env=true -config.file /etc/promtail/config.yaml 
Restart=on-failure 
RestartSec=20 
 
[Install] 
WantedBy=multi-user.target
```

To enable and test the service, run:

```bash
sudo systemctl daemon-reload
sudo systemctl enable promtail
sudo systemctl start promtail
sudo systemctl status promtail
```

## WLED

```bash
git subtree pull --prefix embedded_software/WLED https://github.com/Aircoookie/WLED.git v0.14.0-b4 --squash
```

