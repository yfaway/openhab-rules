import time

from aaa_modules.layout_model.neighbor import Neighbor, NeighborType
from aaa_modules.layout_model.switch import Light, Switch
from aaa_modules.layout_model.motion_sensor import MotionSensor
from aaa_modules.layout_model.actions.action import Action
from aaa_modules.layout_model.actions.turn_off_adjacent_zones import TurnOffAdjacentZones

from org.slf4j import Logger, LoggerFactory
logger = LoggerFactory.getLogger("org.eclipse.smarthome.model.script.Rules")

# Turns on a switch (fan, dimmer or regular light).
# If the switch is a dimmer or light, only turns it on if it is evening time or
# if the illuminance is below a threshold.
# If the switch is a light and the adjacent zone is of type OPEN_SPACE_MASTER
# with the light currently on, it won't be turned on.
#
# No matter whether the switch is turned on or not (see the condition above),
# any adjacent zones of type OPEN_SPACE, and OPEN_SPACE_SLAVE that currently
# has the light on, will be sent a command to shut off the light.
class TurnOnSwitch(Action):
    # The period of time in seconds (from the last timestamp a switch was
    # turned off) to ignore the motion sensor event. This takes care of the
    # scenario when the user manually turns off a light, but that physical
    # spot is covered by a motion sensor, which immediately turns on the light
    # again.
    DELAY_AFTER_LAST_OFF_TIME_IN_SECONDS = 8

    def onAction(self, events, zone, getZoneByIdFn):
        isProcessed = False
        canTurnOffOtherZones = False
        lightOnTime = zone.isLightOnTime()
        zoneIlluminance = zone.getIlluminanceLevel()

        for switch in zone.getDevicesByType(Switch):
            if not switch.canBeTriggeredByMotionSensor():
                continue

            # Break if switch was just turned off.
            if None != switch.getLastOffTimestampInSeconds():
                if (time.time() - switch.getLastOffTimestampInSeconds()) <= \
                    TurnOnSwitch.DELAY_AFTER_LAST_OFF_TIME_IN_SECONDS:
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
                continue

            canTurnOffOtherZones = True

            if isinstance(switch, Light):
                if (lightOnTime or
                        None == switch.getIlluminanceThreshold() or 
                        zoneIlluminance < switch.getIlluminanceThreshold()):
                    isProcessed = True
                    
                if isProcessed and None != getZoneByIdFn:
                    masterZones = [getZoneByIdFn(n.getZoneId()) \
                        for n in zone.getNeighbors() \
                        if NeighborType.OPEN_SPACE_MASTER == n.getType()]
                    if any(z.isLightOn() for z in masterZones):
                        isProcessed = False

                if isProcessed:
                    switch.turnOn(events)
            else:
                switch.turnOn(events)
                isProcessed = True

        # Now shut off the light in any shared space zones
        if canTurnOffOtherZones:
            TurnOffAdjacentZones().onAction(events, zone, getZoneByIdFn)
        
        return isProcessed
