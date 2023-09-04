# Embedded software

## Orange Pi 3 setup

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

```
{
   "log-driver": "journald"
}
```

## GPIO poweroff service

This service listens GPIO port for shutdown signal (physical poweroff switch).
Only use this service, if poweroff switch is installed. 
For installation, follow instructions from [gpio_poweroff/README.md](gpio_poweroff/README.md).



## WLED

```bash
git subtree pull --prefix embedded_software/WLED https://github.com/Aircoookie/WLED.git v0.14.0-b4 --squash
```
