from aaa_modules.layout_model.zone import ZoneEvent
from aaa_modules.layout_model.neighbor import Neighbor, NeighborType
from aaa_modules.layout_model.devices.switch import Light
from aaa_modules.layout_model.action import action

@action(events = [ZoneEvent.SWITCH_TURNED_ON], devices = [Light], internal = True, external = True)
class TurnOffAdjacentZones:
    '''
    Turn off the lights in the zones adjacent to the current zone if the 
    current zone's liht is on and if the adjacent zones are of the OPEN_SPACE
    and OPEN_SPACE_SLAVE type.
    '''
    def __init__(self):
        pass

    def onAction(self, eventInfo):
        events = eventInfo.getEventDispatcher()
        zone = eventInfo.getZone()
        zoneManager = eventInfo.getZoneManager()

        if None == zoneManager:
            raise ValueError('zoneManager must be specified')

        adjacentZones = zone.getNeighborZones(zoneManager,
                [NeighborType.OPEN_SPACE, NeighborType.OPEN_SPACE_SLAVE])
        for z in adjacentZones:
            if z.isLightOn():
                z.turnOffLights(events)
        
        return True
