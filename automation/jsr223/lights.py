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


#@rule("Hello World timer rule")
#@when("Time cron 0/5 * * * * ?")
#def hellowWorldDecorator(event):
#    item = itemRegistry.getItem("SF_Lobby_LightSwitch")

    #turnOffWallSwitch("FF_Foyer_LightSwitch_Timer")
    #meta = MetadataRegistry.get(MetadataKey("light", "SF_Lobby_LightSwitch")) 
    #config = meta.configuration
    #log.info("meta: " + str(config["level"]))


