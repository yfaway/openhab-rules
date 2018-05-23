# openhab-rules
A set of rules for my house.

# Prerequisites
The following sensors, bindings, actions, and transformations need to be present and installed for the rules to work.

**Sensors**
1. Chamberlain 3/4 HPS Belt Drive Garage Door Opener Built-in Wifi (LW6000WFC)
2. DSC Security System

**Bindings**
1. [Chamberlain MyQ Binding](https://docs.openhab.org/addons/bindings/myq1/readme.html)
2. [DSC Alarm Binding](https://docs.openhab.org/addons/bindings/dscalarm/readme.html)
3. [Network Binding](https://docs.openhab.org/addons/bindings/network/readme.html) - for presence detection by phone

**Actions**
1. [Mail Actions](https://docs.openhab.org/addons/actions/mail/readme.html) - for sending email alerts

**Transformations**
1. [JsonPath](https://docs.openhab.org/addons/transformations/jsonpath/readme.html)
2. [Map](https://docs.openhab.org/addons/transformations/map/readme.html)

# Current Functionalities
## Alerts
* Garage door remains open after a period of time.
* Security alarm triggers with fire/smoke alarm and zone indication (plus mapping from zone to actual items in the house).
* A zone tripped when system is not armed, and an owner is not home, and within a specific period. 

## Display
* Garage door status.
* Presence.
* Security system status.

## Presence
* Cell phone wifi connection using Network binding.
* Security motion sensor (if triggered, set to be good for the next 5 minutes).

## Security Actions
* Automatically “armed stay” in the night if someone is home.
* Automatically unarm in the morning before going to work.
* Automatically unarm if an owner open the garage door from the outside.
* Automatically unarm if garage door is open from Hab UI.
