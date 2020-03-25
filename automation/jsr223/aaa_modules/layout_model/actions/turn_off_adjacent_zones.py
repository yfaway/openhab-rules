from aaa_modules.layout_model.zone import ZoneEvent
from aaa_modules.layout_model.neighbor import Neighbor, NeighborType
from aaa_modules.layout_model.devices.switch import Light
from aaa_modules.layout_model.action import Action

class TurnOffAdjacentZones(Action):
    '''
    Turn off the lights in the zones adjacent to the current zone if the 
    current zone's liht is on and if the adjacent zones are of the OPEN_SPACE
    and OPEN_SPACE_SLAVE type.
    '''

    def getTriggeringEvents(self):
        '''
        :return: list of triggering events this action process.
        :rtype: list(ZoneEvent)
        '''
        return [ZoneEvent.SWITCH_TURNED_ON]

    def onAction(self, eventInfo):
        events = eventInfo.getEventDispatcher()
        zone = eventInfo.getZone()
        zoneManager = eventInfo.getZoneManager()

        if None == zoneManager:
            raise ValueError('zoneManager must be specified')

        lights = zone.getDevicesByType(Light)
        if len(lights) == 0:
            return False

        adjacentZones = [zoneManager.getZoneById(n.getZoneId()) \
            for n in zone.getNeighbors() \
            if (NeighborType.OPEN_SPACE == n.getType() or \
                    NeighborType.OPEN_SPACE_SLAVE == n.getType()) ]

        for z in adjacentZones:
            if z.isLightOn():
                z.turnOffLights(events)
        
        return True
