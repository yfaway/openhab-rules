from org.eclipse.smarthome.core.library.types import StringType
from aaa_modules.layout_model.device import Device

# A virtual sensor to determine the light on time; backed by a StringItem.
class AstroSensor(Device):
    # Ctor
    # @param stringItem org.eclipse.smarthome.core.library.items.StringItem
    # @throw ValueError if any parameter is invalid
    def __init__(self, stringItem):
        Device.__init__(self, stringItem)

    # Returns True if it is evening time; returns False otherwise.
    # @return bool
    def isLightOnTime(self):
        state = self.getItem().getState()
        return state == StringType("EVENING") or state == StringType("NIGHT") \
            or state == StringType("BED")
