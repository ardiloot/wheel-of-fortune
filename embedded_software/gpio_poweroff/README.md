
# GPIO Poweroff


## Overview

This is a simple service designed to poll a GPIO pin for a poweroff signal. Currently, pin `PL08` (16) is assigned for detecting the shutdown signal. Please ensure that a pull-up resistor is installed.

During regular operation, the pin should remain in a low state. A transition to the high state will trigger the system to initiate a poweroff sequence.

## Installation

Copy Service Files to /opt:

```bash
sudo cp -r ~/wheel-of-fortune/embedded_software/gpio_poweroff /opt/
```

Enable and Start the Service:

```bash
sudo systemctl enable /opt/gpio_poweroff/gpio-poweroff.service
sudo systemctl start gpio-poweroff.service
```

Check Service Status:

```bash
sudo systemctl status gpio-poweroff.service
```

Remember to ensure that the `gpio-poweroff-script.sh` script is properly configured to poll the GPIO pin and trigger the poweroff sequence as needed.
