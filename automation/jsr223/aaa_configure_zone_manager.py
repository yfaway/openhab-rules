from core import osgi
from core.rules import rule
from core.triggers import when

from aaa_modules import switch_manager
from aaa_modules import security_manager
from aaa_modules.platform_encapsulator import PlatformEncapsulator as PE
from aaa_modules.security_manager import SecurityManager as SM
from aaa_modules.zone_parser import ZoneParser
from aaa_modules.layout_model.zone import ZoneEvent
from aaa_modules.layout_model.zone_manager import ZoneManager

from aaa_modules.layout_model.devices.activity_times import ActivityTimes
from aaa_modules.layout_model.devices.alarm_partition import AlarmPartition
from aaa_modules.layout_model.devices.chromecast_audio_sink import ChromeCastAudioSink
from aaa_modules.layout_model.devices.humidity_sensor import HumiditySensor
from aaa_modules.layout_model.devices.switch import Fan, Switch

from aaa_modules.layout_model.actions.alert_on_entrance_activity import AlertOnEntraceActivity
from aaa_modules.layout_model.actions.alert_on_door_left_open import AlertOnExternalDoorLeftOpen
from aaa_modules.layout_model.actions.alert_on_humidity_out_of_range import AlertOnHumidityOutOfRange
from aaa_modules.layout_model.actions.arm_after_front_door_closed import ArmAfterFrontDoorClosed
from aaa_modules.layout_model.actions.play_music_during_shower import PlayMusicDuringShower
from aaa_modules.layout_model.actions.simulate_daytime_presence import SimulateDaytimePresence
from aaa_modules.layout_model.actions.turn_on_switch import TurnOnSwitch
from aaa_modules.layout_model.actions.turn_off_adjacent_zones import TurnOffAdjacentZones
from aaa_modules.layout_model.actions.turn_off_devices_on_alarm_mode_change import TurnOffDevicesOnAlarmModeChange

'''
Initialize an instance of ZoneManager, populate the zones, add the actions,
and put the following variables on the script context: 'zm'.
'''

_mutableZoneManager = None

def initializeZoneManager():
    '''
    Creates a new instance of ZoneManager and populate the zones.

    :rtype: ZoneManager
    '''
    zones = ZoneParser().parse(items, itemRegistry)

    zm = ZoneManager()

    # actions
    externalZoneActions = [
        AlertOnEntraceActivity(),
        SimulateDaytimePresence("http://hestia2.cdnstream.com:80/1277_192"),
        AlertOnExternalDoorLeftOpen(),
        ArmAfterFrontDoorClosed(12 * 60), # arm after 12'
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

        if len(z.getDevicesByType(AlarmPartition)) > 0:
            z = z.addAction(TurnOffDevicesOnAlarmModeChange())

        if len(z.getDevicesByType(HumiditySensor)) > 0 and not z.isExternal():
            z = z.addAction(AlertOnHumidityOutOfRange())

        # add the play music action if zone has a fan switch.
        fans = z.getDevicesByType(Fan)
        if len(fans) > 0:
            for a in fanActions:
                z = z.addAction(a)

        zm.addZone(z)

    PE.logInfo("Configured ZoneManager with {} zones.".format(len(zones)))

    zones = zm.getZones()
    output = "{} zones".format(len(zones))
    for z in zones:
        output += '\n' + str(z)
    PE.logInfo(output)

    return zm

def addContextVariables(zoneManager):
    '''
    Make the variable zm available to all scripts.
    '''
    if "zm" not in locals():
        import core
        core.JythonExtensionProvider.addValue("zm", 
                zoneManager._createImmutableInstance())

        core.JythonExtensionProvider.addPreset(
                "layout_preset", ["zm"], True)

@rule("Turn on light when motion sensor triggered")
@when("Member of gWallSwitchMotionSensor changed to ON")
def onMotionSensor(event):
    # Ensure that if this is a Group event (Group:Switch), the timestamp for
    # the triggering item is also updated.
    if "getMemberName" in dir(event):
        _mutableZoneManager._updateDeviceLastActivatedTime(event.getMemberName())

    dispatchEvent(ZoneEvent.MOTION, event)

@rule("Dispatch switch changed event")
@when("Member of gWallSwitch changed")
def onSwitchIsChanged(event):
    triggeringItem = itemRegistry.getItem(event.itemName)

    if switch_manager.isSwitchOn(triggeringItem):
        if not _mutableZoneManager.onSwitchTurnedOn(events, triggeringItem):
            PE.logDebug('Switch on event for {} is not processed.'.format(
                        event.itemName))
    else:
        if not _mutableZoneManager.onSwitchTurnedOff(events, triggeringItem):
            PE.logDebug('Switch off event for {} is not processed.'.format(
                        event.itemName))

@rule("Dispatch contact changed event")
@when("Member of gZoneTripped changed")
@when("Item FF_Garage_Door changed")
def onDoorOrWindowsChanged(event):
    triggeringItem = itemRegistry.getItem(event.itemName)

    if PE.isInStateOn(triggeringItem.getState()) \
        or PE.isInStateOpen(triggeringItem.getState()):

        dispatchEvent(ZoneEvent.CONTACT_OPEN, event)
    else:
        dispatchEvent(ZoneEvent.CONTACT_CLOSED, event)

@rule("Dispatch timer expired event")
@when("Member of gWallSwitchTimer changed to OFF")
def onTimerExpired(event):
    if not _mutableZoneManager.onTimerExpired(events, itemRegistry.getItem(event.itemName)):
        PE.logDebug('Timer event for {} is not processed.'.format(
                    event.itemName))

@rule("Dispatch network device connected event")
@when("Member of gNetworkPresence changed to ON")
def onNetworkDeviceConnected(event):
    if not _mutableZoneManager.onNetworkDeviceConnected(events, itemRegistry.getItem(event.itemName)):
        PE.logDebug('Network device connected event for {} is not processed.'.format(
                    event.itemName))

@rule("Dispatch arm-away event.")
@when(security_manager.WHEN_CHANGED_TO_ARMED_AWAY)
def onAlarmPartitionArmedAway(event):
    dispatchEvent(ZoneEvent.PARTITION_ARMED_AWAY, event, False)

@rule("Dispatch disarm event.")
@when(security_manager.WHEN_CHANGED_FROM_ARM_AWAY_TO_UNARMED)
def onAlarmPartitionDisarmedFromAway(event):
    dispatchEvent(ZoneEvent.PARTITION_DISARMED_FROM_AWAY, event, False)

@rule("Dispatch humidity changed event")
@when("Member of gHumidity changed")
def onHumidityChanged(event):
    dispatchEvent(ZoneEvent.HUMIDITY_CHANGED, event)

@rule("Dispatch temperature changed event")
@when("Member of gTemperature changed")
def onHumidityChanged(event):
    dispatchEvent(ZoneEvent.TEMPERATURE_CHANGED, event)

def dispatchEvent(zoneEvent, event, enforceItemInZone = True):
    '''
    Dispatches an event to the ZoneManager. If the event is not processed,
    create a debug log.
    '''
    triggeringItem = itemRegistry.getItem(event.itemName)

    if not _mutableZoneManager.dispatchEvent(zoneEvent, events, triggeringItem, enforceItemInZone):
        PE.logDebug('Event {} for item {} is not processed.'.format(zoneEvent,
                    event.itemName))

_mutableZoneManager = initializeZoneManager()
addContextVariables(_mutableZoneManager)
