from org.eclipse.smarthome.core.library.types import OnOffType

from aaa_modules.layout_model import device
reload(device)
from aaa_modules.layout_model.device import Device

# Represents a light/illuminance sensor; the underlying OpenHab object is a
# NumberItem.
class IlluminanceSensor(Device):
    # Ctor
    # @param numberItem org.eclipse.smarthome.core.library.items.NumberItem
    # @throw ValueError if any parameter is invalid
    def __init__(self, numberItem):
        Device.__init__(self, numberItem)

    # Returns an positive integer representing the LUX value.
    def getIlluminanceLevel(self):
        return self.getItem().getState().intValue()
