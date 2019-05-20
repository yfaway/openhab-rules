from org.slf4j import Logger, LoggerFactory
from core import osgi
from core.rules import rule
from core.triggers import when

from aaa_modules import switch_manager

# temporary reloads during development
from aaa_modules.layout_model import zone
reload(zone)
from aaa_modules.layout_model import zone_manager
reload(zone_manager)
from aaa_modules import zone_parser
reload(zone_parser)
from aaa_modules.layout_model.actions import turn_on_switch
reload(turn_on_switch)

from aaa_modules.zone_parser import ZoneParser
from aaa_modules.layout_model.zone_manager import ZoneManager

logger = LoggerFactory.getLogger("org.eclipse.smarthome.model.script.Rules")

def initializeZoneManager():
    zones = ZoneParser.parse(items, itemRegistry)

    ZoneManager.removeAllZones()
    for z in zones:
        ZoneManager.addZone(z)

    logger.info("Configured ZoneManager with {} zones.".format(len(zones)))

#@rule("Turn on light when motion sensor triggered")
#@when("Member of gWallSwitchMotionSensor changed to ON")
def onMotionSensor(event):
    if not ZoneManager.onMotionSensorTurnedOn(events, event.itemName):
        logger.info('Motion event for {} is not processed.'.format(
                    event.itemName))

#@rule("Dispatch switch changed event")
#@when("Member of gWallSwitch changed")
def onSwitchIsChanged(event):
    triggeringItem = itemRegistry.getItem(event.itemName)

    if switch_manager.isSwitchOn(triggeringItem):
        if not ZoneManager.onSwitchTurnedOn(events, event.itemName):
            logger.info('Switch on event for {} is not processed.'.format(
                        event.itemName))
    else:
        if not ZoneManager.onSwitchTurnedOff(events, event.itemName):
            logger.info('Switch off event for {} is not processed.'.format(
                        event.itemName))

#@rule("Dispatch timer expired event")
#@when("Member of gWallSwitchTimer changed to OFF")
def onTimerExpired(event):
    if not ZoneManager.onTimerExpired(events, event.itemName):
        logger.info('Timer event for {} is not processed.'.format(
                    event.itemName))

initializeZoneManager()

