import time

from aaa_modules.layout_model.neighbor import Neighbor, NeighborType
from aaa_modules.layout_model.switch import Light, Switch
from aaa_modules.layout_model.motion_sensor import MotionSensor
from aaa_modules.layout_model.actions.action import Action
from aaa_modules.layout_model.actions.turn_off_adjacent_zones import TurnOffAdjacentZones

from org.slf4j import Logger, LoggerFactory
logger = LoggerFactory.getLogger("org.eclipse.smarthome.model.script.Rules")

DEBUG = False

class TurnOnSwitch(Action):
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

    def onAction(self, events, zone, getZoneByIdFn):
        isProcessed = False
        canTurnOffAdjacentZones = True
        lightOnTime = zone.isLightOnTime()
        zoneIlluminance = zone.getIlluminanceLevel()

        for switch in zone.getDevicesByType(Switch):
            if not switch.canBeTriggeredByMotionSensor():
                # A special case: if a switch is configured not to be
                # triggered by a motion sensor, it means there is already 
                # another switch sharing that motion sensor. In this case, we
                # don't want to turn off the other switch.
                canTurnOffAdjacentZones = False
                if DEBUG:
                    logger.info("{}: rejected - can't be triggerred by motion sensor".format(
                            switch.getItemName()))

                continue

            # Break if switch was just turned off.
            if None != switch.getLastOffTimestampInSeconds():
                if (time.time() - switch.getLastOffTimestampInSeconds()) <= \
                    TurnOnSwitch.DELAY_AFTER_LAST_OFF_TIME_IN_SECONDS:
                    if DEBUG:
                        logger.info("{}: rejected - switch was just turned off".format(
                            switch.getItemName()))
                    continue

            # Break if the switch of a neighbor sharing the motion sensor was
            # just turned off.
            openSpaceZones = [getZoneByIdFn(n.getZoneId()) \
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
                    logger.info("{}: rejected - can't be triggerred by motion sensor".format(
                            switch.getItemName()))
                continue

            if isinstance(switch, Light):
                if lightOnTime or switch.isLowIlluminance(zoneIlluminance):
                    isProcessed = True
                    
                if isProcessed and None != getZoneByIdFn:
                    masterZones = [getZoneByIdFn(n.getZoneId()) \
                        for n in zone.getNeighbors() \
                        if NeighborType.OPEN_SPACE_MASTER == n.getType()]
                    if any(z.isLightOn() for z in masterZones):
                        isProcessed = False
                        if DEBUG:
                            logger.info("{}: rejected - a master zone's light is on".format(
                                    switch.getItemName()))

                if isProcessed:
                    switch.turnOn(events)
            else:
                switch.turnOn(events)
                isProcessed = True

        # Now shut off the light in any shared space zones
        if canTurnOffAdjacentZones:
            if DEBUG:
                logger.info("{}: turning off adjancent zone's light".format(
                        switch.getItemName()))
            TurnOffAdjacentZones().onAction(events, zone, getZoneByIdFn)
        
        return isProcessed
