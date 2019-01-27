import time
from org.eclipse.smarthome.core.library.types import OnOffType

# Represents a light or fan switch.
class Switch:
    # Ctor
    # @param switchItem org.eclipse.smarthome.core.library.items.SwitchItem
    # @param timerItem org.eclipse.smarthome.core.library.items.SwitchItem
    # @throw ValueError if any parameter is invalid
    def __init__(self, switchItem, timerItem):
        if None == switchItem:
            raise ValueError('switchItem must not be None')

        if None == timerItem:
            raise ValueError('timerItem must not be None')

        self.switchItem = switchItem
        self.timerItem = timerItem

    # Turns on this light, if it is not on yet. In either case, the associated
    # timer item is also turned on.
    def turnOn(self, events):
        if OnOffType.ON != self.switchItem.getState():
            events.sendCommand(self.switchItem.getName(), "ON")
        
        self._handleCommonOnAction(events)

    # Turn off this light.
    def turnOff(self, events):
        if OnOffType.ON == self.switchItem.getState():
            events.sendCommand(self.switchItem.getName(), "OFF")

        if OnOffType.OFF != self.switchItem.getState():
            events.sendCommand(self.timerItem.getName(), "OFF")

    # Returns true if the switch is turned on; false otherwise.
    def isOn(self):
        return OnOffType.ON == self.switchItem.getState()

    def getSwitchItem(self):
        return self.switchItem

    def getTimerItem(self):
        return self.timerItem

    # Misc common things to do when a switch is turned on.
    def _handleCommonOnAction(self, events):
        self.lastLightOnSecondSinceEpoch = time.time()
        # start or renew timer
        events.sendCommand(self.timerItem.getName(), "ON")

# Represents a regular light.
class Light(Switch):
    def __init__(self, switchItem, timerItem):
        Switch.__init__(self, switchItem, timerItem)

# Represents a regular light.
class Fan(Switch):
    def __init__(self, switchItem, timerItem):
        Switch.__init__(self, switchItem, timerItem)
