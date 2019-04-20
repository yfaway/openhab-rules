from aaa_modules.layout_model.device import Device

# A virtual sensor to determine the light on time; backed by a StringItem.
class AstroSensor(Device):
    LIGHT_ON_TIMES = ["EVENING", "NIGHT", "BED"]

    # Ctor
    # @param stringItem org.eclipse.smarthome.core.library.items.StringItem
    # @throw ValueError if any parameter is invalid
    def __init__(self, stringItem):
        Device.__init__(self, stringItem)

    # Returns True if it is evening time; returns False otherwise.
    # @return bool
    def isLightOnTime(self):
        state = self.getItem().getState()
        return any(s == state.toString() for s in self.LIGHT_ON_TIMES)
