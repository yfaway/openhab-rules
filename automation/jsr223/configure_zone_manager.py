from core import osgi
from core.rules import rule
from core.triggers import when

from aaa_modules import switch_manager
from aaa_modules.platform_encapsulator import PlatformEncapsulator as PE
from aaa_modules.security_manager import SecurityManager as SM
from aaa_modules.zone_parser import ZoneParser
from aaa_modules.layout_model.zone import ZoneEvent
from aaa_modules.layout_model.zone_manager import ZoneManager

from aaa_modules.layout_model.devices.switch import Fan, Switch
from aaa_modules.layout_model.devices.activity_times import ActivityTimes
from aaa_modules.layout_model.devices.chromecast_audio_sink import ChromeCastAudioSink

from aaa_modules.layout_model.actions.alert_on_entrance_activity import AlertOnEntraceActivity
from aaa_modules.layout_model.actions.alert_on_door_left_open import AlertOnExternalDoorLeftOpen
from aaa_modules.layout_model.actions.arm_after_front_door_closed import ArmAfterFrontDoorClosed
from aaa_modules.layout_model.actions.play_music_during_shower import PlayMusicDuringShower
from aaa_modules.layout_model.actions.simulate_daytime_presence import SimulateDaytimePresence
from aaa_modules.layout_model.actions.turn_on_switch import TurnOnSwitch
from aaa_modules.layout_model.actions.turn_off_adjacent_zones import TurnOffAdjacentZones

def initializeZoneManager():
    zones = ZoneParser.parse(items, itemRegistry)

    ZoneManager.removeAllZones()

    # actions
    externalZoneActions = [
        AlertOnEntraceActivity(),
        SimulateDaytimePresence("http://hestia2.cdnstream.com:80/1277_192"),
        AlertOnExternalDoorLeftOpen(),
        ArmAfterFrontDoorClosed(15 * 60), # arm after 15'
    ]

    fanActions = [PlayMusicDuringShower("http://hestia2.cdnstream.com:80/1277_192")]

    switchActions = [TurnOnSwitch(), TurnOffAdjacentZones()]

    # add virtual devices and actions
    for z in zones:
        if z.getName() == 'Virtual':
            timeMap = {
                'wakeup': '6 - 9',
                'lunch': '12:00 - 13:30',
                'quiet' : '14:00 - 16:00, 20:00 - 22:59',
                'dinner': '17:50 - 20:00',
                'sleep': '23:00 - 7:00' 
            }
            z = z.addDevice(ActivityTimes(timeMap))

        if len(z.getDevicesByType(Switch)) > 0:
            for a in switchActions:
                z = z.addAction(a)

        if z.isExternal():
            for a in externalZoneActions:
                z = z.addAction(a)

        # add the play music action if zone has a fan switch.
        fans = z.getDevicesByType(Fan)
        if len(fans) > 0:
            for a in fanActions:
                z = z.addAction(a)

        ZoneManager.addZone(z)

    PE.logInfo("Configured ZoneManager with {} zones.".format(len(zones)))

    zones = ZoneManager.getZones()
    output = "{} zones".format(len(zones))
    for z in zones:
        output += '\n' + str(z)
    PE.logInfo(output)

def addContextVariables():
    '''
    Make the variable zm available to all scripts.
    '''
    if "zm" not in locals():
        import core
        core.JythonExtensionProvider.addValue("zm",
                ZoneManager._createImmutableInstance())
        core.JythonExtensionProvider.addPreset("layout_preset", ["zm"], True)

@rule("Turn on light when motion sensor triggered")
@when("Member of gWallSwitchMotionSensor changed to ON")
def onMotionSensor(event):
    # Ensure that if this is a Group event (Group:Switch), the timestamp for
    # the triggering item is also updated.
    if "getMemberName" in dir(event):
        ZoneManager._updateDeviceLastActivatedTime(event.getMemberName())

    if not ZoneManager.onMotionSensorTurnedOn(
            events, itemRegistry.getItem(event.itemName)):
        PE.logDebug('Motion event for {} is not processed.'.format(
                    event.itemName))

@rule("Dispatch switch changed event")
@when("Member of gWallSwitch changed")
def onSwitchIsChanged(event):
    triggeringItem = itemRegistry.getItem(event.itemName)

    if switch_manager.isSwitchOn(triggeringItem):
        if not ZoneManager.onSwitchTurnedOn(events, triggeringItem):
            PE.logDebug('Switch on event for {} is not processed.'.format(
                        event.itemName))
    else:
        if not ZoneManager.onSwitchTurnedOff(events, triggeringItem):
            PE.logDebug('Switch off event for {} is not processed.'.format(
                        event.itemName))

@rule("Dispatch contact changed event")
@when("Member of gZoneTripped changed")
@when("Item FF_Garage_Door changed")
def onDoorOrWindowsChanged(event):
    triggeringItem = itemRegistry.getItem(event.itemName)

    if PE.isInStateOn(triggeringItem.getState()) \
        or PE.isInStateOpen(triggeringItem.getState()):
        if not ZoneManager.onContactOpen(events, triggeringItem):
            PE.logDebug('Contact open event for {} is not processed.'.format(
                        event.itemName))
    else:
        if not ZoneManager.onContactClosed(events, triggeringItem):
            PE.logDebug('Contact closed event for {} is not processed.'.format(
                        event.itemName))

@rule("Dispatch timer expired event")
@when("Member of gWallSwitchTimer changed to OFF")
def onTimerExpired(event):
    if not ZoneManager.onTimerExpired(events, itemRegistry.getItem(event.itemName)):
        PE.logDebug('Timer event for {} is not processed.'.format(
                    event.itemName))

@rule("Dispatch network device connected event")
@when("Member of gNetworkPresence changed to ON")
def onNetworkDeviceConnected(event):
    if not ZoneManager.onNetworkDeviceConnected(events, itemRegistry.getItem(event.itemName)):
        PE.logDebug('Network device connected event for {} is not processed.'.format(
                    event.itemName))


initializeZoneManager()
addContextVariables()
