from aaa_modules.layout_model.zone import Zone

class ZoneManager:
    """
    Contains a set of Zone instances.
    """

    zones = {} # map from string zoneId to Zone

    @staticmethod
    def addZone(zone):
        """
        Adds a zone.

        :param Zone zone: a Zone instance
        """
        if None == zone:
            raise ValueError('zone must not be None')

        ZoneManager.zones[zone.getId()] = zone

    @staticmethod
    def removeZone(zone):
        ''' 
        Removes a zone.

        :param Zone zone: a Zone instance
        ''' 
        if None == zone:
            raise ValueError('zone must not be None')

        ZoneManager.zones.pop(zone.getId())

    @staticmethod
    def removeAllZones():
        """ Removes all zone. """
        ZoneManager.zones.clear()

    @staticmethod
    def getZones():
        ''' 
        Returns a new list contains all zone.

        :rtype: list(Zone)
        ''' 
        return [z for z in ZoneManager.zones.values()]

    @staticmethod
    def getZoneById(zoneId):
        """
        Returns the zone associated with the given zoneId.

        :param string zoneId: the value returned by Zone::getId()
        :return: the associated zone or None if the zoneId is not found
        :rtype: Zone
        """
        return ZoneManager.zones[zoneId] if zoneId in ZoneManager.zones else None

    @staticmethod
    def onMotionSensorTurnedOn(events, itemName):
        """
        Dispatches the motion sensor turned on event to each zone.

        :return: True if at least one zone processed the event; False otherwise
        :rtype: bool
        """
        returnValues = [
            z.onMotionSensorTurnedOn(
                    events, itemName, ZoneManager.getZoneById) 
            for z in ZoneManager.zones.values()]
        return any(returnValues)

    @staticmethod
    def onTimerExpired(events, itemName):
        """
        Dispatches the timer expiry event to each zone.

        :param scope.events events: the global events object
        :param str itemName:
        :return: True if at least one zone processed the event; False otherwise
        :rtype: bool
        """
        returnValues = [
            z.onTimerExpired(events, itemName) for z in ZoneManager.zones.values()]
        return any(returnValues)

    @staticmethod
    def onSwitchTurnedOn(events, itemName):
        """
        Dispatches the switch turned on event to each zone.

        :return: True if at least one zone processed the event; False otherwise
        :rtype: bool
        """
        returnValues = [
            z.onSwitchTurnedOn(events, itemName, ZoneManager.getZoneById)
            for z in ZoneManager.zones.values()]
        return any(returnValues)

    @staticmethod
    def onSwitchTurnedOff(events, itemName):
        """
        Dispatches the switch turned off event to each zone.

        :return: True if at least one zone processed the event; False otherwise
        :rtype: bool
        """
        returnValues = [
            z.onSwitchTurnedOff(events, itemName) for z in ZoneManager.zones.values()]
        return any(returnValues)

