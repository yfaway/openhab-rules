# openhab-rules
A set of rules for my house.

# Prerequisites
The following sensors, bindings, actions, and transformations need to be present and installed for the rules to work.

**Sensors**
1. Chamberlain 3/4 HPS Belt Drive Garage Door Opener Built-in Wifi (LW6000WFC)
2. DSC Security System with EnvisaLink inteface
3. Ecobee3 Thermostat
4. Aeotec Z-Wave USB ZStick Gen 5
5. Inovelli NZW30 Z-Wave Wall Switch
6. TP-Link HS100 WiFi Plug
7. Xiaomi Aqara Motion Sensor (Zigbee)

**Bindings**
1. [Astro Binding](https://docs.openhab.org/addons/bindings/astro/readme.html) - to determine sunrise and sunset time
2. [Chamberlain MyQ Binding](https://docs.openhab.org/addons/bindings/myq1/readme.html)
3. [DSC Alarm Binding](https://docs.openhab.org/addons/bindings/dscalarm/readme.html)
4. [Ecobee Binding](https://docs.openhab.org/addons/bindings/ecobee1/readme.html)
5. [Network Binding](https://docs.openhab.org/addons/bindings/network/readme.html) - for presence detection by phone
6. [TPLinkSmartHome Binding](https://www.openhab.org/addons/bindings/tplinksmarthome/#supported-things)
7. [ZWave](https://www.openhab.org/addons/bindings/zwave/#supported-things)

**Actions**
1. [Mail Actions](https://docs.openhab.org/addons/actions/mail/readme.html) - for sending email alerts

**Transformations**
1. [Javascript](https://www.openhab.org/addons/transformations/javascript/)
2. [JsonPath](https://docs.openhab.org/addons/transformations/jsonpath/readme.html)
3. [Map](https://docs.openhab.org/addons/transformations/map/readme.html)

# Current Functionalities
## Alerts (email)
* When garage door remains open after a period of time.
* When the security system is in alarm.
* When the security system can't be armed programatically (e.g. a door is open).
* When a zone is tripped and all the following conditions are met: 1. system is not armed, 2. an owner is not home, and 3. within a specific period. 
* When the owner is on vacation and a zone is tripped or the system arm mode changes (use the Ecobee vacation mode).
* When temperature or humidity value is outside the allowed ranges.
* When a triggering event (e.g. arm-away or vacation mode) tries to turn off a smart plug with energy reading, but the plug still has high wattage --> an appliance/device wasn't turned off yet. Won't turn off the plug in this case to avoid damaging the appliance; send an alert instead.

## Display
* Garage door status.
* Presence.
* Security system status.
* Indoor and forecasted temperature and humidity.
* Lights, fans, and smart plug status.
* Motion sensors states

## Light/Fan Control
* Global switch on HabUI to turn on/off individual or all controlled lights/fans.
* Turn on foyer light when the garage or front door is open.
* Turn on/off other lights automatically using an optional timer and an optional motion sensor.
* Support an optional item to disable motion sensor from turning on a light but still use the motion sensor event to keep the light on. This is for the scenario where a shared motion sensor is associated with multiple lights, but we only need to turn on a light at a time.  E.g. the great room and kitchen share the same motion sensor. That sensor needs to update the timer for both lights, but must not turn on the office light.
* Support an optional item to disable motion sensor from turning on a light if an associated light is already on. E.g. the great room and kitchen share an open space, if a light is already on, then a motion sensor event should not turn on the other light.
* Support an optional String item that contains the light switch to turn off when this light switch is turn on. E.g. when office light is turned on, turn off foyer light.
* Ignore the motion sensor event if a wall switch was just turned off. This prevents the light/fan from turning on again when a user manually turns it off and movng a way from the area. If not ignored, the motion sensor might trigger the switch to turn on again.

## Presence
* Cell phone wifi connection using Network binding.
* Security motion sensor (if triggered, set to be good for the next 5 minutes).
* Generic vacation mode (currently backed by the Ecobee's vacation setting).

## Route
* One or more route profiles can be configured in transform/routes.map file. Each profile specifies the destination address, the time range and the typical travelled road names. When the garage or front door is open, the rule will check if the current time is in the time range. If yes, it requests a route to the destination address using Google Maps service. If the route is different from a normally travelled route, it will send an email alert to the user.

## Smart Plugs
* Turn on/off plugs based on the security arm status, vacation mode, and hours of days.
* Turn on/off associated light when a power wattage crosses a threshold. E.g. turn on the office light when the PC is turned on.

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
* Water leakage.
* Smart plugs turned on while in vacation mode.
* Sensor battery is low.

## Control
* Turn on/off main water valve.
* Turn off water valve and alert when water leakage detected.
* Control blinds.

## Light/Fan/Plug Control
* Turn off all managed lights and fans when armed away.
* Turn on light based on motion sensor and illuminate level (if available).

## Display
* Energy usage.

## Presence
* Ecobee motion sensor.
* Xiaomi motion sensors

## Voice Alerts
* Pronounce name of the person heading back home.
* Voice alert if some one is at the front door or garage.
* Voice/text alert when washer/dryer finishs if owner is at home (required energy monitor).

# Todos - Design
* Move ZWave things to config file.
