# openhab-rules
A set of rules for my house.

# Prerequisites
The following sensors, bindings, actions, and transformations need to be present and installed for the rules to work.

**Sensors**
1. Chamberlain 3/4 HPS Belt Drive Garage Door Opener Built-in Wifi (LW6000WFC)
2. DSC Security System with EnvisaLink inteface
3. Ecobee3 Thermostat

**Bindings**
1. [Astro Binding](https://docs.openhab.org/addons/bindings/astro/readme.html) - to determine sunrise and sunset time
1. [Chamberlain MyQ Binding](https://docs.openhab.org/addons/bindings/myq1/readme.html)
2. [DSC Alarm Binding](https://docs.openhab.org/addons/bindings/dscalarm/readme.html)
3. [Ecobee Binding](https://docs.openhab.org/addons/bindings/ecobee1/readme.html)
4. [Network Binding](https://docs.openhab.org/addons/bindings/network/readme.html) - for presence detection by phone

**Actions**
1. [Mail Actions](https://docs.openhab.org/addons/actions/mail/readme.html) - for sending email alerts

**Transformations**
1. [JsonPath](https://docs.openhab.org/addons/transformations/jsonpath/readme.html)
2. [Map](https://docs.openhab.org/addons/transformations/map/readme.html)

# Current Functionalities
## Text Alerts
* When garage door remains open after a period of time.
* When the security system is in alarmed.
* When a zone tripped while system is not armed, and an owner is not home, and within a specific period. 
* When on vacation and a zone is tripped or the system arm state chagnes (use the Ecobee vacation mode).
* When temperature or humidity value is outside the allowed ranges.

## Display
* Garage door status.
* Presence.
* Security system status.
* Indoor and forecasted temperature and humidity.

## Light Control
* Turn on foyer light when the garage or front door is open.
* Automatically turn off light after a certain period of time (configured per light).
* Global switch to turn on/off all controlled lights.

## Presence
* Cell phone wifi connection using Network binding.
* Security motion sensor (if triggered, set to be good for the next 5 minutes).

## Security Actions
* Automatically “armed stay” in the night if someone is home.
* Automatically unarm in the morning before going to work.
* Automatically unarm if an owner open the garage door from the outside.
* Automatically unarm if garage door is open from Hab UI.

# Todos - Functionalities
## Text Alerts
* Send a camera snapshot when motion is detected and system is in vacation mode.
* Audio alert when someone is at the front door, if an owner is at home.
* Energy monitors such as Brultech GreenEye Monitor, Smappee, emonPi, or HEM Gen5 (zwave). Can be used to send alert if there is higher than baseline energy usage and noone is home.
* Automatic security arm failed -> send alert with the name of the opened door (zone tripped)
* Water leakage.

## Control
* Turn on/off main water valve.
* Turn off water valve and alert when water leakage detected.
* Control blinds.

## Display
* Energy usage.

## Presence
* Ecobee motion sensor.

## Voice Alerts
* Pronounce name of the person heading back home.
* Voice alert if some one is at the front door or garage.
* Voice/text alert when washer/dryer finishs if owner is at home (required energy monitor).

# Todos - Design
* Move ZWave things to config file.
* Add an event for vacation mode (e.g. detect through vacation setting on the ecobee).
