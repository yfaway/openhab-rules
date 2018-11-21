from org.slf4j import Logger, LoggerFactory
from openhab import osgi
from openhab.rules import rule
from openhab.triggers import when
from org.eclipse.smarthome.core.items import Metadata
from org.eclipse.smarthome.core.items import MetadataKey
from org.eclipse.smarthome.core.library.items import DimmerItem

import constants
reload(constants)
from constants import *

scriptExtension.importPreset("RuleSupport")
scriptExtension.importPreset("RuleSimple")

MetadataRegistry = osgi.get_service("org.eclipse.smarthome.core.items.MetadataRegistry")
log = LoggerFactory.getLogger("org.eclipse.smarthome.model.script.Rules")

@rule("Turn off all lights when armed away")
@when("Item {0} changed to {1:d}".format(SECURITY_ITEM_ARM_MODE, SECURITY_STATE_ARM_AWAY))
def turnOffAllLights(event):
    events.sendCommand(GROUP_LIGHT_SWITCHS, "OFF")

@rule("Turn on light when motion sensor triggered")
@when("Member of gWallSwitchMotionSensor changed to ON")
def turnOnSwitchOrRenewTimer(motionSensorEvent):
    triggeringItem = itemRegistry.getItem(motionSensorEvent.itemName)
    localIdx = triggeringItem.name.rfind("_")
    switchName = triggeringItem.name[:localIdx]

    switchItem = itemRegistry.getItem(switchName)
    if null === switchItem:
        return
    
    if isSwitchOn(switchItem):
        # renew timer
        timerName = switchName + "_Timer"
        timerItem = itemRegistry.getItem(timerName)
        timerItem.sendCommand(ON)
        return

    
    # the associate switch was on; let's do further processing.

    # Is this a fan switch?
    isFanSwitch = switchName.endsWith("FanSwitch")

    # This check needs to be here rather than in the outter scope because
    # the user might have turned on the light before the programmed 
    # light on time. In such case, we continue to maintain the timer.
    if items["VT_Time_LightOn"].state != ON and ! isFanSwitch:
        # check if there is a valid illuminance value
        illuminanceName = switchName + "_Illuminance"
        if illuminanceName not in  items:
            return

        illuminanceItem = items[illuminanceName]
        if UnDefType.NULL == illuminanceItem.state or UnDefType.UNDEF == illuminanceItem.state:
            return
        elif illuminanceItem.state > DecimalType(ILLUMINANCE_THRESHOLD_IN_LUX):
            return
        # else pass through to turn on the light
    
    # If a wall switch was just turned off, ignore the motion sensor event.
    #if ( lastOffTimes.containsKey(switchItem.name) ) {
    #  val long timestamp = lastOffTimes.get(switchItem.name)
    #  if (now.getMillis() - timestamp <= DELAY_AFTER_LAST_OFF_TIME_IN_MS) {
    #    return
    #  }
    #}

    # An open area might have multiple lights with a shared motion sensor
    # (e.g. in the security system motion sensor where the motion sensor
    # tends to be in a corner and cover the whole lobby). In this case, we
    # only want to trigger a single light if all lights were off. However,
    # if any light is already on, we still want to renew the timer to keep
    # the light on.
    #
    # Check to see if the motion sensor is allowed to trigger the light.
    disableAlwaysItemName = triggeringItem.name + "_DisableTriggeringAlways"
    if disableAlwaysItemName in items and items[disableAlwaysItemName].state == ON:
        return

    # Check to see if there is a dependent relationship between lights.
    # I.e. if light B is already on, then don't turn on light A if its
    # motion sensor is triggered.
    disableIfItemName = triggeringItem.name + "_DisableTriggeringIf"
    val disableTriggeringIfItem = gMotionSensorDisableTriggeringIf.members.findFirst[ 
        t | t.name == disableIfItemName 
    ]

    if UnDefType.NULL == illuminanceItem.state or UnDefType.UNDEF == illuminanceItem.state:

    if disableTriggeringIfItem in items \
        && UnDefType.NULL != items[disableTriggeringIfItem].state \
        && UnDefType.UNDEF != items[disableTriggeringIfItem].state:
        # see if the other light is on
        val theOtherLight = gWallSwitch.members.findFirst[ 
          t | t.name == disableTriggeringIfItem.state.toString ]

      if isSwitchOn(theOtherLight):
        return
      #elif switchItem.hasTag(TAG_SHARED_MOTION_SENSOR):
        # If it was just turned off, then don't trigger this light yet.
        # This might be the case that the user is getting out of this zone
        #if ( lastOffTimes.containsKey(theOtherLight.name) ) {
        #  val long timestamp = lastOffTimes.get(theOtherLight.name)
        #  if (now.getMillis() - timestamp <= DELAY_AFTER_LAST_OFF_TIME_IN_MS) {
        #    return
      # else - pass through

    events.sendCommand(switchItem.name, "ON")


@rule("Turn off wall switch when timer expires")
@when("Member of gWallSwitchTimer changed to OFF")
def turnOffWallSwitch(timerEvent):
    triggeringItem = itemRegistry.getItem(timerEvent.itemName)
    localIdx = triggeringItem.name.rfind("_")
    switchName = triggeringItem.name[:localIdx]

    # Check if motion sensor state is still on; if yes, renew timer. This
    # take care of the situation where there is constant activity and thus
    # the motion sensor was never shut off --> timer wasn't being renewed.
    motionSensorName = switchName + "_MotionSensor"
    motionSensorItems = filter(lambda item: item.name == motionSensorName, 
            ir.getItem(GROUP_WALL_SWITCH_MOTION_SENSORS).members)

    if len(motionSensorItems) > 0 and motionSensorItems[0].state == ON:
        events.sendCommand(triggeringItem.name, "ON")
    else:
        target = filter(lambda item: item.name == switchName, 
                ir.getItem(GROUP_WALL_SWITCH).members)[0]
        if isSwitchOn(target):
            events.sendCommand(target.name, "OFF")

# Returns true if a switch is on.
# @param switchItem can be a regular OnOffItem or a DimmerItem. In the later
#     case, the dimmer switch is considered on if its value is greater than 0.
def isSwitchOn(switchItem):
    return (switchItem.state == ON) \
        or (isinstance(switchItem, DimmerItem)
            and UnDefType.NULL != switchItem.state
            and UnDefType.UNDEF != switchItem.state 
            and switchItem.state > DecimalType(0))


@rule("Hello World timer rule")
@when("Time cron 0/5 * * * * ?")
def hellowWorldDecorator(event):
    item = itemRegistry.getItem("SF_Lobby_LightSwitch")

    #turnOffWallSwitch("FF_Foyer_LightSwitch_Timer")
    #meta = MetadataRegistry.get(MetadataKey("light", "SF_Lobby_LightSwitch")) 
    #config = meta.configuration
    #log.info("meta: " + str(config["level"]))


