
from org.eclipse.smarthome.core.library.types import OnOffType

# Represents a light or fan switch.
class Switch:
    # Ctor
    # @param switchItem org.eclipse.smarthome.core.library.items.SwitchItem
    # @param timerItem org.eclipse.smarthome.core.library.items.SwitchItem
    def __init__(self, switchItem, timerItem):
        self.switchItem = switchItem
        self.timerItem = timerItem

    # Turn on this light. If the light is dimmable, and if the current time
    # falls into the specified time ranges, it will be dimmed; otherwise it is
    # turned on at 100%.
    def turnOn(self, events):
        if OnOffType.ON != self.switchItem.getState():
            events.sendCommand(self.switchItem.getName(), "ON")
        
        # start or renew timer
        events.sendCommand(self.timerItem.getName(), "ON")

    # Turn off this light.
    def turnOff(self, events):
        if OnOffType.ON == self.switchItem.getState():
            events.sendCommand(self.switchItem.getName(), "OFF")

        if OnOffType.OFF != self.switchItem.getState():
            events.sendCommand(self.timerItem.getName(), "OFF")

    def getSwitchItem(self):
        return self.switchItem

    def getTimerItem(self):
        return self.timerItem

# Represents a regular light.
class Light(Switch):
    def __init__(self, switchItem, timerItem):
        Switch.__init__(self, switchItem, timerItem)

# Represents a regular light.
class Fan(Switch):
    def __init__(self, switchItem, timerItem):
        Switch.__init__(self, switchItem, timerItem)
