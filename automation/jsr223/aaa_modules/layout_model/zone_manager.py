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

    # Dispatches the motion sensor turned on event to each zone.
    # @return True if at least one zone processed the event; False otherwise
    @staticmethod
    def onMotionSensorTurnedOn(events, itemName):
        returnValues = [
            z.onMotionSensorTurnedOn(events, itemName) for z in ZoneManager.zones]
        return any(returnValues)

    # Dispatches the timer expiry event to each zone.
    # @return True if at least one zone processed the event; False otherwise
    @staticmethod
    def onTimerExpired(events, itemName):
        returnValues = [
            z.onTimerExpired(events, itemName) for z in ZoneManager.zones]
        return any(returnValues)

    # Dispatches the switch turned on event to each zone.
    # @return True if at least one zone processed the event; False otherwise
    @staticmethod
    def onSwitchTurnedOn(events, itemName):
        returnValues = [
            z.onSwitchTurnedOn(events, itemName) for z in ZoneManager.zones]
        return any(returnValues)

    # Dispatches the switch turned off event to each zone.
    # @return True if at least one zone processed the event; False otherwise
    @staticmethod
    def onSwitchTurnedOff(events, itemName):
        returnValues = [
            z.onSwitchTurnedOff(events, itemName) for z in ZoneManager.zones]
        return any(returnValues)

