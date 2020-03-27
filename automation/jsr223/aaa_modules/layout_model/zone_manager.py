from aaa_modules.layout_model.immutable_zone_manager import ImmutableZoneManager
from aaa_modules.layout_model.zone import Zone
from aaa_modules.layout_model.device import Device

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
    def getDevicesByType(cls):
        '''
        Returns a list of devices in all zones matching the given type.

        :param Device cls: the device type
        :rtype: list(Device)
        '''
        if None == cls:
            raise ValueError('cls must not be None')

        devices = []
        for zone in ZoneManager.zones.values():
            devices = devices + zone.getDevicesByType(cls)

        return devices

    @staticmethod
    def onMotionSensorTurnedOn(events, item):
        """
        Dispatches the motion sensor turned on event to each zone.

        :return: True if at least one zone processed the event; False otherwise
        :rtype: bool
        """
        ZoneManager._updateDeviceLastActivatedTime(item.getName())

        returnValues = [
            z.onMotionSensorTurnedOn(
                    events, item, ZoneManager._createImmutableInstance()) 
            for z in ZoneManager.zones.values()]
        return any(returnValues)

    @staticmethod
    def onTimerExpired(events, item):
        """
        Dispatches the timer expiry event to each zone.

        :param scope.events events: the global events object
        :param Item item:
        :return: True if at least one zone processed the event; False otherwise
        :rtype: bool
        """
        returnValues = [
            z.onTimerExpired(events, item) for z in ZoneManager.zones.values()]
        return any(returnValues)

    @staticmethod
    def onSwitchTurnedOn(events, item):
        """
        Dispatches the switch turned on event to each zone.

        :return: True if at least one zone processed the event; False otherwise
        :rtype: bool
        """
        ZoneManager._updateDeviceLastActivatedTime(item.getName())

        returnValues = [
            z.onSwitchTurnedOn(events, item, ZoneManager._createImmutableInstance())
            for z in ZoneManager.zones.values()]
        return any(returnValues)

    @staticmethod
    def onSwitchTurnedOff(events, item):
        """
        Dispatches the switch turned off event to each zone.

        :return: True if at least one zone processed the event; False otherwise
        :rtype: bool
        """
        returnValues = [
            z.onSwitchTurnedOff(events, item, ZoneManager._createImmutableInstance())
            for z in ZoneManager.zones.values()]
        return any(returnValues)

    @staticmethod
    def onContactOpen(events, item):
        """
        Dispatches the contact (door/windows) open event to each zone.

        :return: True if at least one zone processed the event; False otherwise
        :rtype: bool
        """
        ZoneManager._updateDeviceLastActivatedTime(item.getName())

        returnValues = [
            z.onContactOpen(events, item, ZoneManager._createImmutableInstance())
            for z in ZoneManager.zones.values()]
        return any(returnValues)

    @staticmethod
    def onContactClosed(events, item):
        """
        Dispatches the contact closed event to each zone.

        :return: True if at least one zone processed the event; False otherwise
        :rtype: bool
        """
        returnValues = [
            z.onContactClosed(events, item, ZoneManager._createImmutableInstance())
            for z in ZoneManager.zones.values()]
        return any(returnValues)

    @staticmethod
    def onNetworkDeviceConnected(events, item):
        """
        Dispatches the network device connected (to local network) to each zone.

        :return: True if at least one zone processed the event; False otherwise
        :rtype: bool
        """
        ZoneManager._updateDeviceLastActivatedTime(item.getName())

        return True

    @staticmethod
    def onAlarmPartitionArmedAway(events, item):
        """
        Dispatches the armed-away event to each zone.

        :return: True if at least one zone processed the event; False otherwise
        :rtype: bool
        """
        returnValues = [
            z.onAlarmPartitionArmedAway(
                    events, item, ZoneManager._createImmutableInstance())
            for z in ZoneManager.zones.values()]
        return any(returnValues)

    @staticmethod
    def onAlarmPartitionDisarmedFromAway(events, item):
        """
        Dispatches the disarmed-from-armed-away event to each zone.

        :return: True if at least one zone processed the event; False otherwise
        :rtype: bool
        """
        returnValues = [
            z.onAlarmPartitionDisarmedFromAway(
                    events, item, ZoneManager._createImmutableInstance())
            for z in ZoneManager.zones.values()]
        return any(returnValues)

    @staticmethod
    def _updateDeviceLastActivatedTime(itemName):
        """
        Determine if the itemName is associated with a managed device. If yes,
        update it last activated time to the current epoch second.
        """
        for zone in ZoneManager.zones.values():
            devices = [d for d in zone.getDevices() if d.getItemName() == itemName]
            for d in devices:
                d._updateLastActivatedTimestamp()

    @staticmethod
    def _createImmutableInstance():
        return ImmutableZoneManager(ZoneManager.getZones,
                ZoneManager.getZoneById,
                ZoneManager.getDevicesByType)
