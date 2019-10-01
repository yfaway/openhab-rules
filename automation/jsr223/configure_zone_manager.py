from core import osgi
from core.rules import rule
from core.triggers import when

from aaa_modules import switch_manager
from aaa_modules.platform_encapsulator import PlatformEncapsulator as PE

from aaa_modules import security_manager
reload(security_manager)
from aaa_modules.security_manager import SecurityManager as SM

from aaa_modules.zone_parser import ZoneParser
from aaa_modules.layout_model.zone import ZoneEvent
from aaa_modules.layout_model.zone_manager import ZoneManager
from aaa_modules.layout_model.switch import Switch
from aaa_modules.layout_model.actions.alert_on_entrance_activity import AlertOnEntraceActivity
from aaa_modules.layout_model.actions.turn_on_switch import TurnOnSwitch
from aaa_modules.layout_model.actions.turn_off_adjacent_zones import TurnOffAdjacentZones

def initializeZoneManager():
    zones = ZoneParser.parse(items, itemRegistry)

    ZoneManager.removeAllZones()

    turnOnSwitchAction = TurnOnSwitch()
    turnOffAdjacentZonesAction = TurnOffAdjacentZones()
    alertOnEntranceActivity = AlertOnEntraceActivity()

    for z in zones:
        if len(z.getDevicesByType(Switch)) > 0:
            z = z.addAction(ZoneEvent.MOTION, turnOnSwitchAction)
            z = z.addAction(ZoneEvent.SWITCH_TURNED_ON, turnOffAdjacentZonesAction)

        if z.isExternal():
            z = z.addAction(ZoneEvent.MOTION, alertOnEntranceActivity)

        ZoneManager.addZone(z)

    PE.logInfo("Configured ZoneManager with {} zones.".format(len(zones)))

@rule("Turn on light when motion sensor triggered")
@when("Member of gWallSwitchMotionSensor changed to ON")
def onMotionSensor(event):
    if not ZoneManager.onMotionSensorTurnedOn(events, event.itemName):
        PE.logInfo('Motion event for {} is not processed.'.format(
                    event.itemName))

@rule("Dispatch switch changed event")
@when("Member of gWallSwitch changed")
def onSwitchIsChanged(event):
    triggeringItem = itemRegistry.getItem(event.itemName)

    if switch_manager.isSwitchOn(triggeringItem):
        if not ZoneManager.onSwitchTurnedOn(events, event.itemName):
            PE.logInfo('Switch on event for {} is not processed.'.format(
                        event.itemName))
    else:
        if not ZoneManager.onSwitchTurnedOff(events, event.itemName):
            PE.logInfo('Switch off event for {} is not processed.'.format(
                        event.itemName))

@rule("Dispatch timer expired event")
@when("Member of gWallSwitchTimer changed to OFF")
def onTimerExpired(event):
    if not ZoneManager.onTimerExpired(events, event.itemName):
        PE.logInfo('Timer event for {} is not processed.'.format(
                    event.itemName))


initializeZoneManager()
