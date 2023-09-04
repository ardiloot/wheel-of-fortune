
# Embedded software

## Orange Pi 3 LTS setup

Manual and downloads: http://www.orangepi.org/html/hardWare/computerAndMicrocontrollers/service-and-support/Orange-pi-3-LTS.html

### Burn image to SD card

Follow steps outlined in chapters 2.4 - 2.5.
Use `Orangepi3-lts_3.0.8_ubuntu_jammy_server_linux5.16.17.7z` image.

### Initial config

Install SD card, connect monitor and keyboard
Login using default username & password: orangepi/orangepi
Change user password.

### WIfi

Connect to Wifi (Chapter 3.8.2)

```bash
nmcli dev wifi
nmcli dev wifi connect [wifi_name] password [wifi_passwd]
```

### Install updates & reboot

```bash
sudo apt-get update
sudo apt-get upgrade
sudo reboot
```

### SSH

Add your public key to `~/.ssh/authorized_keys`
Disable password login (`sudo nano /etc/ssh/sshd_config`, set `PasswordAuthentication no`)


### WiringOP

User manual: "3.18. How to install wiringOP"

```bash
git clone https://github.com/orangepi-xunlong/wiringOP
cd wiringOP
sudo ./build clean
sudo ./build
```

Test
```bash
gpio readall
```

### Static ip Ethernet interface (connection to WLED)

```bash
nmcli con mod "Wired connection 1" ipv4.addresses "192.168.242.2/24" ipv4.method "manual"
sudo reboot
```

### GPIO permissions

```bash
sudo nano /etc/udev/rules.d/99-gpio.rules 
```

```
SUBSYSTEM=="gpio", KERNEL=="gpiochip*", ACTION=="add", PROGRAM="/bin/sh -c 'chown root:orangepi /sys/class/gpio/export /sys/class/gpio/unexport ; chmod 220 /sys/class/gpio/export /sys/class/gpio/unexport'"
SUBSYSTEM=="gpio", KERNEL=="gpio*", ACTION=="add", PROGRAM="/bin/sh -c 'chown root:orangepi /sys%p/active_low /sys%p/direction /sys%p/edge /sys%p/value ; chmod 660 /sys%p/active_low /sys%p/direction /sys%p/edge /sys%p/value'"
```

```bash
sudo reboot
```

## GPIO poweroff

Follow instructions from []

### Docker

https://docs.docker.com/engine/install/ubuntu/

```bash
sudo apt-get update
sudo apt-get install ca-certificates curl gnupg
```

```bash
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg
```

```bash
echo \
  "deb [arch="$(dpkg --print-architecture)" signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  "$(. /etc/os-release && echo "$VERSION_CODENAME")" stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
```

```bash
sudo apt-get update
```

```bash
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

```bash
sudo groupadd docker
```

```bash
sudo groupadd docker
sudo usermod -aG docker $USER
newgrp docker
```

Test:

```bash
docker run hello-world
```

### Move docker logs to journald

```bash
sudo nano /etc/docker/daemon.json 
```

```
{
   "log-driver": "journald"
}
```





## WLED

```bash
git subtree pull --prefix embedded_software/WLED https://github.com/Aircoookie/WLED.git v0.14.0-b4 --squash
```