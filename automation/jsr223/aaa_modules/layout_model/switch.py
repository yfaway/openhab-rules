import time
from org.eclipse.smarthome.core.library.types import OnOffType

from aaa_modules.layout_model.device import Device

class Switch(Device):
    '''
    Represents a light or fan switch. Each switch is associated with a timer
    item. When the switch is turned on, the timer is turned on as well. As the
    timer expires, the switch is turned off (if it is not off already). If the
    switch is turned off not by the timer, the timer is cancelled.
    '''

    def __init__(self, switchItem, timerItem,
            disableTrigeringFromMotionSensor = False):
        '''
        Ctor
        :param org.eclipse.smarthome.core.library.items.SwitchItem switchItem:
        :param org.eclipse.smarthome.core.library.items.SwitchItem timerItem:
        :param bool disableTrigeringFromMotionSensor: a flag to indicate whether
        the switch should be turned on when motion sensor is triggered.
        There is no logic associate with this value in this class; it is 
        used by external classes through the getter.
        :raise ValueError: if any parameter is invalid
        '''
        Device.__init__(self, switchItem)

        if None == timerItem:
            raise ValueError('timerItem must not be None')

        self.timerItem = timerItem
        self.disableTrigeringFromMotionSensor = disableTrigeringFromMotionSensor
        self.lastOffTimestampInSeconds = -1

    def turnOn(self, events):
        '''
        Turns on this light, if it is not on yet. In either case, the associated
        timer item is also turned on.
        '''
        if OnOffType.ON != self.getItem().getState():
            events.sendCommand(self.getItemName(), "ON")
        else: # already on, renew timer
            events.sendCommand(self.timerItem.getName(), "ON")

    def turnOff(self, events):
        '''
        Turn off this light.
        '''
        if self.isOn():
            events.sendCommand(self.getItemName(), "OFF")

    def isOn(self):
        '''
        Returns true if the switch is turned on; false otherwise.
        '''
        return OnOffType.ON == self.getItem().getState()

    def onSwitchTurnedOn(self, events, itemName):
        '''
        Invoked when a switch on event is triggered. Note that a switch can be
        turned on through this class' turnOn method, or through the event bus, or
        manually by the user.
        The following actions are done:
        - the on timestamp is set;
        - the timer item is set to ON.

        :param scope.events events 
        :param string itemName: the name of the item triggering the event
        :return True: if itemName refers to this switch; False otherwise
        '''
        isProcessed = (self.getItemName() == itemName)
        if isProcessed:
            self._handleCommonOnAction(events)

        return isProcessed

    def onSwitchTurnedOff(self, events, itemName):
        '''
        Invoked when a switch off event is triggered. Note that a switch can be
        turned off through this class' turnOff method, or through the event bus,
        or manually by the user.
        The following actions are done:
        - the timer item is set to OFF.

        :param scope.events events: 
        :param string itemName: the name of the item triggering the event
        :return: True if itemName refers to this switch; False otherwise
        '''
        isProcessed = (self.getItemName() == itemName)
        if isProcessed:
            self.lastOffTimestampInSeconds = time.time()
            if OnOffType.OFF != self.timerItem.getState():
                events.sendCommand(self.timerItem.getName(), "OFF")

        return isProcessed

    def getLastOffTimestampInSeconds(self):
        '''
        Returns the timestamp in epoch seconds the switch was last turned off.

        :return: -1 if the timestamp is not available, or an integer presenting\
        the epoch seconds
        '''
        return self.lastOffTimestampInSeconds

    def getTimerItem(self):
        return self.timerItem

    def canBeTriggeredByMotionSensor(self):
        '''
        Returns True if this switch can be turned on when a motion sensor is
        triggered.
        A False value might be desired if two switches share the same motion
        sensor, and only one switch shall be turned on when the motion sensor is
        triggered.

        :rtype: bool
        '''
        return not self.disableTrigeringFromMotionSensor

    # Misc common things to do when a switch is turned on.
    def _handleCommonOnAction(self, events):
        self.lastLightOnSecondSinceEpoch = time.time()
        # start or renew timer
        events.sendCommand(self.timerItem.getName(), "ON")

    def isLowIlluminance(self, currentIlluminance):
        '''
        Always return False.
        '''
        return False

    def __unicode__(self):
        '''
        @override
        '''
        return u"{}, {}".format(
                super(Switch, self).__unicode__(), self.timerItem.getName())


class Light(Switch):
    '''
    Represents a regular light.
    '''

    def __init__(self, switchItem, timerItem, illuminanceLevel = None,
            disableTrigeringFromMotionSensor = False):
        '''
        :param int illuminanceLevel: the illuminance level in LUX unit. The \
        light should only be turned on if the light level is below this unit.
        '''
        Switch.__init__(self, switchItem, timerItem,
                disableTrigeringFromMotionSensor)
        self._illuminanceLevel = illuminanceLevel

    def getIlluminanceThreshold(self):
        '''
        Returns the illuminance level in LUX unit. Returns None if not applicable.
        '''
        return self._illuminanceLevel

    def isLowIlluminance(self, currentIlluminance):
        '''
        Returns False if this light has no illuminance threshold or if 
        currentIlluminance is less than 0. Otherwise returns True if the
        currentIlluminance is less than threshold.
        @override
        '''
        if None == self.getIlluminanceThreshold():
            return False

        if currentIlluminance < 0: # current illuminance not available
            return False

        return currentIlluminance < self.getIlluminanceThreshold()

    def __unicode__(self):
        '''
        @override
        '''
        return u"{}, illuminance: {}".format(
                super(Light, self).__unicode__(), self._illuminanceLevel)

class Fan(Switch):
    '''
    Represents a fan switch.
    '''
    def __init__(self, switchItem, timerItem):
        Switch.__init__(self, switchItem, timerItem)
