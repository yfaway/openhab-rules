> **_NOTE:_** The reuseable APIs is being documented at https://yfaway.github.io/. Eventually all the doc will go there as well.

# openhab-rules
A set of rules for my house.

# Prerequisites
The rules work with the following devices/sensors, bindings, actions, and transformations. They make heavy use of OpenHab's groups concept and as such are quite general. You don't need to have all the sensors below to make use of the rules. If are new to OpenHab, or interested in practical integrations, these rules can be the starting point.

**Devices/Sensors**
* Chamberlain 3/4 HPS Belt Drive Garage Door Opener Built-in Wifi (LW6000WFC)
* DSC Security System with EnvisaLink inteface
* Ecobee3 Thermostat
* Aeotec Z-Wave USB ZStick Gen 5
* Inovelli NZW30 Z-Wave Wall Switch
* TP-Link HS100 WiFi Plug
* Xiaomi Aqara Motion Sensor (Zigbee)
* Xiaomi Aqara Temperature Sensor (Zigbee)
* Google Home/mini, Chromecast, Chromecast Audio

The following add-ons need to be installed.

Actions
1. [Mail Actions](https://docs.openhab.org/addons/actions/mail/readme.html) - for sending email alerts

Bindings
* [Astro](https://docs.openhab.org/addons/bindings/astro/readme.html) - to determine sunrise and sunset time
* [Chamberlain MyQ](https://docs.openhab.org/addons/bindings/myq1/readme.html)
* [Chromecast](https://www.openhab.org/addons/bindings/chromecast/)
* [DSC Alarm](https://docs.openhab.org/addons/bindings/dscalarm/readme.html)
* [Ecobee](https://docs.openhab.org/addons/bindings/ecobee1/readme.html)
* [Expire](https://www.openhab.org/addons/bindings/expire1/)
* [Feed](https://www.openhab.org/addons/bindings/feed/)
* [MQTT](https://www.openhab.org/addons/bindings/mqtt1/)
* [Network](https://docs.openhab.org/addons/bindings/network/readme.html) - for presence detection by phone
* [TPLinkSmartHome](https://www.openhab.org/addons/bindings/tplinksmarthome/#supported-things)
* [Weather](https://www.openhab.org/addons/bindings/weather1/#table-of-contents)
* [ZWave](https://www.openhab.org/addons/bindings/zwave/#supported-things)

Misc
1. Rule Engine (Experimental) - to support rules written in Jython

Transformations
1. [Javascript](https://www.openhab.org/addons/transformations/javascript/)
2. [JsonPath](https://docs.openhab.org/addons/transformations/jsonpath/readme.html)
3. [Map](https://docs.openhab.org/addons/transformations/map/readme.html)

Voice
These add-ons are used to play audio files, stream, or text to speech (TTS). Either Google Cloud TTS or VocieRSS would work. The "Marry TTS" is very slow on the Raspberry PI. Once downloaded, in the Paper UI, go to Configuration -> System -> Voice (at the very end of the page) to configure the default engine.

# Current Functionalities
## Alerts (email & TTS audio)
* Generic alert API in Python. By default all alerts go to email addresses. If the alert's level is warning or criticial, it also go to the audio sinks (speakers) through the text to speech (TTS) service.
* A separate python rule listens to changes in a string item to support legacy alerts from xtend rules.

## Ecobee Thermostat
* Change the thermostat to 'away' mode (climate ref) when the system is armed away. 'Away' mode should have lower heat setting and higher cool setting. Proactively change to away mode rather than relying on the static setting in the thermostat should save more energy.
* In the winter turn on the far when owner is at home. This helps to circulate the air to the second floor.

## Display (Basic UI)
* Garage door status.
* Security system status.
* Presence.
* Indoor temperature & humidity and forecasted weather inclduing Environment Canada alert.
* Lights, fans, and smart plug status.
* Motion sensors states
* Music stream control: play a stream over 1 or multiple chrome casts; pause, play and control volume.
* Camera snapshot viewer.

## Indoor Temperature/Humidity
* Send alert when indoor temperature or humidity value is outside the allowed ranges.
* Send alert when the kitchen temperature sensor is a certain degree above the thermostat settings. This might indicate an oven remains on.

## Light/Fan Control
* Global switch on HabUI to turn on/off individual or all controlled lights/fans.
* Turn on foyer light when the garage or front door is open.
* Turn on/off other lights automatically using an optional timer and an optional motion sensor.
* By default, only turn on the light if it is evening time (based on the sunset time from the Astro binding).
* Support an optional Number item for the illuminance value; turn on the light if it is below a illuminance LUX threshold, even if it is not yet evening.
* Support an optional item to disable motion sensor from turning on a light but still use the motion sensor event to keep the light on. This is for the scenario where a shared motion sensor is associated with multiple lights, but we only need to turn on a light at a time.  E.g. the great room and kitchen share the same motion sensor. That sensor needs to update the timer for both lights, but must not turn on the office light.
* Support an optional item to disable motion sensor from turning on a light if an associated light is already on. E.g. the great room and kitchen share an open space, if a light is already on, then a motion sensor event should not turn on the other light.
* Support an optional String item that contains the light switch to turn off when this light switch is turn on. E.g. when office light is turned on, turn off foyer light.
* Ignore the motion sensor event if a wall switch was just turned off. This prevents the light/fan from turning on again when a user manually turns it off and movng a way from the area. If not ignored, the motion sensor might trigger the switch to turn on again.
* Send alert when a triggering event (e.g. arm-away or vacation mode) tries to turn off a smart plug with energy reading, but the plug still has high wattage --> an appliance/device wasn't turned off yet. Won't turn off the plug in this case to avoid damaging the appliance; send an alert instead.
* Turn off all managed lights when armed away.

## Music / Voice Alerts
* A single Player and Volume control for the selected chromecast and music stream. Switching the chromecast or stream automaticaly play/re-cast the right music. Can select a single chrome cast or multiple.
* Pause Chromecast music when system is armed away.
* Automatically read out weather info (TTS), and then play classical music in the specified morning hour range. The two owners have different leaving schedules so the music is played up to 2 times during that hour range. Music is paused when the front door or garage door is open (implies owner leaving the house).
* Play music when a washroom fan is turned on, and pause when it is off.
* Tell kids to go to bed at 8:30 and 8:45; on the second notice, turn off the first floor lights as well.

## Presence
* Cell phone wifi connection using Network binding.
* Doors open (presence state expires in 5')
* Security motion sensor (presence state expires in 5')
* Xiaomi motion sensors (presence state expires in 5')
* Generic vacation mode (currently backed by the Ecobee's vacation setting).

## Route
* One or more route profiles can be configured in transform/routes.map file. Each profile specifies the destination address, the time range and the typical travelled road names. When the garage or front door is open, the rule will check if the current time is in the time range. If yes, it requests a route to the destination address using Google Maps service. If the route is different from a normally travelled route, it will send an email alert to the user.

## Smart Plugs
* Turn on/off plugs based on the security arm status, vacation mode, and hours of days.
* Turn on/off associated light when a power wattage crosses a threshold. E.g. turn on the office light when the PC is turned on.

## Security System
* Automatically arm-stay in the night if someone is home.
* Automatically arm-away after garage door is closed, and no presence detected after certain time. This is the usecase of the user left the house but forgot to arm-away.
* Automatically unarm in the morning before going to work.
* Automatically unarm if an owner open the garage door from the outside.
* Automatically unarm if garage door is open from Hab UI.
* Automatically arm away an hour after last presence event, if in vacation mode.
* Send alert when garage door remains open after a period of time.
* Send alert when the security system is in alarm.
* Send alert when the security system can't be armed programatically (e.g. a door is open).
* Send alert when a zone is tripped and all the following conditions are met: 1. system is not armed, 2. an owner is not home, and 3. within a specific period. 
* Send alert when the owner is on vacation and a zone is tripped or the system arm mode changes (use the Ecobee vacation mode).
* Send alert if a window is open (might indicate intrusion from the basement windows).

## Weather
* Send alert early in the morning if it is going rain today.
* Send alert if wind speed or wind gust speed crosses a threshold.
* Send alert if Environment Canada has a weather alert for the city.

# Todos - Functionalities
## Text Alerts
* Energy monitors such as Brultech GreenEye Monitor, Smappee, emonPi, or HEM Gen5 (zwave). Can be used to send alert if there is higher than baseline energy usage and no one is home.
* Water leakage.
* Smart plugs turned on while in vacation mode.
* Sensor battery is low.

## Control
* Turn on/off main water valve.
* Turn off water valve and alert when water leakage detected.
* Control blinds.
* Turn on/off vacation mode from sitemap --> set vacation mode on Ecobee as well.

## Light/Fan/Plug Control
* Associate each light with the dimming value and time range.

## Chrome cast
* Associate music life cycle with presence.
* Automatically transfer music as owner moves around; i.e. follow me mode.
* Add timer to stop music after 5', 10, 15, 30, 1h.

## Presence
* Ecobee motion sensor.

## Route
* Show time different between revised route and normal route.

## Security
* Audio alert when someone is at the front door, if an owner is at home.
* Send a camera snapshot when motion is detected and system is in vacation mode.

## Voice Alerts
* Pronounce name of the person heading back home.
* Voice alert if some one is at the front door or garage.
* Voice/text alert when washer/dryer finishs if owner is at home (required energy monitor).

# Todos - Design
* Move ZWave things to config file.
* Redesign the alert message structure to support audio alert as well as priority (info/warning/severe). Even if audio output is not specified, any event that is above INFO level should still generate an audio alert if the owner is presence.
