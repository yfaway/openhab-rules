from core.jsr223 import scope
from org.eclipse.smarthome.core.library.types import OnOffType
    
from aaa_modules.layout_model import switch
reload(switch)
from aaa_modules.layout_model.switch import Light

from aaa_modules import time_utilities

# Represents a light dimmer with the dimm level value ranges from 1 to 100.
class Dimmer(Light):
    # Constructs a new object.
    # @throw ValueError if any parameter is invalid
    def __init__(self, switchItem, timerItem, dimLevel = 5, timeRanges = None,
            illuminanceLevel = None):
        Light.__init__(self, switchItem, timerItem, illuminanceLevel)

        if dimLevel < 0 or dimLevel > 100:
            raise ValueError('dimLevel must be between 0 and 100 inclusive')

        time_utilities.stringToTimeRangeLists(timeRanges) # validate

        self.dimLevel = dimLevel
        self.timeRanges = timeRanges

    # Turn on this light if it is not on yet.
    # If the light is dimmable, and if the current time falls into the
    # specified time ranges, it will be dimmed; otherwise it is turned on at
    # 100%. The associated timer item is also turned on.
    # @override
    def turnOn(self, events):
        if OnOffType.ON != self.getItem().getState():
            if time_utilities.isInTimeRange(self.timeRanges):
                events.sendCommand(self.getItemName(),
                        str(self.dimLevel))
            else:
                events.sendCommand(self.getItemName(), "100")

        self._handleCommonOnAction(events)

    # Returns true if the dimmer is turned on; false otherwise.
    # @override
    def isOn(self):
        return self.getItem().state > scope.DecimalType(0)

