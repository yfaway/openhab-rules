from org.eclipse.smarthome.core.library.types import OnOffType

# The base class that all other sensors and switches derive from.
class Device:
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

