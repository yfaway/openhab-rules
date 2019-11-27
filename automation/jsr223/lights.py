from core import osgi
from core.rules import rule
from core.triggers import when
from org.eclipse.smarthome.core.items import Metadata
from org.eclipse.smarthome.core.items import MetadataKey
from org.eclipse.smarthome.core.library.items import DimmerItem
from org.joda.time import DateTime

from aaa_modules import switch_manager
from aaa_modules import security_manager
from aaa_modules import time_utilities

scriptExtension.importPreset("RuleSupport")
scriptExtension.importPreset("RuleSimple")

MetadataRegistry = osgi.get_service("org.eclipse.smarthome.core.items.MetadataRegistry")

# The period of time in seconds (from the last timestamp a switch was turned
# off) to ignore the ON command trigged by the motion sensor. This takes care
# of the scenario when the user manually turns off a light, but that physical
# spot is covered by a motion sensor, which immediately turns on the light
# again.
DELAY_AFTER_LAST_OFF_TIME_IN_MS = 8000 # 8 secs

# The light level threshold; if it is below this value, turn on the light.
ILLUMINANCE_THRESHOLD_IN_LUX = 8

# This Item tag indicates that the switch shares a motion sensor with one
# or more other switches. These switches then share the same
# DELAY_AFTER_LAST_OFF_TIME_IN_MS value. I.e. if a switch is just turned
# off, for the next couple seconds any motion sensor triggering will do
# nothing. This is because the user is getting out of the zone, and thus it
# is wrong to turn on another light.
TAG_SHARED_MOTION_SENSOR = "shared-motion-sensor"

# Indicates that the switch must not be turned on when the associated 
# motion sensor is triggered.
TAG_DISABLE_TRIGGERING_FROM_MOTION_SENSOR = "disable-triggering-from-motion-sensor"

# A metadata item to indicate which light to turn off when the current light
# is switched on.
META_TURN_OFF_OTHER_LIGHT = 'turnOff'

# A meta data item to indicate that this light shouldn't be turned on when a
# motion event is triggered, if the other light is already on.
META_DISABLE_MOTION_TRIGGERING_IF_OTHER_LIGHT_IS_ON = 'disableMotionTriggeringIfOtherLightIsOn'

META_DIMMING_SETTING = 'dimmable'

lastOffTimes = {}

@rule("Update light-on time")
#@when("System started")
@when("Item VT_Time_Of_Day changed")
def setLightOnTime(event):
  state = items["VT_Time_Of_Day"]
  if state == StringType("EVENING") or state == StringType("NIGHT") \
        or state == StringType("BED"):
    events.sendCommand("VT_Time_LightOn", "ON")
  else:
    events.sendCommand("VT_Time_LightOn", "OFF")


@rule("Turn off all lights when armed away")
@when(security_manager.WHEN_CHANGED_TO_ARMED_AWAY)
def turnOffAllLights(event):
    events.sendCommand(switch_manager.GROUP_LIGHT_SWITCH, "OFF")

#@rule("Turn on light when motion sensor triggered")
#@when("Member of gWallSwitchMotionSensor changed to ON")
def turnOnSwitchOrRenewTimer(motionSensorEvent):
    triggeringItem = itemRegistry.getItem(motionSensorEvent.itemName)
    localIdx = triggeringItem.name.rfind("_")
    switchName = triggeringItem.name[:localIdx]

    if switchName not in items:
        return

    switchItem = itemRegistry.getItem(switchName)
    
    if switch_manager.isSwitchOn(switchItem):
        # renew timer
        timerName = switchName + "_Timer"
        events.sendCommand(timerName, "ON")
        return

    
    # the associate switch was on; let's do further processing.

    # Is this a fan switch?
    isFanSwitch = ("FanSwitch" in switchName)

    # This check needs to be here rather than in the outter scope because
    # the user might have turned on the light before the programmed 
    # light on time. In such case, we continue to maintain the timer.
    if items["VT_Time_LightOn"] != ON and (not isFanSwitch):
        # check if there is a valid illuminance value
        illuminanceName = switchName + "_Illuminance"
        if illuminanceName not in items:
            return

        illuminanceItem = itemRegistry.getItem(illuminanceName)
        if UnDefType.NULL == illuminanceItem.state or UnDefType.UNDEF == illuminanceItem.state:
            return
        elif illuminanceItem.state > DecimalType(ILLUMINANCE_THRESHOLD_IN_LUX):
            return
        # else pass through to turn on the light
    
    # If a wall switch was just turned off, ignore the motion sensor event.
    if switchName in lastOffTimes:
        timestamp = lastOffTimes[switchName]
        if (DateTime.now().getMillis() - timestamp <= DELAY_AFTER_LAST_OFF_TIME_IN_MS):
            return

    # An open area might have multiple lights with a shared motion sensor
    # (e.g. in the security system motion sensor where the motion sensor
    # tends to be in a corner and cover the whole lobby). In this case, we
    # only want to trigger a single light if all lights were off. However,
    # if any light is already on, we still want to renew the timer to keep
    # the light on.
    #
    # Check to see if the motion sensor is allowed to trigger the light.
    if switchItem.hasTag(TAG_DISABLE_TRIGGERING_FROM_MOTION_SENSOR):
        return

    # Check to see if there is a dependent relationship between lights.
    # I.e. if light B is already on, then don't turn on light A if its
    # motion sensor is triggered.
    meta = MetadataRegistry.get(
            MetadataKey(META_DISABLE_MOTION_TRIGGERING_IF_OTHER_LIGHT_IS_ON,
                switchName)) 
    if None != meta and meta.value in items:
        # see if the other light is on
        theOtherLight = itemRegistry.getItem(meta.value)

        if switch_manager.isSwitchOn(theOtherLight):
            return
        elif switchItem.hasTag(TAG_SHARED_MOTION_SENSOR):
            # If it was just turned off, then don't trigger this light yet.
            # This might be the case that the user is getting out of this zone
            if theOtherLight.name in lastOffTimes:
                timestamp = lastOffTimes[theOtherLight.name]
                if (DateTime.now().getMillis() - timestamp <= DELAY_AFTER_LAST_OFF_TIME_IN_MS):
                    return
        # else - pass through

    if isinstance(switchItem, DimmerItem):
        meta = MetadataRegistry.get(
                MetadataKey(META_DIMMING_SETTING, switchName)) 
        if None != meta:
            config = meta.configuration
            level = config['level']
            timeRanges = config['timeRanges']

            if time_utilities.isInTimeRange(timeRanges):
                events.sendCommand(switchItem.name, str(level))
            else:
                events.sendCommand(switchItem.name, "100")
        else:
            events.sendCommand(switchItem.name, "100")
    else:
        events.sendCommand(switchItem.name, "ON")

