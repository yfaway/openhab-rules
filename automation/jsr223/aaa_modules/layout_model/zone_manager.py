from aaa_modules.layout_model import zone
reload(zone)
from aaa_modules.layout_model.zone import Zone

class ZoneManager:
    zones = []

    # Adds a zone.
    @staticmethod
    def addZone(zone):
        if None == zone:
            raise ValueError('zone must not be None')

        ZoneManager.zones.append(zone)

    # Removes a zone.
    @staticmethod
    def removeZone(zone):
        if None == zone:
            raise ValueError('zone must not be None')

        ZoneManager.zones.remove(zone)

    # Removes a zone.
    @staticmethod
    def removeAllZones():
       ZoneManager.zones = []

    # Returns a new list contains all zone.
    @staticmethod
    def getZones():
        return [z for z in ZoneManager.zones]

    @staticmethod
    def onMotionSensorTriggered(itemName):
        pass

    @staticmethod
    def onTimerExpired(itemName):
        pass

    @staticmethod
    def onSwitchTurnedOn(itemName):
        pass

    @staticmethod
    def onSwitchTurnedOff(itemName):
        pass
