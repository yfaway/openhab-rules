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
                        for neighbor in zone.getNeighbors():
                            adjacentZone = getZoneByIdFn(neighbor.getZoneId())
                            if NeighborType.OPEN_SPACE_MASTER == neighbor.getType():
                                if adjacentZone.isLightOn():
                                    isProcessed = False

                    if isProcessed:
                        switch.turnOn(events)
            else:
                switch.turnOn(events)
                isProcessed = True
        
        return isProcessed
