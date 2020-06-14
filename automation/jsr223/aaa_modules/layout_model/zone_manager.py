from aaa_modules.layout_model.immutable_zone_manager import ImmutableZoneManager
from aaa_modules.layout_model.zone import Zone
from aaa_modules.layout_model.device import Device

class ZoneManager:
    """
    Contains a set of Zone instances.
    """

    def __init__(self):
        self.zones = {} # map from string zoneId to Zone

    def addZone(self, zone):
        """
        Adds a zone.

        :param Zone zone: a Zone instance
        """
        if None == zone:
            raise ValueError('zone must not be None')

        self.zones[zone.getId()] = zone

    def removeZone(self, zone):
        ''' 
        Removes a zone.

        :param Zone zone: a Zone instance
        ''' 
        if None == zone:
            raise ValueError('zone must not be None')

        self.zones.pop(zone.getId())

    def removeAllZones(self):
        """ Removes all zone. """
        self.zones.clear()

    def getZones(self):
        ''' 
        Returns a new list contains all zone.

        :rtype: list(Zone)
        ''' 
        return [z for z in self.zones.values()]

    def getZoneById(self, zoneId):
        """
        Returns the zone associated with the given zoneId.

        :param string zoneId: the value returned by Zone::getId()
        :return: the associated zone or None if the zoneId is not found
        :rtype: Zone
        """
        return self.zones[zoneId] if zoneId in self.zones else None

    def getDevicesByType(self, cls):
        '''
        Returns a list of devices in all zones matching the given type.

        :param Device cls: the device type
        :rtype: list(Device)
        '''
        if None == cls:
            raise ValueError('cls must not be None')

        devices = []
        for zone in self.zones.values():
            devices = devices + zone.getDevicesByType(cls)

        return devices

    def onMotionSensorTurnedOn(self, events, item):
        """
        Dispatches the motion sensor turned on event to each zone.

        :return: True if at least one zone processed the event; False otherwise
        :rtype: bool
        """
        self._updateDeviceLastActivatedTime(item.getName())

        returnValues = [
            z.onMotionSensorTurnedOn(
                    events, item, self._createImmutableInstance()) 
            for z in self.zones.values()]
        return any(returnValues)

    def onTimerExpired(self, events, item):
        """
        Dispatches the timer expiry event to each zone.

        :param scope.events events: the global events object
        :param Item item:
        :return: True if at least one zone processed the event; False otherwise
        :rtype: bool
        """
        returnValues = [
            z.onTimerExpired(events, item) for z in self.zones.values()]
        return any(returnValues)

    def onSwitchTurnedOn(self, events, item):
        """
        Dispatches the switch turned on event to each zone.

        :return: True if at least one zone processed the event; False otherwise
        :rtype: bool
        """
        self._updateDeviceLastActivatedTime(item.getName())

        returnValues = [
            z.onSwitchTurnedOn(events, item, self._createImmutableInstance())
            for z in self.zones.values()]
        return any(returnValues)

    def onSwitchTurnedOff(self, events, item):
        """
        Dispatches the switch turned off event to each zone.

        :return: True if at least one zone processed the event; False otherwise
        :rtype: bool
        """
        returnValues = [
            z.onSwitchTurnedOff(events, item, self._createImmutableInstance())
            for z in self.zones.values()]
        return any(returnValues)

    def onContactOpen(self, events, item):
        """
        Dispatches the contact (door/windows) open event to each zone.

        :return: True if at least one zone processed the event; False otherwise
        :rtype: bool
        """
        self._updateDeviceLastActivatedTime(item.getName())

        returnValues = [
            z.onContactOpen(events, item, self._createImmutableInstance())
            for z in self.zones.values()]
        return any(returnValues)

    def onContactClosed(self, events, item):
        """
        Dispatches the contact closed event to each zone.

        :return: True if at least one zone processed the event; False otherwise
        :rtype: bool
        """
        returnValues = [
            z.onContactClosed(events, item, self._createImmutableInstance())
            for z in self.zones.values()]
        return any(returnValues)

    def onNetworkDeviceConnected(self, events, item):
        """
        Dispatches the network device connected (to local network) to each zone.

        :return: True if at least one zone processed the event; False otherwise
        :rtype: bool
        """
        self._updateDeviceLastActivatedTime(item.getName())

        return True

    def onAlarmPartitionArmedAway(self, events, item):
        """
        Dispatches the armed-away event to each zone.

        :return: True if at least one zone processed the event; False otherwise
        :rtype: bool
        """
        returnValues = [
            z.onAlarmPartitionArmedAway(
                    events, item, self._createImmutableInstance())
            for z in self.zones.values()]
        return any(returnValues)

    def onAlarmPartitionDisarmedFromAway(self, events, item):
        """
        Dispatches the disarmed-from-armed-away event to each zone.

        :return: True if at least one zone processed the event; False otherwise
        :rtype: bool
        """
        returnValues = [
            z.onAlarmPartitionDisarmedFromAway(
                    events, item, self._createImmutableInstance())
            for z in self.zones.values()]
        return any(returnValues)

    def onHumidityChanged(self, events, item):
        """
        Dispatches the humidity changed event to each zone.

        :return: True if at least one zone processed the event; False otherwise
        :rtype: bool
        """
        self._updateDeviceLastActivatedTime(item.getName())

        returnValues = [
            z.onHumidityChanged(events, item, self._createImmutableInstance())
            for z in self.zones.values()]
        return any(returnValues)

    def _updateDeviceLastActivatedTime(self, itemName):
        """
        Determine if the itemName is associated with a managed device. If yes,
        update it last activated time to the current epoch second.
        """
        for zone in self.zones.values():
            devices = [d for d in zone.getDevices() if d.getItemName() == itemName]
            for d in devices:
                d._updateLastActivatedTimestamp()

    def _createImmutableInstance(self):
        return ImmutableZoneManager(self.getZones,
                self.getZoneById,
                self.getDevicesByType)
