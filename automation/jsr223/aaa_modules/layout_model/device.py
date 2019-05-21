
from core import osgi
from org.eclipse.smarthome.core.items import Metadata
from org.eclipse.smarthome.core.items import MetadataKey

MetadataRegistry = osgi.get_service("org.eclipse.smarthome.core.items.MetadataRegistry")

# The base class that all other sensors and switches derive from.
class Device(object):
    # Ctor
    # @param openhabItem org.eclipse.smarthome.core.items.Item
    # @throw ValueError if any parameter is invalid
    def __init__(self, openhabItem):
        if None == openhabItem:
            raise ValueError('openhabItem must not be None')

        self.item = openhabItem

    # Returns the backed OpenHab item.
    # @return org.eclipse.smarthome.core.items.Item
    def getItem(self):
        return self.item

    # Returns the backed OpenHab item name.
    # @return string
    def getItemName(self):
        return self.item.getName()

    # Returns the OpenHab channel string linked with the item.
    # @return string the channel string or None if the item is not linked to
    #     a channel
    def getChannel(self):
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
