
# Electrical design

## Wiring diagram

[Wiring diagram](wiring%20diagram.pdf) of the Wheel of Fortune shows how to wire together different modules of the system (displayed as rectangles with round edges). It tries to follow the physical layout of the components if possible. Different wiring colors show different purpose of the wires and are described in the legend. All connectors are displayed from the "top view" (wires going into the screen).

In the following chapters each submodule is separately described together with its connections.

![Wiring diagram](imgs/wiring%20diagram.png)


## Backlight LEDS

A long led strip attached to the side of the backplate:
* Model: `WS2812 5V`
* Number of LEDs: 133
* LEDs per meter: 60

As LED strip can draw considerable amount of current (6.7 A), it is advised to power the LED strip form two distinct points (e.g. 1/4 and 3/4). Thick wires should be used (0.75 mm<sup>2</sup>). It is easiest to just solder power wires to the LED strip, but use of connectors is also possible if needed.

Power wires lead to `voltage converter` module and data wire is connected to `WLED` module (ESP32).

# Logo and wheel LEDs

Inside the center logo assembly there are two additional LED strips. Logo LED strip is used as a backlight to the logo and wheel LED strip is illuminating the front of the wheel.

They are powered separately from `voltage converter` module, but they share the data wire (like we have one long LED strip).

## Servo motors

Wheel of Fortune has 3 servo motors (`JX W4505-4T`) used to display side logos. They are regular 5V servos capable of doing multiple turns (to have enough actuation range). They are powered from `voltage converter` module and controlled by `WLED` module (ESP32).

3-pin Dupont connector is used to connect the motor.

![](imgs/servo%20module.png)

## Encoder

Encoder module contains of 5 line sensors that is used to monitor the encoder pattern attached to the back side of the wheel plate. One sensor is used for clock (and speed) signal and the rest of 4 sensors are used to have absolute positioning of the wheel (2<sup>4</sup> = 16 sectors). Accurate position inside of the sector is not monitored.

Encoder module is powered form `voltage converter` module (5 V) and the position of the wheel is communicated through 5 digital outputs (3.3 V) to `compute` module (Orange Pi).

Details of the schematic and manufacturing of the module can be found in [README](line_sensor_encoder/README.md) file.

![Audio module](imgs/encoder%20module.png)

## Power switch

Power switch is used (`DPST MRS201-3C3`) is used to gracefully power off and on the the electronics. Double Pole Single Throw (DPST) switch is used to send information to the `compute` module (Orange Pi) and to `power relay` module. If power is switched off, the `compute` module can initiate clean shutdown and `power relay` module can start countdown to cut the power (e.g. 30 secs). It should avoid disk corruption of the `compute` module.

![](imgs/speaker%20and%20power%20switch.png)


## Speakers

System has two speakers (`Alpine SXE-0825S`, RMS power 20W, peak power 150W). They are connected with spade connectors to the `audio` module.

## Audio module

Audio module mainly consists of:
1. Audio amplifier (`A502S TPA3116D2 50W`)
2. Ground loop isolator (`Kebidumei`)

Ground loop isolator is needed to avoid noise from the ground loop as Orange Pi (source of audio) and sound amplifier are are sharing ground connection. Adding sound cable is creating a ground loop unless isolator is used.

Module is powered from `power relay` module (20 V). On the image a custom power connector (`XT30`) is used, however standard barrel connector can also be used. Audio signal originates from `compute` module (Orange Pi).

![](imgs/audio%20module.png)

## Voltage converter

Almost all electronics are running on 5 V and this module is responsible for providing enough 5 V power. As LED strips can be power hungry (full brightness at white color) then this power module must be rated to 15 A (realistic max usage around 12 A).

Here, to keep it simple, a low cost 5 V converter (`TOBSUN 12V/24V TO 5V 15A`) is used together with two `WAGO 221-415` connectors. Module is powered from `power relay` module (20V) and 5 V power is distributed to almost all other module in the system.

NB: Wires from the converter to the WAGO connectors must be rated for 15 A (cross section > 1.5 mm<sup>2</sup>)

![](imgs/dc%20converter%20module.png)

## Power relay

The purpose of power relay is to:
1. Delay poweroff (e.g. 30 seconds) to allow graceful shutdown of the `compute` module (Orange Pi)
2. Short protection (fuse)
3. 20 V power distribution box

As this relay will be always powered on (even if the wheel is switched off) a good quality off the shelf timer relay is used (`Relpol RPC-1ER-UNI`) to lower the risk of possible malfunctions. Timer relay is programmed to delay power off by 30 seconds and to delay power on for 2 seconds.

There is a separate wiring diagram for power relay module in the bottom right corner of the diagram. It describes how to connect together timer relay, fuse and power switch. For connections, WAGO connectors are used.


![](imgs/relay%20module.png)

## Compute module

Compute module contains two sub-modules:
1. Orange Pi 3 LTS compute board
2. Olimex ESP32 POE

Orange Pi is the main compute unit of the system. It is powered from 5V and it has encoder module connected to its GPIO pins. Also, it is connected to the power switch to for shutdown signal. Note, that poweroff pin needs pull-up resistor.

ESP32 unit runs modified WLED software and is responsible for controlling LED strips and servo motors. It is powered by 5V and it has 3 PWM outputs for servo motors and 2 outputs for controlling LED strips.

Two units are connected together with short Ethernet cable.


![](imgs/compute%20module.png)

## Power supply

It is recommended to use at least 90 W power supply (19 - 24 V). In this case, `XT30` connector is used for easy replacement of the power supply.
