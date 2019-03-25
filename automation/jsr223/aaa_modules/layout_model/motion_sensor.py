from org.eclipse.smarthome.core.library.types import OnOffType

# Represents a motion sensor; the underlying OpenHab object is a SwitchItem.
class MotionSensor:
    # Ctor
    # @param switchItem org.eclipse.smarthome.core.library.items.SwitchItem
    # @throw ValueError if any parameter is invalid
    def __init__(self, switchItem):
        if None == switchItem:
            raise ValueError('switchItem must not be None')

        self.switchItem = switchItem

    # Returns true if the motion sensor's state is on; false otherwise.
    def isOn(self):
        return OnOffType.ON == self.switchItem.getState()

    def getSwitchItem(self):
        return self.switchItem
