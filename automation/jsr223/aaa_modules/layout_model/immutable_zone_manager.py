from aaa_modules.layout_model.zone import Zone
from aaa_modules.layout_model.zone_manager import ZoneManager
from aaa_modules.layout_model.device import Device

class ImmutableZoneManager:
    """
    Similar to ZoneManager, but this class contains read-only methods. 
    Instances of this class is passed to the method Action#onAction.
    """

    def __init__(self):
        pass

    def getZones(self):
        ''' 
        Returns a new list contains all zone.

        :rtype: list(Zone)
        ''' 
        return ZoneManager.getZones()

    def getZoneById(self, zoneId):
        """
        Returns the zone associated with the given zoneId.

        :param string zoneId: the value returned by Zone::getId()
        :return: the associated zone or None if the zoneId is not found
        :rtype: Zone
        """
        return ZoneManager.getZoneById(zoneId)

    def getDevicesByType(self, cls):
        '''
        Returns a list of devices in all zones matching the given type.

        :param Device cls: the device type
        :rtype: list(Device)
        '''
        return ZoneManager.getDevicesByType(cls)

