from copy import copy
import time

from core import osgi
from org.eclipse.smarthome.core.items import Metadata
from org.eclipse.smarthome.core.items import MetadataKey

from aaa_modules.platform_encapsulator import PlatformEncapsulator as PE

MetadataRegistry = osgi.get_service("org.eclipse.smarthome.core.items.MetadataRegistry")

class Device(object):
    '''
    The base class that all other sensors and switches derive from.
    '''

    def __init__(self, openhabItem, batteryPowered = False, wifi = False,
            autoReport = False):
        '''
        Ctor

        :param org.eclipse.smarthome.core.items.Item openhabItem:
        :param bool batteryPowered: indicates if the device is powered by battery.
        :param bool wifi: indicates if the device communicates by WiFi.
        :param bool autoReport: indicates if the device periodically reports
                its value.
        :raise ValueError: if any parameter is invalid
        '''
        if None == openhabItem:
            raise ValueError('openhabItem must not be None')

        self.item = openhabItem
        self.batteryPowered = batteryPowered
        self.wifi = wifi
        self.autoReport = autoReport
        self.lastActivatedTimestamp = None

    def getItem(self):
        '''
        Returns the backed OpenHab item.

        :rtype: org.eclipse.smarthome.core.items.Item
        '''
        return self.item

    def getItemName(self):
        '''
        Returns the backed OpenHab item name.

        :rtype: str
        '''
        return self.item.getName()

    def getChannel(self):
        '''
        Returns the OpenHab channel string linked with the item.

        :rtype: str the channel string or None if the item is not linked to
        a channel
        '''
        channelMeta = MetadataRegistry.get(
                MetadataKey('channel', self.getItemName())) 
        if None != channelMeta:
            return channelMeta.value
        else:
            return None

    def setBatteryPowered(self, boolValue):
        '''
        :return: A NEW object with the batteryPowered attribute set to the
                specified value
        '''
        newObj = copy(self)
        newObj.batteryPowered = boolValue

        return newObj

    def isBatteryPowered(self):
        '''
        Returns True if the device is powered by a batter; False otherwise.

        :rtype: Boolean
        '''

        return self.batteryPowered

    def setUseWifi(self, boolValue):
        '''
        :return: A NEW object with the wifi attribute set to the specified value
        '''
        newObj = copy(self)
        newObj.wifi = boolValue

        return newObj

    def useWifi(self):
        '''
        Returns True if the device communicates using WiFi.

        :rtype: Boolean
        '''
        return self.wifi

    def setAutoReport(self, boolValue):
        '''
        :return: A NEW object with the autoReport attribute set to the specified value.
        '''
        newObj = copy(self)
        newObj.autoReport = boolValue

        return newObj

    def isAutoReport(self):
        '''
        Returns True if the device periodically sends its value.

        :rtype: Boolean
        '''
        return self.autoReport

    def getLastActivatedTimestamp(self):
        '''
        Returns the timestamp in epoch seconds of the last event generated by
        the device.

        :rtype: int the last activated epoch second or None if not no event has
            been generated.
        '''
        return self.lastActivatedTimestamp

    def wasRecentlyActivated(self, seconds):
        '''
        :param int seconds: the past duration (from the current time) to
            determine if the device was activated.
        :rtype: bool True if the device was activated during the specified
            seconds; False otherwise.
        '''
        prevTimestamp = self.getLastActivatedTimestamp()
        if None == prevTimestamp:
            return False
        else:
            return (time.time() - prevTimestamp) <= seconds

    def _updateLastActivatedTimestamp(self):
        '''
        Set the lastActivatedTimestamp field to the current epoch second.
        '''
        self.lastActivatedTimestamp = time.time()

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __unicode__(self):
        str = u"{}: {}".format(self.__class__.__name__, self.item.getName())

        if self.isBatteryPowered():
            str += ", battery powered"

        if self.useWifi():
            str += ", wifi"

        if self.isAutoReport():
            str += ", auto report"

        if None != self.lastActivatedTimestamp:
            str += ", last activated: {}".format(self.lastActivatedTimestamp)

        return str
