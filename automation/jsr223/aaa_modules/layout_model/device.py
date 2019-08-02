from core import osgi
from org.eclipse.smarthome.core.items import Metadata
from org.eclipse.smarthome.core.items import MetadataKey

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

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __unicode__(self):
        str = u"{}: {}".format(self.__class__.__name__, self.item.getName())
        return str
