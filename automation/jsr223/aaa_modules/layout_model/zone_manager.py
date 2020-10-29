from threading import Timer

from aaa_modules.platform_encapsulator import PlatformEncapsulator as PE
from aaa_modules.layout_model.immutable_zone_manager import ImmutableZoneManager
from aaa_modules.layout_model.zone import Zone
from aaa_modules.layout_model.device import Device

class ZoneManager:
    """
    Contains a set of Zone instances.
    """

    def __init__(self):
        self.zones = {} # map from string zoneId to Zone
        self.autoReportWatchDogTimer = None

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
        list = [z for z in self.zones.values()]
        list.sort(key = lambda z: z.getDisplayOrder())

        return list

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

    def startAutoReporWatchDog(self, timerIntervalInSeconds = 10 * 60,
            inactiveIntervalInSeconds = 10 * 60):
        '''
        Starts a timer that run every timerIntervalInSeconds. When the timer is
        triggered, it will scan auto-report devices (Devices::isAutoReport),
        and if any of them hasn't been triggered in the last
        inactiveIntervalInSeconds, it will reset the item value.

        This method is safe to call multiple times (a new timer will be started
        and any old timer is cancelled).

        :param int timerIntervalInSeconds: the timer duration
        :param int inactiveIntervalInSeconds: the inactive duration after which
            the device's value will be reset.
        :rtype: None
        '''

        def resetFailedAutoReportDevices():
            devices = []
            for z in self.getZones():
                [devices.append(d) for d in z.getDevices() \
                     if d.isAutoReport() and \
                        not d.wasRecentlyActivated(inactiveIntervalInSeconds)]

            if len(devices) > 0:
                itemNames = []
                for d in devices:
                    itemNames.append(d.getItemName())
                    d.resetValueStates()

                PE.logWarning(
                        "AutoReport Watchdog: {} failed auto-report devices: {}".format(
                            len(devices), itemNames))
            else:
                PE.logDebug("AutoReport Watchdog: no failed auto-report devices")

            # restart the timer
            self.autoReportWatchDogTimer = Timer(
                    timerIntervalInSeconds, resetFailedAutoReportDevices)
            self.autoReportWatchDogTimer.start()

        if None != self.autoReportWatchDogTimer \
                   and self.autoReportWatchDogTimer.isAlive():
            self.autoReportWatchDogTimer.cancel()
            self.autoReportWatchDogTimer = None

        self.autoReportWatchDogTimer = Timer(
                timerIntervalInSeconds, resetFailedAutoReportDevices)
        self.autoReportWatchDogTimer.start()
        PE.logInfo("Started auto-report watchdog timer.")

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
        self._updateDeviceLastActivatedTime(item)

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

    def onNetworkDeviceConnected(self, events, item):
        """
        Dispatches the network device connected (to local network) to each zone.

        :return: True if at least one zone processed the event; False otherwise
        :rtype: bool
        """
        self._updateDeviceLastActivatedTime(item)

        return True

    def dispatchEvent(self, zoneEvent, openHabEvents, item, enforceItemInZone = True):
        """
        Dispatches the event to the zones.

        :param ZoneEvent zoneEvent:
        :param scope.events openHabEvents:
        :param bool enforceItemInZone: if set to true, the actions won't be
            triggered if the zone doesn't contain the item.
        """
        self._updateDeviceLastActivatedTime(item)

        zm = self._createImmutableInstance()
        returnValues = [
            z.dispatchEvent(zoneEvent, openHabEvents, item, zm, enforceItemInZone)
            for z in self.zones.values()]
        return any(returnValues)

    def _updateDeviceLastActivatedTime(self, item):
        """
        Determine if the itemName is associated with a managed device. If yes,
        update it last activated time to the current epoch second.
        """
        for zone in self.zones.values():
            devices = [d for d in zone.getDevices() if d.containsItem(item)]
            for d in devices:
                d._updateLastActivatedTimestamp()

    def _createImmutableInstance(self):
        return ImmutableZoneManager(self.getZones,
                self.getZoneById,
                self.getDevicesByType)
