This repository contains the smart home rules used in my house. They have been constantly tweaked since I started with [OpenHab](https://github.com/openhab) in 2018. While it is specific to my house, a lot of the [concepts](#sample-home-automation-rules) and [APIs](#layout-model-api---an-alternative-approach-to-access-devicessensors) might be re-usable in your own projects.

The majority of the APIs and rules are in Python. There are a few older rules in Xtend; they will eventually be migrated over to Python. This projects relies on the excellent [openHAB Scripters project](https://github.com/openhab-scripters/openhab-helper-libraries).

<!-- vim-markdown-toc GFM -->

* [1. What does it mean to be smart?](#1-what-does-it-mean-to-be-smart)
* [2. Why is it so difficult to build a truely smart home system?](#2-why-is-it-so-difficult-to-build-a-truely-smart-home-system)
* [3. High level aspects of smart home system](#3-high-level-aspects-of-smart-home-system)
* [4. Sample home automation rules](#4-sample-home-automation-rules)
    * [4.1 Switches (lights / fans)](#41-switches-lights--fans)
        * [4.1.1 When to turn on light?](#411-when-to-turn-on-light)
        * [4.1.2 Dimmer is just a special light](#412-dimmer-is-just-a-special-light)
        * [4.1.3 Advanced light interaction](#413-advanced-light-interaction)
        * [4.1.4 Shared motion sensor](#414-shared-motion-sensor)
        * [4.1.5 Simulate presence during vacation time](#415-simulate-presence-during-vacation-time)
        * [4.1.6 Interaction with other devices](#416-interaction-with-other-devices)
    * [4.2 Security system](#42-security-system)
        * [4.2.1 Alerts](#421-alerts)
        * [4.2.2 Automatic security actions](#422-automatic-security-actions)
            * [4.2.2.1 Arm-stay in the night](#4221-arm-stay-in-the-night)
            * [4.2.2.2 Arm-away while in vacation mode](#4222-arm-away-while-in-vacation-mode)
            * [4.2.2.3 Disarm in the morning](#4223-disarm-in-the-morning)
            * [4.2.2.4 Disarm when the garage door is open](#4224-disarm-when-the-garage-door-is-open)
        * [4.2.3 Day time instrusion prevention](#423-day-time-instrusion-prevention)
        * [4.2.4 Scare the instruder even more when the security system is in alarm mode](#424-scare-the-instruder-even-more-when-the-security-system-is-in-alarm-mode)
        * [4.2.5 Use the arm-away event to trigger the system-wide away mode](#425-use-the-arm-away-event-to-trigger-the-system-wide-away-mode)
    * [4.3 Environment](#43-environment)
        * [4.3.1 Finer control over the furnace and air conditioner](#431-finer-control-over-the-furnace-and-air-conditioner)
        * [4.3.2 Controling the humidifier to reduce condensation.](#432-controling-the-humidifier-to-reduce-condensation)
        * [4.3.3 Alert on tornado warning, high wind or other severe conditions](#433-alert-on-tornado-warning-high-wind-or-other-severe-conditions)
        * [4.3.4 Alert on abnormal conditions inside the house](#434-alert-on-abnormal-conditions-inside-the-house)
        * [4.3.5 Read out the current weather and short term forecast](#435-read-out-the-current-weather-and-short-term-forecast)
    * [4.4 Entertainment/audio related](#44-entertainmentaudio-related)
        * [4.4.1 Play music during specific activities](#441-play-music-during-specific-activities)
        * [4.4.2 Play the mindfulness bell](#442-play-the-mindfulness-bell)
        * [4.4.3 Create a stream-based music player](#443-create-a-stream-based-music-player)
        * [4.4.4 Remind kids to go to bed](#444-remind-kids-to-go-to-bed)
    * [4.5 Productivity](#45-productivity)
        * [4.5.1 Alert if an alternative route to work should be taken](#451-alert-if-an-alternative-route-to-work-should-be-taken)
    * [4.6 Saving money](#46-saving-money)
    * [4.7 User Interface](#47-user-interface)
    * [4.8 System administration](#48-system-administration)
        * [4.8.1 Run daily unit tests](#481-run-daily-unit-tests)
        * [4.8.2 Run timer rule to determine if any devices hasn't been triggered](#482-run-timer-rule-to-determine-if-any-devices-hasnt-been-triggered)
        * [4.8.3 Alert if any battery-powered device is low on battery](#483-alert-if-any-battery-powered-device-is-low-on-battery)
* [5. Layout Model API - an alternative approach to access devices/sensors](#5-layout-model-api---an-alternative-approach-to-access-devicessensors)
    * [5.1 ZoneManager](#51-zonemanager)
    * [5.2 Zone](#52-zone)
    * [5.3 Devices](#53-devices)
    * [5.4 Actions](#54-actions)
    * [5.5 Rules vs actions](#55-rules-vs-actions)
* [6. Key enabler](#6-key-enabler)
    * [6.1 OpenHab controller](#61-openhab-controller)
    * [6.2 Alert](#62-alert)
        * [6.2.1 The Alert API](#621-the-alert-api)
        * [6.2.2 Text-to-Speed engine](#622-text-to-speed-engine)
    * [6.3 Garage opener](#63-garage-opener)
    * [6.4 MQTT](#64-mqtt)
    * [6.5 Presence](#65-presence)
    * [6.6 Plugs](#66-plugs)
    * [6.7 Security System](#67-security-system)
    * [6.8 Switches](#68-switches)
    * [6.9 Thermostats](#69-thermostats)
        * [6.9.1 Temperature sensors](#691-temperature-sensors)
    * [6.10 Zigbee stick](#610-zigbee-stick)
    * [6.11 Zigbee2mqtt](#611-zigbee2mqtt)
    * [6.12 ZWave stick](#612-zwave-stick)
    * [6.14 Others](#614-others)
* [7. Things to avoid](#7-things-to-avoid)

<!-- vim-markdown-toc -->

# 1. What does it mean to be smart?
Everyone is into Smart Home nowaday. However, contrary to what ordinary consumer might think (or led to think), a truely smart home should not require user's explicit instructions such as voice command through Google Assistant or Amazon Alexa.

A truely smart home system would be able to do things for you automatically based on various environmental factors. Its purpose is to simplify your life.  Let's look at an example on how you can check today's weather forecast.

* Level 3 (in the old day): you would open the browser, go to your favorite weather provider, and look up your city.
* Level 2: ask your smart home hub such as Google Home "OK Google, what is the weather like today".
* Level 1: as you step into the kitchen first thing in the morning, your smart home system uses Text-to-speech to read out the current weather, today's forecast, and whatever else you want to read out (e.g. calendar events).

In most cases, you would want the Level 1 notification above. However, occasionally there is a need to query the system for information out of band. We fall back to the middle tier (level 2) of home automation: interaction with the system through voice, applications, or physical devices. Nevertheless, the ultimate goal is still full automation.

# 2. Why is it so difficult to build a truely smart home system?
Coming up with an automation concept isn't that difficult. The lazier you are, the better ideas you can come up with. It is about taking a fresh look at every aspect of our lives, and ask questions such as "What are some of the everyday routines that I'd like to automate?", or "Given the availability of these new devices, what more can I do to simplify my life?"

The main difficulty lies in **integration**. There are so many different devices and hubs with different communication protocols created by different vendors.  Getting them to work together is difficult. It also doesn't help that there is no easy way for the ordinary consumers to create home automation rules. This problem is somewhat similar to trying to automatically generate computer programs from high level UML models back in the 80s and 90s.  Today, sophisticated rules are still in the domain of highly technical users (mainly software developers or super users).

In the future, as more standardization happens (recently Google, Apple, Zigbee and others formed an alliance to create a single connectivity standard), and as software system becomes more sophisticated, it will be possible for the consumer to create rules like this *"OK Google, create this rule 'tell me today's weather forecast when I step into the washroom for the first time in the morning, then play some classical music'"*. It is not all free lunch however, as the user has to supply *contexts* to the system (e.g. what is 'morning' for you).  The user also has to know what rules to create. The assistant helps, but the user needs to play the role of the *programmer* at the conceptual level. Privacy is also a concern, but that is a different topic at this point.

In the short terms, sophisticated rules have to developed or coded.

# 3. High level aspects of smart home system
Home automation can be classified into three main areas:

1. **Take actions**: the rules are triggered by some events, and they perform some actions.
2. **Notify**: an event occurred, and the system needs to notify it to the users.
3. **Query/control**: not rules per say, but this is the exposed interface that let the user query/control the system. Typically, it is through a web application.

As discussed above, it is more desirable to have rules performing actions automaticaly.

# 4. Sample home automation rules

## 4.1 Switches (lights / fans)
Controlling lights is the most common scenario people think of. There are low tech solutions that integrate with a motion sensor. These are relatively cheap and self-operated. However, you can't control them programmatically.

For a fully flexible solution, we would need at minimum one motion sensor and one smart switch in each controllable zone. The basic logic is to turn on the switch when the motion sensor is triggered. Each switch needs to be associated with a timer so that it can be automatically turned off. The timer is started when the switch is turned on, and is renewed if the motion sensor is triggered again.

There are however more nuiances with light control in general. The sections below list some of those aspects. The actions [Turn on Switch](https://github.com/yfaway/openhab-rules/blob/master/automation/jsr223/aaa_modules/layout_model/actions/turn_on_switch.py) and [Turn off Adjacent Zones](https://github.com/yfaway/openhab-rules/blob/master/automation/jsr223/aaa_modules/layout_model/actions/turn_off_adjacent_zones.py) take care of these.

### 4.1.1 When to turn on light?
Naturally light must be turned on when it is dark. One way to do that is based on the sun set time. The [Astro binding](https://www.openhab.org/addons/bindings/astro/) provides this capability. 

But what if there is a lot of cloud today and the zone is just dark. An illumination sensor can be incorporated to measure the illumination level. The rule can define an illumination threshold after which the light is turned on no matter whether it is day or night.

If the light is in a bedroom, it shouldn't be turned on at bed time. This suggests a virtual device that tell the rule when is the bed time for this particular zone. Or more generally, what are the time ranges for no-light.

### 4.1.2 Dimmer is just a special light
A dimmer is just an instance of a light. It knows how to turn on and off. It also has special property to restrict the brightness level between 0% and 100%. This makes it suitable in area such as lobby or washrooms. The rule can adjust the brightness level based on the zone activity. However, in terms of complexity management, it should be the same rule controlling both regular light and dimmer.

### 4.1.3 Advanced light interaction
Sci-fi movies in the past showed the light transition as the main actor moves between zones (the current zone's light is turned on, and the previous zone's light is turned off). This can be done quite easily today. The trick is to define relationships between zones.

Given two zones A and B, the following relationships can be defined:
1. A and B are not connected, and thus is considered closed space. There is no interaction in this case.
2. A is an open space neighbor of B. This is the typical scenario and automatic light transitioning can be done. For example: Foyer, Lobby and Kitchen are linearly connected. As the user opens the front door, Foyer light is turned on. As they walk into the Lobby, the Lobby light is turned on and the Foyer light is turned off. Similar thing with the Kitchen light.
3. A is an open space master of B. Similar with 2) above, but with further rule: as A is considered to be the main zone, if its light is already on, then B's light won't be turned on even if its motion sensor was triggered.
4. A is an open space slave of B. This is just a reverse of 3).

### 4.1.4 Shared motion sensor
In open space houses, a motion sensor might cover mulitple zones. Which zone's light should be turned on when the motion sensor is triggerred? A special flag might be used here to indicate which zone takes precedent.

### 4.1.5 Simulate presence during vacation time
When on extended vacations, the smart lights in the house can be programmed to simulate owner presence (thief prevention). The rule to do this is quite simple.
1. Triggered at sunset time.
2. Loop until bed time or when the house is unarmed or when stopped from the control panel.
3. Randomize a light-on period in minutes.
4. Pick one of the light, and turn it on for the random period above.
5. Sleep for that duration and loop again with another light and another light-on period.

This Xtend [light vacation](https://github.com/yfaway/openhab-rules/blob/master/rules/lights-vacation-mode.rules) does just that. Eventually it will be converted to Python using the layout model APIs.

### 4.1.6 Interaction with other devices
The switches can be both the originator (triggering other actions) or the receiver (to turn itself on/off) from other actions.

Here are some examples:
* When the washroom fan is turned on (indicating that someone is taking a shower), play some music and also turn on the furnace fan.
* When the smoke alarm beeps, turn on all lights.

## 4.2 Security system
Modern house may have an wired security system. This is the most reliable way to secure a house. If you are building a new home, ensure to pay for this upgrade.

An wired security system gives you a lot of sensors: boundary door sensors, windows sensors, motion sensor, security panel, and possibly a smoke sensor. Doing this using wireless technology is possible, but it will be a lot of work, expensive and not as reliable.

The number of sensors gives you many possible integration opportunities.

### 4.2.1 Alerts
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

### 4.2.2 Automatic security actions
Reference: [Security Actions](https://github.com/yfaway/openhab-rules/blob/master/automation/jsr223/aaa_modules/layout_model/actions/simulate_daytime_presence.py) rules.

#### 4.2.2.1 Arm-stay in the night
A simple rule can help to ensure that the house is always armed in the *stay* mode in the evening, while taking into account the possible walk-ins to the garage.

This can be done by using a series of time-triggered event 15 minutes apart, starting from say 8PM to 2AM. Each 15 minute, the rule checks if the system is armed, if not, it arms in the *stay* mode.

As the owners go in/out to/from the garage, they don't need to remember to arm it again. This is now automatic.

#### 4.2.2.2 Arm-away while in vacation mode
If you are on vacation, you want the house to be in the *arm-away* mode. But what if you have plants in the house, and have to ask friends to come by to water them. A way to ensure that the system continues to be armed after they leave is to detect a presence-off event (no one is inside the house), arm the system sometimes after that.

#### 4.2.2.3 Disarm in the morning
Two options:
1. Hard-code the time to disarm the system in the morning.
2. Put a motion sensor in the foyer or common area. As the motion sensor is triggerred in the *wake-up* time period, disarm the system.

#### 4.2.2.4 Disarm when the garage door is open
If the garage door is open, and the system detects that it is one of the user going home, automatically disarm the alarm system. The following devices would be needed:
* Smart garage door opener.
* Presence devices (cell phone or WiFi/bluetooth dongles).
* Security system.

Relying on the cellphone is this case will be hit or miss. Cellphones are optimized to conserve the battery, so unless the owners start using the phone, the system won't be able to determine presence based on network devices. A dedicated WiFi/bluetooth dongle would be more reliable.

### 4.2.3 Day time instrusion prevention
In certain areas, there are blazing house break-in in the day time when the owners are away at work.  One way to prevent that is to fake owner presence by playing loud music as someone approachs the house. The following devices would be needed:
* A way to indicate that the user is away. The arm-away mode of an security system is a perfect way to do this.
* An exterior motion sensor.
* An audio device on the first floor.

When the motion sensor is triggered, if the system is in arm-away mode, play some loud music on the audio device. Turn off the music after some minutes.

See [Simulate Daytime Presence](https://github.com/yfaway/openhab-rules/blob/master/automation/jsr223/aaa_modules/layout_model/actions/simulate_daytime_presence.py) action.

### 4.2.4 Scare the instruder even more when the security system is in alarm mode
See [GH-19](https://github.com/yfaway/openhab-rules/issues/19) issue.

Here's the basic idea:
* Triggered when security system is in alarm.
* If this is light-on time, turn on all smart light.
* Play loud text-to-speed messages on the main floor audio sink.
    * First message: "Communicating with the alarm monitoring company."
    * Subsequence messages in a loop: "Police has been dispatched" ...
* Stop the rule when the system is disarmed.

### 4.2.5 Use the arm-away event to trigger the system-wide away mode
Presence detection is a complex area. There are many devices that can indicate the presence of the occupants in a house such as motion sensors, light-on status, network devices, and bluetooth devices. They work well but are not always accurate.

The security system's *arm-away* event however provides an absolute certainty that there is no one at home. This allows rule to do multitude of things such as:
* Turn off all lights;
* Turn off all audio devices;
* Turn off all smart plugs;
* Change the furnace/AC to 'away' mode.

That saves time and money.

## 4.3 Environment
Environment refers to the outdoor weather as well as the indoor temperature and humidity.

### 4.3.1 Finer control over the furnace and air conditioner
Every smart thermostat allows the user to set different time periods such as 'home', 'away', or 'sleep'. These are fixed for each day of the week. With the help of other devices/sensors we can make these periods a lot more precise.

For example, when the security system is armed away, this indicates there won't be any user at home. The thermostat can then be switched over to 'away' mode immediately. And as the system is disarmed, it switches back to 'home' mode.

### 4.3.2 Controling the humidifier to reduce condensation.
In many areas in Canada, it is very dry in the winter. Many houses are equipped with a whole-house humidifer unit, which is typically hook up with the furnace. As the furnace runs, the humidifier emits water vapour.  That is all good except when the outdoor weather is very cold, in which case the high humidity level inside the house will cause condensation on the windows.

Thus the humidifier has to be constantly adjusted based on the temperature outside. If you can hook up the humidifier to the smart thermostat, a rule can be created to adjust the humid level based on the outdoor temperature. The rule can be ran couple times per day.

### 4.3.3 Alert on tornado warning, high wind or other severe conditions
Some weather services provide emergency warnings such as incoming tornado. A rule can be set up to provide audible notice (through the Google Chromecast for example) to the occupants.

If the house has big tall tree nearby and if the forecast indicates high wind gust, another rule can be created to provide alert and allow moving the occupant to another area.

### 4.3.4 Alert on abnormal conditions inside the house
Temperature and humid sensors are relatively cheap. Beside the main thermostat, additional sensors can be placed throughout the house and a rule can be created to provide alert if the temperature or humid level falls outside the normal ranges.

### 4.3.5 Read out the current weather and short term forecast
There is no need to explicitly ask for the weather info to determine what we shall wear for the day. If you have the following services/devices, the system can provide that info automatically.
* Motion sensor
* Text-to-speed service
* Weather service
* Audio sink such as Chromecast
* Spefication for *wake-up* time.

A motion sensor can be placed in the washroom on common area. As it is triggered for the first time by the motion sensor, it determines if this is *wake-up* time. If yes, query weather service, formulate the text, and read it out on the audio sink.

## 4.4 Entertainment/audio related

### 4.4.1 Play music during specific activities
Reference: [music-and-announcement](https://github.com/yfaway/openhab-rules/blob/master/automation/jsr223/music-and-announcement.py)

### 4.4.2 Play the mindfulness bell
Reference: [play-mindfullness-bell](https://github.com/yfaway/openhab-rules/blob/master/automation/jsr223/play-mindfullness-bell.py)

### 4.4.3 Create a stream-based music player
A single Player and Volume control for the selected chromecast and music stream. Switching the chromecast or stream automaticaly play/re-cast the right music. Can select a single chrome cast or multiple.
Reference: [chrome-cast-master-control](https://github.com/yfaway/openhab-rules/blob/master/automation/jsr223/chrome-cast-master-control.py)

### 4.4.4 Remind kids to go to bed
* Tell kids to go to bed at 8:30 and 8:45; on the second notice, turn off the first floor lights as well.
Reference: [kids-sleep-time-reminder](https://github.com/yfaway/openhab-rules/blob/master/automation/jsr223/kids-sleep-time-reminder.py)

## 4.5 Productivity
### 4.5.1 Alert if an alternative route to work should be taken
One or more route profiles can be configured in transform/routes.map file. Each profile specifies the destination address, the time range and the typical travelled road names. When the garage or front door is open, the rule will check if the current time is in the time range. If yes, it requests a route to the destination address using Google Maps service. If the route is different from a normally travelled route, it will send an email alert to the user.

## 4.6 Saving money
* Turn on/off plugs or lights based on the security arm status, vacation mode, and hours of days.
* Turn on/off associated light when a smart plug power wattage crosses a threshold. E.g. turn on the office light when the PC is turned on.

## 4.7 User Interface
* Garage door status.
* Security system status.
* Presence.
* Indoor temperature & humidity and forecasted weather inclduing Environment Canada alert.
* Lights, fans, and smart plug status.
* Motion sensors states.
* Music stream control.
* Camera snapshot viewer.

## 4.8 System administration
This section does not concern with the end-user rules, but it lists things that can be done to ensure the system is running correctly.

### 4.8.1 Run daily unit tests
Reference: [zzz-run-unit-tests](https://github.com/yfaway/openhab-rules/blob/master/automation/jsr223/zzz-run-unit-tests.py)

The majority of the library code in this project has unit tests. A single Python rule is used to find all unit tests within a folder and run them nightly. If there is any failed test, an alert is send to the administrator.

To speed up tests, a mocked event dispatcher is used in all the tests code instead of `scope.event`. This allows changing the state of an OpenHab item synchronously and directly instead of asynchronously going through the event bus.

### 4.8.2 Run timer rule to determine if any devices hasn't been triggered
Reference: [alert_on_inactive_battery_devices](https://github.com/yfaway/openhab-rules/blob/master/automation/jsr223/alert_on_inactive_battery_devices.py)

Wireless connection (WiFi, Zigbee or ZWave) can be flaky. The device could be off due to router issue or coordinator issue. One way to determine failed device is to see if it has not been triggered for a while. The script above does just that.

### 4.8.3 Alert if any battery-powered device is low on battery
tbd

# 5. Layout Model API - an alternative approach to access devices/sensors
In OpenHab, items are defined in a flat manner in .items files under /etc/openhab2/items folder. They are usually linked to a channel exposed by the underlying hardware (vitual items do not link to any).

This flat structure has an impact on how rules (whether in Xtend or Python) are organized. When the rules need to interact with mulitple devices of the same type, they can utilize the [group concept](https://www.openhab.org/docs/configuration/items.html#groups). An example of good usage of group is to turn off all lights. By linking all smart lights to a group switch, turning off all the lights can be done by changing the state of the group switch to OFF.

What is more tricky is when rules need to interact with different devices within the same area. The typical solution is to group unrelated items that belong to the same zone either by using naming pattern, or by dedicated groups. For example, the light switch and motion sensor in the Foyer area can be named like this: "FF_Foyer_Light", and "FF_Foyer_MotionSensor". When a sensor is triggered, the zone can be derived from the name of the triggering item, and other devices/sensors can be retrieved using that naming convention.

This project provides another approach through the [Layout Model API](https://github.com/yfaway/openhab-rules/tree/master/automation/jsr223/aaa_modules/layout_model). The idea is to provide a layer above the devices/sensors (this is somewhat similar to the difference between database relational model versus ORM). Each house (a ZoneManager) contains multiple rooms (Zones), and each room contains multiple devices. Each zone is associated with a set of actions. The usual OpenHab events are routed in this manner: `OpenHab events --> ZoneManager --> Zones --> Actions`. It provides a level of abstraction on top of the raw items. The actions can operate on the abstract devices and do not concern about the naming of the items. Rather than write Python rules, you would write actions. Actions can be unit-tested with various levels of mocking.

> **_NOTE:_** This API is documented at https://yfaway.github.io/. It is not up to date however.

Sample action to turn off lights in neighboring zones:
`
    def onAction(self, eventInfo):
        events = eventInfo.getEventDispatcher()
        zone = eventInfo.getZone()
        zoneManager = eventInfo.getZoneManager()

        if None == zoneManager:
            raise ValueError('zoneManager must be specified')

        lights = zone.getDevicesByType(Light)
        if len(lights) == 0:
            return False

        adjacentZones = zone.getNeighborZones(zoneManager,
                [NeighborType.OPEN_SPACE, NeighborType.OPEN_SPACE_SLAVE])
        for z in adjacentZones:
            if z.isLightOn():
                z.turnOffLights(events)
        
        return True
`

## 5.1 ZoneManager
There are two kinds of ZoneManager. The [mutable one](https://github.com/yfaway/openhab-rules/blob/master/automation/jsr223/aaa_modules/layout_model/zone_manager.py) is constructed once when OpenHab starts up in order to create the zones. In this specific project, the [ZoneParser](https://github.com/yfaway/openhab-rules/blob/master/automation/jsr223/aaa_modules/zone_parser.py) class parses from the existing .items files to construct a ZoneManager instance. The [configure_zone_manager.py](https://github.com/yfaway/openhab-rules/blob/master/automation/jsr223/configure_zone_manager.py) script uses the ZoneParser to populate the ZoneManager, add actions to the zones, and then puts an instance of ImmutableZoneManager on the script context. Other mechanisms can be used to populate the ZoneManager.

Instances of the [ImmutableZoneManager](https://github.com/yfaway/openhab-rules/blob/master/automation/jsr223/aaa_modules/layout_model/immutable_zone_manager.py) class are parsed around to the zones, and the actions. It provides access to zones and devices without allowing modification to its states.

## 5.2 Zone
Each immutable [Zone](https://github.com/yfaway/openhab-rules/blob/master/automation/jsr223/aaa_modules/layout_model/zone.py) instance maps to a room or an area within the house. The Zone class provides APIs to:
* Manage neighbor zones,
* Manage devices/sensors,
* Manage actions,
* Dispatch events.

Any method with side-effect semantic returns a new instance of Zone. Note that Zone is immutable but the devices/sensors contained within may not.

## 5.3 Devices
The devices classes inherit from [Device](https://github.com/yfaway/openhab-rules/blob/master/automation/jsr223/aaa_modules/layout_model/device.py). They are either virtual or backed by one or more OpenHab items. They provide APIs to change their states.

The following devices are available at this point:
* ActivityTime: a virtual device to capture the time ranges for different activities in the house such as wake-up time, quiet time, dinner time, sleep time, and so on.
* AlarmPartition: a DSC Alarm backed device to allow arming/disarming the house.
* AstroSensor: provides sunrise and sunset time.
* Camera: provide APIs to query for motion and for image snapshots. The current impl relies on a network share containing images produced by camera managed by the MotionEyesOS (run on a PI).
* ChromecastAudioSink: an audio sink backed by Chromecast.
* Contact: for doors, windows, and similar devices.
* Dimmer: a Light-derived class.
* IlluminanceSensor: query the brightness level.
* MotionSensor
* NetworkPresence: detects presence by doing network IP scan.
* Plug: smart plug, currently backed by the TP Link plugs.
* Switch: contains specific classes for Fan and Light.

Additional devices or specific implementation can be added through the inheritance mechanism.

## 5.4 Actions
In the Layout Model APIs, in most cases, actions are used instead of regular Python rules. They derive from the [Action](https://github.com/yfaway/openhab-rules/blob/master/automation/jsr223/aaa_modules/layout_model/action.py) class and are registerd with each zone through `Zone::addAction()`.

When an action is triggered, it has access to the event, the triggered item, the zone, and the zone manager. I.e. it has access to all the devices within the zone and within the whole house without needing to know of the devices' naming convention.

## 5.5 Rules vs actions
If a rule is trigged by a device, create an action and register it with the zone.

On the other hand, if a rule is trigged by a cron time, it is simpler to use a regular Python rule. The script still has access to the `ImmutableZoneManager` through the script context `zm`.

# 6. Key enabler
This section lists the essential technologies and devices to enable the rules above.

## 6.1 OpenHab controller
This is the heart of the system. Any machine can run OpenHab. What many people use is vanilla OpenHab on the Raspberry PI 3. If you don't need to run another other software on the PI, you can also use the [OpenHabian](https://www.openhab.org/docs/installation/openhabian.html) distribution. For people new to OpenHab, OpenHabian is the best option as it pre-installs a lot of the neeed home automation software.

## 6.2 Alert
There are multitude of ways to send notification for events. The traditional approach is emailing using the [Mail](https://www.openhab.org/addons/bindings/mail/) binding, but there are also social networking messages.

For local notification, when the users are home, voice or light colour changes or similar mechanism can be used. The most common one is using an audio sink (the Google Home/mini, Chromecast, or Chromecast Audio work well via the [Chromecast](https://www.openhab.org/addons/bindings/chromecast/) binding).

### 6.2.1 The Alert API
The [Alert](https://github.com/yfaway/openhab-rules/blob/master/automation/jsr223/aaa_modules/alert.py) and [AlertManager](https://github.com/yfaway/openhab-rules/blob/master/automation/jsr223/aaa_modules/alert_manager.py) classes provide a simple API to send alerts. There is a decoupling between the alert message and the execution of the alert itself. The rules and actions only need to classify the criticality of the alert. The AlertManager will determine the appropriate actions.

For example, normal alert is sent to the email address of every users in the household. In addition, if the users are home and it is not sleep time, the alert is also played on the audio sink via TTS. The implementation of the AlertManager will make use of various devices/sensors in the house.

### 6.2.2 Text-to-Speed engine
Either Google Cloud TTS or VocieRSS would work. The "Marry TTS" is very slow on the Raspberry PI. Once downloaded, in the Paper UI, go to Configuration -> System -> Voice (at the very end of the page) to configure the default engine.

## 6.3 Garage opener
Any Chamberlain garage door opener can be controlled via the [Chamberlain MyQ](https://docs.openhab.org/addons/bindings/myq1/readme.html) binding. Note that Chamberlain is pretty bad with break APIs; so expect churns.

For non-WiFi-connected garage door opener, there are other approaches to detect when the door is open/closed.

## 6.4 MQTT
A light weight protocol that transports messages between device. On Linux, the most common implementation is [Mosquito](https://mosquitto.org/). MQTT is integratd with OpenHav via the [MQTT](https://www.openhab.org/addons/bindings/mqtt1/) binding.

## 6.5 Presence
Presence is a very important aspect in home automation. Depending on the requirement, it could be course grain (is someone home?), or fine grain (is someone in this particular zone?). Below are several ways to achieve this:
* **Network devices**: laptop, PC, cell phones. The [Network](https://docs.openhab.org/addons/bindings/network/readme.html) binding is used to scan for device presence on the network. The idea is that if the device is in the network, the user is home. Note that cell phones are now optimized to reduce battery consumption, so when not in used, they might be off the network as well.
* **Motion sensor**: These are relatively cheap device, especially Zigbee devices. They provide fine location info. This project uses the Xiaomi Aqara Motion Sensor (Zigbee).
* **Security system**: The DSC Security System with EnvisaLink inteface is used in this project. It provides course grain location info.
* **Light**: If a light is on, it is likely that the zone is occupied. Not reliable and only work in night time.

Others: Bluetooth / WiFi dongles.

The Zone API provides this method: `Zone::isOccupied(self, secondsFromLastEvent = 5 * 60)`.

## 6.6 Plugs
TP-Link HS100 WiFi Plug via [TPLinkSmartHome](https://www.openhab.org/addons/bindings/tplinksmarthome/) binding.

## 6.7 Security System
DSC Security System with the [EnvisaLink](http://www.eyezon.com/index.php) module via the [DSC Alarm](https://www.openhab.org/addons/bindings/dscalarm/) binding.

## 6.8 Switches
Many consumer uses smart light bulbs. It is convenient and quick to install, but is not the best approach. Changing to a smart switch is the more permanent solution. Nowadays, the smart switches can communicate via WiFi, Zigbee, or ZWave. Ensure that the one you buy are compliant with the electrical code in your region. In addition, be aware that WiFi devices might suffer from inteferences in the 2.4 Ghz band. Finally, if the switch drives a motor such as a washroom exhaust fan, make sure that it can handle the inductive load.

This project uses the two ZWave switches Inovelli NZW30 and Leviton DZ15S through the [ZWave](https://www.openhab.org/addons/bindings/zwave/#supported-things) binding. The latter can control fans as well.

Another approach is to make an existing switch smart by using devices such as Sonoff or Shelly.

## 6.9 Thermostats
The two commons one are the Nest Eco and the EcoBee. The Ecobee3 is used in this project through the [Ecobee](https://docs.openhab.org/addons/bindings/ecobee1/readme.html) binding.

### 6.9.1 Temperature sensors
Xaoimi Aqara Temperature Sensor (Zigbee).

## 6.10 Zigbee stick
A single Zigbee USB stick is needed in order to support Zigbee devices. The [Zigbee](https://www.openhab.org/addons/bindings/zigbee/) binding recommends the Ember controller.

This project uses the Texas Instrument CC2531 USB stick. It is no longer supported, and it doesn't work very well with the Zigbee binding. However, it works well when used in conjunction with zigbee2mqtt. Note that the range of the CC2531 isn't very far, so additional CC2531 routers should be incorporated into the network.

## 6.11 Zigbee2mqtt
The [zigbee2mqtt](https://www.zigbee2mqtt.io/) software provides an alternative approach to communicating with Zigbee devices.It maps Zigbee device events to mqtt events, which can then be routed to OpenHab. Zigbee2mqtt supports many devices, including the non-standard compliant Xiaomi Aqara (which doesn't work well with the Zigbee binding). 

## 6.12 ZWave stick
The Aeotec Z-Wave USB ZStick Gen 5 is the recommended stick for the [ZWave](https://www.openhab.org/addons/bindings/zwave/) binding. It acts as a coordinator for all ZWave devices.

## 6.14 Others
* [Astro](https://docs.openhab.org/addons/bindings/astro/readme.html) - to determine sunrise and sunset time

# 7. Things to avoid
* Avoid the cloud: dependency on the cloud means that you are at the mercy of the service provider. If their server goes down or if they discontinue the product, your device becomes a brick. Always go with devices associated with open specs such as ZWave or Zigbee devices, or go with devices that have custom firmware that can bypass the cloud.
* Security: if you do have to go with devices that are connected to the Internet, either put them in a separate WiFi network disjoint from the main network, or configure the router to disable Internet access for those devices.
* Reduce complexity
* Non-compliant devices: when it comes to hardwire devices such as wall switches or plugs, ensure that the devices are compliant with the regional electrical code. Otherwise if it causes fire, the insurance company won't cover the damage.