#@rule("Set a timer to turn off the switch after it was programatically turned on")
#@when("Member of gWallSwitch changed")
def setTimerWhenSwitchIsTurnedOn(switchEvent):
    triggeringItem = itemRegistry.getItem(switchEvent.itemName)

    timerItemName = triggeringItem.name + "_Timer"

    # Some light might stay on until manually turned off, so the timer item
    # could be null.
    if switch_manager.isSwitchOn(triggeringItem):
        # When in vacation mode, the lights be turned on/off randomly to
        # simulate presence (thief prevention). The simulation rule has full
        # control of the lights; thus we don't want to enable the timer.
        isFanItem = "FanSwitch" in triggeringItem.name
        if (not security_manager.isInVacation(items)) or isFanItem:
            if timerItemName in items:
                events.sendCommand(timerItemName, "ON")

            meta = MetadataRegistry.get(MetadataKey(META_TURN_OFF_OTHER_LIGHT,
                        switchEvent.itemName)) 
            if None != meta:
                stringItemName = meta.value
                if stringItemName in items:
                    events.sendCommand(stringItemName, "OFF")
    else:
      if timerItemName in items:
            events.sendCommand(timerItemName, "OFF")

      lastOffTimes[triggeringItem.name] = DateTime.now().getMillis()

#@rule("Turn off wall switch when timer expires")
#@when("Member of gWallSwitchTimer changed to OFF")
def turnOffWallSwitch(timerEvent):
    triggeringItem = itemRegistry.getItem(timerEvent.itemName)
    localIdx = triggeringItem.name.rfind("_")
    switchName = triggeringItem.name[:localIdx]

    # Check if motion sensor state is still on; if yes, renew timer. This
    # take care of the situation where there is constant activity and thus
    # the motion sensor was never shut off --> timer wasn't being renewed.
    motionSensorName = switchName + "_MotionSensor"
    motionSensorItems = filter(lambda item: item.name == motionSensorName, 
            ir.getItem(switch_manager.GROUP_WALL_SWITCH_MOTION_SENSOR).members)

    if len(motionSensorItems) > 0 and motionSensorItems[0] == ON:
        events.sendCommand(triggeringItem.name, "ON")
    else:
        target = filter(lambda item: item.name == switchName, 
                ir.getItem(switch_manager.GROUP_WALL_SWITCH).members)[0]
        if switch_manager.isSwitchOn(target):
            events.sendCommand(target.name, "OFF")

#@rule("Hello World timer rule")
#@when("Time cron 0/45 * * * * ?")
#def hellowWorldDecorator(event):
    #item = itemRegistry.getItem("SF_Lobby_LightSwitch")

    #turnOffWallSwitch("FF_Foyer_LightSwitch_Timer")
    #meta = MetadataRegistry.get(MetadataKey("light", "SF_Lobby_LightSwitch")) 
    #config = meta.configuration
    #PE.logInfo("meta: " + str(config["level"]))


# TODO remove when @when supports "System started".
setLightOnTime(None)
