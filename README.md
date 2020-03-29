Thank you for visiting. This repository contains the smart home rules used in my house. They have been constantly tweaked since I started with OpenHab in 2018. While it is specific to my house, a lot of the concepts and APIs are re-usable in your own projects, so please read on.

<!-- vim-markdown-toc GFM -->

* [What does it mean to be smart?](#what-does-it-mean-to-be-smart)
* [Why is it so difficult to build a truely smart home system?](#why-is-it-so-difficult-to-build-a-truely-smart-home-system)
* [High level aspects of smart home system](#high-level-aspects-of-smart-home-system)
* [Sample home automation rules](#sample-home-automation-rules)
    * [Switches (lights / fans)](#switches-lights--fans)
        * [When to turn on light?](#when-to-turn-on-light)
        * [Dimmer is just a special light](#dimmer-is-just-a-special-light)
        * [Advanced light interaction](#advanced-light-interaction)
        * [Shared motion sensor](#shared-motion-sensor)
        * [Simulate presence during vacation time](#simulate-presence-during-vacation-time)
        * [Interaction with other devices](#interaction-with-other-devices)
    * [Security system](#security-system)
        * [Alerts](#alerts)
        * [Automatic security actions](#automatic-security-actions)
            * [Arm-stay in the night](#arm-stay-in-the-night)
            * [Arm-away while in vacation mode](#arm-away-while-in-vacation-mode)
            * [Disarm in the morning](#disarm-in-the-morning)
            * [Disarm when the garage door is open](#disarm-when-the-garage-door-is-open)
        * [Day time instrusion prevention](#day-time-instrusion-prevention)
        * [Scare the instruder even more when the security system is in alarm mode](#scare-the-instruder-even-more-when-the-security-system-is-in-alarm-mode)
        * [Use the arm-away event to trigger the system-wide away mode](#use-the-arm-away-event-to-trigger-the-system-wide-away-mode)
    * [Environment](#environment)
        * [Finer control over the furnace and air conditioner](#finer-control-over-the-furnace-and-air-conditioner)
        * [Controling the humidifier to reduce condensation.](#controling-the-humidifier-to-reduce-condensation)
        * [Alert on tornado warning, high wind or other severe conditions](#alert-on-tornado-warning-high-wind-or-other-severe-conditions)
        * [Alert on abnormal conditions inside the house](#alert-on-abnormal-conditions-inside-the-house)
        * [Read out the current weather and short term forecast](#read-out-the-current-weather-and-short-term-forecast)
    * [Entertainment/audio related](#entertainmentaudio-related)
        * [Play music during specific activities](#play-music-during-specific-activities)
        * [Play the mindfulness bell](#play-the-mindfulness-bell)
        * [Create a stream-based music player](#create-a-stream-based-music-player)
        * [Remind kids to go to bed](#remind-kids-to-go-to-bed)
    * [System administration](#system-administration)
        * [Run daily unit tests](#run-daily-unit-tests)
        * [Run timer rule to determine if any devices hasn't been triggered](#run-timer-rule-to-determine-if-any-devices-hasnt-been-triggered)
        * [Alert if any battery-powered device is low on battery](#alert-if-any-battery-powered-device-is-low-on-battery)
* [Key enabler](#key-enabler)
* [Things to avoid](#things-to-avoid)
* [Layout Model API - an alternative approach to access devices/sensors](#layout-model-api---an-alternative-approach-to-access-devicessensors)
    * [ZoneManager](#zonemanager)
    * [Zone](#zone)
    * [Devices](#devices)
    * [Actions](#actions)
* [Hardware](#hardware)
* [Current Functionalities](#current-functionalities)
    * [Alerts (email & TTS audio)](#alerts-email--tts-audio)
    * [Display (Basic UI)](#display-basic-ui)
    * [Presence](#presence)
    * [Route](#route)
    * [Smart Plugs](#smart-plugs)
* [Todos - Functionalities](#todos---functionalities)
    * [Text Alerts](#text-alerts)
    * [Control](#control)
    * [Light/Fan/Plug Control](#lightfanplug-control)
    * [Chrome cast](#chrome-cast)
    * [Presence](#presence-1)
    * [Route](#route-1)
    * [Security](#security)
    * [Voice Alerts](#voice-alerts)
* [Todos - Design](#todos---design)

<!-- vim-markdown-toc -->

# What does it mean to be smart?
Everyone is into Smart Home nowaday. However, contrary to what ordinary consumer might think (or led to think), a truely smart home should not require user's explicit instructions such as voice command through Google Assistant or Amazon Alexa.

A truely smart home system would be able to do things for you automatically based on various environmental factors. Its purpose is to simplify your life.  Let's look at an example on how you can check today's weather forecast.

* Level 3 (in the old day): you would open the browser, go to your favorite weather provider, and look up your city.
* Level 2: ask your smart home hub such as Google Home "OK Google, what is the weather like today".
* Level 1: as you step into the kitchen first thing in the morning, your smart home system uses Text-to-speech to read out the current weather, today's forecast, and whatever else you want to read out (e.g. calendar events).

In most cases, you would want the Level 1 notification above. However, occasionally there is a need to query the system for information out of band. We fall back to the middle tier (level 2) of home automation: interaction with the system through voice, applications, or physical devices. Nevertheless, the ultimate goal is still full automation.

# Why is it so difficult to build a truely smart home system?
Coming up with an automation concept isn't that difficult. The lazier you are, the better ideas you can come up with. It is about taking a fresh look at every aspect of our lives, and ask questions such as "What are some of the everyday routines that I'd like to automate?", or "Given the availability of these new devices, what more can I do to simplify my life?"

The main difficulty lies in **integration**. There are so many different devices and hubs with different communication protocols created by different vendors.  Getting them to work together is difficult. It also doesn't help that there is no easy way for the ordinary consumers to create home automation rules. This problem is somewhat similar to trying to automatically generate computer programs from high level UML models back in the 80s and 90s.  Today, sophisticated rules are still in the domain of highly technical users (mainly software developers or super users).

In the future, as more standardization happens (recently Google, Apple, Zigbee and others formed an alliance to create a single connectivity standard), and as software system becomes more sophisticated, it will be possible for the consumer to create rules like this *"OK Google, create this rule 'tell me today's weather forecast when I step into the washroom for the first time in the morning, then play some classical music'"*. It is not all free lunch however, as the user has to supply *contexts* to the system (e.g. what is 'morning' for you).  The user also has to know what rules to create. The assistant helps, but the user needs to play the role of the *programmer* at the conceptual level. Privacy is also a concern, but that is a different topic at this point.

In the short terms, sophisticated rules have to developed or coded.

# High level aspects of smart home system
Home automation can be classified into three main areas:

1. **Take actions**: the rules are triggered by some events, and they perform some actions.
2. **Notify**: an event occurred, and the system needs to notify it to the users.
3. **Query/control**: not rules per say, but this is the exposed interface that let the user query/control the system. Typically, it is through a web application.

As discussed above, it is more desirable to have rules performing actions automaticaly.

# Sample home automation rules

## Switches (lights / fans)
Controlling lights is the most common scenario people think of. There are low tech solutions that integrate with a motion sensor. These are relatively cheap and self-operated. However, you can't control them programmatically.

For a fully flexible solution, we would need at minimum one motion sensor and one smart switch in each controllable zone. The basic logic is to turn on the switch when the motion sensor is triggered. Each switch needs to be associated with a timer so that it can be automatically turned off. The timer is started when the switch is turned on, and is renewed if the motion sensor is triggered again.

There are however more nuiances with light control in general. The sections below list some of those aspects. The actions [Turn on Switch](https://github.com/yfaway/openhab-rules/blob/master/automation/jsr223/aaa_modules/layout_model/actions/turn_on_switch.py) and [Turn off Adjacent Zones](https://github.com/yfaway/openhab-rules/blob/master/automation/jsr223/aaa_modules/layout_model/actions/turn_off_adjacent_zones.py) take care of these.

### When to turn on light?
Naturally light must be turned on when it is dark. One way to do that is based on the sun set time. The [Astro binding](https://www.openhab.org/addons/bindings/astro/) provides this capability. 

But what if there is a lot of cloud today and the zone is just dark. An illumination sensor can be incorporated to measure the illumination level. The rule can define an illumination threshold after which the light is turned on no matter whether it is day or night.

If the light is in a bedroom, it shouldn't be turned on at bed time. This suggests a virtual device that tell the rule when is the bed time for this particular zone. Or more generally, what are the time ranges for no-light.

### Dimmer is just a special light
A dimmer is just an instance of a light. It knows how to turn on and off. It also has special property to restrict the brightness level between 0% and 100%. This makes it suitable in area such as lobby or washrooms. The rule can adjust the brightness level based on the zone activity. However, in terms of complexity management, it should be the same rule controlling both regular light and dimmer.

### Advanced light interaction
Sci-fi movies in the past showed the light transition as the main actor moves between zones (the current zone's light is turned on, and the previous zone's light is turned off). This can be done quite easily today. The trick is to define relationships between zones.

Given two zones A and B, the following relationships can be defined:
1. A and B are not connected, and thus is considered closed space. There is no interaction in this case.
2. A is an open space neighbor of B. This is the typical scenario and automatic light transitioning can be done. For example: Foyer, Lobby and Kitchen are linearly connected. As the user opens the front door, Foyer light is turned on. As they walk into the Lobby, the Lobby light is turned on and the Foyer light is turned off. Similar thing with the Kitchen light.
3. A is an open space master of B. Similar with 2) above, but with further rule: as A is considered to be the main zone, if its light is already on, then B's light won't be turned on even if its motion sensor was triggered.
4. A is an open space slave of B. This is just a reverse of 3).

### Shared motion sensor
In open space houses, a motion sensor might cover mulitple zones. Which zone's light should be turned on when the motion sensor is triggerred? A special flag might be used here to indicate which zone takes precedent.

### Simulate presence during vacation time
When on extended vacations, the smart lights in the house can be programmed to simulate owner presence (thief prevention). The rule to do this is quite simple.
1. Triggered at sunset time.
2. Loop until bed time or when the house is unarmed or when stopped from the control panel.
3. Randomize a light-on period in minutes.
4. Pick one of the light, and turn it on for the random period above.
5. Sleep for that duration and loop again with another light and another light-on period.

This Xtend [light vacation](https://github.com/yfaway/openhab-rules/blob/master/rules/lights-vacation-mode.rules) does just that. Eventually it will be converted to Python using the layout model APIs.

### Interaction with other devices
The switches can be both the originator (triggering other actions) or the receiver (to turn itself on/off) from other actions.

Here are some examples:
* When the washroom fan is turned on (indicating that someone is taking a shower), play some music and also turn on the furnace fan.
* When the smoke alarm beeps, turn on all lights.

## Security system
Modern house may have an wired security system. This is the most reliable way to secure a house. If you are building a new home, ensure to pay for this upgrade.

An wired security system gives you a lot of sensors: boundary door sensors, windows sensors, motion sensor, security panel, and possibly a smoke sensor. Doing this using wireless technology is possible, but it will be a lot of work, expensive and not as reliable.

The number of sensors gives you many possible integration opportunities.

### Alerts
The following alerts can be programmed:
* Send alert when garage door remains open after a period of time.
* Send alert when the security system is in alarm.
* Send alert when the security system can't be armed programatically (e.g. a door is open).
* Send alert when a zone is tripped and all the following conditions are met: 1. system is not armed, 2. an owner is not home, and 3. within a specific period. 
* Send alert when the owners are on vacation and a zone is tripped or the system arm mode changes. This is also useful for tracking purpose.
* Send alert if a window is open (might indicate intrusion from the basement windows).

Reference: 
* [security-alert-when-in-alarm](https://github.com/yfaway/openhab-rules/blob/master/rules/security-alert-when-in-alarm.rules),
* [security-alert-when-in-vacation](https://github.com/yfaway/openhab-rules/blob/master/rules/security-alert-when-in-vacation.rules),
* [security-alerts-general](https://github.com/yfaway/openhab-rules/blob/master/rules/security-alerts-general.rules),
* [Alert On Door Left Open](https://github.com/yfaway/openhab-rules/blob/master/automation/jsr223/aaa_modules/layout_model/actions/alert_on_door_left_open.py) action.

### Automatic security actions
Reference: [Security Actions](https://github.com/yfaway/openhab-rules/blob/master/automation/jsr223/aaa_modules/layout_model/actions/simulate_daytime_presence.py) rules.

#### Arm-stay in the night
A simple rule can help to ensure that the house is always armed in the *stay* mode in the evening, while taking into account the possible walk-ins to the garage.

This can be done by using a series of time-triggered event 15 minutes apart, starting from say 8PM to 2AM. Each 15 minute, the rule checks if the system is armed, if not, it arms in the *stay* mode.

As the owners go in/out to/from the garage, they don't need to remember to arm it again. This is now automatic.

#### Arm-away while in vacation mode
If you are on vacation, you want the house to be in the *arm-away* mode. But what if you have plants in the house, and have to ask friends to come by to water them. A way to ensure that the system continues to be armed after they leave is to detect a presence-off event (no one is inside the house), arm the system sometimes after that.

#### Disarm in the morning
Two options:
1. Hard-code the time to disarm the system in the morning.
2. Put a motion sensor in the foyer or common area. As the motion sensor is triggerred in the *wake-up* time period, disarm the system.

#### Disarm when the garage door is open
If the garage door is open, and the system detects that it is one of the user going home, automatically disarm the alarm system. The following devices would be needed:
* Smart garage door opener.
* Presence devices (cell phone or WiFi/bluetooth dongles).
* Security system.

Relying on the cellphone is this case will be hit or miss. Cellphones are optimized to conserve the battery, so unless the owners start using the phone, the system won't be able to determine presence based on network devices. A dedicated WiFi/bluetooth dongle would be more reliable.

### Day time instrusion prevention
In certain areas, there are blazing house break-in in the day time when the owners are away at work.  One way to prevent that is to fake owner presence by playing loud music as someone approachs the house. The following devices would be needed:
* A way to indicate that the user is away. The arm-away mode of an security system is a perfect way to do this.
* An exterior motion sensor.
* An audio device on the first floor.

When the motion sensor is triggered, if the system is in arm-away mode, play some loud music on the audio device. Turn off the music after some minutes.

See [Simulate Daytime Presence](https://github.com/yfaway/openhab-rules/blob/master/automation/jsr223/aaa_modules/layout_model/actions/simulate_daytime_presence.py) action.

### Scare the instruder even more when the security system is in alarm mode
See [GH-19](https://github.com/yfaway/openhab-rules/issues/19) issue.

Here's the basic idea:
* Triggered when security system is in alarm.
* If this is light-on time, turn on all smart light.
* Play loud text-to-speed messages on the main floor audio sink.
    * First message: "Communicating with the alarm monitoring company."
    * Subsequence messages in a loop: "Police has been dispatched" ...
* Stop the rule when the system is disarmed.

### Use the arm-away event to trigger the system-wide away mode
Presence detection is a complex area. There are many devices that can indicate the presence of the occupants in a house such as motion sensors, light-on status, network devices, and bluetooth devices. They work well but are not always accurate.

The security system's *arm-away* event however provides an absolute certainty that there is no one at home. This allows rule to do multitude of things such as:
* Turn off all lights;
* Turn off all audio devices;
* Turn off all smart plugs;
* Change the furnace/AC to 'away' mode.

That saves time and money.

## Environment
Environment refers to the outdoor weather as well as the indoor temperature and humidity.

### Finer control over the furnace and air conditioner
Every smart thermostat allows the user to set different time periods such as 'home', 'away', or 'sleep'. These are fixed for each day of the week. With the help of other devices/sensors we can make these periods a lot more precise.

For example, when the security system is armed away, this indicates there won't be any user at home. The thermostat can then be switched over to 'away' mode immediately. And as the system is disarmed, it switches back to 'home' mode.

### Controling the humidifier to reduce condensation.
In many areas in Canada, it is very dry in the winter. Many houses are equipped with a whole-house humidifer unit, which is typically hook up with the furnace. As the furnace runs, the humidifier emits water vapour.  That is all good except when the outdoor weather is very cold, in which case the high humidity level inside the house will cause condensation on the windows.

Thus the humidifier has to be constantly adjusted based on the temperature outside. If you can hook up the humidifier to the smart thermostat, a rule can be created to adjust the humid level based on the outdoor temperature. The rule can be ran couple times per day.

### Alert on tornado warning, high wind or other severe conditions
Some weather services provide emergency warnings such as incoming tornado. A rule can be set up to provide audible notice (through the Google Chromecast for example) to the occupants.

If the house has big tall tree nearby and if the forecast indicates high wind gust, another rule can be created to provide alert and allow moving the occupant to another area.

### Alert on abnormal conditions inside the house
Temperature and humid sensors are relatively cheap. Beside the main thermostat, additional sensors can be placed throughout the house and a rule can be created to provide alert if the temperature or humid level falls outside the normal ranges.

### Read out the current weather and short term forecast
There is no need to explicitly ask for the weather info to determine what we shall wear for the day. If you have the following services/devices, the system can provide that info automatically.
* Motion sensor
* Text-to-speed service
* Weather service
* Audio sink such as Chromecast
* Spefication for *wake-up* time.

A motion sensor can be placed in the washroom on common area. As it is triggered for the first time by the motion sensor, it determines if this is *wake-up* time. If yes, query weather service, formulate the text, and read it out on the audio sink.

## Entertainment/audio related

### Play music during specific activities
Reference: [music-and-announcement](https://github.com/yfaway/openhab-rules/blob/master/automation/jsr223/music-and-announcement.py)

### Play the mindfulness bell
Reference: [play-mindfullness-bell](https://github.com/yfaway/openhab-rules/blob/master/automation/jsr223/play-mindfullness-bell.py)

### Create a stream-based music player
* A single Player and Volume control for the selected chromecast and music stream. Switching the chromecast or stream automaticaly play/re-cast the right music. Can select a single chrome cast or multiple.
Reference: [chrome-cast-master-control](https://github.com/yfaway/openhab-rules/blob/master/automation/jsr223/chrome-cast-master-control.py)

### Remind kids to go to bed
* Tell kids to go to bed at 8:30 and 8:45; on the second notice, turn off the first floor lights as well.
Reference: [kids-sleep-time-reminder](https://github.com/yfaway/openhab-rules/blob/master/automation/jsr223/kids-sleep-time-reminder.py)

## System administration
This section does not concern with the end-user rules, but it lists things that can be done to ensure the system is running correctly.

### Run daily unit tests
Reference: [zzz-run-unit-tests](https://github.com/yfaway/openhab-rules/blob/master/automation/jsr223/zzz-run-unit-tests.py)

### Run timer rule to determine if any devices hasn't been triggered
Reference: [alert_on_inactive_battery_devices](https://github.com/yfaway/openhab-rules/blob/master/automation/jsr223/alert_on_inactive_battery_devices.py)

### Alert if any battery-powered device is low on battery
tbd

# Key enabler
- Alert
- Presence

# Things to avoid
* Cloud
* Security

> **_NOTE:_** The reuseable APIs is being documented at https://yfaway.github.io/. Eventually all the doc will go there as well.

# Layout Model API - an alternative approach to access devices/sensors
In OpenHab, items are defined in a flat manner in .items file under /etc/openhab2/items folder. They are usually linked to a channel exposed by the underlying hardware. Vitual items do not link to any channel.
This flat structure has an impact on how rules (whether in Xtend or Python) are organized. When the rules need to interact with mulitple devices of the same type, they can utilize the group concept. Examples of this is to turn off all lights. What is more tricky is when rules need to interact with different devices within the same area. The typical solution to this is to group unrelated items that belong to the same zone either by using naming pattern, or by dedicated groups. For example, the light switch and motion sensor in the Foyer area can be named like this: "FF_Foyer_Light", and "FF_Foyer_MotionSensor". When a sensor is triggered, the zone can be derived from the triggering item name, and other devices/sensors can be retrieved using that naming convention.

This project provides another approach through the [Layout Model API](https://github.com/yfaway/openhab-rules/tree/master/automation/jsr223/aaa_modules/layout_model). The idea is similar to the difference between database relational model versus ORM. Each house (a ZoneManager) contains multiple rooms (Zones), and each room contains multiple devices. Each zone is associated with actions. The usual OpenHab events are routed in this manner: OpenHab events --> ZoneManager --> Zones --> Actions. It provides a level of abstraction on top of the items. Actions can operate on abstract devices and not concerned about the naming of the items.

## ZoneManager
There are two instances of ZoneManager. The mutable one is constructed once when OpenHab startup to create the zones. In this project, the [ZoneParser](https://github.com/yfaway/openhab-rules/blob/master/automation/jsr223/aaa_modules/zone_parser.py) class parses from the existing .items files to construct a ZoneManager instance.

Then there is the [ImmutableZoneManager](https://github.com/yfaway/openhab-rules/blob/master/automation/jsr223/aaa_modules/layout_model/immutable_zone_manager.py) that are parsed around to zones, and actions. It provides access to zones and devices without allowing modification to its states.

## Zone

## Devices

## Actions

# Hardware
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

## Display (Basic UI)
* Garage door status.
* Security system status.
* Presence.
* Indoor temperature & humidity and forecasted weather inclduing Environment Canada alert.
* Lights, fans, and smart plug status.
* Motion sensors states
* Music stream control: play a stream over 1 or multiple chrome casts; pause, play and control volume.
* Camera snapshot viewer.

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
* Voice/text alert when washer/dryer finishs if owner is at home (required energy monitor).

# Todos - Design
* Move ZWave things to config file.
