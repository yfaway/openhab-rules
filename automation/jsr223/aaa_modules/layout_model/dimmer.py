from aaa_modules.layout_model import switch
reload(switch)
from aaa_modules.layout_model.switch import Light

# Represents a light dimmer with the dimm level value ranges from 1 to 100.
class Dimmer(Light):
    def __init__(self, switchItem, timerItem, dimLevel = 5, timeRanges = None):
        Light.__init__(self, switchItem, timerItem)
        self.dimLevel = dimLevel
        self.timeRanges = timeRanges

    # Turn on this light. If the light is dimmable, and if the current time
    # falls into the specified time ranges, it will be dimmed; otherwise it is
    # turned on at 100%.
    def turnOn(self, events):
        super().turnOn(events)
