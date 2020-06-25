import time

from aaa_modules.platform_encapsulator import PlatformEncapsulator as PE
from aaa_modules.layout_model.action import action
from aaa_modules.layout_model.event_info import EventInfo
from aaa_modules.layout_model.zone import ZoneEvent
from aaa_modules.layout_model.neighbor import Neighbor, NeighborType
from aaa_modules.layout_model.devices.switch import Light, Switch
from aaa_modules.layout_model.devices.motion_sensor import MotionSensor

from aaa_modules.layout_model.actions.turn_off_adjacent_zones import TurnOffAdjacentZones

DEBUG = False

@action(events = [ZoneEvent.MOTION], internal = True, external = True)
class TurnOnSwitch:
    '''
    Turns on a switch (fan, dimmer or regular light), after being triggered by
    a motion event.
    If the switch is a dimmer or light, it is only turned on if:
    1. It is evening time, or
    2. The illuminance is below a threshold.

    A light/dimmer switch won't be turned on if:
    1. The light has the flag set to ignore motion event, or
    2. The adjacent zone is of type OPEN_SPACE_MASTER with the light on, or
    3. The light was jsut turned off, or
    4. The neighbor zone has a light switch that shares the same motion sensor,
    and that light switch was just recently turned off.

    No matter whether the switch is turned on or not (see the condition above),
    any adjacent zones of type OPEN_SPACE, and OPEN_SPACE_SLAVE that currently
    has the light on, will be sent a command to shut off the light.
    '''

    DELAY_AFTER_LAST_OFF_TIME_IN_SECONDS = 8
    '''
    The period of time in seconds (from the last timestamp a switch was
    turned off) to ignore the motion sensor event. This takes care of the
    scenario when the user manually turns off a light, but that physical
    spot is covered by a motion sensor, which immediately turns on the light
    again.
    '''
    def __init__(self):
        pass

    def onAction(self, eventInfo):
        events = eventInfo.getEventDispatcher()
        zone = eventInfo.getZone()
        zoneManager = eventInfo.getZoneManager()

        isProcessed = False
        canTurnOffAdjacentZones = True
        lightOnTime = zone.isLightOnTime()
        zoneIlluminance = zone.getIlluminanceLevel()

        for switch in zone.getDevicesByType(Switch):
            if switch.isOn():
                switch.turnOn(events) # renew the timer if a switch is already on
                isProcessed = True
                canTurnOffAdjacentZones = False
                continue

            if not switch.canBeTriggeredByMotionSensor():
                # A special case: if a switch is configured not to be
                # triggered by a motion sensor, it means there is already 
                # another switch sharing that motion sensor. In this case, we
                # don't want to turn off the other switch.
                canTurnOffAdjacentZones = False
                if DEBUG:
                    PE.logInfo("{}: rejected - can't be triggerred by motion sensor".format(
                            switch.getItemName()))

                continue

            # Break if switch was just turned off.
            if None != switch.getLastOffTimestampInSeconds():
                if (time.time() - switch.getLastOffTimestampInSeconds()) <= \
                    TurnOnSwitch.DELAY_AFTER_LAST_OFF_TIME_IN_SECONDS:
                    if DEBUG:
                        PE.logInfo("{}: rejected - switch was just turned off".format(
                            switch.getItemName()))
                    continue

            # Break if the switch of a neighbor sharing the motion sensor was
            # just turned off.
            openSpaceZones = [zoneManager.getZoneById(n.getZoneId()) \
                for n in zone.getNeighbors() if n.isOpenSpace()]
            sharedMotionSensorZones = [z for z in openSpaceZones 
                if zone.shareSensorWith(z, MotionSensor)]
            theirSwitches = reduce(lambda a, b : a + b,
                    [z.getDevicesByType(Switch) for z in sharedMotionSensorZones],
                    [])
            if any(time.time() - s.getLastOffTimestampInSeconds() <= \
                        TurnOnSwitch.DELAY_AFTER_LAST_OFF_TIME_IN_SECONDS \
                    for s in theirSwitches):
                if DEBUG:
                    PE.logInfo("{}: rejected - can't be triggerred by motion sensor".format(
                            switch.getItemName()))
                continue

            if isinstance(switch, Light):
                if lightOnTime or switch.isLowIlluminance(zoneIlluminance):
                    isProcessed = True
                    
                if isProcessed and None != zoneManager:
                    masterZones = [zoneManager.getZoneById(n.getZoneId()) \
                        for n in zone.getNeighbors() \
                        if NeighborType.OPEN_SPACE_MASTER == n.getType()]
                    if any(z.isLightOn() for z in masterZones):
                        isProcessed = False

                        # This scenario indicates that there is already 
                        # activity in the master zone, and thus such activity
                        # must not prematurely turns off the light in the
                        # adjacent zone.
                        canTurnOffAdjacentZones = False

                        if DEBUG:
                            PE.logInfo("{}: rejected - a master zone's light is on".format(
                                    switch.getItemName()))

                if isProcessed:
                    switch.turnOn(events)
            else:
                switch.turnOn(events)
                isProcessed = True

        # Now shut off the light in any shared space zones
        if canTurnOffAdjacentZones:
            if DEBUG:
                PE.logInfo("{}: turning off adjancent zone's light".format(
                        switch.getItemName()))
            offEventInfo = EventInfo(ZoneEvent.SWITCH_TURNED_ON,
                    eventInfo.getItem(), eventInfo.getZone(),
                    eventInfo.getZoneManager(), eventInfo.getEventDispatcher())
            TurnOffAdjacentZones().onAction(offEventInfo)
        
        return isProcessed
