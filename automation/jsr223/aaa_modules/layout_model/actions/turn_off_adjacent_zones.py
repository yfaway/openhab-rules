from aaa_modules.layout_model.neighbor import Neighbor, NeighborType
from aaa_modules.layout_model.actions.action import Action

class TurnOffAdjacentZones(Action):
    '''
    Turn off the lights in the zones adjacent to the current zone if those zones
    are of the OPEN_SPACE and OPEN_SPACE_SLAVE type.
    '''

    def onAction(self, events, zone, getZoneByIdFn):
        if None != getZoneByIdFn:
            adjacentZones = [getZoneByIdFn(n.getZoneId()) \
                for n in zone.getNeighbors() \
                if (NeighborType.OPEN_SPACE == n.getType() or \
                        NeighborType.OPEN_SPACE_SLAVE == n.getType()) ]

            for z in adjacentZones:
                if z.isLightOn():
                    z.turnOffLights(events)
        
        return True
