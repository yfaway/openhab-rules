from aaa_modules.layout_model.zone import Zone
from aaa_modules.layout_model.device import Device

class ImmutableZoneManager:
    """
    Similar to ZoneManager, but this class contains read-only methods. 
    Instances of this class is passed to the method Action#onAction.
    """

    def __init__(self, getZonesLambda, getZoneByIdLambda,
            getDevicesByTypeLambda):
        self.getZonesLambda = getZonesLambda
        self.getZoneByIdLambda = getZoneByIdLambda
        self.getDevicesByTypeLambda = getDevicesByTypeLambda

    def getContainingZone(self, device):
        '''
        Returns the first zone containing the device or None if the device
        does not belong to a zone.

        :param Device device: the device
        :rtype: Zone or None
        '''
        if None == device:
            raise ValueError('device must not be None')

        for zone in self.getZones():
            if zone.hasDevice(device):
                return zone

        return None

    def getZones(self):
        ''' 
        Returns a new list contains all zone.

        :rtype: list(Zone)
        ''' 
        return self.getZonesLambda()

    def getZoneById(self, zoneId):
        """
        Returns the zone associated with the given zoneId.

        :param string zoneId: the value returned by Zone::getId()
        :return: the associated zone or None if the zoneId is not found
        :rtype: Zone
        """
        return self.getZoneByIdLambda(zoneId)

    def getDevicesByType(self, cls):
        '''
        Returns a list of devices in all zones matching the given type.

        :param Device cls: the device type
        :rtype: list(Device)
        '''
        return self.getDevicesByTypeLambda(cls)

