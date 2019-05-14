from aaa_modules.layout_model.neighbor import Neighbor, NeighborType
from aaa_modules.layout_model.switch import Light, Switch
from aaa_modules.layout_model.actions.action import Action

from org.slf4j import Logger, LoggerFactory
logger = LoggerFactory.getLogger("org.eclipse.smarthome.model.script.Rules")

# Turns on a switch (fan, dimmer or regular light).
# If the switch is a dimmer or light, only turns it is evening time or if the
# illuminance is below a threshold.
class TurnOnSwitch(Action):
    def onAction(self, events, zone, getZoneByIdFn):
        isProcessed = False
        lightOnTime = zone.isLightOnTime()
        zoneIlluminance = zone.getIlluminanceLevel()

        for switch in zone.getDevicesByType(Switch):
            if isinstance(switch, Light):
                if (lightOnTime or
                        None == switch.getIlluminanceThreshold() or 
                        zoneIlluminance < switch.getIlluminanceThreshold()):

                    isProcessed = True
                    if None != getZoneByIdFn:
                        masterZones = [getZoneByIdFn(n.getZoneId()) \
                            for n in zone.getNeighbors() \
                            if NeighborType.OPEN_SPACE_MASTER == n.getType()]
                        if any(z.isLightOn() for z in masterZones):
                            isProcessed = False

                    if isProcessed:
                        switch.turnOn(events)

                # now shut off any the light in any shared space zones
                if None != getZoneByIdFn:
                    adjacentZones = [getZoneByIdFn(n.getZoneId()) \
                        for n in zone.getNeighbors() \
                        if (NeighborType.OPEN_SPACE == n.getType() or \
                                NeighborType.OPEN_SPACE_SLAVE == n.getType()) ]

                    for z in adjacentZones:
                        if z.isLightOn():
                            z.turnOffLights(events)
            else:
                switch.turnOn(events)
                isProcessed = True
        
        return isProcessed
