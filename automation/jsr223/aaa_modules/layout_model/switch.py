import time
from org.eclipse.smarthome.core.library.types import OnOffType

from aaa_modules.layout_model.device import Device

# Represents a light or fan switch. Each switch is associated with a timer
# item. When the switch is turned on, the timer is turned on as well. As the
# timer expires, the switch is turned off (if it is not off already). If the
# switch is turned off not by the timer, the timer is cancelled.
class Switch(Device):
    # Ctor
    # @param switchItem org.eclipse.smarthome.core.library.items.SwitchItem
    # @param timerItem org.eclipse.smarthome.core.library.items.SwitchItem
    # @throw ValueError if any parameter is invalid
    def __init__(self, switchItem, timerItem):
        Device.__init__(self, switchItem)

        if None == timerItem:
            raise ValueError('timerItem must not be None')

        self.timerItem = timerItem

    # Turns on this light, if it is not on yet. In either case, the associated
    # timer item is also turned on.
    def turnOn(self, events):
        if OnOffType.ON != self.getItem().getState():
            events.sendCommand(self.getItemName(), "ON")
        else: # already on, renew timer
            events.sendCommand(self.timerItem.getName(), "ON")

    # Turn off this light.
    def turnOff(self, events):
        if OnOffType.ON == self.getItem().getState():
            events.sendCommand(self.getItemName(), "OFF")

    # Returns true if the switch is turned on; false otherwise.
    def isOn(self):
        return OnOffType.ON == self.getItem().getState()

    # Invoked when a switch on event is triggered. Note that a switch can be
    # turned on through this class' turnOn method, or through the event bus, or
    # manually by the user.
    # The following actions are done:
    #   - the on timestamp is set;
    #   - the timer item is set to ON.
    # @param events scope.events
    # @param itemName string - the name of the item triggering the event
    # @return True if itemName refers to this switch; False otherwise
    def onSwitchTurnedOn(self, events, itemName):
        isProcessed = (self.getItemName() == itemName)
        if isProcessed:
            self._handleCommonOnAction(events)

        return isProcessed

    # Invoked when a switch off event is triggered. Note that a switch can be
    # turned off through this class' turnOff method, or through the event bus,
    # or manually by the user.
    # The following actions are done:
    #   - the timer item is set to OFF.
    # @param events scope.events
    # @param itemName string - the name of the item triggering the event
    # @return True if itemName refers to this switch; False otherwise
    def onSwitchTurnedOff(self, events, itemName):
        isProcessed = (self.getItemName() == itemName)
        if isProcessed:
            if OnOffType.OFF != self.timerItem.getState():
                events.sendCommand(self.timerItem.getName(), "OFF")

        return isProcessed

    def getTimerItem(self):
        return self.timerItem

    # Misc common things to do when a switch is turned on.
    def _handleCommonOnAction(self, events):
        self.lastLightOnSecondSinceEpoch = time.time()
        # start or renew timer
        events.sendCommand(self.timerItem.getName(), "ON")

# Represents a regular light.
class Light(Switch):
    # @param illuminanceLevel the illuminance level in LUX unit. The light should only
    #     be turned on if the light level is below this unit.
    def __init__(self, switchItem, timerItem, illuminanceLevel = None):
        Switch.__init__(self, switchItem, timerItem)
        self._illuminanceLevel = illuminanceLevel

    # Returns the illuminance level in LUX unit. Returns None if not applicable.
    def getIlluminanceThreshold(self):
        return self._illuminanceLevel

# Represents a regular light.
class Fan(Switch):
    def __init__(self, switchItem, timerItem):
        Switch.__init__(self, switchItem, timerItem)
