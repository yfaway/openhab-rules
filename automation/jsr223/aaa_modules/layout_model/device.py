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

    def __init__(self, openhabItem):
        '''
        Ctor

        :param org.eclipse.smarthome.core.items.Item openhabItem:
        :raise ValueError: if any parameter is invalid
        '''
        if None == openhabItem:
            raise ValueError('openhabItem must not be None')

        self.item = openhabItem
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

    def getLastActivatedTimestamp(self):
        '''
        Returns the timestamp in epoch seconds of the last event generated by
        the device.

        :rtype: int the last activated epoch second or None if not no event has
            been generated.
        '''
        return self.lastActivatedTimestamp

    def wasActivatedInTheLastSeconds(self, seconds):
        '''
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
        return str
